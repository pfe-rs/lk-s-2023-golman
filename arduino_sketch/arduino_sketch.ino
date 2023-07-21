#include <digitalWriteFast.h>
#include <Servo.h>

#define SPR 800
#define direkcija 5
#define steper 2
#define EN 8
#define servi 9
int ppoz;
const unsigned int DELAY = 500; // in micros
Servo s;

void make_step() 
{
  digitalWrite(steper, HIGH);
  delayMicroseconds(DELAY);
  digitalWrite(steper, LOW);
  delayMicroseconds(DELAY);
}

void set_dir(int dir) {
  switch (dir) 
  {
    case 0:
      digitalWriteFast(direkcija, HIGH);
      break;
    case 1:
      digitalWriteFast(direkcija, LOW);
      break;
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
  digitalWriteFast(direkcija,HIGH);
  for (int i=0;i<4000;i++)
  { 
         make_step();
  }
  digitalWriteFast(direkcija,LOW);
  for (int i=0;i<4000;i++)
  { 
         make_step();
  }
}

void loop() 
{

}
