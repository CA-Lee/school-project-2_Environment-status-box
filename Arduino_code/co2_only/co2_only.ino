#include <Arduino.h>   // required before wiring_private.h
#include "wiring_private.h" // pinPeripheral() function
 
Uart Serial2 (&sercom1, 11, 10, SERCOM_RX_PAD_0, UART_TX_PAD_2);
void SERCOM1_Handler()
{
  Serial2.IrqHandler();
}
#include <SoftwareSerial.h>

#define CO2_TX 3
#define CO2_RX 2

SoftwareSerial SerialCO2(CO2_RX, CO2_TX); // RX, TX

const uint8_t cmd[9] = {0xFF,0x01,0x86,0x00,0x00,0x00,0x00,0x00,0x79};
int getCO2() {
  
  uint8_t response[9];
  for (int i=0; i<9; i++) {
    SerialCO2.write(cmd[i]);
  }

  if (SerialCO2.available()) {
    for(int i=0; i < 9; i++) {
      response[i] = SerialCO2.read();
    }
  }
  
  int responseHigh = (int) response[2];
  int responseLow = (int) response[3];
  int ppm = (responseHigh << 8) + responseLow;

  return ppm;
}

void setup() {
  pinPeripheral(10, PIO_SERCOM);
  pinPeripheral(11, PIO_SERCOM);
  Serial.begin(9600);
  SerialCO2.begin(9600);
  Serial.println("Initialized.");
}

void loop() {
  Serial.println(getCO2());
  delay(200);
}