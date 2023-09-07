import asyncio
import json
from asyncio import AbstractEventLoop
from collections import Counter
from collections import defaultdict
from dataclasses import field, dataclass, asdict
from typing import (
    Callable,
    Type,
    Coroutine, Optional, Dict
)
from uuid import uuid4

import aio_pika
from aio_pika.abc import (AbstractRobustConnection, AbstractRobustChannel,
                          AbstractRobustExchange, ExchangeType,
                          AbstractIncomingMessage)

from EventBus.config import RabbitmqConfig
from EventBus.event import Event
from EventBus.event_bus import EventBus
from EventBus.exceptions import EventTypeNotSubscribed, HandlerNotFound


@dataclass
class RabbitMQEventBus(EventBus):
    Handler = Callable[[Event], Coroutine | None]

    rabbitmq_config: RabbitmqConfig = field(
        init=True
    )
    connection: AbstractRobustConnection = field(init=False)
    channel: AbstractRobustChannel = field(init=False)
    exchange: AbstractRobustExchange = field(init=False)

    event_handlers: dict[str, list[Handler]] = field(
        default_factory=lambda: defaultdict(list)
    )
    event_queues: dict[Type[Event], list[Handler]] = field(
        default_factory=lambda: defaultdict(list)
    )

    event_loop: AbstractEventLoop = field(
        default_factory=asyncio.get_running_loop  # Get the current event loop.
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

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(
                self.rabbitmq_config.AMPQ_URI
            )
            self.channel = await self.connection.channel()

            self.exchange = await self.channel.declare_exchange(
                "event_bus",
                type=ExchangeType.TOPIC
            )
        except Exception as e:
            print(e)
            await asyncio.sleep(3)
            return await self.connect()

    def subscribe(self, event_type: Type[Event], handler: Handler) -> None:
        self.event_handlers[event_type].append(handler)

    async def _start_consuming(self, event_type: Type[Event]):
        event_queue = await self.channel.declare_queue(exclusive=True, durable=True)
        await event_queue.bind(self.exchange, routing_key=event_type.name)

        async def foo(message: AbstractIncomingMessage):
            async with message.process():
                serialized_event = json.loads(message.body.decode('utf-8'))

                # TODO: you need to fix the Event class so as not to remove fields, but simply unpack
                del serialized_event['id']
                del serialized_event['name']

                handlers_our_event = self.event_handlers.get(event_type, [])

                await asyncio.gather(*[handler(event_type(**serialized_event)) for handler in handlers_our_event])

        await event_queue.consume(foo, no_ack=False)

    async def start_consuming(self):
        for event_type in self.event_handlers:
            await self._start_consuming(event_type)
        await asyncio.sleep(0.1)
        await asyncio.Future()

    @staticmethod
    def _create_message(data: bytes, message_id: Optional[str] = None):
        return aio_pika.Message(
            body=data,
            content_type="application/json",
            content_encoding="utf-8",
            message_id=message_id or uuid4().hex,
            delivery_mode=aio_pika.abc.DeliveryMode.PERSISTENT
        )

    async def publish(self, event: Event) -> None:
        event_queue = await self.channel.declare_queue(type(event).name, durable=True)
        await event_queue.bind(self.exchange)

        serialized_event = json.dumps(asdict(event))

        await self.exchange.publish(
            message=self._create_message(
                serialized_event.encode(),
                event.id
            ),
            routing_key=event.name
        )

    def unsubscribe(self, event_type: Type[Event], handler: Handler) -> None:
        if event_type not in self.event_handlers:
            raise EventTypeNotSubscribed(event_type)

        handlers = self.event_handlers[event_type]

        if handler not in handlers:
            raise HandlerNotFound(event_type, handler)

        handlers.remove(handler)
        if len(handlers) == 0:
            self.event_handlers.pop(event_type)

    async def shutdown(self):
        await self.channel.close()
        await self.connection.close()
