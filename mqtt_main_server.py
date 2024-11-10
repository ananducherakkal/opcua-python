import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "Main/topic"

def on_message(client, userdata, message):
    print(f"Received message On main server: '{message.payload.decode()}' on topic '{message.topic}'")

client = mqtt.Client()

client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.subscribe(MQTT_TOPIC)

client.loop_start()

try:
    count = 1
    while True:
        message = f"Hello {count}"
        client.publish(MQTT_TOPIC, message)
        print(f"Published message: '{message}'")
        count += 1
        time.sleep(2)
except KeyboardInterrupt:
    print("Disconnecting from broker")
finally:
    client.loop_stop()
    client.disconnect()
