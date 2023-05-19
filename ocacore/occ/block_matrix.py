from ocacore.occ.base import *
from ocacore.occ.framework import *
from typing import ClassVar
from enum import Enum


OcaProtoONo = OcaUint32
OcaProtoMember = OcaProtoONo
OcaMatrixCoordinate = OcaUint16


class OcaBlockMember(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaObjectIdentification.format}{OcaONo.format}"
    member_object_identification: OcaObjectIdentification
    container_object_number: OcaONo


class OcaPortMode(Enum):
    INPUT = 1
    OUTPUT = 2


class OcaPortID(OcaAbstractBase):
    mode: OcaPortMode
    index: OcaUint16


class OcaPort(OcaAbstractBase):
    owner: OcaONo
    id: OcaPortID
    name: OcaString

    @property
    def format(self) -> str:
        return f"{OcaONo.format}{OcaPortID.format}{self.name._format}"


class OcaSignalPath(OcaAbstractBase):
    source_port: OcaPort
    sink_port: OcaPort

    @property
    def format(self) -> str:
        return f"{self.source_port.format}{self.sink_port.format}"


class OcaProtoObjectIdentification(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaProtoONo.format}{OcaClassIdentification.format}"
    pono: OcaProtoONo
    class_identification: OcaClassIdentification


class OcaProtoPortID(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaPortMode.format}{OcaUint16.format}"
    mode: OcaPortMode
    index: OcaUint16


class OcaProtoPort(OcaAbstractBase):
    owner: OcaProtoONo
    proto_id: OcaProtoPortID
    name: OcaString

    @property
    def format(self) -> str:
        return f"{OcaProtoONo.format}{self.proto_id.format}{self.name._format}"


class OcaProtoSignalPath(OcaAbstractBase):
    source_protoport: OcaProtoPort
    sink_protoport: OcaProtoPort

    @property
    def format(self) -> str:
        return f"{self.source_protoport.format}{self.sink_protoport.format}"


class OcaObjectSearchResult(OcaAbstractBase):
    ono: OcaONo
    class_identification: OcaClassIdentification
    container_path: OcaONoPath
    role: OcaString
    label: OcaString

    @property
    def format(self) -> str:
        return f"{OcaONo.format}{OcaClassIdentification.format}{OcaONoPath.format}{self.role._format}{self.label._format}"

