"""Tests for the BitfountAM and BitfountHub API calls."""
import base64
from datetime import datetime, timezone
import inspect
import json
import logging
from pathlib import Path
import re
from typing import List, Optional, Type, Union, cast
from unittest.mock import Mock, PropertyMock

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import pytest
from pytest import LogCaptureFixture, MonkeyPatch, fixture
from pytest_lazyfixture import lazy_fixture
from pytest_mock import MockerFixture
import requests
from requests import HTTPError, RequestException
from requests.exceptions import InvalidJSONError
import responses
from responses.matchers import json_params_matcher, query_param_matcher

from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.types import SerializedProtocol, _PodResponseType
from bitfount.hub.api import (
    _DEV_AM_URL,
    _MAX_CUSTOM_MODEL_SIZE_BYTES,
    _MAX_CUSTOM_MODEL_SIZE_MEGABYTES,
    _MAX_SCHEMA_SIZE_BYTES,
    _MAX_SCHEMA_SIZE_MEGABYTES,
    _MAX_WEIGHTS_SIZE_BYTES,
    _MAX_WEIGHTS_SIZE_MEGABYTES,
    _STAGING_AM_URL,
    PRODUCTION_AM_URL,
    BitfountAM,
    BitfountHub,
    PodPublicMetadata,
    _check_pod_id_details,
    hash_file_contents,
)
from bitfount.hub.authentication_flow import BitfountSession
from bitfount.hub.exceptions import ModelUploadError, SchemaUploadError
from bitfount.hub.types import (
    _AccessManagerKeyResponseJSON,
    _AMAccessCheckResponseJSON,
    _HubFailureResponseJSON,
    _HubSuccessResponseJSON,
    _ModelDetailsResponseJSON,
    _ModelUploadResponseJSON,
    _MonitorPostJSON,
    _MultiModelDetailsResponseJSON,
    _MultiPodDetailsResponseJSON,
    _OIDCAccessCheckPostJSON,
    _PodDetailsResponseJSON,
    _PublicKeyJSON,
    _SAMLAdditionalInfoPOSTJSON,
    _SAMLChallengeResponseJSON,
    _SignatureBasedAccessCheckPostJSON,
    _UserRSAPublicKeysResponseJSON,
)
from bitfount.models.bitfount_model import BitfountModel
from bitfount.storage import _get_packed_data_object_size
from bitfount.types import (
    BaseDistributedModelProtocol,
    _JSONDict,
    _S3PresignedPOSTFields,
    _S3PresignedPOSTURL,
    _S3PresignedURL,
    _SAMLResponse,
)
from bitfount.utils import (
    _get_mb_from_bytes,
    _get_non_abstract_classes_from_module,
    web_utils,
)
from tests.utils import PytestRequest
from tests.utils.helper import (
    get_debug_logs,
    get_error_logs,
    get_warning_logs,
    integration_test,
    unit_test,
)

# This forces `requests` to make IPv4 connections
# TODO: [BIT-1443] Remove this once Hub/AM support IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False  # type: ignore[attr-defined] # Reason: see above # noqa: B950


def sign_message(message: bytes, private_key: RSAPrivateKey) -> bytes:
    """Signs provided `message` with provided `private_key` and returns signature."""
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=20  # padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )

    return signature


@fixture
def pod_namespace() -> str:
    """Pod namespace information."""
    return "pod_namespace"


@fixture
def pod_name() -> str:
    """Pod name information."""
    return "pod_name"


@fixture
def pod_identifier(pod_name: str, pod_namespace: str) -> str:
    """Pod identifier information."""
    return f"{pod_namespace}/{pod_name}"


@unit_test
class TestBitfountHub:
    """Tests for the BitfountHub API."""

    # START OF FIXTURES #
    @fixture
    def good_pod(self, s3_download_url: _S3PresignedURL) -> _PodDetailsResponseJSON:
        """JSON response for a good get pod."""
        return {
            "podIdentifier": "123e4567-e89b-12d3-a456-426614174000",
            "podName": "blahhh",
            "podDisplayName": "None",
            "podPublicKey": "None",
            "accessManagerPublicKey": "None",
            "description": "None",
            "schemaStorageKey": "None",
            "isOnline": True,
            "providerUserName": "username",
            "visibility": "public",
            # This is appended if schemaStorageKey is not null. For our tests
            # we attach it regardless.
            "schemaDownloadUrl": s3_download_url,
        }

    @fixture
    def good_pods(self) -> List[_MultiPodDetailsResponseJSON]:
        """JSON response for get all pods.

        Matches the return value of getAllPods() in
        bitfount-web/bf-packages/bitfount-hub/modules/model/pods.js
        """
        return [
            {
                "podIdentifier": "123e4567-e89b-12d3-a456-426614174000",
                "name": "blahhh",
                "podDisplayName": "None",
                "isOnline": True,
                "podPublicKey": "None",
                "accessManagerPublicKey": "None",
                "description": "None",
                "providerUserName": "username",
                "podPagePath": "username/blahhh",
            }
        ]

    @fixture
    def model_missing_implementations(self) -> str:
        """Bitfount Model file with still abstract model."""
        return inspect.cleandoc(
            """
            from bitfount.models.bitfount_model import BitfountModel

            class MyModel(BitfountModel):
                pass
            """
        )

    @fixture
    def model_multiple_classes(self) -> str:
        """Bitfount Model file containing multiple classes."""
        return inspect.cleandoc(
            """
            from bitfount.models.bitfount_model import BitfountModel

            class MyModel(BitfountModel):
                def _set_metrics(self, metrics=None):
                    pass

                def serialize(self, filename):
                    pass

                def deserialize(self, filename):
                    pass

                def evaluate(self, test_dl=None):
                    pass

                def fit(self, *args, **kwargs):
                    pass

                def predict(self, *args, **kwargs):
                    pass

                def apply_weight_updates():
                    ...

                def backend_tensor_shim():
                    ...

                def diff_params():
                    ...

                def get_param_states():
                    ...

                def set_model_training_iterations():
                    ...

                def tensor_precision():
                    ...

                def update_params():
                    ...

                def _get_import_statements():
                    ...

                def _get_model():
                    ...

            class MyOtherModel(BitfountModel):
                def _set_metrics(self, metrics=None):
                    pass

                def serialize(self, filename):
                    pass

                def deserialize(self, filename):
                    pass

                def evaluate(self, test_dl=None):
                    pass

                def predict(self, *args, **kwargs):
                    pass

                def fit(self, *args, **kwargs):
                    pass

                def apply_weight_updates():
                    ...

                def backend_tensor_shim():
                    ...

                def diff_params():
                    ...

                def get_param_states():
                    ...

                def set_model_training_iterations():
                    ...

                def tensor_precision():
                    ...

                def update_params():
                    ...

                def _get_import_statements():
                    ...

                def _get_model():
                    ...
            """
        )

    @fixture
    def good_models_response(self) -> List[_MultiModelDetailsResponseJSON]:
        """Good model details in format for multiple models as fixture."""
        return [
            {
                "modellerName": "username",
                "modelName": "blah",
                "modelStorageKey": "nice_hash",
                "modelVersion": 1,
            },
        ]

    @fixture
    def good_model_response(
        self,
        bitfount_model_correct_structure: str,
        s3_download_url: _S3PresignedURL,
        tmp_path: Path,
    ) -> _ModelDetailsResponseJSON:
        """Good model code and correct hash as fixture."""
        model_file = tmp_path / "model.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)
        return {
            "modelDownloadUrl": s3_download_url,
            "modelHash": hash_file_contents(model_file),
            "modelVersion": 1,
        }

    @fixture
    def good_model_response_w_weights(
        self,
        bitfount_model_correct_structure: str,
        s3_download_url: _S3PresignedURL,
        tmp_path: Path,
    ) -> _ModelDetailsResponseJSON:
        """Good model code and correct hash as fixture."""
        model_file = tmp_path / "model.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)
        return {
            "modelDownloadUrl": s3_download_url,
            "modelHash": hash_file_contents(model_file),
            "weightsDownloadUrl": s3_download_url,
            "modelVersion": 1,
        }

    @fixture
    def json_success(self) -> _HubSuccessResponseJSON:
        """Hub success message in JSON format as fixture."""
        return {
            "success": True,
            "message": "No message",
        }

    @fixture
    def json_failure(self) -> _HubFailureResponseJSON:
        """Hub failure message in JSON format as fixture."""
        return {
            "success": False,
            "errorMessage": "Error",
        }

    @fixture
    def username(self) -> str:
        """Fake username for auth session."""
        return "session_username"

    @fixture
    def hub_url(self) -> str:
        """Test hub URL as fixture."""
        return "http://test.bitfount.com"

    @fixture
    def hub(
        self, hub_url: str, mocker: MockerFixture, tmp_path: Path, username: str
    ) -> BitfountHub:
        """A BitfountHub instance as fixture."""
        session = BitfountSession()
        # Patch authenticated, username and user_storage_path onto session
        mocker.patch.object(
            type(session), "authenticated", PropertyMock(return_value=True)
        )
        mocker.patch.object(
            type(session), "username", PropertyMock(return_value=username)
        )

        # Treat this as a BitfountSession for these tests
        return BitfountHub(session, hub_url)

    @fixture
    def schema_json(self) -> _JSONDict:
        """Dictionary view of a false schema."""
        return {"I": "am", "a": "pod schema"}

    @fixture
    def schema_size(self, schema_json: _JSONDict) -> int:
        """Returns the object upload size of the schema."""
        return _get_packed_data_object_size(schema_json)

    @fixture
    def public_metadata(
        self, pod_name: str, schema_json: _JSONDict
    ) -> PodPublicMetadata:
        """Pod public metadata as fixture."""
        return PodPublicMetadata(
            pod_name,
            "pod_display_name",
            "pod_description",
            schema_json,
        )

    # END OF FIXTURES #

    def test_issubclass_check_for_correctly_structured_bitfount_model(
        self, bitfount_model_correct_structure: str, tmp_path: Path
    ) -> None:
        """Tests that the bitfount model is correctly structured.

        And that the issubclass protocol check picks this up correctly.
        """
        model_name = "MyModel"
        model_file = tmp_path / f"{model_name}.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)
        model_cls = _get_non_abstract_classes_from_module(model_file)[model_name]
        assert issubclass(model_cls, BaseDistributedModelProtocol)

    def test_issubclass_check_for_incorrectly_structured_bitfount_model(
        self, bitfount_model_incorrect_structure: str, tmp_path: Path
    ) -> None:
        """Tests that the bitfount model is incorrectly structured.

        And that the issubclass protocol check picks this up correctly.
        """
        model_name = "MyModel"
        model_file = tmp_path / f"{model_name}.py"
        model_file.touch()
        model_file.write_text(bitfount_model_incorrect_structure)
        model_cls = _get_non_abstract_classes_from_module(model_file)[model_name]
        assert not issubclass(model_cls, BaseDistributedModelProtocol)

    def test_create_hub_without_bitfount_session(self, mocker: MockerFixture) -> None:
        """Tests that BitfountSession is created under the hood if not provided."""
        mock_session = Mock(
            spec=BitfountSession,
            authenticated=False,
            user_storage_path="",
            username="",
            authentication_handler=Mock(),
        )
        mocker.patch("bitfount.hub.api.BitfountSession", return_value=mock_session)
        hub = BitfountHub()
        mock_session.authenticate.assert_called_once()
        assert isinstance(hub.session, BitfountSession)

    @pytest.mark.parametrize(
        argnames=["pod_identifier_", "pod_name_", "pod_namespace_"],
        argvalues=[
            [lazy_fixture("pod_identifier"), None, None],
            [None, lazy_fixture("pod_name"), lazy_fixture("pod_namespace")],
        ],
    )
    @responses.activate
    def test_get_pod(
        self,
        good_pod: _PodDetailsResponseJSON,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
        # We use these names to avoid recursive parameterisation issues due to the
        # parametrize() call above.
        pod_identifier_: str,
        pod_name_: str,
        pod_namespace_: str,
    ) -> None:
        """Test Hub.get_pod() can retrieve pod details."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            json=good_pod,
        )

        pod_details = hub.get_pod(pod_identifier_, pod_namespace_, pod_name_)

        assert pod_details == good_pod

    @pytest.mark.parametrize(
        argnames=["pod_identifier_", "pod_name_", "pod_namespace_"],
        argvalues=[
            [lazy_fixture("pod_identifier"), None, None],
            [None, lazy_fixture("pod_name"), lazy_fixture("pod_namespace")],
        ],
    )
    @responses.activate
    def test_get_pod_request_exception(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
        # We use these names to avoid recursive parameterisation issues due to the
        # parametrize() call above.
        pod_identifier_: str,
        pod_name_: str,
        pod_namespace_: str,
    ) -> None:
        """Test Hub.get_pod() returns None if RequestException is encountered."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            body=RequestException("TEST"),
        )

        pod_details = hub.get_pod(pod_identifier_, pod_namespace_, pod_name_)

        # Pod details should be None due to exception
        assert pod_details is None
        # Check call was made
        assert responses.assert_call_count(f"{hub_url}/api/pods/{pod_identifier}", 1)
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Bitfount Hub connection failed with: TEST" in error_logs

    @pytest.mark.parametrize("status_code", (400, 404, 500))
    @pytest.mark.parametrize(
        argnames=["pod_identifier_", "pod_name_", "pod_namespace_"],
        argvalues=[
            [lazy_fixture("pod_identifier"), None, None],
            [None, lazy_fixture("pod_name"), lazy_fixture("pod_namespace")],
        ],
    )
    @responses.activate
    def test_get_pod_bad_response(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
        remove_web_retry_backoff_sleep: Optional[Mock],
        status_code: int,
        # We use these names to avoid recursive parameterisation issues due to the
        # parametrize() call above.
        pod_identifier_: Optional[str],
        pod_name_: Optional[str],
        pod_namespace_: Optional[str],
    ) -> None:
        """Test Hub.get_pod() returns None if a non-OK response is returned."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            status=status_code,
        )

        pod_details = hub.get_pod(pod_identifier_, pod_namespace_, pod_name_)

        # Pod details should be None due to exception
        assert pod_details is None
        # Check call/retries were made
        expected_url_calls = 1
        if status_code in web_utils._RETRY_STATUS_CODES:
            expected_url_calls += web_utils._DEFAULT_MAX_RETRIES
        assert responses.assert_call_count(
            f"{hub_url}/api/pods/{pod_identifier}", expected_url_calls
        )
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert f"Bitfount Hub connection failed with: {status_code}" in error_logs

        # Check retries occurred if expected
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_web_retry_backoff_sleep.call_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            remove_web_retry_backoff_sleep.assert_not_called()

    @pytest.mark.parametrize(
        argnames=["pod_identifier_", "pod_name_", "pod_namespace_"],
        argvalues=[
            [lazy_fixture("pod_identifier"), None, None],
            [None, lazy_fixture("pod_name"), lazy_fixture("pod_namespace")],
        ],
    )
    @responses.activate
    def test_get_pod_bad_json(
        self,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
        # We use these names to avoid recursive parameterisation issues due to the
        # parametrize() call above.
        pod_identifier_: Optional[str],
        pod_name_: Optional[str],
        pod_namespace_: Optional[str],
    ) -> None:
        """Test Hub.get_pod() raises an exception if no JSON in response."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            body="NOT_JSON",
        )

        with pytest.raises(InvalidJSONError, match="Invalid JSON response "):
            hub.get_pod(pod_identifier_, pod_namespace_, pod_name_)

        # Check call was made
        assert responses.assert_call_count(f"{hub_url}/api/pods/{pod_identifier}", 1)

    @pytest.mark.parametrize(
        argnames=["pod_identifier_", "pod_name_", "pod_namespace_"],
        argvalues=[
            [lazy_fixture("pod_identifier"), None, None],
            [None, lazy_fixture("pod_name"), lazy_fixture("pod_namespace")],
        ],
    )
    @responses.activate
    def test_get_pod_key(
        self,
        good_pod: _PodDetailsResponseJSON,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
        # We use these names to avoid recursive parameterisation issues due to the
        # parametrize() call above.
        pod_identifier_: Optional[str],
        pod_name_: Optional[str],
        pod_namespace_: Optional[str],
    ) -> None:
        """Checks get pod key works correctly."""
        # Change pod key to other value
        good_pod["podPublicKey"] = "KEY"

        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            json=good_pod,
        )

        key = hub.get_pod_key(pod_identifier_, pod_namespace_, pod_name_)

        assert key == "KEY"

    @pytest.mark.parametrize(
        argnames=["pod_identifier_", "pod_name_", "pod_namespace_"],
        argvalues=[
            [lazy_fixture("pod_identifier"), None, None],
            [None, lazy_fixture("pod_name"), lazy_fixture("pod_namespace")],
        ],
    )
    @responses.activate
    def test_get_pod_key_request_exception(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
        # We use these names to avoid recursive parameterisation issues due to the
        # parametrize() call above.
        pod_identifier_: Optional[str],
        pod_name_: Optional[str],
        pod_namespace_: Optional[str],
    ) -> None:
        """Checks get pod key handles RequestException during request."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            body=RequestException("TEST"),
        )

        key = hub.get_pod_key(pod_identifier_, pod_namespace_, pod_name_)

        # Returned value is empty if exception occurred
        assert key is None
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Bitfount Hub connection failed with: TEST" in error_logs

    @pytest.mark.parametrize(
        argnames=["pod_identifier_", "pod_name_", "pod_namespace_"],
        argvalues=[
            [lazy_fixture("pod_identifier"), None, None],
            [None, lazy_fixture("pod_name"), lazy_fixture("pod_namespace")],
        ],
    )
    @responses.activate
    def test_get_pod_key_bad_json(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
        # We use these names to avoid recursive parameterisation issues due to the
        # parametrize() call above.
        pod_identifier_: Optional[str],
        pod_name_: Optional[str],
        pod_namespace_: Optional[str],
    ) -> None:
        """Checks get pod key raises HTTPError when passed bad JSON."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            body="NOT_JSON",
        )

        with pytest.raises(InvalidJSONError, match="Invalid JSON response "):
            hub.get_pod(pod_identifier_, pod_namespace_, pod_name_)

        # Check call was made
        assert responses.assert_call_count(f"{hub_url}/api/pods/{pod_identifier}", 1)

    @pytest.mark.parametrize(
        argnames=["pod_identifier_", "pod_name_", "pod_namespace_"],
        argvalues=[
            [lazy_fixture("pod_identifier"), None, None],
            [None, lazy_fixture("pod_name"), lazy_fixture("pod_namespace")],
        ],
    )
    @responses.activate
    def test_get_pod_key_no_key_in_json(
        self,
        caplog: LogCaptureFixture,
        good_pod: _PodDetailsResponseJSON,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
        # We use these names to avoid recursive parameterisation issues due to the
        # parametrize() call above.
        pod_identifier_: Optional[str],
        pod_name_: Optional[str],
        pod_namespace_: Optional[str],
    ) -> None:
        """Checks get pod key returns empty string if no key in JSON."""
        # Remove public key field from response
        good_pod.pop("podPublicKey")  # type: ignore[misc] # Reason: this is the test purpose # noqa: B950

        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            json=good_pod,
        )

        key = hub.get_pod_key(pod_identifier_, pod_namespace_, pod_name_)

        # Key should be None
        assert key is None
        # Check call was made
        assert responses.assert_call_count(f"{hub_url}/api/pods/{pod_identifier}", 1)
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Response JSON contained no public key: " in error_logs

    @responses.activate
    def test_get_all_pods_success(
        self,
        good_pods: List[_MultiPodDetailsResponseJSON],
        hub: BitfountHub,
        hub_url: str,
    ) -> None:
        """Checks get pods works correctly."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods",
            json=good_pods,
        )

        results = hub.get_all_pods()

        # Should only find a single pod
        assert results == good_pods
        # Check that correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/pods", 1)

    @responses.activate
    def test_get_all_models_success(
        self,
        good_models_response: List[_MultiModelDetailsResponseJSON],
        hub: BitfountHub,
        hub_url: str,
    ) -> None:
        """Checks get models works correctly."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/models",
            json=good_models_response,
        )

        results = hub.get_all_models()

        # Should only return the single model
        assert results == good_models_response
        # Check that correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/models", 1)

    @responses.activate
    def test_get_all_pods_failure(
        self, caplog: LogCaptureFixture, hub: BitfountHub, hub_url: str
    ) -> None:
        """Checks empty list returned if get pods raises exception."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods",
            body=RequestException("TEST"),
        )

        results = hub.get_all_pods()

        # Check that correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/pods", 1)
        # Returned value is empty if exception occurred
        assert len(results) == 0
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Bitfount Hub connection failed with: TEST" in error_logs

    @responses.activate
    def test_get_all_models_failure(
        self, caplog: LogCaptureFixture, hub: BitfountHub, hub_url: str
    ) -> None:
        """Checks empty list returned if get models raises exception."""
        responses.add(
            responses.GET,
            f"{hub_url}/api/models",
            body=RequestException("TEST"),
        )

        results = hub.get_all_models()

        # Check that correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/models", 1)
        # Returned value is empty if exception occurred
        assert len(results) == 0
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Bitfount Hub connection failed with: TEST" in error_logs

    @responses.activate
    def test_send_model_success(
        self,
        bitfount_model_correct_structure: str,
        bitfount_model_correct_structure_size: int,
        hub: BitfountHub,
        hub_url: str,
        mock_s3_file_upload_in_api_module: Mock,
        mocker: MockerFixture,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        tmp_path: Path,
    ) -> None:
        """Checks send model works correctly."""
        model_name = "MyModel"
        model_file = tmp_path / f"{model_name}.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)
        mock_hash = mocker.patch("bitfount.hub.api.hash_file_contents")
        file_hash = "file_hash"
        mock_hash.return_value = file_hash

        # Create fake hub response
        model_upload_response: _ModelUploadResponseJSON = {
            "uploadUrl": s3_upload_url,
            "uploadFields": s3_upload_fields,
            "success": True,
            "errorMessage": "None",
            "alreadyExisted": False,
            "version": 1,
        }

        responses.add(
            responses.POST,
            f"{hub_url}/api/models",
            json=model_upload_response,
            match=[
                json_params_matcher(
                    {
                        "modelName": model_name,
                        "modelSize": bitfount_model_correct_structure_size,
                        "modelHash": file_hash,
                        "privateModel": False,
                    }
                )
            ],
        )

        hub.send_model(model_file)

        # Check that correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/models", 1)
        # Check upload call was made to S3 correctly
        mock_s3_file_upload_in_api_module.assert_called_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            file_contents=bitfount_model_correct_structure.encode("utf-8"),
            file_name=model_file.name,
        )

    @responses.activate
    def test_send_model_fails_too_large(
        self, hub: BitfountHub, mocker: MockerFixture
    ) -> None:
        """Tests that send_model() fails if the model file is too large."""
        # Mock out model verification so it will pass
        mocker.patch.object(hub, "_verify_bitfount_model_format")
        mock_hash = mocker.patch("bitfount.hub.api.hash_file_contents")

        # Create mock file path and set the "content" to be slightly too big
        too_long_size: int = _MAX_CUSTOM_MODEL_SIZE_BYTES + 1
        mock_code_path = Mock()
        mock_code_path.read_text.return_value = "a" * too_long_size

        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Model is too large to upload: expected max "
                f"{_MAX_CUSTOM_MODEL_SIZE_MEGABYTES} megabytes, got "
                f"{_get_mb_from_bytes(too_long_size).fractional} megabytes."
            ),
        ):
            hub.send_model(mock_code_path)

        # Check that call to hub didn't occur before error occurred
        assert not responses.calls
        mock_hash.assert_called_once_with(mock_code_path)

    @responses.activate
    def test_send_model_missing_implementations(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        model_missing_implementations: str,
        tmp_path: Path,
    ) -> None:
        """Checks send fails if model is still abstract."""
        model_file = tmp_path / "MyModel.py"
        model_file.touch()
        model_file.write_text(model_missing_implementations)

        with pytest.raises(ModelUploadError, match="Model incorrectly structured"):
            hub.send_model(model_file)

        # Check that no request was made (should have stopped before this point)
        assert len(responses.calls) == 0
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert (
            "Model incorrectly structured. Error: Subclass of `BitfountModel` "
            "not found in file or is still abstract." in error_logs
        )

    @responses.activate
    def test_send_model_incorrect_format(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        model_multiple_classes: str,
        tmp_path: Path,
    ) -> None:
        """Checks send fails if multiple classes."""
        model_file = tmp_path / "MyModel.py"
        model_file.touch()
        model_file.write_text(model_multiple_classes)

        with pytest.raises(ModelUploadError, match="Model incorrectly structured"):
            hub.send_model(model_file)

        # Check that no request was made (should have stopped before this point)
        assert len(responses.calls) == 0
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert (
            "Model incorrectly structured. Error: Model file contains 2 models. "
            "Must be just 1." in error_logs
        )

    @responses.activate
    def test_send_model_incorrect_name(
        self,
        bitfount_model_correct_structure: str,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        tmp_path: Path,
    ) -> None:
        """Checks send fails if class name and filename don't match."""
        model_file = tmp_path / "NotaMatchingName.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)

        with pytest.raises(ModelUploadError, match="Model incorrectly structured."):
            hub.send_model(model_file)

        # Check that no request was made (should have stopped before this point)
        assert len(responses.calls) == 0
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert (
            "Model incorrectly structured. Error: MyModel != NotaMatchingName. "
            "Model class name must be the same as the filename" in error_logs
        )

    @responses.activate
    def test_send_model_handles_import_error(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        mocker: MockerFixture,
    ) -> None:
        """Checks send fails if unable to import."""
        mocker.patch.object(
            hub,
            "_verify_bitfount_model_format",
            side_effect=ImportError("IMPORT ERROR"),
        )

        with pytest.raises(ModelUploadError, match="Unable to import model."):
            hub.send_model(model_code_path=Mock())

        # Check that no request was made (should have stopped before this point)
        assert len(responses.calls) == 0
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "IMPORT ERROR" in error_logs

    @responses.activate
    def test_send_model_failure(
        self,
        bitfount_model_correct_structure: str,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        json_failure: _HubFailureResponseJSON,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Checks send model handles failure to upload."""
        model_name = "MyModel"
        model_file = tmp_path / f"{model_name}.py"
        mock_hash = mocker.patch("bitfount.hub.api.hash_file_contents")
        file_hash = "file_hash"
        mock_hash.return_value = file_hash
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)

        responses.add(
            responses.POST,
            f"{hub_url}/api/models",
            json=json_failure,
            match=[
                json_params_matcher(
                    {
                        "modelName": model_name,
                        "modelSize": len(
                            bitfount_model_correct_structure.encode("utf-8")
                        ),
                        "modelHash": file_hash,
                        "privateModel": False,
                    }
                )
            ],
        )

        with pytest.raises(
            ModelUploadError,
            match="Failed to upload model details to hub",
        ):
            hub.send_model(model_file)

        # Check that correct request was made (even though it failed))
        assert responses.assert_call_count(f"{hub_url}/api/models", 1)
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert (
            "Could not send model to Bitfount Hub. Failed with message: Error"
            in error_logs
        )

    @responses.activate
    def test_send_model_request_exception(
        self,
        bitfount_model_correct_structure: str,
        bitfount_model_correct_structure_size: int,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Checks request exception handled and logged if raised when sending."""
        model_name = "MyModel"
        model_file = tmp_path / f"{model_name}.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)
        mock_hash = mocker.patch("bitfount.hub.api.hash_file_contents")
        file_hash = "file_hash"
        mock_hash.return_value = file_hash

        responses.add(
            responses.POST,
            f"{hub_url}/api/models",
            body=RequestException("TEST"),
            match=[
                json_params_matcher(
                    {
                        "modelName": model_name,
                        "modelSize": bitfount_model_correct_structure_size,
                        "modelHash": file_hash,
                        "privateModel": False,
                    }
                )
            ],
        )

        with pytest.raises(
            ModelUploadError,
            match="Request exception occurred when uploading model details to hub",
        ):
            hub.send_model(model_file)

        # Check that correct request was made (even though it failed))
        assert responses.assert_call_count(f"{hub_url}/api/models", 1)
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Bitfount Hub connection failed with: TEST" in error_logs

    @pytest.mark.parametrize("s3_exception_cls", (RequestException, HTTPError))
    @responses.activate
    def test_send_model_handles_s3_exception(
        self,
        bitfount_model_correct_structure: str,
        bitfount_model_correct_structure_size: int,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        mock_s3_file_upload_in_api_module: Mock,
        mocker: MockerFixture,
        s3_exception_cls: Type[Exception],
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        tmp_path: Path,
    ) -> None:
        """Checks send model handles an exception when uploading to S3."""
        model_name = "MyModel"
        model_file = tmp_path / f"{model_name}.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)
        mock_hash = mocker.patch("bitfount.hub.api.hash_file_contents")
        file_hash = "file_hash"
        mock_hash.return_value = file_hash

        # Create fake hub response
        model_upload_response: _ModelUploadResponseJSON = {
            "uploadUrl": s3_upload_url,
            "uploadFields": s3_upload_fields,
            "success": True,
            "errorMessage": "None",
            "alreadyExisted": False,
            "version": 1,
        }

        responses.add(
            responses.POST,
            f"{hub_url}/api/models",
            json=model_upload_response,
            match=[
                json_params_matcher(
                    {
                        "modelName": model_name,
                        "modelSize": bitfount_model_correct_structure_size,
                        "modelHash": file_hash,
                        "privateModel": False,
                    }
                )
            ],
        )

        # Add exception to S3 upload
        mock_s3_file_upload_in_api_module.side_effect = s3_exception_cls("S3 ERROR")

        with pytest.raises(ModelUploadError, match="Failed to upload model to S3"):
            hub.send_model(model_file)

        # Check that correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/models", 1)
        # Check upload call was made to S3 correctly
        mock_s3_file_upload_in_api_module.assert_called_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            file_contents=bitfount_model_correct_structure.encode("utf-8"),
            file_name=model_file.name,
        )
        # Check logs
        error_logs = get_error_logs(caplog)
        assert "Failed to upload model to S3: S3 ERROR" in error_logs

    @responses.activate
    def test_send_weights_success(
        self,
        hub: BitfountHub,
        hub_url: str,
        mock_s3_file_upload_in_api_module: Mock,
        mocker: MockerFixture,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        tmp_path: Path,
    ) -> None:
        """Checks send weights works correctly."""
        model_name = "MyModel"
        weights_file = tmp_path / f"{model_name}_weights.pt"
        weights_file.touch()
        weights_contents = b"some bytes"
        weights_file.write_bytes(weights_contents)
        model_version = 1

        # Create fake hub response
        weights_upload_response: _ModelUploadResponseJSON = {
            "success": True,
            "uploadUrl": s3_upload_url,
            "uploadFields": s3_upload_fields,
            "alreadyExisted": False,
            "version": 1,
        }

        responses.add(
            responses.PUT,
            f"{hub_url}/api/models",
            json=weights_upload_response,
            match=[
                json_params_matcher(
                    {
                        "modelName": model_name,
                        "modelVersion": model_version,
                        "weightSize": 10,
                    }
                )
            ],
        )

        hub.send_weights(model_name, model_version, weights_file)

        # Check that correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/models", 1)
        # Check upload call was made to S3 correctly
        mock_s3_file_upload_in_api_module.assert_called_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            file_contents=weights_contents,
            file_name=weights_file.name,
        )

    @responses.activate
    def test_send_weights_fails_too_large(self, hub: BitfountHub) -> None:
        """Tests that send_weights() fails if the weights file is too large."""
        # Create mock file path and set the "content" to be slightly too big
        too_long_size: int = _MAX_WEIGHTS_SIZE_BYTES + 1
        mock_code_path = Mock()
        mock_code_path.read_bytes.return_value = "a" * too_long_size

        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Model weights are too large to upload: expected max "
                f"{_MAX_WEIGHTS_SIZE_MEGABYTES} megabytes, got "
                f"{_get_mb_from_bytes(too_long_size).fractional} megabytes."
            ),
        ):
            hub.send_weights("model_name", 1, mock_code_path)

        # Check that call to hub didn't occur before error occurred
        assert not responses.calls

    @pytest.mark.parametrize("s3_exception_cls", (RequestException, HTTPError))
    @responses.activate
    def test_send_weights_handles_s3_exception(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        mock_s3_file_upload_in_api_module: Mock,
        s3_exception_cls: Type[Exception],
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        tmp_path: Path,
    ) -> None:
        """Checks send weights handles an exception when uploading to S3."""
        model_name = "MyModel"
        weights_file = tmp_path / f"{model_name}_weights.py"
        weights_file.touch()
        content = b"bitfount_model_correct_structure"
        weights_file.write_bytes(content)
        model_version = 1

        # Create fake hub response
        weights_upload_response: _ModelUploadResponseJSON = {
            "success": True,
            "uploadUrl": s3_upload_url,
            "uploadFields": s3_upload_fields,
            "alreadyExisted": False,
            "version": 1,
        }

        responses.add(
            responses.PUT,
            f"{hub_url}/api/models",
            json=weights_upload_response,
            match=[
                json_params_matcher(
                    {
                        "modelName": model_name,
                        "modelVersion": model_version,
                        "weightSize": 32,
                    }
                )
            ],
        )

        # Add exception to S3 upload
        mock_s3_file_upload_in_api_module.side_effect = s3_exception_cls("S3 ERROR")

        with pytest.raises(
            ModelUploadError, match="Failed to upload model weights to S3"
        ):
            hub.send_weights(model_name, 1, weights_file)

        # Check that correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/models", 1)
        # Check upload call was made to S3 correctly
        mock_s3_file_upload_in_api_module.assert_called_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            file_contents=content,
            file_name=weights_file.name,
        )
        # Check logs
        error_logs = get_error_logs(caplog)
        assert "Failed to upload model weights to S3: S3 ERROR" in error_logs

    @responses.activate
    def test_get_weights_success(
        self,
        good_model_response_w_weights: str,
        hub: BitfountHub,
        hub_url: str,
        mock_s3_file_download_in_api_module: Mock,
        s3_download_url: _S3PresignedURL,
    ) -> None:
        """Checks get weights works correctly."""
        # Mock S3 download return value
        model_version = 1
        mock_s3_file_download_in_api_module.return_value = b"weight file"
        url = (
            f"{hub_url}/api/models?modellerName=username&modelName=MyModel"
            f"&modelVersion={model_version}"
        )
        responses.add(
            responses.GET,
            url,
            match_querystring=True,
            json=good_model_response_w_weights,
        )
        weights = hub.get_weights("username", "MyModel", model_version)

        # Returned weights is of correct type
        assert weights is not None
        assert isinstance(weights, bytes)
        # Check correct request was made
        assert responses.assert_call_count(url, 1)
        # Check correct S3 download was made
        mock_s3_file_download_in_api_module.assert_called_once_with(s3_download_url)

    @responses.activate
    def test_get_weights_none_returned(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
    ) -> None:
        """Checks None returned if no weights were found."""
        model_version = 1
        modeller_name = "username"
        model_name = "blah"
        url = (
            f"{hub_url}/api/models?modellerName={modeller_name}"
            f"&modelName={model_name}&modelVersion={model_version}"
        )

        responses.add(
            responses.GET,
            url,
            match_querystring=True,
            json=[],
        )

        response = hub.get_weights("username", "blah", model_version)

        # Check that no model was returned
        assert response is None
        # Check correct request was made
        assert responses.assert_call_count(
            url,
            1,
        )
        # Assert warning message
        warning_logs = get_warning_logs(caplog)
        assert (
            f"No models registered by the name of {model_name} "
            f"from user {modeller_name}" in warning_logs
        )

    @responses.activate
    def test_get_weights_failure(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
    ) -> None:
        """Checks get model handles RequestException being raised."""
        model_version = 1
        url = (
            f"{hub_url}/api/models?modellerName=username&modelName=MyModel"
            "&modelVersion=1"
        )

        responses.add(
            responses.GET,
            url,
            match_querystring=True,
            body=RequestException("TEST"),
        )

        response = hub.get_weights("username", "MyModel", model_version)

        # Check that no model was returned
        assert response is None
        # Check correct request was made
        assert responses.assert_call_count(url, 6)
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Bitfount Hub connection failed with: TEST" in error_logs

    @pytest.mark.parametrize("model_version", [None, 1])
    @pytest.mark.parametrize(
        "model_response",
        ["good_model_response", "good_model_response_w_weights"],
    )
    @responses.activate
    def test_get_model_success(
        self,
        bitfount_model_correct_structure: str,
        hub: BitfountHub,
        hub_url: str,
        mock_s3_file_download_in_api_module: Mock,
        model_response: str,
        model_version: Optional[int],
        request: PytestRequest,
        s3_download_url: _S3PresignedURL,
    ) -> None:
        """Checks get model works correctly."""
        # Mock S3 download return value
        mock_s3_file_download_in_api_module.return_value = (
            bitfount_model_correct_structure
        )
        url = f"{hub_url}/api/models?modellerName=username&modelName=MyModel"
        if model_version:
            url = url + f"&modelVersion={model_version}"

        json: _ModelDetailsResponseJSON = request.getfixturevalue(model_response)
        responses.add(
            responses.GET,
            url,
            match_querystring=True,
            json=json,
        )
        model = hub.get_model("username", "MyModel", model_version)

        # Returned model is of correct type
        assert model is not None
        assert issubclass(model, BitfountModel)
        # Check correct request was made
        assert responses.assert_call_count(url, 1)
        # Check correct S3 download was made
        mock_s3_file_download_in_api_module.assert_called_once_with(
            s3_download_url, encoding="utf-8"
        )

    @pytest.mark.parametrize("model_version", [None, 1])
    @responses.activate
    def test_get_model_none_returned(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        model_version: Optional[int],
    ) -> None:
        """Checks None returned if no model was found."""
        modeller_name = "username"
        model_name = "blah"
        url = (
            f"{hub_url}/api/models?modellerName={modeller_name}&modelName={model_name}"
        )
        if model_version:
            url = url + f"&modelVersion={model_version}"

        responses.add(
            responses.GET,
            url,
            match_querystring=True,
            json=[],
        )

        response = hub.get_model("username", "blah", model_version)

        # Check that no model was returned
        assert response is None
        # Check correct request was made
        assert responses.assert_call_count(
            url,
            1,
        )
        # Assert warning message
        warning_logs = get_warning_logs(caplog)
        assert (
            f"No models registered by the name of {model_name} "
            f"from user {modeller_name}" in warning_logs
        )

    @pytest.mark.parametrize("model_version", [None, 1])
    @responses.activate
    def test_get_model_wrong_json_dict(
        self,
        hub: BitfountHub,
        hub_url: str,
        json_failure: _HubFailureResponseJSON,
        model_version: Optional[int],
    ) -> None:
        """Checks error raised if wrong JSON dict returned.

        Expected inner exception is KeyError.
        """
        modeller_name = "username"
        model_name = "blah"
        url = (
            f"{hub_url}/api/models?modellerName={modeller_name}&modelName={model_name}"
        )
        if model_version:
            url = url + f"&modelVersion={model_version}"

        responses.add(
            responses.GET,
            url,
            match_querystring=True,
            json=json_failure,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(
                f"Cannot retrieve model, no model URL in pod response: {json_failure}"
            ),
        ):
            hub.get_model(modeller_name, model_name, model_version)

    @pytest.mark.parametrize("model_version", [None, 1])
    @responses.activate
    def test_get_model_wrong_json_type(
        self,
        hub: BitfountHub,
        hub_url: str,
        json_failure: _HubFailureResponseJSON,
        model_version: Optional[int],
    ) -> None:
        """Checks error raised if wrong JSON type returned.

        Expected inner exception is TypeError.
        """
        modeller_name = "username"
        model_name = "blah"
        url = (
            f"{hub_url}/api/models?modellerName={modeller_name}&modelName={model_name}"
        )
        if model_version:
            url = url + f"&modelVersion={model_version}"

        responses.add(
            responses.GET,
            url,
            match_querystring=True,
            json=[json_failure],  # list rather than dict
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(
                f"Cannot retrieve model, no model URL in pod response: {[json_failure]}"
            ),
        ):
            hub.get_model(modeller_name, model_name, model_version)

    @pytest.mark.parametrize("model_version", [None, 1])
    @responses.activate
    def test_get_model_failure(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        model_version: Optional[int],
    ) -> None:
        """Checks get model handles RequestException being raised."""
        url = f"{hub_url}/api/models?modellerName=username&modelName=MyModel"
        if model_version:
            url += f"&modelVersion={model_version}"

        responses.add(
            responses.GET,
            url,
            match_querystring=True,
            body=RequestException("TEST"),
        )

        response = hub.get_model("username", "MyModel", model_version)

        # Check that no model was returned
        assert response is None
        # Check correct request was made
        assert responses.assert_call_count(url, 6)
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Bitfount Hub connection failed with: TEST" in error_logs

    @pytest.mark.skip("Reintroduce after [BIT-1073] is implemented.")
    @pytest.mark.parametrize("model_version", [None, 1])
    @responses.activate
    def test_get_model_hash_mismatch_raises_value_error(
        self,
        good_model_response: _ModelDetailsResponseJSON,
        hub: BitfountHub,
        hub_url: str,
        model_version: Optional[int],
    ) -> None:
        """Checks exception raised when model code hash doesn't match."""
        # add a newline to the end of the model code to change hash
        # good_model_response["code"] = good_model_response["code"] + "\n"
        #
        # responses.add(
        #     responses.GET,
        #     f"{hub_url}/api/models?modellerName=username&modelName=MyModel",
        #     match_querystring=True,
        #     json=good_model_response,
        # )
        #
        # with pytest.raises(ValueError):
        #     hub.get_model("username", "MyModel", model_version)
        #
        # # Check correct request was made
        # assert responses.assert_call_count(
        #     f"{hub_url}/api/models?modellerName=username&modelName=MyModel", 1
        # )
        pass

    @responses.activate
    def test_register_pod_success(
        self,
        access_manager_public_key: RSAPublicKey,
        authoriser_public_key: RSAPublicKey,
        hub: BitfountHub,
        hub_url: str,
        mock_s3_data_upload_in_api_module: Mock,
        pod_name: str,
        public_metadata: PodPublicMetadata,
        s3_upload_fields: _S3PresignedPOSTFields,
        s3_upload_url: _S3PresignedPOSTURL,
        schema_size: int,
    ) -> None:
        """Checks pod registration works correctly."""
        pod_public_key_str: str = _RSAEncryption.serialize_public_key(
            authoriser_public_key, form="SSH"
        ).decode("utf-8")
        access_manager_public_key_str: str = _RSAEncryption.serialize_public_key(
            access_manager_public_key, form="SSH"
        ).decode("utf-8")

        responses.add(
            responses.POST,
            f"{hub_url}/api/pods",
            json={
                "success": True,
                "uploadUrl": s3_upload_url,
                "uploadFields": s3_upload_fields,
            },
            match=[
                json_params_matcher(
                    {
                        "name": pod_name,
                        "podPublicKey": pod_public_key_str,
                        "accessManagerPublicKey": access_manager_public_key_str,
                        "podDisplayName": public_metadata.display_name,
                        "description": public_metadata.description,
                        "schemaSize": schema_size,
                    }
                )
            ],
        )

        hub.register_pod(
            public_metadata, authoriser_public_key, access_manager_public_key
        )

        # Check correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/pods", 1)
        # Assert S3 upload was made for schema
        mock_s3_data_upload_in_api_module.assert_called_once_with(
            upload_url=s3_upload_url,
            presigned_fields=s3_upload_fields,
            data=public_metadata.schema,
        )

    @responses.activate
    def test_register_pod_failed(
        self,
        access_manager_public_key: RSAPublicKey,
        authoriser_public_key: RSAPublicKey,
        hub: BitfountHub,
        hub_url: str,
        mock_s3_data_upload_in_api_module: Mock,
        public_metadata: PodPublicMetadata,
    ) -> None:
        """Checks pod registration handles "failed" response from hub."""
        responses.add(
            responses.POST,
            f"{hub_url}/api/pods",
            json={"success": False},
            status=400,
        )

        with pytest.raises(HTTPError, match="Bitfount Hub connection failed with: 400"):
            hub.register_pod(
                public_metadata, authoriser_public_key, access_manager_public_key
            )

        # Check that we haven't attempted to upload the schema
        mock_s3_data_upload_in_api_module.assert_not_called()

    @responses.activate
    def test_register_pod_bad_json(
        self,
        access_manager_public_key: RSAPublicKey,
        authoriser_public_key: RSAPublicKey,
        hub: BitfountHub,
        hub_url: str,
        public_metadata: PodPublicMetadata,
    ) -> None:
        """Checks exception raised on `body`, not `json`, response."""
        non_json_response = "NOT JSON RESPONSE"
        responses.add(
            responses.POST,
            f"{hub_url}/api/pods",
            body=non_json_response,
            status=200,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(f"Invalid JSON response (200): {non_json_response}"),
        ):
            hub.register_pod(
                public_metadata, authoriser_public_key, access_manager_public_key
            )

    def test_register_pod_fails_schema_too_large(
        self,
        access_manager_public_key: RSAPublicKey,
        authoriser_public_key: RSAPublicKey,
        hub: BitfountHub,
        mocker: MockerFixture,
        public_metadata: PodPublicMetadata,
    ) -> None:
        """Tests that exception raised if schema is too large for storage."""
        # Patch out schema size calculation so we can set it
        too_large_size = _MAX_SCHEMA_SIZE_BYTES + 1
        mock_data_sizer = mocker.patch("bitfount.hub.api._get_packed_data_object_size")
        mock_data_sizer.return_value = too_large_size

        with pytest.raises(
            SchemaUploadError,
            match=re.escape(
                "Schema is too large to upload: "
                f"expected max {_MAX_SCHEMA_SIZE_MEGABYTES} megabytes, "
                f"got {_get_mb_from_bytes(too_large_size).fractional} megabytes."
            ),
        ):
            hub.register_pod(
                public_metadata, authoriser_public_key, access_manager_public_key
            )

    @responses.activate
    def test_do_pod_heartbeat_success(
        self,
        authoriser_public_key: RSAPublicKey,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_name: str,
    ) -> None:
        """Checks do_pod_heartbeat correctly."""
        caplog.set_level(logging.DEBUG)

        authoriser_public_key_str = _RSAEncryption.serialize_public_key(
            authoriser_public_key, form="SSH"
        ).decode("utf-8")

        responses.add(
            responses.PATCH,
            f"{hub_url}/api/pods",
            json={"success": True},
            match=[
                json_params_matcher(
                    {"name": pod_name, "podPublicKey": authoriser_public_key_str}
                )
            ],
        )

        hub.do_pod_heartbeat(pod_name, authoriser_public_key)

        # Check correct request was made
        assert responses.assert_call_count(f"{hub_url}/api/pods", 1)
        # Assert debug message
        debug_logs = get_debug_logs(caplog)
        assert "Status ping successful" in debug_logs

    @responses.activate
    def test_do_pod_heartbeat_failed_bad_status_code(
        self,
        authoriser_public_key: RSAPublicKey,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_name: str,
    ) -> None:
        """Test do_pod_heartbeat raises exception on 400+ status code."""
        responses.add(
            responses.PATCH,
            f"{hub_url}/api/pods",
            json={"success": False},
            status=400,
        )

        with pytest.raises(HTTPError, match="400 Client Error: Bad Request for url"):
            hub.do_pod_heartbeat(pod_name, authoriser_public_key)

        # Check request was made
        assert responses.assert_call_count(f"{hub_url}/api/pods", 1)

    @responses.activate
    def test_do_pod_heartbeat_failed_not_ok_status_code(
        self,
        authoriser_public_key: RSAPublicKey,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_name: str,
    ) -> None:
        """Test do_pod_heartbeat skips "failed" (non-200) response from hub."""
        responses.add(
            responses.PATCH,
            f"{hub_url}/api/pods",
            json={"success": False},
            status=201,
        )

        hub.do_pod_heartbeat(pod_name, authoriser_public_key)

        # Check request was made
        assert responses.assert_call_count(f"{hub_url}/api/pods", 1)
        # Assert warning message
        warning_logs = get_warning_logs(caplog)
        assert "Status update failed with (201):" in warning_logs

    @responses.activate
    def test_do_pod_heartbeat_bad_json(
        self,
        authoriser_public_key: RSAPublicKey,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_name: str,
    ) -> None:
        """Checks exception raised on `body`, not `json`, response."""
        non_json_response = "NOT JSON RESPONSE"

        responses.add(
            responses.PATCH,
            f"{hub_url}/api/pods",
            body=non_json_response,
            status=200,
        )

        hub.do_pod_heartbeat(pod_name, authoriser_public_key)

        # Check request was made
        assert responses.assert_call_count(f"{hub_url}/api/pods", 1)
        # Assert warning message
        warning_logs = get_warning_logs(caplog)
        assert f"Invalid JSON response (200): {non_json_response}" in warning_logs

    @responses.activate
    def test_add_pod_handles_http_500_error_when_registering(
        self,
        access_manager_public_key: RSAPublicKey,
        authoriser_public_key: RSAPublicKey,
        hub: BitfountHub,
        hub_url: str,
        json_failure: _HubFailureResponseJSON,
        public_metadata: PodPublicMetadata,
        remove_web_retry_backoff_sleep: Optional[Mock],
    ) -> None:
        """Tests 500 response correctly handled during pod registration."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        responses.add(
            responses.POST,
            f"{hub_url}/api/pods",
            json=json_failure,
            status=500,
        )

        with pytest.raises(
            HTTPError,
            match="Bitfount Hub connection failed with: 500 Server Error",
        ):
            hub.register_pod(
                public_metadata, authoriser_public_key, access_manager_public_key
            )

        # Check retries occurred
        assert (
            remove_web_retry_backoff_sleep.call_count == web_utils._DEFAULT_MAX_RETRIES
        )

    @responses.activate
    def test_add_pod_handles_http_non_200_201_error_when_registering(
        self,
        access_manager_public_key: RSAPublicKey,
        authoriser_public_key: RSAPublicKey,
        hub: BitfountHub,
        hub_url: str,
        json_failure: _HubFailureResponseJSON,
        public_metadata: PodPublicMetadata,
    ) -> None:
        """Tests non-200/201 response correctly handled during pod registration."""
        responses.add(
            responses.POST,
            f"{hub_url}/api/pods",
            json=json_failure,
            status=203,
        )

        with pytest.raises(
            HTTPError,
            match=re.escape(f"Unexpected response (203): {json.dumps(json_failure)}"),
        ):
            hub.register_pod(
                public_metadata, authoriser_public_key, access_manager_public_key
            )

    @responses.activate
    def test_worker_handles_connection_error_when_registering(
        self,
        access_manager_public_key: RSAPublicKey,
        authoriser_public_key: RSAPublicKey,
        hub: BitfountHub,
        public_metadata: PodPublicMetadata,
        remove_web_retry_backoff_sleep: Optional[Mock],
    ) -> None:
        """Checks connection error raised during failed registering."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        # No `response` added, so responses raises a connection error. This is
        # wrapped with the RequestException raised by Hub.
        with pytest.raises(
            requests.exceptions.ConnectionError,
            match="Bitfount Hub connection failed with: Connection refused by",
        ):
            hub.register_pod(
                public_metadata, authoriser_public_key, access_manager_public_key
            )

        # Check retries occurred
        assert (
            remove_web_retry_backoff_sleep.call_count == web_utils._DEFAULT_MAX_RETRIES
        )

    @responses.activate
    def test_get_pod_schema(
        self,
        good_pod: _PodDetailsResponseJSON,
        hub: BitfountHub,
        hub_url: str,
        mock_bitfount_schema_load: Mock,
        mock_s3_data_download_in_api_module: Mock,
        pod_identifier: str,
        schema_json: _JSONDict,
    ) -> None:
        """Test get_pod_schema() works correctly."""
        # Mock out S3 downloading of schema
        mock_s3_data_download_in_api_module.return_value = schema_json

        # Mock request response of pod details
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            json=good_pod,
        )

        schema = hub.get_pod_schema(pod_identifier)

        # Check schema is as expected
        assert schema == schema_json

    @responses.activate
    def test_get_pod_schema_request_exception(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
    ) -> None:
        """Test get_pod_schema() raises exception when RequestException() thrown."""
        # Mock request response of pod details
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            body=RequestException("TEST"),
        )

        with pytest.raises(
            InvalidJSONError,
            match="Cannot retrieve pod schema, no schema URL in pod response: None",
        ):
            hub.get_pod_schema(pod_identifier)

        # Check URL was called
        assert responses.assert_call_count(f"{hub_url}/api/pods/{pod_identifier}", 1)
        # Assert error message
        error_logs = get_error_logs(caplog)
        assert "Bitfount Hub connection failed with: TEST" in error_logs

    @responses.activate
    def test_get_pod_schema_bad_json(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
    ) -> None:
        """Test get_pod_schema() raises exception when bad JSON received."""
        # Mock request response of pod details
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            body="NOT_JSON",
        )

        with pytest.raises(InvalidJSONError, match="Invalid JSON response "):
            hub.get_pod_schema(pod_identifier)

        # Check URL was called
        assert responses.assert_call_count(f"{hub_url}/api/pods/{pod_identifier}", 1)

    @responses.activate
    def test_get_pod_schema_no_schema_url(
        self,
        caplog: LogCaptureFixture,
        good_pod: _PodDetailsResponseJSON,
        hub: BitfountHub,
        hub_url: str,
        pod_identifier: str,
    ) -> None:
        """Test get_pod_schema() raises exception when no download URL in response."""
        # Remove schemaDownloadUrl from pod response
        good_pod.pop("schemaDownloadUrl")  # type: ignore[misc] # Reason: purpose of test # noqa: B950

        # Mock request response of pod details
        responses.add(
            responses.GET,
            f"{hub_url}/api/pods/{pod_identifier}",
            json=good_pod,
        )

        with pytest.raises(
            InvalidJSONError,
            match=f"Cannot retrieve pod schema, no schema URL in pod response: "
            f"{good_pod}",
        ):
            hub.get_pod_schema(pod_identifier)

        # Check URL was called
        assert responses.assert_call_count(f"{hub_url}/api/pods/{pod_identifier}", 1)

    @fixture
    def monitor_update(self) -> _MonitorPostJSON:
        """Example monitor update in JSON format."""
        return {
            "taskId": "task-id",
            "senderId": "sender-mailbox-id",
            "recipientId": "recipient-mailbox-id",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "privacy": "PRIVATE",
            "type": "TASK_STATUS_UPDATE",
            "message": "this is a message",
            "metadata": {"meta": "data"},
            "progress": {"progress": {"value": 1, "total": 10}},
            "resourceUsage": {"a_resource": 10},
        }

    @fixture
    def ingestion_endpoint_url(self, hub_url: str) -> str:
        """Monitor service ingestion endpoint url."""
        return f"{hub_url}/api/ingest"

    @responses.activate
    def test_send_monitor_update(
        self,
        hub: BitfountHub,
        ingestion_endpoint_url: str,
        monitor_update: _MonitorPostJSON,
    ) -> None:
        """Test send_monitor_update works correctly."""
        responses.add(
            responses.POST,
            url=ingestion_endpoint_url,
            status=200,
            match=[json_params_matcher(cast(_JSONDict, monitor_update))],
        )

        hub.send_monitor_update(monitor_update)

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=(400, 404, 500),
    )
    @responses.activate
    def test_send_monitor_update_http_error(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        ingestion_endpoint_url: str,
        monitor_update: _MonitorPostJSON,
        status_code: int,
    ) -> None:
        """Test send_monitor_update handles HTTP errors."""
        responses.add(
            responses.POST,
            url=ingestion_endpoint_url,
            status=status_code,
            match=[json_params_matcher(cast(_JSONDict, monitor_update))],
        )

        with pytest.raises(HTTPError):
            hub.send_monitor_update(monitor_update)

        # Check error logs
        error_logs = get_error_logs(caplog)
        assert str(status_code) in error_logs

    @responses.activate
    def test_send_monitor_update_request_exception(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        ingestion_endpoint_url: str,
        monitor_update: _MonitorPostJSON,
    ) -> None:
        """Test send_monitor_update handles request errors."""
        responses.add(
            responses.POST,
            url=ingestion_endpoint_url,
            body=RequestException("test error"),
            match=[json_params_matcher(cast(_JSONDict, monitor_update))],
        )

        with pytest.raises(RequestException, match="test error"):
            hub.send_monitor_update(monitor_update)

        # Check error logs
        error_logs = get_error_logs(caplog)
        assert "test error" in error_logs

    @fixture(scope="class")
    def registration_public_key(self) -> RSAPublicKey:
        """Public key for hub public key registration tests."""
        _, public_key = _RSAEncryption.generate_key_pair()
        return public_key

    @responses.activate
    def test_register_public_key(
        self,
        hub: BitfountHub,
        hub_url: str,
        registration_public_key: RSAPublicKey,
        username: str,
    ) -> None:
        """Tests register_public_key() passes through public key correctly."""
        responses.add(
            responses.POST,
            f"{hub_url}/api/{username}/keys",
            json={"id": "1234"},
            status=200,
            match=[
                json_params_matcher(
                    {
                        "key": _RSAEncryption.serialize_public_key(
                            registration_public_key, form="SSH"
                        ).decode()
                    }
                ),
                query_param_matcher({"version": 2}),
            ],
        )

        hub.register_user_public_key(registration_public_key)

    @pytest.mark.parametrize(
        argnames="status_code",
        argvalues=(400, 404, 500),
    )
    @responses.activate
    def test_register_public_key_http_error(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        registration_public_key: RSAPublicKey,
        status_code: int,
        username: str,
    ) -> None:
        """Tests register_public_key() handles HTTP error."""
        responses.add(
            responses.POST,
            f"{hub_url}/api/{username}/keys",
            json={"success": False},
            status=status_code,
            match=[
                json_params_matcher(
                    {
                        "key": _RSAEncryption.serialize_public_key(
                            registration_public_key, form="SSH"
                        ).decode()
                    }
                ),
                query_param_matcher({"version": 2}),
            ],
        )

        with pytest.raises(HTTPError):
            hub.register_user_public_key(registration_public_key)

        # Check error logs
        error_logs = get_error_logs(caplog)
        assert str(status_code) in error_logs

    @responses.activate
    def test_register_public_key_request_exception(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        registration_public_key: RSAPublicKey,
        username: str,
    ) -> None:
        """Tests register_public_key() handles request error."""
        responses.add(
            responses.POST,
            f"{hub_url}/api/{username}/keys",
            body=RequestException("TEST"),
            match=[
                json_params_matcher(
                    {
                        "key": _RSAEncryption.serialize_public_key(
                            registration_public_key, form="SSH"
                        ).decode()
                    }
                ),
                query_param_matcher({"version": 2}),
            ],
        )

        with pytest.raises(RequestException, match="TEST"):
            hub.register_user_public_key(registration_public_key)

        # Check error logs
        error_logs = get_error_logs(caplog)
        assert "TEST" in error_logs

    @fixture
    def user_identity_verifiers_response_json(
        self,
        public_key_registered: Union[str, bool, None],
        registration_public_key: RSAPublicKey,
        username: str,
    ) -> _UserRSAPublicKeysResponseJSON:
        """Mock response from /api/identity-verifiers.

        `public_key_registered` will control whether the public key is included
        in the response and what form it takes.
        """
        if public_key_registered is True:
            public_key = _RSAEncryption.serialize_public_key(
                registration_public_key
            ).decode()
        elif isinstance(public_key_registered, str):
            public_key = public_key_registered
        else:
            public_key = None

        response_json: _UserRSAPublicKeysResponseJSON = {
            "maximumOffset": -1,
            "keys": [],
        }
        if public_key and public_key_registered is not False:
            response_json = {
                "maximumOffset": 0,
                "keys": [_PublicKeyJSON(id="4", active=True, public_key=public_key)],
            }

        return response_json

    @responses.activate
    def test_check_public_key_registered(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        registration_public_key: RSAPublicKey,
        username: str,
    ) -> None:
        """Tests register_public_key() handles request error."""
        expected_key_id = "1337"
        hub_response = {
            "active": True,
            "id": expected_key_id,
            "public_key": _RSAEncryption.serialize_public_key(
                registration_public_key, form="SSH"
            ).decode(),
        }
        responses.add(
            responses.GET,
            f"{hub_url}/api/{username}/keys/{expected_key_id}",
            json=hub_response,
        )

        result = hub.check_public_key_registered_and_active(expected_key_id)

        assert result is not None
        assert result["active"] == hub_response["active"]
        assert result["id"] == expected_key_id
        assert _RSAEncryption.public_keys_equal(
            result["public_key"], registration_public_key
        )

    @responses.activate
    def test_check_public_key_registered_but_inactive(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        registration_public_key: RSAPublicKey,
        username: str,
    ) -> None:
        """Tests register_public_key() handles request error."""
        expected_key_id = "1337"
        expected_key = {"active": False, "id": expected_key_id, "public_key": "someKey"}
        responses.add(
            responses.GET,
            f"{hub_url}/api/{username}/keys/{expected_key_id}",
            json=expected_key,
        )

        assert hub.check_public_key_registered_and_active(expected_key_id) is None

    @responses.activate
    def test_check_public_key_not_found(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        registration_public_key: RSAPublicKey,
        username: str,
    ) -> None:
        """Tests register_public_key() handles request error."""
        expected_key_id = "1337"
        responses.add(
            responses.GET,
            f"{hub_url}/api/{username}/keys/{expected_key_id}",
            status=404,
        )

        assert hub.check_public_key_registered_and_active(expected_key_id) is None

    @responses.activate
    def test_check_public_key_registered_hub_returns_error(
        self,
        caplog: LogCaptureFixture,
        hub: BitfountHub,
        hub_url: str,
        registration_public_key: RSAPublicKey,
        username: str,
    ) -> None:
        """Tests check_public_key_registered_and_active() handles request error."""
        expected_key_id = "1337"
        responses.add(
            responses.GET,
            f"{hub_url}/api/{username}/keys/{expected_key_id}",
            body=RequestException("TEST"),
        )

        with pytest.raises(RequestException, match="TEST"):
            hub.check_public_key_registered_and_active(expected_key_id)

        # Check error logs
        error_logs = get_error_logs(caplog)
        assert "TEST" in error_logs


class TestAccessManager:
    """Test the BitfountAM class."""

    @fixture
    def url(self) -> str:
        """Access Manager URL as a fixture."""
        return "http://test-am.hub.bitfount.com"

    @fixture
    def session(self, mocker: MockerFixture) -> BitfountSession:
        """A session with auth."""
        session = BitfountSession()
        # Patching `authenticated` status onto session as it is required
        mocker.patch.object(
            type(session), "authenticated", PropertyMock(return_value=True)
        )
        mocker.patch.object(
            type(session),
            "hub_request_headers",
            PropertyMock(return_value={"authorization": "Bearer test"}),
        )
        mocker.patch.object(
            type(session),
            "am_request_headers",
            PropertyMock(return_value={"authorization": "Bearer test"}),
        )
        session.headers.update({"x-Bitfount-unit-test": "Session was used"})
        return session

    @fixture
    def access_manager(self, session: BitfountSession, url: str) -> BitfountAM:
        """Access Manager instance as a fixture."""
        return BitfountAM(session, url)

    @fixture
    def expected_saml_challenge(self) -> str:
        """SAML Challenge string from access manager."""
        return "a legit saml challenge"

    @fixture
    def expected_saml_request_id(self) -> str:
        """SAML Request ID from access manager."""
        return "my first saml"

    @fixture
    def saml_endpoint_result(
        self, expected_saml_challenge: str, expected_saml_request_id: str
    ) -> _SAMLChallengeResponseJSON:
        """Result of GET request to AM SAML endpoint."""
        return {"id": expected_saml_request_id, "samlRequest": expected_saml_challenge}

    @fixture
    def modeller_name(self) -> str:
        """Modeller name."""
        return "someModeller"

    @fixture
    def modeller_protocol_request(self) -> SerializedProtocol:
        """Modeller request."""
        return {
            "class_name": "bitfount.FederatedAveraging",
            "algorithm": {"class_name": "bitfount.FederatedModelTraining"},
        }

    @fixture
    def fake_original_saml_request_id(self) -> str:
        """Original SAML Request ID for tests."""
        return "12345"

    @fixture
    def expected_saml_post_body(
        self,
        fake_original_saml_request_id: str,
        modeller_name: str,
        modeller_protocol_request: SerializedProtocol,
        pod_identifier: str,
    ) -> _SAMLAdditionalInfoPOSTJSON:
        """JSON body Pod sends to AM to check access."""
        saml_post_body: _SAMLAdditionalInfoPOSTJSON = {
            "originalSAMLRequestID": fake_original_saml_request_id,
            "podIdentifier": pod_identifier,
            "modellerName": modeller_name,
            "modellerProtocolRequest": modeller_protocol_request,
            "identityProvider": "SAML",
        }
        return saml_post_body

    @fixture
    def fake_access_token(self) -> str:
        """Fake access token."""
        return "fake_access_token"

    @fixture
    def expected_oidc_post_body(
        self,
        fake_access_token: str,
        modeller_name: str,
        modeller_protocol_request: SerializedProtocol,
        pod_identifier: str,
    ) -> _OIDCAccessCheckPostJSON:
        """JSON body for OIDC Access Check POST request."""
        return {
            "podIdentifier": pod_identifier,
            "modellerName": modeller_name,
            "modellerProtocolRequest": modeller_protocol_request,
            "modellerToken": fake_access_token,
            "identityProvider": "OIDC",
        }

    @fixture
    def unsigned_task(self) -> bytes:
        """Unsigned task."""
        return b"unsigned_task"

    @fixture
    def task_signature(self) -> bytes:
        """Task signature."""
        return b"task_signature"

    @fixture
    def expected_signature_based_access_post_body(
        self,
        modeller_name: str,
        modeller_protocol_request: SerializedProtocol,
        pod_identifier: str,
        task_signature: bytes,
        unsigned_task: bytes,
    ) -> _SignatureBasedAccessCheckPostJSON:
        """JSON body for Signature based Access Check POST request."""
        return {
            "podIdentifier": pod_identifier,
            "modellerName": modeller_name,
            "modellerProtocolRequest": modeller_protocol_request,
            "unsignedTask": base64.b64encode(unsigned_task).decode("utf-8"),
            "taskSignature": base64.b64encode(task_signature).decode("utf-8"),
            "identityProvider": "SIGNATURE",
        }

    @unit_test
    def test_create_access_manager_without_bitfount_session(
        self, mocker: MockerFixture
    ) -> None:
        """Tests that BitfountSession is created under the hood if not provided."""
        mock_session = Mock(
            spec=BitfountSession,
            authenticated=False,
            user_storage_path="",
            username="",
        )
        mocker.patch("bitfount.hub.api.BitfountSession", return_value=mock_session)
        hub = BitfountAM()
        mock_session.authenticate.assert_called_once()
        assert isinstance(hub.session, BitfountSession)

    @unit_test
    @responses.activate
    def test_get_access_manager_key(
        self,
        access_manager: BitfountAM,
        access_manager_public_key: RSAPublicKey,
        url: str,
    ) -> None:
        """Checks AM key getter works."""
        expected_response: _AccessManagerKeyResponseJSON = {
            "accessManagerPublicKey": _RSAEncryption.serialize_public_key(
                access_manager_public_key, form="SSH"
            ).decode("utf-8"),
        }

        responses.add(
            responses.GET,
            f"{url}/api/access-manager-key",
            json=expected_response,
            status=200,
        )

        key = access_manager.get_access_manager_key()

        # Check key type and value are what we expect
        assert isinstance(key, RSAPublicKey)
        assert _RSAEncryption.serialize_public_key(
            key
        ) == _RSAEncryption.serialize_public_key(access_manager_public_key)

    @integration_test
    @pytest.mark.timeout(10)
    def test_get_access_manager_key_speed(self, monkeypatch: MonkeyPatch) -> None:
        """Checks AM key getter is able to retrieve the key with minimal delay.

        This test is to ensure we don't regress due to IPv4/IPv6 issues either on the
        requests side or the AM side.
        """
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "staging")
        mock_session = Mock(authenticated=True, spec=BitfountSession)
        am = BitfountAM(session=mock_session)
        key = am.get_access_manager_key()
        # Check key type and value are what we expect
        assert isinstance(key, RSAPublicKey)
        # Assert that the authenticate method on the session was not called
        mock_session.authenticate.assert_not_called()

    @unit_test
    @responses.activate
    def test_get_access_manager_key_fails_request_exception(
        self, access_manager: BitfountAM, url: str
    ) -> None:
        """Checks exception raised on if request raises RequestException."""
        responses.add(
            responses.GET,
            f"{url}/api/access-manager-key",
            body=RequestException("TEST"),
        )

        with pytest.raises(
            RequestException,
            match="Bitfount Access Manager connection failed with: TEST.$",
        ):
            access_manager.get_access_manager_key()

    @unit_test
    @pytest.mark.parametrize("status_code", (400, 404, 500))
    @responses.activate
    def test_get_access_manager_key_fails_non_200(
        self,
        access_manager: BitfountAM,
        remove_web_retry_backoff_sleep: Optional[Mock],
        status_code: int,
        url: str,
    ) -> None:
        """Checks exception raised on non-200 response."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        responses.add(
            responses.GET,
            f"{url}/api/access-manager-key",
            status=status_code,
        )

        with pytest.raises(HTTPError):
            access_manager.get_access_manager_key()

        # Check retries occurred if expected
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_web_retry_backoff_sleep.call_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            remove_web_retry_backoff_sleep.assert_not_called()

    @unit_test
    @responses.activate
    def test_get_access_manager_key_fails_non_json(
        self, access_manager: BitfountAM, url: str
    ) -> None:
        """Checks exception raised if response is `body`, not `json`."""
        non_json_response = "NOT JSON RESPONSE"
        responses.add(
            responses.GET,
            f"{url}/api/access-manager-key",
            body=non_json_response,
            status=200,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(f"Invalid JSON response (200): {non_json_response}"),
        ):
            access_manager.get_access_manager_key()

    @unit_test
    @responses.activate
    def test_get_access_manager_key_fails_no_key_in_json(
        self, access_manager: BitfountAM, url: str
    ) -> None:
        """Checks exception raised if key not in JSON."""
        expected_response = {
            "incorrectKey": "incorrectValue",
        }

        responses.add(
            responses.GET,
            f"{url}/api/access-manager-key",
            json=expected_response,
            status=200,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(
                f"Unable to extract public key from access manager response, "
                f"no key in JSON: {expected_response}"
            ),
        ):
            access_manager.get_access_manager_key()

    @unit_test
    @responses.activate
    def test_get_access_manager_key_fails_bad_json(
        self, access_manager: BitfountAM, url: str
    ) -> None:
        """Checks bad JSON response causes exception."""
        expected_response = "JSON BUT AT WHAT COST"

        responses.add(
            responses.GET,
            f"{url}/api/access-manager-key",
            json=expected_response,
            status=200,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(
                f"Unable to extract public key from access manager response, "
                f"no key in JSON: {expected_response}"
            ),
        ):
            access_manager.get_access_manager_key()

    @unit_test
    @responses.activate
    def test_get_saml_challenge(
        self,
        access_manager: BitfountAM,
        expected_saml_challenge: str,
        expected_saml_request_id: str,
        mocker: MockerFixture,
        saml_endpoint_result: _SAMLChallengeResponseJSON,
        session: BitfountSession,
        url: str,
    ) -> None:
        """Checks SAML challenge retrieval works."""
        mocker.patch.object(type(session), "_is_am_url", Mock(return_value=True))
        responses.add(
            responses.GET,
            f"{url}/api/saml?idp=cli",
            json=saml_endpoint_result,
            status=200,
        )

        saml_challenge, saml_request_id = access_manager.get_saml_challenge()

        assert saml_challenge == expected_saml_challenge
        assert saml_request_id == expected_saml_request_id
        # Make sure the access token is added as a header to the request
        first_call: responses.Call = responses.calls[0]
        assert (
            first_call.request.headers["Authorization"]
            == session.hub_request_headers["authorization"]
        )

    @unit_test
    @responses.activate
    def test_get_saml_challenge_fails_request_exception(
        self, access_manager: BitfountAM, url: str
    ) -> None:
        """Checks exception raised on if request raises RequestException."""
        responses.add(
            responses.GET, f"{url}/api/saml?idp=cli", body=RequestException("TEST")
        )

        with pytest.raises(
            RequestException,
            match="Bitfount Access Manager connection failed with: TEST.$",
        ):
            access_manager.get_saml_challenge()

    @unit_test
    @pytest.mark.parametrize("status_code", (400, 404, 500))
    @responses.activate
    def test_get_saml_challenge_fails_non_200(
        self,
        access_manager: BitfountAM,
        remove_web_retry_backoff_sleep: Optional[Mock],
        status_code: int,
        url: str,
    ) -> None:
        """Checks exception raised on non-200 response."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        responses.add(
            responses.GET,
            f"{url}/api/saml?idp=cli",
            status=status_code,
            json={"error": "Some error"},
        )

        with pytest.raises(HTTPError):
            access_manager.get_saml_challenge()

        # Check retries occurred if expected
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_web_retry_backoff_sleep.call_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            remove_web_retry_backoff_sleep.assert_not_called()

    @unit_test
    @responses.activate
    def test_get_saml_challenge_fails_non_json(
        self, access_manager: BitfountAM, url: str
    ) -> None:
        """Checks exception raised if response is `body`, not `json`."""
        non_json_response = "NOT JSON RESPONSE"
        responses.add(
            responses.GET,
            f"{url}/api/saml?idp=cli",
            body=non_json_response,
            status=200,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(f"Invalid JSON response (200): {non_json_response}"),
        ):
            access_manager.get_saml_challenge()

    @unit_test
    @responses.activate
    def test_get_saml_challenge_fails_wrong_json(
        self, access_manager: BitfountAM, url: str
    ) -> None:
        """Checks exception raised if expected keys not in JSON."""
        expected_response = {
            "incorrectKey": "incorrectValue",
        }

        responses.add(
            responses.GET,
            f"{url}/api/saml?idp=cli",
            json=expected_response,
            status=200,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(
                f"Unable to extract SAML Challenge from access manager response, "
                f"no challenge in JSON: {expected_response}"
            ),
        ):
            access_manager.get_saml_challenge()

    @unit_test
    @responses.activate
    def test_get_saml_challenge_fails_bad_json(
        self, access_manager: BitfountAM, url: str
    ) -> None:
        """Checks bad JSON response causes exception."""
        expected_response = "JSON BUT AT WHAT COST"

        responses.add(
            responses.GET,
            f"{url}/api/saml?idp=cli",
            json=expected_response,
            status=200,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(
                f"Unable to extract SAML Challenge from access manager response, "
                f"no challenge in JSON: {expected_response}"
            ),
        ):
            access_manager.get_saml_challenge()

    @unit_test
    @responses.activate
    def test_validate_saml_response_success(
        self,
        access_manager: BitfountAM,
        expected_saml_post_body: _SAMLAdditionalInfoPOSTJSON,
        session: BitfountSession,
        url: str,
    ) -> None:
        """Checks accepted SAML & Access check is returned."""
        accept_response: _AMAccessCheckResponseJSON = {"code": "ACCEPT"}
        saml_response: _SAMLResponse = {"saml": "response"}
        responses.add(
            responses.POST,
            f"{url}/api/access?idp=cli",
            json=accept_response,
        )

        assert (
            access_manager.validate_saml_response(
                saml_response,
                expected_saml_post_body["originalSAMLRequestID"],
                expected_saml_post_body["podIdentifier"],
                expected_saml_post_body["modellerName"],
                expected_saml_post_body["modellerProtocolRequest"],
            )
            == _PodResponseType.ACCEPT
        )

        first_call: responses.Call = responses.calls[0]
        request_body = first_call.request.body
        assert request_body is not None
        assert json.loads(request_body) == {**saml_response, **expected_saml_post_body}
        # Make sure we used the session to make the request!
        # Some headers are added when we attach the body
        # So we just check that the expected headers are a subset of the attached ones
        assert session.headers.items() <= first_call.request.headers.items()

    @unit_test
    @responses.activate
    def test_validate_saml_response_rejects_access(
        self, access_manager: BitfountAM, expected_saml_post_body: _JSONDict, url: str
    ) -> None:
        """Check validate SAML response when AM denies access."""
        reject_response: _AMAccessCheckResponseJSON = {"code": "UNAUTHORISED"}
        saml_response: _SAMLResponse = {"saml": "response"}
        responses.add(
            responses.POST,
            f"{url}/api/access?idp=cli",
            json=reject_response,
        )

        assert (
            access_manager.validate_saml_response(
                saml_response,
                expected_saml_post_body["originalSAMLRequestID"],
                expected_saml_post_body["podIdentifier"],
                expected_saml_post_body["modellerName"],
                expected_saml_post_body["modellerProtocolRequest"],
            )
            == _PodResponseType.UNAUTHORISED
        )

        first_call: responses.Call = responses.calls[0]
        request_body = first_call.request.body
        assert request_body is not None
        assert json.loads(request_body) == {**saml_response, **expected_saml_post_body}

    @unit_test
    @responses.activate
    def test_validate_saml_response_fails_request_exception(
        self, access_manager: BitfountAM, expected_saml_post_body: _JSONDict, url: str
    ) -> None:
        """Checks exception raised on request raising RequestException."""
        responses.add(
            responses.POST, f"{url}/api/access?idp=cli", body=RequestException("TEST")
        )

        with pytest.raises(
            RequestException,
            match="Bitfount Access Manager connection failed with: TEST.$",
        ):
            access_manager.validate_saml_response(
                {"saml": "response"},
                expected_saml_post_body["originalSAMLRequestID"],
                expected_saml_post_body["podIdentifier"],
                expected_saml_post_body["modellerName"],
                expected_saml_post_body["modellerProtocolRequest"],
            )

    @unit_test
    @pytest.mark.parametrize("status_code", (400, 404, 500))
    @responses.activate
    def test_validate_saml_response_fails_non_200(
        self,
        access_manager: BitfountAM,
        expected_saml_post_body: _JSONDict,
        remove_web_retry_backoff_sleep: Optional[Mock],
        status_code: int,
        url: str,
    ) -> None:
        """Checks exception raised on non-200 response."""
        # Check retry backoff is patched
        assert remove_web_retry_backoff_sleep is not None

        responses.add(
            responses.POST,
            f"{url}/api/access?idp=cli",
            status=status_code,
            json={"error": "Some error"},
        )

        with pytest.raises(HTTPError):
            access_manager.validate_saml_response(
                {"saml": "response"},
                expected_saml_post_body["originalSAMLRequestID"],
                expected_saml_post_body["podIdentifier"],
                expected_saml_post_body["modellerName"],
                expected_saml_post_body["modellerProtocolRequest"],
            )

        # Check retries occurred if expected
        if status_code in web_utils._RETRY_STATUS_CODES:
            assert (
                remove_web_retry_backoff_sleep.call_count
                == web_utils._DEFAULT_MAX_RETRIES
            )
        else:
            remove_web_retry_backoff_sleep.assert_not_called()

    @unit_test
    @responses.activate
    def test_validate_saml_response_fails_json_missing_response_code(
        self, access_manager: BitfountAM, expected_saml_post_body: _JSONDict, url: str
    ) -> None:
        """Checks "ERROR" code returned if expected keys not in JSON."""
        expected_response = {
            "incorrectKey": "incorrectValue",
        }

        responses.add(
            responses.POST,
            f"{url}/api/access?idp=cli",
            json=expected_response,
            status=200,
        )

        assert (
            access_manager.validate_saml_response(
                {"saml": "response"},
                expected_saml_post_body["originalSAMLRequestID"],
                expected_saml_post_body["podIdentifier"],
                expected_saml_post_body["modellerName"],
                expected_saml_post_body["modellerProtocolRequest"],
            )
            == _PodResponseType.NO_ACCESS
        )

    @unit_test
    @responses.activate
    def test_validate_saml_response_fails_wrong_json(
        self, access_manager: BitfountAM, expected_saml_post_body: _JSONDict, url: str
    ) -> None:
        """Checks exception raised if expected keys not in JSON."""
        expected_response = "JSON BUT AT WHAT COST"

        responses.add(
            responses.POST,
            f"{url}/api/access?idp=cli",
            json=expected_response,
            status=200,
        )

        with pytest.raises(
            InvalidJSONError,
            match=re.escape(f'Invalid JSON response (200): "{expected_response}"'),
        ):
            access_manager.validate_saml_response(
                {"saml": "response"},
                expected_saml_post_body["originalSAMLRequestID"],
                expected_saml_post_body["podIdentifier"],
                expected_saml_post_body["modellerName"],
                expected_saml_post_body["modellerProtocolRequest"],
            )

    @unit_test
    @responses.activate
    def test_check_oidc_access_request_success(
        self,
        access_manager: BitfountAM,
        expected_oidc_post_body: _OIDCAccessCheckPostJSON,
        fake_access_token: str,
        modeller_name: str,
        modeller_protocol_request: SerializedProtocol,
        pod_identifier: str,
        session: BitfountSession,
        url: str,
    ) -> None:
        """Checks OIDC access check works."""
        accept_response: _AMAccessCheckResponseJSON = {"code": "ACCEPT"}

        responses.add(
            responses.POST,
            f"{url}/api/access",
            json=accept_response,
        )

        assert (
            access_manager.check_oidc_access_request(
                pod_identifier=pod_identifier,
                serialized_protocol=modeller_protocol_request,
                modeller_name=modeller_name,
                modeller_access_token=fake_access_token,
            )
            == _PodResponseType.ACCEPT
        )

        first_call: responses.Call = responses.calls[0]
        request_body = first_call.request.body
        assert request_body is not None
        assert json.loads(request_body) == expected_oidc_post_body
        # Make sure we used the session to make the request!
        # Some headers are added when we attach the body
        # So we just check that the expected headers are a subset of the attached ones
        assert session.headers.items() <= first_call.request.headers.items()

    @unit_test
    @responses.activate
    def test_check_signature_based_access_request_success(
        self,
        access_manager: BitfountAM,
        expected_signature_based_access_post_body: _SignatureBasedAccessCheckPostJSON,
        modeller_name: str,
        modeller_protocol_request: SerializedProtocol,
        pod_identifier: str,
        session: BitfountSession,
        task_signature: bytes,
        unsigned_task: bytes,
        url: str,
    ) -> None:
        """Checks signatured based access check works."""
        accept_response: _AMAccessCheckResponseJSON = {"code": "ACCEPT"}

        responses.add(
            responses.POST,
            f"{url}/api/access",
            json=accept_response,
        )

        assert (
            access_manager.check_signature_based_access_request(
                unsigned_task=unsigned_task,
                task_signature=task_signature,
                pod_identifier=pod_identifier,
                serialized_protocol=modeller_protocol_request,
                modeller_name=modeller_name,
            )
            == _PodResponseType.ACCEPT
        )

        first_call: responses.Call = responses.calls[0]
        request_body = first_call.request.body
        assert request_body is not None

        # assert json.loads(request_body) == expected_signature_based_access_post_body
        # Make sure we used the session to make the request!
        # Some headers are added when we attach the body
        # So we just check that the expected headers are a subset of the attached ones
        assert session.headers.items() <= first_call.request.headers.items()

    @unit_test
    def test_am_url_gets_prod_url(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests that the am is loaded based on production environment."""
        mock_session = Mock(
            spec=BitfountSession,
            authenticated=False,
            user_storage_path="",
            username="",
        )
        mocker.patch("bitfount.hub.api.BitfountSession", return_value=mock_session)
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "production")
        am = BitfountAM()
        assert am.access_manager_url == PRODUCTION_AM_URL

    @unit_test
    def test_am_url_gets_staging_url(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests that the am url is loaded based on staging environment."""
        mock_session = Mock(
            spec=BitfountSession,
            authenticated=False,
            user_storage_path="",
            username="",
        )
        mocker.patch("bitfount.hub.api.BitfountSession", return_value=mock_session)
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "staging")
        am = BitfountAM()
        assert am.access_manager_url == _STAGING_AM_URL

    @unit_test
    def test_am_url_gets_dev_url(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch
    ) -> None:
        """Tests that the idp_url is loaded based on dev environment."""
        mock_session = Mock(
            spec=BitfountSession,
            authenticated=False,
            username="",
        )
        mocker.patch("bitfount.hub.api.BitfountSession", return_value=mock_session)
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "dev")
        am = BitfountAM()
        assert am.access_manager_url == _DEV_AM_URL


@unit_test
class TestCheckPodDetails:
    """Tests __check_pod_id_details function."""

    def test__check_pod_id_details_pod_identifier(self, pod_identifier: str) -> None:
        """Tests _check_pod_id_details works when given only pod_identifier."""
        returned_pod_id = _check_pod_id_details(pod_identifier=pod_identifier)
        assert returned_pod_id == pod_identifier

    def test__check_pod_id_details_pod_namespace_and_name(
        self, pod_identifier: str, pod_name: str, pod_namespace: str
    ) -> None:
        """Tests _check_pod_id_details works when given pod_namespace and pod_name.

        Check that DeprecationWarning is raised.
        """
        with pytest.warns(
            DeprecationWarning,
            match="pod_identifier should be used instead of pod_namespace and pod_name",
        ):
            returned_pod_id = _check_pod_id_details(
                pod_namespace=pod_namespace, pod_name=pod_name
            )
        assert returned_pod_id == pod_identifier

    def test__check_pod_id_details_none(self) -> None:
        """Tests _check_pod_id_details errors when given no args."""
        with pytest.raises(
            ValueError,
            match="At least one of pod_identifier OR pod_namespace and pod_name "
            "must be provided",
        ):
            _check_pod_id_details()

    def test__check_pod_id_details_one_of_namespace_or_name(
        self, pod_name: str, pod_namespace: str
    ) -> None:
        """Test _check_pod_id_details errors with only one of namespace or name."""
        # Only name
        with pytest.raises(
            ValueError,
            match="Both pod_namespace and pod_name must be provided, "
            "or neither must be.",
        ):
            _check_pod_id_details(pod_name=pod_name)

        # Only namespace
        with pytest.raises(
            ValueError,
            match="Both pod_namespace and pod_name must be provided, "
            "or neither must be.",
        ):
            _check_pod_id_details(pod_namespace=pod_namespace)

    def test__check_pod_id_details_all_provided(
        self, pod_identifier: str, pod_name: str, pod_namespace: str
    ) -> None:
        """Tests _check_pod_id_details works when all are provided and match.

        i.e. pod_identifier == pod_namespace/pod_name
        """
        returned_pod_id = _check_pod_id_details(pod_identifier, pod_namespace, pod_name)
        assert returned_pod_id == pod_identifier

    def test__check_pod_id_details_all_provided_but_not_match(
        self, pod_name: str, pod_namespace: str
    ) -> None:
        """Tests _check_pod_id_details errors when all are provided but don't match.

        i.e. pod_identifier != pod_namespace/pod_name
        """
        mismatch_pod_identifier = "not/theSame"

        with pytest.raises(
            ValueError,
            match="pod_identifier, pod_namespace and pod_name all provided, but "
            "pod_identifier doesn't match pod_namespace/pod_name.",
        ):
            _check_pod_id_details(mismatch_pod_identifier, pod_namespace, pod_name)
