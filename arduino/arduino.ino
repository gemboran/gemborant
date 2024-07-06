// https://github.com/BlynkGO/ESP32-BLE-Combo
#include <BleCombo.h>

#define ONBOARD_LED 2

const uint8_t MOUSE_CMD            = 0xE0;
const uint8_t MOUSE_CALIBRATE      = 0xE1;
const uint8_t MOUSE_PRESS          = 0xE2;
const uint8_t MOUSE_RELEASE        = 0xE3;

const uint8_t MOUSE_CLICK          = 0xE4;
const uint8_t MOUSE_FAST_CLICK     = 0xE5;
const uint8_t MOUSE_MOVE           = 0xE6;
const uint8_t MOUSE_BEZIER         = 0xE7;

const uint8_t LEFT_BUTTON          = 0xEA; 
const uint8_t RIGHT_BUTTON         = 0xEB;
const uint8_t MIDDLE_BUTTON        = 0xEC;

const uint8_t KEYBOARD_CMD         = 0xF0;
const uint8_t KEYBOARD_PRESS       = 0xF1;
const uint8_t KEYBOARD_RELEASE     = 0xF2;
const uint8_t KEYBOARD_RELEASE_ALL = 0xF3;
const uint8_t KEYBOARD_PRINT       = 0xF4;
const uint8_t KEYBOARD_PRINTLN     = 0xF5;
const uint8_t KEYBOARD_WRITE       = 0xF6;
const uint8_t KEYBOARD_TYPE        = 0xF7;

const uint8_t SCREEN_CALIBRATE     = 0xFF;
const uint8_t COMMAND_COMPLETE     = 0xFE;

typedef struct point {
  uint16_t x;
  uint16_t y;
} Point;

Point SCREEN_DIMENSIONS;
Point MOUSE_POSITION;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);

  Keyboard.begin();
  Mouse.begin();
  pinMode(ONBOARD_LED, OUTPUT);
}

void loop() {
  if(Keyboard.isConnected()) {
    if (Serial.available() > 0) {
      switch (Serial.read())
      {
        case MOUSE_CMD:
          parseMouseCommand();
          break;
          
        case KEYBOARD_CMD:
          parseKeyboardCommand();
          break;
      }
    }
  }
}

void parseMouseCommand()
{
  while (!Serial.available());
  uint8_t command = Serial.read();
  
  switch (command)
  {
    case MOUSE_CLICK:
      humanClick(readMouseButton());
      break;
    
    case MOUSE_FAST_CLICK:
      Mouse.click(readMouseButton());
      break;
      
    case MOUSE_PRESS:
      Mouse.press(readMouseButton());
      break;
      
    case MOUSE_RELEASE:
      Mouse.release(readMouseButton());
      break;
      
    default:
      Point destination;
      readPoint(destination);
      
      switch (command)
      {
        case MOUSE_MOVE:
          besenhamMove(destination);
          break;
        
        case MOUSE_BEZIER:
          bezierMove(destination);
          break;
      }
  }
  
  Serial.write(COMMAND_COMPLETE);
}

void readPoint(Point &p)
{
  while (!Serial.available()); p.x = Serial.read();
  while (!Serial.available()); p.x += Serial.read() << 8;
  while (!Serial.available()); p.y = Serial.read();
  while (!Serial.available()); p.y += Serial.read() << 8;
}

void calibrateMouse()
{
  Serial.write(MOUSE_CALIBRATE);
  readPoint(MOUSE_POSITION);
}

void calibrateScreen()
{
  Serial.write(SCREEN_CALIBRATE);
  readPoint(SCREEN_DIMENSIONS);
}

int readMouseButton()
{
  while (!Serial.available());
  switch (Serial.read())
  {
    case LEFT_BUTTON:
      return MOUSE_LEFT;
      break;
    case MIDDLE_BUTTON:
      return MOUSE_MIDDLE;
      break;
    case RIGHT_BUTTON:
      return MOUSE_RIGHT;
      break;
  }
}

void humanClick(int mouseButton)
{
  Mouse.press(mouseButton);
  delay(random(50, 100));
  Mouse.release(mouseButton);
}

void bezierMove(Point destination)
{
  calibrateMouse();
  calibrateScreen();
  
  // STEP * NUM_STEP = 1.0
  const double STEP = 0.01;
  const int NUM_STEP = 100;
  
  // number of control points
  const int NUM_CONTROL_POINTS = 2;
  
  int x1 = MOUSE_POSITION.x;
  int y1 = MOUSE_POSITION.y;
  int x2 = constrain(destination.x, 0, SCREEN_DIMENSIONS.x - 1);
  int y2 = constrain(destination.y, 0, SCREEN_DIMENSIONS.y - 1);
  
  Point controlPoints[NUM_CONTROL_POINTS];
  
  for (int i = 0; i < NUM_CONTROL_POINTS; i++)
  {
    controlPoints[i].x = random(0, SCREEN_DIMENSIONS.x);
    controlPoints[i].y = random(0, SCREEN_DIMENSIONS.y);
  }
  
  for (int i = 0; i <= NUM_STEP; i++)
  {
    double x_weights[] = 
    {
      x1,
      controlPoints[0].x,
      controlPoints[1].x,
      x2
    };
    
    double y_weights[] = 
    {
      y1,
      controlPoints[0].y,
      controlPoints[1].y,
      y2
    };
    
    Point point = 
    {
      cubicBezier(STEP * i, x_weights),
      cubicBezier(STEP * i, y_weights)
    };
    
    besenhamMove(point);
  }
}

double cubicBezier(double t, double weights[3])
{
  double t2 = t * t;
  double t3 = t2 * t;
  double mt = 1 - t;
  double mt2 = mt * mt;
  double mt3 = mt2 * mt;
  
  return 1 * weights[0] * mt3 +
         3 * weights[1] * mt2 * t +
         3 * weights[2] * mt * t2 +
         1 * weights[3] * t3;
}

double quarticBezier(double t, double weights[4])
{
  double t2 = t * t;
  double t3 = t2 * t;
  double t4 = t3 * t;
  double mt = 1 - t;
  double mt2 = mt * mt;
  double mt3 = mt2 * mt;
  double mt4 = mt3 * mt;
  
  return 1 * weights[0] * mt4 +
         4 * weights[1] * mt3 * t +
         6 * weights[2] * mt2 * t2 +
         4 * weights[3] * mt * t3 +
         1 * weights[4] * t4;
}

void besenhamMove(Point destination)
{
  calibrateScreen();
  calibrateMouse();
  
  while (!pointsEqual(MOUSE_POSITION, destination))
  {
    int x1 = MOUSE_POSITION.x;
    int y1 = MOUSE_POSITION.y;
    int x2 = constrain(destination.x, 0, SCREEN_DIMENSIONS.x - 1);
    int y2 = constrain(destination.y, 0, SCREEN_DIMENSIONS.y - 1);
    
    /*
     * If the slope is steep, invert the x and y values so
     * that we can iterate over the y-ordinate instead of the
     * x-ordinate.
     */
    bool steep = abs(y2 - y1) / abs(x2 - x1);
    
    if (steep)
    {
      swap(x1, y1);
      swap(x2, y2);
    }
    
    /*
     * Depending on the quadrant, we must change the direction
     * in which the mouse moves.
     */
    int x_step = (x1 < x2) ? 1 : -1;
    int y_step = (y1 < y2) ? 1 : -1;
    
    int dx = abs(x2 - x1);
    int dy = abs(y2 - y1);
    
    double slope = (double) dy / (double) dx;
    double error = 0;
    
    for (int i = 0; i < dx; i++)
    {
      if (!steep)
        Mouse.move(x_step, 0);
      else
        Mouse.move(0, x_step);
      
      error += slope;
      
      if (error >= 0.5)
      {
        if (!steep)
          Mouse.move(0, y_step);
        else
          Mouse.move(y_step, 0);
        
        error -= 1;
      }
    }
    
    calibrateMouse();
  }
}

bool pointsEqual(Point a, Point b)
{
  return (a.x == b.x && a.y == b.y) ? true : false;
}

void swap(int &a, int &b)
{
  int t = a;
  a = b;
  b = t;
}

// Keyboard

void parseKeyboardCommand()
{
  while (!Serial.available());
  uint8_t command = Serial.read();
  
  switch(command)
  {
    case KEYBOARD_PRESS:
      Keyboard.press(readByte());
      break;
    
    case KEYBOARD_RELEASE:
      Keyboard.release(readByte());
      break;
    
    case KEYBOARD_RELEASE_ALL:
      Keyboard.releaseAll();
      break;
      
    case KEYBOARD_WRITE:
      Keyboard.write(readByte());
      break;
    
    case KEYBOARD_PRINT:
      Keyboard.print(Serial.readStringUntil('\0'));
      break;
      
    case KEYBOARD_PRINTLN:
      Keyboard.println(Serial.readStringUntil('\0'));
      break;
    
    case KEYBOARD_TYPE:
      String str = Serial.readStringUntil('\0');
      uint8_t wpm = readByte();
      bool mistakes = readByte();
      uint8_t accuracy = readByte();
      type(str, wpm, mistakes, accuracy);
      break;
  }
  
  Serial.write(COMMAND_COMPLETE);
}

uint8_t readByte()
{
  while (!Serial.available());
  return Serial.read();
}

void type(String str, uint8_t wpm, bool mistakes, uint8_t accuracy)
{
  // assuming that 5 characters = 1 word
  const int MILLISECONDS_PER_CHARACTER = 12000 / wpm;
  
  for (int i = 0; i < str.length(); i++)
  {
    Keyboard.press(str[i]);
    
    delay(
      constrain(
        random(MILLISECONDS_PER_CHARACTER * 0.1, 
               MILLISECONDS_PER_CHARACTER * 0.2),
        5,  // do not hold key for less than 5 ms
        50  // and no more than 50 ms
      )
    );
    
    Keyboard.release(str[i]);
    
    delay(random(MILLISECONDS_PER_CHARACTER * 0.2,
                 MILLISECONDS_PER_CHARACTER * 1.4));
    
    if (mistakes && random(0, 100) > accuracy)
    {
      int num_mistakes = random(1, 5);
      
      // make mistakes
      for (int j = 0; j < num_mistakes; j++)
      {
        int key_index = constrain(random(i - 2, i + 2), 
                                  0, str.length() - 1);
                             
        Keyboard.press(str[key_index]);
        
        delay(
          constrain(
            random(MILLISECONDS_PER_CHARACTER * 0.2, 
                   MILLISECONDS_PER_CHARACTER * 0.4),
            5,  // do not hold key for less than 5 ms
            50  // and no more than 50 ms
          )
        );
        
        Keyboard.release(str[key_index]);
        
        delay(random(MILLISECONDS_PER_CHARACTER * 0.2,
                     MILLISECONDS_PER_CHARACTER * 1.4));
      }
      
      // realize mistake and reach for the backspace key
      delay(random(500, 1000));
      
      // fix mistakes
      for (int j = 0; j < num_mistakes; j++)
      {
        Keyboard.press(KEY_BACKSPACE);
        delay(random(20, 50));
        Keyboard.release(KEY_BACKSPACE);
        delay(random(100, 200));
      }
    }
  }
}
