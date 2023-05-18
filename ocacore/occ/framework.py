
from typing import ClassVar
from enum import Enum
from ocacore.occ.base import *
from ocacore.occ.network import OcaNetworkHostID


OcaClassVersionNumber = OcaUint16
OcaONo = OcaUint32
OcaNamePath = list[OcaString]
OcaONoPath = list[OcaONo]
OcaOrganizationID = OcaBlob



class OcaClassAuthorityID(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaUint16.format}{OcaUint8.format}{OcaOrganizationID.format}"
    sentinel: OcaUint16
    reserved: OcaUint8
    organization_id: OcaOrganizationID


class OcaClassIDField(OcaAbstractBase):
    pass


class OcaClassID(OcaAbstractBase):
    field_count: OcaUint16
    fields: list[OcaClassIDField]

    @property
    def format(self) -> str:
        return "".join([
            OcaUint16.format,
            *[field.format for field in self.fields]
        ])


class OcaVersion(OcaAbstractBase):
    major: OcaUint32
    minor: OcaUint32
    build: OcaUint32
    component: "OcaComponent"

    @property
    def format(self) -> str:
        return f"3{OcaUint32.format}{self.component.format}"


class OcaClassIdentification(OcaAbstractBase):
    class_id: OcaClassID
    class_version: OcaClassVersionNumber

    @property
    def format(self) -> str:
        return f"{self.class_id.format}{OcaClassVersionNumber.format}"


class OcaOPath(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaNetworkHostID.format}{OcaONo.format}"
    host_id: OcaNetworkHostID
    ono: OcaONo


class OcaObjectIdentification(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaONo.format}{OcaClassIdentification.format}"
    ono: OcaONo
    class_identification: OcaClassIdentification


class OcaMethodID(OcaAbstractBase):
    format: ClassVar[str] = f"2{OcaUint16.format}"
    def_level: OcaUint16
    method_index: OcaUint16

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            self.format,
            self.def_level,
            self.method_index
        )


class OcaPropertyID(OcaAbstractBase):
    format: ClassVar[str] = f"2{OcaUint16.format}"
    def_level: OcaUint16
    property_index: OcaUint16


class OcaEventID(OcaAbstractBase):
    format: ClassVar[str] = f"2{OcaUint16.format}"
    def_level: OcaUint16
    event_index: OcaUint16


class OcaPropertyDescriptor(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaPropertyID.format}B{OcaMethodID.format}{OcaMethodID.format}"
    property_id: OcaPropertyID
    base_data_type: OcaUint8 # Key for base.oca_base_data_type
    getter_method_id: OcaMethodID
    setter_method_id: OcaMethodID


class OcaProperty(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaONo.format}{OcaPropertyDescriptor.format}"
    ono: OcaONo
    descriptor: OcaPropertyDescriptor


class OcaStatus(Enum):
    OK: 0
    ProtocolVersionError: 1
    DeviceError: 2
    Locked: 3
    BadFormat: 4
    BadONo: 5
    ParameterError: 6
    ParameterOutOfRange: 7
    NotImplemented: 8
    InvalidRequest: 9
    ProcessingFailed: 10
    BadMethod: 11
    PartiallySucceeded: 12
    Timeout: 13
    BufferOverflow: 14


class OcaGlobalTypeIdentifier(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaOrganizationID.format}{OcaUint32.format}"
    authority: OcaOrganizationID
    id: OcaUint32


class OcaStringComparisonType(Enum):
    Exact: 0
    Substring: 1
    Contains: 2
    ExactCaseInsensitive: 3
    SubstringCaseInsensitive: 4
    ContainsCaseInsensitive: 5


class OcaPositionCoordinateSystem(Enum):
    Robotic: 1
    ItuAudioObjectBasedPolar: 2
    ItuAudioObjectBasedCartesian: 3
    ItuAudioSceneBasedPolar: 4
    ItuAudioSceneBasedCartesian: 5
    NAV: 6
    ProprietaryBase: 128

