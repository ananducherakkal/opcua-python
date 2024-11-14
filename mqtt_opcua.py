import asyncio
import paho.mqtt.client as mqtt
from asyncua import Client

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
    async def datachange_notification(self, node, val, data):
        var_name = await node.read_browse_name()
        var_name_str = var_name.Name
        print(f"OPC <- topic: {var_name_str} valud: {val}")

        # If the value change was triggered by us, ignore it
        if (var_name_str, val) in opcua_to_mqtt_tracker:
            opcua_to_mqtt_tracker.remove((var_name_str, val))
        else:
            print(f"MQTT -> topic: {var_name_str} valud: {val}")
            mqtt_client.publish(var_name_str, int(val))
            mqtt_to_opcua_tracker.add((var_name_str, val))

    def event_notification(self, event):
        pass

async def setup_opcua_client():
    global myvar
    async with Client(url=OPC_URL) as client:

        uri = "namespace"
        idx = await client.get_namespace_index(uri)
        for key, value in topics.items():
            myvarx = await client.nodes.root.get_child(f"/Objects/2:MyObject/2:{key}")
            myvar[key] = myvarx

        handler = SubHandler()
        sub = await client.create_subscription(10, handler)
        for key, value in myvar.items():
            handle = await sub.subscribe_data_change(value)
            await asyncio.sleep(0.1)

        await sub.subscribe_events()

        while True:
            await asyncio.sleep(1)

def on_message(client, userdata, message):
    topicx = message.topic
    payload = message.payload.decode("utf-8")

    print(f"MQTT <- topic: {topicx} valud: {payload}")

    # Check if message was sent by us, if yes, ignore
    if (topicx, int(payload)) in mqtt_to_opcua_tracker:
        mqtt_to_opcua_tracker.remove((topicx, int(payload)))
        return

    if myvar[topicx]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Track the value before sending to OPC UA
        opcua_to_mqtt_tracker.add((myvar[topicx], int(payload)))
        print(f"OPC -> topic: {topicx} valud: {payload}")
        loop.run_until_complete(myvar[topicx].write_value(int(payload)))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connected successfully")
        client.subscribe("#")  # Subscribe to all topics (can be customized)
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
    # Create the asyncio event loop
    loop = asyncio.get_event_loop()

    # Run OPC UA client setup in the event loop
    loop.create_task(setup_opcua_client())

    # Start MQTT loop in a separate thread so it doesn't block asyncio
    mqtt_client.loop_start()

    # Run the event loop
    loop.run_forever()

if __name__ == "__main__":
    run_all()
