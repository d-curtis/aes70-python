from ocacore.occ.types.base import *
from ocacore.occ.types.worker import *
from ocacore.occ.types.framework import OcaONo


OcaMediaConnectorID = OcaUint16
OcaMediaCodingSchemeID = OcaUint16
OcaMediaStreamParameters = OcaBlob
OcaSDPString = OcaString


class OcaMediaConnectorState(Enum):
    _format = "B"
    STOPPED = 0
    SETTING_UP = 1
    RUNNING = 2
    PAUSED = 3
    FAULT = 4


class OcaMediaConnectorCommand(Enum):
    _format = "B"
    NONE = 0
    START = 1
    PAUSE = 2


class OcaMediaStreamCastMode(Enum):
    NONE = 0
    UNICAST = 1
    MULTICAST = 2


class OcaMediaCoding(OCCBase):
    coding_scheme_id: OcaMediaCodingSchemeID
    codec_parameters: OcaString
    clock_ono: OcaONo


class OcaMediaConnection(OCCBase):
    secure: OcaBoolean
    stream_parameters: OcaMediaStreamParameters
    stream_cast_mode: OcaMediaStreamCastMode
    stream_channel_count: OcaUint16

    @property
    def _format(self) -> str:
        return f"{OcaBoolean._format}{self.stream_parameters._format}{self.stream_cast_mode._format}{OcaUint16._format}"


class OcaMediaSinkConnector(OCCBase):
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
    def _format(self) -> str:
        return "".join([
            OcaMediaConnectorID._format,
            self.id_external.__format,
            self.connection._format,
            self.available_codings._format,
            OcaUint16._format,
            self.channel_pin_map._format,
            OcaDBFS._format,
            OcaDB._format,
            OcaMediaCoding._format
        ])


class OcaMediaSourceConnector(OCCBase):
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
    def _format(self) -> str:
        return "".join([
            OcaMediaConnectorID._format,
            self.id_external.__format,
            self.connection._format,
            self.available_codings._format,
            OcaUint16._format,
            self.channel_pin_map._format,
            OcaDBFS._format,
            OcaDB._format,
            OcaMediaCoding._format
        ])


class OcaMediaConnectorStatus(OCCBase):
    _format: ClassVar[str] = f"{OcaMediaConnectorID._format}{OcaMediaConnectorState._format}{OcaUint16._format}"
    connector_id: OcaMediaConnectorID
    state: OcaMediaConnectorState
    error_code: OcaUint16

