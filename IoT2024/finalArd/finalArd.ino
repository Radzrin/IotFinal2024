#include <SPI.h>
#include <MFRC522.h>
#include <PubSubClient.h>
#include <ESP8266WiFi.h>
MFRC522 rfid(15, 16); // Instance of the class
MFRC522::MIFARE_Key key;
// Init array that will store new NUID
byte nuidPICC[4];


const char* ssid = "grigor";
const char* password = "julieta11";
const char* mqtt_server = "192.168.0.142";

int value; 
const int pResistor = A0;

WiFiClient espClient;
PubSubClient client(espClient);

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
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("ESP8266Client")) {
      Serial.println("connected");

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(15000);
    }
  }
}
void setup() {
Serial.begin(115200);
setup_wifi();
client.setServer(mqtt_server, 1883);
client.setCallback(callback);
SPI.begin(); // Init SPI bus
rfid.PCD_Init(); // Init MFRC522
Serial.println();
Serial.print(F("Reader :"));
rfid.PCD_DumpVersionToSerial();
pinMode(pResistor, INPUT);
for (byte i = 0; i < 6; i++) {
 key.keyByte[i] = 0xFF;
}

Serial.println();
Serial.println(F("This code scan the MIFARE Classic NUID."));
Serial.print(F("Using the following key:"));
printHex(key.keyByte, MFRC522::MF_KEY_SIZE);
}
void loop() {
// Reset the loop if no new card present on the sensor/reader. This saves the entire process when

if ( ! rfid.PICC_IsNewCardPresent())
 return;
// Verify if the NUID has been readed
if ( ! rfid.PICC_ReadCardSerial())
 return;
Serial.print(F("PICC type: "));
MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
Serial.println(rfid.PICC_GetTypeName(piccType));
// Check is the PICC of Classic MIFARE type
if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
 piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
 piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
 Serial.println(F("Your tag is not of type MIFARE Classic."));
 return;
}

 Serial.println(F("A new card has been detected."));
 // Store NUID into nuidPICC array
 for (byte i = 0; i < 4; i++) {
 nuidPICC[i] = rfid.uid.uidByte[i];
 }
 Serial.println(F("The NUID tag is:"));
 Serial.print(F("In hex: "));
 String hex = printHex(rfid.uid.uidByte, rfid.uid.size);
 Serial.print(hex);
 Serial.println();
 Serial.print(F("In dec: "));
 printDec(rfid.uid.uidByte, rfid.uid.size);
/// Serial.print("the hex" + hexo);
 static char tagnum[14];
// Halt PICC
rfid.PICC_HaltA();
// Stop encryption on PCD
rfid.PCD_StopCrypto1();
if (!client.connected()) {
    reconnect();
  }
  if (!client.loop())
    client.connect("ESP8266Client");
 Serial.println();

hex.toCharArray(tagnum, 14);

client.publish("/esp8266/data", tagnum);

  value = analogRead(pResistor);
 Serial.println("Light intensity is: ");
Serial.println (value );
String lgt =  String(value);  

 client.publish("IoTlab/ESP",lgt.c_str());
 
delay(5000);
}
/**
 Helper routine to dump a byte array as hex values to Serial.
*/
String printHex(byte *buffer, byte bufferSize) {
String tagnum;
for (byte i = 0; i < bufferSize; i++) {
String space = (buffer[i] < 0x10 ? " 0" : " ");
String hexo = String(buffer[i], HEX);
tagnum += space;
tagnum += hexo;
}
return tagnum;
}
/**
 Helper routine to dump a byte array as dec values to Serial.
*/
void printDec(byte *buffer, byte bufferSize) {
for (byte i = 0; i < bufferSize; i++) {
 Serial.print(buffer[i] < 0x10 ? " 0" : " ");
 Serial.print(buffer[i], DEC);
}
}
