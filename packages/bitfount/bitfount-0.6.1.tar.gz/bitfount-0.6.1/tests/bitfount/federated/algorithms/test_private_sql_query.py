"""Tests for the sql query algorithm."""
from copy import deepcopy
import logging
import re
from typing import TYPE_CHECKING
from unittest.mock import Mock, create_autospec

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import pandas_dtype
import pytest
from pytest import LogCaptureFixture, fixture
from pytest_mock import MockerFixture
import sqlalchemy

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.database_source import DatabaseConnection, DatabaseSource
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import ContinuousRecord
from bitfount.federated.algorithms.base import (
    BaseModellerAlgorithm,
    BaseWorkerAlgorithm,
    _BaseAlgorithm,
)
from bitfount.federated.algorithms.private_sql_query import (
    PrivateSqlQuery,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.exceptions import AlgorithmError
from bitfount.federated.modeller import _Modeller
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.utils import _ALGORITHMS
from bitfount.hub import BitfountHub
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import (
    TABLE_NAME,
    create_datasource,
    create_schema,
    create_schema_pii,
    dp_test,
    unit_test,
)


@fixture
def column_ranges() -> dict:
    """Fixture for the column ranges."""
    return {
        "A": {"lower": 1, "upper": 1000},  # will be int (A-D)
        "B": {"lower": 1, "upper": 1000},
        "C": {"lower": 1, "upper": 1000},
        "D": {"lower": 1, "upper": 1000},
        "E": {"lower": 0, "upper": 1},  # will be float (E-H)
        "F": {"lower": 0, "upper": 1},
        "G": {"lower": 0, "upper": 1},
        "H": {"lower": 0, "upper": 1},
        "I": {},  # will be string (I-L)
        "J": {},
        "K": {},
        "L": {},
        "TARGET": {"lower": 0, "upper": 1},  # will be int
    }


@dp_test
class TestPrivateSqlQuery:
    """Test PrivateSqlQuery algorithm."""

    @fixture
    def datasource(self) -> BaseSource:
        """Fixture for datasource."""
        return create_datasource(classification=True)

    @fixture
    def column_ranges_multi(self) -> dict:
        """Fixture for the column ranges."""
        return {
            "dummy_data": {
                "name": {"lower": 1, "upper": 5000, "private_id": True},
                "age": {"lower": 1, "upper": 100},
                "weight": {"lower": 1.8, "upper": 230},
                "exercise": {},
            },
            "dummy_data_2": {
                "name": {"lower": 1, "upper": 5000, "private_id": True},
                "height": {"lower": 25, "upper": 230},
            },
        }

    @fixture
    def pod_schema(self) -> BitfountSchema:
        """Fixture for schema."""
        return create_schema(classification=True)

    @fixture
    def pod_schema_pii(self) -> BitfountSchema:
        """Fixture for PII data schema."""
        return create_schema_pii()

    def test_modeller_types(self, column_ranges: dict) -> None:
        """Test modeller method."""
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        algorithm = algorithm_factory.modeller()
        for type_ in [
            _BaseAlgorithm,
            BaseModellerAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    def test_worker_types(self, column_ranges: dict) -> None:
        """Test worker method."""
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        algorithm = algorithm_factory.worker(
            hub=create_autospec(BitfountHub, instance=True)
        )
        for type_ in [
            _BaseAlgorithm,
            BaseWorkerAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    def test_worker_init_datasource(
        self, column_ranges: dict, datasource: BaseSource
    ) -> None:
        """Test worker init with datasource."""
        kwargs = {"hub": Mock(spec=BitfountHub)}
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
            **kwargs,
        )
        algorithm_factory.worker(**kwargs).initialise(
            datasource=datasource,
            pod_identifier="user/test-pod",
            pod_dp=DPPodConfig(epsilon=1, delta=0.0001),
        )

    def test_worker_init_missingargs(
        self, column_ranges: dict, datasource: BaseSource
    ) -> None:
        """Test worker init without all arguments."""
        kwargs = {"hub": Mock(spec=BitfountHub)}
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
            **kwargs,
        )
        algorithm_factory.worker(**kwargs).initialise(datasource=datasource)

    def test_modeller_init(self, column_ranges: dict) -> None:
        """Test modeller init method."""
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        algorithm_factory.modeller().initialise()

    def test_bad_sql_no_table(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test that having bad SQL query raises an error."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        algorithm_factory = PrivateSqlQuery(
            query="SELECT MAX(G) AS MAX_OF_G",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        with pytest.raises(
            AlgorithmError,
            match="The default table for single table datasource is the pod",
        ):
            worker.run()

    def test_no_pod_identifier(
        self,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test that having no pod identifier raises error."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = None
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        with pytest.raises(
            AlgorithmError, match="No pod identifier - cannot get schema"
        ):
            worker.run()

    def test_bad_sql_query_statement(
        self,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test that a bad operator in SQL query errors out."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}
        pod_identifier = "test-pod"

        algorithm_factory = PrivateSqlQuery(
            query="SELECTOR MAX(G) AS MAX_OF_G from `test-pod`.`test-pod`",
            table=pod_identifier,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        with pytest.raises(AlgorithmError, match="Error executing PrivateSQL query"):
            worker.run()

    def test_bad_sql_query_column(
        self,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test that an invalid column in SQL query errors out."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}
        pod_identifier = "test-pod"

        algorithm_factory = PrivateSqlQuery(
            query="SELECT MAX(BITFOUNT_TEST) AS MAX_OF_BITFOUNT_TEST from `test-pod`.`test-pod`",  # noqa: B950
            table=pod_identifier,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        with pytest.raises(AlgorithmError, match="Error executing PrivateSQL query"):
            worker.run()

    def test_worker_gets_sql_results(
        self, column_ranges: dict, datasource: BaseSource, pod_schema: BitfountSchema
    ) -> None:
        """Test that a SQL query returns correct result."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM `testpod`.`testpod`",
            table="testpod",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "testpod"
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        results = worker.run()

        assert results is not None
        assert len(results) > 0
        # The result should not be the same as the true value
        assert float(results["AVG_OF_G"][0]) != 0.500129

    def test_sql_algorithm_db_connection_multitable_onetable(
        self,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test sql algorithm on multitable db connection, check ranges."""
        pod_identifier = "testpod"
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}

        db_src = DatabaseSource(
            DatabaseConnection(
                db_session_pii, table_names=["dummy_data", "dummy_data_2"]
            )
        )
        db_src.validate()
        algorithm_factory = PrivateSqlQuery(
            query="""
            SELECT avg(age) as avg_adult
            FROM public.dummy_data
            WHERE age > 17;""",
            table=pod_identifier,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = db_src
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        results = worker.run()

        # Check output has the correct form
        assert results is not None
        assert len(results) == 1

        # Check the results are as expected (name and within range)
        assert "avg_adult" in results.columns and len(results.columns) == 1
        assert 1 <= float(results["avg_adult"][0]) <= 100

    def test_sql_algorithm_db_connection_no_dp(
        self,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test sql algorithm on multitable db connection, no pod dp."""
        pod_identifier = "testpod"
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}

        db_src = DatabaseSource(
            DatabaseConnection(
                db_session_pii, table_names=["dummy_data", "dummy_data_2"]
            )
        )
        db_src.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(age) as avg_adult FROM public.dummy_data where age > 17;",  # noqa: B950
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = db_src
        worker.pod_identifier = pod_identifier
        worker.pod_dp = None
        worker.run()

        # Check that the pod_dp is set to the DP configuration given by modeller.
        assert worker.pod_dp is not None
        assert worker.pod_dp.epsilon == 0.1
        assert worker.pod_dp.delta == 0.00001

    def test_sql_algorithm_db_connection_test_float(
        self,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test sql algorithm on multitable db connection, check float result."""
        pod_identifier = "testpod"
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        # Create column metadata without ranges to test defaults
        column_ranges_multi_nobounds = column_ranges_multi
        column_ranges_multi_nobounds["dummy_data_2"]["height"] = {}

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi_nobounds,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        results = worker.run()

        # Check output has the correct form
        assert results is not None
        assert len(results) == 1

        # Check the results are as expected (name and within range)
        assert "avg_height" in results.columns and len(results.columns) == 1
        # There is a very small probability these tests will fail
        assert float(results["avg_height"][0]) <= 4
        assert float(results["avg_height"][0]) >= -4

    def test_sql_algorithm_db_connection_test_colnotthere(
        self,
        caplog: LogCaptureFixture,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test fallback for column not in data schema."""
        pod_identifier = "testpod"
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        # Create column metadata without ranges to test defaults
        column_ranges_multi_nobounds = column_ranges_multi
        column_ranges_multi_nobounds["dummy_data_2"]["dynamic"] = {}

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi_nobounds,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        worker.run()
        assert "proceed assuming it is a string" in caplog.text

    def test_sql_algorithm_db_connection_test_tabnotthere(
        self,
        caplog: LogCaptureFixture,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test query fails if table in metadata not in pod data."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"
        pod_identifier = "testpod"
        # Create column metadata without ranges to test defaults
        column_ranges_multi_nobounds = column_ranges_multi
        column_ranges_multi_nobounds["dummy_data_3"] = {"dynamic": {}}

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi_nobounds,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        worker.run()
        assert "SQL query will probably fail" in caplog.text

    def test_sql_algorithm_db_connection_test_incompletemeta(
        self,
        caplog: LogCaptureFixture,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test the code which auto-completes the metadata if not complete."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"
        pod_identifier = "testpod"
        # Create column metadata without ranges to test defaults
        column_ranges_missing_feature = column_ranges_multi
        del column_ranges_missing_feature["dummy_data"]["weight"]

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        ds.load_data()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_missing_feature,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        worker.run()
        assert "lower and upper bound of (0,1) for field [weight]" in caplog.text

    def test_sql_algorithm_db_connection_test_othertypes(
        self,
        caplog: LogCaptureFixture,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test metadata auto-complete.

        If a column/feature is missing, test that defaults ranges
        are correctly applied.
        """
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        # Create column metadata without ranges to test defaults
        column_ranges_missing_feature = column_ranges_multi
        del column_ranges_missing_feature["dummy_data"]["weight"]

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_missing_feature,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "testpod"
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        worker.run()
        assert "lower and upper bound of (0,1) for field [weight]" in caplog.text

    def test_sql_algorithm_db_connection_multitable_groupby(
        self,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test Group By statement in SQL query ."""
        pod_identifier = "testpod"
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query=(
                "SELECT avg(age) as avg_adult, exercise as e "
                "FROM public.dummy_data where age > 17 "
                "GROUP BY exercise "
                "ORDER BY avg_adult ASC;"
            ),
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        results = worker.run()
        # Check output has the correct form
        assert results is not None
        assert len(results) == 11

        # Check the results are as expected (name and within range)
        assert len(results.columns) == 2
        assert "avg_adult" in results.columns
        assert "e" in results.columns
        assert float(results["avg_adult"][0]) <= 100
        for i in range(1, 11):
            assert 1 <= float(results["avg_adult"][i]) <= 100

    def test_sql_algorithm_db_connection_multitable_anothertable(
        self,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test result of SQL algorithm in different table."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(height) AS avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "testpod"
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        results = worker.run()

        # Check output has the correct form
        assert results is not None
        print(results)
        assert len(results) == 1

        # Check the results are as expected (name and within range)
        assert "avg_height" in results.columns and len(results.columns) == 1
        assert float(results["avg_height"][0]) <= 230
        assert float(results["avg_height"][0]) >= 25

    def test_join_sql_query_statement(
        self,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test that a JOIN yields an appropriate error."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="""
            SELECT 'd1.Date', 'A'
            FROM public.dummy_data d1
            LEFT JOIN public.dummy_data_2 d2
            ON 'd1.Date' = 'd2.Date'
            """,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = ""
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        with pytest.raises(AlgorithmError, match="JOIN clauses are not supported"):
            worker.run()

    def test_sql_algorithm_db_connection_multitable_epsilonspent(
        self,
        caplog: LogCaptureFixture,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test that epsilon is respected with SQL query."""
        caplog.set_level(logging.INFO)
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )

        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(height) AS avg_height FROM public.dummy_data_2;",
            epsilon=0.4,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        worker.run()
        # Check that we surface an error for exceeding budget
        assert (
            "Total privacy cost for query will be "
            "(epsilon=0.9999999999166668, delta=1.4999949999983109e-05)" in caplog.text
        )
        assert (
            "Executing SQL query with epsilon 0.3333333333055556 and delta "
            "1e-05 applied on each queried column." in caplog.text
        )

    def test_sql_algorithm_db_connection_schema_name(
        self,
        caplog: LogCaptureFixture,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test that the schema name is added in the run method."""
        caplog.set_level(logging.INFO)
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )

        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(height) AS avg_height FROM public.dummy_data_2;",
            epsilon=20,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.run()
        assert worker.db_schema == "public"

    def test_sql_algorithm_db_connection_wrong_schema_name(
        self,
        column_ranges_multi: dict,
        db_session_pii: sqlalchemy.engine.base.Engine,
        pod_schema_pii: BitfountSchema,
    ) -> None:
        """Test that wrong schema name raises error."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )

        ds = DatabaseSource(db_conn, seed=420)
        ds.validate()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(height) AS avg_height FROM public.dummy_data_2;",
            epsilon=20,
            delta=0.00001,
            column_ranges=column_ranges_multi,
            db_schema="wrong",
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        with pytest.raises(
            AlgorithmError, match="Schema 'wrong' not found in database."
        ):
            worker.run()

    def test_schema_mapping_unknown_column(
        self,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test failure if feature specified not in pod data."""
        pod_identifier = "testpod"
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Update column ranges to have a column not in the schema
        column_ranges_bad = column_ranges
        column_ranges_bad["Z"] = {"lower": 0, "upper": 1}

        # Run the query
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM `testpod`.`testpod`",
            table=pod_identifier,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_bad,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        with pytest.raises(AlgorithmError, match=re.escape("got error ['Z']")):
            worker.run()

    def test_schema_mapping_no_bounds(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test backing off to default bound values."""
        caplog.set_level(logging.INFO)
        pod_identifier = "testpod"
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Update column ranges to have a column not in the schema
        column_ranges_bad = column_ranges
        column_ranges_bad["A"] = {}

        # Run the query
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM `testpod`.`testpod`",
            table=pod_identifier,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_bad,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        worker.run()

        assert "Using default lower and upper bound" in caplog.text

    def test_schema_mapping_unknown_type(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test schema with unsupported type raises error."""
        caplog.set_level(logging.INFO)
        pod_identifier = "testpod"
        # Unsupported schema
        pod_schema.get_table_schema(TABLE_NAME).features["continuous"][
            "G"
        ] = ContinuousRecord("G", pandas_dtype("datetime64"))

        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run the query
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM `testpod`.`testpod`",
            table=pod_identifier,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "testpod"
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)
        with pytest.raises(
            AlgorithmError, match="must be over numeric or boolean, got string in AVG"
        ):
            worker.run()

    def test_modeller_gets_sql_results(
        self, caplog: LogCaptureFixture, column_ranges: dict, pod_schema: BitfountSchema
    ) -> None:
        """Test SQL query returns a result to modeller."""
        caplog.set_level(logging.INFO)
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema

        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM testpod.testpod",
            table="testpod",
            epsilon=0.1,
            delta=0.001,
            column_ranges=column_ranges,
        )
        modeller = algorithm_factory.modeller()
        data = {"AVG_OF_G": [0.500129]}
        results = {
            "pod1": pd.DataFrame(data),
        }
        returned_results = modeller.run(results=results)
        np.testing.assert_almost_equal(
            returned_results["pod1"]["AVG_OF_G"].to_numpy(),
            results["pod1"]["AVG_OF_G"].to_numpy(),
            decimal=4,
        )

    def test_different_privacy_different_results(
        self, column_ranges: dict, datasource: BaseSource, pod_schema: BitfountSchema
    ) -> None:
        """Test different DP levels provide different results."""
        pod_identifier = "testpod"
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run query with good privacy (i.e. low epsilon and delta)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM `testpod`.`testpod`",
            table=pod_identifier,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=2, delta=0.001)

        # Run query 10 times, aggregate deviations from truth value
        all_deviations = []
        ground_truth = 0.500129
        for _ in range(10):
            results_good_privacy = worker.run()
            # results should be a single column, single row DataFrame
            # with column "AVG_OF_G"
            avg_of_g = float(results_good_privacy["AVG_OF_G"][0])
            all_deviations.append(np.abs(ground_truth - avg_of_g))
        mean_deviation_good = np.mean(np.array(all_deviations))

        # Run query with bad privacy (i.e. high epsilon and delta)
        algorithm_factory_bad = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM `testpod`.`testpod`",
            table=pod_identifier,
            epsilon=20.0,
            delta=1.0,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory_bad.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=40, delta=2.0)

        # Run query 10 times, aggregate deviations from truth value
        all_deviations_bad = []
        for _ in range(10):
            results_bad_privacy = worker.run()
            # results should be a single column, single row DataFrame
            # with column "AVG_OF_G"
            avg_of_g = float(results_bad_privacy["AVG_OF_G"][0])
            all_deviations_bad.append(np.abs(ground_truth - avg_of_g))
        mean_deviation_bad = np.mean(np.array(all_deviations_bad))

        # Check that deviation is higher with more DP noise
        assert mean_deviation_good > mean_deviation_bad

    def test_different_privacy_applied(
        self, column_ranges: dict, datasource: BaseSource, pod_schema: BitfountSchema
    ) -> None:
        """Test that DP yields different results over multiple queries."""
        pod_identifier = "testpod"
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run query with good privacy (i.e. low epsilon and delta)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM `testpod`.`testpod`",
            table=pod_identifier,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=1, delta=0.0001)

        # Run query 10 times, ensure results are unique
        all_results = {}
        for _ in range(10):
            results = worker.run()
            # results should be a single column, single row DataFrame
            # with column "AVG_OF_G"
            avg_of_g = float(results["AVG_OF_G"][0])
            assert avg_of_g not in all_results
            all_results[avg_of_g] = 1

    def test_no_pod_dp(
        self,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test modeller DP is applied to pod with no DP."""
        pod_identifier = "testpod"
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run query with good privacy (i.e. low epsilon and delta)
        algorithm_factory = PrivateSqlQuery(
            query=f"SELECT SUM(G) AS SUM_OF_G FROM {pod_identifier}.{pod_identifier}",
            epsilon=3.0,
            delta=0.1,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = pod_identifier
        worker.pod_dp = None
        with pytest.raises(AlgorithmError):
            worker.run()

        # Check that the pod_dp is set to the DP configuration given by modeller.
        assert worker.pod_dp is not None
        assert worker.pod_dp.epsilon == 3.0
        assert worker.pod_dp.delta == 0.1

    def test_pod_dp_prevails(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test Pod DP is preferred over modeller DP."""
        caplog.set_level(logging.INFO)
        pod_identifier = "testpod"
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run query with good privacy (i.e. low epsilon and delta)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT SUM(G) AS SUM_OF_G FROM `testpod`.`testpod`",
            table=pod_identifier,
            epsilon=3.0,
            delta=0.1,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = pod_identifier
        worker.pod_dp = DPPodConfig(epsilon=2.0, delta=0.001)

        worker.run()
        assert "Requested DP max epsilon (3.0) exceeds maximum" in caplog.text
        assert "Requested DP target delta (0.1) exceeds maximum" in caplog.text
        assert (
            "Total privacy cost for query will be "
            "(epsilon=2.0, delta=0.0009997777777778216)" in caplog.text
        )
        assert (
            "Executing SQL query with epsilon 1.0 and "
            "delta 0.0006666666666666666 applied on each queried column." in caplog.text
        )

    def test_private_sql_execute(
        self, column_ranges: dict, mock_bitfount_session: Mock, mocker: MockerFixture
    ) -> None:
        """Test execute syntactic sugar."""
        query = PrivateSqlQuery(
            query="SELECT * FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        pod_identifiers = ["username/pod-id"]

        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")
        query.execute(pod_identifiers=pod_identifiers)
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers=pod_identifiers, require_all_pods=False, project_id=None
        )


@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for private sql algorithm."""

    def test_serialization(self, column_ranges: dict) -> None:
        """Test Marshmallow Serialization for private sql algorithm."""
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)
        assert isinstance(loaded, PrivateSqlQuery)
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
    _algo_factory: _ResultsOnlyCompatibleAlgoFactory_ = PrivateSqlQuery(
        query=cast(str, object()),
        epsilon=cast(float, object()),
        delta=cast(float, object()),
        column_ranges=cast(dict, object()),
    )
    _modeller_side: _ResultsOnlyCompatibleModellerAlgorithm = _ModellerSide()
    _worker_side: _ResultsOnlyModelIncompatibleWorkerAlgorithm = _WorkerSide(
        query=cast(str, object()),
        epsilon=cast(float, object()),
        delta=cast(float, object()),
        column_ranges=cast(dict, object()),
        hub=cast(BitfountHub, object()),
        table=cast(str, object()),
    )
