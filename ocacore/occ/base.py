"""
"""

from typing import Union, ClassVar
from pydantic import BaseModel, validator, conint
from enum import Enum
from math import ceil
import struct


int8 = conint(ge=-0x80, le=0x7F)
int16 = conint(ge=-0x80_00, le=0x7F_FF)
int32 = conint(ge=-0x80_00_00_00, le=0x7F_FF_FF_FF)
int64 = conint(ge=-0x80_00_00_00_00_00_00_00, le=0x7F_FF_FF_FF_FF_FF_FF_FF)
uint8 = conint(ge=0, le=0xFF)
uint16 = conint(ge=0, le=0xFF_FF)
uint32 = conint(ge=0, le=0xFF_FF_FF_FF)
uint64 = conint(ge=0, le=0xFF_FF_FF_FF_FF_FF_FF_FF)


class OcaAbstractBase(BaseModel):
    """ Base type for all OCC classes. Does not implement anything, only used for typing """
    pass


class OcaValueBase(OcaAbstractBase):
    """ Base type for simple types to add dunder methods for the `value` field """
    
    def __init__(self, value) -> None:
        super().__init__(value=value)
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return int(self.value)

    def __index__(self) -> int:
        return int(self.value)
    
    def __bool__(self) -> bool:
        return bool(self.value)
    
    def __eq__(self, other) -> bool:
        return other == self.value


class SerialisableBase(OcaAbstractBase):

    @property
    def bytes(self) -> bytes:
        attributes = dict(self)
        return struct.pack(
            "!" + self.format.replace("!", ""),
            *[value for value in attributes.values()]
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "SerialisableBase":
        attributes = struct.unpack("!" + cls.format.replace("!", ""), data)
        fields = cls.__fields__.keys()
        if len(attributes) > 1:
            return cls(**dict(zip(fields, *attributes)))
        return cls(**dict(zip(fields, attributes)))


# == == == == == Base data types

class OcaBit(OcaAbstractBase):
    format: ClassVar[str] = "B"
    value: int8


class OcaBoolean(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "?"
    value: bool


class OcaInt8(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "b"
    value: int8


class OcaInt16(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "h"
    value: int16


class OcaInt32(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "i"
    value: int32


class OcaInt64(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "q"
    value: int64


class OcaUint8(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "B"
    value: uint8


class OcaUint16(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "H"
    value: uint16


class OcaUint32(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "I"
    value: uint32


class OcaUint64(OcaValueBase, SerialisableBase):
    format: ClassVar[str] = "Q"
    value: uint64


class OcaFloat32(OcaValueBase):
    format: ClassVar[str] = "f"
    value: float #TODO how to constrain floats?


class OcaFloat64(OcaValueBase):
    format: ClassVar[str] = "d"
    value: float #TODO how to constrain floats?


class OcaString(OcaValueBase, SerialisableBase):
    @property
    def length(self) -> OcaUint16:
        return len(self.value)

    value: str

    @property
    def format(self) -> str:
        return f"{OcaUint16.format}{len(self.value)}s"


class OcaBitstring(OcaAbstractBase):
    num_bits: OcaUint16
    bitstring: list[OcaUint8]

    def __len__(self) -> int:
        return self.num_bits

    @property
    def format(self) -> str:
        return f"{ceil(self.num_bits / 8)}{OcaUint8.format}"


class OcaBlob(OcaAbstractBase):
    data_size: OcaUint16
    data: list[OcaUint8]

    @property
    def format(self) -> str:
        return f"{self.data_size}{OcaUint8.format}"


#NotImplemented
# class OcaBlobFixedLen(OcaBaseType):


class OcaList(OcaAbstractBase):
    template_type: OcaAbstractBase
    count: OcaUint16
    items: list["template_type"]

    @property
    def format(self) -> str:
        return f"{self.count}{self.data_type.format}"


class OcaList2D(OcaAbstractBase):
    template_type: OcaAbstractBase
    num_x: OcaUint16
    num_y: OcaUint16
    items: list[list["template_type"]]

    @property
    def format(self) -> str:
        raise NotImplementedError


class OcaMapItem(OcaAbstractBase):
    key_type: OcaAbstractBase
    value_type: OcaAbstractBase
    key: "key_type"
    value: "value_type"

    @property
    def format(self) -> str:
        return f"{self.key_type.format}{self.value_type.format}"


class OcaMap(OcaAbstractBase):
    key_type: OcaAbstractBase
    value_type: OcaAbstractBase
    count: OcaUint16
    items: list[OcaMapItem]

    @property
    def format(self) -> str:
        return f"{self.key_type.format}{self.value_type.format}" * self.count


class OcaMultiMap(OcaAbstractBase):
    key_type: OcaAbstractBase
    value_type: OcaAbstractBase
    count: OcaUint16
    items: list[OcaMapItem]

    @property
    def format(self) -> str:
        return f"{self.key_type.format}{self.value_type.format}" * self.count


# == == == == == 


oca_base_data_type = {
    0: None,
    1: OcaInt8,
    2: OcaInt16,
    3: OcaInt16,
    4: OcaInt32,
    5: OcaInt64,
    6: OcaUint8,
    7: OcaUint16,
    8: OcaUint32,
    9: OcaUint64,
    10: OcaFloat32,
    11: OcaFloat64,
    12: OcaString,
    13: OcaBitstring,
    14: OcaBlob,
    15: "OcaBlobFixedLen",
    16: OcaBit
}