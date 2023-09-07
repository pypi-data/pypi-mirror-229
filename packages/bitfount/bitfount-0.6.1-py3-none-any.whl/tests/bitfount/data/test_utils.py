"""Tests for data utils classes and methods."""
import datetime
import hashlib
import json
from typing import Any, Dict, Generator, List, Mapping, Optional, Protocol, Union
from unittest.mock import MagicMock, Mock

import numpy as np
import pandas as pd
from pandas._typing import Dtype
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy

from bitfount import BitfountSchema, DataStructure
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.exceptions import (
    DatabaseMissingTableError,
    DatabaseSchemaNotFoundError,
    DatabaseUnsupportedQueryError,
    DatabaseValueError,
)
from bitfount.data.helper import convert_epochs_to_steps
from bitfount.data.utils import (
    DatabaseConnection,
    DataStructureSchemaCompatibility,
    _convert_python_dtypes_to_pandas_dtypes,
    _generate_dtypes_hash,
    _hash_str,
    check_datastructure_schema_compatibility,
)
from bitfount.types import _Dtypes
from tests.utils.helper import unit_test


@unit_test
def test_convert_epochs_to_steps() -> None:
    """Test converting of epochs to steps is correct."""
    dataloader = MagicMock()
    dataloader.__len__.return_value = 100
    steps = convert_epochs_to_steps(5, dataloader)
    assert steps == 100 * 5


@unit_test
class TestDatabaseConnection:
    """Tests DatabaseConnection class."""

    @fixture
    def mock_engine(self) -> Mock:
        """Returns mock sqlalchemy engine."""
        return Mock(spec=sqlalchemy.engine.base.Engine)

    @fixture(autouse=True)
    def mock_inspector(self, mocker: MockerFixture) -> Generator[Mock, None, None]:
        """Automatically mocks sqlalchemy inspector and yields mocked object."""
        mock_inspector = Mock(
            default_schema_name="public", spec=sqlalchemy.engine.Inspector
        )
        mock_inspector.get_schema_names.return_value = ["public"]
        mock_inspector.get_table_names.return_value = ["test_data"]
        mocker.patch("bitfount.data.utils.inspect", return_value=mock_inspector)
        yield mock_inspector

    def test_create_engine_from_connection_string(self, mocker: MockerFixture) -> None:
        """Tests that a sqlalchemy object can be created from a database URI."""
        mock_create_engine = mocker.patch(
            "bitfount.data.utils.create_engine", autospec=True
        )
        db = DatabaseConnection(
            "postgresql://localhost:5432/test", query="SELECT * FROM test_data"
        )
        db.validate()
        mock_create_engine.assert_called_once_with("postgresql://localhost:5432/test")

    def test_schema_not_found_in_database_raises_value_error(
        self, mock_engine: Mock, mock_inspector: Mock
    ) -> None:
        """Tests that DatabaseSchemaNotFoundError raised if schema not in database."""
        with pytest.raises(DatabaseSchemaNotFoundError):
            db = DatabaseConnection(mock_engine, db_schema="nonexistent_schema")
            db.validate()

        mock_inspector.get_schema_names.assert_called_once()

    def test_query_and_table_names_raises_value_error(self, mock_engine: Mock) -> None:
        """Tests that query and table names can't both be specified."""
        with pytest.raises(DatabaseValueError):
            db = DatabaseConnection(
                mock_engine, query="SELECT * FROM test_data", table_names=["test_data"]
            )
            db.validate()

    def test_specified_table_not_found_in_schema_raises_value_error(
        self,
        mock_engine: Mock,
    ) -> None:
        """Tests that DatabaseMissingTableError raised if table not in schema."""
        with pytest.raises(DatabaseMissingTableError):
            db = DatabaseConnection(mock_engine, table_names=["nonexistent_table"])
            db.validate()

    def test_no_tables_found_in_schema_raises_value_error(
        self, mock_engine: Mock, mock_inspector: Mock
    ) -> None:
        """Tests that DatabaseMissingTableError raised if no tables in schema."""
        mock_inspector.get_table_names.return_value = []
        with pytest.raises(DatabaseMissingTableError):
            db = DatabaseConnection(mock_engine)
            db.validate()

    def test_get_default_schema(self, mock_engine: Mock, mock_inspector: Mock) -> None:
        """Tests that default schema is used if none specified."""
        db = DatabaseConnection(mock_engine)
        db.validate()
        mock_inspector.get_table_names.assert_called_once_with(schema="public")

    def test_single_table_name(self, mock_engine: Mock) -> None:
        """Tests that a single table name can be specified."""
        db_conn = DatabaseConnection(mock_engine, table_names=["test_data"])
        db_conn.validate()
        assert not db_conn.multi_table

    def test_multiple_table_names(
        self, mock_engine: Mock, mock_inspector: Mock
    ) -> None:
        """Tests that multiple table names can be specified."""
        mock_inspector.get_table_names.return_value = ["test_data", "test_data_2"]
        db_conn = DatabaseConnection(
            mock_engine, table_names=["test_data", "test_data_2"]
        )
        db_conn.validate()
        assert db_conn.multi_table

    def test_all_tables_in_schema(
        self, mock_engine: Mock, mock_inspector: Mock
    ) -> None:
        """Tests that connection will default to all tables if none provided."""
        mock_inspector.get_table_names.return_value = [
            "test_data",
            "test_data_2",
            "test_data_3",
        ]
        db_conn = DatabaseConnection(mock_engine)
        db_conn.validate()
        assert db_conn.multi_table
        assert db_conn.table_names == ["test_data", "test_data_2", "test_data_3"]

    def test_query(self, mock_engine: Mock) -> None:
        """Tests that query can be specified."""
        db_conn = DatabaseConnection(mock_engine, query="SELECT * FROM test_data")
        db_conn.validate()
        assert not db_conn.multi_table
        assert db_conn.query

    def test_into_query_error(self, mock_engine: Mock) -> None:
        """Tests that a query containing into raises error."""
        with pytest.raises(DatabaseUnsupportedQueryError):
            db = DatabaseConnection(mock_engine, query="SELECT * INTO df")
            db.validate()


@unit_test
class TestDataFrameHashing:
    """Tests for generate_dataframe_hash()."""

    @fixture
    def dtypes(self) -> _Dtypes:
        """A test dataframe with data."""
        return {
            "np_test": np.dtype(int),
            "pd_test": pd.core.arrays.integer.Int64Dtype(),
        }

    @fixture
    def dtypes_hash(self) -> str:
        """The expected hash for the dataframe fixture."""
        # The hash is on the DataFrame.dtypes (which returns a Series), so we
        # manually construct the expected matching one.
        dtypes = {
            "np_test": str(np.dtype(int)),
            "pd_test": str(pd.core.arrays.integer.Int64Dtype()),
        }
        str_rep = json.dumps(dtypes, sort_keys=True)
        return hashlib.sha256(str_rep.encode("utf8")).hexdigest()

    @fixture
    def empty_dtypes(self) -> _Dtypes:
        """A test dtype mapping with no data."""
        return {}

    @fixture
    def empty_dtypes_hash(self) -> str:
        """The expected hash of an empty dataframe."""
        # The hash is on the DataFrame.dtypes (which returns a Series), so we
        # manually construct the expected matching one.
        empty_series: Dict = {}
        str_rep: str = str(empty_series)
        return hashlib.sha256(str_rep.encode("utf8")).hexdigest()

    def test_generate_dtypes_hash(self, dtypes: _Dtypes, dtypes_hash: str) -> None:
        """Tests generated hash is expected one for non-empty dataframe."""
        assert _generate_dtypes_hash(dtypes) == dtypes_hash

    def test_generate_dtypes_hash_empty_dataframe(
        self, empty_dtypes: _Dtypes, empty_dtypes_hash: str
    ) -> None:
        """Tests generated hash is expected one for empty dataframe."""
        assert _generate_dtypes_hash(empty_dtypes) == empty_dtypes_hash

    def test_generate_dtypes_hash_same_for_same_dtypes(
        self, dtypes: Dict[str, Union[Dtype, np.dtype]], dtypes_hash: str
    ) -> None:
        """Tests generated hash is consistent for two dataframes with same cols."""
        dtypes_2 = dtypes.copy()

        # Check they are different instances
        assert dtypes is not dtypes_2
        # Check hashes match
        assert (
            _generate_dtypes_hash(dtypes)
            == _generate_dtypes_hash(dtypes_2)
            == dtypes_hash
        )

    def test_generate_dtypes_hash_different_for_different_dtype_dataframes(
        self, dtypes: _Dtypes, dtypes_hash: str
    ) -> None:
        """Tests hash is different for two dataframes with diff col dtypes."""
        # Change the column dtype from int64 to string
        dtypes_2 = {k: np.dtype(str) for k in dtypes.keys()}

        # Check they are different instances
        assert dtypes is not dtypes_2
        # Check hashes differ
        assert (
            _generate_dtypes_hash(dtypes)
            != _generate_dtypes_hash(dtypes_2)
            != dtypes_hash
        )


@unit_test
def test_hash_str() -> None:
    """Tests that hash_str() works."""
    test_string = "Hello, world!"
    expected_hash = "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3"
    assert _hash_str(test_string) == expected_hash


@unit_test
def test_convert_python_dtypes_to_panda_dtypes_error_unsupported_type() -> None:
    """Tests error is raised with unsupported type."""
    with pytest.raises(ValueError):
        _convert_python_dtypes_to_pandas_dtypes(set, "col_name")


@unit_test
def test_convert_python_dtypes_to_panda_dtypes_error_date_type() -> None:
    """Tests string is returned with date type."""
    dtype = _convert_python_dtypes_to_pandas_dtypes(datetime.date, "col_name")
    assert dtype == pd.StringDtype()


@unit_test
def test_convert_python_dtypes_to_panda_dtypes_error_datetime_type() -> None:
    """Tests string is returned with datetime type."""
    dtype = _convert_python_dtypes_to_pandas_dtypes(datetime.datetime, "col_name")
    assert dtype == pd.StringDtype()


class DataStructureBuilder(Protocol):
    """Callback Protocol for the datastructure_builder fixture."""

    def __call__(
        self,
        table: Optional[Union[str, Mapping[str, str]]] = "main",
        target: Optional[Union[str, List[str]]] = "c",
        ignore_cols: Optional[List[str]] = None,
        selected_cols: Optional[List[str]] = None,
        loss_weights_col: Optional[str] = None,
        multihead_col: Optional[str] = None,
        ignore_classes_col: Optional[str] = None,
        image_cols: Optional[List[str]] = None,
        query_based_ds: bool = False,
        multihead_size: Optional[int] = None,
    ) -> DataStructure:
        """Call signature of the builder fixture."""
        ...


@unit_test
class TestDataStructureSchemaCompatibilityChecking:
    """Tests for the check_datastructure_schema_compatibility function."""

    @fixture(scope="class")
    def data(self) -> Dict[str, List[Any]]:
        """Data to use for the schema."""
        return {"a": [1, 2, 3], "b": [1.0, 2.0, 3.0], "c": ["hello", "world", "hello"]}

    @fixture(scope="class")
    def dataframe(self, data: Dict[str, List[Any]]) -> pd.DataFrame:
        """The DataFrame representation of the data."""
        return pd.DataFrame.from_dict(data)

    @fixture(scope="class")
    def schema(self, dataframe: pd.DataFrame) -> BitfountSchema:
        """Pod Schema generated from the data.

        Uses "main" as the name of the sole table.
        """
        return BitfountSchema(DataFrameSource(dataframe), table_name="main")

    @fixture(scope="class")
    def datastructure_builder(self) -> DataStructureBuilder:
        """Builder function for different forms of DataStructure."""

        def _builder(
            table: Optional[Union[str, Mapping[str, str]]] = "main",
            target: Optional[Union[str, List[str]]] = "c",
            ignore_cols: Optional[List[str]] = None,
            selected_cols: Optional[List[str]] = None,
            loss_weights_col: Optional[str] = None,
            multihead_col: Optional[str] = None,
            ignore_classes_col: Optional[str] = None,
            image_cols: Optional[List[str]] = None,
            query_based_ds: bool = False,
            multihead_size: Optional[int] = None,
        ) -> DataStructure:
            # Query-based fail out fast in compat-check so can just mock out the
            # details
            if query_based_ds:
                return DataStructure(query=Mock(), schema_types_override=Mock())

            # Set defaults if not provided
            if ignore_cols is None:
                ignore_cols = []

            # Set defaults if not provided
            if selected_cols is None:
                selected_cols = ["a", "b"]

            return DataStructure(
                table=table,
                target=target,
                ignore_cols=ignore_cols,
                selected_cols=selected_cols,
                loss_weights_col=loss_weights_col,
                multihead_col=multihead_col,
                ignore_classes_col=ignore_classes_col,
                image_cols=image_cols,
                multihead_size=multihead_size,
            )

        return _builder

    def test_compat_check_works(
        self, datastructure_builder: DataStructureBuilder, schema: BitfountSchema
    ) -> None:
        """Test that COMPATIBLE returned if ds/schema are compatible."""
        compat, msgs = check_datastructure_schema_compatibility(
            datastructure_builder(), schema
        )

        assert compat == DataStructureSchemaCompatibility.COMPATIBLE
        assert not msgs

    def test_query_compat_check_errors(
        self, datastructure_builder: DataStructureBuilder, schema: BitfountSchema
    ) -> None:
        """Test that WARNING returned if ds is query-based."""
        compat, msgs = check_datastructure_schema_compatibility(
            datastructure_builder(query_based_ds=True), schema
        )

        assert compat == DataStructureSchemaCompatibility.WARNING
        assert msgs == ["Warning: Cannot check query compatibility."]

    @pytest.mark.parametrize(
        "data_identifier", (None, "not_main"), ids=lambda x: f"data_id={x}"
    )
    def test_compat_check_missing_data_identifier_errors(
        self,
        data_identifier: Optional[str],
        datastructure_builder: DataStructureBuilder,
        schema: BitfountSchema,
    ) -> None:
        """Test that ERROR returned if ds for "multiple" pods but data_id missing."""
        # DS set up as though multiple pod references (even though just single)
        # and we pass through data_identifiers that aren't in the dict
        compat, msgs = check_datastructure_schema_compatibility(
            datastructure_builder(table={"main": "main"}),
            schema,
            data_identifier=data_identifier,
        )

        assert compat == DataStructureSchemaCompatibility.ERROR
        assert msgs == [
            f"Error: Multiple pods are specified in the datastructure"
            f' but pod "{data_identifier}" was not one of them.'
        ]

    def test_compat_check_missing_table_schema_errors(
        self, datastructure_builder: DataStructureBuilder, schema: BitfountSchema
    ) -> None:
        """Test that ERROR returned if ds requests non-existent table."""
        # Setup DS so we can extract the table name for the target data_identifier
        # but it's the WRONG table name
        compat, msgs = check_datastructure_schema_compatibility(
            datastructure_builder(table={"main": "not_the_right_table_name"}),
            schema,
            data_identifier="main",
        )

        assert compat == DataStructureSchemaCompatibility.ERROR
        assert msgs == [
            "Error: Unable to find the table schema for"
            ' the table name "not_the_right_table_name".'
        ]

    @pytest.mark.parametrize(
        "col_type_attr_map",
        ({"ignore": "ignore_cols"},),
        ids=lambda d: "attrs_referencing_missing_cols=" + ",".join(sorted(d.values())),
    )
    def test_compat_check_missing_ignore_cols_warns(
        self,
        col_type_attr_map: Dict[str, str],
        datastructure_builder: DataStructureBuilder,
        schema: BitfountSchema,
    ) -> None:
        """Test that WARNING returned if ds refs missing cols in "warn" attrs.

        Checks that we only return warning level if the datastructure references
        columns that don't exist but only for uses that are considered "warning"
        level (e.g. ignore_cols) as the task might still be able to run.
        """
        # Set the builder args for the desired column types to reference non-existing
        # columns
        missing_cols = ["d", "e"]
        kwargs: Dict[str, Any] = {v: missing_cols for _, v in col_type_attr_map.items()}

        if "ignore_cols" in kwargs:
            # as can't have both
            kwargs["selected_cols"] = []

        compat, msgs = check_datastructure_schema_compatibility(
            datastructure_builder(**kwargs), schema
        )

        assert compat == DataStructureSchemaCompatibility.WARNING
        assert msgs == [
            f'Warning: Expected "{col_type}" column, "{i}",'
            f" but it could not be found in the data schema."
            for col_type in col_type_attr_map
            for i in missing_cols
        ]

    @pytest.mark.parametrize(
        "col_type_attr_map",
        (
            {"target": "target"},
            {"select": "selected_cols"},
            {"image": "image_cols"},
            {"loss weights": "loss_weights_col"},
            {"multihead": "multihead_col"},
            {"ignore classes": "ignore_classes_col"},
            {
                "target": "target",
                "select": "selected_cols",
            },
        ),
        ids=lambda d: "attrs_referencing_missing_cols=" + ",".join(sorted(d.values())),
    )
    def test_compat_check_missing_error_cols_incompatible(
        self,
        col_type_attr_map: Dict[str, str],
        datastructure_builder: DataStructureBuilder,
        schema: BitfountSchema,
    ) -> None:
        """Test that INCOMPATIBLE returned if ds refs missing cols in "error" attrs.

        Checks that we return incompatible level if the datastructure references
        columns that don't exist for uses that are considered "error" level
        (e.g. target) as the task will not be able to run.
        """
        # Set the builder args for the desired column types to reference non-existing
        # columns
        missing_cols = ["d", "e"]
        kwargs: Dict[str, Any] = {v: missing_cols for _, v in col_type_attr_map.items()}

        if "multihead_col" in kwargs:
            # as needed if multihead_col is specified
            kwargs["multihead_size"] = 1

        compat, msgs = check_datastructure_schema_compatibility(
            datastructure_builder(**kwargs), schema
        )

        assert compat == DataStructureSchemaCompatibility.INCOMPATIBLE
        assert msgs == sorted(
            [
                f'Incompatible: Expected "{col_type}" column, "{col}",'
                f" but it could not be found in the data schema."
                for col_type in col_type_attr_map
                for col in missing_cols
            ]
        )

    def test_compat_check_missing_warning_and_error_cols_incompatible(
        self, datastructure_builder: DataStructureBuilder, schema: BitfountSchema
    ) -> None:
        """INCOMPATIBLE returned if ds refs missing cols in some "error" attrs.

        Checks that we return incompatible level if the datastructure references
        columns that don't exist for uses that are considered "error" level
        (e.g. target) AND also generates some warnings.

        Check that both "incompatible" and "warning" messages are returned.
        """
        # Set the builder args for the desired column types to reference non-existing
        # columns
        col_type_attr_map: Dict[str, str] = {
            "target": "target",
            "image": "image_cols",
            "ignore": "ignore_cols",
        }
        missing_cols = ["d", "e"]
        kwargs: Dict[str, Any] = {v: missing_cols for _, v in col_type_attr_map.items()}

        compat, msgs = check_datastructure_schema_compatibility(
            datastructure_builder(selected_cols=[], **kwargs), schema
        )

        assert compat == DataStructureSchemaCompatibility.INCOMPATIBLE
        assert msgs == sorted(
            [
                f'Incompatible: Expected "{col_type}" column, "{col}",'
                f" but it could not be found in the data schema."
                for col_type in col_type_attr_map
                for col in missing_cols
                if col_type != "ignore"
            ]
        ) + sorted(
            [
                f'Warning: Expected "{col_type}" column, "{i}",'
                f" but it could not be found in the data schema."
                for col_type in col_type_attr_map
                for i in missing_cols
                if col_type == "ignore"
            ]
        )
