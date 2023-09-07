"""Tests that modeller can initiate training with Pods."""
from __future__ import annotations

from collections import namedtuple
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Tuple
from unittest.mock import Mock, call, create_autospec

from grpc import RpcError
import msgpack
import pytest
from pytest import LogCaptureFixture, fixture, raises
from pytest_mock import MockerFixture

from bitfount.federated.authorisation_checkers import IdentityVerificationMethod
from bitfount.federated.encryption import _AESEncryption, _RSAEncryption
from bitfount.federated.exceptions import BitfountTaskStartError
from bitfount.federated.task_requests import (
    _EncryptedTaskRequest,
    _SignedEncryptedTaskRequest,
    _TaskRequest,
    _TaskRequestMessage,
)
from bitfount.federated.transport.base_transport import _run_func_and_listen_to_mailbox
from bitfount.federated.transport.handlers import _AsyncMultipleResponsesHandler
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _DecryptedBitfountMessage,
    _MessageEncryption,
    _MessageService,
)
from bitfount.federated.transport.modeller_transport import (
    _get_parameter_updates_from_workers,
    _get_psi_datasets_from_workers,
    _get_public_key,
    _get_training_metrics_from_workers,
    _ModellerMailbox,
    _parameter_updates_handler,
    _psi_dataset_handler,
    _public_key_handler,
    _training_metrics_handler,
    _WorkerMailboxDetails,
)
from bitfount.federated.transport.protos.messages_pb2 import TaskMetadata
from bitfount.federated.transport.types import (
    _OIDCAuthFlowResponse,
    _OIDCClientID,
    _PodDeviceCodeDetails,
)
from bitfount.federated.types import (
    SerializedAlgorithm,
    SerializedProtocol,
    _PodResponseType,
    _TaskRequestMessageGenerator,
)
from bitfount.types import _SerializedWeights
from tests.utils import PytestRequest
from tests.utils.fixtures import (
    KeyBasedGenerator,
    MessageOrException,
    PollForMessagesPatcher,
)
from tests.utils.helper import get_info_logs, unit_test

WorkerDetails = namedtuple(
    "WorkerDetails", ["pod_identifier", "mailbox_id", "aes_encryption_key"]
)


@fixture
def modeller_name() -> str:
    """Name of the modeller."""
    return "modeller"


@fixture
def modeller_mailbox_id() -> str:
    """A fake modeller mailbox id."""
    return "modeller_mailbox_id"


@fixture
def pod_identifiers() -> List[str]:
    """List of pod identifiers."""
    return ["user1/pod_1", "user2/pod_2", "user3/pod_3"]


@fixture
def worker_mailbox_ids(pod_identifiers: List[str]) -> Dict[str, str]:
    """A dict of pod identifiers to worker mailboxes IDs."""
    return {
        pod_identifier: f"worker_mailbox_id_{idx}"
        for idx, pod_identifier in enumerate(pod_identifiers)
    }


@fixture
def worker_mailbox_details(worker_mailbox_ids: Dict[str, str]) -> List[WorkerDetails]:
    """Provides an indexable version of worker mailbox IDs."""
    # Need to be able to more easily index into the worker_mailbox_ids
    worker_details = [
        WorkerDetails(pod_identifier, mailbox_id, b"aes_encryption_key")
        for pod_identifier, mailbox_id in worker_mailbox_ids.items()
    ]
    return worker_details


@fixture
def pod_public_keys(pod_identifiers: List[str]) -> Dict[str, Mock]:
    """Mocked out public keys for pods."""
    return {pod_identifier: Mock() for pod_identifier in pod_identifiers}


@fixture
def aes_keys() -> List[bytes]:
    """AES keys to use in encrypting."""
    return [_AESEncryption.generate_key() for _ in range(3)]


@fixture
def worker_mailboxes(
    aes_keys: List[bytes],
    pod_public_keys: Dict[str, Mock],
    worker_mailbox_ids: Dict[str, str],
) -> Dict[str, _WorkerMailboxDetails]:
    """A set of worker mailboxes to use."""
    return {
        pod_identifier: _WorkerMailboxDetails(
            pod_identifier=pod_identifier,
            public_key=pod_public_keys[pod_identifier],
            mailbox_id=mailbox_id,
            aes_encryption_key=aes_keys[idx],
        )
        for idx, (pod_identifier, mailbox_id) in enumerate(worker_mailbox_ids.items())
    }


@fixture
def mock_message_service() -> Mock:
    """A mocked MessageService."""
    mock_message_service: Mock = create_autospec(_MessageService, instance=True)
    return mock_message_service


@fixture
def idp_url() -> str:
    """Identity Provider URL."""
    return "https://idp-url.unit-testing.bitfount.com"


@fixture
def task_id() -> str:
    """Task ID."""
    return "this-is-a-task-id"


@fixture(params=(True, False), ids=("project_id_incl", "no_project_id"))
def opt_project_id(request: PytestRequest) -> Optional[str]:
    """Project ID."""
    incl_project_id: bool = request.param
    if incl_project_id:
        return "this-is-a-project-id"
    else:
        return None


@fixture(params=(True, False), ids=("task_id_incl", "no_task_id"))
def opt_task_id(request: PytestRequest, task_id: str) -> Optional[str]:
    """Returns a task ID or None, to cover both cases."""
    incl_task_id: bool = request.param
    if incl_task_id:
        return task_id
    else:
        return None


@fixture
def online_check_uuid() -> str:
    """UUID for online checking."""
    return "auuidforonlinecheck"


@fixture
def modeller_mailbox(
    idp_url: str,
    mock_message_service: Mock,
    modeller_mailbox_id: str,
    task_id: str,
    worker_mailboxes: Dict[str, _WorkerMailboxDetails],
) -> _ModellerMailbox:
    """The ModellerMailbox under test."""
    return _ModellerMailbox(
        mailbox_id="modeller_mailbox_id",
        worker_mailboxes=worker_mailboxes,
        message_service=mock_message_service,
        task_id=task_id,
    )


@fixture
def signatures() -> List[bytes]:
    """List of fake signatures for message signing."""
    signatures = [b"signature1", b"signature2", b"signature3"]
    return signatures


@fixture
def mock_signer(mocker: MockerFixture, signatures: List[bytes]) -> Mock:
    """Mock RSA signing with predefined signatures to return."""
    mock_signer = mocker.patch.object(_RSAEncryption, "sign_message")
    mock_signer.side_effect = signatures
    return mock_signer


@fixture
def encrypted_task_requests() -> List[bytes]:
    """List of fake encrypted task requests."""
    encrypted_task_requests = [b"first", b"second", b"third"]
    return encrypted_task_requests


@fixture
def mock_rsa_encrypter(
    encrypted_task_requests: List[bytes], mocker: MockerFixture
) -> Mock:
    """Mock RSA encryption with predefined encrypted messages to return."""
    mock_rsa_encrypter = mocker.patch.object(_RSAEncryption, "encrypt")
    mock_rsa_encrypter.side_effect = encrypted_task_requests
    return mock_rsa_encrypter


@fixture
def mock_aes_decrypter(mocker: MockerFixture) -> Mock:
    """Mock AES decryption for cases where message bodies aren't encrypted."""
    # If the message bodies are not encrypted we need to mock out the decryption
    # and instead replace it with just returning message bodies.
    mock_decrypter = mocker.patch.object(_MessageEncryption, "decrypt_incoming_message")
    mock_decrypter.side_effect = lambda body, key: body
    return mock_decrypter


@fixture
def serialized_protocol() -> SerializedProtocol:
    """Protocol details."""
    return SerializedProtocol(
        class_name="some protocol",
        algorithm=SerializedAlgorithm(class_name="some algorithm"),
    )


@unit_test
class TestModellerMailbox:
    """Tests for ModellerMailbox class."""

    async def test_send_task_requests(
        self,
        default_task_request_msg_gen: _TaskRequestMessageGenerator,
        idp_url: str,
        mock_message_service: Mock,
        mocker: MockerFixture,
        modeller_mailbox_id: str,
        task_id: str,
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Test send_task_requests factory method.

        This is the class method and so should return us a created ModellerMailbox.
        """
        # Mock out underlying send method
        mocked_sender = mocker.patch.object(_ModellerMailbox, "_send_task_requests")
        mocked_sender.return_value = (modeller_mailbox_id, worker_mailboxes, task_id)

        modeller_mailbox = await _ModellerMailbox.send_task_requests(
            serialized_protocol=SerializedProtocol(
                class_name="some protocol",
                algorithm=SerializedAlgorithm(class_name="some algorithm"),
            ),
            pod_public_keys=Mock(),
            task_request_msg_gen=default_task_request_msg_gen,
            message_service=mock_message_service,
        )

        assert modeller_mailbox.mailbox_id == modeller_mailbox_id
        assert modeller_mailbox.worker_mailboxes == worker_mailboxes
        assert modeller_mailbox.message_service == mock_message_service
        assert modeller_mailbox._task_id == task_id

    async def test__send_task_requests_is_successful(
        self,
        aes_keys: List[bytes],
        encrypted_task_requests: List[bytes],
        key_based_task_request_msg_gen: KeyBasedGenerator,
        mock_message_service: Mock,
        mock_rsa_encrypter: Mock,
        mock_signer: Mock,
        mocker: MockerFixture,
        modeller_mailbox_id: str,
        opt_project_id: Optional[str],
        pod_identifiers: List[str],
        pod_public_keys: Dict[str, Mock],
        serialized_protocol: SerializedProtocol,
        signatures: List[bytes],
        task_id: str,
        worker_mailbox_ids: Dict[str, str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Happy path, job requests are all sent successfully.

        Key-based identity verification.
        """
        # Mock AES key generation
        mock_key_generator = mocker.patch.object(_AESEncryption, "generate_key")
        mock_key_generator.side_effect = aes_keys

        # Mock the message services setup method
        mock_message_service.setup_task.return_value = (
            modeller_mailbox_id,
            worker_mailbox_ids,
            task_id,
        )

        # Mock/create other args
        private_key = key_based_task_request_msg_gen.key
        task_request_msg_gen = key_based_task_request_msg_gen.gen

        # Call method
        (
            received_modeller_mailbox_id,
            received_worker_mailboxes,
            received_task_id,
        ) = await _ModellerMailbox._send_task_requests(
            serialized_protocol=serialized_protocol,
            pod_public_keys=pod_public_keys,
            task_request_msg_gen=task_request_msg_gen,
            message_service=mock_message_service,
            project_id=opt_project_id,
        )

        # Check return values
        assert received_modeller_mailbox_id == modeller_mailbox_id
        assert received_worker_mailboxes == worker_mailboxes
        assert received_task_id == task_id

        # Check message service method call
        mock_message_service.setup_task.assert_called_once_with(
            {
                pod_identifier: _TaskRequestMessage(
                    serialized_protocol=serialized_protocol,
                    auth_type=IdentityVerificationMethod.KEYS.value,
                    request=_SignedEncryptedTaskRequest(
                        encrypted_request=encrypted_task_requests[i],
                        signature=signatures[i],
                    ).serialize(),
                    project_id=opt_project_id,
                ).serialize()
                for i, pod_identifier in enumerate(pod_identifiers)
            },
            TaskMetadata(protocol=serialized_protocol["class_name"]),
            opt_project_id,
        )

        # Ensure we encrypt and sign correctly
        mock_rsa_encrypter.assert_has_calls(
            [
                # Each call to the encryption should be the (task request body,
                # the list of all pods involved, generated AES key) and the public
                # key to encrypt with.
                call(
                    _TaskRequest(
                        serialized_protocol=serialized_protocol,
                        pod_identifiers=pod_identifiers,
                        aes_key=aes_keys[i],
                    ).serialize(),
                    pod_public_key,
                )
                for i, pod_public_key in enumerate(pod_public_keys.values())
            ]
        )
        mock_signer.assert_has_calls(
            # Each call to the signer should be the private key to sign with and
            # the encrypted message body (i.e. task).
            [call(private_key, etr) for etr in encrypted_task_requests]
        )

    async def test__send_task_requests_is_successful_when_some_pods_are_offline(
        self,
        aes_keys: List[bytes],
        encrypted_task_requests: List[bytes],
        key_based_task_request_msg_gen: KeyBasedGenerator,
        mock_message_service: Mock,
        mock_rsa_encrypter: Mock,
        mock_signer: Mock,
        mocker: MockerFixture,
        modeller_mailbox_id: str,
        opt_project_id: Optional[str],
        pod_identifiers: List[str],
        pod_public_keys: Dict[str, Mock],
        serialized_protocol: SerializedProtocol,
        signatures: List[bytes],
        task_id: str,
        worker_mailbox_ids: Dict[str, str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Some pods are offline, so there aren't mailboxes returned for them.

        In the case where some pods are offline we continue the task,
        except we only receive mailboxes for some of the pods for the
        message service.

        We then continue training, but only with the online tasks.
        """
        # Mock AES key generation
        mock_key_generator = mocker.patch.object(_AESEncryption, "generate_key")
        mock_key_generator.side_effect = aes_keys

        # For this test we ensure the message service returns fewer
        # pods than were requested.
        worker_mailboxes_from_message_service = dict(worker_mailbox_ids)
        worker_mailboxes_from_message_service.popitem()

        # Mock the message services setup method
        mock_message_service.setup_task.return_value = (
            modeller_mailbox_id,
            worker_mailboxes_from_message_service,
            task_id,
        )

        # Mock/create other args
        private_key = key_based_task_request_msg_gen.key
        task_request_msg_gen = key_based_task_request_msg_gen.gen

        # Call method
        (
            received_modeller_mailbox_id,
            received_worker_mailboxes,
            received_task_id,
        ) = await _ModellerMailbox._send_task_requests(
            serialized_protocol=serialized_protocol,
            pod_public_keys=pod_public_keys,
            task_request_msg_gen=task_request_msg_gen,
            message_service=mock_message_service,
            project_id=opt_project_id,
        )

        # Modeller mailbox ID matches the mocked message service response
        assert received_modeller_mailbox_id == modeller_mailbox_id
        # We only create WorkerMailboxDetails for the mailboxes
        # returned by the message service
        worker_mailboxes.popitem()
        assert received_worker_mailboxes == worker_mailboxes
        assert received_task_id == task_id

        # Check message service method call included all pod identifiers
        # This includes the ones that aren't online, we don't know that one is
        # offline until the message service tells us!
        mock_message_service.setup_task.assert_called_once_with(
            {
                pod_identifier: _TaskRequestMessage(
                    serialized_protocol=serialized_protocol,
                    auth_type=IdentityVerificationMethod.KEYS.value,
                    request=_SignedEncryptedTaskRequest(
                        encrypted_request=encrypted_task_requests[i],
                        signature=signatures[i],
                    ).serialize(),
                    project_id=opt_project_id,
                ).serialize()
                for i, pod_identifier in enumerate(worker_mailbox_ids.keys())
            },
            TaskMetadata(protocol=serialized_protocol["class_name"]),
            opt_project_id,
        )

        # Ensure we encrypt and sign correctly the first task messages
        # This includes the ones that aren't online, we don't know that one is
        # offline until the message service tells us!
        mock_rsa_encrypter.assert_has_calls(
            [
                # Each call to the encryption should be the (task request body,
                # the list of all pods involved, generated AES key) and the public
                # key to encrypt with.
                call(
                    _TaskRequest(
                        serialized_protocol=serialized_protocol,
                        pod_identifiers=pod_identifiers,
                        aes_key=aes_keys[i],
                    ).serialize(),
                    pod_public_key,
                )
                for i, pod_public_key in enumerate(pod_public_keys.values())
            ]
        )
        mock_signer.assert_has_calls(
            # Each call to the signer should be the private key to sign with and
            # the encrypted message body (i.e. task).
            [call(private_key, etr) for etr in encrypted_task_requests]
        )

    async def test__send_task_requests_fails(
        self,
        encrypted_task_requests: List[bytes],
        key_based_task_request_msg_gen: KeyBasedGenerator,
        mock_message_service: Mock,
        mock_rsa_encrypter: Mock,
        mock_signer: Mock,
        opt_project_id: Optional[str],
        pod_identifiers: List[str],
        pod_public_keys: Dict[str, Mock],
        rpc_error: RpcError,
        serialized_protocol: SerializedProtocol,
        signatures: List[bytes],
    ) -> None:
        """RPC Error occurs for one attempt at starting training.

        Uses key-based identity verification method.
        """
        # Mock out error raising in message service.
        mock_message_service.setup_task.side_effect = rpc_error

        # Mock/create other args
        task_request_msg_gen = key_based_task_request_msg_gen.gen

        # Call method
        with raises(RuntimeError, match="Failed to start task with pods:"):
            await _ModellerMailbox._send_task_requests(
                serialized_protocol=serialized_protocol,
                pod_public_keys=pod_public_keys,
                task_request_msg_gen=task_request_msg_gen,
                message_service=mock_message_service,
                project_id=opt_project_id,
            )

        # Check that the encrypted and signed messages were passed to
        # setup_task
        mock_message_service.setup_task.assert_called_once_with(
            {
                pod_identifier: _TaskRequestMessage(
                    serialized_protocol=serialized_protocol,
                    auth_type=IdentityVerificationMethod.KEYS.value,
                    request=_SignedEncryptedTaskRequest(
                        encrypted_request=encrypted_task_requests[i],
                        signature=signatures[i],
                    ).serialize(),
                    project_id=opt_project_id,
                ).serialize()
                for i, pod_identifier in enumerate(pod_identifiers)
            },
            TaskMetadata(protocol=serialized_protocol["class_name"]),
            opt_project_id,
        )

    async def test__send_task_requests_has_no_signatures_if_saml_based(
        self,
        aes_keys: List[bytes],
        encrypted_task_requests: List[bytes],
        mock_message_service: Mock,
        mock_rsa_encrypter: Mock,
        mocker: MockerFixture,
        modeller_mailbox_id: str,
        opt_project_id: Optional[str],
        pod_identifiers: List[str],
        pod_public_keys: Dict[str, Mock],
        saml_task_request_msg_gen: _TaskRequestMessageGenerator,
        serialized_protocol: SerializedProtocol,
        task_id: str,
        worker_mailbox_ids: Dict[str, str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Tests _send_task_requests has no sigs if SAML-based verification."""
        # Mock AES key generation
        mock_key_generator = mocker.patch.object(_AESEncryption, "generate_key")
        mock_key_generator.side_effect = aes_keys

        # Mock the message services setup method
        mock_message_service.setup_task.return_value = (
            modeller_mailbox_id,
            worker_mailbox_ids,
            task_id,
        )

        # Call method
        (
            received_modeller_mailbox_id,
            received_worker_mailboxes,
            received_task_id,
        ) = await _ModellerMailbox._send_task_requests(
            serialized_protocol=serialized_protocol,
            pod_public_keys=pod_public_keys,
            task_request_msg_gen=saml_task_request_msg_gen,
            message_service=mock_message_service,
            project_id=opt_project_id,
        )

        # Check return values
        assert received_modeller_mailbox_id == modeller_mailbox_id
        assert received_worker_mailboxes == worker_mailboxes
        assert received_task_id == task_id

        # Check message service method call
        mock_message_service.setup_task.assert_called_once_with(
            {
                pod_identifier: _TaskRequestMessage(
                    serialized_protocol=serialized_protocol,
                    auth_type=IdentityVerificationMethod.SAML.value,
                    request=_EncryptedTaskRequest(
                        encrypted_request=encrypted_task_requests[i],
                    ).serialize(),
                    project_id=opt_project_id,
                ).serialize()
                for i, pod_identifier in enumerate(pod_identifiers)
            },
            TaskMetadata(protocol=serialized_protocol["class_name"]),
            opt_project_id,
        )

        # Ensure we encrypt correctly
        mock_rsa_encrypter.assert_has_calls(
            [
                # Each call to the encryption should be the (task request body,
                # the list of all pods involved, generated AES key) and the public
                # key to encrypt with.
                call(
                    _TaskRequest(
                        serialized_protocol=serialized_protocol,
                        pod_identifiers=pod_identifiers,
                        aes_key=aes_keys[i],
                    ).serialize(),
                    pod_public_key,
                )
                for i, pod_public_key in enumerate(pod_public_keys.values())
            ]
        )

    async def test_process_task_request_responses(
        self,
        mock_aes_decrypter: Mock,
        mock_message_service: Mock,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        opt_task_id: Optional[str],
        patch_poll_for_messages: PollForMessagesPatcher,
        worker_mailbox_details: List[WorkerDetails],
        worker_mailbox_ids: Dict[str, str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Happy path, all pods send responses to training requests."""
        # Create fake task response messages
        task_response_messages = [
            _BitfountMessage(
                message_type=_BitfountMessageType.JOB_ACCEPT,
                body=msgpack.dumps(
                    {
                        _PodResponseType.ACCEPT.name: worker_mailbox_details[
                            0
                        ].pod_identifier
                    }
                ),
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[0].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[0].mailbox_id,
                task_id=opt_task_id,
            ),
            _BitfountMessage(
                message_type=_BitfountMessageType.JOB_ACCEPT,
                body=msgpack.dumps(
                    {
                        _PodResponseType.ACCEPT.name: worker_mailbox_details[
                            1
                        ].pod_identifier
                    }
                ),
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[1].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[1].mailbox_id,
                task_id=opt_task_id,
            ),
            _BitfountMessage(
                message_type=_BitfountMessageType.JOB_REJECT,
                body=msgpack.dumps(
                    {
                        _PodResponseType.NO_ACCESS.name: "some/pod",
                        _PodResponseType.NO_ACCESS.name: "some/pod",
                    }
                ),
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[2].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[2].mailbox_id,
                task_id=opt_task_id,
            ),
        ]

        # Assign these to poll_for_messages which is the underlying method we
        # expect to yield messages.
        patch_poll_for_messages(task_response_messages)

        # Start listening and processing messages
        accepted_pod_mailboxes = await _run_func_and_listen_to_mailbox(
            modeller_mailbox.process_task_request_responses(), modeller_mailbox
        )

        # Pod3 rejected the task, so we aren't expecting it!
        worker_mailboxes.pop(worker_mailbox_details[2].pod_identifier)
        assert accepted_pod_mailboxes == worker_mailboxes

    async def test_get_saml_challenges_retrieves_saml_responses(
        self,
        mock_aes_decrypter: Mock,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        opt_task_id: Optional[str],
        patch_poll_for_messages: PollForMessagesPatcher,
        worker_mailbox_details: List[WorkerDetails],
    ) -> None:
        """Happy path, all pods send responses to training requests."""
        saml_challenges = [
            msgpack.dumps(bytes(f"saml challenge {i}", "utf-8")) for i in range(3)
        ]

        # Create fake task response messages
        saml_requests = [
            _BitfountMessage(
                message_type=_BitfountMessageType.SAML_REQUEST,
                body=saml_challenges[0],
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[0].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[0].mailbox_id,
                task_id=opt_task_id,
            ),
            _BitfountMessage(
                message_type=_BitfountMessageType.SAML_REQUEST,
                body=saml_challenges[1],
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[1].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[1].mailbox_id,
                task_id=opt_task_id,
            ),
            _BitfountMessage(
                message_type=_BitfountMessageType.SAML_REQUEST,
                body=saml_challenges[2],
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[2].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[2].mailbox_id,
                task_id=opt_task_id,
            ),
        ]

        # Assign these to poll_for_messages which is the underlying method we
        # expect to yield messages.
        patch_poll_for_messages(saml_requests)

        # Start listening and processing messages
        received_saml_challenges = await _run_func_and_listen_to_mailbox(
            modeller_mailbox.get_saml_challenges(), modeller_mailbox
        )

        # Ensure messages returned match those that we mocked
        # Order is not guaranteed but _DecryptedBitfountMessage is not hashable
        # or sortable so need to manually check equality.
        expected_saml_challenges = [
            challenge.decrypt(
                modeller_mailbox.worker_mailboxes[challenge.sender].aes_encryption_key
            )
            for challenge in saml_requests
        ]
        assert len(received_saml_challenges) == len(expected_saml_challenges)
        assert all(
            challenge in expected_saml_challenges
            for challenge in received_saml_challenges
        )

    async def test_get_saml_challenges_throws_error(
        self,
        modeller_mailbox: _ModellerMailbox,
        patch_poll_for_messages: PollForMessagesPatcher,
        rpc_error: RpcError,
    ) -> None:
        """Test Start Task error thrown on error."""
        patch_poll_for_messages([rpc_error])
        with raises(
            BitfountTaskStartError, match="Failed to start task with all pods."
        ):
            await _run_func_and_listen_to_mailbox(
                modeller_mailbox.get_saml_challenges(),
                modeller_mailbox,
            )

    async def test_handles_pod_never_responds(
        self,
        mock_aes_decrypter: Mock,
        mock_message_service: Mock,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        opt_task_id: Optional[str],
        patch_poll_for_messages: PollForMessagesPatcher,
        worker_mailbox_details: List[WorkerDetails],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Some pods never send a response to the training request."""
        # Create only a single response message
        task_response_messages = [
            _BitfountMessage(
                message_type=_BitfountMessageType.JOB_ACCEPT,
                body=msgpack.dumps(
                    {
                        _PodResponseType.ACCEPT.name: worker_mailbox_details[
                            0
                        ].pod_identifier
                    }
                ),
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[0].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[0].mailbox_id,
                task_id=opt_task_id,
            ),
        ]

        # Assign this message to poll_for_messages yield
        patch_poll_for_messages(task_response_messages)

        # Start listening and processing messages. We timeout on the responses to
        # simulate non-responding pods. This may need to be increased if the test
        # is failing but should need to be no higher than 5 seconds.
        accepted_pod_mailboxes = await _run_func_and_listen_to_mailbox(
            modeller_mailbox.process_task_request_responses(timeout=1), modeller_mailbox
        )

        # Remove non-responding pods from expected results
        worker_mailboxes.pop(worker_mailbox_details[1].pod_identifier)
        worker_mailboxes.pop(worker_mailbox_details[2].pod_identifier)

        assert accepted_pod_mailboxes == worker_mailboxes

    async def test_handles_message_retrieval_exception(
        self,
        mock_aes_decrypter: Mock,
        mock_message_service: Mock,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        opt_task_id: Optional[str],
        patch_poll_for_messages: PollForMessagesPatcher,
        rpc_error: RpcError,
        worker_mailbox_details: List[WorkerDetails],
    ) -> None:
        """RPC Exception when trying to check for responses from pods."""
        task_response_messages: List[MessageOrException] = [
            _BitfountMessage(
                message_type=_BitfountMessageType.JOB_ACCEPT,
                body=msgpack.dumps(
                    {
                        _PodResponseType.ACCEPT.name: worker_mailbox_details[
                            0
                        ].pod_identifier
                    }
                ),
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[0].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[0].mailbox_id,
                task_id=opt_task_id,
            ),
            rpc_error,
        ]

        patch_poll_for_messages(task_response_messages)

        with raises(
            BitfountTaskStartError, match="Failed to start task with all pods."
        ):
            await _run_func_and_listen_to_mailbox(
                modeller_mailbox.process_task_request_responses(),
                modeller_mailbox,
            )

    async def test_send_to_all_pods_aes_encrypt_successful(
        self,
        mock_message_service: Mock,
        mock_message_timestamps: Callable[[Iterable[str]], Mock],
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        pod_identifiers: List[str],
        task_id: str,
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Message is sent AES encrypted using provided key."""
        fake_timestamps = ["Hello", "World", "!"]
        mock_message_timestamps(fake_timestamps)

        encrypt = mocker.patch.object(_MessageEncryption, "encrypt_outgoing_message")
        encrypted_messages = [
            b"first encrypted",
            b"second encrypted",
            b"third encrypted",
        ]
        encrypt.side_effect = encrypted_messages
        message = "some message"
        dumped_message = msgpack.dumps(message)

        mock_message_service.username = modeller_name

        modeller_mailbox.accepted_worker_mailboxes = worker_mailboxes

        await modeller_mailbox._send_to_all_pods_aes_encrypt(
            message, _BitfountMessageType.TRAINING_COMPLETE
        )

        encrypt.assert_has_calls(
            [
                call(
                    dumped_message,
                    worker_mailboxes[pod_identifiers[0]].aes_encryption_key,
                ),
                call(
                    dumped_message,
                    worker_mailboxes[pod_identifiers[1]].aes_encryption_key,
                ),
                call(
                    dumped_message,
                    worker_mailboxes[pod_identifiers[2]].aes_encryption_key,
                ),
            ]
        )
        assert encrypt.call_count == 3
        mock_message_service.send_message.assert_has_calls(
            [
                call(
                    _BitfountMessage(
                        message_type=_BitfountMessageType.TRAINING_COMPLETE,
                        body=encrypted_messages[0],
                        recipient=pod_identifiers[0],
                        recipient_mailbox_id=worker_mailboxes[
                            pod_identifiers[0]
                        ].mailbox_id,
                        sender=modeller_name,
                        sender_mailbox_id=modeller_mailbox_id,
                        timestamp=fake_timestamps[0],
                        task_id=task_id,
                    ),
                    already_packed=True,
                ),
                call(
                    _BitfountMessage(
                        message_type=_BitfountMessageType.TRAINING_COMPLETE,
                        body=encrypted_messages[1],
                        recipient=pod_identifiers[1],
                        recipient_mailbox_id=worker_mailboxes[
                            pod_identifiers[1]
                        ].mailbox_id,
                        sender=modeller_name,
                        sender_mailbox_id=modeller_mailbox_id,
                        timestamp=fake_timestamps[1],
                        task_id=task_id,
                    ),
                    already_packed=True,
                ),
                call(
                    _BitfountMessage(
                        message_type=_BitfountMessageType.TRAINING_COMPLETE,
                        body=encrypted_messages[2],
                        recipient=pod_identifiers[2],
                        recipient_mailbox_id=worker_mailboxes[
                            pod_identifiers[2]
                        ].mailbox_id,
                        sender=modeller_name,
                        sender_mailbox_id=modeller_mailbox_id,
                        timestamp=fake_timestamps[2],
                        task_id=task_id,
                    ),
                    already_packed=True,
                ),
            ]
        )
        assert mock_message_service.send_message.call_count == 3

    async def test_send_to_all_pods_aes_encrypt_throws_error(
        self,
        mock_message_service: Mock,
        mock_message_timestamps: Callable[[Iterable[str]], Mock],
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        pod_identifiers: List[str],
        rpc_error: RpcError,
        task_id: str,
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Sending encrypted message receives RpcError."""
        fake_timestamps = ["Hello"]
        mock_message_timestamps(fake_timestamps)

        expected_encrypted_message = b"encrypted_message"
        encrypt = mocker.patch.object(_MessageEncryption, "encrypt_outgoing_message")
        encrypt.return_value = expected_encrypted_message
        message = "some message"
        dumped_message = msgpack.dumps(message)
        mock_message_service.username = modeller_name
        mock_message_service.send_message.side_effect = rpc_error

        modeller_mailbox.accepted_worker_mailboxes = worker_mailboxes

        with raises(RpcError):
            await modeller_mailbox._send_to_all_pods_aes_encrypt(
                message, _BitfountMessageType.ALGORITHM_EXCHANGE
            )

        encrypt.assert_called_once_with(
            dumped_message, worker_mailboxes[pod_identifiers[0]].aes_encryption_key
        )
        mock_message_service.send_message.assert_called_once_with(
            _BitfountMessage(
                message_type=_BitfountMessageType.ALGORITHM_EXCHANGE,
                body=expected_encrypted_message,
                recipient=pod_identifiers[0],
                recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
                sender=modeller_name,
                sender_mailbox_id=modeller_mailbox_id,
                timestamp=fake_timestamps[0],
                task_id=task_id,
            ),
            already_packed=True,
        )

    def test_receive_aes_decrypt_successful(
        self,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        opt_task_id: Optional[str],
        pod_identifiers: List[str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Receives and decrypts messages using provided AES key."""
        expected_decrypted_message = b"some message"
        original_message = _BitfountMessage(
            message_type=_BitfountMessageType.TRAINING_COMPLETE,
            body=_MessageEncryption.encrypt_outgoing_message(
                msgpack.dumps(expected_decrypted_message),
                worker_mailboxes[pod_identifiers[1]].aes_encryption_key,
            ),
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )
        modeller_mailbox.accepted_worker_mailboxes = worker_mailboxes

        message = modeller_mailbox._decrypt_message(original_message)

        assert message == _DecryptedBitfountMessage(
            message_type=_BitfountMessageType.TRAINING_COMPLETE,
            body=expected_decrypted_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            timestamp=original_message.timestamp,
            task_id=original_message.task_id,
        )

    async def test_send_task_start_message(
        self,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
    ) -> None:
        """Tests modeller sends task start empty message."""
        mock_message_decrypt = mocker.patch.object(
            modeller_mailbox,
            "_send_to_all_pods_aes_encrypt",
            return_value=None,
        )

        await modeller_mailbox.send_task_start_message()
        mock_message_decrypt.assert_awaited_once_with(
            None, _BitfountMessageType.TASK_START
        )

    async def test_send_task_complete_message(
        self,
        mock_message_service: Mock,
        mock_message_timestamps: Callable[[Iterable[str]], Mock],
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        pod_identifiers: List[str],
        task_id: str,
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Task complete message is sent AES encrypted using provided key."""
        fake_timestamps = ["Hello", "World", "!"]
        mock_message_timestamps(fake_timestamps)
        encrypt = mocker.patch.object(_MessageEncryption, "encrypt_outgoing_message")
        encrypt.side_effect = [None, None, None]
        dumped_message = msgpack.dumps(None)
        mock_message_service.username = modeller_name
        modeller_mailbox.accepted_worker_mailboxes = worker_mailboxes

        await modeller_mailbox.send_task_complete_message()

        encrypt.assert_has_calls(
            [
                call(
                    dumped_message,
                    worker_mailboxes[pod_identifiers[0]].aes_encryption_key,
                ),
                call(
                    dumped_message,
                    worker_mailboxes[pod_identifiers[1]].aes_encryption_key,
                ),
                call(
                    dumped_message,
                    worker_mailboxes[pod_identifiers[2]].aes_encryption_key,
                ),
            ]
        )
        assert encrypt.call_count == 3
        mock_message_service.send_message.assert_has_calls(
            [
                call(
                    _BitfountMessage(
                        message_type=_BitfountMessageType.TASK_COMPLETE,
                        body=None,  # type: ignore[arg-type] # reason: message body should be empty # noqa: B950
                        recipient=pod_identifiers[0],
                        recipient_mailbox_id=worker_mailboxes[
                            pod_identifiers[0]
                        ].mailbox_id,
                        sender=modeller_name,
                        sender_mailbox_id=modeller_mailbox_id,
                        timestamp=fake_timestamps[0],
                        task_id=task_id,
                    ),
                    already_packed=True,
                ),
                call(
                    _BitfountMessage(
                        message_type=_BitfountMessageType.TASK_COMPLETE,
                        body=None,  # type: ignore[arg-type] # reason: message body should be empty # noqa: B950
                        recipient=pod_identifiers[1],
                        recipient_mailbox_id=worker_mailboxes[
                            pod_identifiers[1]
                        ].mailbox_id,
                        sender=modeller_name,
                        sender_mailbox_id=modeller_mailbox_id,
                        timestamp=fake_timestamps[1],
                        task_id=task_id,
                    ),
                    already_packed=True,
                ),
                call(
                    _BitfountMessage(
                        message_type=_BitfountMessageType.TASK_COMPLETE,
                        body=None,  # type: ignore[arg-type] # reason: message body should be empty # noqa: B950
                        recipient=pod_identifiers[2],
                        recipient_mailbox_id=worker_mailboxes[
                            pod_identifiers[2]
                        ].mailbox_id,
                        sender=modeller_name,
                        sender_mailbox_id=modeller_mailbox_id,
                        timestamp=fake_timestamps[2],
                        task_id=task_id,
                    ),
                    already_packed=True,
                ),
            ]
        )
        assert mock_message_service.send_message.call_count == 3

    async def test_get_oidc_client_ids(
        self,
        mock_aes_decrypter: Mock,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        opt_task_id: Optional[str],
        patch_poll_for_messages: PollForMessagesPatcher,
        worker_mailbox_details: List[WorkerDetails],
    ) -> None:
        """Test get_oidc_client_ids() extracts needed details."""
        # Create fake task response messages
        oidc_client_ids = [
            _OIDCClientID(f"client_id_{i}").serialize() for i in range(3)
        ]
        oidc_challenges = [
            _BitfountMessage(
                message_type=_BitfountMessageType.OIDC_CHALLENGE,
                body=msgpack.dumps(oidc_client_ids[i]),
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[i].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[i].mailbox_id,
                task_id=opt_task_id,
            )
            for i in range(3)
        ]

        # Assign these to poll_for_messages which is the underlying method we
        # expect to yield messages.
        patch_poll_for_messages(oidc_challenges)

        # Start listening and processing messages
        received_oidc_challenges = await _run_func_and_listen_to_mailbox(
            modeller_mailbox.get_oidc_client_ids(), modeller_mailbox
        )

        # Ensure extracted details match expected
        assert received_oidc_challenges == {
            worker_mailbox_details[i].pod_identifier: _OIDCClientID(
                oidc_client_ids[i]["client_id"]
            )
            for i in range(3)
        }

    async def test_get_oidc_client_ids_throws_error(
        self,
        modeller_mailbox: _ModellerMailbox,
        patch_poll_for_messages: PollForMessagesPatcher,
        rpc_error: RpcError,
    ) -> None:
        """Test Start Task error thrown on error."""
        patch_poll_for_messages([rpc_error])
        with raises(
            BitfountTaskStartError, match="Failed to start task with all pods."
        ):
            await _run_func_and_listen_to_mailbox(
                modeller_mailbox.get_oidc_client_ids(),
                modeller_mailbox,
            )

    async def test_send_oidc_auth_flow_responses(
        self,
        mock_message_service: Mock,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        pod_identifiers: List[str],
        task_id: str,
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Test send_oidc_auth_flow_responses() sends expected messages."""
        # Set modeller username
        mock_message_service.username = modeller_name

        # Mock out _send_aes_encrypted_message()
        mock_send_aes = mocker.patch(
            "bitfount.federated.transport.modeller_transport._send_aes_encrypted_message",  # noqa: B950
            autospec=True,
        )

        oidc_details = {
            pod_identifiers[i]: _OIDCAuthFlowResponse(
                auth_code=f"auth_code_{pod_identifiers[i]}",
                code_verifier=f"code_verifier_{pod_identifiers[i]}",
                redirect_uri=f"redirect_uri_{pod_identifiers[i]}",
            )
            for i in range(len(pod_identifiers))
        }

        await modeller_mailbox.send_oidc_auth_flow_responses(oidc_details)

        # Check calls
        mock_send_aes.assert_has_calls(
            [
                call(
                    message={
                        "auth_code": oidc_details[pod_id].auth_code,
                        "code_verifier": oidc_details[pod_id].code_verifier,
                        "redirect_uri": oidc_details[pod_id].redirect_uri,
                    },
                    aes_encryption_key=worker_mailboxes[pod_id].aes_encryption_key,
                    message_service=modeller_mailbox.message_service,
                    message_type=_BitfountMessageType.OIDC_AFC_PKCE_RESPONSE,
                    recipient=worker_mailboxes[pod_id].pod_identifier,
                    recipient_mailbox_id=worker_mailboxes[pod_id].mailbox_id,
                    sender=modeller_name,
                    sender_mailbox_id=modeller_mailbox_id,
                    task_id=task_id,
                )
                for pod_id in pod_identifiers
            ]
        )

    async def test_send_oidc_device_code_responses(
        self,
        mock_message_service: Mock,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        pod_identifiers: List[str],
        task_id: str,
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Test send_oidc_auth_flow_responses() sends expected messages."""
        # Set modeller username
        mock_message_service.username = modeller_name

        # Mock out _send_aes_encrypted_message()
        mock_send_aes = mocker.patch(
            "bitfount.federated.transport.modeller_transport._send_aes_encrypted_message",  # noqa: B950
            autospec=True,
        )

        # Create pod device code details for each pod
        now = datetime.now(timezone.utc)
        base_interval = 5
        device_code_details: Dict[str, _PodDeviceCodeDetails] = {
            pod_identifiers[i]: _PodDeviceCodeDetails(
                device_code=f"device_code_{i}",
                expires_at=now + timedelta(hours=i),
                interval=base_interval + i,
            )
            for i in range(len(pod_identifiers))
        }

        await modeller_mailbox.send_oidc_device_code_responses(device_code_details)

        # Check calls
        mock_send_aes.assert_has_calls(
            [
                call(
                    message={
                        "device_code": device_code_details[pod_id].device_code,
                        "expires_at": device_code_details[
                            pod_id
                        ].expires_at.isoformat(),
                        "interval": device_code_details[pod_id].interval,
                    },
                    aes_encryption_key=worker_mailboxes[pod_id].aes_encryption_key,
                    message_service=modeller_mailbox.message_service,
                    message_type=_BitfountMessageType.OIDC_DEVICE_CODE_RESPONSE,
                    recipient=worker_mailboxes[pod_id].pod_identifier,
                    recipient_mailbox_id=worker_mailboxes[pod_id].mailbox_id,
                    sender=modeller_name,
                    sender_mailbox_id=modeller_mailbox_id,
                    task_id=task_id,
                )
                for pod_id in pod_identifiers
            ]
        )

    def test__setup_online_status_handler(
        self, mocker: MockerFixture, modeller_mailbox: _ModellerMailbox
    ) -> None:
        """Test that modeller mailbox registers ONLINE_CHECK message handler."""
        mock_register_handler = mocker.patch.object(
            modeller_mailbox, "register_handler"
        )
        modeller_mailbox._setup_online_status_handler()
        mock_register_handler.assert_called_once()
        assert (
            mock_register_handler.call_args[0][0] == _BitfountMessageType.ONLINE_CHECK
        )

    async def test_modeller_responds_to_online_status_request(
        self,
        caplog: LogCaptureFixture,
        mock_aes_decrypter: Mock,
        mock_message_service: Mock,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        online_check_uuid: str,
        opt_task_id: Optional[str],
        patch_poll_for_messages: PollForMessagesPatcher,
        task_id: str,
        worker_mailbox_details: List[WorkerDetails],
    ) -> None:
        """Some pods never send a response to the training request."""
        caplog.set_level("INFO")
        # Pod sends message to modeller checking if they are online
        pod_messages = [
            _BitfountMessage(
                message_type=_BitfountMessageType.ONLINE_CHECK,
                body=online_check_uuid,  # type: ignore[arg-type] # reason: should return unchanged # noqa: B950
                recipient=modeller_name,
                recipient_mailbox_id=modeller_mailbox_id,
                sender=worker_mailbox_details[0].pod_identifier,
                sender_mailbox_id=worker_mailbox_details[0].mailbox_id,
                task_id=opt_task_id,
            ),
        ]

        # For ease of testing, we pretend that the pod has already accepted the task
        modeller_mailbox.accepted_worker_mailboxes = {
            worker_mailbox_details[0].pod_identifier: worker_mailbox_details[0]  # type: ignore[dict-item] # reason: ease of testing # noqa: B950
        }

        mock_send_message = mocker.patch(
            "bitfount.federated.transport.modeller_transport._send_aes_encrypted_message"  # noqa: B950
        )

        # Mock out _BitfountMessage constructor
        mock_bitfount_message_cls = mocker.patch(
            "bitfount.federated.transport.modeller_transport._BitfountMessage"
        )

        # Assign this message to poll_for_messages yield
        patch_poll_for_messages(pod_messages)

        # Start listening and processing messages. We timeout on the responses to
        # simulate non-responding pods. This may need to be increased if the test
        # is failing but should need to be no higher than 5 seconds.
        await _run_func_and_listen_to_mailbox(
            modeller_mailbox.process_task_request_responses(timeout=3), modeller_mailbox
        )

        # Assert that the response was sent to the correct pod and is of the right type
        assert "Informing user1/pod_1 that we are still online." in get_info_logs(
            caplog
        )

        # Check correct message sending was used
        mock_send_message.assert_not_called()
        mock_message_service.send_message.assert_called_once_with(
            mock_bitfount_message_cls.return_value, already_packed=True
        )
        mock_bitfount_message_cls.assert_called_once_with(
            body=online_check_uuid,
            message_type=_BitfountMessageType.ONLINE_RESPONSE,
            recipient=worker_mailbox_details[0].pod_identifier,
            recipient_mailbox_id=worker_mailbox_details[0].mailbox_id,
            sender=modeller_mailbox.message_service.username,
            sender_mailbox_id=modeller_mailbox.mailbox_id,
            task_id=task_id,
        )

    async def test_log(
        self, mocker: MockerFixture, modeller_mailbox: _ModellerMailbox
    ) -> None:
        """Test that log message is sent appropriately."""
        mock_log = mocker.patch.object(
            modeller_mailbox, "_send_to_all_pods_aes_encrypt"
        )
        await modeller_mailbox.log({"msg": "message"})
        mock_log.assert_awaited_once_with(
            {"msg": "message"}, _BitfountMessageType.LOG_MESSAGE
        )

    @pytest.mark.parametrize(
        "process_name",
        ("aProcessName", None),
        ids=lambda x: f"process_name_present={bool(x)}",
    )
    @pytest.mark.parametrize(
        "thread_name",
        ("aThreadName", None),
        ids=lambda x: f"thread_name_present={bool(x)}",
    )
    def test_log_message_handler(
        self,
        mock_aes_decrypter: Mock,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        modeller_name: str,
        process_name: Optional[str],
        task_id: str,
        thread_name: Optional[str],
        worker_mailbox_details: List[WorkerDetails],
    ) -> None:
        """Test LOG_MESSAGE handler modifies record as expected."""
        # Mock out logging framework interaction
        mock_logger = mocker.patch(
            "bitfount.federated.transport.modeller_transport.logger", autospec=True
        )
        mock_logging = mocker.patch(
            "bitfount.federated.transport.modeller_transport.logging", autospec=True
        )

        # Create mock log message
        mock_log_message_contents = {
            "msg": "An important log message",
            "anotherField": "notToBeChanged",
            "federated": True,
        }
        if process_name:
            mock_log_message_contents["processName"] = process_name
        if thread_name:
            mock_log_message_contents["threadName"] = thread_name

        mock_log_message = _BitfountMessage(
            message_type=_BitfountMessageType.LOG_MESSAGE,
            body=msgpack.dumps(mock_log_message_contents),
            recipient=modeller_name,
            recipient_mailbox_id=modeller_mailbox_id,
            sender=worker_mailbox_details[0].pod_identifier,
            sender_mailbox_id=worker_mailbox_details[0].mailbox_id,
            task_id=task_id,
        )

        log_message_handler = modeller_mailbox._get_log_message_handler()
        log_message_handler(mock_log_message)

        # Message contents should have been manipulated and logged out
        expected_log_message = {
            "msg": (
                f"<FROM POD {worker_mailbox_details[0].pod_identifier}>:"
                f" An important log message"
            ),
            "anotherField": "notToBeChanged",
        }
        if process_name:
            expected_log_message["processName"] = f"<{process_name}>"
        if thread_name:
            expected_log_message["threadName"] = f"<{thread_name}>"
        mock_logging.makeLogRecord.assert_called_once_with(expected_log_message)
        mock_logger.handle.assert_called_once_with(
            mock_logging.makeLogRecord.return_value
        )


@unit_test
class TestModellerTransportFunctions:
    """Tests for functions in modeller_transport module."""

    async def test__parameters_update_handler(
        self,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        opt_task_id: Optional[str],
        pod_identifiers: List[str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Tests that weight updates are populated by handler."""
        # Decrypted & message
        expected_message = {"some parameter": ["some weight list"]}
        decrypt = mocker.patch.object(_BitfountMessage, "decrypt")
        decrypt.return_value = _DecryptedBitfountMessage(
            message_type=_BitfountMessageType.TRAINING_UPDATE,
            body=expected_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )

        modeller_mailbox.accepted_worker_mailboxes = worker_mailboxes

        # Message from pod
        expected_encrypted_message = b"encrypted_message"
        message = _BitfountMessage(
            message_type=_BitfountMessageType.TRAINING_UPDATE,
            body=expected_encrypted_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )

        weight_updates: Dict[str, _SerializedWeights] = {}
        model_update_handler = _parameter_updates_handler(
            modeller_mailbox, weight_updates
        )
        with _AsyncMultipleResponsesHandler(
            handler=model_update_handler,
            message_types=_BitfountMessageType.TRAINING_UPDATE,
            mailbox=modeller_mailbox,
            responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
        ) as response_handler:
            await response_handler.handler(message)

        assert weight_updates == {pod_identifiers[1]: expected_message}

    async def test__training_metrics_handler(
        self,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        opt_task_id: Optional[str],
        pod_identifiers: List[str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Tests that validation metrics are populated by handler."""
        # Decrypted & message
        expected_message = {"some parameter": "some metric"}
        decrypt = mocker.patch.object(_BitfountMessage, "decrypt")
        decrypt.return_value = _DecryptedBitfountMessage(
            message_type=_BitfountMessageType.TRAINING_METRICS,
            body=expected_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )

        modeller_mailbox.accepted_worker_mailboxes = worker_mailboxes

        # Message from pod
        expected_encrypted_message = b"encrypted_message"
        message = _BitfountMessage(
            message_type=_BitfountMessageType.TRAINING_METRICS,
            body=expected_encrypted_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )

        validation_metrics: List[Mapping[str, str]] = []
        validation_metrics_handler = _training_metrics_handler(
            modeller_mailbox, validation_metrics
        )

        with _AsyncMultipleResponsesHandler(
            handler=validation_metrics_handler,
            message_types=_BitfountMessageType.TRAINING_UPDATE,
            mailbox=modeller_mailbox,
            responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
        ) as response_handler:
            await response_handler.handler(message)

        # Only single element here but order may be arbitrary in larger numbers
        # As `Mapping`/`Dict` is unsortable and unhashable, have to manually
        # do comparison.
        expected_message_list = [expected_message]
        assert len(validation_metrics) == len(expected_message_list)
        assert all(metrics in expected_message_list for metrics in validation_metrics)

    async def test_get_metrics_updates_calls_handler(
        self, mocker: MockerFixture, modeller_mailbox: _ModellerMailbox
    ) -> None:
        """Tests that the appropriate handler is called."""
        mock_handler = Mock()
        mocker.patch(
            "bitfount.federated.transport.modeller_transport._training_metrics_handler",
            mock_handler,
        )

        await _get_training_metrics_from_workers(modeller_mailbox, timeout=1)
        mock_handler.assert_called_once_with(modeller_mailbox, [])

    async def test_get_parameter_updates_calls_handler(
        self, mocker: MockerFixture, modeller_mailbox: _ModellerMailbox
    ) -> None:
        """Tests that the appropriate handler is called."""
        mock_handler = Mock()
        mocker.patch(
            "bitfount.federated.transport.modeller_transport._parameter_updates_handler",  # noqa: B950 ignore line too long
            mock_handler,
        )

        await _get_parameter_updates_from_workers(modeller_mailbox, timeout=1)
        mock_handler.assert_called_once_with(modeller_mailbox, {})

    async def test__public_key_handler(
        self,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        opt_task_id: Optional[str],
        pod_identifiers: List[str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Tests that public key is given by handler."""
        # Decrypted & message
        expected_message = [{"some public_key"}]
        decrypt = mocker.patch.object(_BitfountMessage, "decrypt")
        decrypt.return_value = _DecryptedBitfountMessage(
            message_type=_BitfountMessageType.KEY_EXCHANGE,
            body=expected_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )

        modeller_mailbox.accepted_worker_mailboxes = worker_mailboxes

        # Message from pod
        expected_encrypted_message = b"encrypted_message"
        message = _BitfountMessage(
            message_type=_BitfountMessageType.KEY_EXCHANGE,
            body=expected_encrypted_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )

        pub_keys: List[bytes] = []
        pub_keys_handler = _public_key_handler(modeller_mailbox, pub_keys)

        with _AsyncMultipleResponsesHandler(
            handler=pub_keys_handler,
            message_types=_BitfountMessageType.KEY_EXCHANGE,
            mailbox=modeller_mailbox,
            responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
        ) as response_handler:
            await response_handler.handler(message)

        # Only single element here but order may be arbitrary in larger numbers.
        # Order is not guaranteed so need to sort.
        assert sorted(pub_keys) == sorted([expected_message])

    async def test__get_public_key_calls_handler(
        self, mocker: MockerFixture, modeller_mailbox: _ModellerMailbox
    ) -> None:
        """Tests that the appropriate handler is called."""
        mock_handler = Mock()
        mocker.patch(
            "bitfount.federated.transport.modeller_transport._public_key_handler",  # noqa: B950 ignore line too long
            mock_handler,
        )
        await _get_public_key(modeller_mailbox, timeout=1)
        mock_handler.assert_called_once_with(modeller_mailbox, [])

    async def test__psi_dataset_handler(
        self,
        mocker: MockerFixture,
        modeller_mailbox: _ModellerMailbox,
        modeller_mailbox_id: str,
        opt_task_id: Optional[str],
        pod_identifiers: List[str],
        worker_mailboxes: Dict[str, _WorkerMailboxDetails],
    ) -> None:
        """Tests that psi dataset is given by handler."""
        # Decrypted & message
        expected_message = [{"some data"}]
        decrypt = mocker.patch.object(_BitfountMessage, "decrypt")
        decrypt.return_value = _DecryptedBitfountMessage(
            message_type=_BitfountMessageType.PSI_DATASET,
            body=expected_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )

        modeller_mailbox.accepted_worker_mailboxes = worker_mailboxes

        # Message from pod
        expected_encrypted_message = b"encrypted_message"
        message = _BitfountMessage(
            message_type=_BitfountMessageType.PSI_DATASET,
            body=expected_encrypted_message,
            recipient=pod_identifiers[0],
            recipient_mailbox_id=worker_mailboxes[pod_identifiers[0]].mailbox_id,
            sender=pod_identifiers[1],
            sender_mailbox_id=modeller_mailbox_id,
            task_id=opt_task_id,
        )

        psi_dataset: List[Tuple[List[str], List[str]]] = []
        psi_dataset_handler = _psi_dataset_handler(modeller_mailbox, psi_dataset)

        with _AsyncMultipleResponsesHandler(
            handler=psi_dataset_handler,
            message_types=_BitfountMessageType.PSI_DATASET,
            mailbox=modeller_mailbox,
            responders=modeller_mailbox.accepted_worker_mailboxes.keys(),
        ) as response_handler:
            await response_handler.handler(message)

        # Only single element here but order may be arbitrary in larger numbers
        # Need to sort as order is not guaranteed
        assert sorted(psi_dataset) == sorted([expected_message])

    async def test__get_psi_datasets_from_workers_calls_handler(
        self, mocker: MockerFixture, modeller_mailbox: _ModellerMailbox
    ) -> None:
        """Tests that the appropriate handler is called."""
        mock_handler = Mock()
        mocker.patch(
            "bitfount.federated.transport.modeller_transport._psi_dataset_handler",  # noqa: B950 ignore line too long
            mock_handler,
        )
        await _get_psi_datasets_from_workers(modeller_mailbox, timeout=1)
        mock_handler.assert_called_once_with(modeller_mailbox, [])
