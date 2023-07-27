#include <digitalWriteFast.h>
#include <SoftwareSerial.h>
#include <Servo.h>

#define SEND_POS_PIN 2
#define LOW_SWITCH 4
#define HIGH_SWITCH 3
#define SPR 800
#define DIR 5
#define STEP 6
#define EN 8
#define servi 9
#define DELAY 50  // in micros
#define CALIB_DELAY 300
Servo s;
SoftwareSerial ss(11,10);

int desPos = 0, cpos = 0, delta = 0, endpos = 0;
bool moveBall = false;
bool newData = false;
const byte numChars = 64;
char receivedChars[numChars];
unsigned long totalSteps = 0;

int countSize(char chars[]) {
  int i = 0;
  while (chars[i] != '\0')
    i++;
  return i;
}

void make_step(unsigned int delay = DELAY) {
  digitalWriteFast(STEP, HIGH);
  delayMicroseconds(delay);
  digitalWriteFast(STEP, LOW);
  delayMicroseconds(delay);
  totalSteps++;
}

int calibrate() {
  // move to the left
  digitalWrite(DIR, LOW);
  while (!digitalRead(LOW_SWITCH)) {
    // Serial.println("loop");
    make_step(CALIB_DELAY);
  }
  // move to the right
  int i;
  digitalWrite(DIR, HIGH);
  while (!digitalRead(HIGH_SWITCH)) {
    make_step(CALIB_DELAY);
    i++;
  }
  // Serial.println("A");
  // move to the left again
  digitalWrite(DIR, LOW);
  while (!digitalRead(LOW_SWITCH)) {
    // Serial.println("loop");
    make_step(CALIB_DELAY);
  }

  // Serial.println("B");
  cpos = 0;
  return i - 200;
}

void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      } else {
        receivedChars[ndx] = '\0';  // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void send_data() {
  ss.println(totalSteps);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  ss.begin(115200);

  pinMode(STEP, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(LOW_SWITCH, INPUT_PULLUP);
  pinMode(HIGH_SWITCH, INPUT_PULLUP);
  pinMode(SEND_POS_PIN, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(SEND_POS_PIN), send_data, FALLING);

  s.attach(9);
  s.write(50);

  endpos = calibrate();
  totalSteps = 0;

  Serial.println("<READY>");
}

void loop() {
  // put your main code here, to run repeatedly:
  // if (Serial.available() > 0) {
  // String str = recvWithStartEndMarkers();
  // str = Serial.readStringUntil('\n');
  // int terminatorIndex = str.indexOf('>');
  // if (terminatorIndex == -1) {
  //   return;
  // }

  // str = str.substring(1, terminatorIndex);
  newData = false;
  recvWithStartEndMarkers();

  // for (int i = 0; i < countSize(receivedChars); i++)
  //   Serial.print(receivedChars[i]);
  // Serial.println("");

  String desPosStr = "";
  for (int i = 0; i < countSize(receivedChars) - 2; i++)
    desPosStr += receivedChars[i];

  desPos = map(desPosStr.toInt(), 170, 420, 0, endpos);

  if (receivedChars[countSize(receivedChars) - 1] == '1') {
    moveBall = true;
  }
  // }

  if (desPos < 0)
    desPos = 0;

  // Serial.print("despos: ");
  // Serial.print(desPos);
  // Serial.print(", srv: ");
  // Serial.println(receivedChars[countSize(receivedChars) - 1] == '1');

  delta = desPos - cpos;

  if (delta != 0) {
    digitalWriteFast(DIR, delta > 0);

    make_step();

    if (delta > 0) {
      cpos++;
    } else if (delta < 0) {
      cpos--;
    }

    // replyToPython();

    // replyToPython();
  } else {
    if (moveBall) {
      s.write(5);
      delay(125);
      s.write(50);
      moveBall = false;
    }
  }
}