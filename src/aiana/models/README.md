# src/aiana/models

**This is where the machine learning models will go.**

**Owner:** `____`  **Status:** not started

## What goes here
- `baselines`: kNN, SVM, Random Forest on summary features. These are the numbers the neural net has to beat.
- `cnn1d`: a 1D convolutional network on the raw time series. It also produces an embedding (a compact fingerprint of a gesture) that the few-shot step uses.
- `fewshot`: prototype matching. Average the embeddings of a user's 3-5 examples into a prototype per gesture, then match new recordings to the nearest prototype. Adding a gesture needs no full retraining.
- Confidence score for each prediction (so low-confidence gestures trigger nothing)

## Write down for the report
- Why each algorithm suits our use case (generic "AI is useful" statements are not accepted)
- Input, output, and how the output drives the real-world action
