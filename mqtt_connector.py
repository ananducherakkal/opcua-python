import asyncio
from asyncua import Client, ua
import paho.mqtt.client as mqtt

# MQTT setup
MQTT_BROKER = 'localhost'
PORT = 1883
MQTT_TOPIC = "topxx"

# OPC UA setup
OPC_UA_SERVER = "opc.tcp://localhost:4840/freeopcua/server/"
OPC_UA_NODE_ID = "ns=2;i=2"  # Replace with your OPC UA node ID

async def write_to_opcua(data):
    async with Client(OPC_UA_SERVER) as client:
        node = client.get_node(OPC_UA_NODE_ID)
        await node.write_value(ua.DataValue(ua.Variant(int(data), ua.VariantType.Int32)))
        print(f"Data written to OPC UA: {data}")

def on_mqtt_message(client, userdata, message):
    data = float(message.payload.decode())
    print(f"Received from MQTT: {data}")
    asyncio.run(write_to_opcua(data))  # Send data to OPC UA

def start_mqtt():
    mqtt_client = mqtt.Client()
    mqtt_client.connect(MQTT_BROKER, PORT, 60)
    mqtt_client.subscribe(MQTT_TOPIC)
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.loop_forever()

if __name__ == "__main__":
    start_mqtt()
