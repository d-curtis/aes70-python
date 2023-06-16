
from typing import ClassVar
from enum import Enum
from ocacore.occ.types.base import *
from ocacore.occ.types.network import OcaNetworkHostID


OcaClassVersionNumber = OcaUint16
OcaONo = OcaUint32
OcaNamePath = list[OcaString]
OcaONoPath = list[OcaONo]
OcaOrganizationID = OcaBlob



class OcaClassAuthorityID(OCCBase):
    _format: ClassVar[str] = f"{OcaUint16._format}{OcaUint8._format}{OcaOrganizationID._format}"
    sentinel: OcaUint16
    reserved: OcaUint8
    organization_id: OcaOrganizationID


class OcaClassIDField(OCCBase):
    pass


class OcaClassID(OCCBase):
    local_id: list[int]
    
    @property
    def field_count(self) -> OcaUint16:
        return OcaUint16(len(self.fields))

    @property
    def _format(self) -> str:
        return "".join([
            OcaUint16._format,
            *[field._format for field in self.fields]
        ])


class OcaVersion(OCCBase):
    major: OcaUint32
    minor: OcaUint32
    build: OcaUint32
    component: "OcaComponent"

    @property
    def _format(self) -> str:
        return f"3{OcaUint32._format}{self.component._format}"


class OcaClassIdentification(OCCBase):
    class_id: OcaClassID
    class_version: OcaClassVersionNumber

    @property
    def _format(self) -> str:
        return f"{self.class_id._format}{OcaClassVersionNumber._format}"


class OcaOPath(OCCBase):
    _format: ClassVar[str] = f"{OcaNetworkHostID._format}{OcaONo._format}"
    host_id: OcaNetworkHostID
    ono: OcaONo


class OcaObjectIdentification(OCCBase):
    _format: ClassVar[str] = f"{OcaONo._format}{OcaClassIdentification._format}"
    ono: OcaONo
    class_identification: OcaClassIdentification


class OcaMethodID(OCCBase):
    _format: ClassVar[str] = f"!2{OcaUint16._format}"
    def_level: Union[int, OcaUint16]
    method_index: Union[int, OcaUint16]
    
    @validator("def_level", "method_index")
    def validate_uint16(cls, value):
        if isinstance(value, int):
            return OcaUint16(value)

    @property
    def bytes(self) -> struct.Struct:
        return struct.pack(
            self._format,
            self.def_level,
            self.method_index
        )

    def __hash__(self):
        return hash((self.def_level, self.method_index))
    
    def __eq__(self, other):
        return hash(self) == hash(other)


class OcaPropertyID(OCCBase):
    _format: ClassVar[str] = f"2{OcaUint16._format}"
    def_level: Union[int, OcaUint16]
    property_index: Union[int, OcaUint16]

    @validator("def_level", "property_index")
    def validate_uint16(cls, value):
        if isinstance(value, int):
            return OcaUint16(value)
    
    def __hash__(self):
        return hash((self.def_level, self.property_index))
    
    def __eq__(self, other):
        return hash(self) == hash(other)


class OcaEventID(OCCBase):
    _format: ClassVar[str] = f"2{OcaUint16._format}"
    def_level: OcaUint16
    event_index: OcaUint16


class OcaPropertyDescriptor(OCCBase):
    _format: ClassVar[str] = f"{OcaPropertyID._format}B{OcaMethodID._format}{OcaMethodID._format}"
    property_id: OcaPropertyID
    base_data_type: OcaUint8 # Key for base.oca_base_data_type
    getter_method_id: OcaMethodID
    setter_method_id: OcaMethodID


class OcaProperty(OCCBase):
    _format: ClassVar[str] = f"{OcaONo._format}{OcaPropertyDescriptor._format}"
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


class OcaGlobalTypeIdentifier(OCCBase):
    _format: ClassVar[str] = f"{OcaOrganizationID._format}{OcaUint32._format}"
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

