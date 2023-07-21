#include <digitalWriteFast.h>
#include <Servo.h>

#define SPR 800
#define direkcija 5
#define steper 2
#define EN 8
#define servi 9
int ppoz;
const unsigned int DELAY = 500;  // in micros
Servo s;

void make_step() {
  digitalWrite(steper, HIGH);
  delayMicroseconds(DELAY);
  digitalWrite(steper, LOW);
  delayMicroseconds(DELAY);
}

void set_dir(int dir) {
  switch (dir) {
    case 0:
      digitalWriteFast(direkcija, HIGH);
      break;
    case 1:
      digitalWriteFast(direkcija, LOW);
      break;
  }
}

String recvWithStartEndMarkers() {
  String str = "";
  if (Serial.available() > 0) {
    str = Serial.readStringUntil('>');
    str = str.substring(1);

    return str;
  }
}

void setup() {
  Serial.begin(115200);

  pinModeFast(LED_BUILTIN, OUTPUT);
  pinModeFast(direkcija, OUTPUT);
  pinModeFast(steper, OUTPUT);
  pinModeFast(EN, OUTPUT);
  pinModeFast(servi, OUTPUT);
  digitalWriteFast(EN, LOW);
  digitalWriteFast(LED_BUILTIN, LOW);

  s.attach(servi);

  digitalWriteFast(direkcija, HIGH);
  for (int i = 0; i < 2100; i++) {
    make_step();
  }

  Serial.println("<READY>");
}

void loop() {
  
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    int i = 0;
    String spoz = "";
    while (input[i] != ' ') {
      spoz = spoz + input[i];
      i = i + 1;
    }
    int poz = spoz.toInt();
    int pomeraj = 0;
    char udara = input[i];
    if (udara == '1') {
      s.write(53);
      delay(125);
      s.write(0);
    }

    //dok ne ubacimo mikrostepere otprilike
    int kalibracija = 3700;

    if (poz > 200 && poz < 400) {
      if (poz < ppoz) {
        digitalWriteFast(direkcija, LOW);
        pomeraj = (poz - ppoz) * 200 / kalibracija;
        for (int j = 0; j < pomeraj; j++) {
          make_step();
        }
      }
      if (ppoz > poz) {
        digitalWriteFast(direkcija, HIGH);
        pomeraj = (ppoz - poz) * 200 / kalibracija;
        for (int j = 0; j < pomeraj; j++) {
          make_step();
        }
      }
      ppoz = poz;
    }

    Serial.println(input);
    Serial.println("kk");
  }
}
