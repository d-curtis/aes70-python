from ocacore.occ.types.base import *
from ocacore.occ.types.framework import *
from typing import ClassVar
from enum import Enum


OcaProtoONo = OcaUint32
OcaProtoMember = OcaProtoONo
OcaMatrixCoordinate = OcaUint16


class OcaBlockMember(OCCBase):
    _format: ClassVar[str] = f"{OcaObjectIdentification._format}{OcaONo._format}"
    member_object_identification: OcaObjectIdentification
    container_object_number: OcaONo


class OcaPortMode(Enum):
    INPUT = 1
    OUTPUT = 2


class OcaPortID(OCCBase):
    mode: OcaPortMode
    index: OcaUint16


class OcaPort(OCCBase):
    owner: OcaONo
    id: OcaPortID
    name: OcaString

    @property
    def _format(self) -> str:
        return f"{OcaONo._format}{OcaPortID._format}{self.name.__format}"


class OcaSignalPath(OCCBase):
    source_port: OcaPort
    sink_port: OcaPort

    @property
    def _format(self) -> str:
        return f"{self.source_port._format}{self.sink_port._format}"


class OcaProtoObjectIdentification(OCCBase):
    _format: ClassVar[str] = f"{OcaProtoONo._format}{OcaClassIdentification._format}"
    pono: OcaProtoONo
    class_identification: OcaClassIdentification


class OcaProtoPortID(OCCBase):
    _format: ClassVar[str] = f"{OcaPortMode._format}{OcaUint16._format}"
    mode: OcaPortMode
    index: OcaUint16


class OcaProtoPort(OCCBase):
    owner: OcaProtoONo
    proto_id: OcaProtoPortID
    name: OcaString

    @property
    def _format(self) -> str:
        return f"{OcaProtoONo._format}{self.proto_id._format}{self.name.__format}"


class OcaProtoSignalPath(OCCBase):
    source_protoport: OcaProtoPort
    sink_protoport: OcaProtoPort

    @property
    def _format(self) -> str:
        return f"{self.source_protoport._format}{self.sink_protoport._format}"


class OcaObjectSearchResult(OCCBase):
    ono: OcaONo
    class_identification: OcaClassIdentification
    container_path: OcaONoPath
    role: OcaString
    label: OcaString

    @property
    def _format(self) -> str:
        return f"{OcaONo._format}{OcaClassIdentification._format}{OcaONoPath._format}{self.role._format}{self.label._format}"

