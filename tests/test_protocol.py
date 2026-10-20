"""Synthetic protobuf fixtures, independent of device data."""

import pytest

from custom_components.ksem_ws.const import CURRENT, EXPORT, IMPORT
from custom_components.ksem_ws.protocol import decode_ksem_message, measurements


def uint(value):
    result = bytearray()
    while value > 127:
        result.append((value & 127) | 128)
        value >>= 7
    result.append(value)
    return bytes(result)


def field(n, value):
    return uint(n << 3 | 2) + uint(len(value)) + value


def frame(values, name=b"smart-meter"):
    gdr = b"".join(field(4, b"\x08" + uint(k) + b"\x10" + uint(v)) for k, v in values.items())
    return field(1, field(1, name) + field(2, gdr))


def test_all_phases_and_signed_power():
    values = dict(zip(CURRENT, (1230, 2340, 3450)))
    values.update(zip(IMPORT, (6000, 0, 2000)))
    values.update(zip(EXPORT, (0, 150000, 500)))
    assert measurements(decode_ksem_message(frame(values))) == {
        "current_l1": 1.23,
        "current_l2": 2.34,
        "current_l3": 3.45,
        "power_l1": 6,
        "power_l2": -150,
        "power_l3": 1.5,
    }


def test_omitted_zero_and_missing_measurements():
    zero_entry = field(4, b"\x08" + uint(CURRENT[0]))
    assert (
        decode_ksem_message(field(1, field(1, b"smart-meter") + field(2, zero_entry)))[CURRENT[0]]
        == 0
    )
    data = measurements({EXPORT[0]: 1000})
    assert data["power_l1"] == -1
    assert data["power_l2"] is None
    assert data["current_l1"] is None


def test_filter_other_gdr_and_unknown_fields():
    assert decode_ksem_message(frame({CURRENT[0]: 99}, b"other")) == {}
    assert decode_ksem_message(frame({CURRENT[0]: 99}) + b"\x51" + b"0" * 8) == {CURRENT[0]: 99}


@pytest.mark.parametrize(
    "data", [b"\x00", b"\x0a\x05x", b"\x80", b"\x0b", b"\x08" + b"\xff" * 10, b"\x0d1"]
)
def test_reject_malformed(data):
    with pytest.raises(ValueError):
        decode_ksem_message(data)
