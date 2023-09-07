"""Tests for the TransformerTextGeneration algorithm."""
import re
from typing import TYPE_CHECKING

from huggingface_hub import _CACHED_NO_EXIST, try_to_load_from_cache
import pytest
from pytest import LogCaptureFixture, fixture

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.federated.algorithms.base import (
    BaseModellerAlgorithm,
    BaseWorkerAlgorithm,
    _BaseAlgorithm,
)
from bitfount.federated.algorithms.transformer_text_generation import (
    TransformerTextGeneration,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.exceptions import AlgorithmError
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.utils import _ALGORITHMS
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import create_datasource_prompts, unit_test


@unit_test
class TestTransformerTextGeneration:
    """Test TransformerTextGeneration algorithm."""

    @fixture
    def datasource(self) -> BaseSource:
        """Fixture for datasource."""
        return create_datasource_prompts()

    def test_modeller_types(self) -> None:
        """Test modeller method."""
        algorithm_factory = TransformerTextGeneration(
            model_id="model-id", text_column_name="column-name"
        )
        algorithm = algorithm_factory.modeller()
        for type_ in [
            _BaseAlgorithm,
            BaseModellerAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    def test_worker_types(self) -> None:
        """Test worker method."""
        algorithm_factory = TransformerTextGeneration(
            model_id="model-id", text_column_name="column-name"
        )
        algorithm = algorithm_factory.worker()
        for type_ in [
            _BaseAlgorithm,
            BaseWorkerAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    def test_modeller_init(self) -> None:
        """Test worker method."""
        algorithm_factory = TransformerTextGeneration(
            model_id="hf-internal-testing/tiny-random-gpt2",
            text_column_name="column-name",
        )
        algorithm_factory.modeller().initialise()

    def test_modeller_run(self) -> None:
        """Tests that modeller run returns results."""
        modeller = _ModellerSide()
        results = {"pod-id": {"generated_text": "Example of generated text"}}
        assert results == modeller.run(results=results)

    def test_modeller_run_log_functionality(self, caplog: LogCaptureFixture) -> None:
        """Tests that the modeller run optionally logs results."""
        caplog.set_level("INFO")
        modeller = _ModellerSide()
        results = {"pod-id": [{"generated_text": "Example of generated text"}]}
        modeller.run(results=results, log=True)
        assert re.search("pod-id: Example of generated text", caplog.text)

    def test_worker_init(self, datasource: DataFrameSource) -> None:
        """Test worker method."""
        model_id = "hf-internal-testing/tiny-random-gpt2"
        model_config = "config.json"

        algorithm_factory = TransformerTextGeneration(
            model_id=model_id,
            text_column_name="column-name",
        )
        algorithm_factory.worker().initialise(datasource=datasource)
        is_cached = try_to_load_from_cache(model_id, filename=model_config)

        # file exists and is cached
        assert isinstance(is_cached, str)
        # non-existence of file is cached
        assert is_cached is not _CACHED_NO_EXIST

    def test_worker_init_fails_when_model_id_does_not_exist(
        self, datasource: DataFrameSource
    ) -> None:
        """Test worker method fails.

        When model id does not exist on HuggingFace Hub.
        """
        algorithm_factory = TransformerTextGeneration(
            model_id="dummy/dummy", text_column_name="column-name"
        )

        with pytest.raises(AlgorithmError, match="not a valid model identifier listed"):
            algorithm_factory.worker().initialise(datasource=datasource)

    def test_worker_init_fails_when_model_id_is_not_causal_lm(
        self, datasource: DataFrameSource
    ) -> None:
        """Test worker method fails.

        When model id does not match a model for causal LLM.
        """
        model_id = "hf-internal-testing/prior-dummy."
        algorithm_factory = TransformerTextGeneration(
            model_id=model_id,
            text_column_name="column-name",
        )

        with pytest.raises(AlgorithmError, match=model_id):
            algorithm_factory.worker().initialise(datasource=datasource)

    def test_worker_init_ignores_dp_setting(
        self, datasource: DataFrameSource, caplog: LogCaptureFixture
    ) -> None:
        """Test worker init ignores setting of pod_dp."""
        algorithm_factory = TransformerTextGeneration(
            model_id="hf-internal-testing/tiny-random-gpt2",
            text_column_name="column-name",
        )
        algorithm_factory.worker().initialise(
            datasource=datasource,
            pod_dp=DPPodConfig(epsilon=1, delta=0.0001),
        )

        log_record = caplog.records[0]
        assert log_record.levelname == "WARNING"
        assert (
            log_record.message
            == "The use of DP is not supported, ignoring set `pod_dp`."
        )
        assert not hasattr(algorithm_factory.worker, "pod_dp")

    def test_worker_run(self, datasource: DataFrameSource) -> None:
        """Tests worker run method with a single table datasource."""
        algorithm_factory = TransformerTextGeneration(
            model_id="hf-internal-testing/tiny-random-gpt2",
            text_column_name="TARGET",
        )

        worker = algorithm_factory.worker()
        worker.initialise(datasource=datasource)
        result = worker.run()
        assert isinstance(result, list)
        assert len(result) == 2

    def test_worker_run_with_prompt(self, datasource: DataFrameSource) -> None:
        """Tests worker run method with a prompt."""
        algorithm_factory = TransformerTextGeneration(
            model_id="hf-internal-testing/tiny-random-gpt2"
        )

        worker = algorithm_factory.worker()
        worker.initialise(datasource=datasource)
        result = worker.run(prompt="This is a prompt")
        assert isinstance(result, list)
        assert len(result) == 1

    def test_worker_run_with_prompt_and_text_column(
        self, datasource: DataFrameSource
    ) -> None:
        """Tests worker run method with a prompt."""
        algorithm_factory = TransformerTextGeneration(
            model_id="hf-internal-testing/tiny-random-gpt2",
            text_column_name="TARGET",
        )

        worker = algorithm_factory.worker()
        worker.initialise(datasource=datasource)
        with pytest.raises(
            AlgorithmError,
            match=re.escape(
                "Cannot provide both `prompt` and `text_column_name` to `run`."
            ),
        ):
            worker.run(prompt="This is a prompt")

    def test_worker_run_without_prompt_or_text_column(
        self, datasource: DataFrameSource
    ) -> None:
        """Tests worker run method without a text column or a prompt."""
        algorithm_factory = TransformerTextGeneration(
            model_id="hf-internal-testing/tiny-random-gpt2",
        )

        worker = algorithm_factory.worker()
        worker.initialise(datasource=datasource)
        with pytest.raises(
            AlgorithmError,
            match=re.escape("Must provide either `prompt` or `text_column_name`."),
        ):
            worker.run()


@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for TransformerTextGeneration algorithm."""

    def test_serialization(self) -> None:
        """Test Marshmallow Serialization for TransformerTextGeneration algorithm."""
        algorithm_factory = TransformerTextGeneration(
            model_id="model-id", text_column_name="column-name"
        )
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)
        assert algorithm_factory.__dict__ == loaded.__dict__


# Static tests for algorithm-protocol compatibility
if TYPE_CHECKING:
    from typing import cast

    from bitfount.federated.protocols.results_only import (
        _ResultsOnlyCompatibleAlgoFactory_,
        _ResultsOnlyCompatibleModellerAlgorithm,
        _ResultsOnlyModelIncompatibleWorkerAlgorithm,
    )

    # Check compatible with ResultsOnly
    _algo_factory: _ResultsOnlyCompatibleAlgoFactory_ = TransformerTextGeneration(
        model_id=cast(str, object()),
        text_column_name=cast(str, object()),
        max_length=cast(int, object()),
        num_return_sequences=cast(int, object()),
        seed=cast(int, object()),
    )
    _modeller_side: _ResultsOnlyCompatibleModellerAlgorithm = _ModellerSide()
    _worker_side: _ResultsOnlyModelIncompatibleWorkerAlgorithm = _WorkerSide(
        model_id=cast(str, object()),
        text_column_name=cast(str, object()),
        max_length=cast(int, object()),
        num_return_sequences=cast(int, object()),
        seed=cast(int, object()),
    )
