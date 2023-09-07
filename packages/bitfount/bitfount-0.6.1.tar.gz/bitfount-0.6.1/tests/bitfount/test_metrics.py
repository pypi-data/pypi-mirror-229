"""Test metrics from bitfount.metrics."""
from dataclasses import dataclass
from typing import Optional, Union, cast

import numpy as np
import pandas as pd
import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture
from sklearn.metrics import recall_score

from bitfount.metrics import (
    BINARY_CLASSIFICATION_METRICS,
    MULTICLASS_CLASSIFICATION_METRICS,
    MULTILABEL_CLASSIFICATION_METRICS,
    REGRESSION_METRICS,
    SEGMENTATION_METRICS,
    ClassificationMetric,
    MetricCollection,
    MetricsProblem,
    _binary_dice_coefficient,
    _stats_score,
    dice_score,
    iou,
    multiclass_dice_coefficients,
    sum_fpr_curve,
)
from bitfount.models.base_models import ClassifierMixIn, RegressorMixIn
from tests.utils.helper import integration_test, unit_test


class TestMetricCollection:
    """Tests Metrics class explicitly where necessitated.

    Currently already being partially tested in `test_models.py`
    """

    @unit_test
    def test_value_error_if_no_metrics_or_problem_provided(self) -> None:
        """Tests that a ValueError is raised in the constructor.

        This happens if neither `problem` nor `metrics` are provided.
        """
        with pytest.raises(ValueError):
            MetricCollection()

    @unit_test
    @pytest.mark.parametrize(
        "classification, multilabel, classes, problem",
        [
            (True, False, 2, MetricsProblem.BINARY_CLASSIFICATION),
            (True, False, 3, MetricsProblem.MULTICLASS_CLASSIFICATION),
            (True, True, 2, MetricsProblem.MULTILABEL_CLASSIFICATION),
            (False, None, None, MetricsProblem.REGRESSION),
        ],
    )
    def test_create_instance_from_model(
        self,
        classes: Optional[int],
        classification: bool,
        multilabel: bool,
        problem: MetricsProblem,
    ) -> None:
        """Test Metric Collection created from Model.

        Tests that MetricCollection creates the right problem from the Model.
        """
        if isinstance(classes, int):
            n_classes = classes

        @dataclass
        class ClassifierModel(ClassifierMixIn):
            multilabel: bool
            n_classes: int

        class RegressorModel(RegressorMixIn):
            pass

        model: Union[ClassifierModel, RegressorModel]
        if classification:
            model = ClassifierModel(multilabel, n_classes)
        else:
            model = RegressorModel()

        m = MetricCollection.create_from_model(model)  # type: ignore[arg-type] # reason: used only for testing # noqa: B950
        assert m.problem == problem

    @unit_test
    def test_create_instance_from_unrecognised_model(
        self, caplog: LogCaptureFixture
    ) -> None:
        """Test Metric Collection created from an unrecognised model."""
        MetricCollection.create_from_model(model="model", metrics=REGRESSION_METRICS)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950
        log_record = caplog.records[0]
        assert log_record.levelname == "WARNING"
        assert (
            log_record.message
            == "Metrics problem type can't be determined. Leaving empty."
        )

    @integration_test
    def test_binary_classification(self) -> None:
        """Test metrics in the binary class setting."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(problem=MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob)

        assert isinstance(m.results, dict)
        assert len(m.results) == len(BINARY_CLASSIFICATION_METRICS)
        assert cast(float, m.optimal_threshold) <= 1.0
        assert cast(float, m.optimal_threshold) >= 0.0
        for _, v in m.results.items():
            # assert 1 number before the decimal place and a maximum of 4 after
            assert len(str(v)) <= 6
            assert v >= 0.0
            assert v <= 1.0

    @integration_test
    def test_binary_classification_not_enough_data(self) -> None:
        """Test metrics in the binary class setting with not enough data."""
        y_true = np.array([0, 0])
        y_prob = np.array([0.1, 0.3])

        m = MetricCollection(problem=MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob)

        assert isinstance(m.results, dict)
        assert len(m.results) == len(BINARY_CLASSIFICATION_METRICS)
        assert m.results["AUC"] == np.inf

    @integration_test
    def test_multiclass_classification(self) -> None:
        """Test metrics in the multiclass setting (>2 classes)."""
        y_true = np.array([0, 1, 2, 0, 1])
        y_prob = np.array(
            [
                [0.5, 0.4, 0.1],
                [0.9, 0.1, 0.0],
                [0.0, 0.5, 0.5],
                [0.3, 0.3, 0.4],
                [0.2, 0.6, 0.2],
            ]
        )

        m = MetricCollection(problem=MetricsProblem.MULTICLASS_CLASSIFICATION)
        m.compute(y_true, y_prob)
        assert isinstance(m.results, dict)
        assert len(m.results) == len(MULTICLASS_CLASSIFICATION_METRICS)
        for _, v in m.results.items():
            # assert 1 number before the decimal place and a maximum of 4 after
            assert len(str(v)) <= 6
            assert v >= 0.0
            assert v <= 1.0

    @integration_test
    def test_multilabel_classification(self) -> None:
        """Test metrics in the multilabel setting."""
        y_true = np.array([[1, 1, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0]])
        y_prob = np.array(
            [
                [0.5, 0.4, 0.1],
                [0.9, 0.1, 0.0],
                [0.0, 0.5, 0.5],
                [0.3, 0.3, 0.4],
                [0.2, 0.6, 0.2],
            ]
        )

        m = MetricCollection(problem=MetricsProblem.MULTILABEL_CLASSIFICATION)
        m.compute(y_true, y_prob)
        assert isinstance(m.results, dict)
        assert len(m.results) == len(MULTILABEL_CLASSIFICATION_METRICS)
        assert cast(float, m.optimal_threshold) <= 1.0
        assert cast(float, m.optimal_threshold) >= 0.0
        for _, v in m.results.items():
            # assert 1 number before the decimal place and a maximum of 4 after
            assert len(str(v)) <= 6
            assert v >= 0.0
            assert v <= 1.0

    @integration_test
    def test_regression(self) -> None:
        """Test metrics in the regression setting."""
        y_true = np.array([0.2, 1, 0.5, 0, 1, 0.55])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(problem=MetricsProblem.REGRESSION)
        m.compute(y_true, y_prob)

        assert isinstance(m.results, dict)
        assert len(m.results) == len(REGRESSION_METRICS)
        assert m.optimal_threshold is None

    @integration_test
    def test_optimise_chosen_metric(self) -> None:
        """Optimise chosen metric in binary classification."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(problem=MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob, "Recall")
        assert m.optimal_threshold == 0.0

    @unit_test
    def test_optimise_chosen_metric_does_not_exist(self) -> None:
        """Test optimisation for classification.

        Chosen metric doesn not exist raises ValueError.
        """
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(problem=MetricsProblem.BINARY_CLASSIFICATION)
        with pytest.raises(ValueError):
            m.compute(y_true, y_prob, "Blah")

    @unit_test
    def test_get_results_df(self) -> None:
        """Tests get_results_df method."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(problem=MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob)
        results_df = m.get_results_df()

        assert isinstance(results_df, pd.DataFrame)
        for index, row in results_df.iterrows():
            assert row["value"] == m.results[cast(str, index)]

    @integration_test
    def test_threshold(self) -> None:
        """Supply the threshold rather than optimising it."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(problem=MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob, threshold=0.5)
        assert m.results["Recall"] == 0.75
        assert m.optimal_threshold is None

    @integration_test
    def test_custom_metric(self) -> None:
        """Test custom metric can be supplied."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])
        custom_metric = ClassificationMetric(recall_score, False)
        m = MetricCollection(
            problem=MetricsProblem.BINARY_CLASSIFICATION,
            metrics={"custom_metric": custom_metric},
        )
        m.compute(y_true, y_prob, metric_to_optimise="custom_metric")
        assert isinstance(m.results, dict)
        assert len(m.results) == 1
        assert m.optimal_threshold is not None

    @unit_test
    def test_correct__get_metrics_segmentation_problem(self) -> None:
        """Test that segmentation metrics are loaded correctly."""
        m = MetricCollection(problem=MetricsProblem.SEGMENTATION)
        assert "IoU" in m.metrics
        assert "DiceCoefficients" in m.metrics
        assert "DiceScore" in m.metrics

    @unit_test
    def test_segmentation_metrics(self) -> None:
        """Test metrics in segmentation setting."""
        y_true = np.array([[1, 1, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0]])
        y_prob = np.array(
            [
                [0.5, 0.4, 0.1],
                [0.9, 0.1, 0.0],
                [0.0, 0.5, 0.5],
                [0.3, 0.3, 0.4],
                [0.2, 0.6, 0.2],
            ]
        )

        m = MetricCollection(problem=MetricsProblem.SEGMENTATION)
        m.compute(y_true, y_prob)
        assert isinstance(m.results, dict)
        assert len(m.results) == len(SEGMENTATION_METRICS)
        assert m.optimal_threshold is None

    @unit_test
    def test_get_metrics_value_error(self) -> None:
        """Test that get_metrics raises ValueError if metric is not found."""
        with pytest.raises(ValueError, match="Problem type not recognised."):
            MetricCollection._get_metrics("not a problem")  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950


@unit_test
class TestSumFPRCurve:
    """Tests sum_fpr_curve() function."""

    def test_one_entry(self) -> None:
        """Tests functionality when only one entry.

        Check that when we have one entry correct, one wrong it gets placed in
        the right places.
        """
        test_target = [1.0, 0.0]
        test_pred = [0.89, 0.32]
        test_var_to_sum = [1.0, -2.0]
        fpr, totals = sum_fpr_curve(
            test_target, test_pred, test_var_to_sum, granularity=10
        )
        # At threshold of 0.3 we start accepting the bad one
        assert fpr == [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        # At threshold of 0.8 we start accepting the good one
        assert totals == [-1, -1, -1, -1, 1, 1, 1, 1, 1, 0, 0]


@unit_test
def test__binary_dice_coefficients() -> None:
    """Tests the binary dice coefficients.

    Computes the expected value as is 2 * the area of intersection divided by
    the total number of pixels in both images.

    """
    y_true = np.array([[1, 1, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0]])
    y_prob = np.array(
        [
            [0.5, 0.4, 0.1],
            [0.9, 0.1, 0.0],
            [0.0, 0.5, 0.5],
            [0.3, 0.3, 0.4],
            [0.2, 0.6, 0.2],
        ]
    )
    # Flatten the target and predictions arrays.
    y_true_f = y_true.flatten()
    y_pred_f = y_prob.flatten()
    # Compute the intersection between predictions and targets
    intersection = (y_true_f * y_pred_f).sum()
    # Get the expected result
    expected_result = (2.0 * intersection) / (y_true_f.sum() + y_pred_f.sum() + 0.0001)
    # Get the result returned from the `_binary_dice_coefficient` function
    res = _binary_dice_coefficient(y_true, y_prob)
    # Make sure the resultis the same
    assert expected_result == res


@unit_test
def test_multiclass_dice_coeff(mocker: MockerFixture) -> None:
    """Tests the multiclass dice coefficients."""
    y_true = np.array([[1, 1, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0]])
    y_prob = np.random.uniform(0, 1, size=(4, 3, 3, 2))
    mock_binary_coeff = mocker.patch(
        "bitfount.metrics._binary_dice_coefficient", return_value=0.6
    )
    res = np.round(multiclass_dice_coefficients(y_true, y_prob), 1)
    mock_binary_coeff.assert_called()
    assert res == 0.4


@unit_test
def test__stats_score() -> None:
    """Tests the stats score function."""
    y_true = np.array([0, 1, 1, 0, 1])
    y_prob = np.array(
        [
            [0.5, 0.4, 0.1],
            [0.9, 0.1, 0.0],
            [0.0, 0.5, 0.5],
            [0.3, 0.3, 0.4],
            [0.2, 0.6, 0.2],
        ]
    )
    tp, fp, tn, fn = _stats_score(y_true, y_prob)
    assert tp == 2
    assert fp == 0
    assert tn == 2
    assert fn == 1


@unit_test
def test_dice_score(mocker: MockerFixture) -> None:
    """Tests the dice score function."""
    y_true = np.array([0, 1, 1, 0, 1])
    y_prob = np.array(
        [
            [0.5, 0.4, 0.1],
            [0.9, 0.1, 0.0],
            [0.0, 0.5, 0.5],
            [0.3, 0.3, 0.4],
            [0.2, 0.6, 0.2],
        ]
    )
    mock_stats_score = mocker.patch(
        "bitfount.metrics._stats_score", return_value=(2, 0, 0, 0)
    )
    score = dice_score(y_true, y_prob)
    mock_stats_score.assert_called()
    assert score == 1.0 / 3


@unit_test
def test_dice_score_no_foreground(mocker: MockerFixture) -> None:
    """Tests dice score zero no foreground class."""
    y_true = np.array([3, 4, 4, 4, 5])
    y_prob = np.array(
        [
            [0.5, 0.4, 0.1],
            [0.9, 0.1, 0.0],
            [0.0, 0.5, 0.5],
            [0.3, 0.3, 0.4],
            [0.2, 0.6, 0.2],
        ]
    )
    mock_stats_score = mocker.patch(
        "bitfount.metrics._stats_score", return_value=(2, 0, 0, 0)
    )
    score = dice_score(y_true, y_prob)
    mock_stats_score.assert_called()
    assert score == 0.0


@unit_test
def test_dice_score_denom_zero(mocker: MockerFixture) -> None:
    """Tests dice score zero when denom is zero."""
    y_true = np.array([0, 1, 1, 0, 1])
    y_prob = np.array(
        [
            [0.5, 0.4, 0.1],
            [0.9, 0.1, 0.0],
            [0.0, 0.5, 0.5],
            [0.3, 0.3, 0.4],
            [0.2, 0.6, 0.2],
        ]
    )
    mock_stats_score = mocker.patch(
        "bitfount.metrics._stats_score", return_value=(0, 0, 0, 0)
    )
    score = dice_score(y_true, y_prob)
    mock_stats_score.assert_called()
    assert score == 0.0


@unit_test
def test_iou(mocker: MockerFixture) -> None:
    """Tests iou score."""
    y_true = np.array([0, 1, 1, 0, 1])
    y_prob = np.array(
        [
            [0.5, 0.4, 0.1],
            [0.9, 0.1, 0.0],
            [0.0, 0.5, 0.5],
            [0.3, 0.3, 0.4],
            [0.2, 0.6, 0.2],
        ]
    )
    mock_stats_score = mocker.patch(
        "bitfount.metrics._stats_score", return_value=(2, 0, 0, 0)
    )
    score = iou(y_true, y_prob)
    mock_stats_score.assert_called()
    assert score == 1.0 / 3


@unit_test
def test_iou_no_foreground_class(mocker: MockerFixture) -> None:
    """Tests iou score zero no foreground class."""
    y_true = np.array([3, 4, 4, 4, 5])
    y_prob = np.array(
        [
            [0.5, 0.4, 0.1],
            [0.9, 0.1, 0.0],
            [0.0, 0.5, 0.5],
            [0.3, 0.3, 0.4],
            [0.2, 0.6, 0.2],
        ]
    )
    mock_stats_score = mocker.patch(
        "bitfount.metrics._stats_score", return_value=(2, 0, 0, 0)
    )
    score = iou(y_true, y_prob)
    mock_stats_score.assert_called()
    assert score == 0.0


@unit_test
def test_iou_denom_zero(mocker: MockerFixture) -> None:
    """Tests iou score zero when denom is zero."""
    y_true = np.array([0, 1, 1, 0, 1])
    y_prob = np.array(
        [
            [0.5, 0.4, 0.1],
            [0.9, 0.1, 0.0],
            [0.0, 0.5, 0.5],
            [0.3, 0.3, 0.4],
            [0.2, 0.6, 0.2],
        ]
    )
    mock_stats_score = mocker.patch(
        "bitfount.metrics._stats_score", return_value=(0, 0, 0, 0)
    )
    score = iou(y_true, y_prob)
    mock_stats_score.assert_called()
    assert score == 0.0
