import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = [
    "topic1",
    "topic2",
    "topic3"
]
count = 1

def on_message(client, userdata, message):
    print(f"MQTT <- topic: {message.topic}, value: {message.payload.decode()}")

client = mqtt.Client()

client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

for item in MQTT_TOPIC:
    print("Subscribing to :", item)
    client.subscribe(item)

client.loop_start()

try:
    while True:
        count += 1
        client.publish("topic1", count)
        print(f"MQTT -> topic: topic1, value: {count}")
        time.sleep(4)
except KeyboardInterrupt:
    print("Disconnecting from broker")
finally:
    client.loop_stop()
    client.disconnect()
