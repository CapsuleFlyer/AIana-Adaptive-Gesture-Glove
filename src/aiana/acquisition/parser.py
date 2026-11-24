"""Parse one line of the ESP32 serial stream (frozen v1 format).

Sample line:  S,<seq>,<t_ms>,<f1>,<f2>,<f3>,<f4>,<f5>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>
Lines starting with '#' are info/errors and are ignored here.
Values stay RAW (flex = ADC counts 0..4095, IMU = raw int16). Calibration is done later, on the laptop.
"""
from typing import NamedTuple, Optional

import numpy as np

N_FLEX = 5
N_IMU = 6
N_CHANNELS = N_FLEX + N_IMU  # 11: flex1..flex5, ax, ay, az, gx, gy, gz

CHANNEL_NAMES = ["flex1", "flex2", "flex3", "flex4", "flex5", "ax", "ay", "az", "gx", "gy", "gz"]


class Sample(NamedTuple):
    seq: int
    t_ms: int
    values: np.ndarray  # shape (11,), float32, raw units


def parse_line(line: str) -> Optional[Sample]:
    """Return a Sample, or None if the line is info, malformed or out of range."""
    line = line.strip()
    if not line or line[0] == "#":
        return None
    parts = line.split(",")
    if len(parts) != 14 or parts[0] != "S":
        return None
    try:
        nums = [int(x) for x in parts[1:]]
    except ValueError:
        return None
    seq, t_ms, vals = nums[0], nums[1], nums[2:]
    if seq < 0 or t_ms < 0:
        return None
    if any(not 0 <= v <= 4095 for v in vals[:N_FLEX]):
        return None  # corrupted flex reading
    if any(not -32768 <= v <= 32767 for v in vals[N_FLEX:]):
        return None  # not a valid int16
    return Sample(seq, t_ms, np.asarray(vals, dtype=np.float32))


class StreamStats:
    """Counts good samples, dropped samples (gaps in seq) and bad lines."""

    def __init__(self):
        self.total = 0
        self.drops = 0
        self.bad = 0
        self._expected = None

    def good(self, seq: int):
        if self._expected is not None and seq > self._expected:
            self.drops += seq - self._expected
        # seq going backwards means the board rebooted or restarted: just resync
        self._expected = seq + 1
        self.total += 1

    def bad_line(self):
        self.bad += 1
