import asyncio
from utils.connector import Connector

async def main():
    connector = Connector()
    
    await connector.config_opcua()
    connector.config_mqtt()

    await connector.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Closing server")
