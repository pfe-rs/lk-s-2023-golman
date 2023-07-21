#define numChars 64

#include <Servo.h>

char receivedChars[numChars];
Servo s;

boolean newData = false;

void setup() {
  Serial.begin(115200);
  Serial.println("<READY>");
  s.attach(9)
}

void loop() {
  recvWithStartEndMarkers();
  // replyToPython();
}

void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;

  const char startMarker = '<';
  const char endMarker = '>';

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

// void replyToPython() {
//     if (newData == true) {
//         Serial.print("<This just in ... ");
//         Serial.print(receivedChars);
//         Serial.print("   ");
//         Serial.print(millis());
//         Serial.print('>');
//             // change the state of the LED everytime a reply is sent
//         digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
//         newData = false;
//     }
// }