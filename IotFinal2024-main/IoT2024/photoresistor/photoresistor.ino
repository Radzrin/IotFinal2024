#include <ESP8266WiFi.h>
#include <PubSubClient.h>
//const char* ssid = "TP-Link_2AD8";
//const char* password = "14730078";
const char* ssid = "SM-A526W7455";
const char* password = "upph3648";
const char* mqtt_server = "192.168.22.210";
WiFiClient espClient;
PubSubClient client(espClient);

const int photoresistorPin = A0;
int lightValue = 0;
//int LED =13;

void setup_wifi() {
 delay(10);
 // We start by connecting to a WiFi network
 Serial.println();
 Serial.print("Connecting to ");
 Serial.println(ssid);
 WiFi.begin(ssid, password);
 while (WiFi.status() != WL_CONNECTED) {
 delay(500);
 Serial.print(".");
 }
 Serial.println("");
 Serial.print("WiFi connected - ESP-8266 IP address: ");
 Serial.println(WiFi.localIP());
}
void callback(String topic, byte* message, unsigned int length) {
 Serial.print("Message arrived on topic: ");
 Serial.print(topic);
 Serial.print(". Message: ");
 String messagein;

 for (int i = 0; i < length; i++) {
 Serial.print((char)message[i]);
 messagein += (char)message[i];
 }

}
void reconnect() {
 while (!client.connected()) {
 Serial.print("Attempting MQTT connection...");
 if (client.connect("espClient")) {
 Serial.println("connected");

 } else {
 Serial.print("failed, rc=");
 Serial.print(client.state());
 Serial.println(" try again in 3 seconds");
 // Wait 5 seconds before retrying
 delay(3000);
 }
 }
}
void setup() {

 Serial.begin(115200);
 pinMode(photoresistorPin, INPUT);
 setup_wifi();
 client.setServer(mqtt_server, 1883);
 client.setCallback(callback);
}
void loop() {
 if (!client.connected()) {
 reconnect();
 }
 if(!client.loop())
 client.connect("espClient");
 
 lightValue = analogRead(photoresistorPin);
 Serial.println(lightValue);
//
//  if (lightValue < 400) {
//    digitalWrite(LED, HIGH);
//  }else {
//    digitalWrite(LED, LOW);
//  }

 client.publish("IoTlab/ESP",String(lightValue).c_str());

 delay(3000);
 }
