# data

**This is where all datasets and the data-collection plan will go.**

**Owner:** `____`  **Status:** not started

## Folders
| Folder | What goes there |
|---|---|
| `raw/` | Our own glove recordings, one subfolder per volunteer (`user01/`, `user02/`, ...) |
| `processed/` | Cleaned, fixed-length windows ready for training |
| `external/` | The SignSpeak dataset (public, downloaded) |

## Data-collection protocol (fill in before collecting)
- Gestures (15-20 plus an "idle / no gesture" class): `____`
- Repetitions per gesture per volunteer: about 20
- Volunteers: 10+, at least a couple with a restricted-movement condition (for example using only three fingers)
- Window length and sample rate: see `configs/settings.yaml`
- Order: randomize gesture order, give short breaks, re-wear the glove between sessions for a couple of people (tests sensitivity to fit)

## File format (decide and document)
One CSV per recording, for example `user03/hello_017.csv`, with columns
`timestamp_ms,flex1..flex5,ax,ay,az,gx,gy,gz` and the label in the filename or a labels file.

## Privacy and ethics
- Identify volunteers by ID only, never names
- Get a short verbal or written OK from each volunteer to use their recordings
- Healthy volunteers only. No clinical claims in the report.

## Data limitations to write about in the report
- Small number of volunteers, healthy participants only
- Glove fit and sensor drift differ per person
- The public SignSpeak data has flex sensors only (no IMU), 10-bit readings from an Arduino, and a different sampling rate than ours
