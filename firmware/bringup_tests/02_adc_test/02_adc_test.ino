// Step 2: check the five analog inputs we will use for the flex sensors.
// All five are ADC1 pins (ADC2 conflicts with the radio, so we avoid it).
// Test idea: wire a 10k + 10k voltage divider (3V3 -> 10k -> pin -> 10k -> GND).
// That pin should read about 2000-2100 (half of 4095). An unconnected pin reads noisy garbage.
// Later, each flex sensor replaces the top 10k resistor of its divider.
// Open Serial Monitor at 115200 baud (or Tools -> Serial Plotter).
const int PINS[5] = {32, 33, 34, 35, 36};

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);        // 0..4095
  analogSetAttenuation(ADC_11db);  // full 0..3.3 V range
}

void loop() {
  for (int i = 0; i < 5; i++) {
    Serial.print(analogRead(PINS[i]));
    Serial.print(i < 4 ? "\t" : "\n");
  }
  delay(200);
}
