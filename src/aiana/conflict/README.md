# src/aiana/conflict

The gesture conflict checker. Not written yet.

When a user teaches a new gesture, it measures how close the gesture is to existing ones (distance between embeddings or prototypes). If it is too close, it warns: "too similar to 'yes', try a bigger movement."

**Why:** similar gestures get confused, and a wrong phrase in a call is worse than none.

**How we will show it works:** compare the confusion rate with and without the checker, and check that the pairs it flags match the pairs the confusion matrix says get mixed up.

The threshold is `conflict_checker.similarity_warning_threshold` in `configs/settings.yaml`.
