# results

Evaluation outputs: figures and tables for the report and slides.

Expected contents:
- Confusion matrices (baselines and 1D-CNN). `python scripts/run_baselines.py` writes `cm_<model>.csv` and `.png` here.
- Accuracy vs number of examples (1, 3 and 5 shots).
- Leave-one-person-out results table.
- Latency: end of gesture to phrase heard in the call.
- False-activation rate and the confidence-threshold trade-off.
- Sensor ablation: flex only vs flex + IMU.
- A short written interpretation next to each result (the course requires results to be reported and interpreted).

Always label what each result is from: our own glove or the SignSpeak benchmark, and how many volunteers and recordings it used.
