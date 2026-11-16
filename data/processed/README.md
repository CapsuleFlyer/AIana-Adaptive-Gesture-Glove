# data/processed

Cleaned, fixed-length windows made from `data/raw/` or `data/external/`, ready for training and evaluation.

- Format: `.npz` with `X` float32 `(N, 64, C)`, `y` (gesture labels), `user` (volunteer ID) and `session`.
- `C = 11` for our glove (5 flex + 3 accel + 3 gyro), `C = 5` for SignSpeak (flex only).
- The `user` array is what makes leave-one-person-out evaluation possible.
- Everything here can be regenerated from the raw data, so it is safe to leave out of the final zip if size is a problem.

Produced by `src/aiana/preprocessing/`.
