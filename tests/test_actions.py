from aiana.actions import ActionDispatcher
from aiana.models import Normalizer, StubRecognizer
import numpy as np

CFG = {"confirm_gesture": "confirm", "cancel_gesture": "cancel", "gestures": [
    {"name": "hello", "type": "speak", "phrase": "Hello"},
    {"name": "scroll_down", "type": "laptop", "action": "scroll_down", "needs_confirm": False},
    {"name": "close_window", "type": "laptop", "action": "alt+f4", "needs_confirm": True}]}


def make():
    log, t = [], [0.0]
    d = ActionDispatcher(CFG, lambda s: log.append(("say", s)), lambda a: log.append(("do", a)), clock=lambda: t[0])
    return d, log, t


def test_speak_and_safe_laptop():
    d, log, t = make()
    d.handle("hello"); t[0] += 2; d.handle("scroll_down")
    assert log == [("say", "Hello"), ("do", "scroll_down")]


def test_risky_needs_confirm():
    d, log, t = make()
    d.handle("close_window")
    assert log == []
    t[0] += 1; d.handle("confirm")
    assert log == [("do", "alt+f4")]


def test_confirm_without_pending_does_nothing():
    d, log, t = make()
    d.handle("confirm"); assert log == []


def test_cancel_and_timeout_and_other_gesture():
    d, log, t = make()
    d.handle("close_window"); t[0] += 1; d.handle("cancel"); t[0] += 2; d.handle("confirm")
    d.handle("close_window"); t[0] += 6; d.handle("confirm")           # timed out
    t[0] += 2; d.handle("close_window"); t[0] += 1; d.handle("hello"); t[0] += 1; d.handle("confirm")  # other gesture dropped it
    assert log == [("say", "Hello")]


def test_cooldown_blocks_double_trigger():
    d, log, t = make()
    d.handle("hello"); t[0] += 0.5; d.handle("hello"); t[0] += 2; d.handle("hello")
    assert len(log) == 2


def test_normalizer_and_stub():
    rng = np.random.default_rng(0)
    open_h = rng.normal(1000, 5, (50, 11)); fist = rng.normal(3000, 5, (50, 11))
    n = Normalizer().fit(open_h, fist)
    out = n.transform(fist)
    assert out.shape == (50, 11) and out[:, :5].mean() > 0.95 and out.min() >= 0 and out.max() <= 1
    g, c = StubRecognizer().predict(out)
    assert 0 <= c <= 1
