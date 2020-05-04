#include <SPI.h>
#include <WiFi101.h>

#include "arduino_secrets.h"

#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#include <Arduino.h>
#include "MHZ19.h"

#define DHTPIN 3
#define DHTTYPE DHT11
#define R 0
#define G 1
#define B 2

#define BAUDRATE 9600

MHZ19 myMHZ19;
DHT dht(DHTPIN, DHTTYPE); // Initialize DHT sensor

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key Index number (needed only for WEP)

int status = WL_IDLE_STATUS;

// Initialize the WiFi client library
WiFiSSLClient client;

// server address:
char server[] = "school-project-2-269904.appspot.com";
//IPAddress server(64,131,82,241);

unsigned long lastConnectionTime = 0;            // last time you connected to the server, in milliseconds
const unsigned long postingInterval = 300L * 1000L; // delay between updates, in milliseconds

void setup() {
  pinMode(R, OUTPUT);
  pinMode(G, OUTPUT);
  pinMode(B, OUTPUT);

  set_led(0);

  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  /*
    while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
    }*/

  Serial.println("DHT11 test!");
  dht.begin();

  Serial1.begin(BAUDRATE);
  myMHZ19.begin(Serial1);
  myMHZ19.autoCalibration();

  init_wifi();

  set_led(1);
}

void loop() {
  // if there's incoming data from the net connection.
  // send it out the serial port.  This is for debugging
  // purposes only:
  while (client.available()) {
    char c = client.read();
    Serial.write(c);
  }

  // if ten seconds have passed since your last connection,
  // then connect again and send data:
  if (millis() - lastConnectionTime > postingInterval) {
    httpsRequest(gen_post_str());
  }

}

String gen_post_str() {

  String post_str = "source=MKR1000";

  post_str += "&brightness=" + String(analogRead(A1));

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    post_str += "&t=" + String(t, 1);
    post_str += "&h=" + String(h, 1);
  }

  int CO2 = myMHZ19.getCO2();

  post_str += "&co2=" + String(CO2) ;

  return post_str;

}

// this method makes a HTTP connection to the server:
void httpsRequest(String post_str) {
  // close any connection before send a new request.
  // This will free the socket on the WiFi shield
  client.stop();

  // if there's a successful connection:
  if (client.connect(server, 443)) {

    Serial.println("connecting...");
    // send the HTTP PUT request:
    client.println("POST /arduino_entry HTTP/1.1");
    client.println("Host: school-project-2-269904.appspot.com");
    client.println("Content-Length: " + String(post_str.length()));
    client.println("Content-Type: application/x-www-form-urlencoded");
    client.println();
    client.println(post_str);
    Serial.println("\n" + post_str);

    // note the time that the connection was made:
    lastConnectionTime = millis();
  }
  else {
    // if you couldn't make a connection:
    Serial.println("connection failed");
  }
}

void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void init_wifi() {
  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  // attempt to connect to WiFi network:
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);
    if (status == WL_CONNECTED)break;
    delay(1000);

  }
  // you're connected now, so print out the status:
  printWiFiStatus();
}

void set_led(int stat) {
  switch (stat) {
    case 0:
      //starting
      digitalWrite(R, 1);
      digitalWrite(G, 0);
      digitalWrite(B, 0);
      break;
    case 1:
      //working
      digitalWrite(R, 0);
      digitalWrite(G, 1);
      digitalWrite(B, 0);
      break;
    case 2:
      //something get wrong
      break;
  }
}
