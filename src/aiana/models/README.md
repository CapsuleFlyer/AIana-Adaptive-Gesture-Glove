# src/aiana/models

Recognition models and the interface the app uses to call them.

Written so far (`api.py`):
- `Recognizer` interface: `predict(window) -> (gesture | None, confidence)`, `enroll(name, windows) -> EnrollResult`, `save`, `load`.
- `StubRecognizer`: **fake** output so the app can be built before the real model exists.
- `Normalizer`: per-user calibration. Flex channels are scaled to 0-1 from an open-hand and a fist recording; IMU channels use fixed full-scale scaling.

Planned:
- Baselines: kNN, SVM, Random Forest on summary features (the numbers the neural net must beat).
- `cnn1d`: a 1D CNN on raw windows, also used as the embedding.
- Few-shot prototype matching: average the embeddings of a user's 3-5 examples per gesture and match new recordings to the nearest prototype, so adding a gesture needs no retraining. Includes the confidence threshold and the `idle` class.
