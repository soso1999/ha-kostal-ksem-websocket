"""Minimal bounded decoder for GDRs -> smart-meter -> uint64 values.

Wire structure documented by mgoeppe/ksem; see THIRD_PARTY_NOTICES.md.
Unknown standard scalar fields are skipped. No generated third-party code.
"""

from .const import CURRENT, EXPORT, IMPORT


def varint(data, pos):
    value = 0
    for shift in range(0, 70, 7):
        if pos >= len(data):
            raise ValueError("Truncated varint")
        byte = data[pos]
        pos += 1
        if shift == 63 and byte > 1:
            raise ValueError("uint64 overflow")
        value |= (byte & 127) << shift
        if not byte & 128:
            return value, pos
    raise ValueError("Invalid varint")


def fields(data):
    pos = 0
    while pos < len(data):
        tag, pos = varint(data, pos)
        number, wire = tag >> 3, tag & 7
        if not number or number > 0x1FFFFFFF:
            raise ValueError("Invalid field number")
        if wire == 0:
            value, pos = varint(data, pos)
        elif wire in (1, 2, 5):
            if wire == 2:
                length, pos = varint(data, pos)
            else:
                length = 8 if wire == 1 else 4
            end = pos + length
            if end > len(data):
                raise ValueError("Truncated field")
            value, pos = data[pos:end], end
        else:
            raise ValueError("Unsupported wire type")
        yield number, wire, value


def decode_ksem_message(data):
    values = {}
    for number, wire, entry in fields(data):
        if (number, wire) != (1, 2):
            continue
        record = {n: v for n, w, v in fields(entry) if w == 2}
        if record.get(1) != b"smart-meter" or 2 not in record:
            continue
        for n, w, item in fields(record[2]):
            if (n, w) == (4, 2):
                pair = {a: b for a, t, b in fields(item) if t == 0}
                values[pair.get(1, 0)] = pair.get(2, 0)
    return values


def measurements(values):
    result = {}
    for phase, (current, imp, exp) in enumerate(zip(CURRENT, IMPORT, EXPORT), 1):
        result[f"current_l{phase}"] = values[current] / 1000 if current in values else None
        result[f"power_l{phase}"] = (
            (values.get(imp, 0) - values.get(exp, 0)) / 1000
            if imp in values or exp in values
            else None
        )
    return result
