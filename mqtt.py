"""
mqtt server
"""
import paho.mqtt.client as mqtt
import time

# MQTT broker configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = ["topic1", "topic2", "topic3"]

count = 1

# Callback for received messages
def on_message(client, userdata, message):
    print(f"MQTT <- topic: {message.topic}, value: {message.payload.decode()}")

# Set up MQTT client and connect
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Subscribe to specified topics
for topic in MQTT_TOPICS:
    print(f"Subscribing to: {topic}")
    client.subscribe(topic)

client.loop_start()

# Publish messages to MQTT broker periodically
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
