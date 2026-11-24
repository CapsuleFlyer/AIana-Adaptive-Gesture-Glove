# docs/wiring

Hardware documentation: how the glove is wired and why.

Contents (as they get made):
- Circuit diagram: ESP32, 5 flex sensors each in a voltage divider with a 10k resistor, MPU6050 on I2C.
- Pin table: flex sensors on ADC1 pins GPIO 32, 33, 34, 35, 36 (ADC2 conflicts with the radio); MPU6050 SDA = GPIO 25, SCL = GPIO 26, VCC = 3V3.
- Photos of the breadboard prototype and the finished glove.
- Bill of materials with prices.
- The role of each component (the course statement asks for this explicitly).
