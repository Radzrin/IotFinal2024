from paho.mqtt import client as mqtt_client
import random

class PhotoResistor :
    broker = '10.0.0.148'
    port = 1884
    topic = "IoTlab/ESP"
    topic2 = "/esp8266/data"
    client_id = f'subscribe-{random.randint(0, 100)}'
    lightValue = 0
    rfidValue = ""

    def init(self) :
        print(f'PhotoResistor Initialized')

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client


    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):      
            if(msg.topic is "IoTlab/ESP"):
                self.lightValue = msg.payload.decode()
            else:
                self.rfidValue = msg.payload.decode()
                print(self.rfidValue)

        client.subscribe(self.topic)
        client.subscribe(self.topic2)
        client.on_message = on_message

    def run(self):
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_forever()