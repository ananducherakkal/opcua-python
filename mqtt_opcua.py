import asyncio
import paho.mqtt.client as mqtt
from asyncua import Client

BROKER = 'localhost'
PORT = 1883

OPC_URL = "opc.tcp://localhost:4840/freeopcua/server/"

myvar = None

class SubHandler:
    async def datachange_notification(self, node, val, data):
        var_name = await node.read_browse_name()
        print("Sending data to mqtt", var_name.Name, val)
        mqtt_client.publish(var_name.Name, str(val))

    def event_notification(self, event):
        print("New event", event)

async def setup_opcua_client():
    global myvar
    async with Client(url=OPC_URL) as client:
        print("Connected to OPC UA server")

        uri = "namespace"
        idx = await client.get_namespace_index(uri)
        print("index of our namespace is %s", idx)

        myvar = await client.nodes.root.get_child("/Objects/2:MyObject/2:MyVariable")
        print("myvar is: %r", myvar)

        handler = SubHandler()
        sub = await client.create_subscription(10, handler)
        handle = await sub.subscribe_data_change(myvar)
        await asyncio.sleep(0.1)

        await sub.subscribe_events()

        while True:
            await asyncio.sleep(1)

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    print(f"Received message from mqtt server::: {topic}: {payload}")

    if topic.startswith("opc"):
        if myvar:
            print(f"Sending to OPCUA: {payload}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(myvar.write_value(int(payload)))

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
