"""Guided recorder: prompts a gesture, counts down 3-2-1-GO, records 2.0 s, saves a CSV.

Examples:
  python scripts/record.py --user user01 --gestures hello,yes,no,idle --reps 5 --port COM5
  python scripts/record.py --user user99 --gestures hello,yes --reps 2 --source fake   (no glove needed)
Output: data/raw/<user>/<gesture>_<rep:03d>.csv + session.json, then data/raw/manifest.csv.
Timing comes from the samples themselves (50 samples = 1 s), so the countdown stays in sync with the glove.
Press Ctrl+C to stop; recordings already saved are kept.
"""
import argparse
import json
import random
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from aiana.acquisition import count_drops, read_samples  # noqa: E402
from build_manifest import build_manifest  # noqa: E402

HEADER = "timestamp_ms,flex1,flex2,flex3,flex4,flex5,ax,ay,az,gx,gy,gz"
RATE = 50
N_ROWS = 100  # 2.0 s


def next_rep(folder, gesture):
    reps = [int(m.group(1)) for f in folder.glob(f"{gesture}_*.csv") if (m := re.match(rf"{gesture}_(\d+)\.csv", f.name))]
    return max(reps, default=0) + 1


def take(it, n):
    out = []
    for s in it:
        out.append(s)
        if len(out) == n:
            return out
    raise RuntimeError("Sample stream ended early")


def save_csv(path, samples):
    t0 = samples[0].t_ms
    with open(path, "w", newline="") as f:
        f.write(HEADER + "\n")
        for s in samples:
            f.write(",".join(str(v) for v in [s.t_ms - t0] + list(s.values)) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True, help="e.g. user01 (never a real name)")
    ap.add_argument("--gestures", required=True, help="comma list of slugs, e.g. hello,yes,idle")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--session", default="s1")
    ap.add_argument("--hand", default="right")
    ap.add_argument("--condition", default="normal", help="normal | restricted:<what>")
    ap.add_argument("--refit", action="store_true", help="glove was taken off and re-worn")
    ap.add_argument("--notes", default="")
    ap.add_argument("--source", default="serial", choices=["serial", "fake"])
    ap.add_argument("--port", default=None)
    ap.add_argument("--out", default="data/raw")
    a = ap.parse_args()

    gestures = [g.strip().lower() for g in a.gestures.split(",")]
    for g in gestures:
        if not re.fullmatch(r"[a-z0-9-]+", g):
            sys.exit(f"Bad gesture slug '{g}': use lowercase letters, digits, '-'")
    folder = Path(a.out) / a.user
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "session.json").write_text(json.dumps({
        "user_id": a.user, "session_id": a.session, "date": str(date.today()), "hand": a.hand,
        "condition": a.condition, "refit": a.refit, "fw_version": 1, "rate_hz": RATE, "notes": a.notes}, indent=2))

    it = read_samples(a.source, **({"port": a.port} if a.source == "serial" else {"realtime": False}))
    # Order: round 1 = every gesture once (shuffled), round 2 = again... spreads fatigue evenly.
    plan = []
    rng = random.Random(a.user)
    for _ in range(a.reps):
        order = gestures[:]
        rng.shuffle(order)
        plan += order
    saved = 0
    try:
        for i, g in enumerate(plan, 1):
            print(f"\n[{i}/{len(plan)}] Next: {g.upper()}")
            take(it, RATE)  # 1 s pause, samples discarded
            for n in (3, 2, 1):
                print(f"  {n}...")
                take(it, RATE)
            print("  GO!")
            clip = take(it, N_ROWS)
            drops = count_drops(clip)
            if drops > 5:
                print(f"  WARNING: {drops} dropped samples, repeat this one later")
            rep = next_rep(folder, g)
            save_csv(folder / f"{g}_{rep:03d}.csv", clip)
            saved += 1
            print(f"  saved {g}_{rep:03d}.csv  (drops: {drops})")
    except KeyboardInterrupt:
        print("\nStopped by user.")
    print(f"\nSaved {saved} recordings in {folder}")
    n = build_manifest(Path(a.out))
    print(f"Manifest updated: {n} rows")


if __name__ == "__main__":
    main()
