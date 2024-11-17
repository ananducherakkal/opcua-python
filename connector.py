"""
For connecting
mqtt -> opcua
opcua -> mqtt
"""
import asyncio
import paho.mqtt.client as mqtt
from asyncua import Client

# Configuration for MQTT and OPC UA
BROKER = 'localhost'
PORT = 1883
OPC_URL = "opc.tcp://localhost:4840/freeopcua/server/"
myvar = {}
topics = {
    "topic1": 1,
    "topic2": 2,
    "topic3": 3,
}

# Tracking sets for recently sent updates
mqtt_to_opcua_tracker = set()
opcua_to_mqtt_tracker = set()

class SubHandler:
    # Handle updates from OPC UA server to MQTT
    async def datachange_notification(self, node, val, data):
        var_name = await node.read_browse_name()
        var_name_str = var_name.Name
        print(f"OPC <- topic: {var_name_str} value: {val}")

        # Avoid duplicate update cycles
        if (var_name_str, val) in opcua_to_mqtt_tracker:
            opcua_to_mqtt_tracker.remove((var_name_str, val))
        else:
            print(f"MQTT -> topic: {var_name_str} value: {val}")
            mqtt_client.publish(var_name_str, int(val))
            mqtt_to_opcua_tracker.add((var_name_str, val))

    def event_notification(self, event):
        pass

# Set up OPC UA client and subscribe to topics
async def setup_opcua_client():
    global myvar
    async with Client(url=OPC_URL) as client:
        uri = "namespace"
        idx = await client.get_namespace_index(uri)
        
        # Retrieve OPC UA nodes for topics
        for key in topics:
            myvar[key] = await client.nodes.root.get_child(f"/Objects/2:MyObject/2:{key}")

        handler = SubHandler()
        sub = await client.create_subscription(10, handler)
        
        for key, value in myvar.items():
            await sub.subscribe_data_change(value)
            await asyncio.sleep(0.1)

        await sub.subscribe_events()

        while True:
            await asyncio.sleep(1)

# Handle incoming MQTT messages
def on_message(client, userdata, message):
    topicx = message.topic
    payload = int(message.payload.decode("utf-8"))
    print(f"MQTT <- topic: {topicx} value: {payload}")

    # Avoid duplicate update cycles
    if (topicx, payload) in mqtt_to_opcua_tracker:
        mqtt_to_opcua_tracker.remove((topicx, payload))
        return

    if myvar.get(topicx):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        opcua_to_mqtt_tracker.add((topicx, payload))
        print(f"OPC -> topic: {topicx} value: {payload}")
        loop.run_until_complete(myvar[topicx].write_value(payload))

# Connect to MQTT broker and subscribe to topics
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected successfully")
        client.subscribe("#")  # Subscribe to all topics
    else:
        print(f"Connection failed with code {rc}")

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(BROKER, PORT, 60)

# Run OPC UA client and MQTT loop concurrently
def run_all():
    loop = asyncio.get_event_loop()
    loop.create_task(setup_opcua_client())
    mqtt_client.loop_start()
    loop.run_forever()

if __name__ == "__main__":
    run_all()
