| Area | Owner | Backup | Covers |
|---|---|---|---|
| A. Hardware + firmware + data-collection station | P1 | P3 | wiring, firmware, glove build, power, daily sensor check, running volunteer sessions, wiring docs, pipeline diagram, demo video, slides assembly |
| B. ML + evaluation + conflict checker | P2 | P1 | collection protocol, SignSpeak loader, preprocessing, baselines, 1D-CNN, few-shot, thresholds, LOPO, results figures, conflict checker |
| C. Laptop app + speech + actions + demo + report | P3 | P2 | serial reader + windowing, recorder, virtual mic + TTS, laptop actions + confirm, enrollment UI, auto-reconnect, demo script, report assembly, final zip |

Rules:
- The **backup reviews every PR** in the area. No merge without the backup's approval. This is how backups actually learn the code.
- Load balance: P1 is heaviest Nov 14-25 and lightest after Nov 28 (so P1 takes diagram, video, slides). P2 is heaviest Nov 22-Dec 1. P3 is steady, then assembles the report.
- The glove is a single point of failure. P3 helps build it (pair build), so P3 can rebuild or re-flash it alone.
- Everyone attends and runs at least two volunteer sessions.

## 2. Interfaces (freeze v1 by Nov 13, change only through a PR + message to the group)

### 2.1 Serial line from the ESP32 (USB serial, 115200 baud, 50 Hz)
Board: ESP32 WROOM-32, 38-pin dev board with CP2102 USB-serial and USB Type-C (classic ESP32, so Bluetooth Classic serial is available). Suggested pins: flex on ADC1 GPIO 32, 33, 34, 35, 36; MPU6050 on I2C GPIO 21 (SDA) / 22 (SCL). Install the CP210x driver on the demo laptop and use a USB **data** cable.
```
# boot banner (once):  #AIANA,fw=1,rate_hz=50,adc_bits=12,acc_fs=4g,gyr_fs=500dps
# sample (one per line): S,<seq>,<t_ms>,<f1>,<f2>,<f3>,<f4>,<f5>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>
```
- `seq`: counter that starts at 0 and increases by 1 per sample (the laptop counts drops from gaps).
- `t_ms`: `millis()` on the ESP32.
- `f1..f5`: raw ADC counts (0-4095), thumb to pinky. Use ADC1 pins only.
- `ax..gz`: raw int16 from the MPU6050. The laptop converts with the full-scale values in the banner.
- Lines starting with `#` are info or errors. The parser ignores any malformed line and counts it.
- Laptop to ESP32 (one line each): `PING`, `START`, `STOP`. Firmware streams raw values; **calibration and normalization live on the laptop**.

### 2.2 Recording CSV (our own data)
```
data/raw/user03/hello_017.csv
timestamp_ms,flex1,flex2,flex3,flex4,flex5,ax,ay,az,gx,gy,gz
```
- Same raw units as the serial line. `timestamp_ms` starts at 0 for each recording. Fixed 2.0 s recording per gesture (about 100 rows).
- File name = `<gesture>_<rep:03d>.csv`. Gesture slug: lowercase `[a-z0-9-]`. No-gesture class is `idle`.
- One `session.json` per volunteer session: `user_id, session_id, date, hand, condition (normal | restricted:<what>), refit (true if glove was re-worn), fw_version, rate_hz, notes`.
- `scripts/build_manifest.py` builds `data/raw/manifest.csv` (`path,user,session,gesture,rep,condition`). All splits (leave-one-person-out) come from the manifest.
- Processed data: `.npz` with `X` float32 `(N, 64, C)`, `y`, `user`, `session`. `C` = 11 (flex + IMU) or 5 (SignSpeak, flex only). The SignSpeak loader must output the same shape.

### 2.3 Recognizer API (P2 delivers, P3 calls)
```python
# aiana/models/api.py   (a StubRecognizer with fake output ships on Nov 13)
Window = np.ndarray   # (64, C) float32, already per-user normalized to 0..1

def predict(window: Window) -> tuple[str | None, float]:
    """(gesture, confidence). gesture is None if idle or confidence < threshold."""

class Recognizer:
    def predict(self, window) -> tuple[str | None, float]: ...
    def enroll(self, name: str, windows: list[Window]) -> EnrollResult: ...
        # EnrollResult(ok: bool, nearest: str | None, similarity: float, warning: str | None)
    def save(self, path): ...
    @classmethod
    def load(cls, path): ...

class Normalizer:      # P2 delivers
    def fit(self, open_hand: np.ndarray, fist: np.ndarray): ...
    def transform(self, raw_window: np.ndarray) -> Window: ...
```
- P3's acquisition code exposes `read_samples()` (real serial, replay, or fake source: same interface), so everyone can develop without the glove.
- `configs/gestures.json` and `configs/settings.yaml` are shared files. Change through a PR.

### 2.4 Decisions to make together by Nov 20 (they affect everyone)
- **Segmentation:** we record fixed 2 s clips, but live use is continuous. Decision: onset detection (gyro/flex activity gate) captures a 2 s window, an `idle` class rejects non-gestures, and the same gesture must win on N consecutive windows plus a refractory period before anything is spoken.
- **Few-shot split:** train the embedding on SignSpeak + our "base" gestures. Keep 4-5 gestures as "novel" (never seen in training) and enroll them from 1/3/5 examples on the held-out person. Otherwise the 1/3/5-shot curve is not a true few-shot result.
- **ASL starter dictionary:** SignSpeak is letters/numbers, flex only, 36 Hz. Our starter set = 8-10 gestures we verify are separable on our glove (recorded by us). SignSpeak is for pipeline development, baselines and optional pretraining, not a claim about our glove's ASL accuracy.

### 2.5 Measurable targets (adjust after the Nov 20 pilot, then freeze)
- Unseen person, base gestures: >= 80% accuracy (leave-one-person-out).
- Personalized, novel gestures: 1 / 3 / 5 shots reported; target >= 90% at 5 shots. Benchmark: 55.3 / 83.1 / 87.2% (arXiv 2203.15239).
- False activations: <= 1 per 5 min of idle wearing with normal hand movement.
- Latency, end of gesture to phrase heard in the call: <= 1.5 s.

## 3. Timeline

**Feature freeze: Tue Dec 1 (end of day).** After it: bug fixes, evaluation, report, slides, video only.
**Data freeze: Sat Nov 28.** No new recordings after that. Final numbers use frozen data.
**Submission target: Sat Dec 5 evening.** Dec 6 is buffer only.

### Now to Nov 15: before the hardware arrives
- P1: pin table (flex on ADC1 pins, MPU6050 on I2C), voltage-divider calculation, glove layout sketch (strain relief at the finger base). Firmware v0 that compiles and has a SIMULATE mode. Order 2-3 extra flex sensors now.
- P2: download SignSpeak, notebooks 01-02 (explore, loader, kNN/SVM/RF baselines, first confusion matrix). Draft the collection protocol (gesture list, reps, order, consent line). Write the LOPO and few-shot evaluation plan. Ship the StubRecognizer.
- P3: install VB-CABLE, TTS into the virtual mic, test in a real Meet/Zoom call, measure latency. Actions module + confirm logic + tests. Reader, parser, windowing and fake glove source with tests. App skeleton.
- All: freeze interface v1, pick PyTorch (delete the tensorflow line), line up 10+ volunteers (2 with a restricted-movement condition), agree on branches and PR rules.

### Week 1: Nov 16-22 (hardware week)
- Breadboard bring-up Nov 17, reader on the real board Nov 18, glove v1 Nov 20.
- Recorder + calibration + QC script by Nov 19-22.
- **Pilot Nov 19-20:** the three of us record, check noise, drift and separability, then lock the gesture list and targets.
- Cross-explaining session Tue Nov 17.

### Week 2: Nov 23-29 (data + models + integration)
- Volunteers 1-6 by Nov 25, 7-10+ by Nov 28 (data freeze).
- Models on pilot data from Nov 22; few-shot + threshold + conflict checker by Nov 27-28.
- **Walking skeleton by Thu Nov 26:** glove -> reader -> predict -> speech in a call, even with a weak model.
- Wireless is optional; go/no-go on Nov 26, only if the USB demo is already stable. First choice is Bluetooth Classic serial (the ESP32 `BluetoothSerial` library; Windows shows it as a COM port, so the reader needs almost no change). BLE only after that.
- Cross-explaining session Tue Nov 24.

### Week 3: Nov 30-Dec 3 (evaluation + freeze + deliverables)
- Nov 30: final LOPO, shots curve, ablation (flex vs flex+IMU), confusion matrices. Dec 1: latency and false-activation runs, **feature freeze**, three full demo run-throughs in a row.
- Dec 2: figures, pipeline diagram final, report sections drafted. Dec 3: video recorded and uploaded, report assembled.
- Cross-explaining session Tue Dec 1.

### Dec 4-6
- Dec 4: slides done, mock viva, zip dry run from a fresh venv. Dec 5: submit (one member). Dec 6: buffer.
- Dec 5-6: demo rehearsal in a real call, pack the demo kit (spare USB cable, power bank, spare flex wiring, laptop charger, VB-CABLE installed).
- Dec 7-9: live demo.

## 4. Everyone can explain everything
- **Weekly teach-back (Tue Nov 17, Nov 24, Dec 1; 45 min):** the *backup* explains the area (10 min) to the other two. Then each of the other two asks 3 questions. Record unanswered ones in `docs/qa-log.md` and close them by the next session.
- **PR rule:** no merge without the backup's review.
- **Swap run:** each member runs the full demo (wear glove, enroll a gesture, speak into a call) and does one hardware task (re-flash, re-seat a sensor).
- **Mock viva Fri Dec 4:** random member, random question from the question bank (below). A member who stumbles gets the topic re-taught the same day.
- **Question bank (start now in `docs/qa-log.md`):** why 1D-CNN and why prototype matching, what a voltage divider does, why ADC1 pins, why per-user normalization, how the virtual mic works, what leave-one-person-out means, how the confidence threshold is chosen, how the conflict checker works, what the limits are.

## 5. Top 5 risks and fallbacks

| # | Risk | Prevention | Fallback |
|---|---|---|---|
| 1 | Flex sensor or wiring breaks (finger-base fracture, loose jumper) | Strain relief, extra sensors ordered now, daily min/max sensor check, hot-glue/solder instead of loose breadboard wires before volunteers | Spare sensor swap in under 30 min (P3 can do it). If a sensor is lost for good: 4 flex + IMU; channels are configurable, retrain. A breadboard version stays working as a spare rig. |
| 2 | Too few volunteers or too little data (one glove, sessions are sequential) | Budget: 18 gestures x 20 reps is about 35-45 min per person with breaks; book slots now; team members count as 3 volunteers | Minimum viable set: 12 gestures x 15 reps from 8 people (incl. 2 restricted-movement). Say clearly in the report how many people and recordings we actually have. |
| 3 | Overfits to one person, poor unseen-user accuracy, or false activations in live use | Per-user normalization, idle class, augmentation (noise, time-warp, amplitude), leave-one-person-out from day one, separable gesture set, debounce + confirm gesture | Report zero-shot and personalized numbers honestly. Raise the confidence threshold and use a bigger gesture-to-gesture margin. If the CNN does not beat kNN/DTW, ship the simpler model and say so. |
| 4 | Connection or audio failure at demo (BLE drops, COM port, VB-CABLE routing, no internet) | USB serial is the primary demo path. Auto-reconnect. Offline TTS (pyttsx3) only. Rehearse in a real call on the demo laptop | Wired fallback, then "speak to speakers" mode if the virtual mic fails, then the pre-recorded video plus a live explanation. The live demo is still mandatory. |
| 5 | Schedule slip or a member unavailable (exams, illness) | Walking skeleton Nov 26, freeze Dec 1, backup per area, short weekly sync | Cut in the README order (Urdu, LSTM, pretraining, TinyML, BLE first; extra actions to 3-4; conflict checker last). Never cut: glove -> classifier -> few-shot -> speech into a call, plus honest evaluation. |

## 6. Task table

| ID | Task | Owner | Backup | Due | Depends on |
|---|---|---|---|---|---|
| T01 | Branches, PR rules, PyTorch only, member names in READMEs, volunteer list started | P3 | P2 | Nov 12 | - |
| T02 | Freeze interface spec v1 (`docs/interfaces.md`: serial, CSV, Recognizer API) | P2 | P1 | Nov 13 | T01 |
| T03 | StubRecognizer + Normalizer stub | P2 | P3 | Nov 13 | T02 |
| T04 | Order extra flex sensors, spare wires/resistors | P1 | P3 | Nov 12 | - |
| T05 | Pin table, divider calc, glove layout sketch | P1 | P3 | Nov 14 | - |
| T06 | Firmware v0 compiles, SIMULATE mode | P1 | P3 | Nov 14 | T02 |
| T07 | Reader, parser, windowing, fake glove source + tests | P3 | P2 | Nov 15 | T02 |
| T08 | VB-CABLE + TTS into a real call, latency measured | P3 | P1 | Nov 14 | - |
| T09 | Actions module + confirm/cancel logic + tests; real `gestures.json` v1 | P3 | P2 | Nov 16 | T02 |
| T10 | SignSpeak loader, fixed-length windows, baselines, first confusion matrix | P2 | P1 | Nov 15 | - |
| T11 | Collection protocol v1 (gestures, reps, order, consent) + volunteer schedule | P2 | P3 | Nov 16 | T01 |
| T12 | Evaluation plan (LOPO, base/novel split, shots, targets) in `docs/` | P2 | P1 | Nov 16 | T10 |
| T13 | Breadboard bring-up: 5 flex + MPU6050 streaming, firmware v1 | P1 | P3 | Nov 17 | parts, T06 |
| T14 | Reader on real board; check rate and drops | P3 | P1 | Nov 18 | T07, T13 |
| T15 | Recorder script (guided prompts, CSV + session.json + manifest) | P3 | P2 | Nov 18 | T07, T11 |
| T16 | Calibration (open/fist) + per-user normalizer | P2 | P1 | Nov 19 | T14 |
| T17 | Glove build v1 (mount, strain relief, cable, power bank), pair build with backup | P1 | P3 | Nov 20 | T13 |
| T18 | Pilot recordings (the team), noise/drift/separability notebook; lock gestures, targets, segmentation decision | P2 | P1 | Nov 20 | T15, T16, T17 |
| T19 | Data QC script (flatline, saturation, drops) + daily sensor check | P2 | P1 | Nov 22 | T15 |
| T20 | Wiring doc: circuit diagram, pin table, BOM, photos, role of each part | P1 | P3 | Nov 22 | T17 |
| T21 | Collection sessions, volunteers 1-6 (P1 runs the station) | P1 | P3 | Nov 25 | T18 |
| T22 | Collection sessions, volunteers 7-10+, restricted-movement + re-wear sessions | P1 | P3 | Nov 28 (data freeze) | T21 |
| T23 | Baselines + 1D-CNN on own data (pilot, then growing) | P2 | P1 | Nov 25 | T18 |
| T24 | Walking skeleton: glove -> predict -> speech in a call | P3 | P2 | Nov 26 | T14, T03, T08 |
| T25 | Auto-reconnect + unplug test + wired fallback | P3 | P1 | Nov 27 | T24 |
| T26 | Few-shot prototypes, idle class, confidence threshold | P2 | P1 | Nov 27 | T23 |
| T27 | Conflict checker + check against confusion-matrix pairs | P2 | P3 | Nov 28 | T26 |
| T28 | Real Recognizer swapped into the app | P3 | P2 | Nov 28 | T26 |
| T29 | Enrollment UI (record 3-5, link phrase/action, conflict warning) | P3 | P2 | Nov 29 | T27 or stub |
| T30 | Wireless link: Bluetooth Classic serial as a COM port (stretch, go/no-go Nov 26) | P1 | P3 | Nov 29 | T24, T25 |
| T31 | Final evaluation on frozen data: LOPO, 1/3/5 shots, ablation, confusion matrices | P2 | P1 | Nov 30 | T22, T26 |
| T32 | Latency + false-activation measurement runs | P3 | P2 | Dec 1 | T28 |
| T33 | **Feature freeze** + three demo run-throughs in a row | P3 | P1 | Dec 1 | T28, T29, T32 |
| T34 | Results figures script (`make_report_figures.py`) + written interpretation | P2 | P3 | Dec 2 | T31, T32 |
| T35 | Pipeline diagram (+ enrollment flow), final | P1 | P3 | Dec 2 | T33 |
| T36 | Report section drafts (hardware P1, ML P2, app/speech P3), related work + "how we differ from Lexicon Glove" | P3 | P2 | Dec 2 | T20, T31 |
| T37 | Demo video recorded, uploaded to Google Drive, link saved in `docs/demo/video-link.txt` | P1 | P3 | Dec 3 | T33 |
| T38 | Report assembly + peer review by all | P3 | P2 | Dec 3 | T34, T35, T36 |
| T39 | Slides | P1 | P2 | Dec 4 | T34, T35 |
| T40 | Mock viva + teach-back sessions (Nov 17, Nov 24, Dec 1, Dec 4) | P2 | P3 | Dec 4 | - |
| T41 | Repo clean-up + zip dry run (fresh venv, final model included, no `.git`, no `reference_code`) | P3 | P2 | Dec 4 | T38 |
| T42 | Final zip on GCR (one member) + video link in zip and in the GCR submission | P3 | P1 | Dec 5 (deadline Dec 6) | T37, T41 |
| T43 | Demo rehearsal in a real call + demo kit packed | P1 | P3 | Dec 6 | T33 |

