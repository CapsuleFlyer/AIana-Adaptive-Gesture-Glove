# src/aiana/conflict

**This is where the gesture conflict checker will go.**

**Owner:** `____`  **Status:** not started

## What it does
When a user teaches a new gesture, measure how close it is to the gestures that already exist (distance between their embeddings or prototypes). If it is too close, warn the user: "too similar to 'yes', try a bigger movement."

## Why
Similar gestures get confused by the classifier, and a wrong phrase in a call is worse than none. Other work found that users with atypical movement sometimes need gesture sets that avoid similar patterns.

## How we will show it works
- Compare confusion rate with and without the checker
- Check that the pairs it flags match the pairs the confusion matrix says get mixed up

Threshold lives in `configs/settings.yaml`.
