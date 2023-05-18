from ocacore.occ.base import *
from ocacore.occ.worker import *
from ocacore.occ.framework import OcaONo


OcaMediaConnectorID = OcaUint16
OcaMediaCodingSchemeID = OcaUint16
OcaMediaStreamParameters = OcaBlob
OcaSDPString = OcaString


class OcaMediaConnectorState(Enum):
    format = "B"
    STOPPED = 0
    SETTING_UP = 1
    RUNNING = 2
    PAUSED = 3
    FAULT = 4


class OcaMediaConnectorCommand(Enum):
    format = "B"
    NONE = 0
    START = 1
    PAUSE = 2


class OcaMediaStreamCastMode(Enum):
    NONE = 0
    UNICAST = 1
    MULTICAST = 2


class OcaMediaCoding(OcaAbstractBase):
    coding_scheme_id: OcaMediaCodingSchemeID
    codec_parameters: OcaString
    clock_ono: OcaONo


class OcaMediaConnection(OcaAbstractBase):
    secure: OcaBoolean
    stream_parameters: OcaMediaStreamParameters
    stream_cast_mode: OcaMediaStreamCastMode
    stream_channel_count: OcaUint16

    @property
    def format(self) -> str:
        return f"{OcaBoolean.format}{self.stream_parameters.format}{self.stream_cast_mode.format}{OcaUint16.format}"


class OcaMediaSinkConnector(OcaAbstractBase):
    id_internal: OcaMediaConnectorID
    id_external: OcaString
    connection: OcaMediaConnection
    available_codings: OcaList #[OcaMediaCoding]
    pin_count: OcaUint16
    channel_pin_map: OcaMultiMap #[OcaUint16, OcaPortID]
    alignment_level: OcaDBFS
    alignment_gain: OcaDB
    current_coding: OcaMediaCoding

    @property
    def format(self) -> str:
        return "".join([
            OcaMediaConnectorID.format,
            self.id_external.format,
            self.connection.format,
            self.available_codings.format,
            OcaUint16.format,
            self.channel_pin_map.format,
            OcaDBFS.format,
            OcaDB.format,
            OcaMediaCoding.format
        ])


class OcaMediaSourceConnector(OcaAbstractBase):
    id_internal: OcaMediaConnectorID
    id_external: OcaString
    connection: OcaMediaConnection
    available_codings: OcaList #[OcaMediaCoding]
    pin_count: OcaUint16
    channel_pin_map: OcaMultiMap #[OcaUint16, OcaPortID]
    alignment_level: OcaDBFS
    alignment_gain: OcaDB
    current_coding: OcaMediaCoding

    @property
    def format(self) -> str:
        return "".join([
            OcaMediaConnectorID.format,
            self.id_external.format,
            self.connection.format,
            self.available_codings.format,
            OcaUint16.format,
            self.channel_pin_map.format,
            OcaDBFS.format,
            OcaDB.format,
            OcaMediaCoding.format
        ])


class OcaMediaConnectorStatus(OcaAbstractBase):
    format: ClassVar[str] = f"{OcaMediaConnectorID.format}{OcaMediaConnectorState.format}{OcaUint16.format}"
    connector_id: OcaMediaConnectorID
    state: OcaMediaConnectorState
    error_code: OcaUint16

