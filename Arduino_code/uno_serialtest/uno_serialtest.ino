#include "SoftwareSerial.h"

SoftwareSerial ss(5,6);
SoftwareSerial ss2(9,10);
void setup() {
  // put your setup code here, to run once:
  ss.begin(9600);
  ss2.begin(9600);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  //while(Serial.available())S
  ss.println("hello?");
  while(ss2.available())Serial.write(ss2.read());
  ss2.println("moshimoshi");
  while(ss.available())Serial.write(ss.read());
  delay(500);
}
