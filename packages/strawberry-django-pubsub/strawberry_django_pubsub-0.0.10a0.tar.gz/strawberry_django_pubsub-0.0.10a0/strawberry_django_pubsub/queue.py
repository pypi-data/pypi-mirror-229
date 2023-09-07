import sys
import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, AsyncIterator, Optional

from channels.layers import get_channel_layer
from strawberry.channels.handlers.base import ChannelsLayer, ChannelsWSConsumer

from strawberry_django_pubsub.event import Event
from strawberry_django_pubsub.serializer import deserialize, serialize


class ChannelSubscriber:
    """Subscriber to handle Channel AsyncGeneratorContext messages"""

    def __init__(self, ws: "ChannelsWSConsumer", channel: str) -> None:
        self.ws = ws
        self.channel = channel

    async def __aiter__(self) -> Optional[AsyncGenerator["Event", None]]:
        """
        generator to fetch Event, this methods keeps on listening
        until it's iterator stops.
        """
        async with self.ws.listen_to_channel(
            self.channel, groups=["broadcast"]
        ) as subscriber:
            async for event in subscriber:
                payload = await deserialize(event["payload"])
                yield Event(channel=self.channel, payload=payload["payload"])


class ChannelsBroadcastContextQueue:
    def __init__(self, ws: ChannelsWSConsumer):
        self.ws: ChannelsWSConsumer = ws
        self.channel_layer: ChannelsLayer = ws.channel_layer

    async def publish(self, channel: str, payload: Any) -> None:
        data = await serialize(payload)
        await self.channel_layer.group_send(
            "broadcast", {"type": channel, "payload": data}
        )

    @asynccontextmanager
    async def subscribe(self, channel: str) -> AsyncIterator["Event"]:
        """
        subscribe to channel and start listening for events on from ChannelLayer
        """
        try:
            yield ChannelSubscriber(ws=self.ws, channel=channel)
        except Exception as e:
            print(e)
            print(
                "".join(
                    traceback.format_exception(
                        sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
                    )
                )
            )


class ChannelsBroadcast:
    async def publish(self, channel: str, payload: Any) -> None:
        channel_layer = get_channel_layer()
        data = await serialize(payload)
        await channel_layer.group_send("broadcast", {"type": channel, "payload": data})


queue = None


async def get_queue() -> ChannelsBroadcast:
    global queue
    if not queue:
        queue = ChannelsBroadcast()

    return queue
