import asyncio
from asyncua import Client

class SubHandler:
    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)

    def event_notification(self, event):
        print("New event", event)

async def main():
    url = "opc.tcp://localhost:4840/freeopcua/server/"
    async with Client(url=url) as client:
        print("Root node is: %r", client.nodes.root)
        print("Objects node is: %r", client.nodes.objects)
        print("Children of root are: %r", await client.nodes.root.get_children())

        uri = "namespace"
        idx = await client.get_namespace_index(uri)
        print("index of our namespace is %s", idx)

        myvar = await client.nodes.root.get_child("/Objects/2:MyObject/2:MyVariable")
        obj = await client.nodes.root.get_child("Objects/2:MyObject")
        print("myvar is: %r", myvar)

        handler = SubHandler()
        sub = await client.create_subscription(10, handler)
        handle = await sub.subscribe_data_change(myvar)
        await asyncio.sleep(0.1)

        await sub.subscribe_events()
        while True:
            await asyncio.sleep(10)
            await myvar.write_value(100)


if __name__ == "__main__":
    asyncio.run(main())