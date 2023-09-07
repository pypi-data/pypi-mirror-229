"""Tests for differential privacy module."""
import copy
import logging

import desert
import marshmallow
import numpy as np
import pytest
from pytest import LogCaptureFixture, fixture

from bitfount.federated.exceptions import DPParameterError
from bitfount.federated.privacy.differential import (
    DPModellerConfig,
    DPPodConfig,
    _DifferentiallyPrivate,
)
from bitfount.types import _StrAnyDict
from tests.utils.helper import dp_test


@fixture
def config_dict() -> _StrAnyDict:
    """Configuration dictionary for Differential Privacy settings."""
    return {
        "max_grad_norm": 1.0,
        "noise_multiplier": 0.0,
        "alphas": [0.0, 1.1],
        "delta": 0.01,
        "loss_reduction": "sum",
        "epsilon": 10.0,
        "auto_fix": False,
    }


@dp_test
class TestDPModellerConfig:
    """Tests for differential privacy config dataclass."""

    def test_loss_reduction_validation(self) -> None:
        """Tests config rejects invalid loss_reduction values."""
        with pytest.raises(ValueError, match="loss_reduction must be one of"):
            # noinspection PyTypeChecker
            DPModellerConfig(epsilon=1.0, loss_reduction="test")  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950

    def test_schema_loads(self, config_dict: _StrAnyDict) -> None:
        """Tests config loading from data."""
        schema = desert.schema(DPModellerConfig)
        test_config = schema.load(config_dict)

        # Assertions for correct conversion
        assert test_config.noise_multiplier == config_dict["noise_multiplier"]
        assert test_config.max_grad_norm == config_dict["max_grad_norm"]
        assert test_config.alphas == config_dict["alphas"]
        assert test_config.delta == config_dict["delta"]
        assert test_config.loss_reduction == config_dict["loss_reduction"]
        assert test_config.epsilon == config_dict["epsilon"]
        assert test_config.auto_fix == config_dict["auto_fix"]

    def test_schema_validation_failures(self) -> None:
        """Tests that schema validation catches incorrect options."""
        schema = desert.schema(DPModellerConfig)
        with pytest.raises(marshmallow.exceptions.ValidationError):
            schema.load({"loss_reduction": "test"})

    def test_error_alpha_1(self) -> None:
        """Tests error is raised when one alpha is 1."""
        with pytest.raises(DPParameterError):
            DPModellerConfig(
                epsilon=1,
                delta=1e-6,
                alphas=list(np.linspace(1.0, 440.0, 440)),
            )


@dp_test
class TestDifferentiallyPrivate:
    """Tests related to the DifferentiallyPrivate class."""

    @fixture
    def dp_config(self) -> DPModellerConfig:
        """Creates a DPConfig instance."""
        return DPModellerConfig(epsilon=10.0, delta=1.0)

    @fixture
    def pod_dp_config(self) -> DPPodConfig:
        """Creates a DPPodConfig instance."""
        return DPPodConfig(epsilon=1.0, delta=0.5)

    def test__convert_to_dpconfig(self, config_dict: _StrAnyDict) -> None:
        """Tests the conversion from dict to DPConfig."""
        test_config = _DifferentiallyPrivate._convert_to_dpconfig(config_dict)

        # Assertions for correct conversion
        assert test_config is not None
        assert test_config.noise_multiplier == config_dict["noise_multiplier"]
        assert test_config.max_grad_norm == config_dict["max_grad_norm"]
        assert test_config.alphas == config_dict["alphas"]
        assert test_config.delta == config_dict["delta"]
        assert test_config.loss_reduction == config_dict["loss_reduction"]
        assert test_config.epsilon == config_dict["epsilon"]
        assert test_config.auto_fix == config_dict["auto_fix"]

    def test__convert_to_dpconfig_with_none(self) -> None:
        """Tests that None is returned if None supplied."""
        assert None is _DifferentiallyPrivate._convert_to_dpconfig(None)

    def test_config_settings_logged(
        self, caplog: LogCaptureFixture, dp_config: DPModellerConfig
    ) -> None:
        """Tests that config settings are logged out."""
        caplog.set_level(logging.INFO)
        _DifferentiallyPrivate(dp_config)
        assert str(dp_config) in caplog.text

    def test_no_config_supplied_is_logged(self, caplog: LogCaptureFixture) -> None:
        """Tests that lack of config settings is logged out."""
        caplog.set_level(logging.INFO)
        _DifferentiallyPrivate(None)
        assert "No differential privacy settings provided." in caplog.text

    def test_apply_pod_dp_no_modeller_config(self) -> None:
        """Tests apply_pod_dp causes no change if no modeller config."""
        dp = _DifferentiallyPrivate()
        dp.apply_pod_dp(None)
        assert dp._dp_config is None

    def test_apply_pod_dp_no_pod_config(
        self, caplog: LogCaptureFixture, dp_config: DPModellerConfig
    ) -> None:
        """Tests apply_pod_dp causes no changes if no pod dp."""
        caplog.set_level(logging.INFO)
        orig_dp_config = copy.deepcopy(dp_config)
        dp = _DifferentiallyPrivate(dp_config)
        dp.apply_pod_dp(None)

        assert vars(dp._dp_config) == vars(orig_dp_config)  # hasn't changed
        assert "No pod DP preferences, using modeller preferences." in caplog.text

    def test_apply_pod_dp_caps_values(
        self,
        caplog: LogCaptureFixture,
        dp_config: DPModellerConfig,
        pod_dp_config: DPPodConfig,
    ) -> None:
        """Tests that limits are applied and logged from pod DP config."""
        orig_dp_config = copy.deepcopy(dp_config)
        dp = _DifferentiallyPrivate(dp_config)
        dp.apply_pod_dp(pod_dp_config)

        # Check config applied
        assert dp._dp_config is not None

        # Check caps are applied
        assert dp._dp_config.epsilon == pod_dp_config.epsilon
        assert dp._dp_config.delta == pod_dp_config.delta

        # Check these are different from the supplied ones
        assert dp._dp_config.epsilon != orig_dp_config.epsilon
        assert dp._dp_config.delta != orig_dp_config.delta

        # Check these changes are logged
        assert (
            f"Requested DP max epsilon ({orig_dp_config.epsilon}) exceeds "
            f"maximum value allowed by pod. Using pod max of "
            f"{pod_dp_config.epsilon}." in caplog.text
        )
        assert (
            f"Requested DP target delta ({orig_dp_config.delta}) exceeds "
            f"maximum value allowed by pod. Using pod max of "
            f"{pod_dp_config.delta}." in caplog.text
        )
