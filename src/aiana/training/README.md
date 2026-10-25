# src/aiana/training

**This is where training and evaluation scripts will go.**

**Owner:** `____`  **Status:** not started

## What goes here
- Training scripts for each model
- **Evaluation:**
  - accuracy, F1, confusion matrix
  - **leave-one-person-out** (train on everyone but one volunteer, test on that person)
  - **accuracy vs number of examples** (1, 3 and 5 shots) for few-shot personalization
  - latency from the end of a gesture to speech heard
  - false-activation rate (the glove acted when no gesture was made)
- Saving plots and tables into `results/` and models into `saved_models/`

Reference point: the wrist-worn customization paper reports 55.3%, 83.1% and 87.2% accuracy at 1, 3 and 5 examples. SignSpeak's paper reports 92% for its best model.
