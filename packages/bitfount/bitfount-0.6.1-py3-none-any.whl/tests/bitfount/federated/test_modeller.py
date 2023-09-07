"""Tests modeller.py module."""
import logging
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Protocol, Union, cast
from unittest.mock import AsyncMock, MagicMock, Mock, create_autospec

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
import pytest
from pytest import LogCaptureFixture, fixture
from pytest_mock import MockerFixture

from bitfount.backends.pytorch import PyTorchTabularClassifier
from bitfount.data.schema import BitfountSchema
from bitfount.federated.aggregators.secure import SecureAggregator
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithmFactory,
)
from bitfount.federated.algorithms.model_algorithms.federated_training import (
    FederatedModelTraining,
)
from bitfount.federated.authorisation_checkers import (
    IdentityVerificationMethod,
    _SAMLAuthorisation,
    _SignatureBasedAuthorisation,
)
from bitfount.federated.encryption import _RSAEncryption
from bitfount.federated.exceptions import PodResponseError
from bitfount.federated.keys_setup import RSAKeyPair
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.modeller import _Modeller
from bitfount.federated.protocols.base import BaseProtocolFactory
from bitfount.federated.protocols.model_protocols.federated_averaging import (
    FederatedAveraging,
)
from bitfount.federated.transport.identity_verification.types import _ResponseHandler
from bitfount.federated.transport.message_service import (
    _BitfountMessageType,
    _MessageService,
)
from bitfount.federated.transport.modeller_transport import (
    _ModellerMailbox,
    _WorkerMailboxDetails,
)
from bitfount.federated.types import (
    SerializedAggregator,
    SerializedAlgorithm,
    SerializedModel,
    SerializedProtocol,
    _TaskRequestMessageGenerator,
)
from bitfount.hub.api import BitfountHub
from bitfount.hub.authentication_flow import _AuthEnv
from bitfount.hub.types import _ActivePublicKey
from bitfount.models.base_models import _BaseModel
from tests.bitfount import TEST_SECURITY_FILES
from tests.utils import PytestRequest
from tests.utils.helper import (
    create_datastructure,
    get_debug_logs,
    get_error_logs,
    get_warning_logs,
    unit_test,
)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

PUBLIC_KEY_PATH = TEST_SECURITY_FILES / "test_public.testkey"
PRIVATE_KEY_PATH = TEST_SECURITY_FILES / "test_private.testkey"


class _RegisteredPublicKeyPatcher(Protocol):
    def __call__(
        self,
        key: Optional[Union[RSAPublicKey, RSAPrivateKey]],
        is_private_key_mock: bool = False,
    ) -> None:
        ...


@unit_test
class TestModeller:
    """Unit tests for Modeller."""

    @fixture(params=(True, False), ids=("project_id_incl", "no_project_id"))
    def opt_project_id(self, request: PytestRequest) -> Optional[str]:
        """Project ID."""
        incl_project_id: bool = request.param
        if incl_project_id:
            return "this-is-a-project-id"
        else:
            return None

    @fixture
    def protocol_factory_name(self) -> str:
        """Fake BaseProtocolFactory.name attribute."""
        return "protocol_factory_name"

    @fixture
    def algorithm_factory_name(self) -> str:
        """Fake BaseAlgorithmFactory.name attribute."""
        return "algorithm_factory_name"

    @fixture
    def aggregator_factory_name(self) -> str:
        """Fake Aggregator.name attribute."""
        return "aggregator_factory_name"

    @fixture
    def model_name(self) -> str:
        """Fake model.name attribute."""
        return "PyTorchTabularClassifier"

    @fixture(
        params=[
            "protocol_with_aggregator",
            "protocol_with_aggregator_custom_model",
            "protocol_without_aggregator",
        ]
    )
    def mock_protocol_factory_param(self, request: PytestRequest) -> str:
        """Allows test-level retrieval of mock_protocol_factory params."""
        return cast(str, request.param)

    @fixture
    def mock_protocol_factory(
        self,
        aggregator_factory_name: str,
        algorithm_factory_name: str,
        mock_protocol_factory_param: str,
        model_name: str,
        protocol_factory_name: str,
    ) -> Mock:
        """A mocked protocol factory.

        Is parameterised to return one with and without an aggregator attribute.
        """
        mock_protocol_factory: Mock = create_autospec(
            BaseProtocolFactory, instance=True
        )
        mock_protocol_factory.algorithm = Mock()
        dump_return_value = {
            "class_name": protocol_factory_name,
            "algorithm": {"class_name": algorithm_factory_name},
        }

        # If we are testing with a protocol+aggregator, mock it out.
        if mock_protocol_factory_param != "protocol_without_aggregator":
            dump_return_value["aggregator"] = {"class_name": aggregator_factory_name}

            if mock_protocol_factory_param == "protocol_with_aggregator":
                dump_return_value["algorithm"] = {
                    "class_name": "bitfount.FederatedModelTraining",
                    "model": {"class_name": model_name},
                }
            else:
                dump_return_value["algorithm"] = {
                    "class_name": "bitfount.FederatedModelTraining",
                    "model": {"class_name": "bitfount.BitfountModelReference"},
                }

        mock_protocol_factory.dump.return_value = dump_return_value
        return mock_protocol_factory

    @staticmethod
    def _enum__get_item__(x: str) -> Mock:
        """Returns a mock with x set as the `value` attribute."""
        mock = Mock()
        mock.value = x
        return mock

    @fixture
    def mock_protocol_type_enum(self, mocker: MockerFixture) -> Mock:
        """Mocks out the ProtocolType enum."""
        mock_enum = mocker.patch("bitfount.federated.modeller.ProtocolType")
        # Mock out the ProtocolType[x].value accesses
        mock_enum.__getitem__.side_effect = self._enum__get_item__
        return mock_enum

    @fixture
    def mock_algorithm_type_enum(self, mocker: MockerFixture) -> Mock:
        """Mocks out the AlgorithmType enum."""
        mock_enum = mocker.patch("bitfount.federated.modeller.AlgorithmType")
        # Mock out the AlgorithmType[x].value accesses
        mock_enum.__getitem__.side_effect = self._enum__get_item__
        return mock_enum

    @fixture
    def mock_aggregator_type_enum(self, mocker: MockerFixture) -> Mock:
        """Mocks out the AggregatorType enum."""
        mock_enum = mocker.patch("bitfount.federated.modeller.AggregatorType")
        # Mock out the AggregatorType[x].value accesses
        mock_enum.__getitem__.side_effect = self._enum__get_item__
        return mock_enum

    @fixture
    def mock_message_service(self) -> Mock:
        """A mocked message service."""
        mock_message_service: Mock = create_autospec(_MessageService, instance=True)
        return mock_message_service

    @fixture
    def mock_private_key(self) -> Mock:
        """A mocked RSA private key."""
        mock_private_key: Mock = create_autospec(RSAPrivateKey, instance=True)
        return mock_private_key

    @fixture
    def username(self) -> str:
        """Fake username."""
        return "fakeUser"

    @fixture
    def mock_bitfount_hub(self, username: str) -> Mock:
        """A mocked BitfountHub instance."""
        mock_bitfount_hub: Mock = create_autospec(BitfountHub, instance=True)
        mock_bitfount_hub.username = username
        return mock_bitfount_hub

    @fixture
    def registered_public_key_patcher(
        self, mock_bitfount_hub: Mock, mocker: MockerFixture
    ) -> _RegisteredPublicKeyPatcher:
        """Patcher for setting the return value of hub.get_user_public_key()."""

        def _patch_registered_public_key(
            key: Optional[Union[RSAPublicKey, RSAPrivateKey]],
            is_private_key_mock: bool = False,
        ) -> None:
            mocker.patch("bitfount.federated.modeller._store_key_id")
            mocker.patch("bitfount.federated.modeller._get_key_id", return_value="1")
            if key is None:
                mock_bitfount_hub.check_public_key_registered_and_active.return_value = (  # noqa: B950
                    None
                )
            else:
                if isinstance(key, RSAPrivateKey) or is_private_key_mock:
                    public_key = cast(RSAPrivateKey, key).public_key()
                else:
                    public_key = key
                mock_bitfount_hub.check_public_key_registered_and_active.return_value = _ActivePublicKey(  # noqa: B950
                    public_key=public_key,
                    id="2",
                    active=True,
                )

        return _patch_registered_public_key

    @fixture
    def pod_identifiers(self) -> List[str]:
        """A list of pod identifiers."""
        return ["user1/pod1", "user2/pod2"]

    @fixture
    def mock_pod_public_key_paths(self, pod_identifiers: List[str]) -> Dict[str, Mock]:
        """A dictionary of pod identifiers to mocked key file paths."""
        return {pod_identifier: Mock() for pod_identifier in pod_identifiers}

    @fixture
    def pretrained_file(self) -> str:
        """A fake path to a pretrained file."""
        return "fake_pretrained_file_path"

    @fixture
    def modeller(
        self,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_private_key: Mock,
        mock_protocol_factory: Mock,
    ) -> _Modeller:
        """Creates a modeller instance with most aspects mocked out.

        Optional args are not mocked, but are left as None.
        """
        modeller = _Modeller(
            protocol=mock_protocol_factory,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            private_key=mock_private_key,
        )
        return modeller

    @fixture
    def mailbox_id(self) -> str:
        """Fake mailbox id for modeller mailbox."""
        return "modeller-mailbox-id"

    @fixture
    def mock_modeller_mailbox(self, mailbox_id: str) -> Mock:
        """Returns mock mailbox."""
        mock_mailbox: Mock = create_autospec(_ModellerMailbox, instance=True)
        mock_mailbox.mailbox_id = mailbox_id
        return mock_mailbox

    async def test__send_task_requests(
        self,
        aggregator_factory_name: str,
        algorithm_factory_name: str,
        default_task_request_msg_gen: _TaskRequestMessageGenerator,
        mock_message_service: Mock,
        mock_modeller_mailbox: Mock,
        mock_private_key: Mock,
        mock_protocol_factory_param: str,
        mocker: MockerFixture,
        model_name: str,
        modeller: _Modeller,
        opt_project_id: Optional[str],
        pod_identifiers: List[str],
        protocol_factory_name: str,
    ) -> None:
        """Tests Modeller._send_task_requests()."""
        # Mock out get_pod_public_keys_call; don't need autospec=True as don't
        # care about the actual call details.
        mock_get_public_keys = mocker.patch(
            "bitfount.federated.modeller._get_pod_public_keys"
        )

        # Mock out ModellerMailbox.send_task_requests() class method. autospec=True
        # means we can check assert_called_with() without having to worry about
        # args vs kwargs.
        mock_mailbox_send_task_requests = mocker.patch.object(
            _ModellerMailbox, "send_task_requests", autospec=True
        )
        mock_mailbox_send_task_requests.return_value = mock_modeller_mailbox
        # mock_protocol_factory_param.class_name ="FederatedModelTraining"
        # Recreate the expected task_request_body
        if mock_protocol_factory_param == "protocol_with_aggregator":
            expected_task_request_body = SerializedProtocol(
                class_name=protocol_factory_name,
                algorithm=SerializedAlgorithm(
                    class_name="bitfount.FederatedModelTraining",
                    # must be an instance of BaseModelAlgorithmFactory
                    model=SerializedModel(class_name=f"{model_name}"),
                ),
                aggregator=SerializedAggregator(class_name=aggregator_factory_name),
            )
        elif mock_protocol_factory_param == "protocol_with_aggregator_custom_model":
            expected_task_request_body = SerializedProtocol(
                class_name=protocol_factory_name,
                algorithm=SerializedAlgorithm(
                    class_name="bitfount.FederatedModelTraining",
                    # must be an instance of BaseModelAlgorithmFactory
                    model=SerializedModel(class_name="bitfount.BitfountModelReference"),
                ),
                aggregator=SerializedAggregator(class_name=aggregator_factory_name),
            )
        else:
            expected_task_request_body = SerializedProtocol(
                class_name=protocol_factory_name,
                algorithm=SerializedAlgorithm(class_name=algorithm_factory_name),
            )

        modeller_mailbox = await modeller._send_task_requests(
            pod_identifiers, opt_project_id
        )

        # The mailbox returned from Modeller._send_task_requests() should be the
        # same as the one from ModellerMailbox.send_task_requests().
        assert modeller_mailbox == mock_modeller_mailbox
        # The class method should have been called with correctly constructed args.
        mock_mailbox_send_task_requests.assert_called_once_with(
            serialized_protocol=expected_task_request_body,
            pod_public_keys=mock_get_public_keys(),
            message_service=mock_message_service,
            task_request_msg_gen=default_task_request_msg_gen,
            project_id=opt_project_id,
            run_on_new_data_only=False,
            batched_execution=False,
        )

    def test_modeller_init_fails_invalid_verification_method(
        self,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_protocol_factory: Mock,
    ) -> None:
        """Tests Modeller.__init__ fails if unrecognised verification method."""
        fake_method = "fake_method"

        with pytest.raises(
            ValueError,
            match=re.escape(f"Unsupported identity verification method: {fake_method}"),
        ):
            _Modeller(
                protocol=mock_protocol_factory,
                message_service=mock_message_service,
                bitfounthub=mock_bitfount_hub,
                identity_verification_method=fake_method,
            )

    def test_modeller_init_generates_keys_if_key_based_verification_but_no_key(
        self,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_private_key: Mock,
        mock_protocol_factory: Mock,
        mocker: MockerFixture,
        registered_public_key_patcher: _RegisteredPublicKeyPatcher,
    ) -> None:
        """Tests autogenerates keys if key-based verification method but no key."""
        # Mock out key generation/loading
        mock_public_key = mock_private_key.public_key()
        mock__get_modeller_keys: Mock = mocker.patch(
            "bitfount.federated.modeller._get_modeller_keys",
            autospec=True,
            return_value=RSAKeyPair(mock_public_key, mock_private_key),
        )
        registered_public_key_patcher(None)

        modeller = _Modeller(
            protocol=mock_protocol_factory,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            identity_verification_method=IdentityVerificationMethod.KEYS,
            private_key=None,
        )

        # Check keys generated/loaded and registered
        mock__get_modeller_keys.assert_called_once()
        mock_bitfount_hub.register_user_public_key.assert_called_once_with(
            mock_public_key
        )
        assert modeller._private_key == mock_private_key

    def test_modeller_init_warns_non_key_verification_but_key_provided(
        self,
        caplog: LogCaptureFixture,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_private_key: Mock,
        mock_protocol_factory: Mock,
    ) -> None:
        """Tests Modeller.__init__ warns if key provided for non-key verification."""
        _Modeller(
            protocol=mock_protocol_factory,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            identity_verification_method=IdentityVerificationMethod.SAML,
            private_key=mock_private_key,
        )

        warning_logs = get_warning_logs(caplog)
        assert (
            f"Private key provided but identity verification method "
            f'"{IdentityVerificationMethod.SAML.value}" was chosen. Private key '
            f"will be ignored." in warning_logs
        )

    def test_modeller_init_loads_key_if_path(
        self,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_protocol_factory: Mock,
        mocker: MockerFixture,
        registered_public_key_patcher: _RegisteredPublicKeyPatcher,
    ) -> None:
        """Tests Modeller.__init__ loads key from path."""
        # Mock out key loading
        mock_load_private_key = mocker.patch.object(
            _RSAEncryption, "load_private_key", autospec=True
        )
        registered_public_key_patcher(
            mock_load_private_key.return_value, is_private_key_mock=True
        )

        # Fake key path
        fake_path = create_autospec(Path, instance=True)

        m = _Modeller(
            protocol=mock_protocol_factory,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            identity_verification_method=IdentityVerificationMethod.KEYS,
            private_key=fake_path,
        )

        # Check loading done
        mock_load_private_key.assert_called_once_with(fake_path)
        assert m._private_key == mock_load_private_key.return_value

    def test_modeller_init_loads_key_if_key(
        self,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_private_key: Mock,
        mock_protocol_factory: Mock,
        registered_public_key_patcher: _RegisteredPublicKeyPatcher,
    ) -> None:
        """Tests Modeller.__init__ uses provided key."""
        registered_public_key_patcher(mock_private_key, is_private_key_mock=True)
        m = _Modeller(
            protocol=mock_protocol_factory,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            identity_verification_method=IdentityVerificationMethod.KEYS,
            private_key=mock_private_key,
        )

        # Check loading done
        assert m._private_key == mock_private_key

    def test_modeller_init_handles_non_key(
        self,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_protocol_factory: Mock,
    ) -> None:
        """Test error handling if non-private-key is passed to Modeller init."""
        with pytest.raises(TypeError):
            _Modeller(
                protocol=mock_protocol_factory,
                message_service=mock_message_service,
                bitfounthub=mock_bitfount_hub,
                identity_verification_method=IdentityVerificationMethod.KEYS,
                private_key=Mock(),
            )

    async def test__modeller_run(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
    ) -> None:
        """Tests _modeller_run performs expected operations."""
        # Set "accepted" pods
        mock_worker_mailboxes = {
            pod_identifier: create_autospec(_WorkerMailboxDetails, instance=True)
            for pod_identifier in pod_identifiers
        }
        mock_modeller_mailbox.accepted_worker_mailboxes = mock_worker_mailboxes
        # Mock out next call in chain
        mock__run_modeller_protocol = mocker.patch.object(
            modeller, "_run_modeller_protocol", autospec=True
        )

        await modeller._modeller_run(
            modeller_mailbox=mock_modeller_mailbox, pod_identifiers=pod_identifiers
        )

        # Check task response processing was called
        mock_modeller_mailbox.process_task_request_responses.assert_awaited_once()
        # Check next stage called
        mock__run_modeller_protocol.assert_awaited_once()

    def test_modeller_run_secure_aggregation_params(
        self,
        caplog: LogCaptureFixture,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_private_key: Mock,
        mocker: MockerFixture,
        pod_identifiers: List[str],
    ) -> None:
        """Tests parameters for clipping are set for secure aggregation."""
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            epochs=2,
        )
        algorithm_factory = FederatedModelTraining(model=model)
        fed_avg = FederatedAveraging(
            algorithm=algorithm_factory, aggregator=SecureAggregator()
        )
        modeller = _Modeller(
            protocol=fed_avg,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            private_key=mock_private_key,
        )

        mocker.patch.object(
            _Modeller, "run_async", new_callable=AsyncMock, return_value=False
        )

        modeller.run(pod_identifiers=pod_identifiers)
        assert (
            "SecureAggregation in use. "
            "We recommend normalization of continuous features prior to training."
            in get_warning_logs(caplog)
        )
        assert model.param_clipping == {
            "prime_q": 2**61 - 1,
            "precision": 10**10,
            "num_workers": 2,
        }

    def test_modeller_run_secure_aggregation_params_steps(
        self,
        caplog: LogCaptureFixture,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_private_key: Mock,
        mocker: MockerFixture,
        pod_identifiers: List[str],
    ) -> None:
        """Tests parameters for clipping are not set for secure aggregation.

        Tests the case when steps_between_parameter_updates=1 in
        the protocol definition.
        """
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            steps=2,
        )
        algorithm_factory = FederatedModelTraining(model=model)
        fed_avg = FederatedAveraging(
            algorithm=algorithm_factory,
            aggregator=SecureAggregator(),
            steps_between_parameter_updates=1,
        )
        modeller = _Modeller(
            protocol=fed_avg,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            private_key=mock_private_key,
        )

        mocker.patch.object(
            _Modeller, "run_async", new_callable=AsyncMock, return_value=False
        )

        modeller.run(pod_identifiers=pod_identifiers)
        assert (
            caplog.records[-1].msg != "SecureAggregation in use. "
            "We recommend normalization of continuous features prior to training."
        )
        assert model.param_clipping is None

    def test_modeller_run_secure_aggregation_params_bfmodel(
        self,
        bitfount_model_correct_structure: str,
        caplog: LogCaptureFixture,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_private_key: Mock,
        mocker: MockerFixture,
        pod_identifiers: List[str],
        tmp_path: Path,
    ) -> None:
        """Tests parameters for clipping are set for secure aggregation.

        Tests that an extra warning is raised in the case
        of a custom model in the protocol definition.
        """
        model_file = tmp_path / "MyModel.py"
        model_file.touch()
        model_file.write_text(bitfount_model_correct_structure)
        hub_mock = MagicMock()
        hub_mock.send_model.return_value = True
        hub_mock.username = "test_username"
        model_ref = BitfountModelReference(
            username="test",
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            model_ref=model_file,
            hub=hub_mock,
            hyperparameters={"param1": 1, "param2": 2},
        )
        algorithm_factory = FederatedModelTraining(model=model_ref)
        fed_avg = FederatedAveraging(
            algorithm=algorithm_factory,
            aggregator=SecureAggregator(),
            steps_between_parameter_updates=2,
        )
        modeller = _Modeller(
            protocol=fed_avg,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            private_key=mock_private_key,
        )

        mocker.patch.object(
            _Modeller, "run_async", new_callable=AsyncMock, return_value=False
        )

        modeller.run(pod_identifiers=pod_identifiers)

        # Check logs
        warning_logs = get_warning_logs(caplog)
        assert (
            "SecureAggregation in use. "
            "We recommend normalization of continuous features prior to training."
            in warning_logs
        )
        assert (
            "You are using a custom model with Secure Aggregation."
            "We recommend clipping the model parameters." in warning_logs
        )

    @pytest.mark.parametrize("require_all_pods", [True, False])
    async def test__modeller_run_offline_pods(
        self,
        caplog: LogCaptureFixture,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
        require_all_pods: bool,
    ) -> None:
        """Tests _modeller_run performs errors/warns about offline pods."""
        # Set "accepted" pods
        mock_worker_mailboxes = {
            pod_identifiers[0]: create_autospec(_WorkerMailboxDetails, instance=True)
        }
        mock_modeller_mailbox.accepted_worker_mailboxes = mock_worker_mailboxes

        # Mock out next call in chain
        mock__run_modeller_protocol = mocker.patch.object(
            modeller, "_run_modeller_protocol", autospec=True
        )

        err_msg = "Pods user2/pod2 rejected task request or failed to respond. "

        if require_all_pods:
            with pytest.raises(
                PodResponseError,
                match=err_msg + "Task requires all pods accept the task request.",
            ):
                await modeller._modeller_run(
                    modeller_mailbox=mock_modeller_mailbox,
                    pod_identifiers=pod_identifiers,
                    require_all_pods=require_all_pods,
                )
                # Check next stage not called
                mock__run_modeller_protocol.assert_not_called()
        else:
            await modeller._modeller_run(
                modeller_mailbox=mock_modeller_mailbox,
                pod_identifiers=pod_identifiers,
                require_all_pods=require_all_pods,
            )
            # Check next stage called
            mock__run_modeller_protocol.assert_awaited_once()
            warning_logs = get_warning_logs(caplog)
            assert warning_logs == err_msg + "Continuing task without these pods ..."

        # Check task response processing was called
        mock_modeller_mailbox.process_task_request_responses.assert_awaited_once()

    async def test__modeller_run_fails_fast_if_no_accepted_pods(
        self,
        caplog: LogCaptureFixture,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        modeller: _Modeller,
    ) -> None:
        """Tests _modeller_run method fails fast if no pods accept."""
        # Set no "accepted" pods
        mock_modeller_mailbox.accepted_worker_mailboxes = {}

        # Mock out next call in chain
        mock__run_modeller_protocol = mocker.patch.object(
            modeller, "_run_modeller_protocol", autospec=True
        )

        result = await modeller._modeller_run(
            modeller_mailbox=mock_modeller_mailbox, pod_identifiers=["pod_id"]
        )

        # Check false return value
        assert result is False
        # Check error logged out
        error_logs = get_error_logs(caplog)
        assert "No workers with which to train." in error_logs
        # Check next stage NOT called
        mock__run_modeller_protocol.assert_not_called()

    async def test__modeller_run_with_response_handler(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
    ) -> None:
        """Tests _modeller_run method when provided with a ResponseHandler."""
        # Set "accepted" pods
        mock_worker_mailboxes = {
            pod_identifier: create_autospec(_WorkerMailboxDetails, instance=True)
            for pod_identifier in pod_identifiers
        }
        mock_modeller_mailbox.accepted_worker_mailboxes = mock_worker_mailboxes

        # Mock out next call in chain
        mock__run_modeller_protocol = mocker.patch.object(
            modeller, "_run_modeller_protocol", autospec=True
        )

        # Create mock ResponseHandler
        mock_response_handler = create_autospec(_ResponseHandler, instance=True)

        await modeller._modeller_run(
            modeller_mailbox=mock_modeller_mailbox,
            response_handler=mock_response_handler,
            pod_identifiers=pod_identifiers,
        )

        # Check task response pre-processing was called
        mock_response_handler.handle.assert_awaited_once()
        # Check task response processing was called
        mock_modeller_mailbox.process_task_request_responses.assert_awaited_once()
        # Check next stage called
        mock__run_modeller_protocol.assert_awaited_once()

    async def test_run_async(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
    ) -> None:
        """Tests run_async method performs expected operations."""
        # Mock out task request sending
        mock__send_task_requests = mocker.patch.object(
            modeller,
            "_send_task_requests",
            autospec=True,
            return_value=mock_modeller_mailbox,
        )
        # Mock out next stage call
        mock__modeller_run = mocker.patch.object(
            modeller, "_modeller_run", autospec=True
        )

        result = await modeller.run_async(pod_identifiers, require_all_pods=False)

        # Assert task requests sent
        mock__send_task_requests.assert_awaited_once()
        # Assert next stage called
        mock__modeller_run.assert_awaited_once()
        # Check log message handler removed
        mock_modeller_mailbox.delete_all_handlers.assert_called_once_with(
            _BitfountMessageType.LOG_MESSAGE
        )
        # Check return value
        assert result == mock__modeller_run.return_value

    async def test_run_async_with_saml_handler(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
    ) -> None:
        """Test run_async correctly starts SAML challenge handler."""
        # Set SAML identity verification method on modeller
        modeller._identity_verification_method = IdentityVerificationMethod.SAML

        # Mock out task request sending
        mock__send_task_requests = mocker.patch.object(
            modeller,
            "_send_task_requests",
            autospec=True,
            return_value=mock_modeller_mailbox,
        )
        # Mock out next stage call
        mock__modeller_run = mocker.patch.object(
            modeller, "_modeller_run", autospec=True
        )

        # Mock out SAML servers
        mock_saml_handler_cls = mocker.patch(
            "bitfount.federated.modeller._SAMLChallengeHandler", autospec=True
        )
        mock_saml_handler = mock_saml_handler_cls.return_value

        result = await modeller.run_async(pod_identifiers, require_all_pods=False)

        # Assert SAML server running
        mock_saml_handler.start_server.assert_called_once()

        # Assert task requests sent
        mock__send_task_requests.assert_awaited_once()
        # Assert next stage called
        mock__modeller_run.assert_awaited_once()
        # Check log message handler removed
        mock_modeller_mailbox.delete_all_handlers.assert_called_once_with(
            _BitfountMessageType.LOG_MESSAGE
        )
        # Check return value
        assert result == mock__modeller_run.return_value

    async def test_run_async_with_oidc_auth_flow_handler(
        self,
        caplog: LogCaptureFixture,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
    ) -> None:
        """Test run_async correctly starts OIDC auth code challenge handler."""
        # Set OIDC identity verification method on modeller
        modeller._identity_verification_method = (
            IdentityVerificationMethod.OIDC_ACF_PKCE
        )

        # Mock out task request sending
        mock__send_task_requests = mocker.patch.object(
            modeller,
            "_send_task_requests",
            autospec=True,
            return_value=mock_modeller_mailbox,
        )
        # Mock out next stage call
        mock__modeller_run = mocker.patch.object(
            modeller, "_modeller_run", autospec=True
        )

        # Mock out environment retrieval
        fake_auth_env = _AuthEnv(
            name="auth_env_name",
            auth_domain="auth_env_auth_domain",
            client_id="auth_env_client_id",
        )
        mocker.patch(
            "bitfount.federated.modeller._get_auth_environment",
            autospec=True,
            return_value=fake_auth_env,
        )

        # Mock out OIDC server
        mock_oidc_handler_cls = mocker.patch(
            "bitfount.federated.modeller._OIDCAuthFlowChallengeHandler", autospec=True
        )
        mock_oidc_handler = mock_oidc_handler_cls.return_value

        with caplog.at_level(logging.DEBUG):
            result = await modeller.run_async(pod_identifiers, require_all_pods=False)

        # Assert OIDC server running
        mock_oidc_handler.start_server.assert_called_once()
        # Check OIDC server constructed correctly
        mock_oidc_handler_cls.assert_called_once_with(
            auth_domain=fake_auth_env.auth_domain
        )
        # Check logs output
        debug_logs = get_debug_logs(caplog)
        assert (
            f"Setting up OIDC Authorization Code Flow challenge listener against "
            f"{fake_auth_env.name} authorization environment." in debug_logs
        )

        # Assert task requests sent
        mock__send_task_requests.assert_awaited_once()
        # Assert next stage called
        mock__modeller_run.assert_awaited_once()
        # Check log message handler removed
        mock_modeller_mailbox.delete_all_handlers.assert_called_once_with(
            _BitfountMessageType.LOG_MESSAGE
        )
        # Check return value
        assert result == mock__modeller_run.return_value

    async def test_run_async_with_oidc_device_code_handler(
        self,
        mock_modeller_mailbox: Mock,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
    ) -> None:
        """Test run_async correctly starts OIDC device code challenge handler."""
        # Set OIDC identity verification method on modeller
        modeller._identity_verification_method = (
            IdentityVerificationMethod.OIDC_DEVICE_CODE
        )

        # Mock out task request sending
        mock__send_task_requests = mocker.patch.object(
            modeller,
            "_send_task_requests",
            autospec=True,
            return_value=mock_modeller_mailbox,
        )
        # Mock out next stage call
        mock__modeller_run = mocker.patch.object(
            modeller, "_modeller_run", autospec=True
        )

        # Mock out environment retrieval
        fake_auth_env = _AuthEnv(
            name="auth_env_name",
            auth_domain="auth_env_auth_domain",
            client_id="auth_env_client_id",
        )
        mocker.patch(
            "bitfount.federated.modeller._get_auth_environment",
            autospec=True,
            return_value=fake_auth_env,
        )

        # Mock out OIDC Device Code init
        mock_oidc_handler_cls = mocker.patch(
            "bitfount.federated.modeller._OIDCDeviceCodeHandler", autospec=True
        )

        result = await modeller.run_async(pod_identifiers, require_all_pods=False)

        # Check OIDC handler constructed correctly
        mock_oidc_handler_cls.assert_called_once_with(
            auth_domain=fake_auth_env.auth_domain
        )

        # Assert task requests sent
        mock__send_task_requests.assert_awaited_once()
        # Assert next stage called
        mock__modeller_run.assert_awaited_once()
        # Check log message handler removed
        mock_modeller_mailbox.delete_all_handlers.assert_called_once_with(
            _BitfountMessageType.LOG_MESSAGE
        )
        # Check return value
        assert result == mock__modeller_run.return_value

    async def test_run_async_finally_works_with_no_response_handler(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
    ) -> None:
        """Test run_async finally block handles non-existent handler variable."""
        mocker.patch.object(modeller, "_get_response_handler", side_effect=Exception)

        with pytest.raises(Exception):
            await modeller.run_async(pod_identifiers, require_all_pods=False)

        warning_logs = get_warning_logs(caplog)
        assert "Tried to shutdown non-existent response handler" in warning_logs

    async def test_run_async_finally_works_with_non_server_response_handler(
        self,
        mocker: MockerFixture,
        modeller: _Modeller,
        pod_identifiers: List[str],
    ) -> None:
        """Test run_async finally block handles non-server handler variable."""
        require_all_pods = False
        # Mock out response_handler. We don't use autospec so we can guarantee
        # that stop_server isn't present.
        mock_get_response_handler = mocker.patch.object(
            modeller, "_get_response_handler", autospec=True
        )
        # Remove stop_server() from being autocreated, forcing an AttributeError
        # to be raised when mock.stop_server is called.
        del (
            mock_response_handler := mock_get_response_handler.return_value
        ).stop_server
        assert not hasattr(mock_response_handler, "stop_server")

        # Set _send_task_requests to error out to force us into the `finally`
        # block earlier. Use specific error message to ensure that's the one we see.
        mocker.patch.object(
            modeller, "_send_task_requests", side_effect=Exception("specific exception")
        )

        with pytest.raises(Exception, match="specific exception"):
            await modeller.run_async(pod_identifiers, require_all_pods)

    async def test_modeller_aborts_task_correctly_if_pod_does_not_exist(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
        modeller: _Modeller,
    ) -> None:
        """Test modeller aborts the task as expected if there is a non-existent pod.

        This includes raising an informative error message.
        """
        pod_identifier = "non-existent-pod"
        mocker.patch.object(modeller, "_get_response_handler", return_value=AsyncMock())
        mock_get_pod_key = mocker.patch.object(
            modeller._hub, "get_pod_key", return_value=None
        )
        result = await modeller.run_async(
            pod_identifiers=[pod_identifier], require_all_pods=False
        )
        assert result is False
        final_log_message = caplog.records[-1]
        penultimate_log_message = caplog.records[-2]

        assert final_log_message.levelname == "ERROR"
        assert final_log_message.message == "Aborted task request."
        assert penultimate_log_message.levelname == "ERROR"
        assert (
            penultimate_log_message.message
            == f"No public key found for pod: {pod_identifier}"
        )
        mock_get_pod_key.assert_called_once_with(pod_identifier=pod_identifier)

    def test__get_task_request_msg_gen_key_based(
        self,
        mock_bitfount_hub: Mock,
        mock_message_service: Mock,
        mock_private_key: Mock,
        mock_protocol_factory: Mock,
        mocker: MockerFixture,
        registered_public_key_patcher: _RegisteredPublicKeyPatcher,
    ) -> None:
        """Test request message generator creation for key-based authentication."""
        # Guarantee private key and key-based on modeller
        registered_public_key_patcher(mock_private_key, is_private_key_mock=True)
        modeller = _Modeller(
            protocol=mock_protocol_factory,
            message_service=mock_message_service,
            bitfounthub=mock_bitfount_hub,
            private_key=mock_private_key,
            identity_verification_method=IdentityVerificationMethod.KEYS,
        )

        # Wrap mock around authorisation checker class
        wrapped_creator = mocker.patch.object(
            _SignatureBasedAuthorisation,
            "create_task_request_message_generator",
            wraps=_SignatureBasedAuthorisation.create_task_request_message_generator,
        )

        msg_gen = modeller._get_task_request_msg_gen()

        # Check called with key
        wrapped_creator.assert_called_once_with(mock_private_key)
        # Check returned gen
        assert isinstance(msg_gen, _TaskRequestMessageGenerator)

    def test__get_task_request_msg_gen_saml_based(
        self,
        mocker: MockerFixture,
        modeller: _Modeller,
    ) -> None:
        """Test request message generator creation for key-based authentication."""
        # Guarantee SAML-based on modeller
        modeller._identity_verification_method = IdentityVerificationMethod.SAML

        # Wrap mock around authorisation checker class
        wrapped_creator = mocker.patch.object(
            _SAMLAuthorisation,
            "create_task_request_message_generator",
            wraps=_SAMLAuthorisation.create_task_request_message_generator,
        )

        msg_gen = modeller._get_task_request_msg_gen()

        # Check called with key
        wrapped_creator.assert_called_once()
        # Check returned gen
        assert isinstance(msg_gen, _TaskRequestMessageGenerator)

    @pytest.mark.parametrize("model_out", (None, Path("out_file.pt")))
    def test_run(
        self, mocker: MockerFixture, model_out: Optional[Path], modeller: _Modeller
    ) -> None:
        """Test modeller run method."""
        pod_id = "pod_id"
        mock_check_and_update_pod_ids = mocker.patch(
            "bitfount.federated.modeller._check_and_update_pod_ids"
        )
        mock_run = mocker.patch("asyncio.run")
        mock_serialize = mocker.patch.object(modeller, "_serialize")
        modeller.run(pod_id, model_out=model_out)
        mock_check_and_update_pod_ids.assert_called_once()
        if model_out:
            mock_serialize.assert_called_once()
        else:
            mock_serialize.assert_not_called()
        mock_run.assert_called_once()

    @pytest.mark.parametrize("protocol", ("ResultsOnly", "NotResultsOnly"))
    def test__serialize(
        self,
        algorithm_factory_name: str,
        caplog: LogCaptureFixture,
        mock_protocol_factory_param: str,
        mocker: MockerFixture,
        model_name: str,
        modeller: _Modeller,
        protocol: str,
    ) -> None:
        """Test serializing of model."""
        # This is because the protocol that has an algorithm also has a model
        if mock_protocol_factory_param == "protocol_with_aggregator":
            modeller.protocol.class_name = protocol
            mock_algorithm_factory = create_autospec(
                _BaseModelAlgorithmFactory, instance=True
            )
            mock_algorithm_factory.class_name = algorithm_factory_name
            mock_algorithm_factory.model = Mock(spec=_BaseModel)
            mock_algorithm_factory.model.class_name = model_name
            modeller.protocol.algorithm = mock_algorithm_factory
        else:
            # Explicitly deleting model attribute from Mock object to ensure an
            # AttributeError is raised when trying to access it. This is necessary
            # because Mocks allow the accessing of any made-up attribute
            del modeller.protocol.algorithm.model  # type: ignore[union-attr] # Reason: See above # noqa: B950

        # Overriding the `algorithms` property to match the behaviour in the target
        # object (i.e. returning a list of algorithms)
        modeller.protocol.algorithms = [  # type: ignore[misc] # Reason: See above # noqa: B950
            modeller.protocol.algorithm  # type: ignore[list-item] # Reason: See above # noqa: B950
        ]
        modeller._serialize(Path("file_name"))

        if hasattr(modeller.protocol.algorithm, "model"):
            modeller.protocol.algorithm.model.serialize.assert_called_once()
