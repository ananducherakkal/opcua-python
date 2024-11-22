import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from config.topics import topics

class MQTT_CLIENT:
    def __init__(self):
        # Load env vars from .env
        load_dotenv()

        username = os.getenv('MQTT_USERNAME')
        password = os.getenv('MQTT_PASSWORD')
        broker = os.getenv('MQTT_BROKER')
        port = int(os.getenv('MQTT_PORT'))

        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.connect(broker, port, 60)
        self.client.on_message = self.on_message
    
    def subscribe_all_topic (self):
        for topic in topics:
            self.client.subscribe(topic)

    def on_message(self, client, userdata, message):
        print(f"MQTT <- topic: {message.topic}, value: {message.payload.decode()}")

    def listen(self):
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
