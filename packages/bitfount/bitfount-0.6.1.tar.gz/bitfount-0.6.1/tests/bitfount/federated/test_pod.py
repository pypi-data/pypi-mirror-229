"""Tests for worker and pod classes."""
import logging
import os.path
from pathlib import Path
import platform
import re
import sqlite3
import time
from typing import Any, Dict, List, Optional, Protocol, Type, cast
from unittest.mock import AsyncMock, MagicMock, Mock, NonCallableMock, create_autospec

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import numpy as np
import pandas as pd
import pytest
from pytest import LogCaptureFixture, MonkeyPatch, TempPathFactory, fixture
from pytest_lazyfixture import lazy_fixture
from pytest_mock import MockerFixture
from requests import HTTPError, RequestException

import bitfount
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.csv_source import CSVSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasources.excel_source import ExcelSource
from bitfount.data.datasources.views import SQLViewConfig, ViewDatasourceConfig
from bitfount.data.exceptions import DataSourceError
from bitfount.data.schema import BitfountSchema
from bitfount.data.utils import DatabaseConnection, _generate_dtypes_hash
from bitfount.federated.authorisation_checkers import IdentityVerificationMethod
from bitfount.federated.exceptions import (
    BitfountTaskStartError,
    PodNameError,
    PodViewDatabaseError,
    PodViewError,
)
from bitfount.federated.keys_setup import RSAKeyPair
from bitfount.federated.pod import (
    DatasourceContainer,
    DatasourceContainerConfig,
    Pod,
    PodRegistrationError,
)
from bitfount.federated.pod_response_message import _PodResponseMessage
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.task_requests import (
    _EncryptedTaskRequest,
    _SignedEncryptedTaskRequest,
    _TaskRequest,
    _TaskRequestMessage,
)
from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _BitfountMessageType,
    _MessageService,
)
from bitfount.federated.transport.pod_transport import _PodMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.federated.types import (
    SerializedAggregator,
    SerializedAlgorithm,
    SerializedModel,
    SerializedProtocol,
    _PodResponseType,
)
from bitfount.hooks import BasePodHook, _registry
from bitfount.hub.api import BitfountAM, BitfountHub
from bitfount.hub.authentication_flow import BitfountSession, _AuthEnv
from bitfount.hub.exceptions import SchemaUploadError
from bitfount.runners.config_schemas import (
    MessageServiceConfig,
    PodDataConfig,
    PodDetailsConfig,
)
from bitfount.transformations.processor import TransformationProcessor
from tests.utils import PytestRequest
from tests.utils.helper import (
    create_dataset,
    create_datasource,
    get_arg_from_args_or_kwargs,
    get_debug_logs,
    get_warning_logs,
    unit_test,
)
from tests.utils.mocks import DataclassMock, create_dataclass_mock


@fixture
def logging_mock(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock replacement for `logging`."""
    my_mock = MagicMock()
    monkeypatch.setattr(bitfount.federated.pod, "logger", my_mock)
    return my_mock


@unit_test
class TestPod:
    """Tests for Pod class."""

    # TODO: [BIT-983] Add tests that include aggregation

    @pytest.fixture(autouse=True)
    def cleanup_registry(self) -> None:
        """Cleans up the registry after test invocation."""
        _registry.clear()

    @fixture
    def pod_name(self) -> str:
        """Pod name."""
        return "some-pod-name"

    @fixture
    def mock_datasource(self) -> DataFrameSource:
        """Mock of a pandas dataframe."""
        mock_dataframe: Mock = create_autospec(pd.DataFrame, instance=True)

        # Setup details for hash generation
        mock_dataframe.dtypes.to_string.return_value = "COLUMN INFO FOR MOCK DATAFRAME"

        mock_datasource = DataFrameSource(mock_dataframe)

        return mock_datasource

    @fixture
    def username(self) -> str:
        """Name of user hosting pod."""
        return "test_username"

    @fixture
    def pod_mailbox_id(self, pod_name: str) -> str:
        """The pod's mailbox ID."""
        # TODO: [BIT-960] Currently this is just hardcoded to return the pod_name
        #       (which is what the mailbox ID will actually be). [BIT-960] will have
        #       the PodConnect method actually return the generated mailbox ID so
        #       that if the approach changes in future it only needs to change on
        #       the message service side. At that point this should return the
        #       generated mailbox ID instead.
        return pod_name

    @fixture
    def pod_identifier(self, pod_mailbox_id: str, username: str) -> str:
        """Pod identifier for the pod."""
        return f"{username}/{pod_mailbox_id}"

    @fixture
    def mock_pod_data_config(self) -> DataclassMock:
        """A dataclass mock of PodDataConfig."""
        mock_pod_data_config = create_dataclass_mock(PodDataConfig)
        # So the following can be used in dict unpacking
        mock_pod_data_config.data_split.args = dict()
        mock_pod_data_config.datasource_args = dict()
        mock_pod_data_config.auto_tidy = False
        mock_pod_data_config.ignore_cols = None
        return mock_pod_data_config

    @fixture
    def mock_pod_details_config(self) -> DataclassMock:
        """A dataclass mock of PodDetailsConfig."""
        return create_dataclass_mock(PodDetailsConfig)

    @fixture
    def mock_bitfount_hub(self, username: str) -> Mock:
        """A mock of BitfountHub."""
        mock_hub: Mock = create_autospec(BitfountHub, instance=True)
        mock_hub.session = create_autospec(BitfountSession, instance=True)
        mock_hub.session.username = username
        return mock_hub

    @fixture
    def mock_access_manager(self) -> Mock:
        """A mock of BitfountAM."""
        mock_access_manager: Mock = create_autospec(BitfountAM, instance=True)
        return mock_access_manager

    @fixture
    def mock_message_service_config(self) -> DataclassMock:
        """A dataclass mock of MessageServiceConfig."""
        return create_dataclass_mock(MessageServiceConfig)

    @fixture
    def mock_access_manager_public_key(self) -> Mock:
        """A mock of the access managers public key."""
        mock_access_manager_public_key: Mock = create_autospec(
            RSAPublicKey, instance=True
        )
        return mock_access_manager_public_key

    @fixture
    def mock_pod_keys(self) -> DataclassMock:
        """A dataclass mock of RSAKeyPair for a pod."""
        return create_dataclass_mock(RSAKeyPair)

    @fixture
    def approved_pods(self) -> List[str]:
        """A list of pod identifiers for approved pods to work with."""
        return [
            "blah/worker_1",
            "blah/worker_2",
            "blah/worker_3",
            "blah/worker_4",
            "blah/worker_name",
        ]

    @fixture
    def mock_pod_mailbox(self) -> Mock:
        """Mock PodMailbox."""
        mailbox: Mock = create_autospec(_PodMailbox, instance=True)
        mailbox.message_service = create_autospec(_MessageService, instance=True)
        return mailbox

    @fixture
    def mock_pod_vitals(self) -> Mock:
        """Mock _PodVitals."""
        mock_pod_vitals = create_dataclass_mock(_PodVitals)
        return mock_pod_vitals

    @fixture
    def mock_pod_mailbox_create_helper(
        self, mock_pod_mailbox: Mock, mocker: MockerFixture
    ) -> Mock:
        """Mocks out create_and_connect_pod_mailbox."""
        mock_create_function = mocker.patch(
            "bitfount.federated.pod._create_and_connect_pod_mailbox", autospec=True
        )
        mock_create_function.return_value = mock_pod_mailbox
        return mock_create_function

    @fixture
    def pod(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        pod_name: str,
        username: str,
    ) -> Pod:
        """Pod instance with mocked components."""
        pod_mock = Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        # Pod.mailbox is usually set in Pod.start() but as that might not be being
        # called, we set it here manually.
        pod_mock._mailbox = mock_pod_mailbox
        pod_mock._pod_vitals = mock_pod_vitals

        return pod_mock

    @fixture
    def modeller_name(self) -> str:
        """Modeller name."""
        return "someModellerName"

    @fixture
    def modeller_mailbox_id(self) -> str:
        """Modeller Mailbox ID."""
        return "someModellerMailboxID"

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

    class _MakeBitfountMessageCallable(Protocol):
        """Callback protocol to describe make_bitfount_message fixture return."""

        def __call__(
            self,
            body: Any,
            other_pods_in_task: Optional[Dict[str, str]] = None,
        ) -> _BitfountMessage:
            ...

    @fixture
    def make_bitfount_message(
        self,
        modeller_mailbox_id: str,
        modeller_name: str,
        opt_task_id: Optional[str],
        pod_identifier: str,
        pod_mailbox_id: str,
    ) -> _MakeBitfountMessageCallable:
        """Returns a function to generate a Bitfount message with fixtures in place."""

        def _make_bitfount_message(
            body: Any, other_pods_in_task: Optional[Dict[str, str]] = None
        ) -> _BitfountMessage:
            """Makes the BitfountMessage."""
            pod_mailbox_ids = {pod_identifier: pod_mailbox_id}

            if other_pods_in_task:
                pod_mailbox_ids.update(other_pods_in_task)

            return _BitfountMessage(
                message_type=_BitfountMessageType.JOB_REQUEST,
                body=body,
                recipient=pod_identifier,
                recipient_mailbox_id=pod_mailbox_id,
                sender=modeller_name,
                sender_mailbox_id=modeller_mailbox_id,
                pod_mailbox_ids=pod_mailbox_ids,
                task_id=opt_task_id,
            )

        return _make_bitfount_message

    @fixture
    def aes_key(self) -> bytes:
        """An AES key."""
        return b"someAesKey"

    @fixture(scope="class")
    def single_table_excel_file(self, tmp_path_factory: TempPathFactory) -> Path:
        """Path to single table excel file."""
        dataframe = create_dataset()
        tmp_path = tmp_path_factory.mktemp("temp_excel")
        filename = tmp_path / "test.xlsx"
        dataframe.to_excel(filename, index=False, sheet_name="Sheet1")
        return filename

    @fixture(scope="class")
    def multi_table_excel_file(self, tmp_path_factory: TempPathFactory) -> Path:
        """Path to multi table excel file."""
        dataframe = create_dataset()
        tmp_path = tmp_path_factory.mktemp("temp_excel")
        filename = tmp_path / "test.xlsx"
        with pd.ExcelWriter(filename) as writer:
            dataframe.to_excel(writer, index=False, sheet_name="Sheet1")
            dataframe.to_excel(writer, index=False, sheet_name="Sheet2")

        return filename

    @fixture(scope="class")
    def single_table_excel_source(self, single_table_excel_file: Path) -> ExcelSource:
        """Single Table ExcelSource - Read-only."""
        source = ExcelSource(single_table_excel_file, sheet_name="Sheet1")
        assert not source.multi_table
        return source

    @fixture(scope="class")
    def multi_table_excel_source(self, multi_table_excel_file: Path) -> ExcelSource:
        """Multi Table ExcelSource - Read-only."""
        source = ExcelSource(multi_table_excel_file, sheet_name=["Sheet1", "Sheet2"])
        assert source.multi_table
        return source

    @pytest.mark.parametrize(
        "invalid_pod_name",
        ["Invalid", "INVALID", "invalid-", "-invalid", "invalid--invalid"],
    )
    def test_invalid_pod_name(
        self,
        approved_pods: List[str],
        invalid_pod_name: str,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        username: str,
    ) -> None:
        """Test PodNameError raised for invalid pod name."""
        with pytest.raises(PodNameError):
            Pod(
                name=invalid_pod_name,
                datasources=[
                    DatasourceContainerConfig(
                        name=invalid_pod_name,
                        datasource_details=mock_pod_details_config,
                        datasource=mock_datasource,
                        data_config=mock_pod_data_config,
                        schema=None,
                    )
                ],
                username=username,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
                pod_keys=mock_pod_keys,
                approved_pods=approved_pods,
            )

    def test_show_datapoints_with_results_in_db_pod_db_false(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that if pod_db is false, show_datapoints is set to false as well."""
        pod = Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
            pod_db=False,
            show_datapoints_with_results_in_db=True,
        )
        assert pod.show_datapoints_with_results_in_db is False

    def test__update_pod_db_multi_table(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        multi_table_excel_source: ExcelSource,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that _add_data_to_db for multi-table datasources."""
        mock_add_to_db = mocker.patch("bitfount.federated.pod._add_data_to_pod_db")

        pod = Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=multi_table_excel_source,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
            pod_db=True,
            show_datapoints_with_results_in_db=True,
        )

        ds = pod.datasource
        assert ds is not None
        assert mock_add_to_db.call_count == len(ds.schema.tables)

    def test_databasesource_pod_db_false(
        self,
        approved_pods: List[str],
        caplog: LogCaptureFixture,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that pod_db is false if datasource is DatabaseSource."""
        db_conn = Mock(
            spec=DatabaseConnection,
            table_names=["table1"],
            multi_table=False,
            query=None,
            con=Mock(),
            db_schema="test",
        )
        mocker.patch.object(Pod, "_setup_schema")
        datasource = DatabaseSource(db_conn=db_conn)
        datasource.validate()
        pod = Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=datasource,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
            pod_db=True,
            show_datapoints_with_results_in_db=True,
        )
        assert pod.pod_db is False
        assert (
            "Pod database not supported for DatabaseSource. "
            "Starting pod without database." in caplog.text
        )

    @pytest.mark.skipif(
        condition=platform.system() == "Windows",
        reason=(
            "Only works intermittently on Windows. "
            "Connection to database not always closed properly,"
            "leading to PermissionError."
        ),
    )
    def test_pod_db(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests database is created for pod."""
        if os.path.exists(f"{pod_name}.sqlite"):
            os.remove(f"{pod_name}.sqlite")
        ds = create_datasource(classification=True)
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=ds,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
            pod_db=True,
            show_datapoints_with_results_in_db=True,
        )
        assert os.path.exists(f"{pod_name}.sqlite")
        con = sqlite3.connect(f"{pod_name}.sqlite")
        existing_data = pd.read_sql(f'SELECT * FROM "{pod_name}"', con)
        assert existing_data.shape[0] == ds._data.shape[0]
        assert (
            existing_data.shape[1] - 2 == ds._data.shape[1]
        )  # existing_data has the extra columns datapoint_hash and rowID
        con.close()
        os.remove(f"{pod_name}.sqlite")

    def test_datapoint_hash_in_datasource_raises_error(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests error is raised if 'datapoint_hash' is a column name in datasource."""
        dataset = create_dataset(classification=True)
        dataset["datapoint_hash"] = np.nan
        with pytest.raises(ValueError):
            Pod(
                name=pod_name,
                datasources=[
                    DatasourceContainerConfig(
                        name=pod_name,
                        datasource_details=mock_pod_details_config,
                        datasource=DataFrameSource(dataset),
                        data_config=mock_pod_data_config,
                        schema=None,
                    )
                ],
                username=username,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
                pod_keys=mock_pod_keys,
                approved_pods=approved_pods,
                pod_db=True,
                show_datapoints_with_results_in_db=True,
            )

    @pytest.mark.skipif(
        condition=platform.system() == "Windows",
        reason=(
            "Only works intermittently on Windows. "
            "Connection to database not always closed properly,"
            "leading to PermissionError."
        ),
    )
    def test_pod_db_new_datapoints(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests only new datapoint added to db."""
        if os.path.exists(f"{pod_name}.sqlite"):
            os.remove(f"{pod_name}.sqlite")
        dataset = create_dataset(classification=True)
        dataset.drop("Date", inplace=True, axis=1)
        ds = DataFrameSource(data=dataset[0:3000])
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=ds,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
            pod_db=True,
            show_datapoints_with_results_in_db=True,
        )
        assert os.path.exists(f"{pod_name}.sqlite")
        con = sqlite3.connect(f"{pod_name}.sqlite")
        existing_data = pd.read_sql(f'SELECT * FROM "{pod_name}"', con)
        assert existing_data.shape[0] == ds._data.shape[0]
        assert (
            existing_data.shape[1] - 2 == ds._data.shape[1]
        )  # existing_data has the extra datapoint_hash and rowID columns
        ds = DataFrameSource(data=dataset)
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=ds,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
            pod_db=True,
            show_datapoints_with_results_in_db=True,
        )

        existing_data = pd.read_sql(f'SELECT * FROM "{pod_name}"', con)
        # Check that only the new datapoints have been added to the ds
        assert existing_data.shape[0] == dataset.shape[0]
        assert existing_data.shape[1] - 2 == dataset.shape[1]
        con.close()
        os.remove(f"{pod_name}.sqlite")

    def test_schema_raises_error_basesource_flag(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests pod raises error when BaseSource is not initialised."""
        del mock_datasource._base_source_init
        with pytest.raises(DataSourceError):
            Pod(
                name=pod_name,
                datasources=[
                    DatasourceContainerConfig(
                        name=pod_name,
                        datasource_details=mock_pod_details_config,
                        datasource=mock_datasource,
                        data_config=mock_pod_data_config,
                        schema=None,
                    )
                ],
                username=username,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
                pod_keys=mock_pod_keys,
                approved_pods=approved_pods,
            )

    def test_datasource_property_warns_if_multiple_datasources(
        self,
        caplog: LogCaptureFixture,
        pod: Pod,
    ) -> None:
        """Tests datasource property warns if multiple datasources are provided."""
        pod.datasources["second_datasource"] = create_autospec(
            DatasourceContainer, instance=True
        )

        ds = pod.datasource

        assert ds is None
        assert (
            "Pod has 2 datasources; unable to extract with Pod.datasource property."
            in get_warning_logs(caplog)
        )

    def test_datasource_property_warns_if_no_datasources(
        self,
        caplog: LogCaptureFixture,
        pod: Pod,
    ) -> None:
        """Tests datasource property warns if no datasources are provided."""
        pod.datasources = {}

        ds = pod.datasource

        assert ds is None
        assert (
            "Pod has no datasources configured;"
            " unable to extract with Pod.datasource property."
            in get_warning_logs(caplog)
        )

    async def test__check_for_unapproved_pods_without_secure_aggregation(
        self, pod: Pod, pod_identifier: str
    ) -> None:
        """Tests authorisation check passes not using secure aggregation."""
        training_request = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="some aggregator"),
        )
        pods_involved_in_task = [pod_identifier]

        assert (
            pod._check_for_unapproved_pods(pods_involved_in_task, training_request)
            is None
        )

    async def test__check_for_unapproved_pods_with_secure_aggregation_unapproved(
        self, pod: Pod, pod_identifier: str
    ) -> None:
        """Tests unapproved workers are returned when using secure aggregation."""
        training_request = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
        )
        unapproved_pods = ["some/unapproved-pod", "another/unapproved_pod"]
        pods_involved_in_task = [pod_identifier, *unapproved_pods]

        assert (
            pod._check_for_unapproved_pods(pods_involved_in_task, training_request)
            == unapproved_pods
        )

    @pytest.mark.asyncio
    async def test__check_for_unapproved_pods_with_secure_aggregation_approved(
        self, approved_pods: List[str], pod: Pod, pod_identifier: str
    ) -> None:
        """Tests all workers approved when using secure aggregation."""
        training_request = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
        )
        pods_involved_in_task = [pod_identifier, *approved_pods]

        assert (
            pod._check_for_unapproved_pods(pods_involved_in_task, training_request)
            is None
        )

    async def test__new_task_request_handler_rejects(
        self,
        aes_key: bytes,
        caplog: LogCaptureFixture,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_mailbox: Mock,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        opt_task_id: Optional[str],
        pod: Pod,
    ) -> None:
        """Tests new job callback fails when access request rejected."""
        caplog.set_level(logging.INFO)

        mock_worker_mailbox = mocker.patch(
            "bitfount.federated.pod._WorkerMailbox", autospec=True
        )

        # Mock out Pod._check_for_unapproved_pods() as that's not under test here.
        mock__check_for_unapproved_pods = mocker.patch.object(
            pod, "_check_for_unapproved_pods", autospec=True
        )
        # Testing rejection, so there are unapproved pods
        expected_unapproved_pods = ["some/unapproved-pod"]
        mock__check_for_unapproved_pods.return_value = expected_unapproved_pods

        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="some aggregator"),
        )
        task_request = _TaskRequest(task_protocol_details, ["pods"], aes_key)
        message = make_bitfount_message(
            _TaskRequestMessage(
                serialized_protocol=task_protocol_details,
                auth_type=IdentityVerificationMethod.SAML.value,
                request=_EncryptedTaskRequest(
                    # We don't actually encrypt this due to the mocked decryption
                    encrypted_request=task_request.serialize(),
                ).serialize(),
            ).serialize()
        )

        await pod._new_task_request_handler(message)

        # We expect this log on rejection
        assert f"Task from '{modeller_name}' rejected." in caplog.text
        # Check accept_task() not called (happens in _new_task_request_handler)
        mock_worker_mailbox.accept_task.assert_not_called()

        mock_worker_mailbox.assert_called_once_with(
            pod_identifier=pod.pod_identifier,
            modeller_mailbox_id=message.sender_mailbox_id,
            modeller_name=message.sender,
            aes_encryption_key=aes_key,
            message_service=mock_pod_mailbox.message_service,
            pod_mailbox_ids=message.pod_mailbox_ids,
            task_id=opt_task_id,
        )

        # Ensure reject task was called
        mock_worker_mailbox.return_value.reject_task.assert_called_once_with(
            {
                _PodResponseType.NO_ACCESS.name: [
                    *expected_unapproved_pods,
                ]
            }
        )

    async def test__new_task_request_handler_creates_worker(
        self,
        aes_key: bytes,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_mailbox: Mock,
        mocker: MockerFixture,
        modeller_mailbox_id: str,
        modeller_name: str,
        pod: Pod,
        pod_identifier: str,
        pod_mailbox_id: str,
    ) -> None:
        """Tests the simple wrapper.

        This is just ensuring that the creation of the worker
        has been called as expected.
        """
        # Mock out _create_and_run_worker as that's not under test here.
        mock__create_and_run_worker = mocker.patch.object(
            pod, "_create_and_run_worker", autospec=True
        )
        message = make_bitfount_message(Mock())

        await pod._new_task_request_handler(
            # body only used in _is_authorised so can mock out
            message
        )

        # Check that worker is created and run
        mock__create_and_run_worker.assert_called_once_with(message)

    async def test__create_and_run_worker_runs_worker(
        self,
        aes_key: bytes,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        opt_task_id: Optional[str],
        pod: Pod,
    ) -> None:
        """Test that worker is created with SAML authorisation.

        Verification type is explicitly set to SAML.
        """
        mock_worker_mailbox_cls = mocker.patch(
            "bitfount.federated.pod._WorkerMailbox",
            autospec=True,
        )
        mock_worker_mailbox_cls.return_value.mailbox_id = "worker-mailbox-id"

        mock_worker_cls = mocker.patch("bitfount.federated.pod._Worker", autospec=True)

        mock__create_authorisation_checker = mocker.patch.object(
            Pod, "_create_authorisation_checker", autospec=True
        )

        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="some aggregator"),
        )
        task_request = _TaskRequest(task_protocol_details, [], aes_key)
        encrypted_message = make_bitfount_message(
            _TaskRequestMessage(
                serialized_protocol=task_protocol_details,
                auth_type=IdentityVerificationMethod.SAML.value,
                request=_EncryptedTaskRequest(
                    # We don't actually encrypt this due to the mocked decryption
                    encrypted_request=task_request.serialize(),
                ).serialize(),
                run_on_new_data_only=False,
                batched_execution=False,
            ).serialize()
        )

        await pod._create_and_run_worker(encrypted_message)

        # Ensure worker mailbox created based on task
        mock_worker_mailbox_cls.assert_called_once_with(
            pod_identifier=pod.pod_identifier,
            modeller_mailbox_id=encrypted_message.sender_mailbox_id,
            modeller_name=encrypted_message.sender,
            aes_encryption_key=aes_key,
            message_service=mock_pod_mailbox.message_service,
            pod_mailbox_ids=encrypted_message.pod_mailbox_ids,
            task_id=opt_task_id,
        )

        # Ensure worker was created with the created SAML based authoriser
        ds = pod.datasource
        assert ds is not None
        mock_worker_cls.assert_called_once_with(
            datasource=ds.datasource,
            schema=ds.schema,
            mailbox=mock_worker_mailbox_cls.return_value,
            bitfounthub=pod._hub,
            authorisation=mock__create_authorisation_checker.return_value,
            pod_dp=pod._pod_dp,
            pod_vitals=mock_pod_vitals,
            parent_pod_identifier=pod.pod_identifier,
            data_identifier=pod.pod_identifier,
            serialized_protocol=task_protocol_details,
            pod_db=False,
            show_datapoints_in_results_db=False,
            run_on_new_data_only=False,
            project_id=None,
            batched_execution=False,
            multi_pod_task=False,
        )

    async def test__create_and_run_worker_with_secure_aggregation_unapproved_pods(
        self,
        aes_key: bytes,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_mailbox: Mock,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        pod: Pod,
    ) -> None:
        """Test that the Pod rejects a task if there are unapproved pods in the task.

        SAML identity verification is explicitly used.
        """
        mock_worker_mailbox = AsyncMock(spec=_WorkerMailbox)
        mocker.patch(
            "bitfount.federated.pod._WorkerMailbox", return_value=mock_worker_mailbox
        )

        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
            aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
        )
        task_request = _TaskRequest(task_protocol_details, [], aes_key)
        encrypted_message = make_bitfount_message(
            _TaskRequestMessage(
                serialized_protocol=task_protocol_details,
                auth_type=IdentityVerificationMethod.SAML.value,
                request=_EncryptedTaskRequest(
                    # We don't actually encrypt this due to the mocked decryption
                    encrypted_request=task_request.serialize(),
                ).serialize(),
            ).serialize(),
            {"unapproved_pod_name": "unapproved_mailbox_id"},
        )

        await pod._create_and_run_worker(encrypted_message)

        # Ensure worker mailbox has rejected the task
        mock_worker_mailbox.reject_task.assert_awaited_once_with(
            {
                "NO_ACCESS": [
                    "unapproved_pod_name",
                ]
            }
        )

    async def test__create_and_run_worker_with_secure_aggregation(
        self,
        aes_key: bytes,
        caplog: LogCaptureFixture,
        make_bitfount_message: _MakeBitfountMessageCallable,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        opt_task_id: Optional[str],
        pod: Pod,
    ) -> None:
        """Test that expected mailbox is created for secure aggregator."""
        # Mock out constructors
        mock_interpod_worker_mailbox_cls = mocker.patch(
            "bitfount.federated.pod._InterPodWorkerMailbox", autospec=True
        )
        mock_interpod_worker_mailbox_cls.return_value.mailbox_id = "worker-mailbox-id"

        mock_worker_cls = mocker.patch("bitfount.federated.pod._Worker", autospec=True)

        # Mock out other methods
        mock__create_authorisation_checker = mocker.patch.object(
            Pod, "_create_authorisation_checker", autospec=True
        )

        # Mock out other pod public key retrieval
        mock__get_pod_public_keys = mocker.patch(
            "bitfount.federated.pod._get_pod_public_keys", autospec=True
        )

        # Create appropriate task request
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(
                class_name="some algorithm",
                model=SerializedModel(class_name="some model"),
            ),
            aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
        )
        task_request = _TaskRequest(task_protocol_details, [], aes_key)
        encrypted_message = make_bitfount_message(
            _TaskRequestMessage(
                serialized_protocol=task_protocol_details,
                auth_type=IdentityVerificationMethod.SAML.value,
                request=_EncryptedTaskRequest(
                    # We don't actually encrypt this due to the mocked decryption
                    encrypted_request=task_request.serialize(),
                ).serialize(),
                run_on_new_data_only=False,
            ).serialize()
        )

        # Call method under test
        with caplog.at_level(logging.DEBUG):
            await pod._create_and_run_worker(encrypted_message)

        # Ensure interpod worker mailbox created based on task
        mock_interpod_worker_mailbox_cls.assert_called_once_with(
            pod_identifier=pod.pod_identifier,
            modeller_mailbox_id=encrypted_message.sender_mailbox_id,
            modeller_name=encrypted_message.sender,
            aes_encryption_key=aes_key,
            message_service=mock_pod_mailbox.message_service,
            pod_mailbox_ids=encrypted_message.pod_mailbox_ids,
            pod_public_keys=mock__get_pod_public_keys.return_value,
            private_key=mock_pod_keys.private,
            task_id=opt_task_id,
        )

        # Ensure worker was created correctly
        ds = pod.datasource
        assert ds is not None
        mock_worker_cls.assert_called_once_with(
            datasource=ds.datasource,
            schema=ds.schema,
            mailbox=mock_interpod_worker_mailbox_cls.return_value,
            bitfounthub=pod._hub,
            authorisation=mock__create_authorisation_checker.return_value,
            pod_dp=pod._pod_dp,
            pod_vitals=mock_pod_vitals,
            parent_pod_identifier=pod.pod_identifier,
            data_identifier=pod.pod_identifier,
            serialized_protocol=task_protocol_details,
            pod_db=False,
            show_datapoints_in_results_db=False,
            run_on_new_data_only=False,
            project_id=None,
            batched_execution=False,
            multi_pod_task=False,
        )

        # Ensure interpod mailbox creation logged
        debug_logs = get_debug_logs(caplog)
        assert "Creating mailbox with inter-pod support." in debug_logs

    def test__create_authorisation_checker_creates_saml_checker(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test SAML Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.SAML.value,
            _EncryptedTaskRequest(
                # no need to actually encrypt
                task_request.serialize()
            ).serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)

        mock_saml_authorisation = mocker.patch(
            "bitfount.federated.pod._SAMLAuthorisation", autospec=True
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_saml_authorisation.return_value

        mock_saml_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            access_manager=pod._access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=task_protocol_details,
        )

    def test__create_authorisation_checker_creates_signature_checker(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test Signature Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        packed_request = _SignedEncryptedTaskRequest(
            # no need to actually encrypt
            task_request.serialize(),
            signature=b"signature",
        )
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.KEYS.value,
            packed_request.serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)
        mock_worker_mailbox.modeller_name = "modeller_name"

        mock_signature_authorisation = mocker.patch(
            "bitfount.federated.pod._SignatureBasedAuthorisation", autospec=True
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_signature_authorisation.return_value

        mock_signature_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            access_manager=pod._access_manager,
            modeller_name="modeller_name",
            encrypted_task_request=packed_request.encrypted_request,
            signature=packed_request.signature,
            serialized_protocol=task_protocol_details,
        )

    def test__create_authorisation_checker_removes_schema_protocol(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test Signature Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(
                class_name="some algorithm",
                model=SerializedModel(class_name="model", schema="bla"),  # type: ignore[typeddict-item] # Reason: testing purposes  # noqa: B950
            ),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        packed_request = _SignedEncryptedTaskRequest(
            # no need to actually encrypt
            task_request.serialize(),
            signature=b"signature",
        )
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.KEYS.value,
            packed_request.serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)
        mock_worker_mailbox.modeller_name = "modeller_name"

        mock_signature_authorisation = mocker.patch(
            "bitfount.federated.pod._SignatureBasedAuthorisation", autospec=True
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_signature_authorisation.return_value
        serialized_algorithm = cast(
            SerializedAlgorithm, task_protocol_details["algorithm"]
        )
        serialized_algorithm["model"].pop("schema")
        mock_signature_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            access_manager=pod._access_manager,
            modeller_name="modeller_name",
            encrypted_task_request=packed_request.encrypted_request,
            signature=packed_request.signature,
            serialized_protocol=task_protocol_details,
        )

    def test__create_authorisation_checker_creates_oidc_auth_code_checker(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test OIDC Authorization Code Flow Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        packed_request = _EncryptedTaskRequest(
            # no need to actually encrypt
            task_request.serialize(),
        )
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.OIDC_ACF_PKCE.value,
            packed_request.serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)

        # Mock authorisation checker class import
        mock_oidc_authorisation = mocker.patch(
            "bitfount.federated.pod._OIDCAuthorisationCode", autospec=True
        )

        # Mock _get_auth_environment() function
        mocker.patch(
            "bitfount.federated.pod._get_auth_environment",
            autospec=True,
            return_value=_AuthEnv(
                name="auth_env_name",
                auth_domain="auth_env_auth_domain",
                client_id="auth_env_client_id",
            ),
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_oidc_authorisation.return_value
        mock_oidc_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            access_manager=pod._access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=task_protocol_details,
            _auth_domain="auth_env_auth_domain",
            _client_id="auth_env_client_id",
        )

    def test__create_authorisation_checker_creates_oidc_device_code_checker(
        self,
        mock_rsa_decryption: Mock,
        mocker: MockerFixture,
        modeller_name: str,
        pod: Pod,
    ) -> None:
        """Test OIDC Device Code Flow Authorisation Checker created."""
        task_protocol_details = SerializedProtocol(
            class_name="some protocol",
            algorithm=SerializedAlgorithm(class_name="some algorithm"),
        )
        task_request = _TaskRequest(task_protocol_details, [], b"aes_key")
        packed_request = _EncryptedTaskRequest(
            # no need to actually encrypt
            task_request.serialize(),
        )
        task_request_message = _TaskRequestMessage(
            task_protocol_details,
            IdentityVerificationMethod.OIDC_DEVICE_CODE.value,
            packed_request.serialize(),
        )

        mock_worker_mailbox = Mock(_WorkerMailbox)

        # Mock authorisation checker class import
        mock_oidc_device_code_authorisation = mocker.patch(
            "bitfount.federated.pod._OIDCDeviceCode", autospec=True
        )

        # Mock _get_auth_environment() function
        mocker.patch(
            "bitfount.federated.pod._get_auth_environment",
            autospec=True,
            return_value=_AuthEnv(
                name="auth_env_name",
                auth_domain="auth_env_auth_domain",
                client_id="auth_env_client_id",
            ),
        )

        authorisation_checker = pod._create_authorisation_checker(
            task_request_message=task_request_message,
            sender=modeller_name,
            worker_mailbox=mock_worker_mailbox,
        )

        assert authorisation_checker == mock_oidc_device_code_authorisation.return_value
        mock_oidc_device_code_authorisation.assert_called_once_with(
            pod_response_message=_PodResponseMessage(modeller_name, pod.pod_identifier),
            access_manager=pod._access_manager,
            mailbox=mock_worker_mailbox,
            serialized_protocol=task_protocol_details,
            _auth_domain="auth_env_auth_domain",
            _client_id="auth_env_client_id",
        )

    @fixture
    def mock_sub_datasource(self) -> Mock:
        """Mock sub datasource for use in Pod._datasources."""
        mock_sub_datasource: Mock = create_autospec(BaseSource, instance=True)
        return mock_sub_datasource

    @fixture
    def mock_view_config(self) -> Mock:
        """Mock view config for use in Pod._datasources."""
        mock_view_config: Mock = create_autospec(ViewDatasourceConfig, instance=True)
        return mock_view_config

    @fixture
    def mock_sql_view_config(self) -> Mock:
        """Mock view config for use in Pod._datasources."""
        mock_sql_view_config: Mock = create_autospec(SQLViewConfig, instance=True)
        return mock_sql_view_config

    @fixture
    def pod_sub_datasources(
        self,
        mock_sub_datasource: Mock,
        mock_view_config: Mock,
        pod_name: str,
    ) -> Dict[str, DatasourceContainer]:
        """Additional datasources/views to store in Pod._datasources."""
        mock_sub_datasource_container = create_dataclass_mock(DatasourceContainer)
        mock_sub_datasource_container.datasource = mock_sub_datasource

        mock_view_config_container = create_dataclass_mock(DatasourceContainer)
        mock_view_config_container.datasource = mock_view_config
        mock_view_config_container.data_config.datasource_args = {
            "source_dataset": pod_name
        }

        return {
            "sub_source": mock_sub_datasource_container,
            "view": mock_view_config_container,
        }

    @fixture()
    def mock_pod(
        self,
        pod_name: str,
        username: str,
        mock_pod_data_config: Mock,
        mock_pod_details_config: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: Mock,
        mock_access_manager: Mock,
        mock_sub_datasource: Mock,
        mock_view_config: Mock,
        mocker: MockerFixture,
    ) -> Pod:
        """Pod fixture."""
        mock_sub_datasource_container = create_dataclass_mock(DatasourceContainer)
        mock_sub_datasource_container.name = pod_name
        mock_sub_datasource_container.datasource = mock_sub_datasource

        mock_view_config_container = create_dataclass_mock(DatasourceContainer)
        mock_view_config_container.name = "testview"
        mock_view_config_container.datasource = mock_view_config
        mock_view_config_container.data_config.datasource_args = {
            "source_dataset_name": pod_name
        }
        mocker.patch("bitfount.federated.pod.Pod._load_basesource_schema_if_necessary")
        mocker.patch("bitfount.federated.pod.Pod._load_view_schema_if_necessary")
        mocker.patch("bitfount.federated.pod._check_and_update_pod_ids")
        pod = Pod(
            name="testpod",
            datasources=[mock_sub_datasource_container, mock_view_config_container],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
        )
        return pod

    @pytest.mark.parametrize(
        argnames=("requested_datasource", "expected_datasource"),
        argvalues=(
            ("sub_source", lazy_fixture("mock_sub_datasource")),
            ("view", lazy_fixture("mock_view_config")),
            (lazy_fixture("pod_name"), lazy_fixture("mock_datasource")),
        ),
    )
    def test__get_target_datasource(
        self,
        expected_datasource: Mock,
        mock_view_config: Mock,
        mocker: MockerFixture,
        pod: Pod,
        pod_sub_datasources: Dict[str, DatasourceContainer],
        requested_datasource: str,
    ) -> None:
        """Test that _get_target_datasource returns expected datasource/view.

        3 different datasources are tested:
            - A view, that will wrap a built-in datasource
            - A sub datasource, explicitly added in Pod.datasources
            - The datasource already within Pod.datasources
        """
        # Mock out _extract_requested_datasource
        mocker.patch.object(
            pod,
            "_extract_requested_datasource",
            autospec=True,
            return_value=requested_datasource,
        )

        # Add subsidiary datasources to pod
        pod.datasources.update(pod_sub_datasources)

        ds, _ = pod._get_target_datasource_schema(message=Mock())

        if requested_datasource == "view":
            assert ds == expected_datasource.build.return_value
            mock_view_config.build.assert_called_once()
        else:
            assert ds == expected_datasource

    def test__get_target_datasource_error_on_missing_requested_datasource(
        self,
        mocker: MockerFixture,
        pod: Pod,
    ) -> None:
        """Test _get_target_datasource() errors on missing requested datasource.

        This situation happens when the `requested_datasource` from the message
        is one that does not exist.
        """
        mocker.patch.object(pod, "_extract_requested_datasource", return_value=None)

        with pytest.raises(
            BitfountTaskStartError,
            match="Failed to start task addressed to recipient_mailbox_id='None'",
        ):
            pod._get_target_datasource_schema(Mock())

    @pytest.mark.parametrize(
        "missing_source_dataset_arg",
        (False, True),
        ids=lambda x: f"missing_source_dataset_arg={x}",
    )
    def test__get_target_datasource_error_on_missing_view_source_datasource(
        self,
        missing_source_dataset_arg: bool,
        mocker: MockerFixture,
        pod: Pod,
    ) -> None:
        """Test _get_target_datasource() errors on missing view source datasource.

        This situation happens when the `requested_datasource` from the message
        is a view and the datasource referenced in the view is missing OR if the
        view fails to specify "source_dataset" in its args.
        """
        # Get _extract_requested_datasource() to return the name of a view object
        view_datasource_name = "underlying_datasource"
        mocker.patch.object(
            pod, "_extract_requested_datasource", return_value=view_datasource_name
        )

        # Set up view datasource referencing either a non-existent source datasource
        # OR failing to reference any source datasource at all.
        if missing_source_dataset_arg:
            datasource_args = {}
        else:
            datasource_args = {"source_dataset": "non-existent-datasource"}
        mock_view_datasource = Mock(
            **{
                "data_config.datasource_args": datasource_args,
                "datasource": Mock(ViewDatasourceConfig),
            }
        )
        mock_view_datasource.name = view_datasource_name  # https://docs.python.org/3.8/library/unittest.mock.html#mock-names-and-the-name-attribute # noqa: B950

        # Set the view datasource as the sole datasource of the pod
        pod.datasources = {view_datasource_name: mock_view_datasource}
        if missing_source_dataset_arg:
            with pytest.raises(
                PodViewError,
                match=(
                    f"Failed to find source_dataset"
                    f" for view datasource {view_datasource_name}"
                ),
            ):
                pod._get_target_datasource_schema(Mock())
        else:
            with pytest.raises(
                BitfountTaskStartError,
                match=(
                    f"Failed to find source_dataset"
                    f" for view datasource {view_datasource_name}"
                ),
            ):
                pod._get_target_datasource_schema(Mock())

    @pytest.mark.parametrize(
        "recipient_mailbox_id", (lazy_fixture("pod_name"), "other_datasource")
    )
    def test__extract_requested_datasource(
        self, pod: Pod, pod_name: str, recipient_mailbox_id: str
    ) -> None:
        """Tests extraction of requested datasource from the received message.

        If datasource with that name is available, should return the name.
        `pod_name` is already on the pod datasources list.

        If not available, should return None.
        """
        mock_message = create_autospec(_BitfountMessage, instance=True)
        mock_message.recipient_mailbox_id = recipient_mailbox_id

        extracted_datasource = pod._extract_requested_datasource(mock_message)

        if recipient_mailbox_id == pod_name:
            assert extracted_datasource == pod_name
        else:
            assert extracted_datasource is None

    async def test__pod_heartbeat_handles_RequestException(
        self, caplog: LogCaptureFixture, mock_bitfount_hub: Mock, pod: Pod
    ) -> None:
        """Tests _pod_heartbeat handles RequestException from hub."""
        mock_bitfount_hub.do_pod_heartbeat.side_effect = RequestException
        await pod._pod_heartbeat()
        assert "Could not connect to hub for status:" in caplog.text

    async def test__pod_heartbeat_handles_HTTPError(
        self, caplog: LogCaptureFixture, mock_bitfount_hub: Mock, pod: Pod
    ) -> None:
        """Tests _pod_heartbeat handles HTTPError from hub."""
        mock_bitfount_hub.do_pod_heartbeat.side_effect = HTTPError
        await pod._pod_heartbeat()
        assert "Failed to reach hub for status:" in caplog.text

    def test_run_pod_heartbeat_task_responds_to_stop_event(self, pod: Pod) -> None:
        """Tests that the Pod heartbeat stops when stop event is set."""
        pod_heartbeat = pod._get_pod_heartbeat_thread()
        # Start heartbeat thread
        pod_heartbeat.start()

        # Wait a few seconds to ensure that the heart has beaten once
        time.sleep(5)

        # Ensure that the pod called the hub heartbeat method
        pod._hub.do_pod_heartbeat.assert_called()  # type: ignore[attr-defined] # Reason: attribute is mocked # noqa: B950

        # Check that the thread is alive and well
        assert pod_heartbeat.is_alive()
        assert not pod_heartbeat.stopped

        # Set the stop event
        pod_heartbeat.stop()
        assert pod_heartbeat.stopped

        # Waiting 15 seconds for the thread to stop
        pod_heartbeat.join(15)
        assert not pod_heartbeat.is_alive()

    def test_pod_cleans_up_if_an_exception_is_encountered(
        self, caplog: LogCaptureFixture, mocker: MockerFixture, pod: Pod, pod_name: str
    ) -> None:
        """Tests that the Pod cleans up after itself after an exception."""
        caplog.set_level("INFO")
        pod._mailbox.listen_indefinitely.side_effect = ValueError(  # type: ignore[union-attr] # Reason: attribute is mocked # noqa: B950
            "not-a-real-exception"
        )
        mocker.patch.object(pod, "_initialise")
        mock_heartbeat_thread = mocker.patch.object(pod, "_get_pod_heartbeat_thread")
        mock_vitals_server = mocker.patch.object(
            pod, "_run_pod_vitals_server", return_value=AsyncMock()
        )
        with pytest.raises(ValueError, match="not-a-real-exception"):
            pod.start()

            # Ensure Pod went through the cleanup process
            assert f"Pod {pod_name} stopped." in caplog.records[-1].msg
            mock_heartbeat_thread.stop.assert_called_once()
            mock_heartbeat_thread.join.assert_called_once()
            mock_vitals_server.runner.cleanup.assert_awaited_once()

    @pytest.mark.parametrize(
        argnames=("exception_cls", "exception_msg"),
        argvalues=(
            (HTTPError, "Failed to register with hub"),
            (RequestException, "Could not connect to hub"),
            (SchemaUploadError, "Failed to register with hub"),
        ),
    )
    def test__register_pod_handles_exceptions(
        self,
        caplog: LogCaptureFixture,
        exception_cls: Type[Exception],
        exception_msg: str,
        mock_bitfount_hub: Mock,
        pod: Pod,
    ) -> None:
        """Tests _register_pod handles HTTPError from hub."""
        mock_bitfount_hub.register_pod.side_effect = exception_cls

        ds = pod.datasource
        assert ds is not None

        public_metadata = pod._get_public_metadata(
            ds.name, ds.datasource_details, ds.schema
        )

        with pytest.raises(PodRegistrationError, match=re.escape(exception_msg)):
            pod._register_pod(public_metadata)

        assert exception_msg in caplog.text

    def test__get_default_pod_keys_with_keys(
        self, mock_pod_keys: DataclassMock, pod: Pod
    ) -> None:
        """Tests that the default pod keys are loaded correctly with keys."""
        # Check that the keys are simply extracted and returned
        private_key, public_key = pod._get_default_pod_keys(mock_pod_keys)
        assert private_key == mock_pod_keys.private
        assert public_key == mock_pod_keys.public

    def test__get_default_pod_keys_with_None(
        self, mocker: MockerFixture, pod: Pod
    ) -> None:
        """Tests that the default pod keys are loaded correctly with no keys."""
        # Mock out get_pod_keys() function
        mock_get_pod_keys = mocker.patch(
            "bitfount.federated.pod._get_pod_keys", autospec=True
        )
        mock_private_key = create_autospec(RSAPrivateKey, instance=True)
        mock_get_pod_keys.return_value.private = mock_private_key
        mock_public_key = create_autospec(RSAPublicKey, instance=True)
        mock_get_pod_keys.return_value.public = mock_public_key

        # Explicitly call this with None
        private_key, public_key = pod._get_default_pod_keys(None)

        assert private_key == mock_private_key
        assert public_key == mock_public_key

    def test_pod_init_no_am_key(
        self,
        approved_pods: List[str],
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that the default access manager key is loaded."""
        # Mock out get_access_manager_key() function.
        mock_bitfount_am_key = mocker.patch.object(
            bitfount.federated.pod.BitfountAM, "get_access_manager_key"
        )
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=None,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        mock_bitfount_am_key.assert_called_once()

    def test_pod_no_approved_pods(
        self,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that the default approved workers are loaded correctly.

        Approved workers will be the pod's own name if no other approved
        workers defined.
        """
        pod = Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=None,
        )
        assert pod.approved_pods == [f"{username}/{pod_name}"]

    @pytest.mark.parametrize(
        argnames=("cli_mode", "expected_exc"),
        argvalues=((True, SystemExit), (False, PodRegistrationError)),
    )
    def test_pod_init_fails_if_cannot_register(
        self,
        cli_mode: bool,
        expected_exc: Type[BaseException],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        monkeypatch: MonkeyPatch,
        pod_name: str,
        username: str,
    ) -> None:
        """Test Pod init fails if cannot register with hub."""
        # Set _BITFOUNT_CLI_MODE config variable to elicit different error handling
        monkeypatch.setattr(bitfount.config, "_BITFOUNT_CLI_MODE", cli_mode)

        mocker.patch.object(
            Pod, "_register_pod", side_effect=PodRegistrationError("ERROR")
        )

        with pytest.raises(expected_exc, match="ERROR"):
            Pod(
                name=pod_name,
                datasources=[
                    DatasourceContainerConfig(
                        name=pod_name,
                        datasource_details=mock_pod_details_config,
                        datasource=mock_datasource,
                        data_config=mock_pod_data_config,
                        schema=None,
                    )
                ],
                username=username,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
                pod_keys=mock_pod_keys,
            )

    def test_pod_fails_no_csv_path(
        self, mock_pod_data_config: DataclassMock, pod: Pod
    ) -> None:
        """Tests that the pod does not load data with non-csv extension."""
        with pytest.raises(
            TypeError, match="Please provide a Path or URL to a CSV file."
        ):
            datasource = CSVSource(Path("mock.pdf"))
            pod._setup_schema(
                datasource_name=pod.name,
                datasource=datasource,
                data_config=mock_pod_data_config,
            )

    def test_pod_auto_tidy_is_not_applied_with_multi_table_datasource(
        self,
        caplog: LogCaptureFixture,
        mock_engine: Mock,
        mock_pod_data_config: DataclassMock,
        pod: Pod,
    ) -> None:
        """Tests that the pod does not auto tidy multi-table datasource."""
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        datasource = DatabaseSource(db_conn)
        datasource.validate()
        mock_pod_data_config.auto_tidy = True
        mock_schema = Mock()
        pod._setup_schema(
            datasource_name=pod.name,
            datasource=datasource,
            data_config=mock_pod_data_config,
            schema=mock_schema,
        )
        mock_schema.add_datasource_tables.assert_called_once()
        assert "Can't autotidy multi-table data." in caplog.text

    def test_pod_fails_wrong_data(
        self, mock_pod_data_config: DataclassMock, pod: Pod
    ) -> None:
        """Tests that the pod does not load data in an unaccepted data format."""
        with pytest.raises(
            TypeError,
            match=(
                "Invalid data attribute. Expected pandas dataframe "
                "but received :<class 'unittest.mock.Mock'>"
            ),
        ):
            datasource = DataFrameSource(Mock())
            pod._setup_schema(
                datasource_name=pod.name,
                datasource=datasource,
                data_config=mock_pod_data_config,
            )

    def test__setup_schema_single_excelsource(
        self,
        mock_pod_data_config: DataclassMock,
        pod: Pod,
        single_table_excel_source: ExcelSource,
    ) -> None:
        """Test schema is generated correctly for single tables excel source."""
        schema = pod._setup_schema(pod.name, single_table_excel_source, PodDataConfig())
        assert schema is not None
        assert len(schema.tables) == 1

    def test__setup_schema_multitable_excelsource(
        self,
        mock_pod_data_config: DataclassMock,
        multi_table_excel_source: ExcelSource,
        pod: Pod,
    ) -> None:
        """Test schema is generated correctly for multi tables excel source."""
        schema = pod._setup_schema(pod.name, multi_table_excel_source, PodDataConfig())
        assert schema is not None
        assert len(schema.tables) == 2

    def test_read_sql_tabular(self, mocker: MockerFixture, pod: Pod) -> None:
        """Tests that the pod reads tabular sql data with one table."""
        # Mock out pandas interaction
        dataset = create_dataset()
        dtypes = dataset.convert_dtypes().dtypes.to_dict()
        mocker.patch.object(pd, "read_sql_query", return_value=dataset)
        mocker.patch.object(pd, "read_sql", return_value=dataset)
        db_conn = Mock(
            spec=DatabaseConnection,
            table_names=["table1"],
            multi_table=False,
            query=None,
            con=Mock(),
            db_schema="test",
        )
        datasource = DatabaseSource(db_conn=db_conn)
        datasource.validate()
        datasource._table_hashes.add(_generate_dtypes_hash(dtypes))
        mocker.patch.object(datasource, "get_dtypes", return_value=dtypes)

        mock_pod_config = PodDataConfig(force_stypes={})
        schema = pod._setup_schema(
            datasource_name=pod.name, datasource=datasource, data_config=mock_pod_config
        )

        assert schema is not None
        assert isinstance(schema, BitfountSchema)

    def test__setup_schema(
        self, mock_pod_data_config: DataclassMock, mocker: MockerFixture, pod: Pod
    ) -> None:
        """Tests that the pod schema works as expected."""
        # Mock out BaseSource/BitfountSchema constructor as not under test here.
        mock_datasource: Mock = mocker.patch(
            "bitfount.federated.pod.BaseSource", autospec=True, multi_table=False
        )
        mock_schema = Mock(spec=BitfountSchema)
        mocker.patch("bitfount.federated.pod.BitfountSchema", return_value=mock_schema)
        mock_pod_data_config.auto_tidy = False
        schema = pod._setup_schema(
            datasource_name=pod.name,
            datasource=mock_datasource,
            data_config=mock_pod_data_config,
        )

        # Assert that bitfount schema is constructed with the datasource
        assert (
            get_arg_from_args_or_kwargs(
                mock_schema.add_datasource_tables.call_args,
                args_idx=0,
                kwarg_name="datasource",
            )
            == mock_datasource
        )
        assert isinstance(schema, BitfountSchema)

    def test__setup_schema_applies_transformation_to_floats_only(
        self, pod: Pod
    ) -> None:
        """Tests that pod auto-tidy applies normalization to float columns only."""
        datasource = create_datasource(classification=True)
        data_config = PodDataConfig(auto_tidy=True)
        pod._setup_schema(
            datasource_name=pod.name,
            datasource=datasource,
            data_config=data_config,
        )
        # Check float dtypes
        assert round(datasource.data["E"].mean()) == 0
        assert round(datasource.data["E"].std()) == 1
        assert round(datasource.data["F"].mean()) == 0
        assert round(datasource.data["F"].std()) == 1
        assert round(datasource.data["G"].mean()) == 0
        assert round(datasource.data["G"].std()) == 1
        assert round(datasource.data["H"].mean()) == 0
        assert round(datasource.data["H"].std()) == 1
        # Check int types are unchanged
        assert round(datasource.data["A"].mean()) != 0
        assert round(datasource.data["A"].std()) != 1
        assert round(datasource.data["B"].mean()) != 0
        assert round(datasource.data["B"].std()) != 1
        assert round(datasource.data["C"].mean()) != 0
        assert round(datasource.data["C"].std()) != 1
        assert round(datasource.data["C"].mean()) != 0
        assert round(datasource.data["C"].std()) != 1

    def test_default_pod_details_generation(self, pod: Pod) -> None:
        """Tests the default pod details generation."""
        assert pod._get_default_pod_details_config() == PodDetailsConfig(
            display_name=pod.name,
            description=pod.name,
        )

    async def test__initialise_creates_mailbox(
        self, mock_pod_mailbox: Mock, mock_pod_mailbox_create_helper: Mock, pod: Pod
    ) -> None:
        """Tests that _initialise() creates a mailbox for the pod."""
        # Set the mailbox on generated pod to None to mimic no initialization.
        pod._mailbox = None
        assert pod._mailbox is None
        assert not pod._initialised

        await pod._initialise()

        # Check mailbox is present and what we expect
        assert pod._mailbox is not None
        assert pod._mailbox == mock_pod_mailbox

        # Check marked as initialized
        assert pod._initialised

    async def test__initialise_warns_when_called_multiple(
        self,
        caplog: LogCaptureFixture,
        mock_pod_mailbox: Mock,
        mock_pod_mailbox_create_helper: Mock,
        pod: Pod,
    ) -> None:
        """Tests that _initialise() creates a mailbox for the pod."""
        # Set the mailbox on generated pod to None to mimic no initialization.
        pod._mailbox = None
        assert pod._mailbox is None
        assert not pod._initialised

        await pod._initialise()

        # Check mailbox is present and what we expect
        assert pod._mailbox is not None
        assert pod._mailbox == mock_pod_mailbox
        assert pod._initialised

        # Check no log yet
        assert (
            "Pod._initialise() called twice. This is not allowed."
            not in get_warning_logs(caplog)
        )

        # Call second time
        await pod._initialise()

        # Check unchanged
        assert pod._mailbox is not None
        assert pod._mailbox == mock_pod_mailbox
        assert pod._initialised

        # Check warning issued
        assert (
            "Pod._initialise() called twice. This is not allowed."
            in get_warning_logs(caplog)
        )

    def test_start_calls__initialise(
        self, mock_pod_mailbox: Mock, mocker: MockerFixture, pod: Pod
    ) -> None:
        """Tests that Pod._initialise() is inherently called in Pod.start()."""
        # Patch out _initialise() so we can assert it is called
        mock_initialise = mocker.patch.object(pod, "_initialise", autospec=True)

        # Patch mailbox so we can avoid the _listen_for_messages() looping forever
        pod._mailbox = mock_pod_mailbox

        pod.start()

        # Check _initialise() was called
        mock_initialise.assert_called_once()

    def test_init_works_with_existing_schema_file(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_bitfount_schema: NonCallableMock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that Pod.__init__ works with existing schema files."""
        # Mock out actual schema loading
        mock_bitfount_schema.tables = []
        mock_load_from_file = mocker.patch.object(
            BitfountSchema,
            "load_from_file",
            autospec=True,
            return_value=mock_bitfount_schema,
        )

        # Load pod with fake schema path
        schema_path = "not_a_real_path"
        pod = Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=schema_path,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        # Check correct calls made to schema loading
        mock_load_from_file.assert_called_once_with(schema_path)

        # This is where and how the schema is stored
        ds = pod.datasource
        assert ds is not None
        assert ds.schema == mock_bitfount_schema

    def test__setup_data_works_with_existing_schema(
        self,
        mock_bitfount_schema: NonCallableMock,
        mock_pod_data_config: DataclassMock,
        mocker: MockerFixture,
        pod: Pod,
        pod_name: str,
    ) -> None:
        """Tests that Pod._setup_schema() works with an existing schema."""
        # Mock out datasource import and creation
        mock_datasource = mocker.patch(
            "bitfount.federated.pod.BaseSource",
            autospec=True,
            multi_table=False,
        )
        mock_pod_data_config.auto_tidy = False

        # Mock out transformation application
        mocker.patch.object(TransformationProcessor, "transform")
        schema = pod._setup_schema(
            datasource_name=pod.name,
            datasource=mock_datasource,
            data_config=mock_pod_data_config,
            schema=mock_bitfount_schema,
        )

        # Check datasource added to schema
        mock_bitfount_schema.add_datasource_tables.assert_called_once_with(
            datasource=mock_datasource,
            table_name=pod_name,
            ignore_cols=mock_pod_data_config.ignore_cols,
            force_stypes=mock_pod_data_config.force_stypes,
        )
        # Check expected schema is returned
        assert schema == mock_bitfount_schema

    def test_schema_frozen_after_pod_init(
        self,
        approved_pods: List[str],
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_bitfount_schema: NonCallableMock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that Pod._setup_schema() freezes the schema."""
        mocker.patch(
            "bitfount.federated.pod.BitfountSchema",
            autospec=True,
            return_value=mock_bitfount_schema,
        )
        # Load pod
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        # Check schema was frozen
        mock_bitfount_schema.freeze.assert_called_once()
        mock_bitfount_schema.unfreeze.assert_not_called()

    @pytest.mark.parametrize("is_notebook", [True, False])
    def test__run_pod_vitals_server(
        self, is_notebook: bool, mocker: MockerFixture, pod: Pod
    ) -> None:
        """Test whether pod vitals server is ran.

        The pod vitals webserver should not be ran when
        executed from a notebook.
        """
        mock_is_notebook = mocker.patch(
            "bitfount.federated.pod.is_notebook", return_value=is_notebook
        )
        mock_handler = mocker.patch("bitfount.federated.pod._PodVitalsHandler")
        pod._run_pod_vitals_server()
        mock_is_notebook.assert_called_once()
        if is_notebook:
            mock_handler.assert_not_called()
        else:
            mock_handler.assert_called_once()

    def test_pod_schema_table_takes_pod_name_as_table_name(
        self, pod: Pod, pod_name: str
    ) -> None:
        """Tests that the schema table name is the pod name."""
        ds = pod.datasource
        assert ds is not None
        assert ds.schema.table_names == [pod_name]

    def test_pod_no_schema_generates_new_one(
        self,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests schema is generated if not provided."""
        mock_setup_schema = mocker.patch.object(Pod, "_setup_schema")
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=None,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
        )
        mock_setup_schema.assert_called_once()

    def test_pod_update_schema_flag(
        self,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mocker: MockerFixture,
        multi_table_excel_source: Mock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests schema is re-generated if update_schema is True."""
        mock_setup_schema = mocker.patch.object(Pod, "_setup_schema")

        schema = BitfountSchema()
        schema.add_datasource_tables(multi_table_excel_source, table_name="Sheet1")
        schema.add_datasource_tables(multi_table_excel_source, table_name="Sheet2")
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=multi_table_excel_source,
                    data_config=mock_pod_data_config,
                    schema=schema,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            update_schema=True,
        )
        mock_setup_schema.assert_called_once()

    def test_pod_with_schema(
        self,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests schema is not re-generated when provided."""
        mock_setup_schema = mocker.patch.object(Pod, "_setup_schema")
        schema = BitfountSchema()
        schema.add_datasource_tables(mock_datasource, table_name=pod_name)
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=schema,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
        )
        mock_setup_schema.assert_not_called()

    def test_pod_with_schema_wrong_table_name(
        self,
        caplog: LogCaptureFixture,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests schema warning is issued when it is missing the correct table name."""
        mock_setup_schema = mocker.patch.object(Pod, "_setup_schema")
        schema = BitfountSchema()

        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=schema,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
        )

        mock_setup_schema.assert_not_called()
        assert (
            "Provided schema table name does not match to datasource name,"
            " you may need to regenerate the schema." in get_warning_logs(caplog)
        )

    def test_pod_w_schema_auto_tidy(
        self,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests schema is re-generated with auto_tidy True."""
        mock_setup_schema = mocker.patch.object(Pod, "_setup_schema")
        mock_pod_data_config.auto_tidy = True
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=mock_datasource,
                    data_config=mock_pod_data_config,
                    schema=BitfountSchema(),
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
        )
        mock_setup_schema.assert_called_once()

    def test_pod_w_schema_multitable_all_tables(
        self,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mocker: MockerFixture,
        multi_table_excel_source: Mock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests schema is not re-generated multi-table datasource."""
        mock_setup_schema = mocker.patch.object(Pod, "_setup_schema")
        schema = BitfountSchema()
        schema.add_datasource_tables(multi_table_excel_source, table_name="Sheet1")
        schema.add_datasource_tables(multi_table_excel_source, table_name="Sheet2")
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=multi_table_excel_source,
                    data_config=mock_pod_data_config,
                    schema=schema,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
        )
        mock_setup_schema.assert_not_called()

    def test_pod_w_schema_multitable_missing_table(
        self,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_datasource: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        mock_pod_mailbox: Mock,
        mock_pod_vitals: Mock,
        mocker: MockerFixture,
        multi_table_excel_source: Mock,
        pod_name: str,
        username: str,
    ) -> None:
        """Test schema is re-generated when missing tables."""
        mock_setup_schema = mocker.patch.object(Pod, "_setup_schema")
        schema = BitfountSchema()
        schema.add_datasource_tables(mock_datasource, table_name="Sheet1")
        Pod(
            name=pod_name,
            datasources=[
                DatasourceContainerConfig(
                    name=pod_name,
                    datasource_details=mock_pod_details_config,
                    datasource=multi_table_excel_source,
                    data_config=mock_pod_data_config,
                    schema=schema,
                )
            ],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
        )
        mock_setup_schema.assert_called_once()

    def test_pod_init_raises_error_with_no_registered_hooks(
        self,
        approved_pods: List[str],
        caplog: LogCaptureFixture,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that a pod init raises an error if no error hooks are registered."""
        with pytest.raises(DataSourceError):
            Pod(
                name=pod_name,
                datasource=Mock(spec=BaseSource, is_initialised=False),
                username=username,
                data_config=mock_pod_data_config,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
                pod_keys=mock_pod_keys,
                approved_pods=approved_pods,
            )

    def test_pod_init_error_hook_catches_error(
        self,
        approved_pods: List[str],
        caplog: LogCaptureFixture,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that a pod exception is caught by an error hook.

        Also tests that the error hook is called.
        """

        class DummyPodHook(BasePodHook):
            """Dummy hook to catch init errors."""

            def on_pod_init_error(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
                """Log an error message."""
                logging.error("Error hook caught error")

        DummyPodHook().register()
        Pod(
            name=pod_name,
            datasource=Mock(spec=BaseSource, is_initialised=False),
            username=username,
            data_config=mock_pod_data_config,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        # Assert the hook log message is present
        assert "Error hook caught error" in caplog.text
        # Assert the error is logged
        assert "DataSourceError" in caplog.text

    def test_pod_hook_registered_but_not_implemented(
        self,
        approved_pods: List[str],
        caplog: LogCaptureFixture,
        mock_access_manager: Mock,
        mock_bitfount_hub: Mock,
        mock_message_service_config: DataclassMock,
        mock_pod_data_config: DataclassMock,
        mock_pod_details_config: DataclassMock,
        mock_pod_keys: DataclassMock,
        pod_name: str,
        username: str,
    ) -> None:
        """Tests that a warning message is logged if the hook is not implemented."""

        class DummyPodHook(BasePodHook):
            """Dummy hook with no implemented methods."""

        DummyPodHook().register()
        Pod(
            name=pod_name,
            datasource=Mock(spec=BaseSource, is_initialised=False),
            username=username,
            data_config=mock_pod_data_config,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_keys=mock_pod_keys,
            approved_pods=approved_pods,
        )

        # Assert the hook log message is present
        assert "DummyPodHook has not implemented hook on_pod_init_error" in caplog.text
        # Assert the error is logged
        assert "DataSourceError" in caplog.text

    def test_pod_run_raises_error_with_no_registered_hooks(
        self,
        mocker: MockerFixture,
        pod: Pod,
    ) -> None:
        """Tests that a pod run raises an error if no error hooks are registered."""

        def patched_run(*args: Any) -> None:
            """Patch the run method to raise an error."""
            raise ValueError("Test")

        mocker.patch("bitfount.federated.pod.asyncio.run", side_effect=patched_run)
        with pytest.raises(ValueError, match="Test"):
            pod.start()

    def test_pod_run_error_hook_catches_error(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        pod: Pod,
    ) -> None:
        """Tests that a pod exception is caught by an error hook.

        Also tests that the error hook is called.
        """

        class DummyPodHook(BasePodHook):
            """Dummy hook to catch run errors."""

            def on_pod_startup_error(self, pod: Pod, *args: Any, **kwargs: Any) -> None:
                """Log an error message."""
                logging.error("Error hook caught error")

        def patched_run(*args: Any) -> None:
            """Patch the run method to raise an error."""
            raise ValueError("Test")

        DummyPodHook().register()

        mocker.patch("bitfount.federated.pod.asyncio.run", side_effect=patched_run)
        pod.start()
        # Assert the hook log message is present
        assert "Error hook caught error" in caplog.text
        # Assert the error is logged
        assert "ValueError" in caplog.text

    @pytest.mark.parametrize(
        argnames=(
            "datasources",
            "datasource",
            "pod_name",
            "datasource_details",
            "data_config",
            "schema",
            "expected_err_msg",
        ),
        argvalues=(
            pytest.param(
                Mock(),  # datasources
                Mock(),  # datasource
                None,  # pod_name
                None,  # datasource_details
                None,  # data_config
                None,  # schema
                "Only one of `datasource` and `datasources` can be specified.",
                id="both specified",
            ),
            pytest.param(
                None,  # datasources
                None,  # datasource
                None,  # pod_name
                None,  # datasource_details
                None,  # data_config
                None,  # schema
                "One of `datasource` and `datasources` must be specified.",
                id="neither specified",
            ),
            pytest.param(
                Mock(),  # datasources
                None,  # datasource
                None,  # pod_name
                None,  # datasource_details
                Mock(),  # data_config
                None,  # schema
                "If using `data_config` or `schema`, must supply `datasource`.",
                id="data_config datasource-only",
            ),
            pytest.param(
                Mock(),  # datasources
                None,  # datasource
                None,  # pod_name
                None,  # datasource_details
                None,  # data_config
                Mock(),  # schema
                "If using `data_config` or `schema`, must supply `datasource`.",
                id="schema datasource-only",
            ),
            pytest.param(
                None,  # datasources
                Mock(),  # datasource
                None,  # pod_name
                None,  # datasource_details
                None,  # data_config
                None,  # schema
                (
                    "When supplying `datasource`,"
                    " `pod_name` and `datasource_details` are required."
                ),
                id="datasource needs name and details 1",
            ),
            pytest.param(
                None,  # datasources
                Mock(),  # datasource
                Mock(),  # pod_name
                None,  # datasource_details
                None,  # data_config
                None,  # schema
                (
                    "When supplying `datasource`,"
                    " `pod_name` and `datasource_details` are required."
                ),
                id="datasource needs name and details 2",
            ),
            pytest.param(
                None,  # datasources
                Mock(),  # datasource
                None,  # pod_name
                Mock(),  # datasource_details
                None,  # data_config
                None,  # schema
                (
                    "When supplying `datasource`,"
                    " `pod_name` and `datasource_details` are required."
                ),
                id="datasource needs name and details 3",
            ),
        ),
    )
    def test__process_datasource_args_error_states(
        self,
        data_config: Optional[Mock],
        datasource: Optional[Mock],
        datasource_details: Optional[Mock],
        datasources: Optional[list],
        expected_err_msg: str,
        mock_pod: Pod,
        pod_name: Optional[str],
        schema: Optional[Mock],
    ) -> None:
        """Test the arg parsing/handling of _process_datasource_args().

        Tests that appropriate errors are thrown when mutually exclusive arguments
        are supplied, or when missing args that are required because of the main
        arg that has been supplied.
        """
        with pytest.raises(ValueError, match=expected_err_msg):
            mock_pod._process_datasource_args(
                datasources=datasources,
                datasource=datasource,
                pod_name=pod_name,
                datasource_details=datasource_details,
                data_config=data_config,
                schema=schema,
            )

    def test__process_datasource_args_with_datasources(self, mock_pod: Mock) -> None:
        """Test that _process_datasource_args wraps/returns `datasources`."""
        datasource_1 = create_autospec(DatasourceContainerConfig)
        datasource_1.datasource = create_autospec(BaseSource)
        datasource_1.name = "testing"
        datasource_2 = create_autospec(DatasourceContainerConfig)
        datasource_2.datasource = create_autospec(ViewDatasourceConfig)
        datasource_2.datasource.source_dataset_name = "testing"

        datasources = mock_pod._process_datasource_args(
            datasources=(datasource_1, datasource_2)
        )

        assert isinstance(datasources, list)
        assert len(datasources) == 2
        assert datasources[0] == datasource_1
        assert datasources[1] == datasource_2

    def test__process_datasource_args_with_datasource(self, mock_pod: Mock) -> None:
        """Test that _process_datasource_args wraps `datasource`.

        Check that DeprecationWarning is raised.
        """
        datasource = Mock()
        pod_name = "pod_name"
        datasource_details = Mock()

        with pytest.warns(
            DeprecationWarning,
            match=(
                "Single `datasource` specification will be replaced"
                " with `datasources` in future versions"
            ),
        ):
            datasources = mock_pod._process_datasource_args(
                datasource=datasource,
                pod_name=pod_name,
                datasource_details=datasource_details,
            )

        assert len(datasources) == 1
        datasource_container = datasources[0]
        assert datasource_container.name == pod_name
        assert datasource_container.datasource_details == datasource_details
        assert datasource_container.datasource == datasource

    def test_pod_with_datasources_init(
        self,
        mock_sub_datasource: Mock,
        mock_pod_details_config: Mock,
        mock_bitfount_hub: Mock,
        mock_access_manager: Mock,
        mock_message_service_config: Mock,
        mock_pod_keys: Mock,
        mock_view_config: Mock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Test pod init with datasources."""
        mock_sub_datasource_container = create_dataclass_mock(DatasourceContainer)
        mock_sub_datasource_container.name = pod_name
        mock_sub_datasource_container.datasource = mock_sub_datasource

        mock_view_config_container = create_dataclass_mock(DatasourceContainer)
        mock_view_config_container.name = "testview"
        mock_view_config_container.datasource = mock_view_config
        mock_view_config_container.data_config.datasource_args = {
            "source_dataset_name": pod_name
        }
        mocker.patch("bitfount.federated.pod.Pod._load_basesource_schema_if_necessary")
        mocker.patch("bitfount.federated.pod.Pod._load_view_schema_if_necessary")
        mocker.patch("bitfount.federated.pod._check_and_update_pod_ids")
        pod = Pod(
            name="testpod",
            datasources=[mock_sub_datasource_container, mock_view_config_container],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
        )
        assert pod_name in pod.base_datasources.keys()
        assert "testview" in pod.view_datasources.keys()
        assert pod_name in pod.datasources.keys()
        assert "testview" in pod.datasources.keys()

    def test_load_sql_view_no_db_error(
        self,
        mock_pod: Mock,
        mock_sql_view_config: Mock,
        mocker: MockerFixture,
        mock_sub_datasource: Mock,
        mock_pod_details_config: Mock,
        mock_bitfount_hub: Mock,
        mock_access_manager: Mock,
        mock_message_service_config: Mock,
        mock_pod_keys: Mock,
        username: str,
    ) -> None:
        """Test SQLview raises error with no pod_db."""
        mock_sub_datasource_container = create_dataclass_mock(DatasourceContainer)
        mock_sub_datasource_container.name = "test"
        mock_sub_datasource_container.datasource = mock_sub_datasource

        mock_view_config_container = create_dataclass_mock(DatasourceContainer)
        mock_view_config_container.name = "testview"
        mock_view_config_container.datasource = mock_sql_view_config
        mock_view_config_container.data_config.datasource_args = {
            "source_dataset_name": "test"
        }
        mocker.patch("bitfount.federated.pod.Pod._load_basesource_schema_if_necessary")
        mocker.patch("bitfount.federated.pod.Pod._load_view_schema_if_necessary")
        mocker.patch("bitfount.federated.pod._check_and_update_pod_ids")
        with pytest.raises(PodViewDatabaseError):
            Pod(
                name="testpod",
                datasources=[mock_sub_datasource_container, mock_view_config_container],
                username=username,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
            )

    def test_load_view_source_dataset_not_found(
        self,
        mock_pod: Mock,
        mock_sql_view_config: Mock,
        mocker: MockerFixture,
        mock_sub_datasource: Mock,
        mock_pod_details_config: Mock,
        mock_bitfount_hub: Mock,
        mock_access_manager: Mock,
        mock_message_service_config: Mock,
        pod_name: str,
        username: str,
    ) -> None:
        """Test view raises error when source dataset not found."""
        mock_sub_datasource_container = create_dataclass_mock(DatasourceContainer)
        mock_sub_datasource_container.name = "test"
        mock_sub_datasource_container.datasource = mock_sub_datasource

        mock_view_config_container = create_dataclass_mock(DatasourceContainer)
        mock_view_config_container.name = "testview"
        mock_view_config_container.datasource = mock_sql_view_config
        mock_view_config_container.data_config.datasource_args = {
            "source_dataset": pod_name
        }
        mocker.patch("bitfount.federated.pod.Pod._load_basesource_schema_if_necessary")
        mocker.patch("bitfount.federated.pod.Pod._load_view_schema_if_necessary")
        mocker.patch("bitfount.federated.pod._check_and_update_pod_ids")
        with pytest.raises(PodViewError):
            Pod(
                name="testpod",
                datasources=[mock_sub_datasource_container, mock_view_config_container],
                username=username,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
            )

    def test_load_view_no_source_dataset(
        self,
        mock_pod: Mock,
        mock_sql_view_config: Mock,
        mocker: MockerFixture,
        mock_sub_datasource: Mock,
        mock_pod_details_config: Mock,
        mock_bitfount_hub: Mock,
        mock_access_manager: Mock,
        mock_message_service_config: Mock,
        pod_name: str,
        username: str,
    ) -> None:
        """Test view raises error when source dataset not found."""
        mock_sub_datasource_container = create_dataclass_mock(DatasourceContainer)
        mock_sub_datasource_container.name = "test"
        mock_sub_datasource_container.datasource = mock_sub_datasource

        mock_view_config_container = create_dataclass_mock(DatasourceContainer)
        mock_view_config_container.name = "testview"
        mock_view_config_container.datasource = mock_sql_view_config
        mock_view_config_container.data_config.datasource_args = {
            "source_dataset": pod_name
        }
        mocker.patch("bitfount.federated.pod.Pod._load_basesource_schema_if_necessary")
        mocker.patch("bitfount.federated.pod.Pod._load_view_schema_if_necessary")
        mocker.patch("bitfount.federated.pod._check_and_update_pod_ids")
        with pytest.raises(PodViewError):
            Pod(
                name="testpod",
                datasources=[mock_sub_datasource_container, mock_view_config_container],
                username=username,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
            )

    def test_sql_view_no_pod_db(
        self,
        mock_pod: Mock,
        mock_sql_view_config: Mock,
        mock_sub_datasource: Mock,
        mock_pod_details_config: Mock,
        mock_bitfount_hub: Mock,
        mock_access_manager: Mock,
        mock_message_service_config: Mock,
        pod_name: str,
        username: str,
    ) -> None:
        """Test error raise for SQLView with no pod db."""
        mock_sub_datasource_container = create_dataclass_mock(DatasourceContainer)
        mock_sub_datasource_container.name = pod_name
        mock_sub_datasource_container.datasource = mock_sub_datasource

        mock_view_config_container = create_dataclass_mock(DatasourceContainer)
        mock_view_config_container.name = "testview"
        mock_view_config_container.datasource = mock_sql_view_config
        mock_view_config_container.data_config.datasource_args = {
            "source_dataset_name": pod_name
        }
        mock_view_config_container.schema = None
        with pytest.raises(PodViewDatabaseError):
            Pod(
                name="testpod",
                datasources=[mock_sub_datasource_container, mock_view_config_container],
                username=username,
                pod_details_config=mock_pod_details_config,
                hub=mock_bitfount_hub,
                message_service=mock_message_service_config,
                access_manager=mock_access_manager,
            )

    def test_load_view_schema(
        self,
        mock_sql_view_config: Mock,
        mock_sub_datasource: Mock,
        mock_pod_details_config: Mock,
        mock_bitfount_hub: Mock,
        mock_access_manager: Mock,
        mock_message_service_config: Mock,
        mocker: MockerFixture,
        pod_name: str,
        username: str,
    ) -> None:
        """Test _load_view_schema_if_necessary()."""
        mock_sub_datasource_container = create_dataclass_mock(DatasourceContainer)
        mock_sub_datasource_container.name = pod_name
        mock_sub_datasource_container.datasource = mock_sub_datasource
        mock_sub_datasource_container.datasource.multi_table = False

        mock_view_config_container = create_dataclass_mock(DatasourceContainer)
        mock_view_config_container.name = "testview"
        mock_view_config_container.datasource = mock_sql_view_config
        mock_view_config_container.datasource.source_dataset_name = pod_name
        mock_view_config_container.schema = None
        mock_generate_schema = mocker.patch.object(
            mock_view_config_container.datasource, "generate_schema"
        )
        mock_generate_schema.return_value = BitfountSchema()

        mock_load_base_schema = mocker.patch(
            "bitfount.federated.pod.Pod._load_basesource_schema_if_necessary"
        )
        mock_load_base_schema.return_value = mock_sub_datasource_container
        pod = Pod(
            name="testpod",
            datasources=[mock_sub_datasource_container, mock_view_config_container],
            username=username,
            pod_details_config=mock_pod_details_config,
            hub=mock_bitfount_hub,
            message_service=mock_message_service_config,
            access_manager=mock_access_manager,
            pod_db=True,
        )
        view_container = pod._load_view_schema_if_necessary(
            ds=mock_view_config_container
        )
        assert isinstance(view_container.schema, BitfountSchema)
