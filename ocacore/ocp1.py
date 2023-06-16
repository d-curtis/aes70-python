"""
OCP.1
-----

This contains the data structure definitions for OCP.1
"""

from pydantic import BaseModel
from typing import Any, Union, ClassVar, Optional, TypedDict
from ocacore.occ.types import *
import enum
import struct

# AES70-3 5.6.1.1
SYNC_VAL = 0x3B

HandleRegistry = dict[uint32, "Ocp1Command"]

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
    
    _format: ClassVar[str] = "".join([
        "!",
        OcaUint16._format,
        OcaUint32._format,
        "B",
        OcaUint16._format
    ])

    protocol_version: OcaUint16
    message_size: OcaUint32
    message_type: MessageType
    message_count: OcaUint16

    @validator("message_type")
    def _cast_message_type(val: MessageType) -> uint8:
        return uint8(val.value)

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            self._format,
            self.protocol_version,
            self.message_size,
            self.message_type,
            self.message_count
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "Ocp1Header":
        (
            protocol_version, 
            message_size, 
            message_type, 
            message_count 
        ) = struct.unpack(cls._format, data)
        return cls(
            protocol_version=OcaUint16(protocol_version),
            message_size=OcaUint32(message_size),
            message_type=MessageType(message_type),
            message_count=OcaUint16(message_count)
        )
    
    @classmethod
    def __sizeof__(cls) -> int:
        return struct.calcsize(cls._format)


class Ocp1KeepAlive(BaseModel):
    heartbeat_sec: OcaUint16


class Parameter(BaseModel):
    value: Any
    _format: str # struct format string


class Ocp1Parameters(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    parameters: Union[list[Parameter], None]

    @property
    def parameter_count(self) -> uint8:
        return 0 if self.parameters is None else len(self.parameters)

    @property
    def bytes(self) -> struct.Struct:
        if self.parameters is None:
            return struct.pack("!B", 0)
        parameters_format = "".join(p._format for p in self.parameters)
        return struct.pack(f"!B{parameters_format}", self.parameter_count, *[p.value for p in self.parameters])
    
    @classmethod
    def from_bytes(cls, data: bytes, *args, **kwargs) -> "Ocp1Parameters":
        parameter_count = struct.unpack("!B", data[0])
        #TODO - Parameters will be variable length according to the invoked method.
        #       This needs a way of knowing what the format should be for us to unpack correctly.
        #       For now, let's just store the byte array and deal with it Soon(tm)...
        parameters = [Parameter(value=data[1:], _format="No clue m8")]
        return cls(parameters=parameters)


    def __len__(self) -> int:
        return len(self.parameters)
    
    def __sizeof__(self) -> int:
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

    handle: uint32
    target_ono: uint32
    method_id: OcaMethodID
    parameters: Ocp1Parameters
    response_format: Optional[list[str]]

    @property
    def bytes(self) -> struct.Struct:
        param_len = self.parameters.__sizeof__()
        return struct.pack(
            "!3i4s" + (f"{param_len}s" if param_len else ""),
            self.parameters.__sizeof__() + 16,
            self.handle,
            self.target_ono,
            self.method_id.bytes,
            self.parameters.bytes
        )
    
    def __sizeof__(self) -> int:
        return len(self.bytes)


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
    
    @classmethod
    def from_bytes(cls, data: bytes, *args, **kwargs) -> "Ocp1CommandPdu":
        pass
        
    

class Ocp1NotificationPdu:
    def __init__(self):
        raise NotImplementedError


class Ocp1Response(BaseModel):
    response_size: OcaUint32 # u32
    handle: OcaUint32 # u32
    status_code: OcaStatus # OcaStatus
    parameters: Ocp1Parameters
    
    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            f"!iiB{self.parameters.__sizeof__()}s",
            self.response_size,
            self.handle,
            self.status_code,
            self.parameters.bytes
        )
    
    @classmethod
    def handle_from_bytes(cls, data: bytes) -> int:
        _, handle = struct.unpack("!ii", data[:8])
        return handle
    
    @classmethod
    def from_bytes(cls, data: bytes, handle_registry: HandleRegistry, *args, **kwargs) -> "Ocp1Response":
        response_size, handle, status_code = struct.unpack("!iiB", data[:9])
        parameter_len = response_size - struct.calcsize("!iiB")
        parameters = struct.unpack(f"!{parameter_len}B", data[9:])
        return cls(
            response_size=response_size,
            handle=handle,
            status_code=status_code,
            parameters=Ocp1Parameters(parameters=parameters, format="#TODOOOOO") #TODO see note in Ocp1Parameters
        )


class Ocp1ResponsePdu(Ocp1PDU):
    sync_val: ClassVar[int] = SYNC_VAL
    header: Ocp1Header
    responses: list[Ocp1Response]
    
    @property
    def bytes(self) -> struct.Struct:
        response_size = sum(response.__sizeof__() for response in self.responses)
        return struct.pack(
            f"!B9s{response_size}s",
            self.sync_val,
            self.header,
            self.responses
        )
    
    @classmethod
    def from_bytes(cls, data: bytes, handle_registry: HandleRegistry, *args, **kwargs) -> "Ocp1ResponsePdu":
        #TODO Need to know the method that was invoked, response handle will match, so register this somewhere to know the format of the parameters
        sync_val, header_bytes = struct.unpack(f"!b9s", data[:10]) 
        header = Ocp1Header.from_bytes(header_bytes)
        data = data[10:] # strip header bytes
        
        # The response format depends on the command it is responding to.
        # We can look this up using the `handle` number, bundled with the response.
        for response_i in range(header.message_count):
            handle = Ocp1Response.handle_from_bytes(data)
            source_command = handle_registry[handle]
            breakpoint()
            #TODO: Looks like I need to define local models for alllll of the control classes, in order to know the return types...

        # return cls(
        #     sync_val = sync_val,
        #     header = Ocp1Header.from_bytes(header_bytes)
        #     responses = [Ocp1Response.from_bytes()]
        # )


class Ocp1KeepAlivePdu(Ocp1PDU):
    sync_val: ClassVar[int] = SYNC_VAL
    _format: ClassVar[int] = "".join([
        "!",
        "B",
        str(Ocp1Header.__sizeof__()) + "s",
        OcaUint16._format
    ])
    header: Ocp1Header
    heartbeat: OcaUint16

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            self._format,
            self.sync_val,
            self.header.bytes,
            self.heartbeat
        )
    
    @classmethod
    def from_bytes(cls, data: bytes, *args, **kwargs) -> "Ocp1KeepAlivePdu":
        sync_val, header_bytes, heartbeat = struct.unpack(cls._format, data)
        return cls(
            sync_val = sync_val,
            header = Ocp1Header.from_bytes(header_bytes),
            heartbeat = OcaUint16(heartbeat)
        ) 


# == == == == ==

PDU_CLASSES = {
    0: Ocp1CommandPdu,
    1: Ocp1CommandPdu, # Response required
    2: Ocp1NotificationPdu,
    3: Ocp1ResponsePdu,
    4: Ocp1KeepAlivePdu
}


def marshal(data: bytes, handle_registry: HandleRegistry) -> Ocp1PDU:
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
    return pdu_type.from_bytes(data, handle_registry)
