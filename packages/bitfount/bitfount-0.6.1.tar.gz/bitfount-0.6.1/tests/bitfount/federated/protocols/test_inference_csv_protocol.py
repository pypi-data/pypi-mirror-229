"""Tests for the InferenceAndCSVReport Protocol."""
from typing import Callable, List
from unittest.mock import Mock, create_autospec

import pytest
from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.data.datasources.base_source import BaseSource
from bitfount.federated.algorithms.csv_report_algorithm import (
    CSVReportAlgorithm,
    _ModellerSide as _CSVModellerSide,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _ModellerSide as _InferenceModellerSide,
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.protocols.base import (
    BaseModellerProtocol,
    BaseWorkerProtocol,
    _BaseProtocol,
)
from bitfount.federated.protocols.model_protocols import inference_csv_report
from bitfount.federated.protocols.model_protocols.inference_csv_report import (
    InferenceAndCSVReport,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.hub import BitfountHub, BitfountSession
from tests.utils.helper import unit_test


@unit_test
class TestInferenceAndCSVReportProtocol:
    """Tests for the InferenceAndCSVReport Protocol."""

    @fixture
    def mock_datasource(self) -> Mock:
        """Mock BaseSource."""
        mock_datasource: Mock = create_autospec(BaseSource, instance=True)
        return mock_datasource

    @fixture
    def mock_hub(self) -> Mock:
        """Returns mock BitfountHub."""
        mock_hub: Mock = create_autospec(BitfountHub, instance=True)
        mock_hub.session = create_autospec(BitfountSession, instance=True)
        return mock_hub

    @fixture()
    def remote_algorithms(
        self,
    ) -> List[Mock]:
        """Returns list of remote algorithms."""
        model_inference_algo = create_autospec(ModelInference)
        model_inference_algo.model = Mock()
        model_inference_algo.class_name = "bitfount.ModelInference"
        csv_algo = create_autospec(CSVReportAlgorithm)
        csv_algo.class_name = "bitfount.CSVReportAlgorithm"
        return [
            model_inference_algo,
            csv_algo,
        ]

    @fixture()
    def remote_modeller_algorithms(
        self,
    ) -> List[Mock]:
        """Returns list of remote algorithms."""
        model_inference_algo = create_autospec(_InferenceModellerSide)
        model_inference_algo.model = Mock()
        csv_algo = create_autospec(_CSVModellerSide)
        return [
            model_inference_algo,
            csv_algo,
        ]

    @fixture()
    def remote_worker_algorithms(
        self,
    ) -> List[Mock]:
        """Returns list of remote algorithms."""
        model_inference_algo = create_autospec(_InferenceWorkerSide)
        model_inference_algo.model = Mock()
        csv_algo = create_autospec(_CSVWorkerSide)
        return [
            model_inference_algo,
            csv_algo,
        ]

    @fixture
    def mock_worker_mailbox(self) -> Mock:
        """Returns mock mailbox."""
        mock_worker_mailbox: Mock = create_autospec(_WorkerMailbox, instance=True)
        mock_worker_mailbox._task_id = "test"
        return mock_worker_mailbox

    @fixture
    def mock_modeller_mailbox(self) -> Mock:
        """Returns mock mailbox."""
        mock_mailbox: Mock = create_autospec(_ModellerMailbox, instance=True)
        mock_mailbox._task_id = "task_id"
        return mock_mailbox

    @fixture
    def modeller_side_factory(
        self, mock_modeller_mailbox: Mock
    ) -> Callable[[Mock], _ModellerSide,]:
        """Factory to create ModellerSide instances from mock algorithms."""

        def _create(algo: List[Mock]) -> _ModellerSide:
            return _ModellerSide(algorithm=algo, mailbox=mock_modeller_mailbox)

        return _create

    @fixture
    def worker_side_factory(
        self, mock_worker_mailbox: Mock
    ) -> Callable[[Mock], _WorkerSide]:
        """Factory to create WorkerSide instances from mock algorithms."""

        def _create(algo: List[Mock]) -> _WorkerSide:
            return _WorkerSide(algorithm=algo, mailbox=mock_worker_mailbox)

        return _create

    def test_validate_algo_init_error(self, remote_algorithms: List[Mock]) -> None:
        """Tests error raised with incompatible algorithm."""
        remote_algorithms[1].class_name = "test"
        with pytest.raises(TypeError):
            InferenceAndCSVReport(algorithm=remote_algorithms)

    def test_modeller(
        self, mock_modeller_mailbox: Mock, remote_algorithms: List[Mock]
    ) -> None:
        """Test modeller method."""
        protocol_factory = InferenceAndCSVReport(algorithm=remote_algorithms)
        protocol = protocol_factory.modeller(mailbox=mock_modeller_mailbox)
        for type_ in [
            _BaseProtocol,
            BaseModellerProtocol,
            inference_csv_report._ModellerSide,
        ]:
            assert isinstance(protocol, type_)

    def test_worker(
        self, mock_hub: Mock, mock_worker_mailbox: Mock, remote_algorithms: List[Mock]
    ) -> None:
        """Test worker method."""
        protocol_factory = InferenceAndCSVReport(algorithm=remote_algorithms)
        protocol = protocol_factory.worker(mailbox=mock_worker_mailbox, hub=mock_hub)
        for type_ in [
            _BaseProtocol,
            BaseWorkerProtocol,
            inference_csv_report._WorkerSide,
        ]:
            assert isinstance(protocol, type_)

    @pytest.mark.asyncio
    async def test_modeller_run(
        self,
        mocker: MockerFixture,
        mock_modeller_mailbox: Mock,
        modeller_side_factory: Callable[[List[Mock]], _ModellerSide],
        remote_modeller_algorithms: List[Mock],
    ) -> None:
        """Tests ModellerSide.run() with an algorithm not needing data."""
        modeller_side: _ModellerSide = modeller_side_factory(remote_modeller_algorithms)
        mock_send_parameters = mocker.patch.object(modeller_side, "_send_parameters")

        await modeller_side.run()
        mock_modeller_mailbox.get_evaluation_results_from_workers.assert_awaited()
        mock_send_parameters.assert_awaited()

    @pytest.mark.asyncio
    async def test_modeller_send_parameters(
        self,
        mocker: MockerFixture,
        mock_modeller_mailbox: Mock,
        modeller_side_factory: Callable[[List[Mock]], _ModellerSide],
        remote_modeller_algorithms: List[Mock],
    ) -> None:
        """Tests ModellerSide.run() with an algorithm not needing data."""
        modeller_side: _ModellerSide = modeller_side_factory(remote_modeller_algorithms)
        new_parameters = Mock()
        mock_send_model_parameters = mocker.patch(
            "bitfount.federated.protocols.model_protocols.inference_csv_report._send_model_parameters"
        )
        await modeller_side._send_parameters(new_parameters)
        mock_send_model_parameters.assert_awaited()

    @pytest.mark.asyncio
    async def test_worker_run(
        self,
        mock_datasource: Mock,
        mock_worker_mailbox: Mock,
        worker_side_factory: Callable[[List[Mock]], _WorkerSide],
        remote_worker_algorithms: List[Mock],
    ) -> None:
        """Tests WorkerSide.run()."""
        worker_side: _WorkerSide = worker_side_factory(remote_worker_algorithms)

        await worker_side.run(datasource=mock_datasource)
        mock_worker_mailbox.send_evaluation_results.assert_awaited()

    @pytest.mark.asyncio
    async def test_worker_receive_parameters(
        self,
        mock_datasource: Mock,
        mock_worker_mailbox: Mock,
        mocker: MockerFixture,
        remote_worker_algorithms: List[Mock],
        worker_side_factory: Callable[[List[Mock]], _WorkerSide],
    ) -> None:
        """Test _receive_parameters awaits _get_model_parameters."""
        mock_get_model_parameters = mocker.patch(
            "bitfount.federated.protocols.model_protocols.inference_csv_report._get_model_parameters"
        )
        worker_side: _WorkerSide = worker_side_factory(remote_worker_algorithms)

        await worker_side._receive_parameters()

        mock_get_model_parameters.assert_awaited()
