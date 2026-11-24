"""Cut a stream of samples into fixed-length windows."""
from collections import deque
from typing import Optional

import numpy as np

from .parser import Sample


class Windower:
    """Sliding window over the sample stream.

    length: samples per window (100 = 2 s at 50 Hz, same as our 2 s recordings)
    hop:    after the first full window, emit a new one every `hop` samples
    push() returns a (length, 11) float32 array when a window is ready, else None.
    """

    def __init__(self, length: int = 100, hop: int = 10):
        if length < 1 or hop < 1:
            raise ValueError("length and hop must be >= 1")
        self.length = length
        self.hop = hop
        self._buf = deque(maxlen=length)
        self._k = 0  # samples seen since the buffer first became full

    def push(self, sample: Sample) -> Optional[np.ndarray]:
        self._buf.append(sample.values)
        if len(self._buf) < self.length:
            return None
        emit = (self._k % self.hop == 0)
        self._k += 1
        return np.stack(self._buf).astype(np.float32) if emit else None

    def reset(self):
        self._buf.clear()
        self._k = 0


def resample_window(window: np.ndarray, n_steps: int = 64) -> np.ndarray:
    """Linearly resample a (T, C) window to (n_steps, C). Used to give every
    recording (and SignSpeak's variable 50-80 step samples) the same length."""
    window = np.asarray(window, dtype=np.float32)
    t_old = np.linspace(0.0, 1.0, num=window.shape[0])
    t_new = np.linspace(0.0, 1.0, num=n_steps)
    out = np.empty((n_steps, window.shape[1]), dtype=np.float32)
    for c in range(window.shape[1]):
        out[:, c] = np.interp(t_new, t_old, window[:, c])
    return out
