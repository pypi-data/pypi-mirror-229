"""Tests for the model evaluation algorithm."""
from typing import TYPE_CHECKING
from unittest.mock import Mock, create_autospec

import numpy as np
import pandas as pd
import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture

from bitfount import BitfountSchema
from bitfount.backends.pytorch.models.models import PyTorchTabularClassifier
from bitfount.data.datasources.base_source import BaseSource
from bitfount.federated.algorithms.base import (
    BaseModellerAlgorithm,
    BaseWorkerAlgorithm,
    _BaseAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithm,
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.utils import _ALGORITHMS
from bitfount.hub import BitfountHub
from bitfount.schemas.utils import bf_dump, bf_load
from tests.bitfount.backends.pytorch.models.test_models import assert_vars_equal
from tests.utils.helper import (
    backend_test,
    create_datasource,
    create_datastructure,
    integration_test,
    unit_test,
)


class TestModelInference:
    """Test Evaluate algorithm."""

    @unit_test
    def test_modeller_types(self, model: Mock) -> None:
        """Test modeller method."""
        algorithm_factory = ModelInference(model=model)
        algorithm = algorithm_factory.modeller()
        for type_ in [
            _BaseAlgorithm,
            BaseModellerAlgorithm,
            _BaseModelAlgorithm,
            _BaseModellerModelAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    @unit_test
    def test_worker_types(self, model: Mock) -> None:
        """Test worker method."""
        algorithm_factory = ModelInference(model=model)
        algorithm = algorithm_factory.worker(
            hub=create_autospec(BitfountHub, instance=True)
        )
        for type_ in [
            _BaseAlgorithm,
            BaseWorkerAlgorithm,
            _BaseModelAlgorithm,
            _BaseWorkerModelAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    @unit_test
    def test_attribute_error_raised_run(self) -> None:
        """Test non abstract class without run method raises AttributeError."""
        err_msg = "does not have a `run` method"
        for type_ in [
            BaseWorkerAlgorithm,
            _BaseWorkerModelAlgorithm,
        ]:
            with pytest.raises(AttributeError) as e_info:

                class NoRunMethod(type_):  # type: ignore[valid-type, misc] # reason: test child methods need run method # noqa: B950
                    def initialise(self) -> None:
                        pass

            assert err_msg in str(e_info)

    @unit_test
    def test_worker_run(self, model: Mock, mocker: MockerFixture) -> None:
        """Tests that worker run does metric calculation."""
        worker = _WorkerSide(model=model)
        mocker.patch.object(worker, "update_params")
        worker.datasource = Mock(spec=BaseSource)
        worker.run(model_params=Mock())
        if not isinstance(model, BitfountModelReference):
            model.predict.assert_called_once()

    @unit_test
    def test_worker_run_w_class_outputs(
        self, caplog: LogCaptureFixture, mocker: MockerFixture, model: Mock
    ) -> None:
        """Tests that worker run does metric calculation."""
        mock_hub = create_autospec(BitfountHub, instance=True)
        algo = ModelInference(
            model=model,
            class_outputs=[
                "test0",
            ],
        )
        mocker.patch.object(ModelInference, "_get_model_from_reference")
        worker = algo.worker(hub=mock_hub)
        mock_datasource = Mock(spec=BaseSource)
        worker.initialise(mock_datasource)
        worker.run(model_params=Mock())
        assert worker.class_outputs == ["test0"]
        assert (
            "Class outputs provided do not match the model prediction output. "
            in caplog.text
        )

    @integration_test
    def test_worker_side_returns_list_of_arrays(
        self, caplog: LogCaptureFixture, mocker: MockerFixture
    ) -> None:
        """Tests worker side returns list of arrays."""
        datastructure = create_datastructure()
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), steps=10
        )
        datasource = create_datasource(classification=True)
        model.fit(datasource)
        mock_hub = create_autospec(BitfountHub, instance=True)
        algo = ModelInference(model=model, class_outputs=["test0"])
        worker = algo.worker(hub=mock_hub)
        mocker.patch.object(worker, "update_params")
        worker.initialise(datasource)
        preds = worker.run(model_params=Mock())
        assert (
            "Class outputs provided do not match the model prediction output."
            in caplog.text
        )
        assert isinstance(preds, list)

    @integration_test
    def test_worker_side_returns_dataframe(
        self, caplog: LogCaptureFixture, mocker: MockerFixture
    ) -> None:
        """Tests worker side returns dataframe."""
        datastructure = create_datastructure()
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), steps=10
        )
        datasource = create_datasource(classification=True)
        model.fit(datasource)
        mock_hub = create_autospec(BitfountHub, instance=True)
        algo = ModelInference(model=model, class_outputs=["test0", "test1"])
        worker = algo.worker(hub=mock_hub)
        mocker.patch.object(worker, "update_params")
        worker.initialise(datasource)
        preds = worker.run(model_params=Mock())
        assert isinstance(preds, pd.DataFrame)
        assert set(preds.columns) == set(["test0", "test1"])

    @integration_test
    def test_worker_side_returns_dict(
        self, caplog: LogCaptureFixture, mocker: MockerFixture
    ) -> None:
        """Tests worker side returns dataframe."""
        datastructure = create_datastructure()
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), steps=10
        )
        datasource = create_datasource(classification=True)
        model.fit(datasource)
        img_arr = [
            np.random.rand(2, 49, 496, 512),
            np.random.rand(2, 49, 496, 512),
            np.random.rand(2, 49, 512),
            np.random.rand(2, 1, 768, 768),
        ]
        mocker.patch.object(model, "predict", return_value=img_arr)
        mock_hub = create_autospec(BitfountHub, instance=True)
        algo = ModelInference(
            model=model, class_outputs=["test0", "test1", "test2", "test3"]
        )
        worker = algo.worker(hub=mock_hub)
        mocker.patch.object(worker, "update_params")
        worker.initialise(datasource)
        preds = worker.run(model_params=Mock())
        assert isinstance(preds, dict)
        assert set(preds.keys()) == set(["test0", "test1", "test2", "test3"])

    @unit_test
    def test_modeller_run(self, model: Mock) -> None:
        """Tests that modeller run returns results."""
        modeller = _ModellerSide(model=model)
        predictions = {"pod1": [np.array([0.1, 0.2, 0.3])]}
        assert predictions == modeller.run(predictions)

    @unit_test
    def test_modeller_run_w_df_predictions(self, model: Mock) -> None:
        """Tests that modeller run returns results."""
        modeller = _ModellerSide(model=model)
        predictions = {
            "pod1": pd.DataFrame(
                [np.array([0.1, 0.2, 0.3])], columns=["test0", "test1", "test2"]
            )
        }
        assert predictions == modeller.run(predictions)


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for column average algorithm."""

    def test_serialization(self) -> None:
        """Test dump and load for ModelInference."""
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            epochs=2,
        )
        algorithm_factory = ModelInference(model=model)
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)

        assert algorithm_factory.class_name == loaded.class_name
        assert_vars_equal(vars(algorithm_factory.model), vars(loaded.model))


# Static tests for algorithm-protocol compatibility
if TYPE_CHECKING:
    from typing import cast

    from bitfount.federated.protocols.results_only import (
        _ResultsOnlyCompatibleModelAlgoFactory,
        _ResultsOnlyCompatibleModellerAlgorithm,
        _ResultsOnlyModelCompatibleWorkerAlgorithm,
    )
    from bitfount.types import (
        DistributedModelProtocol,
        _DistributedModelTypeOrReference,
    )

    # Check compatible with ResultsOnly
    _algo_factory: _ResultsOnlyCompatibleModelAlgoFactory = ModelInference(
        model=cast(_DistributedModelTypeOrReference, object())
    )
    _modeller_side: _ResultsOnlyCompatibleModellerAlgorithm = _ModellerSide(
        model=cast(DistributedModelProtocol, object())
    )
    _worker_side: _ResultsOnlyModelCompatibleWorkerAlgorithm = _WorkerSide(
        model=cast(DistributedModelProtocol, object())
    )
