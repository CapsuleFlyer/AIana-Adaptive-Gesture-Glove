# How the project will go

Working plan from Oct 25 to the Dec 6 submission. Dates are targets, not promises. Adjust them as a group.

## Roles (split work, review each other's parts)

| Area | What it covers | Owner |
|---|---|---|
| Hardware | wiring, ESP32 firmware, glove build, power, sensor calibration | `____` |
| ML / data | data collection protocol, preprocessing, models, evaluation, conflict checker | `____` |
| Laptop / speech | glove reader, text-to-speech, virtual mic, laptop actions, app UI | `____` |

Everyone: collect data from volunteers, write their part of the report, and be able to explain all parts.

## Phases

### Phase 0: Setup (Oct 25 - Oct 27)
- [ ] Sheet row submitted and cell locked
- [ ] GitHub repo created, everyone has push access, branches per person
- [ ] Parts ordered (see the shopping list in the team chat)
- [ ] Download SignSpeak into `data/external/`
- [ ] Decide sampling rate and window length (starting guess in `configs/settings.yaml`)

### Phase 1: Build in parallel (Oct 28 - Nov 9)
- **Hardware:** breadboard the ESP32 + 5 flex sensors + MPU6050, stream readings to the laptop, then move onto the glove
- **ML:** load SignSpeak, fixed-length windows, kNN/SVM/Random Forest baselines, first confusion matrix
- **Laptop:** text-to-speech into a virtual mic, test it in a Meet/Zoom call with a teammate
- Milestone: glove prints live readings, and baselines run on SignSpeak

### Phase 2: Our own data (Nov 10 - Nov 22)
- Write the collection protocol in `data/README.md` (gestures, repetitions, order)
- Collect 15-20 gestures from 10+ volunteers, about 20 repetitions each, including a restricted-movement condition
- Idle/"no gesture" class included
- Milestone: raw data in `data/raw/`, one folder per volunteer ID

### Phase 3: Models and personalization (Nov 16 - Nov 30)
- 1D-CNN on our own data, compare with baselines
- Few-shot personalization: accuracy at 1, 3 and 5 examples
- Confidence threshold and false-activation rate
- Conflict checker
- Evaluation: leave-one-person-out, confusion matrices, latency (end of gesture to speech heard)
- Milestone: core classifier reliable on our own glove (target: end of November)

### Phase 4: Integration (Nov 24 - Dec 2)
- Gesture -> action map (`configs/gestures.json`): speak a phrase or run a laptop action
- 5-8 laptop actions and a confirm gesture for risky ones
- Enrollment/training UI: record a new gesture, link it to a phrase or action
- Full run-through of the demo script in `docs/demo/`
- Auto-reconnect for Bluetooth/serial drops
- Milestone: full demo works start to finish, three times in a row

### Phase 5: Deliverables (Dec 1 - Dec 6)
- Report, slides, pipeline diagram, testing evidence
- Pre-recorded video of the working glove (upload to Google Drive, submit the link)
- Clean the repo, zip, one member submits on GCR by Dec 6

### Dec 7-9: Live demonstration
The live demo is mandatory even with a video. Practice it.

## If time runs short, cut in this order
1. Urdu speech, LSTM comparison, pretraining, TinyML, extra feedback hardware
2. Extra laptop actions (keep 3-4)
3. Conflict checker
4. Never cut: glove -> classifier -> few-shot personalization -> speech into a call, plus honest evaluation

## What a demo could look like
1. Wear the glove and join a call with a teammate
2. Make a trained gesture: the phrase is heard in the call
3. Teach a new gesture from 3-5 examples, link it to a phrase
4. Use it right away
5. Make a gesture that triggers a laptop action (switch tab), including a confirm gesture
6. Show the conflict checker warning on a too-similar gesture
7. Show the results slide: accuracy vs number of examples, unseen users, latency

## Risks
- Flex sensors break at the base (buy spares)
- Similar gestures get confused (conflict checker, confusion matrix)
- Sensor drift and glove fit differ per person (calibration, test on new people)
- Bluetooth drops mid-demo (auto-reconnect, wired fallback)
- Collecting data takes longer than expected (start in Phase 2 without waiting for polish)
