import sys
import asyncio
from asyncua import Server, ua

topics = {
    "robot1status": "active"
}

opcuaVars = {}

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
    system1 = await objects.add_object(idx, "MyObject")
    for key, value in topics.items():
        opcuaVars[key] = await system1.add_variable(idx, key, value)
        await opcuaVars[key].set_writable()
   
    await server.start()

    try:
        handler = HandleChangeFromClient()
        subscription = await server.create_subscription(500, handler)
        
        for key, opcua_var in opcuaVars.items():
            await subscription.subscribe_data_change(opcua_var)

    finally:
        await subscription.delete()
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
