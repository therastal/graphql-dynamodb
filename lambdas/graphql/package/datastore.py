import asyncio
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional, TypeVar

import strawberry
from pynamodb.attributes import (
    Attribute,
    DiscriminatorAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.constants import NUMBER, STRING, STRING_SET
from pynamodb.models import Model

TABLE_NAME = os.getenv("DATASTORE_NAME")
T = TypeVar("T", bound="_Item")

# region Public functions
async def get_dt(field: str, uid: strawberry.ID) -> datetime:
    return (await _DateTimeItem.async_get(field, uid)).value


async def get_dec(field: str, uid: strawberry.ID) -> Decimal:
    return (await _DecimalItem.async_get(field, uid)).value


async def get_int(field: str, uid: strawberry.ID) -> int:
    return (await _IntegerItem.async_get(field, uid)).value


async def get_str(field: str, uid: strawberry.ID) -> str:
    return (await _StringItem.async_get(field, uid)).value


async def get_ref(field: str, uid: strawberry.ID, type_: type):
    id = (await _RefItem.async_get(field, uid)).value
    return type_(id=id)


async def get_refs(field: str, uid: str, type_: type) -> Optional[list]:
    ids = (await _RefListItem.async_get(field, uid)).value
    return [type_(id=id) for id in ids] or None


# endregion


# region Attributes
class _IDAttribute(Attribute[strawberry.ID]):
    attr_type = STRING

    def serialize(self, value: strawberry.ID) -> str:
        return str(value)

    def deserialize(self, value: str) -> strawberry.ID:
        return strawberry.ID(value)


class _IDListAttribute(Attribute[list[strawberry.ID]]):
    attr_type = STRING_SET
    null = True

    def serialize(self, value):
        return [str(v) for v in value] or None

    def deserialize(self, value) -> list[strawberry.ID]:
        return [strawberry.ID(v) for v in value]


class _IntegerAttribute(Attribute[int]):
    attr_type = NUMBER

    def serialize(self, value) -> str:
        return json.dumps(int(value))

    def deserialize(self, value) -> int:
        return int(json.loads(value))


class _DecimalAttribute(Attribute[Decimal]):
    attr_type = STRING

    def serialize(self, value: Decimal) -> str:
        return str(value)

    def deserialize(self, value: str) -> Decimal:
        return Decimal(value)


# endregion

# region Models
class _Item(Model):
    class Meta:
        table_name = TABLE_NAME

    pk = UnicodeAttribute(hash_key=True)
    sk = _IDAttribute(range_key=True)
    datatype = DiscriminatorAttribute()

    @classmethod
    async def async_get(cls: type[T], *args, **kwargs) -> T:
        return await asyncio.to_thread(super().get, *args, **kwargs)


class _DateTimeItem(_Item, discriminator="datetime"):
    value = UTCDateTimeAttribute()


class _DecimalItem(_Item, discriminator="decimal"):
    value = _DecimalAttribute()


class _StringItem(_Item, discriminator="string"):
    value = UnicodeAttribute()


class _IntegerItem(_Item, discriminator="integer"):
    value = _IntegerAttribute()


class _RefItem(_Item, discriminator="id"):
    value = _IDAttribute()


class _RefListItem(_Item, discriminator="id_list"):
    value = _IDListAttribute()


# endregion
