import sys
import asyncio
from asyncua import Server, ua

class HandleChangeFromClient:
    async def datachange_notification(self, node, val, data):
        print(f"Value change from client: {val}")

async def main():
    server = Server()
    await server.init()

    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
    idx = await server.register_namespace("namespace")

    objects = server.nodes.objects

    # Setup object and variable
    myobj = await objects.add_object(idx, "MyObject")
    myVar = await myobj.add_variable(idx, "MyVariable", 1)
    await myVar.set_writable()

    await server.start()

    try:
        handler = HandleChangeFromClient()
        subscription = await server.create_subscription(500, handler)
        await subscription.subscribe_data_change(myVar)

        count = 0
        while True:
            await asyncio.sleep(5)
            count += 1
            await myVar.write_value(count)
            print("Message send to client: ", count)

    finally:
        await subscription.delete()
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
