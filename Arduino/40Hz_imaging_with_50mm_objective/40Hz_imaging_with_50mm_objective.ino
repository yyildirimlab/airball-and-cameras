/**
 * Title         : 40_Hz_imaging_with_50mm_objetive.ino
 * Authors       : Murat Yildirim
 *               : Miguel Maldonado
 *               : Omer Faruk Dinc
 * Date Created  : 10 October 2024
 * Description   : This code is intended to be uploaded to the Arduino
 *                 Uno that controls the brain imaging camera.
 */
const int CAMTRIGPIN = 3;
const int BLUEPIN = 9;
const int VIOLPIN = 10;
const int CMDPIN = 8;
const int TOGGLEBUTTONPIN = 11;
const int LEDINDICATORPIN = 12;
const bool MODE_TRIGGER_WITH_LED = true;
const bool MODE_TRIGGER_ONLY_CAMERA = false;

const unsigned int uS_DELAY_LED[] = {
      24000
      ,900
};
const unsigned int uS_DELAY_NO_LED  = 0;   // TODO: Calibrate for maximum capture rate
const unsigned long MS_DEBOUNCE     = 350; // For button when switching between modes

bool cmdOn;
int prevModeLED;
int currModeLED;
unsigned long msLastDebounce;

void setup() {
  pinMode(CAMTRIGPIN, OUTPUT);
  pinMode(BLUEPIN, OUTPUT);
  pinMode(VIOLPIN, OUTPUT);
  pinMode(TOGGLEBUTTONPIN, INPUT);
  pinMode(LEDINDICATORPIN, OUTPUT);
  pinMode(CMDPIN, INPUT);

  digitalWrite(CAMTRIGPIN, HIGH);
  digitalWrite(LEDINDICATORPIN, HIGH);

  cmdOn = false;
  prevModeLED = HIGH;
  currModeLED = HIGH;
  msLastDebounce = millis();
}

void loop() {

  /** ====== Button Logic ======
   *
   * Toggle the mode when the button is pressed
   */
  bool buttonPressed = (digitalRead(TOGGLEBUTTONPIN) == HIGH);
  bool debouncePassed = ((millis() - msLastDebounce) > MS_DEBOUNCE);
  if (buttonPressed && debouncePassed) {
    msLastDebounce = millis();                    // Reset the debounce reference
    currModeLED = !currModeLED;                   // Toggle the mode
    digitalWrite(LEDINDICATORPIN, currModeLED);   // Update the LED indicating the mode
  }

  /**
   * ====== Main Control ======
   *
   * This condition checks if the command pin is high (the signal from the NIDAQ to indicate camera triggering)
   * If the command pin is high, then the camera is triggered according to the current mode
   * If the command pin is low, then the LEDs are turned off
   */
  cmdOn = digitalRead(CMDPIN);
  if (cmdOn) {
   
    if (currModeLED == false && prevModeLED == true) {
    /* If the mode has just been turned off, then turn off the LEDs */
      digitalWrite(VIOLPIN, LOW);
      digitalWrite(BLUEPIN, LOW);
    }
    prevModeLED = currModeLED;

    if (currModeLED == MODE_TRIGGER_WITH_LED) {
    /* =========================== Triggering Logic With LED =========================== */
      digitalWrite(CAMTRIGPIN, HIGH);
      digitalWrite(BLUEPIN, LOW);
      delayMicroseconds(uS_DELAY_LED[0]/2);
      digitalWrite(VIOLPIN, LOW);
      delayMicroseconds(uS_DELAY_LED[1]);
      digitalWrite(CAMTRIGPIN, LOW);
      delayMicroseconds(uS_DELAY_LED[0]/2);
     
      digitalWrite(CAMTRIGPIN, HIGH);
      digitalWrite(BLUEPIN, HIGH);
      delayMicroseconds(uS_DELAY_LED[0]/2);
      digitalWrite(VIOLPIN, HIGH);
      delayMicroseconds(uS_DELAY_LED[1]);
      digitalWrite(CAMTRIGPIN, LOW);
      delayMicroseconds(uS_DELAY_LED[0]/2);
    }
    else {
    /* ========================== Triggering Logic Only Camera ========================== */
      digitalWrite(CAMTRIGPIN, HIGH);
      delayMicroseconds(uS_DELAY_NO_LED/2);
      digitalWrite(CAMTRIGPIN, LOW);
      delayMicroseconds(uS_DELAY_NO_LED/2);
    }
  }
  else {
    digitalWrite(BLUEPIN, LOW);
    digitalWrite(VIOLPIN, LOW);
  }
}

