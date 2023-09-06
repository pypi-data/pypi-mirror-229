import hashlib

from dataclasses import dataclass
from typing import Any
from typing import Iterable


class SerializableMixin(object):
    serializer: callable = None

    def get_serializer(self) -> callable:
        return self.serializer or self.serialize

    @classmethod
    def serialize(cls, value):
        raise NotImplementedError


@dataclass
class KafkaMessage:
    command: str = '.'  # `.` is a default command
    data: Any = None


class HashableProducerMixin(object):
    hash_fields: Iterable  # ordering matters
    hash_sum_attr_name: str = 'hash_sum'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        values = [str(attrs.get(field)) for field in self.get_hash_fields()]
        hash_sum = hashlib.md5(":".join(values).encode()).hexdigest()
        attrs[self.hash_sum_attr_name] = hash_sum
        return attrs

    def get_hash_fields(self):
        return self.hash_fields
