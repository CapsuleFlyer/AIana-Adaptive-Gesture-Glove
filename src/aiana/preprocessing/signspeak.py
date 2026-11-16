"""SignSpeak loader: data/external/SignSpeakDataset.csv -> X (N, 64, 5) float32, y labels, users.

The dataset is ONE tab-delimited table (7,200 rows, 397 columns): one row per gesture, one label column,
and the 5 flex sensors over 50-80 time steps spread across the remaining columns.
I could not download it while writing this, so the exact column layout is a GUESS:
  - the label is the one non-numeric column (or a column named label/class/sign/letter)
  - the leftover numeric columns are sensor values, optionally after a few leading meta columns
    (e.g. an id or length) so that the count is divisible by 5
  - sensor-major order (all steps of sensor 1, then sensor 2, ...); pass layout="time" for step-major
Run `python scripts/inspect_dataset.py data/external` and check the printout. If it differs, fix
`_split_columns` below (it is the only place that depends on the layout). The loader prints what it assumed.
There is no person ID in the table as far as we know, so users are all "unknown": results are NOT unseen-person results.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from aiana.acquisition.reader import resample

STEPS = 64
LABEL_NAMES = ("label", "class", "sign", "letter", "gesture", "target")


def _split_columns(df):
    """Returns (labels, numeric array (N, K), number of leading meta columns dropped)."""
    label_col = next((c for c in df.columns if str(c).strip().lower() in LABEL_NAMES), None)
    if label_col is None:
        non_num = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        label_col = non_num[0] if non_num else df.columns[-1]
    labels = df[label_col].astype(str).to_numpy()
    num = df.drop(columns=[label_col]).apply(pd.to_numeric, errors="coerce")
    num = num.dropna(axis=1, how="all")
    n_meta = next((m for m in range(6) if (num.shape[1] - m) % 5 == 0), None)
    if n_meta is None:
        raise ValueError(f"{num.shape[1]} numeric columns cannot split into 5 sensors; run inspect_dataset.py")
    return labels, num.iloc[:, n_meta:].to_numpy(dtype=np.float32), n_meta


def load_signspeak(root="data/external", layout="sensor"):
    path = Path(root) / "SignSpeakDataset.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing: download it as described in data/external/README.md")
    df = pd.read_csv(path, sep=None, engine="python")
    labels, vals, n_meta = _split_columns(df)
    n, k = vals.shape
    steps = k // 5
    if layout == "sensor":
        arr = vals.reshape(n, 5, steps).transpose(0, 2, 1)   # (N, steps, 5)
    else:
        arr = vals.reshape(n, steps, 5)
    print(f"[signspeak] {n} rows, label column ok, dropped {n_meta} leading meta col(s), "
          f"{steps} steps x 5 sensors, layout={layout}-major (GUESS: verify with inspect_dataset.py)")
    X = []
    for a in arr:
        keep = ~np.isnan(a).all(axis=1)          # trim NaN padding at the end if present
        a = a[keep] if keep.sum() >= 5 else a
        X.append(resample(np.nan_to_num(a), STEPS))
    return np.stack(X).astype(np.float32), labels, np.array(["unknown"] * n)


def per_user_minmax(X, users):
    """Scale each sensor to 0..1 per user (ADC ranges differ between people/sessions)."""
    X = X.copy()
    for u in np.unique(users):
        m = users == u
        lo = X[m].min(axis=(0, 1), keepdims=True)
        hi = X[m].max(axis=(0, 1), keepdims=True)
        X[m] = (X[m] - lo) / np.maximum(hi - lo, 1e-6)
    return X
