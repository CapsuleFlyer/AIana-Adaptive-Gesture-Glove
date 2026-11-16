"""Glove sample sources: real serial, replay from a CSV, or fake. All give the same thing:
an iterator of Sample tuples, so the rest of the app never cares where data comes from.

    for s in read_samples("fake"): ...
    for s in read_samples("serial", port="COM5"): ...
    for s in read_samples("replay", path="data/raw/user01/hello_001.csv"): ...
"""
import time
from collections import namedtuple

import numpy as np

# values = 11 numbers: flex1..flex5, ax, ay, az, gx, gy, gz (raw units)
Sample = namedtuple("Sample", "seq t_ms values")
N_CHANNELS = 11
ACC_LSB_PER_G = 8192.0   # +-4 g
GYR_LSB_PER_DPS = 65.5   # +-500 dps


def parse_line(line):
    """Return a Sample, or None if the line is a '#' info line or malformed."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split(",")
    if parts[0] != "S" or len(parts) != 14:
        return None
    try:
        nums = [int(x) for x in parts[1:]]
    except ValueError:
        return None
    return Sample(nums[0], nums[1], nums[2:])


def serial_source(port=None, baud=115200):
    import serial
    from serial.tools import list_ports
    if port is None:
        for p in list_ports.comports():
            if "CP210" in f"{p.description} {p.manufacturer}":
                port = p.device
        if port is None:
            raise RuntimeError("No CP210x port found; pass port='COM5'")
    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(1.5)            # opening the port resets the ESP32; wait for it to boot
    ser.reset_input_buffer()
    try:
        while True:
            s = parse_line(ser.readline().decode("ascii", errors="ignore"))
            if s is not None:
                yield s
    finally:
        ser.close()


def replay_source(path, realtime=False, rate_hz=50):
    """Replay a recording CSV (columns timestamp_ms,flex1..flex5,ax..gz)."""
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    for i, row in enumerate(np.atleast_2d(data)):
        if realtime:
            time.sleep(1.0 / rate_hz)
        yield Sample(i, int(row[0]), [int(v) for v in row[1:12]])


def fake_source(n=None, rate_hz=50, realtime=False, seed=0):
    """Fake glove: flex channels wiggle like slow finger bends, IMU is gravity plus noise."""
    rng = np.random.default_rng(seed)
    i = 0
    while n is None or i < n:
        t = i / rate_hz
        flex = [int(2000 + 1200 * np.sin(2 * np.pi * 0.5 * t + k) + rng.normal(0, 10)) for k in range(5)]
        imu = [int(rng.normal(0, 50)), int(rng.normal(0, 50)), int(8192 + rng.normal(0, 50)),
               int(rng.normal(0, 20)), int(rng.normal(0, 20)), int(rng.normal(0, 20))]
        if realtime:
            time.sleep(1.0 / rate_hz)
        yield Sample(i, int(t * 1000), flex + imu)
        i += 1


def read_samples(kind="fake", **kw):
    return {"serial": serial_source, "replay": replay_source, "fake": fake_source}[kind](**kw)


class Windower:
    """Sliding window: push samples, get a (steps, 11) array every `stride` samples once full.
    2.0 s at 50 Hz = 100 samples, stride 0.25 s = 12 samples (from configs/settings.yaml)."""

    def __init__(self, size=100, stride=12):
        self.size, self.stride = size, stride
        self.buf, self.since = [], 0

    def push(self, sample):
        self.buf.append(sample.values)
        if len(self.buf) > self.size:
            self.buf.pop(0)
        self.since += 1
        if len(self.buf) == self.size and self.since >= self.stride:
            self.since = 0
            return np.array(self.buf, dtype=np.float32)
        return None


def resample(window, steps=64):
    """Linear-resample a (T, C) window to (steps, C) so every window has the same length."""
    window = np.asarray(window, dtype=np.float32)
    old = np.linspace(0, 1, len(window))
    new = np.linspace(0, 1, steps)
    return np.stack([np.interp(new, old, window[:, c]) for c in range(window.shape[1])], axis=1)


def count_drops(samples):
    """Number of missing sequence numbers in a list of Samples."""
    seqs = [s.seq for s in samples]
    return sum(b - a - 1 for a, b in zip(seqs, seqs[1:]) if b > a + 1)
