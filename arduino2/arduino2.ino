#include <digitalWriteFast.h>
#include <SoftwareSerial.h>
#include <ShiftRegister74HC595.h>
#include <Servo.h>

// #define SEND_POS_PIN 2
#define LOW_SWITCH 4
#define HIGH_SWITCH 3
#define SPR 800
#define DIR 5
#define STEP 6
#define EN 8
#define servi 9
#define DELAY 80  // in micros
#define CALIB_DELAY 300
Servo s;
ShiftRegister74HC595<1> sr(12, 10, 11);

int desPos = 0, cpos = 0, delta = 0, endpos = 0;
bool moveBall = false;
bool newData = false;
const byte numChars = 64;
char receivedChars[numChars];
unsigned long totalSteps = 0;

void setDisplay(int numberToSet) {
  uint8_t broj;
  switch (numberToSet) {
    case 10:
      broj = 0b11111111;
      break;
    case 0:
      broj = 0b11000000;
      break;
    case 1:
      broj = 0b11111001;
      break;
    case 2:
      broj = 0b10100100;
      break;
    case 3:
      broj = 0b10110000;
      break;
    case 4:
      broj = 0b10011001;
      break;
    case 5:
      broj = 0b10010010;
      break;
    case 6:
      broj = 0b10000010;
      break;
    case 7:
      broj = 0b11111000;
      break;
    case 8:
      broj = 0b10000000;
      break;
    case 9:
      broj = 0b10010000;
      break;
    default:
      broj = 0b0000000;
  }
  sr.setAll(&broj);
}

int countSize(char chars[]) {
  int i = 0;
  while (chars[i] != '\0')
    i++;
  return i;
}

void make_step(unsigned int delay = DELAY) {
  // digitalWriteFast(EN, LOW);

  digitalWriteFast(STEP, HIGH);
  delayMicroseconds(delay);
  digitalWriteFast(STEP, LOW);
  delayMicroseconds(delay);
  totalSteps++;

  // digitalWriteFast(EN, HIGH);
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

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(STEP, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(EN, OUTPUT);
  pinMode(LOW_SWITCH, INPUT_PULLUP);
  pinMode(HIGH_SWITCH, INPUT_PULLUP);

  digitalWriteFast(EN, LOW);

  s.attach(9);
  s.write(50);

  setDisplay(10);

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
  for (int i = 0; i < countSize(receivedChars) - 4; i++)
    desPosStr += receivedChars[i];

  desPos = map(desPosStr.toInt(), 127, 463, 0, endpos);

  if (receivedChars[countSize(receivedChars) - 1] == '1') {
    moveBall = true;
  }

  // String hack = "";
  // hack += receivedChars[countSize(receivedChars) - 3];
  // setDisplay(hack.toInt());
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