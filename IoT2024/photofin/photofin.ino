#include <ESP8266WiFi.h>
#include <PubSubClient.h>
const char* ssid = "SM-A526W7455";
const char* password = "upph3648";
const char* mqtt_server = "192.168.22.210";
int value; 
const int pResistor = A0;

WiFiClient vanieriot;
PubSubClient client(vanieriot);
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
 if (client.connect("vanieriot")) {
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
 setup_wifi();
 client.setServer(mqtt_server, 1884);
 client.setCallback(callback);
 pinMode(pResistor, INPUT);
}
void loop() {
 if (!client.connected()) {
 reconnect();
 }
 if(!client.loop())
 client.connect("vanieriot");

  value = analogRead(pResistor);
 Serial.println("Light intensity is: ");
Serial.println (value );
String lgt =  String(value);  

 client.publish("IoTlab/ESP",lgt.c_str());

 delay(500);
 }

