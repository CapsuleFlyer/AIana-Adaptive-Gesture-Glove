"""Text -> speech -> virtual microphone.
pyttsx3 cannot choose an output device, so: synthesize to a WAV file, then play that WAV with
sounddevice on the VB-CABLE device 'CABLE Input'. In Meet/Zoom pick 'CABLE Output' as the microphone.
WAVs are cached per phrase, so a repeated phrase skips the (slow) synthesis step."""
import hashlib
import time
import wave
from pathlib import Path

import numpy as np

CACHE = Path("saved_models/tts_cache")


def find_device(name_part="CABLE Input"):
    import sounddevice as sd
    for i, d in enumerate(sd.query_devices()):
        if name_part.lower() in d["name"].lower() and d["max_output_channels"] > 0:
            return i
    return None


def synth(text, rate=170):
    """Returns the WAV path (cached). Raises if pyttsx3 fails."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.md5(f"{text}|{rate}".encode()).hexdigest() + ".wav")
    if not path.exists():
        import pyttsx3
        eng = pyttsx3.init()
        eng.setProperty("rate", rate)
        eng.save_to_file(text, str(path))
        eng.runAndWait()
        eng.stop()
    return path


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        sr, ch, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if width != 2:
        raise ValueError(f"expected 16-bit WAV, got {8 * width}-bit")
    data = np.frombuffer(raw, dtype=np.int16).reshape(-1, ch)
    return data, sr


def speak(text, device_name="CABLE Input", blocking=True):
    """Say `text` into the virtual mic. Returns (synth_seconds, total_seconds) for latency logging."""
    import sounddevice as sd
    t0 = time.perf_counter()
    wav = synth(text)
    t1 = time.perf_counter()
    data, sr = read_wav(wav)
    dev = find_device(device_name)
    if dev is None:
        raise RuntimeError(f"Output device '{device_name}' not found. Install VB-CABLE and reboot. "
                           "Run: python scripts/speech_test.py --list")
    sd.play(data, sr, device=dev)
    if blocking:
        sd.wait()
    return t1 - t0, time.perf_counter() - t0
