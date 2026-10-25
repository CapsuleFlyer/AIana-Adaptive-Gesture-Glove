# data/processed

**This is where cleaned, fixed-length windows will go** (output of `src/aiana/preprocessing`).

**Owner:** `____`  **Status:** not started

Expected contents later: filtered and normalized arrays (for example `.npy` or `.csv`) with labels and a volunteer ID per sample, so we can split by person for leave-one-person-out evaluation.

These files can be regenerated from `raw/`, so they are fine to leave out of the final zip if size is a problem.
