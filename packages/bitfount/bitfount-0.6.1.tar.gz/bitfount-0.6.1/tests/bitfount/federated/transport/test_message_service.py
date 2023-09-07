"""Tests GRPC Wrapper class."""
from datetime import datetime
import logging
import os
from pathlib import Path
import re
import tempfile
import time
from typing import Final, List, Optional, Tuple
from unittest.mock import (
    ANY,
    AsyncMock,
    Mock,
    NonCallableMock,
    PropertyMock,
    call,
    create_autospec,
)

from grpc import RpcError, StatusCode
import msgpack
import numpy as np
import pandas as pd
import pytest
from pytest import LogCaptureFixture, fixture, raises
from pytest_mock import MockerFixture
from requests import HTTPError, RequestException

from bitfount.federated.encryption import _AESEncryption, _RSAEncryption
from bitfount.federated.exceptions import DecryptError
from bitfount.federated.transport import utils
from bitfount.federated.transport.config import MessageServiceConfig
from bitfount.federated.transport.exceptions import BitfountMessageServiceError
from bitfount.federated.transport.message_service import (
    _MAX_STORAGE_SIZE_BYTES,
    _MAX_STORAGE_SIZE_MEGABYTES,
    _SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES,
    _AutoRetryMessageServiceStub,
    _BitfountMessage,
    _BitfountMessageType,
    _DecryptedBitfountMessage,
    _LargeObjectRequestHandler,
    _MessageEncryption,
    _MessageService,
    msgpackext_decode,
    msgpackext_encode,
)
from bitfount.federated.transport.protos.messages_pb2 import (
    Acknowledgement,
    BitfountMessage as GrpcBitfountMessage,
    BitfountTask,
    BitfountTasks,
    BlobStorageData,
    CommunicationDetails,
    PodData,
    SuccessResponse,
    TaskMetadata,
    TaskTransferMetadata,
    TaskTransferRequest,
    TaskTransferRequests,
)
from bitfount.hub.authentication_flow import BitfountSession
from bitfount.storage import _get_packed_data_object_size
from bitfount.types import _S3PresignedPOSTFields, _S3PresignedPOSTURL, _S3PresignedURL
from bitfount.utils import _get_mb_from_bytes
from tests.utils import PytestRequest
from tests.utils.fixtures import RpcErrorMaker
from tests.utils.helper import create_dataset, get_debug_logs, unit_test
from tests.utils.mocks import create_dataclass_mock

_GRPC_ERROR_CODES: Final = {sc for sc in StatusCode}


@unit_test
class TestMessageService:
    """Test MessageService (GRPC wrapper)."""

    @fixture
    def username(self) -> str:
        """Username."""
        return "theAuthenticatedUser"

    @fixture
    def task_id(self) -> str:
        """Task ID."""
        return "this-is-a-task-id"

    @fixture(params=(True, False), ids=("task_id_incl", "no_task_id"))
    def opt_task_id(self, request: PytestRequest, task_id: str) -> Optional[str]:
        """Returns a task ID or None, to cover both cases."""
        incl_task_id: bool = request.param
        if incl_task_id:
            return task_id
        else:
            return None

    @fixture
    def expected_request_metadata(self) -> List[Tuple[str, str]]:
        """Metadata attached to GRPC request."""
        return [
            ("x-api-key-id", "accessKeyID1"),
            ("x-api-key", "accessKey1"),
        ]

    @fixture
    def session(
        self, expected_request_metadata: List[Tuple[str, str]], username: str
    ) -> Mock:
        """Mocked session."""
        session: Mock = create_autospec(BitfountSession, instance=True)
        session.username = username
        session.message_service_metadata = expected_request_metadata
        return session

    @fixture
    def grpc_stub(self) -> Mock:
        """Mocked GRPC Stub.

        Mocking this is a bit unpleasant due to the way it is constructed.
        """
        mock_stub = AsyncMock(
            spec_set=[
                "PodConnect",
                "SetupTask",
                "InitiateTask",
                "SetupTaskMailboxes",
                "SendBitfountMessage",
                "GetBitfountMessage",
                "GetLargeObjectStorage",
                "AcknowledgeMessage",
            ]
        )

        # Need to explicitly set AsyncMocks on all the methods due to how
        # spec_set works
        mock_stub.PodConnect = AsyncMock()
        mock_stub.SetupTask = AsyncMock()
        mock_stub.InitiateTask = AsyncMock()
        mock_stub.SetupTaskMailboxes = AsyncMock()
        mock_stub.SendBitfountMessage = AsyncMock()
        mock_stub.GetBitfountMessage = AsyncMock()
        mock_stub.GetLargeObjectStorage = AsyncMock()
        mock_stub.AcknowledgeMessage = AsyncMock()

        return mock_stub

    @fixture
    def mock_config_stub_property(self, grpc_stub: Mock) -> PropertyMock:
        """Property mock of the MessageServiceConfig.stub property."""

        async def _mock_stub_property() -> Mock:
            # Need to use small helper function to get the async behaviour.
            return grpc_stub

        return PropertyMock(side_effect=_mock_stub_property)

    @fixture
    def mock_ms_config(
        self, mock_config_stub_property: PropertyMock
    ) -> NonCallableMock:
        """Returns mock MessageServiceConfig."""
        mock_ms_config = create_dataclass_mock(MessageServiceConfig)

        # PropertyMock must be set on type(x), not x.
        type(mock_ms_config).stub = mock_config_stub_property

        # Explicitly set use_local_storage to False
        mock_ms_config.use_local_storage = False

        return mock_ms_config

    @fixture
    def message_service(
        self, mock_ms_config: NonCallableMock, session: Mock
    ) -> _MessageService:
        """The MessageService under test."""
        return _MessageService(session, mock_ms_config)

    @fixture
    def mock_upload_to_s3(self, mocker: MockerFixture) -> AsyncMock:
        """Mock out upload_data_to_s3 function in message_service.py."""
        mock_upload_to_s3 = mocker.patch(
            "bitfount.federated.transport.message_service._async_upload_data_to_s3",
            autospec=True,
        )
        return mock_upload_to_s3

    @fixture
    def mock_download_from_s3(self, mocker: MockerFixture) -> AsyncMock:
        """Mock out download_data_from_s3 function in message_service.py."""
        mock_download_from_s3 = mocker.patch(
            "bitfount.federated.transport.message_service._async_download_data_from_s3",
            autospec=True,
        )
        return mock_download_from_s3

    def test_metadata_property_returns_request_metadata(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        message_service: _MessageService,
    ) -> None:
        """Test metadata property with API keys.

        Checks that only the first portion of the access key is included in the
        metadata.
        """
        assert message_service.metadata == expected_request_metadata

    def test_username_property_returns_username(
        self, message_service: _MessageService, username: str
    ) -> None:
        """Property returns username from session."""
        assert message_service.username == username

    async def test_stub_property(
        self,
        grpc_stub: Mock,
        message_service: _MessageService,
        mock_config_stub_property: PropertyMock,
    ) -> None:
        """Tests that the stub property/generates the stub from config."""
        # Check that the stub generated matches the output of the
        # MessageServiceConfig stub.
        stub = await message_service.stub
        assert isinstance(stub, _AutoRetryMessageServiceStub)
        assert stub._orig == grpc_stub

        # Check value is "cached"
        stub2 = await message_service.stub
        assert stub is stub2
        assert message_service._grpc.stub is not None

        # Check config stub only called once
        mock_config_stub_property.assert_called_once()

    async def test_connect_successful(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        mocker: MockerFixture,
    ) -> None:
        """Pod Connect successful."""
        platform = mocker.patch("bitfount.federated.transport.message_service.platform")
        psutil = mocker.patch("bitfount.federated.transport.message_service.psutil")
        get_gpu_metadata = mocker.patch(
            "bitfount.federated.transport.message_service.get_gpu_metadata"
        )
        platform.processor.return_value = "someProcessor"
        platform.system.return_value = "someOS"
        psutil.cpu_count.return_value = 50
        get_gpu_metadata.return_value = "someGPUName", 33

        memory_data = Mock()
        memory_data.total = 346346436
        psutil.virtual_memory.return_value = memory_data
        grpc_stub.PodConnect.return_value = SuccessResponse()
        pod_name = "somePodName"

        mailbox_id = await message_service.connect_pod(pod_name)

        assert mailbox_id == pod_name
        grpc_stub.PodConnect.assert_called_once_with(
            PodData(
                podName=pod_name,
                processor="someProcessor",
                podOS="someOS",
                cpuCount=50,
                gpuCount=33,
                gpuName="someGPUName",
                totalMemoryBytes=346346436,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=_GRPC_ERROR_CODES,
        ids=lambda sc: f"status_code={sc.name}",
    )
    async def test_connect_raises_error_on_failure(
        self,
        caplog: LogCaptureFixture,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error_maker: RpcErrorMaker,
        status_code: StatusCode,
    ) -> None:
        """Pod Connect receives RpcError."""
        if status_code in utils._RETRY_STATUS_CODES:
            retries = True
            expected_num_calls = utils._DEFAULT_MAX_RETRIES + 1
        else:
            retries = False
            expected_num_calls = 1
        expected_num_retries = expected_num_calls - 1

        grpc_stub.PodConnect.side_effect = rpc_error_maker(
            "Pod connect failed", status_code
        )
        pod_name = "somePodName"

        with raises(
            BitfountMessageServiceError,
            match=re.escape(
                "Unable to connect pod to message service."
                " See debug logs for more details."
            ),
        ), caplog.at_level(logging.DEBUG):
            await message_service.connect_pod(pod_name)

        # Sanity check that PodConnect was called at all
        assert (
            grpc_stub.PodConnect.call_args_list
            == [
                call(
                    ANY,
                    metadata=expected_request_metadata,
                    timeout=utils._DEFAULT_TIMEOUT,
                )
            ]
            * expected_num_calls
        )

        # Check underlying exception was logged to DEBUG
        debug_logs = get_debug_logs(caplog, full_details=True)
        assert "RpcError: Pod connect failed" in debug_logs

        # Check retry messages in debug logs and sleep called if required
        if retries:
            assert remove_grpc_retry_backoff_sleep.await_count == expected_num_retries
            for i in range(1, expected_num_retries + 1):
                assert re.search(
                    rf"gRPC error occurred: .* Pod connect failed; .* \(attempt {i}\)",
                    debug_logs,
                )
        else:
            remove_grpc_retry_backoff_sleep.assert_not_awaited()

    async def test_setup_communication_with_pods_successful(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        task_id: str,
    ) -> None:
        """Setup communication successful."""
        expected_modeller_mailbox_id = "someMailboxId"
        expected_worker_mailboxes = {
            "somePodName": "somePodMailboxId",
            "someOtherPodName": "someOtherMailboxId",
        }
        grpc_stub.SetupTaskMailboxes.return_value = CommunicationDetails(
            mailboxId=expected_modeller_mailbox_id,
            podMailboxIds=expected_worker_mailboxes,
            taskId=task_id,
        )
        pod_identifier = "podOwner/somePodName"
        training_request = b"some training request"

        (
            modeller_mailbox_id,
            worker_mailboxes,
            received_task_id,
        ) = await message_service.setup_communication_with_pods(
            {pod_identifier: training_request}
        )

        assert modeller_mailbox_id == expected_modeller_mailbox_id
        assert worker_mailboxes == expected_worker_mailboxes
        assert received_task_id == task_id
        grpc_stub.SetupTaskMailboxes.assert_called_once_with(
            BitfountTasks(
                tasks=[
                    BitfountTask(
                        podIdentifier=pod_identifier, encryptedTask=training_request
                    )
                ]
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

    async def test_setup_communication_with_pods_successful_taskURL(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        mocker: MockerFixture,
        task_id: str,
    ) -> None:
        """Setup communication successful with taskURL field."""
        expected_modeller_mailbox_id = "someMailboxId"
        expected_worker_mailboxes = {
            "somePodName": "somePodMailboxId",
            "someOtherPodName": "someOtherMailboxId",
        }
        grpc_stub.SetupTaskMailboxes.return_value = CommunicationDetails(
            mailboxId=expected_modeller_mailbox_id,
            podMailboxIds=expected_worker_mailboxes,
            taskId=task_id,
        )
        pod_identifier = "podOwner/somePodName"
        training_request = b"some training request"
        other_training_request = b"other training request"
        mock_task_upload = mocker.patch.object(
            _MessageService, "_maybe_upload_task_to_large_object_storage"
        )
        mock_task_upload.return_value = {pod_identifier: other_training_request}
        (
            modeller_mailbox_id,
            worker_mailboxes,
            received_task_id,
        ) = await message_service.setup_communication_with_pods(
            {pod_identifier: training_request}
        )

        assert modeller_mailbox_id == expected_modeller_mailbox_id
        assert worker_mailboxes == expected_worker_mailboxes
        assert received_task_id == task_id
        grpc_stub.SetupTaskMailboxes.assert_called_once_with(
            BitfountTasks(
                tasks=[
                    BitfountTask(
                        podIdentifier=pod_identifier, taskURL=other_training_request
                    )
                ]
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=_GRPC_ERROR_CODES,
        ids=lambda sc: f"status_code={sc.name}",
    )
    async def test_setup_communication_with_pods_raises_error_on_failure(
        self,
        caplog: LogCaptureFixture,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error_maker: RpcErrorMaker,
        status_code: StatusCode,
    ) -> None:
        """Setup communication receives RpcError."""
        if status_code in utils._RETRY_STATUS_CODES:
            retries = True
            expected_num_calls = utils._DEFAULT_MAX_RETRIES + 1
        else:
            retries = False
            expected_num_calls = 1
        expected_num_retries = expected_num_calls - 1

        grpc_stub.SetupTaskMailboxes.side_effect = rpc_error_maker(
            "SetupTaskMailboxes failed", status_code
        )
        pod_identifier = "podOwner/somePodName"
        training_request = b"some training request"

        with raises(
            BitfountMessageServiceError,
            match=re.escape(
                "Unable to setup communication with target pods."
                " See debug logs for more details."
            ),
        ), caplog.at_level(logging.DEBUG):
            await message_service.setup_communication_with_pods(
                {pod_identifier: training_request}
            )

        # Check calls
        assert (
            grpc_stub.SetupTaskMailboxes.call_args_list
            == [
                call(
                    BitfountTasks(
                        tasks=[
                            BitfountTask(
                                podIdentifier=pod_identifier,
                                encryptedTask=training_request,
                            )
                        ]
                    ),
                    metadata=expected_request_metadata,
                    timeout=utils._DEFAULT_TIMEOUT,
                )
            ]
            * expected_num_calls
        )

        # Check underlying exception was logged to DEBUG
        debug_logs = get_debug_logs(caplog, full_details=True)
        assert "RpcError: SetupTaskMailboxes failed" in debug_logs

        # Check retry messages in debug logs and sleep called if required
        if retries:
            assert remove_grpc_retry_backoff_sleep.await_count == expected_num_retries
            for i in range(1, expected_num_retries + 1):
                assert re.search(
                    rf"gRPC error occurred: .* SetupTaskMailboxes failed;"
                    rf" .* \(attempt {i}\)",
                    debug_logs,
                )
        else:
            remove_grpc_retry_backoff_sleep.assert_not_awaited()

    async def test_setup_task_successful(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        mocker: MockerFixture,
        task_id: str,
    ) -> None:
        """Setup communication successful with taskURL field."""
        expected_modeller_mailbox_id = "someMailboxId"
        expected_worker_mailboxes = {
            "somePodName": "somePodMailboxId",
            "someOtherPodName": "someOtherMailboxId",
        }
        expected_upload_url = "http://example.com/upload"
        expected_download_url = "http://example.com/download"
        expected_upload_fields = {"some": "fields"}
        expected_project_id = "someProjectID"
        expected_task_metadata = TaskMetadata(protocol="someprotocol")
        pod_identifier = "podOwner/somePodName"
        grpc_stub.SetupTask.return_value = TaskTransferMetadata(
            taskStorage=[
                BlobStorageData(
                    podIdentifier=pod_identifier,
                    uploadUrl=expected_upload_url,
                    downloadUrl=expected_download_url,
                    uploadFields=expected_upload_fields,
                )
            ],
            taskId=task_id,
        )
        grpc_stub.InitiateTask.return_value = CommunicationDetails(
            mailboxId=expected_modeller_mailbox_id,
            podMailboxIds=expected_worker_mailboxes,
            taskId=task_id,
        )

        training_request = b"some training request"
        mocker.patch.object(_LargeObjectRequestHandler, "upload_large_object")
        (
            modeller_mailbox_id,
            worker_mailboxes,
            received_task_id,
        ) = await message_service.setup_task(
            {pod_identifier: training_request},
            task_metadata=expected_task_metadata,
            project_id=expected_project_id,
        )

        assert modeller_mailbox_id == expected_modeller_mailbox_id
        assert worker_mailboxes == expected_worker_mailboxes
        assert received_task_id == task_id
        grpc_stub.SetupTask.assert_called_once_with(
            TaskTransferRequests(
                podTasks=[
                    TaskTransferRequest(
                        podIdentifier=pod_identifier,
                        contentSize=_get_packed_data_object_size(training_request),
                    )
                ],
                projectId=expected_project_id,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        grpc_stub.InitiateTask.assert_called_once_with(
            BitfountTasks(
                tasks=[
                    BitfountTask(
                        podIdentifier=pod_identifier,
                        taskURL=msgpack.dumps(
                            expected_download_url, default=msgpackext_encode
                        ),
                    )
                ],
                taskId=task_id,
                projectId=expected_project_id,
                taskMetadata=TaskMetadata(protocol="someprotocol"),
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=_GRPC_ERROR_CODES,
        ids=lambda sc: f"status_code={sc.name}",
    )
    async def test_setup_task_raises_error_on_setup_failure(
        self,
        caplog: LogCaptureFixture,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error_maker: RpcErrorMaker,
        status_code: StatusCode,
    ) -> None:
        """Setup communication receives RpcError."""
        if status_code in utils._RETRY_STATUS_CODES:
            retries = True
            expected_num_calls = utils._DEFAULT_MAX_RETRIES + 1
        else:
            retries = False
            expected_num_calls = 1
        expected_num_retries = expected_num_calls - 1

        grpc_stub.SetupTask.side_effect = rpc_error_maker(
            "SetupTask failed", status_code
        )
        pod_identifier = "podOwner/somePodName"
        training_request = b"some training request"
        expected_project_id = "someProjectID"
        expected_task_metadata = TaskMetadata()

        with raises(
            BitfountMessageServiceError,
            match=re.escape(
                "Unable to start task with target pods."
                " See debug logs for more details."
            ),
        ), caplog.at_level(logging.DEBUG):
            await message_service.setup_task(
                {pod_identifier: training_request},
                task_metadata=expected_task_metadata,
                project_id=expected_project_id,
            )

        # Check calls
        assert (
            grpc_stub.SetupTask.call_args_list
            == [
                call(
                    TaskTransferRequests(
                        podTasks=[
                            TaskTransferRequest(
                                podIdentifier=pod_identifier,
                                contentSize=_get_packed_data_object_size(
                                    training_request
                                ),
                            )
                        ],
                        projectId=expected_project_id,
                    ),
                    metadata=expected_request_metadata,
                    timeout=utils._DEFAULT_TIMEOUT,
                )
            ]
            * expected_num_calls
        )

        # Check underlying exception was logged to DEBUG
        debug_logs = get_debug_logs(caplog, full_details=True)
        assert "RpcError: SetupTask failed" in debug_logs

        # Check retry messages in debug logs and sleep called if required
        if retries:
            assert remove_grpc_retry_backoff_sleep.await_count == expected_num_retries
            for i in range(1, expected_num_retries + 1):
                assert re.search(
                    rf"gRPC error occurred: .* SetupTask failed;"
                    rf" .* \(attempt {i}\)",
                    debug_logs,
                )
        else:
            remove_grpc_retry_backoff_sleep.assert_not_awaited()

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=_GRPC_ERROR_CODES,
        ids=lambda sc: f"status_code={sc.name}",
    )
    async def test_setup_task_raises_error_on_initiate_failure(
        self,
        caplog: LogCaptureFixture,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        mocker: MockerFixture,
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error_maker: RpcErrorMaker,
        status_code: StatusCode,
        task_id: str,
    ) -> None:
        """Setup communication receives RpcError."""
        if status_code in utils._RETRY_STATUS_CODES:
            retries = True
            expected_num_calls = utils._DEFAULT_MAX_RETRIES + 1
        else:
            retries = False
            expected_num_calls = 1
        expected_num_retries = expected_num_calls - 1

        expected_upload_url = "http://example.com/upload"
        expected_download_url = "http://example.com/download"
        expected_upload_fields = {"some": "fields"}
        expected_project_id = "someProjectID"
        expected_task_metadata = TaskMetadata(protocol="someprotocol")
        pod_identifier = "podOwner/somePodName"
        mocker.patch.object(_LargeObjectRequestHandler, "upload_large_object")
        grpc_stub.SetupTask.return_value = TaskTransferMetadata(
            taskStorage=[
                BlobStorageData(
                    podIdentifier=pod_identifier,
                    uploadUrl=expected_upload_url,
                    downloadUrl=expected_download_url,
                    uploadFields=expected_upload_fields,
                )
            ],
            taskId=task_id,
        )
        grpc_stub.InitiateTask.side_effect = rpc_error_maker(
            "InitiateTask failed", status_code
        )
        pod_identifier = "podOwner/somePodName"
        training_request = b"some training request"

        with raises(
            BitfountMessageServiceError,
            match=re.escape(
                "Unable to start task with target pods."
                " See debug logs for more details."
            ),
        ), caplog.at_level(logging.DEBUG):
            await message_service.setup_task(
                {pod_identifier: training_request},
                task_metadata=expected_task_metadata,
                project_id=expected_project_id,
            )

        # Check calls
        assert (
            grpc_stub.InitiateTask.call_args_list
            == [
                call(
                    BitfountTasks(
                        tasks=[
                            BitfountTask(
                                podIdentifier=pod_identifier,
                                taskURL=msgpack.dumps(
                                    expected_download_url, default=msgpackext_encode
                                ),
                            )
                        ],
                        taskId=task_id,
                        projectId=expected_project_id,
                        taskMetadata=TaskMetadata(protocol="someprotocol"),
                    ),
                    metadata=expected_request_metadata,
                    timeout=utils._DEFAULT_TIMEOUT,
                )
            ]
            * expected_num_calls
        )

        # Check underlying exception was logged to DEBUG
        debug_logs = get_debug_logs(caplog, full_details=True)
        assert "RpcError: InitiateTask failed" in debug_logs

        # Check retry messages in debug logs and sleep called if required
        if retries:
            assert remove_grpc_retry_backoff_sleep.await_count == expected_num_retries
            for i in range(1, expected_num_retries + 1):
                assert re.search(
                    rf"gRPC error occurred: .* InitiateTask failed;"
                    rf" .* \(attempt {i}\)",
                    debug_logs,
                )
        else:
            remove_grpc_retry_backoff_sleep.assert_not_awaited()

    async def test_send_message_successful_already_packed(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        opt_task_id: Optional[str],
    ) -> None:
        """Test send packed body to Pod."""
        grpc_stub.SendBitfountMessage.return_value = SuccessResponse()
        packed_message = b"an already packed message"
        pod_identifier = "podOwner/somePodName"
        mailbox_id = "someMailboxId"
        reply_to_mailbox_id = "replyMailboxId"
        sender = "someSender"
        expected_timestamp = datetime.now().isoformat()

        response = await message_service.send_message(
            _BitfountMessage(
                message_type=_BitfountMessageType.TRAINING_UPDATE,
                body=packed_message,
                recipient=pod_identifier,
                recipient_mailbox_id=mailbox_id,
                sender=sender,
                sender_mailbox_id=reply_to_mailbox_id,
                timestamp=expected_timestamp,
                task_id=opt_task_id,
            ),
            already_packed=True,
        )

        assert response == SuccessResponse()
        grpc_stub.SendBitfountMessage.assert_called_once_with(
            GrpcBitfountMessage(
                messageType=_BitfountMessageType.TRAINING_UPDATE.value,
                body=packed_message,
                recipient=pod_identifier,
                recipientMailboxId=mailbox_id,
                sender=sender,
                senderMailboxId=reply_to_mailbox_id,
                timestamp=expected_timestamp,
                taskId=opt_task_id,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=_GRPC_ERROR_CODES,
        ids=lambda sc: f"status_code={sc.name}",
    )
    async def test_send_message_error_is_raised(
        self,
        caplog: LogCaptureFixture,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        opt_task_id: Optional[str],
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error_maker: RpcErrorMaker,
        status_code: StatusCode,
    ) -> None:
        """Test send to pod throws RpcError."""
        if status_code in utils._RETRY_STATUS_CODES:
            retries = True
            expected_num_calls = utils._DEFAULT_MAX_RETRIES + 1
        else:
            retries = False
            expected_num_calls = 1
        expected_num_retries = expected_num_calls - 1

        grpc_stub.SendBitfountMessage.side_effect = rpc_error_maker(
            "send message error", status_code
        )

        packed_message = b"an already packed message"
        pod_identifier = "podOwner/somePodName"
        mailbox_id = "someMailboxId"
        reply_to_mailbox_id = "replyMailboxId"
        sender = "someModeller"
        expected_timestamp = datetime.now().isoformat()

        with raises(
            BitfountMessageServiceError,
            match=re.escape(
                "Encountered problem when sending message."
                " See debug logs for more details."
            ),
        ), caplog.at_level(logging.DEBUG):
            await message_service.send_message(
                _BitfountMessage(
                    message_type=_BitfountMessageType.TRAINING_UPDATE,
                    body=packed_message,
                    recipient=pod_identifier,
                    recipient_mailbox_id=mailbox_id,
                    sender=sender,
                    sender_mailbox_id=reply_to_mailbox_id,
                    timestamp=expected_timestamp,
                    task_id=opt_task_id,
                ),
                already_packed=True,
            )

        # Check called the expected number of times
        assert (
            grpc_stub.SendBitfountMessage.call_args_list
            == [
                call(
                    GrpcBitfountMessage(
                        messageType=_BitfountMessageType.TRAINING_UPDATE.value,
                        body=packed_message,
                        sender=sender,
                        senderMailboxId=reply_to_mailbox_id,
                        recipient=pod_identifier,
                        recipientMailboxId=mailbox_id,
                        timestamp=expected_timestamp,
                        taskId=opt_task_id,
                    ),
                    metadata=expected_request_metadata,
                    timeout=utils._DEFAULT_TIMEOUT,
                )
            ]
            * expected_num_calls
        )

        # Check underlying exception was logged to DEBUG
        debug_logs = get_debug_logs(caplog, full_details=True)
        assert "RpcError: send message error" in debug_logs

        # Check retry messages in debug logs and sleep called if required
        if retries:
            assert remove_grpc_retry_backoff_sleep.await_count == expected_num_retries
            for i in range(1, expected_num_retries + 1):
                assert re.search(
                    rf"gRPC error occurred: .* send message error; .* \(attempt {i}\)",
                    debug_logs,
                )
        else:
            remove_grpc_retry_backoff_sleep.assert_not_awaited()

    async def test_send_message_successful_not_packed(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        opt_task_id: Optional[str],
    ) -> None:
        """Test send plain object to Modeller."""
        grpc_stub.SendBitfountMessage.return_value = SuccessResponse()
        unpacked_message = b"a message to be packed"
        expected_packed_message = msgpack.dumps(unpacked_message)
        modeller_name = "someModeller"
        pod_identifier = "podOwner/somePodName"
        mailbox_id = "someMailboxId"
        reply_to_mailbox_id = "replyMailboxId"
        expected_timestamp = datetime.now().isoformat()

        response = await message_service.send_message(
            _BitfountMessage(
                message_type=_BitfountMessageType.TRAINING_UPDATE,
                body=unpacked_message,
                recipient=modeller_name,
                recipient_mailbox_id=mailbox_id,
                sender=pod_identifier,
                sender_mailbox_id=reply_to_mailbox_id,
                timestamp=expected_timestamp,
                task_id=opt_task_id,
            ),
            already_packed=False,
        )

        assert response == SuccessResponse()
        grpc_stub.SendBitfountMessage.assert_called_once_with(
            GrpcBitfountMessage(
                messageType=_BitfountMessageType.TRAINING_UPDATE.value,
                body=expected_packed_message,
                sender=pod_identifier,
                senderMailboxId=reply_to_mailbox_id,
                recipient=modeller_name,
                recipientMailboxId=mailbox_id,
                timestamp=expected_timestamp,
                taskId=opt_task_id,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

    async def test_get_message_successful(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        mocker: MockerFixture,
        opt_task_id: Optional[str],
    ) -> None:
        """Test get message returns message."""
        expected_message_body = b"some message"
        expected_sent_by = "some modeller"
        expected_mailbox_id = "some mailbox"
        expected_reply_to_mailbox = "some reply to mailbox"
        expected_receipt_handle = "valid receipt handle"
        expected_pod_mailbox_ids = {"somePod": "someId"}
        expected_recipient = "someRecipient"
        expected_timestamp = datetime.now().isoformat()

        mock_sleep = mocker.patch("asyncio.sleep")

        grpc_stub.GetBitfountMessage.return_value = GrpcBitfountMessage(
            messageType=_BitfountMessageType.MODEL_PARAMETERS.value,
            body=expected_message_body,
            sender=expected_sent_by,
            senderMailboxId=expected_reply_to_mailbox,
            receiptHandle=expected_receipt_handle,
            recipient=expected_recipient,
            recipientMailboxId=expected_mailbox_id,
            podMailboxIds=expected_pod_mailbox_ids,
            timestamp=expected_timestamp,
            # Mimic when Grpc message doesn't have taskId
            **({"taskId": opt_task_id} if opt_task_id else {}),
        )
        grpc_stub.AcknowledgeMessage.return_value = SuccessResponse()

        message = await message_service._get_message(expected_mailbox_id)

        # Retrieved message is as expected
        assert message == _BitfountMessage(
            message_type=_BitfountMessageType.MODEL_PARAMETERS,
            body=expected_message_body,
            recipient=expected_recipient,
            recipient_mailbox_id=expected_mailbox_id,
            sender=expected_sent_by,
            sender_mailbox_id=expected_reply_to_mailbox,
            pod_mailbox_ids=expected_pod_mailbox_ids,
            timestamp=expected_timestamp,
            receipt_handle=expected_receipt_handle,
            task_id=opt_task_id,
        )

        # Message was requested correctly
        grpc_stub.GetBitfountMessage.assert_called_once_with(
            CommunicationDetails(mailboxId=expected_mailbox_id),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # Message was acknowledged correctly
        grpc_stub.AcknowledgeMessage.assert_called_once_with(
            Acknowledgement(
                mailboxId=expected_mailbox_id,
                receiptHandle=expected_receipt_handle,
                deleteMailbox=False,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # We didn't sleep unnecessarily
        mock_sleep.assert_not_awaited()

    async def test_get_message_successful_and_is_unpacked(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        mocker: MockerFixture,
        opt_task_id: Optional[str],
    ) -> None:
        """Test get message returns and unpacks message."""
        packed_message_body = msgpack.dumps(b"some message")
        expected_sent_by = "some modeller"
        expected_mailbox_id = "some mailbox"
        expected_reply_to_mailbox = "some reply to mailbox"
        expected_receipt_handle = "valid receipt handle"
        expected_recipient = "someRecipient"
        expected_timestamp = datetime.now().isoformat()

        mock_sleep = mocker.patch("asyncio.sleep")

        grpc_stub.GetBitfountMessage.return_value = GrpcBitfountMessage(
            messageType=_BitfountMessageType.MODEL_PARAMETERS.value,
            body=packed_message_body,
            sender=expected_sent_by,
            senderMailboxId=expected_reply_to_mailbox,
            receiptHandle=expected_receipt_handle,
            recipient=expected_recipient,
            recipientMailboxId=expected_mailbox_id,
            podMailboxIds={},
            timestamp=expected_timestamp,
            # Mimic when Grpc message doesn't have taskId
            **({"taskId": opt_task_id} if opt_task_id else {}),
        )
        grpc_stub.AcknowledgeMessage.return_value = SuccessResponse()

        message = await message_service._get_message(expected_mailbox_id)

        # Retrieved message is as expected
        assert message == _BitfountMessage(
            message_type=_BitfountMessageType.MODEL_PARAMETERS,
            body=packed_message_body,
            recipient=expected_recipient,
            recipient_mailbox_id=expected_mailbox_id,
            sender=expected_sent_by,
            sender_mailbox_id=expected_reply_to_mailbox,
            timestamp=expected_timestamp,
            receipt_handle=expected_receipt_handle,
            pod_mailbox_ids={},
            task_id=opt_task_id,
        )

        # Message was requested correctly
        grpc_stub.GetBitfountMessage.assert_called_once_with(
            CommunicationDetails(mailboxId=expected_mailbox_id),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # Message was acknowledged correctly
        grpc_stub.AcknowledgeMessage.assert_called_once_with(
            Acknowledgement(
                mailboxId=expected_mailbox_id,
                receiptHandle=expected_receipt_handle,
                deleteMailbox=False,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # We didn't sleep unnecessarily
        mock_sleep.assert_not_awaited()

    async def test_get_message_successful_mailbox_delete_flag_set_on_task_complete(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        mocker: MockerFixture,
        opt_task_id: Optional[str],
    ) -> None:
        """Test get message and delete mailbox.

        When a pod receives a TASK_COMPLETE message we acknowledge it,
        informing the message service that the task queue can now
        be deleted.
        """
        packed_message_body = msgpack.dumps(b"some message")
        expected_sent_by = "some modeller"
        expected_mailbox_id = "some mailbox"
        expected_reply_to_mailbox = "some reply to mailbox"
        expected_receipt_handle = "valid receipt handle"
        expected_recipient = "someRecipient"
        expected_timestamp = datetime.now().isoformat()

        mock_sleep = mocker.patch("asyncio.sleep")

        grpc_stub.GetBitfountMessage.return_value = GrpcBitfountMessage(
            messageType=_BitfountMessageType.TASK_COMPLETE.value,
            body=packed_message_body,
            sender=expected_sent_by,
            senderMailboxId=expected_reply_to_mailbox,
            receiptHandle=expected_receipt_handle,
            recipient=expected_recipient,
            recipientMailboxId=expected_mailbox_id,
            podMailboxIds={},
            timestamp=expected_timestamp,
            # Mimic when Grpc message doesn't have taskId
            **({"taskId": opt_task_id} if opt_task_id else {}),
        )
        grpc_stub.AcknowledgeMessage.return_value = SuccessResponse()

        message = await message_service._get_message(expected_mailbox_id)

        # Retrieved message is as expected
        assert message == _BitfountMessage(
            message_type=_BitfountMessageType.TASK_COMPLETE,
            body=packed_message_body,
            recipient=expected_recipient,
            recipient_mailbox_id=expected_mailbox_id,
            sender=expected_sent_by,
            sender_mailbox_id=expected_reply_to_mailbox,
            timestamp=expected_timestamp,
            receipt_handle=expected_receipt_handle,
            pod_mailbox_ids={},
            task_id=opt_task_id,
        )

        # Message was requested correctly
        grpc_stub.GetBitfountMessage.assert_called_once_with(
            CommunicationDetails(mailboxId=expected_mailbox_id),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # Message was acknowledged correctly
        grpc_stub.AcknowledgeMessage.assert_called_once_with(
            Acknowledgement(
                mailboxId=expected_mailbox_id,
                receiptHandle=expected_receipt_handle,
                deleteMailbox=True,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # We didn't sleep unnecessarily
        mock_sleep.assert_not_awaited()

    async def test_get_message_downloads_from_large_object_storage(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        mock_download_from_s3: AsyncMock,
        mocker: MockerFixture,
        opt_task_id: Optional[str],
        s3_download_url: _S3PresignedURL,
    ) -> None:
        """Test get message downloads from blob storage."""
        mock_async_sleep = mocker.patch("asyncio.sleep")

        # Construct GrpcBitfountMessage
        expected_message_body = s3_download_url
        packed_message_body = msgpack.dumps(expected_message_body)
        expected_sent_by = "some_modeller"
        expected_mailbox_id = "some_mailbox"
        expected_reply_to_mailbox = "some reply to mailbox"
        expected_receipt_handle = "valid receipt handle"
        expected_recipient = "some_recipient"
        expected_timestamp = datetime.now().isoformat()

        grpc_stub.GetBitfountMessage.return_value = GrpcBitfountMessage(
            messageType=_BitfountMessageType.TRAINING_UPDATE.value,
            body=packed_message_body,
            sender=expected_sent_by,
            senderMailboxId=expected_reply_to_mailbox,
            recipient=expected_recipient,
            recipientMailboxId=expected_mailbox_id,
            receiptHandle=expected_receipt_handle,
            timestamp=expected_timestamp,
            # Mimic when Grpc message doesn't have taskId
            **({"taskId": opt_task_id} if opt_task_id else {}),  # type: ignore[arg-type] # Reason: workaround to allow optional kwarg presence # noqa: B950
        )

        # Mock out message acknowledgement
        grpc_stub.AcknowledgeMessage.return_value = SuccessResponse()

        # Mock out downloading from S3
        # Messages are inherently packed when stored in S3, but we're mocking out
        # the return here so can avoid that.
        message_body_in_blob_storage = b"here is the actual message"
        mock_download_from_s3.return_value = message_body_in_blob_storage

        # Retrieve message
        message = await message_service._get_message(expected_mailbox_id)

        # Retrieved message is as expected
        assert (
            _BitfountMessage(
                message_type=_BitfountMessageType.TRAINING_UPDATE,
                body=message_body_in_blob_storage,
                recipient=expected_recipient,
                recipient_mailbox_id=expected_mailbox_id,
                sender=expected_sent_by,
                sender_mailbox_id=expected_reply_to_mailbox,
                timestamp=expected_timestamp,
                receipt_handle=expected_receipt_handle,
                pod_mailbox_ids={},
                task_id=opt_task_id,
            )
            == message
        )

        # Message was requested correctly
        grpc_stub.GetBitfountMessage.assert_called_once_with(
            CommunicationDetails(mailboxId=expected_mailbox_id),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # Message was acknowledged correctly
        grpc_stub.AcknowledgeMessage.assert_called_once_with(
            Acknowledgement(
                mailboxId=expected_mailbox_id,
                receiptHandle=expected_receipt_handle,
                deleteMailbox=False,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # Download was called correctly
        mock_download_from_s3.assert_awaited_once_with(s3_download_url)

        # Check we didn't sleep unnecessarily
        mock_async_sleep.assert_not_awaited()

    async def test_get_message_none_found(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error_maker: RpcErrorMaker,
    ) -> None:
        """Test get message when there are none."""
        expected_mailbox_id = "some mailbox"

        error = rpc_error_maker("No message found", StatusCode.NOT_FOUND)

        grpc_stub.GetBitfountMessage.side_effect = error

        message = await message_service._get_message(expected_mailbox_id)

        # Retrieved message is as expected
        assert message is None

        # Message was requested correctly
        grpc_stub.GetBitfountMessage.assert_called_once_with(
            CommunicationDetails(mailboxId=expected_mailbox_id),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # Nothing to acknowledge
        grpc_stub.AcknowledgeMessage.assert_not_called()

        # We didn't sleep unnecessarily
        remove_grpc_retry_backoff_sleep.assert_not_awaited()

    @pytest.mark.parametrize(
        argnames="status_code",
        # We remove NOT_FOUND as this is tested separately
        argvalues=_GRPC_ERROR_CODES - {StatusCode.NOT_FOUND},
        ids=lambda sc: f"status_code={sc.name}",
    )
    async def test_get_message_throws_error_when_never_successful(
        self,
        caplog: LogCaptureFixture,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error_maker: RpcErrorMaker,
        status_code: StatusCode,
    ) -> None:
        """Test get message eventually throws error if errors occur."""
        # Also need to remove NOT_FOUND from retryable status codes
        if status_code in utils._RETRY_STATUS_CODES:
            retries = True
            expected_num_calls = utils._DEFAULT_MAX_RETRIES + 1
        else:
            retries = False
            expected_num_calls = 1
        expected_num_retries = expected_num_calls - 1

        expected_mailbox_id = "some mailbox"

        grpc_stub.GetBitfountMessage.side_effect = rpc_error_maker(
            "an error", status_code
        )

        with raises(
            BitfountMessageServiceError,
            match=re.escape(
                "Issue retrieving message from mailbox. See debug log for details."
            ),
        ), caplog.at_level(logging.DEBUG):
            await message_service._get_message(expected_mailbox_id)

        # Message was requested correctly up to max attempts
        expected_get_call = call(
            CommunicationDetails(mailboxId=expected_mailbox_id),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )
        assert (
            grpc_stub.GetBitfountMessage.call_args_list
            == [expected_get_call] * expected_num_calls
        )

        # Nothing to acknowledge
        grpc_stub.AcknowledgeMessage.assert_not_called()

        # Check underlying exception was logged to DEBUG
        debug_logs = get_debug_logs(caplog, full_details=True)
        assert "RpcError: an error" in debug_logs

        # Check retry messages in debug logs and sleep called if required
        if retries:
            assert remove_grpc_retry_backoff_sleep.await_count == expected_num_retries
            for i in range(1, expected_num_retries + 1):
                assert re.search(
                    rf"gRPC error occurred: .* an error; .* \(attempt {i}\)",
                    debug_logs,
                )
        else:
            remove_grpc_retry_backoff_sleep.assert_not_awaited()

    async def test_get_message_throws_error_but_is_eventually_successful(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        opt_task_id: Optional[str],
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error: RpcError,
    ) -> None:
        """Test get message doesn't throw error, retries until threshold is reached."""
        packed_message_body = msgpack.dumps(b"some message")
        expected_sent_by = "some modeller"
        expected_mailbox_id = "some mailbox"
        expected_reply_to_mailbox = "some reply to mailbox"
        expected_receipt_handle = "valid receipt handle"
        expected_recipient = "someRecipient"
        expected_timestamp = datetime.now().isoformat()

        grpc_stub.GetBitfountMessage.side_effect = [
            rpc_error,
            GrpcBitfountMessage(
                messageType=_BitfountMessageType.MODEL_PARAMETERS.value,
                body=packed_message_body,
                sender=expected_sent_by,
                senderMailboxId=expected_reply_to_mailbox,
                receiptHandle=expected_receipt_handle,
                recipient=expected_recipient,
                recipientMailboxId=expected_mailbox_id,
                podMailboxIds={},
                timestamp=expected_timestamp,
                # Mimic when Grpc message doesn't have taskId
                **({"taskId": opt_task_id} if opt_task_id else {}),
            ),
        ]
        grpc_stub.AcknowledgeMessage.return_value = SuccessResponse()

        message = await message_service._get_message(expected_mailbox_id)

        # Retrieved message is as expected
        assert message == _BitfountMessage(
            message_type=_BitfountMessageType.MODEL_PARAMETERS,
            body=packed_message_body,
            recipient=expected_recipient,
            recipient_mailbox_id=expected_mailbox_id,
            sender=expected_sent_by,
            sender_mailbox_id=expected_reply_to_mailbox,
            pod_mailbox_ids={},
            timestamp=expected_timestamp,
            receipt_handle=expected_receipt_handle,
            task_id=opt_task_id,
        )

        # Message was requested correctly
        expected_get_message_call = call(
            CommunicationDetails(mailboxId=expected_mailbox_id),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )
        grpc_stub.GetBitfountMessage.assert_has_calls([expected_get_message_call] * 2)
        assert grpc_stub.GetBitfountMessage.call_count == 2

        # Message was acknowledged correctly
        grpc_stub.AcknowledgeMessage.assert_called_once_with(
            Acknowledgement(
                mailboxId=expected_mailbox_id,
                receiptHandle=expected_receipt_handle,
                deleteMailbox=False,
            ),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )

        # We didn't sleep unnecessarily
        remove_grpc_retry_backoff_sleep.assert_awaited_once()

    async def test_get_message_is_called_again_if_acknowledgement_fails(
        self,
        expected_request_metadata: List[Tuple[str, str]],
        grpc_stub: Mock,
        message_service: _MessageService,
        opt_task_id: Optional[str],
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error: RpcError,
    ) -> None:
        """Tests that the message is re-fetched if the acknowledgement fails.

        If acknowledgement fails then it may be due to an expired receipt handle,
        to avoid this we make sure that the message is retrieved again before retrying,
        as this will fetch a new receipt handle
        """
        packed_message_body = msgpack.dumps(b"some message")
        expected_sent_by = "some modeller"
        expected_mailbox_id = "some mailbox"
        expected_reply_to_mailbox = "some reply to mailbox"
        expected_receipt_handle = "invalid receipt handle"
        expected_second_receipt_handle = "valid receipt handle"
        expected_recipient = "someRecipient"
        expected_timestamp = datetime.now().isoformat()

        grpc_stub.GetBitfountMessage.side_effect = [
            GrpcBitfountMessage(
                messageType=_BitfountMessageType.MODEL_PARAMETERS.value,
                body=packed_message_body,
                sender=expected_sent_by,
                senderMailboxId=expected_reply_to_mailbox,
                receiptHandle=expected_receipt_handle,
                recipient=expected_recipient,
                recipientMailboxId=expected_mailbox_id,
                podMailboxIds={},
                timestamp=expected_timestamp,
                # Mimic when Grpc message doesn't have taskId
                **({"taskId": opt_task_id} if opt_task_id else {}),
            ),
            GrpcBitfountMessage(
                messageType=_BitfountMessageType.MODEL_PARAMETERS.value,
                body=packed_message_body,
                sender=expected_sent_by,
                senderMailboxId=expected_reply_to_mailbox,
                receiptHandle=expected_second_receipt_handle,
                recipient=expected_recipient,
                recipientMailboxId=expected_mailbox_id,
                podMailboxIds={},
                timestamp=expected_timestamp,
                # Mimic when Grpc message doesn't have taskId
                **({"taskId": opt_task_id} if opt_task_id else {}),
            ),
        ]

        grpc_stub.AcknowledgeMessage.side_effect = [rpc_error, SuccessResponse()]

        message = await message_service._get_message(expected_mailbox_id)

        # Retrieved message is as expected
        assert message == _BitfountMessage(
            message_type=_BitfountMessageType.MODEL_PARAMETERS,
            body=packed_message_body,
            recipient=expected_recipient,
            recipient_mailbox_id=expected_mailbox_id,
            sender=expected_sent_by,
            sender_mailbox_id=expected_reply_to_mailbox,
            pod_mailbox_ids={},
            timestamp=expected_timestamp,
            receipt_handle=expected_second_receipt_handle,
            task_id=opt_task_id,
        )

        # Message was requested correctly
        expected_get_message_call = call(
            CommunicationDetails(mailboxId=expected_mailbox_id),
            metadata=expected_request_metadata,
            timeout=utils._DEFAULT_TIMEOUT,
        )
        grpc_stub.GetBitfountMessage.assert_has_calls([expected_get_message_call] * 2)
        assert grpc_stub.GetBitfountMessage.call_count == 2

        # Message was acknowledged correctly
        grpc_stub.AcknowledgeMessage.assert_has_calls(
            [
                call(
                    Acknowledgement(
                        mailboxId=expected_mailbox_id,
                        receiptHandle=expected_receipt_handle,
                        deleteMailbox=False,
                    ),
                    metadata=expected_request_metadata,
                    timeout=utils._DEFAULT_TIMEOUT,
                ),
                call(
                    Acknowledgement(
                        mailboxId=expected_mailbox_id,
                        receiptHandle=expected_second_receipt_handle,
                        deleteMailbox=False,
                    ),
                    metadata=expected_request_metadata,
                    timeout=utils._DEFAULT_TIMEOUT,
                ),
            ]
        )
        assert grpc_stub.AcknowledgeMessage.call_count == 2

        # Sleep was called between errors
        remove_grpc_retry_backoff_sleep.assert_awaited_once()

    async def test_poll_for_message_eventually_retrieves_message(
        self,
        message_service: _MessageService,
        mocker: MockerFixture,
        opt_task_id: Optional[str],
    ) -> None:
        """Test poll for message receives a message after a few attempts."""
        expected_message = _BitfountMessage(
            message_type=_BitfountMessageType.UNDEFINED,
            body=b"hello world",
            recipient="to_you",
            recipient_mailbox_id="your_mailbox_id",
            sender="from_me",
            sender_mailbox_id="my_mailbox_id",
            task_id=opt_task_id,
        )
        expected_mailbox = "someMailboxID"
        mocked__get_message = mocker.patch.object(
            message_service,
            "_get_message",
            AsyncMock(
                side_effect=[
                    None,
                    None,
                    expected_message,
                ]
            ),
        )

        # There is no anext() built-in so have to do it this way
        message = await message_service.poll_for_messages(
            expected_mailbox, stop_event=Mock(**{"is_set.return_value": False})
        ).__anext__()

        assert message == expected_message
        mocked__get_message.assert_has_awaits([call(expected_mailbox)] * 3)
        assert mocked__get_message.await_count == 3

    async def test_poll_for_message_throws_error(
        self,
        message_service: _MessageService,
        mocker: MockerFixture,
        rpc_error: RpcError,
    ) -> None:
        """Test poll for message throws RpcError."""
        expected_mailbox = "someMailboxID"
        mocked__get_message = mocker.patch.object(
            message_service, "_get_message", AsyncMock(side_effect=[None, rpc_error])
        )

        with raises(RpcError):
            # There is no anext() built-in so have to do it this way
            await message_service.poll_for_messages(
                expected_mailbox, stop_event=Mock(**{"is_set.return_value": False})
            ).__anext__()

        mocked__get_message.assert_has_awaits([call(expected_mailbox)] * 2)
        assert mocked__get_message.await_count == 2

    async def test_maybe_upload_to_large_object_storage_small_message(
        self,
        grpc_stub: Mock,
        message_service: _MessageService,
        mock_upload_to_s3: AsyncMock,
        opt_task_id: Optional[str],
        s3_download_url: _S3PresignedURL,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Test small messages are sent to message service."""
        # Set output as expected fields
        grpc_stub.GetLargeObjectStorage.return_value = BlobStorageData(
            uploadUrl=s3_upload_url,
            downloadUrl=s3_download_url,
            uploadFields=s3_upload_fields,
        )

        # Construct message
        sender = "someSender"
        sender_mailbox_id = "someSenderMailboxId"
        expected_body = msgpack.dumps({"some": "body"})
        bitfount_message = _BitfountMessage(
            body=expected_body,  #
            message_type=_BitfountMessageType.UNDEFINED,
            recipient="someRecipient",
            recipient_mailbox_id="someMailboxId",
            sender=sender,
            sender_mailbox_id=sender_mailbox_id,
            task_id=opt_task_id,
        )

        body = await message_service._maybe_upload_to_large_object_storage(
            bitfount_message
        )

        # Check the upload function wasn't awaited
        mock_upload_to_s3.assert_not_awaited()
        # Check that message body is unchanged
        assert body == expected_body

    async def test_maybe_upload_task_to_large_object_storage_small_message(
        self,
        grpc_stub: Mock,
        message_service: _MessageService,
        mock_upload_to_s3: AsyncMock,
        opt_task_id: Optional[str],
        s3_download_url: _S3PresignedURL,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Test small messages are sent to message service."""
        # Set output as expected fields
        grpc_stub.GetLargeObjectStorage.return_value = BlobStorageData(
            uploadUrl=s3_upload_url,
            downloadUrl=s3_download_url,
            uploadFields=s3_upload_fields,
        )

        tasks_per_pod = {"pod1": b"some task"}

        new_task = await message_service._maybe_upload_task_to_large_object_storage(
            tasks_per_pod
        )

        # Check the upload function wasn't awaited
        mock_upload_to_s3.assert_not_awaited()
        # check that the tasks are not modified
        assert new_task == tasks_per_pod

    async def test_maybe_upload_task_to_large_object_storage_large_message(
        self,
        grpc_stub: Mock,
        message_service: _MessageService,
        mock_upload_to_s3: AsyncMock,
        opt_task_id: Optional[str],
        s3_download_url: _S3PresignedURL,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Test large task object gets uploaded."""
        # Set output as expected fields
        grpc_stub.GetLargeObjectStorage.return_value = BlobStorageData(
            uploadUrl=s3_upload_url,
            downloadUrl=s3_download_url,
            uploadFields=s3_upload_fields,
        )

        # Construct tasks
        expected_body = b"a" * (_SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES + 1)
        tasks_per_pod = {"someSender/somePod": expected_body}
        new_tasks = await message_service._maybe_upload_task_to_large_object_storage(
            tasks_per_pod
        )

        # Assert upload code is called
        mock_upload_to_s3.assert_awaited_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            data=expected_body,
        )
        # Assert download URL is returned (packed) to user
        assert new_tasks["someSender/somePod"] == msgpack.dumps(s3_download_url)

    async def test_maybe_upload_task_to_large_object_storage_fails_too_large_message(
        self, message_service: _MessageService, mocker: MockerFixture
    ) -> None:
        """Tests that exception raised if message body too big for storage."""
        # Patch out schema size calculation so we can set it
        too_large_size = _MAX_STORAGE_SIZE_BYTES + 1
        mock_data_sizer = mocker.patch(
            "bitfount.federated.transport.message_service._get_packed_data_object_size"
        )
        mock_data_sizer = mocker.patch(
            "bitfount.federated.transport.message_service._get_packed_data_object_size"
        )
        mock_data_sizer.return_value = too_large_size

        tasks_per_pod = {"pod1": Mock()}
        tasks_per_pod["pod1"].__len__ = lambda _: too_large_size

        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Message body is too large to upload: "
                f"expected max {_MAX_STORAGE_SIZE_MEGABYTES} megabytes, "
                f"got {_get_mb_from_bytes(too_large_size).fractional} megabytes."
            ),
        ):
            await message_service._maybe_upload_task_to_large_object_storage(
                tasks_per_pod  # type: ignore[arg-type] # Reason: Mocking for testing purposes # noqa: B950
            )

    async def test_maybe_upload_to_large_object_storage_large_message(
        self,
        grpc_stub: Mock,
        message_service: _MessageService,
        mock_upload_to_s3: AsyncMock,
        opt_task_id: Optional[str],
        s3_download_url: _S3PresignedURL,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Test large object gets uploaded."""
        # Set output as expected fields
        grpc_stub.GetLargeObjectStorage.return_value = BlobStorageData(
            uploadUrl=s3_upload_url,
            downloadUrl=s3_download_url,
            uploadFields=s3_upload_fields,
        )

        # Construct message
        sender = "someSender/somePod"
        sender_mailbox_id = "someSenderMailboxId"
        expected_body = b"a" * (_SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES + 1)
        bitfount_message = _BitfountMessage(
            body=expected_body,
            message_type=_BitfountMessageType.UNDEFINED,
            recipient="someRecipient",
            recipient_mailbox_id="someMailboxId",
            sender=sender,
            sender_mailbox_id=sender_mailbox_id,
            task_id=opt_task_id,
        )

        body = await message_service._maybe_upload_to_large_object_storage(
            bitfount_message
        )

        # Assert upload code is called
        mock_upload_to_s3.assert_awaited_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            data=expected_body,
        )
        # Assert download URL is returned (packed) to user
        assert body == msgpack.dumps(s3_download_url)

    async def test_maybe_upload_to_large_object_storage_fails_too_large_message(
        self, message_service: _MessageService, mocker: MockerFixture
    ) -> None:
        """Tests that exception raised if message body too big for storage."""
        # Patch out schema size calculation so we can set it
        too_large_size = _MAX_STORAGE_SIZE_BYTES + 1
        mock_data_sizer = mocker.patch(
            "bitfount.federated.transport.message_service._get_packed_data_object_size"
        )
        mock_data_sizer.return_value = too_large_size

        # Create mock message, mock length is long enough to consider uploading
        mock_message = create_dataclass_mock(_BitfountMessage)
        mock_message.body.__len__ = lambda _: too_large_size

        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Message body is too large to upload: "
                f"expected max {_MAX_STORAGE_SIZE_MEGABYTES} megabytes, "
                f"got {_get_mb_from_bytes(too_large_size).fractional} megabytes."
            ),
        ):
            await message_service._maybe_upload_to_large_object_storage(mock_message)

    async def test_maybe_upload_to_large_object_storage_bad_upload(
        self,
        grpc_stub: Mock,
        message_service: _MessageService,
        mock_upload_to_s3: AsyncMock,
        opt_task_id: Optional[str],
        s3_download_url: _S3PresignedURL,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Test failed upload throws exception."""
        # Set output as expected fields
        grpc_stub.GetLargeObjectStorage.return_value = BlobStorageData(
            uploadUrl=s3_upload_url,
            downloadUrl=s3_download_url,
            uploadFields=s3_upload_fields,
        )

        # Construct message
        sender = "someSender"
        sender_mailbox_id = "someSenderMailboxId"
        expected_body = b"a" * (_SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES + 1)
        bitfount_message = _BitfountMessage(
            body=expected_body,
            message_type=_BitfountMessageType.UNDEFINED,
            recipient="someRecipient",
            recipient_mailbox_id="someMailboxId",
            sender=sender,
            sender_mailbox_id=sender_mailbox_id,
            task_id=opt_task_id,
        )

        # Set upload mock to throw exception
        mock_upload_to_s3.side_effect = HTTPError("TEST ERROR")

        with pytest.raises(
            RequestException,
            match=re.escape(
                "Failed to upload message to large message storage. Cause: TEST ERROR."
            ),
        ):
            await message_service._maybe_upload_to_large_object_storage(
                bitfount_message
            )

        # Assert upload function called correctly even if errored
        mock_upload_to_s3.assert_awaited_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            data=expected_body,
        )

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=_GRPC_ERROR_CODES,
        ids=lambda sc: f"status_code={sc.name}",
    )
    async def test_maybe_upload_to_large_object_storage_rpc_error(
        self,
        caplog: LogCaptureFixture,
        grpc_stub: Mock,
        message_service: _MessageService,
        opt_task_id: Optional[str],
        remove_grpc_retry_backoff_sleep: AsyncMock,
        rpc_error_maker: RpcErrorMaker,
        status_code: StatusCode,
    ) -> None:
        """Test failed upload throws exception."""
        if status_code in utils._RETRY_STATUS_CODES:
            retries = True
            expected_num_calls = utils._DEFAULT_MAX_RETRIES + 1
        else:
            retries = False
            expected_num_calls = 1
        expected_num_retries = expected_num_calls - 1

        # Make GRPC error out
        grpc_stub.GetLargeObjectStorage.side_effect = rpc_error_maker(
            "Failed to create storage", status_code
        )

        # Construct message that should be uploaded
        sender = "someSender"
        sender_mailbox_id = "someSenderMailboxId"
        expected_body = b"a" * (_SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES + 1)
        bitfount_message = _BitfountMessage(
            body=expected_body,
            message_type=_BitfountMessageType.UNDEFINED,
            recipient="someRecipient",
            recipient_mailbox_id="someMailboxId",
            sender=sender,
            sender_mailbox_id=sender_mailbox_id,
            task_id=opt_task_id,
        )

        with pytest.raises(
            BitfountMessageServiceError,
            match=re.escape(
                "Unable to acquire large object storage."
                " See debug logs for more details."
            ),
        ), caplog.at_level(logging.DEBUG):
            await message_service._maybe_upload_to_large_object_storage(
                bitfount_message
            )

        # Check underlying exception was logged to DEBUG
        debug_logs = get_debug_logs(caplog, full_details=True)
        assert "RpcError: Failed to create storage" in debug_logs

        # Check retry messages in debug logs and sleep called if required
        if retries:
            assert remove_grpc_retry_backoff_sleep.await_count == expected_num_retries
            for i in range(1, expected_num_retries + 1):
                assert re.search(
                    rf"gRPC error occurred: .* Failed to create storage;"
                    rf" .* \(attempt {i}\)",
                    debug_logs,
                )
        else:
            remove_grpc_retry_backoff_sleep.assert_not_awaited()

    async def test_upload_large_object_bad_response(
        self,
        mock_upload_to_s3: AsyncMock,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
    ) -> None:
        """Uploading fails due to non 200 response code."""
        # Set upload mock to throw error (non-200 response code)
        mock_upload_to_s3.side_effect = HTTPError("NON-200/201 TEST")
        object_to_upload = b"here is my byte string"

        with pytest.raises(
            RequestException,
            match=re.escape(
                "Failed to upload message to large message storage. "
                "Cause: NON-200/201 TEST."
            ),
        ):
            await _LargeObjectRequestHandler.upload_large_object(
                s3_upload_url, s3_upload_fields, object_to_upload
            )

        # Assert upload function awaited correctly even if errored
        mock_upload_to_s3.assert_awaited_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            data=object_to_upload,
        )

    async def test_download_large_object_bad_response(
        self, mock_download_from_s3: AsyncMock, s3_download_url: _S3PresignedURL
    ) -> None:
        """Downloading fails due to non 200 response code."""
        # Set mock to return HTTP Error (non-200 response code)
        mock_download_from_s3.side_effect = HTTPError("NON-200 TEST ERROR")

        with pytest.raises(
            RequestException,
            match=re.escape(
                "Failed to retrieve message from large message storage. "
                "Cause: NON-200 TEST ERROR."
            ),
        ):
            await _LargeObjectRequestHandler.get_large_object_from_url(s3_download_url)

        # Assert upload function called correctly even if errored
        mock_download_from_s3.assert_awaited_once_with(download_url=s3_download_url)

    def test_save_object_to_local_storage(
        self,
        message_service: _MessageService,
        opt_task_id: Optional[str],
    ) -> None:
        """Tests saving object to local storage."""
        sender = "someSender"
        sender_mailbox_id = "someSenderMailboxId"
        expected_body = b"a" * (_SMALL_MESSAGE_UPPER_LIMIT_SIZE_BYTES + 1)

        bitfount_message = _BitfountMessage(
            body=expected_body,
            message_type=_BitfountMessageType.UNDEFINED,
            recipient="someRecipient",
            recipient_mailbox_id="someMailboxId",
            sender=sender,
            sender_mailbox_id=sender_mailbox_id,
            task_id=opt_task_id,
        )

        filename = message_service._save_object_to_local_storage(bitfount_message)
        assert type(filename) is bytes
        filename_str: str = msgpack.loads(filename)
        assert Path(filename_str).exists()
        with open(filename_str, "rb") as f:
            assert f.read() == expected_body

    async def test_read_local_bitfount_message_from_rpc(
        self, opt_task_id: Optional[str]
    ) -> None:
        """Test reading local object from storage."""
        sender = "someSender"
        mailbox_id = "someSenderMailboxId"
        handle, local_tempfile = tempfile.mkstemp()
        packed_message = msgpack.dumps(local_tempfile)
        expected_message_body = msgpack.dumps(["some message"])
        with os.fdopen(handle, "wb") as f:
            f.write(expected_message_body)
        pod_identifier = "podOwner/somePodName"
        reply_to_mailbox_id = "replyMailboxId"
        expected_timestamp = datetime.now().isoformat()

        grpc_message = GrpcBitfountMessage(
            messageType=_BitfountMessageType.TRAINING_UPDATE.value,
            body=packed_message,
            recipient=pod_identifier,
            recipientMailboxId=mailbox_id,
            sender=sender,
            senderMailboxId=reply_to_mailbox_id,
            timestamp=expected_timestamp,
            # Mimic when Grpc message doesn't have taskId
            **({"taskId": opt_task_id} if opt_task_id else {}),  # type: ignore[arg-type] # Reason: workaround to allow optional kwarg presence # noqa: B950
        )
        bitfount_message = await _BitfountMessage.from_rpc(grpc_message)
        assert type(bitfount_message) == _BitfountMessage
        assert bitfount_message.body == expected_message_body


@unit_test
class TestMessageEncryption:
    """Tests AES message encryption."""

    @fixture
    def original_message(self) -> bytes:
        """Message to encrypt."""
        return b"this is my original message"

    @fixture
    def original_dataframe(self) -> pd.DataFrame:
        """Create DataFrame message to encrypt."""
        data = create_dataset(classification=True)
        return data

    @fixture
    def original_numpyarray(self) -> np.ndarray:
        """Create Numpt Array to encrypt."""
        data = create_dataset(classification=True)
        return data["A"].to_numpy()

    def test_encryption_is_polymorphic(self, original_message: bytes) -> None:
        """Testing that we can decrypt an encrypted message."""
        encryption_key = _AESEncryption.generate_key()

        assert (
            _MessageEncryption.decrypt_incoming_message(
                _MessageEncryption.encrypt_outgoing_message(
                    original_message, encryption_key
                ),
                encryption_key,
            )
            == original_message
        )

    def test_encode_dataframe(self, original_dataframe: pd.DataFrame) -> None:
        """Testing that we can encode a dataframe."""
        # Encode the DataFrame
        encoded_dataframe = msgpack.dumps(original_dataframe, default=msgpackext_encode)
        assert len(encoded_dataframe) > 0

    def test_encode_numpyarray(self, original_numpyarray: np.ndarray) -> None:
        """Testing that we can encode a Numpy Array."""
        # Encode the Numpy Array
        encoded_dataframe = msgpack.dumps(
            original_numpyarray, default=msgpackext_encode
        )
        assert len(encoded_dataframe) > 0

    def test_encryption_is_polymorphic_dataframe(
        self, original_dataframe: pd.DataFrame
    ) -> None:
        """Testing that we can decrypt an encrypted DataFrame."""
        encryption_key = _AESEncryption.generate_key()

        # Encode and encrypt the DataFrame
        encoded_dataframe = msgpack.dumps(original_dataframe, default=msgpackext_encode)
        encrypted_message = _MessageEncryption.encrypt_outgoing_message(
            encoded_dataframe, encryption_key
        )
        # Decrypt and decode the DataFrame
        decrypted_message = _MessageEncryption.decrypt_incoming_message(
            encrypted_message, encryption_key
        )
        decoded_dataframe = msgpack.loads(decrypted_message, ext_hook=msgpackext_decode)

        pd.testing.assert_frame_equal(original_dataframe, decoded_dataframe)

    def test_encryption_is_polymorphic_numpyarray(
        self, original_numpyarray: np.ndarray
    ) -> None:
        """Testing that we can decrypt an encrypted Numpy Array."""
        encryption_key = _AESEncryption.generate_key()

        # Encode and encrypt the Numpy Array
        encoded_array = msgpack.dumps(original_numpyarray, default=msgpackext_encode)
        encrypted_message = _MessageEncryption.encrypt_outgoing_message(
            encoded_array, encryption_key
        )
        # Decrypt and decode the Numpy Array
        decrypted_message = _MessageEncryption.decrypt_incoming_message(
            encrypted_message, encryption_key
        )
        decoded_numpyarray = msgpack.loads(
            decrypted_message, ext_hook=msgpackext_decode
        )

        assert np.array_equal(original_numpyarray, decoded_numpyarray)

    def test_encrypted_message_is_different(self, original_message: bytes) -> None:
        """Sanity checking we haven't just returned the message."""
        encryption_key = _AESEncryption.generate_key()

        encrypted_message = _MessageEncryption.encrypt_outgoing_message(
            original_message, encryption_key
        )

        assert encrypted_message != original_message

    def test_provided_encryption_key_is_used(self, original_message: bytes) -> None:
        """Sanity checking the key actually serves a purpose."""
        encrypted_message = _MessageEncryption.encrypt_outgoing_message(
            original_message, _AESEncryption.generate_key()
        )

        wrong_encryption_key = _AESEncryption.generate_key()

        with pytest.raises(
            DecryptError, match=re.escape("Unable to decrypt ciphertext")
        ):
            _MessageEncryption.decrypt_incoming_message(
                encrypted_message, wrong_encryption_key
            )


@unit_test
class TestBitfountMessage:
    """Tests for BitfountMessage."""

    def test_timestamps_unique(self) -> None:
        """Tests the timestamps for two BitfountMessages are different.

        This will help avoid a regression bug where we had the same default
        timestamp for every instance of the class due the nature of default arg
        values in dataclasses.
        """
        bm1 = _BitfountMessage(
            message_type=Mock(),
            body=b"",
            recipient="recipient",
            recipient_mailbox_id="recipient_mailbox_id",
            sender="sender",
            sender_mailbox_id="sender_mailbox_id",
            task_id="task_id",
        )
        time.sleep(1)  # Windows gives error on this test without the sleep
        bm2 = _BitfountMessage(
            message_type=Mock(),
            body=b"",
            recipient="recipient",
            recipient_mailbox_id="recipient_mailbox_id",
            sender="sender",
            sender_mailbox_id="sender_mailbox_id",
            task_id="task_id",
        )
        assert bm1.timestamp != bm2.timestamp

    def test_decrypt_rsa(self) -> None:
        """Test that decrypt_rsa() method works."""
        # Create RSA encrypted message
        msg_contents = "Hello, world!"
        private_key, public_key = _RSAEncryption.generate_key_pair()
        encypted_msg_contents = _RSAEncryption.encrypt(
            msgpack.dumps(msg_contents), public_key
        )

        # Create message with RSA encrypted body
        bitfount_message = _BitfountMessage(
            message_type=Mock(),
            body=encypted_msg_contents,
            recipient=Mock(),
            recipient_mailbox_id=Mock(),
            sender=Mock(),
            sender_mailbox_id=Mock(),
            task_id=Mock(),
        )
        decrypted_bitfount_message = bitfount_message.decrypt_rsa(private_key)

        # Check decrypted body is same as original contents
        assert decrypted_bitfount_message.body == msg_contents
        # Check other attributes are unchanged
        assert decrypted_bitfount_message.message_type == bitfount_message.message_type
        assert decrypted_bitfount_message.recipient == bitfount_message.recipient
        assert (
            decrypted_bitfount_message.recipient_mailbox_id
            == bitfount_message.recipient_mailbox_id
        )
        assert decrypted_bitfount_message.sender == bitfount_message.sender
        assert (
            decrypted_bitfount_message.sender_mailbox_id
            == bitfount_message.sender_mailbox_id
        )
        assert (
            decrypted_bitfount_message.pod_mailbox_ids
            == bitfount_message.pod_mailbox_ids
        )
        assert decrypted_bitfount_message.timestamp == bitfount_message.timestamp
        assert decrypted_bitfount_message.task_id == bitfount_message.task_id

    def test_default_task_id(self) -> None:
        """Tests that if a task_id is not specified, it is None."""
        bm = _BitfountMessage(
            message_type=Mock(),
            body=b"",
            recipient="recipient",
            recipient_mailbox_id="recipient_mailbox_id",
            sender="sender",
            sender_mailbox_id="sender_mailbox_id",
        )
        assert bm.task_id is None

    async def test_from_rpc_replaces_None_task_id(self) -> None:
        """Tests that if GRPC taskId is None, task_id is None."""
        grpc_message = GrpcBitfountMessage(
            messageType=_BitfountMessageType.JOB_ACCEPT.value,
            body=b"Hello world!",
            recipient="recipient",
            recipientMailboxId="recipientMailboxId",
            sender="sender",
            senderMailboxId="senderMailboxId",
            timestamp=time.asctime(),
            taskId=None,
        )
        bm = await _BitfountMessage.from_rpc(grpc_message)
        assert bm.task_id is None

    async def test_from_rpc_replaces_empty_task_id(self) -> None:
        """Tests that if GRPC taskId is not specified, task_id is None."""
        grpc_message = GrpcBitfountMessage(
            messageType=_BitfountMessageType.JOB_ACCEPT.value,
            body=b"Hello world!",
            recipient="recipient",
            recipientMailboxId="recipientMailboxId",
            sender="sender",
            senderMailboxId="senderMailboxId",
            timestamp=time.asctime(),
        )
        bm = await _BitfountMessage.from_rpc(grpc_message)
        assert bm.task_id is None


@unit_test
class TestDecryptedBitfountMessage:
    """Tests for BitfountMessage."""

    def test_timestamps_unique(self) -> None:
        """Tests the timestamps for two DecryptedBitfountMessages are different.

        This will help avoid a regression bug where we had the same default
        timestamp for every instance of the class due the nature of default arg
        values in dataclasses.
        """
        dbm1 = _DecryptedBitfountMessage(
            message_type=Mock(),
            body=Mock(),
            recipient="recipient",
            recipient_mailbox_id="recipient_mailbox_id",
            sender="sender",
            sender_mailbox_id="sender_mailbox_id",
            task_id="task_id",
        )
        time.sleep(1)  # Windows gives error on this test without the sleep
        dbm2 = _DecryptedBitfountMessage(
            message_type=Mock(),
            body=Mock(),
            recipient="recipient",
            recipient_mailbox_id="recipient_mailbox_id",
            sender="sender",
            sender_mailbox_id="sender_mailbox_id",
            task_id="task_id",
        )
        assert dbm1.timestamp != dbm2.timestamp


@unit_test
def test_msgpackext_encode_returns_obj() -> None:
    """Tests msgpack_encode returns same obj if not np or pd."""
    obj = Mock()
    assert msgpackext_encode(obj) == obj


@unit_test
def test_msgpackext_decode_returns_obj() -> None:
    """Tests msgpack_decode returns same obj if not np or pd."""
    obj = Mock()
    assert msgpackext_decode(code=0, obj=obj) == obj
