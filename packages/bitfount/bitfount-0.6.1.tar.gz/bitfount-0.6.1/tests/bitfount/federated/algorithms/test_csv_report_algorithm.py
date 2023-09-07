"""Tests for the csv report algorithm."""
import logging
import os
from pathlib import Path

from _pytest.logging import LogCaptureFixture
import numpy as np
import pandas as pd
import pytest
from pytest import fixture

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasplitters import PercentageSplitter
from bitfount.federated.algorithms.csv_report_algorithm import (
    ColumnFilter,
    CSVReportAlgorithm,
)
from bitfount.federated.exceptions import AlgorithmError
from tests.utils.helper import create_dataset, unit_test


@unit_test
class TestCSVAlgorithm:
    """Tests for the CSVReportAlgorithm."""

    @fixture
    def datasource(self) -> BaseSource:
        """Fixture for the DataFrameSource."""
        dataset = create_dataset(classification=False)
        datasource = DataFrameSource(
            dataset,
            data_splitter=PercentageSplitter(
                validation_percentage=0, test_percentage=100
            ),
        )
        datasource._test_idxs = np.array([i for i in range(dataset.shape[0])])
        datasource.load_data()
        return datasource

    @fixture
    def results_df(self) -> pd.DataFrame:
        """Fixture for a results dataframe."""
        return pd.DataFrame(
            np.random.rand(4000, 2),  # len of datasource
            columns=["res col 1", "res col 2"],
        )

    @fixture
    def results_df2(self) -> pd.DataFrame:
        """Fixture for a results dataframe."""
        return pd.DataFrame(
            np.random.rand(4000, 1),
            columns=["fin result"],
        )

    def test_worker_side_with_task_id(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test the worker side of the algorithm with task id."""
        csv_report_algo = CSVReportAlgorithm(save_path=str(tmp_path)).worker()
        csv_report_algo.initialise(datasource)
        df = csv_report_algo.run(results_df=[results_df, results_df2], task_id="blah")
        assert os.path.exists(f"{tmp_path}/blah/results.csv")
        assert df.shape == (
            datasource.data.shape[0],
            datasource.data.shape[1] + 3,
        )

    def test_worker_run_method_appends_csv_with_task_id(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Tests the CSV appending functionality during batched execution."""
        csv_report_algo = CSVReportAlgorithm(save_path=str(tmp_path)).worker()
        csv_report_algo.initialise(datasource)
        df = csv_report_algo.run(results_df=[results_df, results_df2], task_id="blah")
        assert os.path.exists(f"{tmp_path}/blah/results.csv")
        assert len(df) == pd.read_csv(f"{tmp_path}/blah/results.csv").shape[0]

        # Mimic a second run of the same task id to test the overwrite functionality
        df = csv_report_algo.run(results_df=[results_df, results_df2], task_id="blah")
        # This time, the number of rows should be doubled
        assert len(df) * 2 == pd.read_csv(f"{tmp_path}/blah/results.csv").shape[0]

    def test_worker_run_method_doesnt_append_to_csv_without_task_id(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Tests that separate CSVs are produced if there is no task ID specified.

        This is because there is no way to know what the right CSV file is.
        """
        csv_report_algo = CSVReportAlgorithm(save_path=str(tmp_path)).worker()
        csv_report_algo.initialise(datasource)
        df = csv_report_algo.run(results_df=[results_df, results_df2])
        assert os.path.exists(f"{tmp_path}/results.csv")
        assert len(df) == pd.read_csv(f"{tmp_path}/results.csv").shape[0]

        # Mimic a second run of the same task id to test the CSV functionality
        df = csv_report_algo.run(results_df=[results_df, results_df2])
        # This time, there should be a second CSV file
        assert os.path.exists(f"{tmp_path}/results (1).csv")
        assert len(df) == pd.read_csv(f"{tmp_path}/results (1).csv").shape[0]

    def test_worker_side_no_task_id(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test the worker side of the algorithm."""
        csv_report_algo = CSVReportAlgorithm(save_path=str(tmp_path)).worker()
        csv_report_algo.initialise(datasource)
        df = csv_report_algo.run(results_df=[results_df, results_df2])
        assert os.path.exists(f"{tmp_path}/results.csv")
        assert df.shape == (
            datasource.data.shape[0],
            datasource.data.shape[1] + 3,
        )  # (2 test patients, 1 ga column, 2 etdrs columns, and 320 datasource original cols) # noqa: B950

    def test_worker_side_w_original_cols(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test the worker side of the algorithm with original_cols."""
        csv_report_algo = CSVReportAlgorithm(
            save_path=str(tmp_path), original_cols=["B"]
        ).worker()
        csv_report_algo.initialise(datasource)
        df = csv_report_algo.run(results_df=[results_df, results_df2])
        assert os.path.exists(f"{tmp_path}/results.csv")
        assert df.shape == (
            4000,
            4,
        )

    def test_worker_side_w_filter(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test the worker side of the algorithm with filter."""
        csv_report_algo = CSVReportAlgorithm(
            save_path=str(tmp_path),
            filter=[
                ColumnFilter(column="fin result", operator="greater than", value=0.3),
                ColumnFilter(
                    column="res col 1",
                    operator="greater than or equal",
                    value=0.78,
                ),
            ],
            original_cols=["A"],
        ).worker()
        csv_report_algo.initialise(datasource)
        df = csv_report_algo.run(results_df=[results_df, results_df2])
        assert os.path.exists(f"{tmp_path}/results.csv")
        assert "fin result greater than 0.3" in df.columns
        assert "Matches all criteria" in df.columns
        assert "res col 1 greater than or equal 0.78" in df.columns
        assert df.shape == (
            4000,
            7,
        )

    def test_worker_side_filter_TypeError(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test TypeError on the filter logs warning."""
        csv_report_algo = CSVReportAlgorithm(
            save_path=str(tmp_path),
            filter=[ColumnFilter(column="I", operator="greater than", value=10)],
            original_cols=["I", "A"],
        ).worker()
        aux_df = pd.DataFrame(np.random.rand(4000, 1), columns=["test"])

        csv_report_algo.initialise(datasource)
        df = csv_report_algo.run(results_df=[results_df, results_df2, aux_df])

        assert (
            "Filter column I is incompatible with operator "
            "type greater than. Raised TypeError: '>' not "
            "supported between instances of 'str' and 'float'" in caplog.text
        )
        assert os.path.exists(f"{tmp_path}/results.csv")
        assert df.shape == (4000, 7)

    def test_worker_side_filter_KeyError(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test KeyError on the filter logs warning."""
        csv_report_algo = CSVReportAlgorithm(
            save_path=str(tmp_path),
            filter=[ColumnFilter(column="test", operator="greater than", value=10)],
            original_cols=["A"],
        ).worker()
        csv_report_algo.initialise(datasource)
        df = csv_report_algo.run(results_df=[results_df, results_df2])
        assert "No column `test` found in the data." in caplog.text
        assert os.path.exists(f"{tmp_path}/results.csv")
        assert df.shape == (4000, 5)  # only filter on Ga column

    def test_worker_side_no_test_idxs(
        self,
        datasource: BaseSource,
        results_df: pd.DataFrame,
        results_df2: pd.DataFrame,
        tmp_path: Path,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test the worker side logs error if data doesn't have test_idxs set."""
        datasource._test_idxs = None
        csv_report_algo = CSVReportAlgorithm(save_path=str(tmp_path)).worker()
        csv_report_algo.initialise(datasource)
        if not datasource.iterable:
            with pytest.raises(AlgorithmError):
                csv_report_algo.run(
                    results_df=[results_df, results_df2], task_id="blah"
                )
            assert "Datasource has no test set, cannot produce CSV." in caplog.text
            assert not os.path.exists(f"{tmp_path}/blah/results.csv")
        else:
            csv_report_algo.run(results_df=[results_df, results_df2], task_id="blah")
            assert os.path.exists(f"{tmp_path}/blah/results.csv")

    def test_modeller_side(self, caplog: LogCaptureFixture, tmp_path: Path) -> None:
        """Test modeller side of the algorithm."""
        caplog.set_level(logging.INFO)
        results = {"pod": None}
        csv_report_algo = CSVReportAlgorithm(
            save_path=str(tmp_path), original_cols=["first_name"]
        ).modeller()
        csv_report_algo.run(results=results)
        assert "CSV saved to the pod." in caplog.text
