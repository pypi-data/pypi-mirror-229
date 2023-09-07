from typing import Callable, Awaitable, Type

from EventBus.event_bus import Event


class EventTypeNotSubscribed(Exception):
    def __init__(self, event_type: Type[Event]):
        self.event_type = event_type
        self.message = "Event " + f"'{self.event_type}'" + " not found in Handler"
        super().__init__(self.message)


class HandlerNotFound(Exception):
    def __init__(self, event_type: Type[Event], handler: Callable[[Event], Awaitable[None]]):
        self.handler = handler
        self.event_type = event_type
        self.message = "Handler " + f"'{self.handler}'" + " not found with this " + f"'{self.event_type}'"
        super().__init__(self.message)
