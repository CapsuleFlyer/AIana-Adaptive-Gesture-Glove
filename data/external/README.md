# data/external

The public **SignSpeak** dataset (American Sign Language letters and numbers from a 5-flex-sensor glove). The dataset file itself is git-ignored: download it yourself.

## Download
Run once: `python scripts/download_data.py` (needs internet; the file is git-ignored, so every team member does this). If it fails, do it by hand:

1. Open https://doi.org/10.7910/DVN/ODY7GH (Harvard Dataverse, "SignSpeak American Sign Language Dataset", Version 1.1).
2. Files tab, then `SignSpeakDataset.csv` (tab-delimited, about 9.8 MB), then Download.
3. Save it as `data/external/SignSpeakDataset.csv`.
4. Check the layout: `python scripts/inspect_dataset.py data/external`. The table has `_id`, `word` (the label) and 395 columns `hand[t][s]` (time step 0-78, sensor 0-4, empty after the gesture ends). The loader in `src/aiana/preprocessing/signspeak.py` reads exactly these names.

## About it
- 7,200 samples, 36 classes (A-Z, 1-10), 5 flex sensors, no IMU.
- Recorded at 36 Hz, 50-80 time steps per gesture, 10-bit values (0-1023) from an Arduino.
- The table has 397 variables. License: CC0 (public domain). Paper: https://arxiv.org/abs/2407.12020

## How we use it
- Build and test the whole pipeline before the glove is ready.
- Baseline numbers (kNN, SVM, Random Forest) with `python scripts/run_baselines.py`.
- Optional pretraining before fine-tuning on our own data.
- It is **not** a claim about our glove's accuracy: different sensors, rate and resolution, and no custom gestures.

## Cite
Makkar, A., Makkar, D., Patel, A., Hebert, L. (2024). SignSpeak American Sign Language Dataset, V1.1. Harvard Dataverse. https://doi.org/10.7910/DVN/ODY7GH
