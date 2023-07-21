#define numChars 64

#include <Servo.h>

char receivedChars[numChars];
Servo s;

boolean newData = false;

void setup() {
  Serial.begin(115200);
  Serial.println("<READY>");
  s.attach(9);
}

void loop() {
  recvWithStartEndMarkers();
}

void recvWithStartEndMarkers() {
  String str = "";
  if (Serial.available() > 0) {
    str = Serial.readStringUntil('>');
    str = str.substring(1);

    Serial.println(str);
    int degs = str.toInt();
    s.write(degs);
  }
}