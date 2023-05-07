"""
OCP.1
-----

This contains the data structure definitions for OCP.1
"""

from pydantic import BaseModel, validator
from asyncio import Queue
from typing import Any, Union
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


class Ocp1Header(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    protocol_version: Union[int, c_uint16]
    message_size: Union[int, c_uint32]
    message_type: Union[int, c_int8]
    message_count: Union[int, c_uint16]

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            "!hibh",
            self.protocol_version,
            self.message_size,
            self.message_type,
            self.message_count
        )


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


class Ocp1CommandPdu(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    header: Ocp1Header
    commands: list[Ocp1Command]

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            f"!B9s{sum([len(command.bytes) for command in self.commands])}s",
            SYNC_VAL,
            self.header.bytes,
            *[c.bytes for c in self.commands]
        )


class Ocp1NotificationPdu:
    def __init__(self):
        raise NotImplementedError


class Ocp1ResponsePdu:
    def __init__(self):
        raise NotImplementedError


class Ocp1KeepAlivePdu(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    header: Ocp1Header
    heartbeat: Union[int, c_uint16]

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            "!B9sH",
            SYNC_VAL,
            self.header.bytes,
            self.heartbeat
        )


PDU_CLASSES = {
    MessageType.COMMAND: Ocp1CommandPdu,
    MessageType.COMMAND_RESPONSE_REQUIRED: Ocp1CommandPdu,
    MessageType.NOTIFICATION: Ocp1NotificationPdu,
    MessageType.RESPONSE: Ocp1ResponsePdu,
    MessageType.KEEPALIVE: Ocp1KeepAlivePdu
}