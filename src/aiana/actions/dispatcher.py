"""Turns a recognized gesture name into an action (speech or laptop), with confirm/cancel safety.

Rules:
- 'speak' gestures say their phrase.
- 'laptop' gestures with needs_confirm=true wait: nothing happens until the confirm gesture
  arrives within `confirm_timeout` seconds. Cancel gesture, any other gesture, or timeout drops it.
- The same gesture is ignored for `cooldown` seconds after it fired (stops double triggers).
speak_fn(text) and laptop_fn(action) are injected, so tests use fakes and the app uses real ones."""
import json
import time


class ActionDispatcher:
    def __init__(self, config, speak_fn, laptop_fn, confirm_timeout=5.0, cooldown=1.5, clock=time.monotonic):
        if isinstance(config, str):
            with open(config, encoding="utf-8") as f:
                config = json.load(f)
        self.confirm_g = config.get("confirm_gesture", "confirm")
        self.cancel_g = config.get("cancel_gesture", "cancel")
        self.map = {g["name"]: g for g in config["gestures"]}
        self.speak_fn, self.laptop_fn = speak_fn, laptop_fn
        self.confirm_timeout, self.cooldown, self.clock = confirm_timeout, cooldown, clock
        self.pending = None        # (gesture_dict, time)
        self.last = {}             # gesture -> time it last fired

    def handle(self, gesture):
        """Returns a short string describing what happened (useful for the UI and tests)."""
        now = self.clock()
        if self.pending and now - self.pending[1] > self.confirm_timeout:
            self.pending = None
        if gesture is None:
            return "idle"
        if gesture in self.last and now - self.last[gesture] < self.cooldown:
            return "ignored (cooldown)"
        if gesture == self.confirm_g:
            if not self.pending:
                return "ignored (nothing to confirm)"
            g, self.pending = self.pending[0], None
            self.last[gesture] = now
            self._run(g)
            return f"confirmed {g['name']}"
        if gesture == self.cancel_g:
            had, self.pending = self.pending, None
            self.last[gesture] = now
            return f"cancelled {had[0]['name']}" if had else "ignored (nothing to cancel)"
        if gesture not in self.map:
            return f"unknown gesture {gesture}"
        if self.pending:           # a different gesture arrived: drop the pending action first
            self.pending = None
        g = self.map[gesture]
        if g["type"] == "laptop" and g.get("needs_confirm"):
            self.pending = (g, now)
            self.last[gesture] = now
            return f"waiting for confirm: {g['name']}"
        self.last[gesture] = now
        self._run(g)
        return f"did {g['name']}"

    def _run(self, g):
        if g["type"] == "speak":
            self.speak_fn(g["phrase"])
        else:
            self.laptop_fn(g["action"])
