# docs/architecture

System design. The report requires a proper pipeline diagram.

Contents (as they get made):
- `pipeline.png` or `.svg`: glove, ESP32, laptop, model, action. A short note on each block says what goes in and what comes out.
- An optional second diagram of the enrollment flow: record 3-5 examples, run the conflict check, save the gesture.

The overall data flow: 5 flex sensors + MPU6050 are read by the ESP32 at 50 Hz and sent over USB serial; the laptop cuts the stream into windows, normalizes them per user, and the recognizer returns a gesture and a confidence; a confident gesture becomes a spoken phrase (played into a call through a virtual mic) or a laptop action.
