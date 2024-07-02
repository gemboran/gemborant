// https://github.com/BlynkGO/ESP32-BLE-Combo
#include <BleCombo.h>

#define ONBOARD_LED 2

signed char delta[3] = {0, 0, 0};

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);

  Keyboard.begin();
  Mouse.begin();
  pinMode(ONBOARD_LED, OUTPUT);
}

void loop() {
  if(Keyboard.isConnected()) {
      delta[0] = 0;
      delta[1] = 0;
      delta[2] = 0;

      if (Serial.available() > 0) {
        char inChar = Serial.read();
        if (inChar == 'M') {
          Serial.readBytes((char *)&delta, 2);
        }
        else if (inChar == 'C') {
          Mouse.click(MOUSE_LEFT);
        }
        else if (inChar == 'P') {
          Keyboard.press('P');
        }
        else if (inChar == 'R') {
          Keyboard.release('P');
        }
        else if (inChar == 'X') {
          if (Mouse.isPressed(MOUSE_LEFT)) {
            Mouse.release(MOUSE_LEFT);
          } else {
            Mouse.press(MOUSE_LEFT);
          }
        }
        Mouse.move(delta[0], delta[1], delta[2]);
      }
      delay(10);
  } else {
    digitalWrite(ONBOARD_LED, HIGH);  // turn the LED on (HIGH is the voltage level)
    delay(1000);                      // wait for a second
    digitalWrite(ONBOARD_LED, LOW);   // turn the LED off by making the voltage LOW
    delay(1000);                      // wait for a second
  }
}
