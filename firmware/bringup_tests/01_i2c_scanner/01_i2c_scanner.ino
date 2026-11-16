// Step 1: find the MPU6050 on the I2C bus.
// Wiring: MPU6050 VCC -> 3V3, GND -> GND, SDA -> GPIO 21, SCL -> GPIO 22
// Open Serial Monitor at 115200 baud. Expect: "Found device at 0x68".
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  delay(1000);
  Serial.println("Scanning I2C...");
}

void loop() {
  int found = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf("Found device at 0x%02X\n", addr);
      found++;
    }
  }
  if (found == 0) {
    Serial.println("No I2C devices found. Check: VCC=3V3, GND, SDA=GPIO21, SCL=GPIO22, solder joints.");
  }
  Serial.println("--- scan done ---");
  delay(3000);
}
