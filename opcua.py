import sys
import asyncio
from asyncua import Server, ua

topics = {
    "topic1": 1,
    "topic2": 2,
    "topic3": 3,
}

class HandleChangeFromClient:
    async def datachange_notification(self, node, val, data):
        var_name = await node.read_browse_name()
        var_name_str = var_name.Name
        print(f"OPC <- topic: {var_name_str} valu: {val}")

async def main():
    server = Server()
    await server.init()

    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
    idx = await server.register_namespace("namespace")

    objects = server.nodes.objects

    # Setup object and variables
    myobj = await objects.add_object(idx, "MyObject")
    try:
        myVars = []
        for key, value in topics.items():
            myVar = await myobj.add_variable(idx, key, value)
            await myVar.set_writable()
            myVars.append(myVar)  # Fixed `push` to `append`

        await server.start()

        handler = HandleChangeFromClient()
        subscription = await server.create_subscription(500, handler)
        for myVar in myVars:
            await subscription.subscribe_data_change(myVar)

        count = 0
        while True:
            await asyncio.sleep(3)
            # count += 1
            # await myVars[0].write_value(count)  # Corrected `myVar[0]` to `myVars[0]`
            # print(f"OPC -> topic: topic1 valu: {count}")

    finally:
        await subscription.delete()
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
