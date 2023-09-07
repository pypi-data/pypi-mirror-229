import datetime

import django.core.serializers
import django.db
import msgpack
import strawberry
from asgiref.sync import sync_to_async


@sync_to_async
def serialize(data):
    """Serialize the `data`."""
    try:

        def encode_extra_types(obj: dict):
            """OrJSON hook to serialize extra types."""

            if hasattr(obj, '__strawberry_definition__'):
                return {
                    "__strawberry__": True,
                    "as_str": strawberry.asdict(
                        obj
                    ),  # json.dumps(obj, default=lambda o: o.__dict__),
                }

            if isinstance(obj, django.db.models.Model):
                return {
                    "__djangomodel__": True,
                    "as_str": django.core.serializers.serialize("json", [obj]),
                }

            return obj

        return msgpack.packb(data, default=encode_extra_types, use_bin_type=True)
    except Exception as e:
        print(e)


@sync_to_async
def deserialize(data):
    """Deserialize the `data`."""

    if not data:
        return {"payload": None}

    def decode_extra_types(obj):
        """MessagePack hook to deserialize extra types."""

        if "__djangomodel__" in obj:
            obj = next(
                django.core.serializers.deserialize("json", obj["as_str"])
            ).object

            obj.refresh_from_db()
        elif "__strawberry__" in obj:
            obj = obj["as_str"]

        elif "__datetime__" in obj:
            obj = datetime.datetime.fromisoformat(obj["as_str"])
        elif "__date__" in obj:
            obj = datetime.date.fromisoformat(obj["as_str"])
        elif "__time__" in obj:
            obj = datetime.time.fromisoformat(obj["as_str"])
        return obj

    unpacked = msgpack.unpackb(data, object_hook=decode_extra_types, raw=False)
    return {"payload": unpacked}
