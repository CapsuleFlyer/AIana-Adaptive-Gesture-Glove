# References

Use these for the report's related-work section. Check each entry against the original page before citing (details here come from abstracts and project pages).

## Datasets
- Makkar, A., Makkar, D., Patel, A., Hebert, L. (2024). *SignSpeak American Sign Language Dataset* (V1.1). Harvard Dataverse. https://doi.org/10.7910/DVN/ODY7GH (CC0)
- Makkar, A., Makkar, D., Patel, A., Hebert, L. (2024). *SignSpeak: Open-Source Time Series Classification for ASL Translation.* arXiv:2407.12020. https://arxiv.org/abs/2407.12020

## Closest existing projects
- Caschetto-Bottcher, M., Lee, J., Wareing, D. *Lexicon Glove* (ENG5220 Real Time Embedded Programming project). https://github.com/mcbottcher/ENG5220 (MIT) and wiki https://github.com/mcbottcher/ENG5220/wiki
- Kanwal, T., Yousaf, R. M., Altaf, S., Sattar, K. (2025). *A Smart Glove-Based System for Dynamic Sign Language Translation Using LSTM Networks.* Proc. 12th Int. Electronic Conf. on Sensors and Applications, MDPI. https://www.mdpi.com/2673-4591/118/1/45
- Leiva, V. et al. (2025). *A Real-Time Intelligent System Based on Machine-Learning Methods for Improving Communication in Sign Language.* IEEE Access, vol. 13. https://doi.org/10.1109/ACCESS.2025.3529025
- *Talking Glove for Mute People* (2021), NUML. https://numl.edu.pk/department/179/project/154
- Ayoub, H. (2022). *Designing a Sensor-Based Wearable Computing System for Custom Hand Gesture Recognition Using Machine Learning.* PhD thesis, Goldsmiths, University of London. https://research.gold.ac.uk/id/eprint/31706

## Few-shot / personalized gestures
- *Enabling Hand Gesture Customization on Wrist-Worn Devices.* arXiv:2203.15239. https://arxiv.org/pdf/2203.15239 (TODO: add the author list from the arXiv page.)
- *Wearable Sensor-Based Few-Shot Continual Learning on Hand Gestures for Motor-Impaired Individuals via Latent Embedding Exploitation.* arXiv:2405.08969. https://arxiv.org/pdf/2405.08969

## Sensor fusion
- *Smart Wearable Hand Device for Sign Language Interpretation System with Sensors Fusion.* IEEE Sensors Journal. DOI 10.1109/JSEN.2017.2779466. (TODO: look up the author list and year before citing.)

## Tools and libraries (cite if used)
- LiveLingo (virtual-mic pipeline). https://github.com/roirude/LiveLingo
- ESP32 BLE Combo (Bluetooth keyboard/mouse). https://github.com/ServAlex/ESP32-BLE-Combo
- VB-CABLE virtual audio device. https://vb-audio.com/Cable/
- gTTS, pyttsx3, VoiceConductor (text-to-speech)

## Our own contribution (what makes this different)
- Speech goes into a live video call as a virtual microphone
- Few-shot personalization with accuracy reported at 1, 3 and 5 examples
- Gesture conflict checker at enrollment
- Evaluation on unseen volunteers, including a restricted-movement condition
- Gesture -> speech **or** laptop action from one dictionary
