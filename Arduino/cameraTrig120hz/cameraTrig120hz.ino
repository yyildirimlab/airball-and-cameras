/**
 * Title         : cameraTrig120Hz.ino
 * Authors       : Miguel Maldonado
 *               : Omer Faruk Dinc
 * Date Created  : 28 November 2025
 * Description   : This code is intended to be uploaded to the Arduino Uno
 *                 and is calibrated to capture at 120Hz.
 */
const int CAMTRIGPIN = 3;
const int CMDPIN = 8;
const int uS_DELAY = 8300; // Calibrated with Oscilloscope

bool cmdOn = false;

void setup() {
  pinMode(CAMTRIGPIN, OUTPUT);
  pinMode(CMDPIN, INPUT);
  digitalWrite(CAMTRIGPIN, HIGH);
}

void loop() {
  cmdOn = digitalRead(CMDPIN);
  if (cmdOn) {
    digitalWrite(CAMTRIGPIN, HIGH);
    delayMicroseconds(uS_DELAY/2);
    digitalWrite(CAMTRIGPIN, LOW);
    delayMicroseconds(uS_DELAY/2);
  }
}
