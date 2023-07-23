#include <digitalWriteFast.h>
#include <Servo.h>

#define SPR 800
#define DIR 5
#define STEP 2
#define EN 8
#define servi 9
#define DELAY 100  // in micros
Servo s;

int desPos = 0, cpos = 0, delta = 0;
bool moveBall = false;

void setup() {
  // put your setup code here, to run once:
  pinMode(STEP, OUTPUT);
  pinMode(DIR, OUTPUT);

  s.attach(9);
  s.write(50);

  Serial.begin(115200);
  Serial.println("<READY>");
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    String str;
    str = Serial.readStringUntil('\n');
    int terminatorIndex = str.indexOf('>');
    if (terminatorIndex == -1) {
      return;
    }

    str = str.substring(1, terminatorIndex);

    String desPosStr = "";
    for (int i = 0; i < str.length() - 2; i++)
      desPosStr += str[i];

    desPos = map(desPosStr.toInt(), 200, 400, 2400, 6000);

    if (str[str.length() - 1] == '1') {
      moveBall = true;
    }
  }

  delta = desPos - cpos;

  if (delta != 0) {
    digitalWriteFast(DIR, delta > 0);

    digitalWriteFast(STEP, HIGH);
    delayMicroseconds(DELAY);
    digitalWriteFast(STEP, LOW);
    delayMicroseconds(DELAY);

    if (delta > 0) {
      cpos++;
    } else if (delta < 0) {
      cpos--;
    }
  }
  else {
    if (moveBall) {
      s.write(5);
      delay(125);
      s.write(50);
      moveBall = false;
    }
  }
}