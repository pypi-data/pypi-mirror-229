"""Tests for the Conversation protocol."""

from unittest.mock import AsyncMock, Mock

from pytest_mock import MockerFixture

from bitfount.federated.algorithms.transformer_text_generation import (
    TransformerTextGeneration,
)
import bitfount.federated.protocols.base as protocols
from bitfount.federated.protocols.conversation import Conversation
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import backend_test, unit_test


@backend_test
@unit_test
class TestConversation:
    """Tests for the Conversation protocol."""

    async def test_modeller_run_exits_if_prompt_is_empty(
        self, mocker: MockerFixture
    ) -> None:
        """Test modeller-side run method exits if prompt is empty."""
        algorithm = Mock()

        # patch input builtin function
        mock_input = mocker.patch("builtins.input", return_value="")

        protocol = Conversation(algorithm=algorithm)
        modeller_protocol = protocol.modeller(mailbox=AsyncMock())
        results = await modeller_protocol.run()
        assert results == []
        algorithm.modeller.return_value.run.assert_not_called()
        mock_input.assert_called_once()

    async def test_modeller_run_carries_on_indefinitely_until_prompt_is_empty(
        self, mocker: MockerFixture
    ) -> None:
        """Test modeller-side run method carries on indefinitely until prompt is empty.

        We patch the input builtin function to return 2 prompts, then an empty prompt.
        """
        algorithm = Mock()

        # patch input builtin function
        mock_input = mocker.patch(
            "builtins.input", side_effect=["prompt", "prompt2", ""]
        )

        # patch _get_model_responses_from_workers
        mock_get_model_responses_from_workers = mocker.patch(
            "bitfount.federated.protocols.conversation._get_model_responses_from_workers",
            side_effect=["response", "response2"],
        )

        protocol = Conversation(algorithm=algorithm)
        modeller_protocol = protocol.modeller(mailbox=AsyncMock())
        results = await modeller_protocol.run()

        # Assert that there were 3 prompts but only 2 responses because the last
        # prompt was empty
        assert results == ["response", "response2"]
        assert algorithm.modeller.return_value.run.call_count == 2  # 2 responses
        assert mock_get_model_responses_from_workers.call_count == 2  # 2 responses
        assert mock_input.call_count == 3  # 3 prompts

    async def test_worker_run_exits_if_prompt_is_empty(
        self, mocker: MockerFixture
    ) -> None:
        """Test worker-side run method exits if prompt is empty."""
        algorithm = Mock()

        # patch _get_model_prompt
        mock_get_model_prompt = mocker.patch(
            "bitfount.federated.protocols.conversation._get_model_prompt",
            return_value="",
        )

        protocol = Conversation(algorithm=algorithm)
        worker_protocol = protocol.worker(mailbox=AsyncMock(), hub=Mock())
        await worker_protocol.run()
        algorithm.worker.return_value.run.assert_not_called()
        mock_get_model_prompt.assert_awaited_once()

    async def test_worker_run_carries_on_indefinitely_until_prompt_is_empty(
        self, mocker: MockerFixture
    ) -> None:
        """Test worker-side run method carries on indefinitely until prompt is empty.

        We patch _get_model_prompt to return 2 prompts, then an empty prompt.
        """
        algorithm = Mock()

        # patch _get_model_prompt
        mock_get_model_prompt = mocker.patch(
            "bitfount.federated.protocols.conversation._get_model_prompt",
            side_effect=["prompt", "prompt2", ""],
        )

        protocol = Conversation(algorithm=algorithm)
        worker_protocol = protocol.worker(mailbox=AsyncMock(), hub=Mock())
        await worker_protocol.run()

        # Assert that there were 3 prompts but only 2 responses because the last
        # prompt was empty
        assert algorithm.worker.return_value.run.call_count == 2  # 2 responses
        assert mock_get_model_prompt.call_count == 3  # 3 prompts

    def test_serialization_with_transformer_text_generation_algorithm(self) -> None:
        """Test Marshmallow Serialization with TransformerTextGeneration algorithm."""
        algorithm_factory = TransformerTextGeneration(model_id="model_id")
        protocol = Conversation(algorithm=algorithm_factory)
        dumped = bf_dump(protocol)
        loaded = bf_load(dumped, protocols.registry)
        assert protocol.class_name == loaded.class_name
        assert protocol.algorithm.__dict__ == loaded.algorithm.__dict__
