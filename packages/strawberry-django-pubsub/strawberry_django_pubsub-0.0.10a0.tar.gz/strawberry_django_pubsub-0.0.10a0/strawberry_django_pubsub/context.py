from dataclasses import dataclass
from typing import Any, Dict, Optional

from strawberry.channels import GraphQLWSConsumer

from strawberry_django_pubsub.queue import ChannelsBroadcastContextQueue


@dataclass
class StrawberryDjangoWsContext:
    """
    A StrawberryDjangoWsContext context
    """

    request: GraphQLWSConsumer
    queue: Optional[ChannelsBroadcastContextQueue] = None
    connection_params: Optional[Dict[str, Any]] = None

    @property
    def ws(self) -> GraphQLWSConsumer:
        return self.request

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)
