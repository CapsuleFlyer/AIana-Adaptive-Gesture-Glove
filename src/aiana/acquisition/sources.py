"""Sample sources. All three expose the same interface:

    source.read_samples()  ->  generator of Sample (see parser.py)

so the rest of the pipeline does not care whether the data comes from the real glove,
a recorded file, or the fake glove.
"""
import csv
import time
from typing import Dict, Iterator, List, Optional, Tuple

import numpy as np

from .parser import N_CHANNELS, Sample, StreamStats, parse_line


# --------------------------------------------------------------------------- real glove
def find_port() -> Optional[str]:
    from serial.tools import list_ports

    for p in list_ports.comports():
        text = f"{p.description} {p.manufacturer}"
        if "CP210" in text or "Silicon Labs" in text:
            return p.device
    return None


class SerialSource:
    """Reads the ESP32 over USB serial (or a Bluetooth COM port)."""

    def __init__(self, port: Optional[str] = None, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.stats = StreamStats()

    def read_samples(self) -> Iterator[Sample]:
        import serial  # imported here so tests and replay work without pyserial

        port = self.port or find_port()
        if port is None:
            raise RuntimeError("No CP210x port found. Plug in the glove (data cable) or pass port='COM5'.")
        ser = serial.Serial(port, self.baud, timeout=1)
        time.sleep(0.5)
        ser.reset_input_buffer()
        try:
            while True:
                line = ser.readline().decode("ascii", errors="ignore")
                if not line.strip() or line.startswith("#"):
                    continue
                s = parse_line(line)
                if s is None:
                    self.stats.bad_line()
                    continue
                self.stats.good(s.seq)
                yield s
        finally:
            ser.close()


# --------------------------------------------------------------------------- recorded file
class ReplaySource:
    """Replays a recording CSV (columns: timestamp_ms,flex1..flex5,ax,ay,az,gx,gy,gz)."""

    def __init__(self, path: str, rate_hz: float = 50.0, realtime: bool = False):
        self.path = path
        self.rate_hz = rate_hz
        self.realtime = realtime

    def read_samples(self) -> Iterator[Sample]:
        with open(self.path, newline="") as f:
            rows = csv.reader(f)
            next(rows)  # header
            for i, row in enumerate(rows):
                vals = np.asarray([float(x) for x in row[1:]], dtype=np.float32)
                if vals.shape[0] != N_CHANNELS:
                    continue
                yield Sample(i, int(float(row[0])), vals)
                if self.realtime:
                    time.sleep(1.0 / self.rate_hz)


# --------------------------------------------------------------------------- fake glove
# Fake gestures: (finger "closed" amount 0..1 for thumb..pinky, IMU motion type)
# These are made-up shapes for developing the pipeline before real data exists.
FAKE_GESTURES: Dict[str, Tuple[List[float], str]] = {
    "idle":      ([0.0, 0.0, 0.0, 0.0, 0.0], "still"),
    "fist":      ([1.0, 1.0, 1.0, 1.0, 1.0], "still"),
    "point":     ([1.0, 0.0, 1.0, 1.0, 1.0], "still"),
    "thumbs_up": ([0.0, 1.0, 1.0, 1.0, 1.0], "still"),
    "wave":      ([0.0, 0.0, 0.0, 0.0, 0.0], "wave"),
    "swipe":     ([0.2, 0.0, 0.0, 0.2, 0.4], "swipe"),
}

# Placeholder raw ADC values for an open / fully bent finger. REAL values must be measured
# on the actual glove (they differ per finger and per divider), see the calibration step.
FAKE_ADC_OPEN = 1500.0
FAKE_ADC_BENT = 2700.0

DEFAULT_SCHEDULE = [("idle", 2.0), ("fist", 2.0), ("idle", 1.5), ("point", 2.0), ("idle", 1.5),
                    ("wave", 2.0), ("idle", 1.5), ("thumbs_up", 2.0), ("idle", 1.5), ("swipe", 1.0)]


class FakeSource:
    """Simulated glove. Produces realistic-looking raw samples at `rate_hz` and exposes the
    ground-truth label in `current_label` (handy for tests and for developing the app)."""

    def __init__(self, schedule=None, rate_hz: float = 50.0, seed: int = 0,
                 realtime: bool = False, loop: bool = True):
        self.schedule = schedule or DEFAULT_SCHEDULE
        self.rate_hz = rate_hz
        self.realtime = realtime
        self.loop = loop
        self.rng = np.random.default_rng(seed)
        self.current_label = "idle"

    def read_samples(self) -> Iterator[Sample]:
        dt = 1.0 / self.rate_hz
        alpha = 1.0 - np.exp(-dt / 0.12)  # fingers move smoothly toward the target (~0.12 s)
        closed = np.zeros(5)
        seq = 0
        while True:
            for name, dur in self.schedule:
                self.current_label = name
                target, motion = FAKE_GESTURES[name]
                n = int(dur * self.rate_hz)
                for k in range(n):
                    tt = k * dt
                    closed += alpha * (np.asarray(target) - closed)
                    flex = FAKE_ADC_OPEN + closed * (FAKE_ADC_BENT - FAKE_ADC_OPEN)
                    flex = flex + self.rng.normal(0, 8, 5)

                    acc = np.array([0.0, 0.0, 8192.0])   # gravity on z at +-4 g
                    gyr = np.zeros(3)
                    if motion == "wave":
                        gyr[2] = 12000 * np.sin(2 * np.pi * 2.0 * tt)
                        acc[1] = 1500 * np.sin(2 * np.pi * 2.0 * tt)
                    elif motion == "swipe":
                        acc[0] = 6000 * np.sin(np.pi * tt / dur)
                        gyr[1] = 5000 * np.sin(np.pi * tt / dur)
                    acc = acc + self.rng.normal(0, 40, 3)
                    gyr = gyr + self.rng.normal(0, 30, 3)

                    vals = np.concatenate([np.clip(flex, 0, 4095), acc, gyr]).astype(np.float32)
                    yield Sample(seq, int(seq * 1000 / self.rate_hz), vals)
                    seq += 1
                    if self.realtime:
                        time.sleep(dt)
            if not self.loop:
                return
