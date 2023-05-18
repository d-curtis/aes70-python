from ocacore.occ.base import *
from typing import ClassVar
from enum import Enum


OcaApplicationNetworkServiceID = OcaBlob
OcaNetworkHostID = OcaUint16


class OcaNetworkLinkType(Enum):
    NONE = 0
    ETHERNET_WIRED = 1
    ETHERNET_WIRELESS = 2
    USB = 3
    SERIAL_P2P = 4


class OcaApplicationNetworkState(Enum):
    UNKNOWN = 0
    NOT_READY = 1
    READYING = 2
    READY = 3
    RUNNING = 4
    PAUSED = 5
    STOPPING = 6
    STOPPED = 7
    FAULT = 8


class OcaApplicationNetworkCommand(Enum):
    NONE = 0
    PREPARE = 1
    START = 2
    PAUSE = 3
    STOP = 4
    RESET = 5


class OcaNetworkMediaProtocol(Enum):
    NONE = 0
    AV3 = 1
    AVBTP = 2
    DANTE = 3
    COBRANET = 4
    AES67 = 5
    SMPTEAUDIO = 6
    LIVEWIRE = 7
    EXTENSION_POINT = 65


class OcaNetworkControlProtocol(Enum):
    NONE = 0
    OCP01 = 1
    OCP02 = 2
    OCP03 = 3


class OcaNetworkAddress(OcaAbstractBase):
    ip: str
    port: int 

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            f"!{len(self.ip)}sH",
            self.ip,
            self.port
        )
    

class OcaNetworkSystemInterfaceDescriptor(OcaAbstractBase):
    system_interface_parameters: OcaBlob
    my_network_address: OcaNetworkAddress

    @property
    def format(self) -> str:
        return f"{self.system_interface_parameters.format}{self.my_network_address.format}"
