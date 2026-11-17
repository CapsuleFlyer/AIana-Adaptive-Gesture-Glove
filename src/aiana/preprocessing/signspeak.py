"""SignSpeak loader: data/external/SignSpeakDataset.csv -> X (N, 64, 5) float32, y labels, users.

Real layout (checked with scripts/inspect_dataset.py on the downloaded file):
  - tab-delimited table, 7,200 rows, 397 columns
  - `_id`: database id (ignored); `word`: the label (letters a-z and numbers)
  - `hand[t][s]`: flex reading at time step t (0..78), sensor s (0..4); unused steps at the end are empty (NaN)
There is no person ID in the table, so every row gets user "unknown": results on it are NOT unseen-person results.
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

from aiana.acquisition.reader import resample

STEPS = 64
COL = re.compile(r"hand\[(\d+)\]\[(\d+)\]")


def load_signspeak(root="data/external"):
    path = Path(root) / "SignSpeakDataset.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing: run python scripts/download_data.py")
    df = pd.read_csv(path, sep=None, engine="python")
    if "word" not in df.columns:
        raise ValueError(f"no 'word' label column; columns start with {list(df.columns[:5])}")
    cols = [(int(m.group(1)), int(m.group(2)), c) for c in df.columns if (m := COL.fullmatch(str(c)))]
    n_steps, n_sens = max(t for t, _, _ in cols) + 1, max(s for _, s, _ in cols) + 1
    if n_sens != 5:
        raise ValueError(f"expected 5 sensors, found {n_sens}")
    arr = np.full((len(df), n_steps, n_sens), np.nan, dtype=np.float32)
    for t, s_, c in cols:
        arr[:, t, s_] = pd.to_numeric(df[c], errors="coerce").to_numpy(dtype=np.float32)
    X = []
    for a in arr:
        a = a[~np.isnan(a).all(axis=1)]          # drop the empty (NaN) steps at the end
        if len(a) < 5:
            raise ValueError("a row has fewer than 5 valid steps")
        X.append(resample(np.nan_to_num(a), STEPS))
    y = df["word"].astype(str).to_numpy()
    print(f"[signspeak] {len(df)} rows, {len(set(y))} classes, up to {n_steps} steps x {n_sens} sensors -> 64 steps")
    return np.stack(X).astype(np.float32), y, np.array(["unknown"] * len(df))


def per_user_minmax(X, users):
    """Scale each sensor to 0..1 per user (ADC ranges differ between people/sessions)."""
    X = X.copy()
    for u in np.unique(users):
        m = users == u
        lo = X[m].min(axis=(0, 1), keepdims=True)
        hi = X[m].max(axis=(0, 1), keepdims=True)
        X[m] = (X[m] - lo) / np.maximum(hi - lo, 1e-6)
    return X
