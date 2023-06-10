"""
"""

from typing import Union, ClassVar
from pydantic import BaseModel, validator, conint
from enum import Enum
from math import ceil
from bitstring import BitArray
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
    @property
    def _attr_order(self):
        raise NotImplementedError("_attr_order should be defined on the child class.")


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

    def __add__(self, other) -> int:
        return self.value + other

    def __sub__(self, other) -> int:
        return self.value - other
    
    def __div__(self, other) -> int:
        return self.value / other

    def __truediv__(self, other) -> int:
        return self.value / other

    def __floordiv__(self, other) -> int:
        return self.value // other
    
    def __mul__(self, other) -> int:
        return self.value * other
    


class OcaSerialisableBase(OcaAbstractBase):

    @property
    def bytes(self) -> bytes:
        """
        Serialise the object using the `struct` module format string `_format`
        Any attribute beginning with "oca_" will be considered "exported" and passed to `struct.pack()`
        This allows for the use of properties and storing other data with the type, such as the format string.

        Returns:
            bytes: The data packed according to the format string
        """
        values = [ getattr(self, attr) for attr in self._attr_order ]
        
        # Handle any extra processing to get a given type's bytes
        getters = {
            str: lambda value: value.encode("UTF-8"),
            BitArray: lambda value: value.bytes
        }
        for i, value in enumerate(values):
            if (t := type(value)) in getters:
                values[i] = getters[t](value)
        
        return struct.pack(
            # Join all of the format strings for all contained types.
            # Byte order modifier `!` can only be at the start of the entire string.
            "!" + self._format.replace("!", ""),
            *values
        )


    @classmethod
    def from_bytes(cls, data: bytes) -> "OcaSerialisableBase":
        """
        Attempt to create an instance of `cls` from the `data` bytes.
        This relies on the class being a fixed length. If the `_format` string is dynamic, such as with `OcaString`
        then this method should be overridden by the child class with more specific unpacking behaviour.

        Args:
            data (bytes): _description_

        Returns:
            OcaSerialisableBase: _description_
        """
        if isinstance(cls._format, property):
            raise TypeError(f"Used inherited `from_bytes` from OcaSerialisableBase, but `_format` is a property. Implement `from_bytes` on {cls.__qualname__}!")
        values = struct.unpack(f"!{cls._format}", data)
        print(f"{values=}\n{cls._attr_order=}")
        if len(values) > 1:
            return cls(**dict(zip(cls._attr_order, *values)))
        return cls(**dict(zip(cls._attr_order, values)))


# == == == == == Base data types

class OcaBit(OcaAbstractBase):
    _format: ClassVar[str] = "B"
    _attr_order: ClassVar[list] = ["value"]
    value: int8


class OcaBoolean(OcaValueBase, OcaSerialisableBase):
    _format: ClassVar[str] = "?"
    _attr_order: ClassVar[list] = ["value"]
    value: bool


class OcaInt8(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "b"
    value: int8


class OcaInt16(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "h"
    value: int16


class OcaInt32(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "i"
    value: int32


class OcaInt64(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "q"
    value: int64


class OcaUint8(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "B"
    value: uint8


class OcaUint16(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "H"
    value: uint16


class OcaUint32(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "I"
    value: uint32


class OcaUint64(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "Q"
    value: uint64


class OcaFloat32(OcaValueBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "f"
    value: float #TODO how to constrain floats?


class OcaFloat64(OcaValueBase):
    _attr_order: ClassVar[list] = ["value"]
    _format: ClassVar[str] = "d"
    value: float #TODO how to constrain floats?


class OcaString(OcaValueBase, OcaSerialisableBase):
    _attr_order: ClassVar[list[str]] = ["length", "value"]

    @property
    def length(self) -> OcaUint16:
        return len(self.value)

    value: str

    @property
    def _format(self) -> str:
        return f"{OcaUint16._format}{len(self.value)}s"
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "OcaString":
        length, *_ = struct.unpack(f"!{OcaUint16._format}", data[:2])
        value, *_ = struct.unpack(f"!{length}s", data[2:])
        return cls(value.decode("UTF-8"))


class OcaBitstring(OcaSerialisableBase):
    _attr_order: ClassVar[list[str]] = ["num_bits", "bitstring"]

    class Config:
        arbitrary_types_allowed = True
        
    @property
    def num_bits(self) -> OcaUint8:
        return OcaUint16(len(self.bitstring))

    bitstring: BitArray

    def __len__(self) -> int:
        return self.num_bits

    @property
    def _format(self) -> str:
        return f"{OcaUint16._format}{ceil(self.num_bits / 8)}s"
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "OcaBitstring":
        length, *_ = struct.unpack(f"!{OcaUint16._format}", data[:2])
        values, *_ = struct.unpack(f"!{ceil(length / 8)}s", data[2:])
        return cls(num_bits=length, bitstring=BitArray(values))


class OcaBlob(OcaAbstractBase):
    _attr_order: ClassVar[list[str]] = ["data_size", "data"]
    data_size: OcaUint16
    data: list[OcaUint8]

    @property
    def _format(self) -> str:
        return f"{self.data_size}{OcaUint8._format}"


#NotImplemented
# class OcaBlobFixedLen(OcaBaseType):


class OcaList(OcaAbstractBase):
    _attr_order: ClassVar[list[str]] = ["template_type", "count", "items"]
    template_type: OcaAbstractBase
    count: OcaUint16
    items: list[OcaAbstractBase] # Of `template_type`

    @property
    def _format(self) -> str:
        return f"{self.count}{self.template_type._format}"


class OcaList2D(OcaAbstractBase):
    _attr_order: ClassVar[list[str]] = ["template_type", "num_x", "num_y", "items"]
    template_type: OcaAbstractBase
    num_x: OcaUint16
    num_y: OcaUint16
    items: list[list[OcaAbstractBase]] # of `template_type`

    @property
    def _format(self) -> str:
        raise NotImplementedError


class OcaMapItem(OcaAbstractBase):
    _attr_order: ClassVar[list[str]] = ["key_type", "value_type", "key", "value"]
    key_type: OcaAbstractBase
    value_type: OcaAbstractBase
    key: OcaAbstractBase # of `key_type`
    value: OcaAbstractBase # of `value_type`

    @property
    def _format(self) -> str:
        return f"{self.key_type._format}{self.value_type._format}"


class OcaMap(OcaAbstractBase):
    _attr_order: ClassVar[list[str]] = ["key_type", "value_type", "count", "items"]
    key_type: OcaAbstractBase
    value_type: OcaAbstractBase
    count: OcaUint16
    items: list[OcaMapItem]

    @property
    def _format(self) -> str:
        return f"{self.key_type._format}{self.value_type._format}" * self.count


class OcaMultiMap(OcaAbstractBase):
    _attr_order: ClassVar[list[str]] = ["key_type", "value_type", "count", "items"]
    key_type: OcaAbstractBase
    value_type: OcaAbstractBase
    count: OcaUint16
    items: list[OcaMapItem]

    @property
    def _format(self) -> str:
        return f"{self.key_type._format}{self.value_type._format}" * self.count


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