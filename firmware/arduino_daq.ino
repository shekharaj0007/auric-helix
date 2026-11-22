/*
 * Minimal DAQ firmware for the machining dashboard.
 *
 * Wiring (5 V Arduino Uno / Nano):
 *   A0  analog accelerometer (or amplified IEPE via signal conditioner)
 *   A1  SCT-013 current transformer (burdened and offset to 2.5 V)
 *   A2  LM35 / analog temperature (10 mV/°C)  — optional
 *   A3  analog force (from charge amp)        — optional
 *
 * Serial 115200:
 *   millis,vibration,current_a,temperature_c[,force_n]
 *
 * Incoming commands from the dashboard (closed-loop mode):
 *   CMD,FEED,<mm/tooth>
 *   CMD,RPM,<rpm>
 *   CMD,STOP,<reason>
 * Pin 8 goes HIGH on STOP — wire through a relay to CNC feed-hold only after
 * you have validated the circuit. This is not a certified emergency stop.
 *
 * In the dashboard: Data source = serial, port = COM3 (Windows).
 */

const int PIN_VIB = A0;
const int PIN_CUR = A1;
const int PIN_TMP = A2;
const int PIN_FRC = A3;
const int PIN_FEEDHOLD = 8;
const bool HAS_FORCE = false;

const float VREF = 5.0;
const float CURRENT_SCALE = 20.0 / 512.0;  // calibrate against a clamp meter
const float TEMP_SCALE_C_PER_V = 100.0;    // LM35
const int SAMPLE_DELAY_MS = 2;             // ~500 Hz

void setup() {
  Serial.begin(115200);
  pinMode(PIN_FEEDHOLD, OUTPUT);
  digitalWrite(PIN_FEEDHOLD, LOW);
}

void handleCommands() {
  if (!Serial.available()) {
    return;
  }
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.startsWith("CMD,STOP")) {
    digitalWrite(PIN_FEEDHOLD, HIGH);
  }
}

void loop() {
  handleCommands();
  int rawV = analogRead(PIN_VIB);
  int rawC = analogRead(PIN_CUR);
  int rawT = analogRead(PIN_TMP);

  float vib = (rawV - 512) * (VREF / 1023.0);
  float current = (rawC - 512) * CURRENT_SCALE;
  float temp = analogRead(PIN_TMP) * (VREF / 1023.0) * TEMP_SCALE_C_PER_V;

  Serial.print(millis());
  Serial.print(',');
  Serial.print(vib, 4);
  Serial.print(',');
  Serial.print(current, 4);
  Serial.print(',');
  Serial.print(temp, 2);

  if (HAS_FORCE) {
    float force = analogRead(PIN_FRC) * (VREF / 1023.0) * 200.0;
    Serial.print(',');
    Serial.print(force, 2);
  }
  Serial.println();
  delay(SAMPLE_DELAY_MS);
}
