import asyncio
from utils.opcua import OPCUA
from utils.mqtt import MQTT_CLIENT
from config.topics import topics

class Connector:
    def __init__(self):
        self.mqtt_to_opcua_tracker = set()
        self.opcua_to_mqtt_tracker = set()

    async def config_opcua(self):
        self.opcua = OPCUA()
        await self.opcua.init()

    def config_mqtt(self):
        self.mqtt = MQTT_CLIENT()
        self.mqtt.subscribe_all_topic()

    async def start_server(self):
        await self.opcua.set_on_message(self.opcua_on_message)
        self.mqtt.client.on_message = self.mqtt_on_message
        self.mqtt.listen()
        await self.opcua.start_server()

    def opcua_on_message(self, topic, value):
        print(f"Received on OPCUA:: {topic}, {value}")
        if (topic, value) in self.opcua_to_mqtt_tracker:
            self.opcua_to_mqtt_tracker.remove((topic, value))
        else:
            print(f"Forwarding to MQTT:: {topic}, {value}")
            self.mqtt.client.publish(topic, value)
            self.mqtt_to_opcua_tracker.add((topic, value))

    def mqtt_on_message(self, client, userdata, message):
        topic = message.topic
        raw_value = message.payload.decode("utf-8")
        topic_obj = topics.get(topic) or {}
        expected_type = topic_obj.get("type", str)
        value = expected_type(raw_value)
        print(f"Received on MQTT:: {topic}, {value}")

        if (topic, value) in self.mqtt_to_opcua_tracker:
            self.mqtt_to_opcua_tracker.remove((topic, value))
        elif topic in self.opcua.topics:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.opcua_to_mqtt_tracker.add((topic, value))

            print(f"Forwarding to OPCUA: {topic} value: {value}")
            loop.run_until_complete(self.opcua.topics[topic].write_value(value))