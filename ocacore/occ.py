"""
"""

from typing import Union
from pydantic import BaseModel, validator
import struct


class OcaMethodID(BaseModel):
    def_level: int
    method_index: int

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            "!HH",
            self.def_level,
            self.method_index
        )


class OcaNetworkAddress(BaseModel):
    ip: str
    port: int 

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            f"!{len(self.ip)}sH",
            self.ip,
            self.port
        )

