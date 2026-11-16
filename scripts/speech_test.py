"""Test speech into the virtual mic and measure latency.
  python scripts/speech_test.py --list                    show audio output devices (look for 'CABLE Input')
  python scripts/speech_test.py                           say 3 phrases twice into CABLE Input, print timings
  python scripts/speech_test.py --device "Speakers"       test on your normal speakers first
Then open Meet/Zoom, choose microphone = 'CABLE Output', and run it again while in a call (second run = cached phrases)."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from aiana.actions.speech import speak  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--list", action="store_true")
ap.add_argument("--device", default="CABLE Input")
a = ap.parse_args()
if a.list:
    import sounddevice as sd
    for i, d in enumerate(sd.query_devices()):
        if d["max_output_channels"] > 0:
            print(i, d["name"])
    sys.exit()
for rnd in (1, 2):
    for phrase in ["Hello, can you hear me?", "Yes.", "Could you please repeat that?"]:
        synth_s, total_s = speak(phrase, a.device)
        print(f"round {rnd} | {phrase!r:35} synth {synth_s * 1000:6.0f} ms | synth+play {total_s * 1000:6.0f} ms")
print("Round 1 includes synthesis; round 2 is cached (synth ~0 ms). Play time is the phrase length itself.")
