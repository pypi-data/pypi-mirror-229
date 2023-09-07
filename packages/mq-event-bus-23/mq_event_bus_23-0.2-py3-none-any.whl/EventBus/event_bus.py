from abc import ABC, abstractmethod
from functools import wraps
from typing import (
    Callable,
    Awaitable,
    Type
)

from EventBus.event import Event


class EventBus(ABC):
    Handler = Callable[[Event], Awaitable[None] | None]

    def on(self, event_name: Type[Event]):
        """ Decorator for subscribing a handler to an event
        """

        def wrapper(handler):
            self.subscribe(event_name, handler)

            @wraps(handler)
            def wrapped(*args, **kwargs):
                return handler(*args, **kwargs)

            return wrapped

        return wrapper

    @abstractmethod
    async def publish(self, event: Event) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def subscribe(self, event_type: Type[Event], handler: Handler) -> None:
        raise NotImplementedError()

    @abstractmethod
    def unsubscribe(self, event_type: Type[Event], handler: Handler) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def shutdown(self) -> None:
        raise NotImplementedError()
