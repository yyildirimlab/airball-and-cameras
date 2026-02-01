/**
 * Title         : 40_Hz_optogenetics_with_50mm_objetive.ino
 * Authors       : Murat Yildirim
 *               : Miguel Maldonado
 * Date Created  : 15 December 2024
 * Description   : This code is intended to be uploaded to the Arduino
 *                 Uno that controls the brain imaging camera.
 *                 This code includes logic for using the laser.
 *
 *                 Pin 11 toggles between "LED Mode" and "Image-Only Mode".
 *                 An indicator on pin 12 can show what mode this code is using.
 *
 *                 LED Mode:
 *                 - When the CMDPIN is high and LASERPIN is low,
 *                 it captures images at 40Hz while alternating Blue and Violet LEDs.
 *
 *                 - When CMDPIN is high and LASERPIN is high,
 *                 it capture's images at 40Hz, but only alternates the LEDs
 *                 for frames while the LASERTRIGPIN is also high.
 *
 *                 Image-Only Mode:
 *                 - When the CMDPIN is high, the code simply captures images at
 *                 maximum speed without flashing LEDs.
 */
const int CAMTRIGPIN = 3;
const int BLUEPIN = 9;
const int VIOLPIN = 10;
const int CMDPIN = 8;
const int LASERTRIGPIN = 6;
const int LASERPIN = 13;
const int TOGGLEBUTTONPIN = 11;
const int LEDINDICATORPIN = 12;
const bool MODE_TRIGGER_WITH_LED = true;
const bool MODE_TRIGGER_LASER = true;
const bool MODE_TRIGGER_ONLY_CAMERA = false;

const unsigned int uS_DELAY_LED[] = {
      2250
      ,200
};
const unsigned int uS_DELAY_NO_LED  = 0;
const unsigned long MS_DEBOUNCE     = 350;

bool cmdOn;
int prevModeLED;
int currModeLED;
unsigned long msLastDebounce;
bool laserOn;
bool laserMode;
bool laserSignal;

void setup() {
  pinMode(CAMTRIGPIN, OUTPUT);
  pinMode(BLUEPIN, OUTPUT);
  pinMode(VIOLPIN, OUTPUT);
  pinMode(TOGGLEBUTTONPIN, INPUT);
  pinMode(LEDINDICATORPIN, OUTPUT);
  pinMode(CMDPIN, INPUT);
  pinMode(LASERPIN, INPUT);
  pinMode(LASERTRIGPIN, INPUT);

  digitalWrite(CAMTRIGPIN, HIGH);
  digitalWrite(LEDINDICATORPIN, HIGH);

  laserOn = false;
  laserSignal = false;
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

      laserMode = digitalRead(LASERPIN);
      if (laserMode == MODE_TRIGGER_LASER) {
        /* =========================== Laser Trigger LEDs =========================== */        
        laserSignal = digitalRead(LASERTRIGPIN);
        if (laserSignal) {
          digitalWrite(CAMTRIGPIN, HIGH);
          digitalWrite(BLUEPIN, LOW);
          delayMicroseconds(uS_DELAY_LED[0]);
          delayMicroseconds(uS_DELAY_LED[1]);
          digitalWrite(CAMTRIGPIN, LOW);
          
          digitalWrite(CAMTRIGPIN, HIGH);
          digitalWrite(BLUEPIN, HIGH);
          delayMicroseconds(uS_DELAY_LED[0]);
          delayMicroseconds(uS_DELAY_LED[1]);
          digitalWrite(CAMTRIGPIN, LOW);
        } else {
          digitalWrite(CAMTRIGPIN, HIGH);
          delayMicroseconds(uS_DELAY_LED[0]);
          delayMicroseconds(uS_DELAY_LED[1]);
          digitalWrite(CAMTRIGPIN, LOW);
        }
      } else {
        /* =========================== Alternate LEDs =========================== */
        digitalWrite(CAMTRIGPIN, HIGH);
        digitalWrite(BLUEPIN, LOW);
        delayMicroseconds(uS_DELAY_LED[0]);
        digitalWrite(VIOLPIN, LOW);
        delayMicroseconds(uS_DELAY_LED[1]);
        digitalWrite(CAMTRIGPIN, LOW);
        
        digitalWrite(CAMTRIGPIN, HIGH);
        digitalWrite(BLUEPIN, HIGH);
        delayMicroseconds(uS_DELAY_LED[0]);
        digitalWrite(VIOLPIN, HIGH);
        delayMicroseconds(uS_DELAY_LED[1]);
        digitalWrite(CAMTRIGPIN, LOW);
      }
    } 
    else {
    /* ========================== Trigger Cameras Only ========================== */
      digitalWrite(CAMTRIGPIN, HIGH);
      delayMicroseconds(uS_DELAY_LED[0]);
      delayMicroseconds(uS_DELAY_LED[1]);
      digitalWrite(CAMTRIGPIN, LOW);
    }
  }
  else {
    digitalWrite(BLUEPIN, LOW);
    digitalWrite(VIOLPIN, LOW);
  }
}
