"""Fixtures for components that are from the transport layer."""
import asyncio
from asyncio import Queue, QueueEmpty
import threading
from typing import AsyncIterator, Callable, Iterable, Optional, Protocol, Type, Union
from unittest.mock import AsyncMock, MagicMock, Mock, create_autospec

from grpc import RpcError, StatusCode
from pytest import fixture
from pytest_mock import MockerFixture
from typing_extensions import TypeAlias

from bitfount.federated.transport.message_service import (
    _BitfountMessage,
    _MessageService,
)
from tests.utils import PytestRequest
from tests.utils.helper import end_to_end_mocks_test, integration_test, unit_test

MessageOrException: TypeAlias = Union[
    _BitfountMessage, BaseException, Type[BaseException]
]


@fixture
def mock_grpc_insecure_channel(mocker: MockerFixture) -> Mock:
    """Mock out grpc.insecure_channel() import in the config module.

    As aio is imported by `from grpc import aio` in the config module we need to
    mock it out that way.
    """
    mock_insecure_channel: Mock = mocker.patch(
        "grpc.aio.insecure_channel", autospec=True
    )
    return mock_insecure_channel


@fixture
def mock_message_service_stub(mocker: MockerFixture) -> Mock:
    """Mock out MessageServiceStub import in the config module."""
    mock_message_service_stub: Mock = mocker.patch(
        "bitfount.federated.transport.config.MessageServiceStub", autospec=True
    )
    return mock_message_service_stub


@fixture
def mock_message_service() -> Mock:
    """Returns a mocked message service."""
    mock_message_service: Mock = create_autospec(_MessageService, instance=True)
    return mock_message_service


class PollForMessagesPatcher(Protocol):
    """Callback protocol for the poll_for_messages patcher."""

    def __call__(
        self,
        messages: Iterable[MessageOrException],
        finish: bool = False,
    ) -> MagicMock:
        """Call signature."""
        ...


@fixture
def patch_poll_for_messages(
    # this should be another fixture in the scope of the tests being run
    mock_message_service: Mock,
) -> PollForMessagesPatcher:
    """Returns a function that can be used to assign messages to yield."""

    def poll_for_messages_patcher(
        messages: Iterable[MessageOrException],
        finish: bool = False,
    ) -> MagicMock:
        """Assigns an iterable of messages to the yield of poll_for_messages.

        If finish is True the poll_for_messages will end after the messages in
        the iterable, otherwise it will "wait" indefinitely as though waiting for
        another message from the message service.
        """
        # Assign these to poll_for_messages which is the underlying method we
        # expect to yield messages.

        async def _mock_poll_for_messages(
            mailbox_id: str,
            stop_event: threading.Event,
        ) -> AsyncIterator[_BitfountMessage]:
            queue_: Queue[MessageOrException] = Queue()
            for message in messages:
                queue_.put_nowait(message)

            while not stop_event.is_set():
                try:
                    item = queue_.get_nowait()

                    # If an exception, raise it
                    if (
                        isinstance(item, BaseException)
                        or isinstance(item, type)
                        and issubclass(item, BaseException)
                    ):
                        raise item

                    # Otherwise yield it
                    yield item
                except QueueEmpty:
                    if finish:
                        return
                    else:
                        await asyncio.sleep(0)

        # Deliberately use MagicMock rather than AsyncMock here because we want
        # to force the wrapped method to return rather than returning a coroutine
        # wrapping the coroutine.
        mock_poll_for_messages = MagicMock(wraps=_mock_poll_for_messages)
        mock_message_service.poll_for_messages = mock_poll_for_messages
        return mock_poll_for_messages

    return poll_for_messages_patcher


class RpcErrorMaker(Protocol):
    """Callback Protocol defining a factory method for RPC errors."""

    def __call__(self, msg: str = ..., code: StatusCode = ...) -> RpcError:
        """Call the factory method."""
        ...


@fixture
def rpc_error_maker() -> RpcErrorMaker:
    """Creates factory method for creating gRPC error objects."""

    def _maker(
        msg: str = "Unknown error", code: StatusCode = StatusCode.UNKNOWN
    ) -> RpcError:
        """Create gRPC error instance.

        Args:
            msg: The error message to be associated with the error.
            code: The status code of the error.

        Returns:
            RpcError instance.
        """
        # Create fake RpcError, manually set code/details methods as valid RpcError
        # can't be created directly in Python code.
        err = RpcError(msg)
        err.code = lambda: code  # type: ignore[method-assign] # Reason: see comment # noqa: B950
        err.details = lambda: msg  # type: ignore[method-assign] # Reason: see comment # noqa: B950
        return err

    return _maker


@fixture
def rpc_error(rpc_error_maker: RpcErrorMaker) -> RpcError:
    """Creates an RpcError exception to use in mocking error message retrieval.

    Error code is "UNKNOWN".
    """
    return rpc_error_maker()


@fixture
def mock_message_timestamps(mocker: MockerFixture) -> Callable[[Iterable[str]], Mock]:
    """Returns a callable that will mock out message_service._current_time.

    Each call to _current_time() will instead return the next string in the supplied
    iterable.
    """

    def _message_timestamp_mocker(fake_timestamps: Iterable[str]) -> Mock:
        # Because of how dataclass default_factory works, patching
        # message_service._current_time won't be sufficient as it's already bound
        # to the dataclass. Instead we have to patch out the inner calls to datetime.
        mock_datetime: Mock = mocker.patch(
            "bitfount.federated.transport.message_service.datetime", autospec=True
        )
        mock_datetime.now.return_value.isoformat.side_effect = fake_timestamps
        return mock_datetime

    return _message_timestamp_mocker


@fixture(autouse=True)
def remove_grpc_retry_backoff_sleep(
    mocker: MockerFixture, request: PytestRequest
) -> Optional[AsyncMock]:
    """Removes backoff sleep for the gRPC auto_retry functionality.

    As we don't want to slow down tests unnecessarily, this fixture mocks out
    the sleep that would normally occur in the automatic retry of web interactions.
    """
    # Only mock it out for tests that don't actually perform web interactions
    # i.e. not e2e or tutorial tests
    if any(
        mark.name in request.keywords
        for mark in (unit_test, integration_test, end_to_end_mocks_test)
    ):
        # Need to patch entire imported module but only want to mock out `.sleep`
        # calls so set that explicitly to a Mock that isn't wrapping
        mock_async: Mock = mocker.patch(
            "bitfount.federated.transport.utils.asyncio", wraps=asyncio
        )
        mock_async.sleep = AsyncMock()
        return mock_async.sleep
    else:
        return None
