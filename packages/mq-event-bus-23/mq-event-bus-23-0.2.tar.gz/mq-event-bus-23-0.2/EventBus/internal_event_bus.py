import asyncio
import inspect
from asyncio import AbstractEventLoop, Task
from collections import Counter
from collections import defaultdict
from dataclasses import field, dataclass
from typing import (
    Callable,
    Type,
    Dict,
    Coroutine
)

from EventBus.event_bus import EventBus, Event
from EventBus.exceptions import EventTypeNotSubscribed, HandlerNotFound


@dataclass
class InternalEventBus(EventBus):
    Handler: Callable[[Event], Coroutine | None] = field(
        default_factory=lambda: Callable[[Event], Coroutine | None]
    )

    event_handlers: dict[Type[Event], list[Handler]] = field(
        default_factory=lambda: defaultdict(list)
    )

    event_loop: AbstractEventLoop = field(
        default_factory=asyncio.get_running_loop  # Get the current event loop.
    )

    active_handlers: list[Task] = field(
        default_factory=list
    )

    def __repr__(self) -> str:
        """ Returns EventBus string representation

        :return: Instance with how many subscribed events
        """
        return "<{}: {} subscribed events>".format(
            self.__class__.__name__,
            self._subscribed_event_count
        )

    def __str__(self) -> str:
        """ Returns EventBus string representation

        :return: Instance with how many subscribed events
        """
        return "{}".format(self.__class__.__name__)

    def _subscribed_event_count(self) -> int:
        """ Returns the total amount of subscribed events

        :return: Total amount of subscribed events
        """
        event_counter: Dict[Type[Event], int] = Counter()

        for key, values in self.event_handlers.items():
            event_counter[key] = len(values)

        return sum(event_counter.values())

    def publish(self, event: Event) -> None:
        # if the event type does not match, nothing happens
        if type(event) not in self.event_handlers:
            return

        for handler in self.event_handlers[type(event)]:
            # checking a function for asynchrony
            if inspect.iscoroutinefunction(handler):
                task = self.event_loop.create_task(handler(event))
            else:
                loop = asyncio.to_thread(handler, event)
                task = self.event_loop.create_task(loop)
            task.add_done_callback(self.active_handlers.remove)
            self.active_handlers.append(task)

    def subscribe(self, event_type: Type[Event], handler: Handler) -> None:
        self.event_handlers[event_type].append(handler)

    def unsubscribe(self, event_type: Type[Event], handler: Handler) -> None:
        if event_type not in self.event_handlers:
            raise EventTypeNotSubscribed(event_type)

        handlers = self.event_handlers[event_type]

        if handler not in handlers:
            raise HandlerNotFound(event_type, handler)

        handlers.remove(handler)
        if len(handlers) == 0:
            self.event_handlers.pop(event_type)

    async def wait_for_handlers(self):
        # 'asyncio.wait', cannot accept empty active_handlers
        if len(self.active_handlers) == 0:
            return

        await asyncio.wait(
            self.active_handlers,
            timeout=None,
            return_when=asyncio.ALL_COMPLETED
        )

    async def shutdown(self):
        for active_handler in self.active_handlers:
            active_handler.cancel()
