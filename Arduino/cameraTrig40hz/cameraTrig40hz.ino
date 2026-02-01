/**
 * Title         : cameraTrig40Hz.ino
 * Authors       : Miguel Maldonado
 *               : Omer Faruk Dinc
 * Date Created  : 28 November 2025
 * Description   : This code is intended to be uploaded to the Arduino Uno
 *                 and is calibrated to capture at 40Hz.
 */
const int CAMTRIG_PIN = 3;
const int CMD_PIN = 8;
const int uS_DELAY = 8300 * 3; // Calibrated with Oscilloscope

bool cmdOn = false;

void setup() {
  pinMode(CAMTRIG_PIN, OUTPUT);
  pinMode(CMD_PIN, INPUT);
  digitalWrite(CAMTRIG_PIN, HIGH);
}

void loop() {
  cmdOn = digitalRead(CMD_PIN);
  if (cmdOn) {
    digitalWrite(CAMTRIG_PIN, HIGH);
    delayMicroseconds(uS_DELAY/2);
    digitalWrite(CAMTRIG_PIN, LOW);
    delayMicroseconds(uS_DELAY/2);
  }
}
