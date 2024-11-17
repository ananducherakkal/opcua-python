"""
opcua server
"""
import asyncio
from asyncua import Server, ua

# Topics for OPC UA server
topics = {
    "topic1": 1,
    "topic2": 2,
    "topic3": 3,
}

class HandleChangeFromClient:
    # Handle incoming changes from clients
    async def datachange_notification(self, node, val, data):
        var_name = await node.read_browse_name()
        print(f"OPC <- topic: {var_name.Name} value: {val}")

async def main():
    # Initialize OPC UA server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
    idx = await server.register_namespace("namespace")

    # Create object and variables
    objects = server.nodes.objects
    myobj = await objects.add_object(idx, "MyObject")
    myVars = [await myobj.add_variable(idx, key, value) for key, value in topics.items()]
    
    for myVar in myVars:
        await myVar.set_writable()

    await server.start()

    handler = HandleChangeFromClient()
    subscription = await server.create_subscription(500, handler)
    
    for myVar in myVars:
        await subscription.subscribe_data_change(myVar)

    count = 0
    try:
        while True:
            await asyncio.sleep(3)
            # count += 1
            # await myVars[0].write_value(count)
            # print(f"OPC -> topic: topic1 value: {count}")

    finally:
        await subscription.delete()
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
