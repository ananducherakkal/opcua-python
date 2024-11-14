import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "opc_something"
count = 1

def on_message(client, userdata, message):
    global count
    count = int(message.payload.decode())
    print("setting count", count)
    print(f"Received on MQTT server:: '{message.payload.decode()}' on topic '{message.topic}'")

client = mqtt.Client()

client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.subscribe(MQTT_TOPIC)

client.loop_start()

try:
    while True:
        count += 1
        client.publish(MQTT_TOPIC, count)
        print(f"Sending message from MQTTServer: '{count}'")
        time.sleep(4)
except KeyboardInterrupt:
    print("Disconnecting from broker")
finally:
    client.loop_stop()
    client.disconnect()
