"""Tests base protocols module."""
from abc import ABC
import importlib
import inspect
import pkgutil
from typing import Any, Optional, Type
from unittest.mock import AsyncMock, Mock, create_autospec

import pytest
from pytest import LogCaptureFixture, fixture
from pytest_mock import MockerFixture

from bitfount.federated.aggregators.aggregator import Aggregator
import bitfount.federated.algorithms.model_algorithms
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithmFactory,
)
from bitfount.federated.helper import TaskContext
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.protocols.base import (
    BaseModellerProtocol,
    BaseWorkerProtocol,
    _BaseProtocol,
)
from bitfount.federated.protocols.model_protocols.federated_averaging import (
    FederatedAveraging,
)
from bitfount.federated.protocols.results_only import ResultsOnly
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.hooks import _HOOK_DECORATED_ATTRIBUTE
from tests.utils.helper import unit_test


@unit_test
class TestBase:
    """Test protocol base module."""

    @fixture
    def mock_aggregator(self) -> Mock:
        """Returns mock aggregator."""
        mock_aggregator: Mock = create_autospec(Aggregator, instance=True)
        return mock_aggregator

    @fixture
    def dummy_modeller_protocol_cls(self) -> Type[BaseModellerProtocol]:
        """Returns dummy modeller protocol class."""

        class DummyModellerProtocol(BaseModellerProtocol):
            async def run(self, **kwargs: Any) -> Any:
                ...

        return DummyModellerProtocol

    @fixture
    def dummy_worker_protocol_cls(self) -> Type[BaseWorkerProtocol]:
        """Returns dummy worker protocol class."""

        class DummyWorkerProtocol(BaseWorkerProtocol):
            async def run(
                self, pod_vitals: Optional[_PodVitals] = None, **kwargs: Any
            ) -> Any:
                ...

        return DummyWorkerProtocol

    def test_base_protocol_methods_are_not_decorated(self) -> None:
        """Tests that base protocol methods are not decorated.

        They should not be decorated because the base protocol is abstract. We can only
        test this with the constructor because the base protocol has no `run` method.
        """
        base = _BaseProtocol(algorithm=Mock(), mailbox=Mock())
        with pytest.raises(AttributeError):
            getattr(base.__init__, _HOOK_DECORATED_ATTRIBUTE)  # type: ignore[misc] # Reason: This is a test. # noqa: B950

    async def test_modeller_protocol_pods_ready(
        self,
        caplog: LogCaptureFixture,
        dummy_modeller_protocol_cls: Type[BaseModellerProtocol],
        mocker: MockerFixture,
    ) -> None:
        """Tests that the modeller protocol starts when workers are ready."""
        caplog.set_level("INFO")
        mailbox = AsyncMock(spec=_ModellerMailbox, pods_ready=True)

        # Mock out asyncio.sleep()
        mock_asyncio_sleep = mocker.patch("asyncio.sleep")

        # The first check of the mailbox `pods_ready` attribute should be True,
        # therefore we expect no logs regarding waiting for pods to be ready and
        # no calls to asyncio.sleep()
        protocol = dummy_modeller_protocol_cls(algorithm=Mock(), mailbox=mailbox)
        await protocol.run(context=TaskContext.MODELLER)
        mailbox.send_task_start_message.assert_awaited_once()
        mock_asyncio_sleep.assert_not_called()
        assert caplog.messages[0] == "Running batch 1 of 1..."
        assert caplog.messages[1] == "Pod(s) are ready. Starting task..."

    async def test_modeller_protocol_doesnt_start_until_workers_ready(
        self,
        caplog: LogCaptureFixture,
        dummy_modeller_protocol_cls: Type[BaseModellerProtocol],
        mocker: MockerFixture,
    ) -> None:
        """Tests that the modeller protocol doesn't start until workers are ready."""
        caplog.set_level("INFO")
        mailbox = AsyncMock(spec=_ModellerMailbox, pods_ready=False)

        # Mock out asyncio.sleep()
        async def mark_pods_ready(*args: Any, **kwargs: Any) -> None:
            mailbox.pods_ready = True

        mock_asyncio_sleep = mocker.patch("asyncio.sleep")
        mock_asyncio_sleep.side_effect = mark_pods_ready

        # The first check of the mailbox `pods_ready` attribute should be False, and the
        # second check should be True. Therefore, we expect only one logging call.
        protocol = dummy_modeller_protocol_cls(algorithm=Mock(), mailbox=mailbox)
        await protocol.run(context=TaskContext.MODELLER)
        mailbox.send_task_start_message.assert_awaited_once()
        mock_asyncio_sleep.assert_awaited_once()
        # Check that the logging message is correct
        assert caplog.messages[0] == "Running batch 1 of 1..."
        assert caplog.messages[1] == "Waiting for pod(s) to be ready..."
        assert caplog.messages[2] == "Pod(s) are ready. Starting task..."

    async def test_worker_protocol_modeller_ready(
        self,
        caplog: LogCaptureFixture,
        dummy_worker_protocol_cls: Type[BaseWorkerProtocol],
        mocker: MockerFixture,
    ) -> None:
        """Tests that the worker protocol starts when the modeller is ready."""
        caplog.set_level("INFO")
        mailbox = AsyncMock(spec=_WorkerMailbox, modeller_ready=True)

        # Mock out asyncio.sleep()
        mock_asyncio_sleep = mocker.patch("asyncio.sleep")

        # The first check of the mailbox `modeller_ready` attribute should be True,
        # therefore we expect no logs regarding waiting for the modeller and
        # no calls to asyncio.sleep()
        protocol = dummy_worker_protocol_cls(algorithm=Mock(), mailbox=mailbox)
        await protocol.run(context=TaskContext.WORKER)
        mailbox.send_task_start_message.assert_awaited_once()
        mock_asyncio_sleep.assert_not_called()
        assert caplog.messages[0] == "Running batch 1 of 1..."
        assert caplog.messages[1] == "Modeller is ready. Starting task..."

    async def test_worker_protocol_doesnt_start_until_modeller_ready(
        self,
        caplog: LogCaptureFixture,
        dummy_worker_protocol_cls: Type[BaseWorkerProtocol],
        mocker: MockerFixture,
    ) -> None:
        """Tests that the worker protocol doesn't start until modeller is ready."""
        caplog.set_level("INFO")
        mailbox = AsyncMock(spec=_WorkerMailbox, modeller_ready=False)

        # Mock out asyncio.sleep()
        async def mark_modeller_ready(*args: Any, **kwargs: Any) -> None:
            mailbox.modeller_ready = True

        mock_asyncio_sleep = mocker.patch("asyncio.sleep")
        mock_asyncio_sleep.side_effect = mark_modeller_ready

        # The first check of the mailbox `modeller_ready` attribute should be False, and
        # the second check should be True. Therefore, we expect only one logging call.
        protocol = dummy_worker_protocol_cls(algorithm=Mock(), mailbox=mailbox)
        await protocol.run(context=TaskContext.WORKER)
        mailbox.send_task_start_message.assert_awaited_once()
        mock_asyncio_sleep.assert_awaited_once()
        # Check that the logging message is correct
        assert caplog.messages[0] == "Running batch 1 of 1..."
        assert caplog.messages[1] == "Waiting for modeller to be ready..."
        assert caplog.messages[2] == "Modeller is ready. Starting task..."

    def test_protocol_initialises_pretrained_file_on_modeller_side(
        self, mock_aggregator: Mock, mock_modeller_mailbox: Mock
    ) -> None:
        """Test all protocols initialise pretrained file on modeller side."""
        pretrained_file_path = "mock/path"

        model_alg_modules = pkgutil.walk_packages(
            path=bitfount.federated.algorithms.model_algorithms.__path__,
            prefix=bitfount.federated.algorithms.model_algorithms.__name__ + ".",
        )

        for module_info in model_alg_modules:
            for _, cls in inspect.getmembers(
                importlib.import_module(module_info.name), inspect.isclass
            ):
                if (
                    issubclass(cls, _BaseModelAlgorithmFactory)
                    and ABC not in cls.__bases__
                ):
                    federated_algorithm = cls(
                        model=Mock(), pretrained_file=pretrained_file_path
                    )

                    for protocol_cls in [ResultsOnly, FederatedAveraging]:
                        protocol_factory = protocol_cls(
                            algorithm=federated_algorithm,
                            aggregator=mock_aggregator,
                            steps_between_parameter_updates=2,
                        )
                        protocol = protocol_factory.modeller(
                            mailbox=mock_modeller_mailbox
                        )

                        assert hasattr(protocol.algorithm, "pretrained_file")
                        assert (
                            protocol.algorithm.pretrained_file == pretrained_file_path
                        )
