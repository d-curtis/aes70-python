import pytest
import pydantic
from ocacore.occ.base import *
from typing import Any

invalid_int_args = [{"k": "v"}, [1, 2, 3], None, "Hello"]

@pytest.mark.parametrize(
    "cls, value, ok_validation_args, ng_validation_args",
    [
        (OcaBoolean, False, [0, 1], [-1, None, ""]),
        (OcaBoolean, 1, [], []),
        (OcaInt8, 3, [-1, 0, 127], invalid_int_args + [0xFF_FF]),
        (OcaInt16, 300, [-1, 0, 0xFF, 0x7F], invalid_int_args + [0xFF_FF_FF]),
        (OcaInt32, 123456789, [-1, 0, 0xFF_FF, 0x7FF_FF], invalid_int_args + [0xFF_FF_FF_FF]),
        (OcaUint8, 0xFF, [0, 1], invalid_int_args + [-1, 0xFF_FF]),
        (OcaUint16, 0xFF_FF, [0, 1], invalid_int_args + [-1, 0xFF_FF_FF]),
        (OcaUint32, 0xFF_FF_FF_FF, [0, 1], invalid_int_args + [-1, 0xFF_FF_FF_FF_FF]),
        (OcaUint64, 0xFF_FF_FF_FF_FF_FF_FF_FF, [0, 1], invalid_int_args + [-1, 0xFF_FF_FF_FF_FF_FF_FF_FF_FF]),
        (OcaString, "Hello", [], []),
    ]
)
def test_OcaPrimitives(
    cls: OcaValueBase,
    value: Any, 
    ok_validation_args: list[Any], 
    ng_validation_args: list[Any],
) -> None:
    assert all([
        cls(value) == value,
        cls(oca_value=value) == value,
    ])

    _ = [cls(arg) for arg in ok_validation_args]

    for arg in ng_validation_args:
        with pytest.raises(pydantic.error_wrappers.ValidationError):
            cls(arg)


@pytest.mark.parametrize(
    "cls, ok_bytes, ng_bytes",
    [
        (OcaBoolean, {b"\x00": OcaBoolean(False), b"\x01": OcaBoolean(True)}, [b"\xFF\x00"]),
        (OcaInt8, {b"\x7F": OcaInt8(0x7F), b"\xFF": OcaInt8(-1)}, [b"\xFF\x00"]),
        (OcaInt16, {b"\x7F\xFF": OcaInt16(0x7F_FF), b"\xFF\xFF": OcaInt16(-1)}, [b"\xFF\xFF\xFF"]),
        (OcaInt32, {b"\x7F\xFF\xFF\xFF": OcaInt32(0x7F_FF_FF_FF), b"\xFF\xFF\xFF\xFF": OcaInt32(-1)}, [b"\xFF\xFF\xFF\xFF\xFF"]),
        (OcaInt64, {b"\x7F\xFF\xFF\xFF\xFF\xFF\xFF\xFF": OcaInt64(0x7F_FF_FF_FF_FF_FF_FF_FF), b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF": OcaInt64(-1)}, [b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF"]),
        (OcaUint8, {b"\xFF": OcaUint8(0xFF), b"\x00": OcaUint8(0)}, [b"\xFF\x00"]),
        (OcaUint16, {b"\xFF\xFF": OcaUint16(0xFF_FF), b"\x00\x00": OcaUint16(0)}, [b"\xFF\x00\xFF", b"\xFF"]),
        (OcaUint32, {b"\xFF\xFF\xFF\xFF": OcaUint32(0xFF_FF_FF_FF), b"\x00\x00\x00\x00": OcaUint32(0)}, [b"\xFF\x00\x00\x00\xFF", b"\xFF\x00"]),
        (OcaUint64, {b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF": OcaUint64(0xFF_FF_FF_FF_FF_FF_FF_FF), b"\x00\x00\x00\x00\x00\x00\x00\x00": OcaUint64(0)}, [b"\xFF\x00\x00\x00\x00\x00\x00\x00\xFF", b"\xFF\x00"]),
        # (OcaString, {})

    ]
)
def test_SerialisableBase_unpack(
    cls: SerialisableBase,
    ok_bytes: dict[bytes, Any],
    ng_bytes: list[bytes],
) -> None:
    for data, result in ok_bytes.items():
        assert cls.from_bytes(data) == result
    
    for data in ng_bytes:
        with pytest.raises((struct.error, pydantic.error_wrappers.ValidationError)):
            struct.unpack(cls._format, data)


@pytest.mark.parametrize(
    "obj, obj_bytes",
    [
        (OcaBoolean(False), b"\x00"), 
        (OcaBoolean(True), b"\x01"),
        (OcaInt8(3), b"\x03"), 
        (OcaInt8(-1), b"\xFF"),
        (OcaInt16(255), b"\x00\xFF"),
        (OcaInt16(-1), b"\xFF\xFF"),
        (OcaInt32(0x7F_FF_FF_FF), b"\x7F\xFF\xFF\xFF"),
        (OcaInt32(-1), b"\xFF\xFF\xFF\xFF"),
        (OcaInt64(0x7F_FF_FF_FF_FF_FF_FF_FF), b"\x7F\xFF\xFF\xFF\xFF\xFF\xFF\xFF"),
        (OcaInt64(-1), b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF"),
        (OcaUint8(0xAF), b"\xAF"),
        (OcaUint16(0xAF_FF), b"\xAF\xFF"),
        (OcaUint32(0xAF_FF_FF_FF), b"\xAF\xFF\xFF\xFF"),
        (OcaUint64(0xAF_FF_FF_FF_FF_FF_FF_FF), b"\xAF\xFF\xFF\xFF\xFF\xFF\xFF\xFF")

    ]
)
def test_SerialisableBase_pack(
    obj: SerialisableBase,
    obj_bytes: bytes
) -> None:
    assert obj.bytes == obj_bytes
