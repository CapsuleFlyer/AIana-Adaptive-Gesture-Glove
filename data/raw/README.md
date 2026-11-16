# data/raw

Our own glove recordings, exactly as streamed from the glove (raw ADC counts and raw IMU values).

```
raw/
├── manifest.csv            # built by scripts/build_manifest.py: path,user,session,gesture,rep,condition
├── user01/
│   ├── session.json        # who, when, which hand, condition, whether the glove was re-worn
│   ├── hello_001.csv
│   ├── hello_002.csv
│   └── idle_001.csv
└── user02/ ...
```

- One folder per volunteer, named by ID, never by name.
- Each CSV is a fixed 2.0 s recording with columns `timestamp_ms,flex1..flex5,ax,ay,az,gx,gy,gz`.
- Create these with `python scripts/record.py --user user01 --gestures hello,yes,idle --reps 5` (see `scripts/README.md`).
- Do not edit files by hand. Bad recordings are re-recorded and the manifest is rebuilt.

Format details and the collection plan are in [`../README.md`](../README.md).
