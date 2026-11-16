# scripts

Command-line tools. Run them from the repository root.

| Script | What it does |
|---|---|
| `reader.py` | Reads the glove's serial stream and prints rate, dropped samples and converted IMU values every second. Close the Arduino Serial Monitor first. `python scripts/reader.py [COM5]` |
| `record.py` | Guided recorder: "do HELLO, 3, 2, 1, GO", saves 2 s clips to `data/raw/<user>/`. `python scripts/record.py --user user01 --gestures hello,yes,idle --reps 5` (add `--source fake` to try it without a glove) |
| `build_manifest.py` | Builds `data/raw/manifest.csv` from all recordings (the recorder also runs it). |
| `download_data.py` | One-time download of the external datasets (SignSpeak) into `data/external/`, which is git-ignored. Run once per person. |
| `inspect_dataset.py` | Prints the structure of a dataset folder, to verify the SignSpeak loader. |
| `run_baselines.py` | kNN / SVM / Random Forest baselines with confusion matrices. `--synthetic` is a self-test without data. |
| `speech_test.py` | Tests text-to-speech into the virtual mic (VB-CABLE) and prints latency. `--list` shows audio devices. |

Planned: `make_report_figures.py` to regenerate all figures in `results/`.
