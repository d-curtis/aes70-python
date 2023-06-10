from ocacore.occ.types.base import *
from typing import ClassVar

OcaDB = OcaFloat32
OcaDBV = OcaDB
OcaDBu = OcaDB
OcaDBFS = OcaDB
OcaDBz = OcaDB
OcaVoltage = OcaFloat32
OcaCurrent = OcaFloat32
OcaFrequency = OcaFloat32
OcaFrequencyResponse = OcaMap #[OcaFrequency, OcaDB]
OcaPeriod = OcaUint32
OcaTemperature = OcaFloat32


class OcaMuteState(Enum):
    MUTED = 1
    UNMUTED = 2


class OcaPolarityState(Enum):
    NON_INVERTED = 1
    INVERTED = 2


class OcaDelayUnit(Enum):
    TIME = 1
    DISTANCE = 2
    SAMPLES = 3
    MICROSECONDS = 4
    MILLISECONDS = 5
    CENTIMETERS = 6
    INCHES = 7
    FEET = 8


class OcaClassicalFilterShape(Enum):
    BUTTERWORTH = 1
    BESSEL = 2
    CHEBYSHEV = 3
    LINKWITZ_RILEY = 4


class OcaFilterPassband(Enum):
    HIGH_PASS = 1
    LOW_PASS = 2
    BAND_PASS = 3
    BAND_REJECT = 4
    ALL_PASS = 5


class OcaParametricEQShape(Enum):
    NONE = 0
    PEQ = 1
    LOW_SHELF = 2
    HIGH_SHELF = 3
    LOW_PASS = 4
    HIGH_PASS = 5
    BAND_PASS = 6
    ALL_PASS = 7
    NOTCH = 8
    TONE_CONTROL_LOW_FIXED = 9
    TONE_CONTROL_LOW_SLIDING = 10
    TONE_CONTROL_HIGH_FIXED = 11
    TONE_CONTROL_HIGH_SLIDING = 12


class OcaDynamicsFunction(Enum):
    NONE = 0
    COMPRESS = 1
    LIMIT = 2
    EXPAND = 3
    GATE = 4


class OcaWaveformType(Enum):
    NONE = 0
    DC = 1
    SINE = 2
    SQUARE = 3
    IMPULSE = 4
    NOISE_PINK = 5
    NOISE_WHITE = 6
    POLARITY_TEST = 7


class OcaSweepType(Enum):
    LINEAR = 1
    LOGARITHMIC = 2
    NONE = 0


class OcaUnitOfMeasure(Enum):
    NONE = 0
    HERTZ = 1
    DEGREE_CELSIUS = 2
    VOLT = 3
    AMPERE = 4
    OHM = 5


class OcaPresentationUnit(Enum):
    DBU = 0
    DBV = 1
    V = 2


class OcaLevelDetectionLaw(Enum):
    NONE = 0
    RMS = 1
    PEAK = 2


class OcaSensorReadingState(Enum):
    UNKNOWN = 0
    VALID = 1
    UNDERRANGE = 2
    OVERRANGE = 3
    ERROR = 4


class OcaLevelMeterLaw(Enum):
    VU = 1
    STANDARD_VU = 2
    PPM1 = 3
    PPM2 = 4
    LKFS = 5
    RMS = 6
    PEAK = 7
    PROPRIETARY_VALUE_BASE = 128

class OcaDBr(OcaAbstractBase):
    _format: ClassVar[str] = f"2{OcaDB._format}"
    value: OcaDB
    ref: OcaDBz


class OcaImpedance(OcaAbstractBase):
    _format: ClassVar[str] = f"2{OcaFloat32._format}"
    magnitude: OcaFloat32
    phase: OcaFloat32


class OcaDelayValue(OcaAbstractBase):
    _format: ClassVar[str] = f"{OcaFloat32._format}B"
    delay_value: OcaFloat32
    delay_unit: OcaDelayUnit


class OcaTransferFunction(OcaAbstractBase):
    frequency: OcaList #[OcaFrequency]
    amplitude: OcaList #[OcaFloat32]
    phase: OcaList #[OcaFloat32]

    @property
    def _format(self) -> str:
        return f"{self.frequency._format}{self.amplitude._format}{self.phase._format}"


class OcaPilotToneDetectorSpec(OcaAbstractBase):
    _format: ClassVar[str] = f"{OcaDBr._format}{OcaFrequency._format}{OcaPeriod._format}"
    threshold: OcaDBr
    frequency: OcaFrequency
    poll_interval: OcaPeriod




