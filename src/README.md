# src

The Python package `aiana` (in [`aiana/`](aiana/)): everything the laptop runs.

Data flows in this order: `acquisition` reads the glove, `preprocessing` cleans and normalizes, `models` recognizes the gesture, `conflict` checks new gestures, `actions` speaks or acts, `app` ties it together. `training` is offline work on the models.
