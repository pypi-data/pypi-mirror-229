"""Unit tests for _PodVitals webserver."""
import time
from typing import Dict, cast
from unittest.mock import AsyncMock, Mock, create_autospec

from aiohttp.test_utils import TestClient, TestServer
import desert
import pytest
from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from bitfount import BitfountSchema, DataStructure
from bitfount.data.utils import DataStructureSchemaCompatibility
from bitfount.federated.pod_vitals import _PodVitals, _PodVitalsHandler
from bitfount.runners.config_schemas import (
    DataStructureAssignConfig,
    DataStructureConfig,
    DataStructureSelectConfig,
    DataStructureTableConfig,
    DataStructureTransformConfig,
)
from bitfount.types import _JSONDict
from tests.utils.helper import unit_test
from tests.utils.mocks import create_dataclass_mock


@unit_test
class TestPodVitals:
    """Test TestPodVitals."""

    async def test__last_task_execution_time_update(self) -> None:
        """Test last_task_execution_time is updated as expected."""
        pod_vitals = _PodVitals()
        new_time = time.time()
        lock_acquired_mock = Mock()
        lock_released_mock = Mock()
        pod_vitals._last_task_execution_lock = Mock(
            __enter__=lock_acquired_mock, __exit__=lock_released_mock
        )

        pod_vitals.last_task_execution_time = new_time

        # check lock was acquired in updating last_task_execution_time
        lock_acquired_mock.assert_called_once()
        lock_released_mock.assert_called_once()
        assert pod_vitals.last_task_execution_time == new_time
        # check lock was acquired again in above assertion when
        # retrieving last_task_execution_time
        assert lock_acquired_mock.call_count == 2
        assert lock_acquired_mock.call_count == 2


@unit_test
class Test_PodVitalsHandler:
    """Test Test_PodVitalsHandler."""

    @pytest.fixture
    def pod_vitals(self) -> Mock:
        """Pod vitals mock fixture."""
        mock_pod_vitals = create_dataclass_mock(_PodVitals)
        mock_pod_vitals.last_task_execution_time = time.time()
        mock_pod_vitals.is_pod_ready.return_value = True
        return mock_pod_vitals

    @pytest.fixture
    def pod_schemas(self) -> Dict[str, Mock]:
        """Schemas for the pod attached to the vitals server."""
        schemas = {
            "dataset1": create_autospec(BitfountSchema, name="dataset1"),
            "dataset2": create_autospec(BitfountSchema, name="dataset2"),
        }
        for k, v in schemas.items():
            v.to_json.return_value = f"to_json_of_{k}"
        return schemas

    @pytest.fixture(scope="class")
    def datastructure_config(self) -> DataStructureConfig:
        """Example datastructure config for a task."""
        return DataStructureConfig(
            table_config=DataStructureTableConfig(table="table_name"),
            assign=DataStructureAssignConfig(target="target_col"),
            select=DataStructureSelectConfig(include=["select_col_1", "select_col_2"]),
            transform=DataStructureTransformConfig(),
        )

    @pytest.fixture
    def datastructure(self, datastructure_config: DataStructureConfig) -> DataStructure:
        """Example datastructure built from datastructure_config."""
        return DataStructure.create_datastructure(
            datastructure_config.table_config,
            datastructure_config.select,
            datastructure_config.transform,
            datastructure_config.assign,
        )

    @pytest.fixture(scope="class")
    def datastructure_config_json(
        self, datastructure_config: DataStructureConfig
    ) -> _JSONDict:
        """Example datastructure config for a task in JSON format."""
        return cast(
            _JSONDict, desert.schema(DataStructureConfig).dump(datastructure_config)
        )

    @pytest.fixture
    def handler(
        self, pod_vitals: _PodVitals, pod_schemas: Dict[str, Mock]
    ) -> _PodVitalsHandler:
        """Pod vitals handler fixture."""
        handler = _PodVitalsHandler(
            pod_vitals, cast(Dict[str, BitfountSchema], pod_schemas)
        )
        handler.runner = Mock()
        return handler

    @pytest.fixture
    def server(self, handler: _PodVitalsHandler) -> TestServer:
        """Test server fixture."""
        return TestServer(handler.app)

    @pytest.fixture
    def mock_open_socket(self, mocker: MockerFixture) -> AsyncMock:
        """Mocks out the Modeller.run() method in protocol.py."""
        mock_open_socket_method: AsyncMock = mocker.patch(
            "bitfount.federated.pod_vitals._PodVitalsHandler._open_socket"
        )
        mock_open_socket_method.return_value = 8080
        return mock_open_socket_method

    async def test__status_request(self, server: TestServer) -> None:
        """Test /status endpoint to determines if the webserver is responding."""
        async with TestClient(server) as client:
            resp = await client.request("GET", "/status")
            json_resp = await resp.json()
            assert resp.status == 200
            assert json_resp == {"status": "OK"}

    async def test__health_request(self, server: TestServer) -> None:
        """Test /health endpoint determines if a pod is healthy."""
        async with TestClient(server) as client:
            resp = await client.request("GET", "/health")
            json_resp: _JSONDict = await resp.json()
            assert resp.status == 200
            assert {"healthy": True}.items() <= json_resp.items()

    async def test__unhealth_request(
        self, mocker: MockerFixture, server: TestServer
    ) -> None:
        """Test /health endpoint determines if a pod is unhealthy.

        If the last time a task was executed is greate than
        MAX_TASK_EXECUTION_TIME, the endpoint should return that
        the pod is unhealthly.
        """
        mocker.patch("bitfount.federated.pod_vitals.MAX_TASK_EXECUTION_TIME", 0)
        async with TestClient(server) as client:
            resp = await client.request("GET", "/health")
            json_resp: _JSONDict = await resp.json()
            assert resp.status == 200
            assert {"healthy": False}.items() <= json_resp.items()

    async def test_compatibility_check(
        self,
        datastructure: DataStructure,
        datastructure_config_json: _JSONDict,
        mocker: MockerFixture,
        pod_schemas: Dict[str, Mock],
        server: TestServer,
    ) -> None:
        """Test compatibility check endpoint works."""
        # Patch out actual compat check
        mock_compat_checker = mocker.patch(
            "bitfount.federated.pod_vitals.check_datastructure_schema_compatibility",
            autospec=True,
            return_value=(DataStructureSchemaCompatibility.COMPATIBLE, []),
        )

        async with TestClient(server) as client:
            resp = await client.request(
                "POST",
                "/compatibility-check",
                json={
                    "datasetName": "dataset1",
                    "taskDataStructure": datastructure_config_json,
                },
            )

            assert resp.status == 200
            assert await resp.json() == {"compatibility": "COMPATIBLE", "msgs": []}
            mock_compat_checker.assert_called_once_with(
                datastructure, pod_schemas["dataset1"]
            )

    async def test_compatibility_check_fails_dataset_not_in_pod_schemas(
        self,
        datastructure_config_json: _JSONDict,
        server: TestServer,
    ) -> None:
        """Test compatibility check endpoint 404 if dataset not known."""
        async with TestClient(server) as client:
            resp = await client.request(
                "POST",
                "/compatibility-check",
                json={
                    "datasetName": "does_not_exist",
                    "taskDataStructure": datastructure_config_json,
                },
            )

            assert resp.status == 404
            assert await resp.json() == {
                "error": (
                    'dataset "does_not_exist" could not be found'
                    " in this pod's schemas."
                )
            }

    async def test_compatibility_check_handles_other_exceptions(
        self,
        datastructure_config_json: _JSONDict,
        mocker: MockerFixture,
        server: TestServer,
    ) -> None:
        """Test compatibility check endpoint 500 if other error occurs."""
        # Patch out actual compat check
        mocker.patch(
            "bitfount.federated.pod_vitals.check_datastructure_schema_compatibility",
            autospec=True,
            side_effect=Exception("COMPAT ERROR"),
        )

        async with TestClient(server) as client:
            resp = await client.request(
                "POST",
                "/compatibility-check",
                json={
                    "datasetName": "dataset1",
                    "taskDataStructure": datastructure_config_json,
                },
            )

            assert resp.status == 500
            assert await resp.json() == {"error": "COMPAT ERROR"}

    async def test_dataset_names(
        self,
        server: TestServer,
    ) -> None:
        """Test dataset_names endpoint returns the pod's datasets."""
        async with TestClient(server) as client:
            resp = await client.request(
                "GET",
                "/dataset-names",
            )

            assert resp.status == 200
            assert await resp.json() == ["dataset1", "dataset2"]

    async def test_get_schemas_all_schemas(
        self,
        pod_schemas: Dict[str, Mock],
        server: TestServer,
    ) -> None:
        """Test schemas endpoint returns all schemas if no args."""
        async with TestClient(server) as client:
            resp = await client.request(
                "GET",
                "/schemas",
            )

            assert resp.status == 200
            assert await resp.json() == [f"to_json_of_{d}" for d in pod_schemas]

    async def test_get_schemas_one_schema(
        self,
        server: TestServer,
    ) -> None:
        """Test schemas endpoint returns specific schema if arg."""
        async with TestClient(server) as client:
            resp = await client.request(
                "GET", "/schemas", params={"datasetName": "dataset1"}
            )

            assert resp.status == 200
            assert await resp.json() == ["to_json_of_dataset1"]

    async def test_get_schemas_fails_if_no_dataset(
        self,
        server: TestServer,
    ) -> None:
        """Test schemas endpoint 404 if cannot find requested schema."""
        async with TestClient(server) as client:
            resp = await client.request(
                "GET", "/schemas", params={"datasetName": "does_not_exist"}
            )

            assert resp.status == 404
            assert await resp.json() == {
                "error": (
                    'dataset "does_not_exist" could not be found in the set of schemas'
                )
            }

    async def test__open_socket(
        self, handler: _PodVitalsHandler, mocker: MockerFixture
    ) -> None:
        """Test the socket library is used to get an open port."""
        expected_port = 8080
        mock_socket = mocker.patch("socket.socket")
        mock_socket.return_value.recv.return_value = 1
        mock_socket.return_value.getsockname.return_value = ("host", expected_port)
        port = handler._open_socket()
        assert port == expected_port
        mock_socket.return_value.getsockname.assert_called_once()

    async def test__pod_vitals_port_env_var_set(
        self,
        handler: _PodVitalsHandler,
        mock_open_socket: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test pod health port is set to BITFOUNT_POD_VITALS_PORT env var."""
        pod_vitals_port = 8080
        monkeypatch.setenv("BITFOUNT_POD_VITALS_PORT", str(pod_vitals_port))
        result = handler._get_pod_vitals_port()
        assert result == pod_vitals_port
        assert not mock_open_socket.called

    async def test__pod_vitals_port_no_env_var(
        self, handler: _PodVitalsHandler, mock_open_socket: Mock
    ) -> None:
        """Test pod health port when BITFOUNT_POD_VITALS_PORT not set.

        If BITFOUNT_POD_VITALS_PORT is not set as an environment variable
        the port number should be determined by _open_socket method.
        """
        port = 8080
        result = handler._get_pod_vitals_port()
        assert result == port
        mock_open_socket.assert_called_once()

    async def test__pod_vitals_error_invalid_port(
        self,
        handler: _PodVitalsHandler,
        mock_open_socket: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test exception raised when BITFOUNT_POD_VITALS_PORT is invalid."""
        pod_vitals_port = "abc123"
        expected_error_msg = (
            "BITFOUNT_POD_VITALS_PORT must be an integer. "
            f"BITFOUNT_POD_VITALS_PORT set to '{pod_vitals_port}'"
        )
        monkeypatch.setenv("BITFOUNT_POD_VITALS_PORT", str(pod_vitals_port))
        with pytest.raises(ValueError) as error:
            handler._get_pod_vitals_port()
            assert str(error.value) == expected_error_msg

        assert not mock_open_socket.called

    async def test__pod_vitals_error_invalid_port_range(
        self,
        handler: _PodVitalsHandler,
        mock_open_socket: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test exception raised when BITFOUNT_POD_VITALS_PORT is invalid."""
        pod_vitals_port = "99999"
        monkeypatch.setenv("BITFOUNT_POD_VITALS_PORT", str(pod_vitals_port))
        with pytest.raises(ValueError) as error:
            handler._get_pod_vitals_port()
            assert (
                str(error.value)
                == "Invalid BITFOUNT_POD_VITALS_PORT given. Must be in range [1-65535]"
            )
        assert not mock_open_socket.called

    async def test__start_webserver(
        self,
        handler: _PodVitalsHandler,
        mocker: MockerFixture,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Ensure server is started with expected settings."""
        port = 8080
        monkeypatch.setenv("BITFOUNT_POD_VITALS_PORT", str(port))
        mock_tcp_site = mocker.patch("bitfount.federated.pod_vitals.TCPSite")
        mock_loop = AsyncMock()

        handler.start(mock_loop)

        mock_tcp_site.assert_called_once_with(handler.runner, "0.0.0.0", port)
        mock_tcp_site.return_value.start.assert_called_once()
