"""
OCP.1
-----

This contains the data structure definitions for OCP.1
"""

from pydantic import BaseModel, validator 
from asyncio import Queue
from typing import Any, Union, ClassVar
from ctypes import (
    c_int8,
    c_uint8,
    c_uint16,
    c_uint32,
)
from .occ import OcaMethodID
import enum
import struct

# AES70-3 5.6.1.1
SYNC_VAL = 0x3B

def _cast_int_to_i8(value: int) -> c_int8:
    return c_int8(value)

def _cast_int_to_u8(value: int) -> c_uint8:
    return c_uint8(value)

def _cast_int_to_u16(value: int) -> c_uint16:
    return c_uint16(value)

def _cast_int_to_u32(value: int) -> c_uint32:
    return c_uint32(value)


class MessageType(enum.Enum):
    COMMAND = 0
    COMMAND_RESPONSE_REQUIRED = 1
    NOTIFICATION = 2
    RESPONSE = 3
    KEEPALIVE = 4


class Ocp1PDU(BaseModel):
    """
    Base class for OCP1 Protocol Data Units (AES70-3 5.6)
    """
    class Config:
        arbitraary_types_allowed = True


class Ocp1Header(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    format: ClassVar[str] = "!hibh"

    protocol_version: Union[int, c_uint16]
    message_size: Union[int, c_uint32]
    message_type: Union[int, c_int8]
    message_count: Union[int, c_uint16]

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            self.format,
            self.protocol_version,
            self.message_size,
            self.message_type,
            self.message_count
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "Ocp1Header":
        unpacked_data = struct.unpack(cls.format, data)
        return cls(
            **dict(zip(cls.__fields__.keys(), unpacked_data))
        )
    
    @classmethod
    def __sizeof__(cls) -> int:
        return struct.calcsize(cls.format)


class Ocp1KeepAlive(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    heartbeat_sec: Union[int, c_uint16]


class Ocp1Parameters(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    parameters: list[Any]

    @property
    def parameter_count(self) -> int:
        return len(self.parameters)

    @property
    def bytes(self) -> struct.Struct:
        #TODO Parameters may be variable widths according to target object. This works for OcaSwitch because it takes a u16.
        return struct.pack(f"!B{self.parameter_count}H", self.parameter_count, *self.parameters)
    
    def __len__(self) -> int:
        return len(self.bytes)


class Ocp1Command(BaseModel):
    """
    The Command struct represents an OCP.1 command.

    Args:
        handle:     Command handle, used to match commands to responses
        target_ono: The target OCA object number
        method_id:  The target OCA method ID
        parameters: Parameters to pass to the invoked method
    """
    class Config:
        arbitrary_types_allowed = True

    handle: int
    target_ono: int
    method_id: OcaMethodID
    parameters: Ocp1Parameters

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            f"!3i4s{str(len(self.parameters))}s",
            len(self.parameters.bytes) + 16, # Length of parameters + u32 size, u32 handle, u32 ono, u32 method
            self.handle,
            self.target_ono,
            self.method_id.bytes,
            self.parameters.bytes
  
        )


class Ocp1CommandPdu(Ocp1PDU):
    sync_val: ClassVar[int] = SYNC_VAL
    header: Ocp1Header
    commands: list[Ocp1Command]

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            f"!B9s{sum([len(command.bytes) for command in self.commands])}s",
            self.sync_val,
            self.header.bytes,
            *[c.bytes for c in self.commands]
        )
    

class Ocp1NotificationPdu:
    def __init__(self):
        raise NotImplementedError


class Ocp1ResponsePdu:
    def __init__(self):
        raise NotImplementedError


class Ocp1KeepAlivePdu(Ocp1PDU):
    sync_val: ClassVar[int] = SYNC_VAL
    header: Ocp1Header
    heartbeat: int

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            "!B9sH",
            self.sync_val,
            self.header.bytes,
            self.heartbeat
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "Ocp1KeepAlivePdu":
        sync_val, header_bytes, heartbeat = struct.unpack("!B9sH", data)
        return cls(
            sync_val = sync_val,
            header = Ocp1Header.from_bytes(header_bytes),
            heartbeat = heartbeat
        ) 


# == == == == ==

PDU_CLASSES = {
    0: Ocp1CommandPdu,
    1: Ocp1CommandPdu,
    2: Ocp1NotificationPdu,
    3: Ocp1ResponsePdu,
    4: Ocp1KeepAlivePdu
}


def marshal(data: bytes) -> Ocp1PDU:
    """
    Parse serialised packets back into OCP1 objects

    Args:
        data: bytes to parse

    Returns:
        Ocp1PDU: Parsed data
    """
    #TODO - How to handle bad sync value here?
    header_offset = 1 
    header_end = header_offset + Ocp1Header.__sizeof__()
    header = Ocp1Header.from_bytes(data[header_offset : header_end])
    pdu_type = PDU_CLASSES[header.message_type]
    return pdu_type.from_bytes(data)
