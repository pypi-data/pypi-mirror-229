"""Tests for base model algorithms module."""

from unittest.mock import Mock

import pytest

from bitfount.data.datasources.base_source import BaseSource
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseWorkerModelAlgorithm,
)
from tests.utils.helper import create_datasource, unit_test


@unit_test
class TestBase:
    """Test base model algorithms module."""

    @pytest.fixture
    def datasource(self) -> BaseSource:
        """Fixture for datasource."""
        return create_datasource(classification=True)

    def test_base_worker_initialise(
        self,
        datasource: BaseSource,
    ) -> None:
        """Test initialise updates model parameters on worker side."""
        model = Mock(create_autospec=True)
        base = _BaseWorkerModelAlgorithm(model=model)
        base.initialise(datasource)
        base.model.initialise_model.assert_called_once()  # type: ignore[attr-defined]  # Reason: model is a mock  # noqa: B950
