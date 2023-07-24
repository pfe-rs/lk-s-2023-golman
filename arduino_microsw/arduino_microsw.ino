#include <digitalWriteFast.h>

#define LOW_SWITCH 4
#define HIGH_SWITCH 3
#define DIR 5
#define STEP 2
#define DELAY 100  // in micros

int calibrate() {
  // Serial.println("f1");
  while(!digitalRead(LOW_SWITCH)) {
    // Serial.println("loop");
    digitalWrite(DIR, LOW);
    digitalWriteFast(STEP, HIGH);
    delayMicroseconds(DELAY);
    digitalWriteFast(STEP, LOW);
    delayMicroseconds(DELAY);
  }
  // Serial.println("f2");
  int i;
  while(!digitalRead(HIGH_SWITCH)) {
    digitalWrite(DIR, HIGH);
    digitalWriteFast(STEP, HIGH);
    delayMicroseconds(DELAY);
    digitalWriteFast(STEP, LOW);
    delayMicroseconds(DELAY);
    i++;
  }
  // Serial.println("f3");
  for (int i = 0; i < 200; i++) {
    digitalWrite(DIR, LOW);
    digitalWriteFast(STEP, HIGH);
    delayMicroseconds(DELAY);
    digitalWriteFast(STEP, LOW);
    delayMicroseconds(DELAY);
  }
  return i - 200;
}

void setup() {
  // put your setup code here, to run once:
  pinMode(LOW_SWITCH, INPUT_PULLUP);
  pinMode(HIGH_SWITCH, INPUT_PULLUP);
  pinMode(STEP, OUTPUT);
  pinMode(DIR, OUTPUT);
  Serial.begin(115200);
  
  digitalWrite(DIR, LOW);

  int end = calibrate();

  Serial.println(end);

  // for (int i = 0; i < end; i++)
  // {
  //   digitalWriteFast(STEP, HIGH);
  //   delayMicroseconds(DELAY);
  //   digitalWriteFast(STEP, LOW);
  //   delayMicroseconds(DELAY);
  // }
}

void loop() {
  // put your main code here, to run repeatedly:
  // Serial.print("lowsw: ");
  // Serial.print(digitalRead(LOW_SWITCH));
  // Serial.print(", highsw: ");
  // Serial.println(digitalRead(HIGH_SWITCH));
}
