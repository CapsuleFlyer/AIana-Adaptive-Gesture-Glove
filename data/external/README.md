# data/external

**This is where the SignSpeak dataset will go.**

**Owner:** `____`  **Status:** not downloaded

## Download
1. Open https://doi.org/10.7910/DVN/ODY7GH (Harvard Dataverse, "SignSpeak American Sign Language Dataset", Version 1.1)
2. Files tab -> `SignSpeakDataset.csv` (tab-delimited, about 9.8 MB) -> Download
3. Save it here as `data/external/SignSpeakDataset.csv`

## About it
- 7,200 samples, 36 classes (A-Z, 1-10), 5 flex sensors
- Recorded at 36 Hz, 50-80 time steps per gesture, 10-bit values (0-1023) from an Arduino
- Table has 397 variables and 7,200 observations. Check which columns hold the sensor values and the label before writing the loader.
- License: CC0 (public domain)
- Paper: https://arxiv.org/abs/2407.12020

## How we use it
- Build and test the whole pipeline before our glove is ready
- Baseline numbers for the report ("our model on SignSpeak vs the published 92%")
- Try the few-shot experiment (hold out some classes, add them from 1/3/5 examples)
- Optional: pretrain, then fine-tune on our own data

It has no IMU data and no custom or atypical gestures, so it cannot replace our own dataset.

## Cite
Makkar, A., Makkar, D., Patel, A., Hebert, L. (2024). SignSpeak American Sign Language Dataset, V1.1. Harvard Dataverse. https://doi.org/10.7910/DVN/ODY7GH
