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
    
    def __init__(self, oca_value) -> None:
        super().__init__(oca_value=oca_value)
    
    def __str__(self) -> str:
        return str(self.oca_value)
    
    def __int__(self) -> int:
        return int(self.oca_value)

    def __index__(self) -> int:
        return int(self.oca_value)
    
    def __bool__(self) -> bool:
        return bool(self.oca_value)
    
    def __eq__(self, other) -> bool:
        return other == self.oca_value


class SerialisableBase(OcaAbstractBase):

    @property
    def bytes(self) -> bytes:
        """
        Serialise the object using the `struct` module format string `_format`
        Any attribute beginning with "oca_" will be considered "exported" and passed to `struct.pack()`
        This allows for the use of properties and storing other data with the type, such as the format string.

        Returns:
            bytes: The data packed according to the format string
        """
        values = [
            getattr(self, attr)
            for attr in dir(self)
            if attr.startswith("oca_")
        ]
        
        # Strings must be encoded when packed
        values = [v.encode("UTF-8") if isinstance(v, str) else v for v in values]

        return struct.pack(
            "!" + self._format.replace("!", ""),
            *values
        )


    @classmethod
    def from_bytes(cls, data: bytes) -> "SerialisableBase":
        attributes = struct.unpack("!" + cls._format.replace("!", ""), data)
        fields = [field for field in cls.__fields__.keys() if not field.startswith("_")]
        if len(attributes) > 1:
            return cls(**dict(zip(fields, *attributes)))
        return cls(**dict(zip(fields, attributes)))


# == == == == == Base data types

class OcaBit(OcaAbstractBase):
    _format: ClassVar[str] = "B"
    oca_value: int8


class OcaBoolean(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "?"
    oca_value: bool


class OcaInt8(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "b"
    oca_value: int8


class OcaInt16(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "h"
    oca_value: int16


class OcaInt32(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "i"
    oca_value: int32


class OcaInt64(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "q"
    oca_value: int64


class OcaUint8(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "B"
    oca_value: uint8


class OcaUint16(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "H"
    oca_value: uint16


class OcaUint32(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "I"
    oca_value: uint32


class OcaUint64(OcaValueBase, SerialisableBase):
    _format: ClassVar[str] = "Q"
    oca_value: uint64


class OcaFloat32(OcaValueBase):
    _format: ClassVar[str] = "f"
    oca_value: float #TODO how to constrain floats?


class OcaFloat64(OcaValueBase):
    _format: ClassVar[str] = "d"
    oca_value: float #TODO how to constrain floats?


class OcaString(OcaValueBase, SerialisableBase):
    @property
    def oca_length(self) -> OcaUint16:
        return len(self.oca_value)

    oca_value: str

    @property
    def _format(self) -> str:
        return f"{OcaUint16._format}{len(self.oca_value)}s"


class OcaBitstring(OcaAbstractBase):
    oca_num_bits: OcaUint16
    oca_bitstring: list[OcaUint8]

    def __len__(self) -> int:
        return self.oca_num_bits

    @property
    def _format(self) -> str:
        return f"{ceil(self.oca_num_bits / 8)}{OcaUint8._format}"


class OcaBlob(OcaAbstractBase):
    oca_data_size: OcaUint16
    oca_data: list[OcaUint8]

    @property
    def _format(self) -> str:
        return f"{self.oca_data_size}{OcaUint8._format}"


#NotImplemented
# class OcaBlobFixedLen(OcaBaseType):


class OcaList(OcaAbstractBase):
    oca_template_type: OcaAbstractBase
    oca_count: OcaUint16
    oca_items: list["template_type"]

    @property
    def _format(self) -> str:
        return f"{self.oca_count}{self.oca_data_type._format}"


class OcaList2D(OcaAbstractBase):
    oca_template_type: OcaAbstractBase
    oca_num_x: OcaUint16
    oca_num_y: OcaUint16
    oca_items: list[list["template_type"]]

    @property
    def _format(self) -> str:
        raise NotImplementedError


class OcaMapItem(OcaAbstractBase):
    oca_key_type: OcaAbstractBase
    oca_value_type: OcaAbstractBase
    oca_key: "key_type"
    oca_value: "value_type"

    @property
    def _format(self) -> str:
        return f"{self.oca_key_type._format}{self.oca_value_type._format}"


class OcaMap(OcaAbstractBase):
    oca_key_type: OcaAbstractBase
    oca_value_type: OcaAbstractBase
    oca_count: OcaUint16
    oca_items: list[OcaMapItem]

    @property
    def _format(self) -> str:
        return f"{self.oca_key_type._format}{self.oca_value_type._format}" * self.oca_count


class OcaMultiMap(OcaAbstractBase):
    oca_key_type: OcaAbstractBase
    oca_value_type: OcaAbstractBase
    oca_count: OcaUint16
    oca_items: list[OcaMapItem]

    @property
    def _format(self) -> str:
        return f"{self.oca_key_type._format}{self.oca_value_type._format}" * self.oca_count


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