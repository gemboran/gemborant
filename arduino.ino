/**
 * This example turns the ESP32 into a Bluetooth LE mouse that scrolls down every 2 seconds.
 */
#include <BleMouse.h>

#define ONBOARD_LED 2

BleMouse bleMouse;

signed char delta[3] = {0, 0, 0};

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);

  bleMouse.begin();
  pinMode(ONBOARD_LED, OUTPUT);
}

void loop() {
  if(bleMouse.isConnected()) {
      delta[0] = 0;
      delta[1] = 0;
      delta[2] = 0;

      if (Serial.available() > 0) {
        char inChar = Serial.read();
        if (inChar == 'M')
          Serial.readBytes((char *)&delta, 2);
        else if (inChar == 'C')
          bleMouse.click();
      }
      bleMouse.move(delta[0], delta[1], delta[2]);
  } else {
    digitalWrite(ONBOARD_LED, HIGH);  // turn the LED on (HIGH is the voltage level)
    delay(1000);                      // wait for a second
    digitalWrite(ONBOARD_LED, LOW);   // turn the LED off by making the voltage LOW
    delay(1000);                      // wait for a second
  }
}
