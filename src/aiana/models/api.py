"""Recognizer API (interface v1). StubRecognizer returns fake output so the app can be built before
the real model exists. Normalizer is a simple working version: flex = per-user min-max from calibration,
IMU = fixed full-scale scaling (so no calibration needed for it)."""
import pickle
from dataclasses import dataclass

import numpy as np

ACC_LSB_PER_G, GYR_LSB_PER_DPS = 8192.0, 65.5


@dataclass
class EnrollResult:
    ok: bool
    nearest: str | None = None
    similarity: float = 0.0
    warning: str | None = None


class Normalizer:
    """Raw window (T, 5 or 11) -> float32 (T, C) in 0..1.
    fit(open_hand, fist): two raw recordings (T, >=5) of the flat hand and a closed fist."""

    def __init__(self):
        self.lo = self.hi = None

    def fit(self, open_hand, fist):
        both = np.vstack([np.asarray(open_hand)[:, :5], np.asarray(fist)[:, :5]]).astype(np.float32)
        a, b = np.asarray(open_hand)[:, :5].mean(0), np.asarray(fist)[:, :5].mean(0)
        self.lo, self.hi = np.minimum(a, b), np.maximum(a, b)
        if (self.hi - self.lo < 50).any():   # sensor barely moved: flag it instead of dividing by ~0
            bad = [i + 1 for i in np.where(self.hi - self.lo < 50)[0]]
            raise ValueError(f"Flex sensor(s) {bad} barely changed between open hand and fist: check wiring")
        return self

    def transform(self, raw_window):
        w = np.asarray(raw_window, dtype=np.float32)
        out = [np.clip((w[:, :5] - self.lo) / (self.hi - self.lo), 0, 1)]
        if w.shape[1] >= 11:
            out.append(np.clip((w[:, 5:8] / ACC_LSB_PER_G + 4) / 8, 0, 1))
            out.append(np.clip((w[:, 8:11] / GYR_LSB_PER_DPS + 500) / 1000, 0, 1))
        return np.concatenate(out, axis=1).astype(np.float32)


class Recognizer:
    def predict(self, window):          # -> (gesture | None, confidence)
        raise NotImplementedError

    def enroll(self, name, windows):    # -> EnrollResult
        raise NotImplementedError

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as f:
            return pickle.load(f)


class StubRecognizer(Recognizer):
    """FAKE: picks a gesture from the mean flex value of the window. Only for building the app."""

    def __init__(self, gestures=("hello", "yes", "no", "thanks"), threshold=0.8):
        self.gestures, self.threshold = list(gestures), threshold

    def predict(self, window):
        w = np.asarray(window)
        if w.std(axis=0).max() < 0.02:                  # nothing moving -> idle
            return None, 0.95
        i = int(w[:, :5].mean() * 10) % len(self.gestures)
        conf = 0.9
        return (self.gestures[i] if conf >= self.threshold else None), conf

    def enroll(self, name, windows):
        if name not in self.gestures:
            self.gestures.append(name)
        return EnrollResult(ok=True)
