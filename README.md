# AIana: Adaptive Gesture Glove

> Giving every gesture a voice.

A sensor glove that **learns each user's own gestures** and turns them into **speech on live video calls** or **hands-free laptop actions**, built for people with limited speech or mobility.

**Course:** AI2002 Artificial Intelligence, Semester Project, Fall 2026 (FAST-NUCES Islamabad)
**Path:** B (Hardware-based)
**Group #:** `7`
**Members:** `24i-3060`, `24i-3062`, `24i-3081` (yes you guys are just numbers to me :smirk:)

---

## 1. The problem

People with limited speech or mobility (for example ALS, stroke, cerebral palsy, spinal injury) often cannot speak, use a keyboard, or form standard sign language. Fixed sign-language systems fail on their atypical movements, and they usually stop at text on a screen.

**Users:** non-speaking or limited-mobility users, and the people they talk to on video calls (family, doctors, interviewers).

**Our solution:** a glove (5 flex sensors + MPU6050 IMU + ESP32) plus a laptop app. The user teaches the glove their own gestures from a few examples. Each gesture is mapped to either a spoken phrase (played into a video call through a virtual microphone) or a laptop action (scroll, switch tab, play/pause). A small ASL starter dictionary ships with it and can be extended.

**Why ML is needed:** every user moves differently, so a fixed dictionary cannot cover them. A model that adapts from 3-5 examples per gesture is the core of the project.

> Honesty note for the report: we test with healthy volunteers, including restricted-movement conditions. We make no clinical claims.

---

## 2. How it works (pipeline)

```
 GLOVE                         LAPTOP (Python)
 -----                         ---------------
 5 flex sensors  ┐
                 ├─> ESP32 ──> serial/BLE ──> window (~2 s) ──> filter + normalize
 MPU6050 IMU     ┘   (sample)                                   (per-user calibration)
                                                                      │
                                                                      ▼
                                       classifier: baselines (kNN/SVM/RF) + 1D-CNN
                                                                      │
                                                  few-shot prototype matching (new gestures
                                                  from 3-5 examples) + confidence threshold
                                                                      │
                          conflict checker (at enrollment: "too similar to 'yes'")
                                                                      │
                                                                      ▼
                                              gesture -> action map (configs/gestures.json)
                                                      │                        │
                                                      ▼                        ▼
                                         SPEAK: text-to-speech        LAPTOP ACTION: shortcut
                                         -> virtual mic -> call       (risky ones need a
                                                                       confirm gesture)
```

A proper diagram goes in `docs/architecture/`. Full plan: [`docs/project-flow.md`](docs/project-flow.md).

### Core vs stretch

| Core (must work for the demo) | Stretch (only if core is solid) |
|---|---|
| Glove streams flex + IMU data | Pretraining on SignSpeak, then fine-tuning |
| Data collection from 10+ volunteers | Urdu speech output |
| kNN/SVM/RF baselines + 1D-CNN | LSTM comparison |
| Few-shot personalization (1/3/5 examples) | Vibration/LED feedback on the glove |
| Confidence threshold (no random speech) | Fingertip contact sensor for confusable gestures |
| Speech into a video call (virtual mic) | TinyML on the ESP32 |
| 5-8 laptop actions + confirm gesture | |
| Conflict checker | |
| Evaluation: accuracy vs shots, unseen users, latency | |

---

## 3. Start here (check these out first)

| | Resource | Why it matters |
|---|---|---|
| ✩ | [Lexicon Glove (GitHub)](https://github.com/mcbottcher/ENG5220) and its [Neural Network wiki page](https://github.com/mcbottcher/ENG5220/wiki/Neural-Network) | Closest existing project: flex + IMU glove, user-trained custom gestures linked to phrases, spoken output. Shows a sliding 2 s window and a confidence threshold. Records its own data (no external dataset). |
| ✩ | [SignSpeak paper (arXiv 2407.12020)](https://arxiv.org/abs/2407.12020) | Open ASL flex-sensor glove dataset, benchmarks of LSTM/GRU/Transformer models (best 92%). |
| ✩ | [SignSpeak dataset (Harvard Dataverse, CC0)](https://doi.org/10.7910/DVN/ODY7GH) | 7,200 samples, 36 classes (A-Z, 1-10), 5 flex sensors at 36 Hz, 50-80 time steps each. Our reference/baseline data. One 9.8 MB tab-delimited CSV. |
| - | [Enabling hand gesture customization on wrist-worn devices (arXiv 2203.15239)](https://arxiv.org/pdf/2203.15239) | Few-shot gesture adding. Reports accuracy at 1, 3 and 5 examples (55.3%, 83.1%, 87.2%). A benchmark for our own curve. |
| - | [Few-shot learning for motor-impaired users (arXiv 2405.08969)](https://arxiv.org/pdf/2405.08969) | Learning new gestures from few samples from motor-impaired people. Matches our user story. |
| - | [LiveLingo (GitHub)](https://github.com/roirude/LiveLingo) | How to push synthesized speech into Zoom/Meet/Teams through VB-CABLE (virtual mic). |
| - | [GloveTalk (Hackster)](https://www.hackster.io/signspeak/glovetalk-converting-sign-language-to-words-6b86ef) | ESP32 + flex sensors + MPU6050 wiring and starter code. |
| ✩ | [PSL glove with LSTM (MDPI, 2025)](https://www.mdpi.com/2673-4591/118/1/45) | Local prior work (Pakistan Sign Language). Examiners may know it, so we should know how we differ. |

## 4. More resources

**Gloves and gesture recognition**
- [Georgescu ASL glove](https://ocw.cs.pub.ro/courses/pm/prj2025/iotelea/ageorgescu2407): softmax regression on an ESP32, 80% confidence cutoff
- [Vision Voice, Fab Academy 2026](https://fabacademy.org/2026/labs/dgi/students/sonam-tshering/assignments/week17/): standalone ESP32-C3 glove with on-device template capture
- [IEEE Access 2025, PSL glove](https://doi.org/10.1109/ACCESS.2025.3529025): flex + MPU-6050, ten PSL signs
- [NUML Talking Glove](https://numl.edu.pk/department/179/project/154): 13 PSL signs plus an Urdu/English voice switch
- [Goldsmiths PhD thesis on custom-gesture wearables](https://research.gold.ac.uk/id/eprint/31706): per-user classifier from small samples
- [InterpreterGlove (ERCIM News)](https://ercim-news.ercim.eu/en99/ri/interpreterglove-an-assistive-tool-that-can-speak-for-the-deaf-and-deaf-mute): user-defined gesture alphabet
- [Somatic glove (Hackaday)](https://hackaday.io/project/169297-somatic-wearable-control-anywhere): honest write-up of overfitting and poor results while walking
- [Smart wearable hand device with sensor fusion (IEEE Sensors J.)](https://www.academia.edu/37516061/Hand_Device_for_Sign_Language): pressure sensors lifted accuracy from 65.7% to 98.2%
- [PenSLR (Persian)](https://arxiv.org/pdf/2406.16388): glove with IMU + 5 flex sensors and a public dataset repo

**Datasets**
- [SignSpeak dataset](https://doi.org/10.7910/DVN/ODY7GH) (above)
- [Sensor-based ASL glove data, Kaggle mirror](https://baselight.app/u/kaggle/dataset/mouadfiali_sensor_based_american_sign_language_recognition): flex + IMU, reported incomplete, and the mirror may be down

**ESP32 firmware and laptop control**
- [ESP32 BLE Combo (keyboard + mouse)](https://github.com/ServAlex/ESP32-BLE-Combo), [NimBLE variant](https://github.com/A-box1000/ESP32-NimBLE-Combo)
- [Magic Wand: ESP32 + MPU6050 gesture recognition](https://github.com/Sidiment/Magic-Wand)
- [ESP32 + MPU6050 TinyML tutorial](https://shillehtek.com/blogs/news/esp32-mpu6050-gesture-recognition-on-device)

**Speech and the virtual microphone**
- [VoiceConductor](https://pypi.org/project/voiceconductor/): route text-to-speech to a virtual mic with phrase caching
- [text-to-speech-mic](https://www.github.com/maalcjke/text-to-speech-mic)
- [gTTS (supports Urdu, needs internet)](https://github.com/atulkushwaha0112-py/text-to-speech-using-gtts-and-python), [LughaatNLP (Urdu)](https://pypi.org/project/LughaatNLP/1.0.5)

Citation entries for the report live in [`docs/references.md`](docs/references.md).

---

## 5. Repository layout

```
aiana-glove/
├── README.md               <- you are here
├── requirements.txt        <- Python packages
├── configs/                <- gestures.json (gesture -> action), settings.yaml
├── firmware/glove_esp32/   <- ESP32 code (reads sensors, streams to laptop)
├── data/
│   ├── raw/                <- our own glove recordings (one folder per volunteer)
│   ├── processed/          <- cleaned, fixed-length windows
│   └── external/           <- SignSpeak dataset (downloaded)
├── src/aiana/
│   ├── acquisition/        <- read glove stream, cut into windows
│   ├── preprocessing/      <- filtering, normalization, per-user calibration
│   ├── models/             <- baselines, 1D-CNN, few-shot prototypes
│   ├── training/           <- training + evaluation (leave-one-person-out)
│   ├── conflict/           <- "this gesture is too similar" checker
│   ├── actions/            <- text-to-speech, virtual mic, laptop actions
│   └── app/                <- main loop + enrollment/training UI
├── notebooks/              <- exploration and experiments
├── saved_models/           <- trained model files
├── results/                <- confusion matrices, plots, metric tables
├── scripts/                <- helper scripts (download data, record samples)
├── tests/                  <- tests
├── reference_code/         <- other people's repos cloned for READING only (git-ignored)
└── docs/
    ├── project-flow.md     <- phases, timeline, who does what
    ├── deliverables-checklist.md
    ├── references.md       <- citations
    ├── architecture/       <- pipeline diagram
    ├── wiring/             <- circuit diagram and glove photos
    ├── report/             <- final report
    ├── slides/             <- presentation
    ├── demo/               <- demo script, video link
    └── papers/             <- PDFs of papers we cite
```

Every working folder has a `README.md` saying what goes there and who owns it. Fill in the **Owner** and **Status** lines as work starts.

---

## 6. Key dates

| Date | What |
|---|---|
| Dec 6, 2026 | Final submission: one zip per group on GCR |
| Dec 7-9, 2026 | Live demonstrations |

Details and weekly targets: [`docs/project-flow.md`](docs/project-flow.md). Required deliverables: [`docs/deliverables-checklist.md`](docs/deliverables-checklist.md).

---

## 7. Ground rules

- Other projects are **reference only**. We write our own code and cite everything we learn from (the course prohibits copying).
- Every member must be able to explain every part of the project.
- Keep API keys and personal data out of the repo. Volunteers are identified by an ID (`user01`, `user02`, ...), never by name.
- Commit often, in small pieces, from your own branch.

## 8. Quick start

*(Fill in once code exists.)*

```bash
pip install -r requirements.txt
# 1. flash firmware/glove_esp32 to the ESP32
# 2. python -m aiana.app.main
```
