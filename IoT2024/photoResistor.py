from paho.mqtt import client as mqtt_client
import random

class PhotoResistor :
    broker = '192.168.0.167'
    port = 1883
    topic = "IoTlab/ESP"
    client_id = f'subscribe-{random.randint(0, 100)}'
    lightValue = 0

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
            self.lightValue = msg.payload.decode()

        client.subscribe(self.topic)
        client.on_message = on_message

    def run(self):
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_forever()