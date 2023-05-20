from ocacore.occ.base import *
from ocacore.occ.framework import *
from typing import ClassVar
from enum import Enum


class OcaManagerDescriptor(OcaAbstractBase):
    object_number: OcaONo
    name: OcaString
    class_id: OcaClassID
    class_version: OcaClassVersionNumber

    @property
    def _format(self) -> str:
        return f"{OcaONo._format}{self.name.__format}{OcaClassID._format, OcaClassVersionNumber._format}"


class OcaManagerDefaultObjectNumbers(OcaAbstractBase):
    _format: ClassVar[str] = f"13{OcaONo._format}"
    device_manager: OcaONo
    security_manager: OcaONo
    firmware_manager: OcaONo
    subscription_manager: OcaONo
    power_manager: OcaONo
    network_manager: OcaONo
    media_clock_manager: OcaONo
    library_manager: OcaONo
    audio_processing_manager: OcaONo
    device_time_manager: OcaONo
    task_manager: OcaONo
    coding_manager: OcaONo
    diagnostic_manager: OcaONo


class OcaModelGUID:
    def __init__(self):
        raise NotImplementedError


class OcaModelDescription(OcaAbstractBase):
    manufacturer: OcaString
    name: OcaString
    version: OcaString

    @property
    def _format(self) -> str:
        return f"{self.manufacturer.__format}{self.name.__format}{self.version.__format}"


class OcaComponent(Enum):
    Bootloader = 0


class OcaPowerState(Enum):
    NONE = 0
    WORKING = 1
    STANDBY = 2
    OFF = 3


