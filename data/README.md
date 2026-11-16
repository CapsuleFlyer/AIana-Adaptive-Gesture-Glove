# data

All datasets for the project and how our own data is collected.

| Folder | Contents |
|---|---|
| [`raw/`](raw/) | Our own glove recordings, one folder per volunteer (`user01/`, `user02/`, ...), plus `manifest.csv`. |
| [`processed/`](processed/) | Cleaned, fixed-length windows ready for training. Can be regenerated from `raw/`. |
| [`external/`](external/) | The public SignSpeak dataset (flex sensors only). For pipeline development and baselines only. |

## Recording format (own data)
- One CSV per recording: `data/raw/userNN/<gesture>_<rep:03d>.csv`, for example `user03/hello_017.csv`.
- Columns: `timestamp_ms,flex1..flex5,ax,ay,az,gx,gy,gz` in raw sensor units (flex = ADC counts 0-4095, IMU = raw int16).
- Fixed 2.0 s per recording (about 100 rows at 50 Hz). Timestamps start at 0 in each file. The no-gesture class is called `idle`.
- One `session.json` per volunteer session: user, session, date, hand, condition (`normal` or `restricted:<what>`), whether the glove was re-worn, firmware version, notes.
- `python scripts/build_manifest.py` builds `raw/manifest.csv`. All train/test splits (leave-one-person-out) come from the manifest.
- Processed `.npz` files hold `X` float32 `(N, 64, C)`, `y`, `user`, `session`, with C = 11 (flex + IMU) or 5 (SignSpeak, flex only).

## How we collect
- Record with `python scripts/record.py` (guided prompts, one clip at a time).
- Target: 10+ volunteers, 15-20 gestures plus `idle`, about 20 repetitions each. At least two volunteers with a restricted-movement condition, and a few re-worn-glove sessions to test sensitivity to fit.
- Gesture order is randomized in rounds, with short breaks.
- Data freeze: Nov 28, 2026. No new recordings after that.

## Privacy and ethics
- Volunteers are identified by ID only, never by name.
- Each volunteer gives a short verbal or written OK for us to use their recordings.
- Healthy volunteers only, no clinical claims.

## Limitations to state in the report
- Few volunteers, all healthy.
- Glove fit and sensor drift differ per person and per session.
- SignSpeak has flex sensors only (no IMU), 10-bit readings at 36 Hz, so it is not directly comparable to our glove.
