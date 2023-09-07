"""Tests model_reference.py module."""
import logging
from pathlib import Path
import sys
from typing import Generator, Type, cast
from unittest.mock import MagicMock

import pytest
from pytest import MonkeyPatch, fixture
from pytest_mock import MockerFixture

import bitfount
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.hub.exceptions import ModelUploadError
from bitfount.hub.utils import hash_file_contents
from bitfount.models.base_models import MAIN_MODEL_REGISTRY
from bitfount.schemas.utils import bf_dump, bf_load
from bitfount.utils import seed_all
from tests.bitfount import TEST_SECURITY_FILES
from tests.utils.helper import create_datastructure, unit_test

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

PUBLIC_KEY_PATH = TEST_SECURITY_FILES / "test_public.testkey"
PRIVATE_KEY_PATH = TEST_SECURITY_FILES / "test_private.testkey"

seed_all(43)


@unit_test
class TestBitfountModelReference:
    """Tests for BitfountModelReference class."""

    @fixture
    def datastructure(self) -> DataStructure:
        """Fixture for datastructure."""
        return create_datastructure()

    @fixture
    def hub(self) -> MagicMock:
        """Hub fixture."""
        hub_mock = MagicMock()
        hub_mock.send_model.return_value = True
        hub_mock.username = "test_username"
        return hub_mock

    @fixture
    def model_ref(
        self,
        bitfount_model_correct_structure: str,
        datastructure: DataStructure,
        hub: MagicMock,
        tmp_path: Path,
    ) -> Generator[BitfountModelReference, None, None]:
        """A BitfountModelReference for use in tests with ref as path."""
        model_file = tmp_path / "MyModel.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)

        model_ref = BitfountModelReference(
            username="test",
            datastructure=datastructure,
            schema=BitfountSchema(),
            model_ref=model_file,
            hub=hub,
            hyperparameters={"param1": 1, "param2": 2},
        )
        yield model_ref

    def test_username_is_taken_from_hub_if_none_provided(
        self,
        bitfount_model_correct_structure: str,
        datastructure: DataStructure,
        tmp_path: Path,
    ) -> None:
        """Tests that the username is taken from hub if none provided."""
        model_file = tmp_path / "MyModel.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)
        hub_mock = MagicMock()
        hub_mock.username = "test"
        hub_mock.send_model.return_value = True
        model_ref = BitfountModelReference(
            datastructure=datastructure,
            schema=BitfountSchema(),
            model_ref=model_file,
            hub=hub_mock,
            hyperparameters={"param1": 1, "param2": 2},
        )
        assert model_ref.username == "test"

    @pytest.mark.parametrize(
        argnames=("cli_mode", "expected_exc"),
        argvalues=((True, SystemExit), (False, ModelUploadError)),
    )
    def test_get_model_model_sending_unsuccessful(
        self,
        cli_mode: bool,
        expected_exc: Type[BaseException],
        model_ref: BitfountModelReference,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Tests exception raised if method upload fails."""
        # Set _BITFOUNT_CLI_MODE config variable to elicit different error handling
        monkeypatch.setattr(bitfount.config, "_BITFOUNT_CLI_MODE", cli_mode)

        # Make hub.send_model raise a exception
        model_ref.hub = cast(MagicMock, model_ref.hub)
        model_ref.hub.send_model.side_effect = ModelUploadError("ERROR")

        with pytest.raises(expected_exc, match="ERROR"):
            model_ref.get_model()

        model_ref.hub.send_model.assert_called_once()

    def test_get_model_correctly(self, model_ref: BitfountModelReference) -> None:
        """Tests model uploaded and model class retrieved."""
        model_ref.hub = cast(MagicMock, model_ref.hub)
        model_class = model_ref.get_model()
        assert model_class is not None
        assert isinstance(model_class, type)  # i.e. is a class, not an instance
        model_ref.hub.send_model.assert_called_once()

    def test_get_model_as_string(self, model_ref: BitfountModelReference) -> None:
        """Tests model retrieval if model ref is a str."""
        model_ref.hub = cast(MagicMock, model_ref.hub)
        model_ref.hub.get_model.return_value = object
        model_ref.model_ref = "MyModel"
        model_class = model_ref.get_model()
        assert model_class is not None
        assert isinstance(model_class, type)
        model_ref.hub.get_model.assert_called_once()
        model_ref.hub.send_model.assert_not_called()

    def test_get_model_not_recognised(self, model_ref: BitfountModelReference) -> None:
        """Tests exception raised if model ref isn't path or str."""
        model_ref.hub = cast(MagicMock, model_ref.hub)
        model_ref.model_ref = 1123  # type: ignore[assignment]  # Reason: this is the purpose of the test  # noqa: B950
        with pytest.raises(TypeError):
            model_ref.get_model()
        model_ref.hub.send_model.assert_not_called()

    def test_get_model_with_model_that_doesnt_implement_distributed_model_protocol(
        self,
        bitfount_model_incorrect_structure: str,
        mocker: MockerFixture,
        model_ref: BitfountModelReference,
    ) -> None:
        """Tests model not implementing `DistributedModelProtocol` raises TypeError.

        Also ensures that the model doesn't get uploaded to the Hub.
        """
        mock_upload_model_to_hub = mocker.patch.object(
            model_ref, "_upload_model_to_hub"
        )
        assert isinstance(model_ref.model_ref, Path)
        model_ref.model_ref.write_text(bitfount_model_incorrect_structure)
        with pytest.raises(
            TypeError,
            match="Model MyModel does not implement DistributedModelProtocol.",
        ):
            model_ref.get_model()
        mock_upload_model_to_hub.assert_not_called()

    def test_serialize_deserialize(
        self, mocker: MockerFixture, model_ref: BitfountModelReference
    ) -> None:
        """Checks that model reference serialization and deserialization works."""
        # Pre-serialization asserts
        assert model_ref.hub is not None
        assert isinstance(model_ref.model_ref, Path)
        assert model_ref.hyperparameters == {"param1": 1, "param2": 2}

        # Serialization asserts
        dumped = bf_dump(model_ref)
        assert "hub" not in dumped

        with mocker.patch(
            "bitfount.federated.model_reference._default_bitfounthub",
            return_value=model_ref.hub,
        ):
            # Post-deserialization asserts
            loaded = bf_load(dumped, MAIN_MODEL_REGISTRY)
            assert isinstance(loaded.model_ref, str)
            assert loaded.model_ref == "MyModel"
            assert model_ref.username == loaded.username
            assert model_ref.hyperparameters == loaded.hyperparameters

    #
    def test_serialize_deserialize_set_hub_value_works_correctly(
        self, mocker: MockerFixture, model_ref: BitfountModelReference
    ) -> None:
        """Checks that hub attribute is not serialized and is set correctly."""
        # Serialization asserts
        dumped = bf_dump(model_ref)
        assert "hub" not in dumped

        mock_hub = mocker.patch(
            "bitfount.federated.model_reference._default_bitfounthub"
        )

        # Post-deserialization asserts
        bf_load(dumped, MAIN_MODEL_REGISTRY)
        mock_hub.assert_called_once()

    def test_serialization_deserialization_of_model_name_ref(
        self, mocker: MockerFixture, model_ref: BitfountModelReference
    ) -> None:
        """Tests serialization of model when contains model name, not path."""
        model_str = "ModelClassName"
        model_ref.model_ref = model_str  # explicitly set as class name str

        # Serialization asserts - model_ref unchanged
        dumped = bf_dump(model_ref)
        assert dumped["model_ref"] == model_str
        assert "hub" not in dumped

        with mocker.patch("bitfount.federated.model_reference._default_bitfounthub"):
            # Post-deserialization asserts
            loaded = bf_load(dumped, MAIN_MODEL_REGISTRY)
            assert loaded.model_ref == model_str

    @pytest.mark.parametrize(
        "ref_str", ["MyModel.py", "/home/MyModel.py", "/home/MyModel"]
    )
    def test_serialization_of_incorrect_model_ref_fails(
        self, model_ref: BitfountModelReference, ref_str: str
    ) -> None:
        """Tests exception raised if model reference isn't a path.

        Tests with:
            - Basic file name as a string
            - Fuller file path as a string
            - Fuller file path ending in potential class name
        """
        model_ref.model_ref = ref_str  # looks like a path but is a string
        with pytest.raises(
            TypeError,
            match="Unable to serialise model_ref; "
            "expected python file path Path or model name str, "
            f"got <class 'str'> with value {ref_str}",
        ):
            bf_dump(model_ref)

    def test_empty_hyperparameters(
        self, datastructure: DataStructure, mocker: MockerFixture
    ) -> None:
        """Tests an empty dict of hyperparameters is created if none are specified."""
        with mocker.patch("bitfount.federated.model_reference._default_bitfounthub"):
            bfmr = BitfountModelReference(
                model_ref="test",
                datastructure=datastructure,
                schema=BitfountSchema(),
                username="test",
            )
            assert bfmr.hyperparameters == {}

    def test_model_is_uploaded_if_hash_no_match(
        self,
        datastructure: DataStructure,
        mocker: MockerFixture,
        model_ref: BitfountModelReference,
    ) -> None:
        """Tests that model is uploaded if hash returned from hub doesn't match."""
        model_ref.hub._get_model_response.return_value = {  # type:ignore[attr-defined]
            "modellerName": "username",
            "modelName": "blah",
            "modelHash": "nice_hash",
            "model_version": 1,
        }

        mock_upload = mocker.patch.object(model_ref, "_upload_model_to_hub")
        model_ref.get_model()
        mock_upload.assert_called_once()

    def test_model_is_uploaded_if_model_not_on_hub(
        self,
        datastructure: DataStructure,
        mocker: MockerFixture,
        model_ref: BitfountModelReference,
    ) -> None:
        """Tests that model is uploaded if None returned from hub."""

        model_ref.hub._get_model_response.return_value = (  # type:ignore[attr-defined]
            None
        )

        mock_upload = mocker.patch.object(model_ref, "_upload_model_to_hub")
        model_ref.get_model()
        mock_upload.assert_called_once()

    def test_model_is_uploaded_if_new_version_true(
        self,
        datastructure: DataStructure,
        mocker: MockerFixture,
        model_ref: BitfountModelReference,
    ) -> None:
        """Tests that model is uploaded if new_version set to True."""
        model_ref.new_version = True
        hash = hash_file_contents(model_ref.model_ref)  # type:ignore[arg-type]
        model_ref.hub._get_model_response.return_value = {  # type:ignore[attr-defined]
            "modellerName": "username",
            "modelName": "blah",
            "modelHash": hash,
            "model_version": 1,
        }

        mock_upload = mocker.patch.object(model_ref, "_upload_model_to_hub")
        model_ref.get_model()
        mock_upload.assert_called_once()

    def test_model_is_not_uploaded_if_hashes_match(
        self,
        datastructure: DataStructure,
        mocker: MockerFixture,
        model_ref: BitfountModelReference,
    ) -> None:
        """Tests that model is uploaded if new_version set to True."""
        hash = hash_file_contents(model_ref.model_ref)  # type:ignore[arg-type]
        model_ref.hub._get_model_response.return_value = {  # type:ignore[attr-defined]
            "modellerName": "username",
            "modelName": "blah",
            "modelHash": hash,
            "model_version": 1,
        }

        mock_upload = mocker.patch.object(model_ref, "_upload_model_to_hub")
        model_ref.get_model()
        mock_upload.assert_not_called()

    def test_send_weights(
        self, mocker: MockerFixture, model_ref: BitfountModelReference, tmp_path: Path
    ) -> None:
        """Test BitfountModelReference.send_weights is called on correct invocation."""
        model_ref.model_version = 1
        mock_send_weights = mocker.patch.object(model_ref.hub, "send_weights")
        model_ref.send_weights(tmp_path)

        mock_send_weights.assert_called_once()

    def test_send_weights_fails_without_model_version(
        self, model_ref: BitfountModelReference, tmp_path: Path
    ) -> None:
        """Test send_weigths throws error without model version."""
        with pytest.raises(
            ValueError,
            match="You must specify model_version in BitfountModelReference "
            "constructor to upload model weights file.",
        ):
            model_ref.send_weights(tmp_path)
