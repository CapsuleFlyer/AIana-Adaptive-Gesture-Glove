# src/aiana/training

Training and evaluation code. Not written yet; the first baselines run from `scripts/run_baselines.py`.

Planned:
- Training scripts for each model.
- Evaluation: accuracy, F1, confusion matrix; **leave-one-person-out**; accuracy at 1, 3 and 5 shots; latency from end of gesture to speech heard; false-activation rate; flex vs flex + IMU ablation.
- Saving plots and tables to `results/` and models to `saved_models/`.

Reference points: the wrist-worn customization paper reports 55.3%, 83.1% and 87.2% at 1, 3 and 5 examples. SignSpeak's paper reports 92% for its best model.
