import asyncio
from asyncua import Server, ua
from config.topics import topics

class HandleChangeFromClient:
    def __init__(self, on_message):
        self.on_message = on_message

    async def datachange_notification(self, node, val, data):
        var_name = await node.read_browse_name()
        self.on_message(var_name.Name, val)

class OPCUA:
    def __init__(self):
        self.url = "opc.tcp://localhost:4840/freeopcua/server/"
        self.namespace = "namespace"
        self.object_name = "SysInte"

        self.server = Server()

    async def init(self):
        await self.server.init()
        self.server.set_endpoint(self.url)
        self.index = await self.server.register_namespace(self.namespace)

        objects = self.server.nodes.objects
        self.object = await objects.add_object(self.index, self.object_name)
        self.topics = {}
        for topic, details in topics.items():
            self.topics[topic] = await self.object.add_variable(self.index, topic, details["default_value"])

        for topic in self.topics.values():
            await topic.set_writable()

        await self.server.start()

    async def set_on_message(self, on_message):
        handler = HandleChangeFromClient(on_message)
        self.subscription = await self.server.create_subscription(500, handler)

        for topic in self.topics.values():
            await self.subscription.subscribe_data_change(topic)

    async def start_server(self):
        try:
            print("OPC UA server started")
            self.stop_event = asyncio.Event()
            await self.stop_event.wait()
        except KeyboardInterrupt:
            print("Stopping server due to KeyboardInterrupt")
        finally:
            print("Cleaning up server resources")
            if hasattr(self, 'subscription'):
                await self.subscription.delete()
            await self.server.stop()
            print("Server stopped")