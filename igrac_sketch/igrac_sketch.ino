#include <digitalWriteFast.h>
#include <SoftwareSerial.h>
#include <Servo.h>

#define RIGHT_SW 3
#define LEFT_SW 2
#define DIR_HIT 5
#define DIR_MOV 6
#define EN_HIT 8
#define EN_MOV 9
#define SERVO 10
#define STEP_HIT 11
#define STEP_MOV 12
#define DELAY 500  // micros

SoftwareSerial ss(13, 12);
Servo s;
int currStrength = 1, currAngle = 90;

void move() {
  digitalWriteFast(EN_MOV, LOW);
  for (int i = 0; i < 500; i++) {
    if (digitalReadFast(LEFT_SW) || digitalReadFast(RIGHT_SW)) {
      digitalWriteFast(DIR_MOV, !digitalReadFast(DIR_MOV));
      for (int j = 0; j < 300; j++) {
        digitalWriteFast(STEP_MOV, HIGH);
        delayMicroseconds(DELAY);
        digitalWriteFast(STEP_MOV, LOW);
        delayMicroseconds(DELAY);
      }
      digitalWriteFast(EN_MOV, HIGH);
      break;
    }
    digitalWriteFast(STEP_MOV, HIGH);
    delayMicroseconds(DELAY);
    digitalWriteFast(STEP_MOV, LOW);
    delayMicroseconds(DELAY);
  }
  digitalWriteFast(EN_MOV, HIGH);
}

void hit(int strength) {
  digitalWriteFast(EN_HIT, LOW);
  digitalWriteFast(DIR_HIT, HIGH);
  for (int i = 0; i < 300; i++) {
    digitalWriteFast(STEP_HIT, HIGH);
    delayMicroseconds(strength * 170);
    digitalWriteFast(STEP_HIT, LOW);
    delayMicroseconds(strength * 170);
  }
  digitalWriteFast(DIR_HIT, LOW);
  for (int i = 0; i < 300; i++) {
    digitalWriteFast(STEP_HIT, HIGH);
    delayMicroseconds(strength * 170);
    digitalWriteFast(STEP_HIT, LOW);
    delayMicroseconds(strength * 170);
  }
  digitalWriteFast(EN_HIT, HIGH);
}

void changeAngle(bool angle) {
  if (angle) {
    currAngle -= 5;
  } else {
    currAngle += 5;
  }

  if (currAngle < 0) {
    currAngle = 0;
  } else if (currAngle > 180) {
    currAngle = 180;
  }

  s.write(currAngle);
}

void updateStrength(int newVal) {
  currStrength = newVal;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  ss.begin(115200);

  pinMode(RIGHT_SW, INPUT_PULLUP);
  pinMode(LEFT_SW, INPUT_PULLUP);
  pinMode(DIR_HIT, OUTPUT);
  pinMode(DIR_MOV, OUTPUT);
  pinMode(SERVO, OUTPUT);
  pinMode(STEP_MOV, OUTPUT);
  pinMode(STEP_HIT, OUTPUT);
  pinMode(EN_HIT, OUTPUT);
  pinMode(EN_MOV, OUTPUT);
  // attachInterrupt(digitalPinToInterrupt(RIGHT_SW), handleEdge, RISING);
  // attachInterrupt(digitalPinToInterrupt(LEFT_SW), handleEdge, RISING);

  digitalWrite(EN_HIT, HIGH);
  digitalWrite(EN_MOV, HIGH);

  s.attach(SERVO);
  s.write(0);
}

void loop() {
  // put your main code here, to run repeatedly:
  while (ss.available()) {
    char cmd = (char)ss.read();
    Serial.println(cmd);
    switch (cmd) {
      case 'l':
        // move to the left
        digitalWriteFast(DIR_MOV, HIGH);
        Serial.println("move to the right");
        move();
        break;
      case 'r':
        // move to the right
        digitalWriteFast(DIR_MOV, LOW);
        Serial.println("move to the left");
        move();
        break;
      case 'q':
        // sweep to the left
        Serial.println("sweeping to the left");
        changeAngle(false);
        break;
      case 'e':
        // sweep to the right
        Serial.println("sweeping to the right");
        changeAngle(true);
        break;
      case 's':
        // shoot
        Serial.println("shot ball");
        hit(currStrength);
      case '1':
        Serial.println("set strength to 1");
        updateStrength(1);
        break;
      case '2':
        Serial.println("set strength to 2");
        updateStrength(2);
        break;
      case '3':
        Serial.println("set strength to 3");
        updateStrength(3);
        break;
      case '4':
        Serial.println("set strength to 4");
        updateStrength(4);
        break;
    }
  }
}