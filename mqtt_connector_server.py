import paho.mqtt.client as mqtt

BROKER = 'localhost' 
PORT = 1883  

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    print(f"Connector mqtt Topic: {topic}, Message: {payload}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connector Connected successfully")
        client.subscribe("#")
    else:
        print(f"Connection failed with code {rc}")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

client.loop_forever()
