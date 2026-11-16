// AIana glove firmware v1 (draft).
// Streams one line per sample at 50 Hz in the agreed serial format:
//   boot banner : #AIANA,fw=1,rate_hz=50,adc_bits=12,acc_fs=4g,gyr_fs=500dps
//   sample      : S,<seq>,<t_ms>,<f1>,<f2>,<f3>,<f4>,<f5>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>
// Lines starting with '#' are info/errors. Commands from the laptop (one line each): PING, START, STOP.
// Values are RAW (flex = ADC counts 0..4095, IMU = raw int16). Calibration lives on the laptop.
//
// Wiring: flex dividers on GPIO 32,33,34,35,36 (ADC1), MPU6050 SDA=21, SCL=22, VCC=3V3.
#include <Wire.h>

// ---- settings ----
const bool SIMULATE_FLEX = true;   // true = flex sensors not connected yet, send constant 2048
const bool STREAM_ON_BOOT = true;  // true = stream right away (easy for Serial Monitor testing)
const int FLEX_PINS[5] = {32, 33, 34, 35, 36};
const uint8_t MPU_ADDR = 0x68;
const uint32_t PERIOD_US = 20000;  // 50 Hz

bool streaming = STREAM_ON_BOOT;
uint32_t seq = 0;
uint32_t nextTick = 0;
String cmd;

bool mpuWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

// Reads accel XYZ, skips temperature, reads gyro XYZ (raw int16).
bool readMpu(int16_t v[6]) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MPU_ADDR, 14) != 14) return false;
  v[0] = (Wire.read() << 8) | Wire.read();  // ax
  v[1] = (Wire.read() << 8) | Wire.read();  // ay
  v[2] = (Wire.read() << 8) | Wire.read();  // az
  Wire.read(); Wire.read();                 // temperature (ignored)
  v[3] = (Wire.read() << 8) | Wire.read();  // gx
  v[4] = (Wire.read() << 8) | Wire.read();  // gy
  v[5] = (Wire.read() << 8) | Wire.read();  // gz
  return true;
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  Wire.begin(21, 22);
  Wire.setClock(400000);
  delay(200);

  bool ok = mpuWrite(0x6B, 0x00);  // wake up
  ok = ok && mpuWrite(0x1C, 0x08); // accel +-4 g  (8192 LSB/g)
  ok = ok && mpuWrite(0x1B, 0x08); // gyro +-500 dps (65.5 LSB/dps)
  if (!ok) Serial.println("#ERR,mpu_not_found_check_wiring");

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x75);  // WHO_AM_I
  Wire.endTransmission(false);
  if (Wire.requestFrom((int)MPU_ADDR, 1) == 1) {
    Serial.printf("#INFO,who_am_i=0x%02X\n", Wire.read());  // usually 0x68 (some clones differ)
  }
  Serial.println("#AIANA,fw=1,rate_hz=50,adc_bits=12,acc_fs=4g,gyr_fs=500dps");
  nextTick = micros();
}

void handleCommand(const String &c) {
  if (c == "PING") Serial.println("#PONG");
  else if (c == "START") { streaming = true; seq = 0; Serial.println("#OK,start"); }
  else if (c == "STOP") { streaming = false; Serial.println("#OK,stop"); }
  else Serial.println("#ERR,unknown_command");
}

void loop() {
  // read commands without blocking
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') { cmd.trim(); if (cmd.length()) handleCommand(cmd); cmd = ""; }
    else if (ch != '\r' && cmd.length() < 32) cmd += ch;
  }

  if (!streaming) return;
  if ((int32_t)(micros() - nextTick) < 0) return;  // not time yet
  nextTick += PERIOD_US;

  int flex[5];
  for (int i = 0; i < 5; i++) flex[i] = SIMULATE_FLEX ? 2048 : analogRead(FLEX_PINS[i]);

  int16_t imu[6];
  if (!readMpu(imu)) {
    Serial.println("#ERR,mpu_read_failed");
    return;
  }

  Serial.printf("S,%lu,%lu,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n",
                (unsigned long)seq, (unsigned long)millis(),
                flex[0], flex[1], flex[2], flex[3], flex[4],
                imu[0], imu[1], imu[2], imu[3], imu[4], imu[5]);
  seq++;
}
