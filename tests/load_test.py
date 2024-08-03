import asyncio
import json
import random
import time

NUM_CLIENTS = 1000
HOST = '10.31.121.63'
PORT = 8001

async def send_vibration_data(client_id):
    reader, writer = await asyncio.open_connection(HOST, PORT)
    try:
        while True:
            data = {
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                "device_id": client_id,
                "vibration_data": [random.uniform(0, 1) for _ in range(3)]
            }
            message = json.dumps(data) + "\n"
            writer.write(message.encode('utf-8'))
            await writer.drain()
            response = await reader.read(100)
            print(f"Client {client_id} received: {response.decode()}")
            await asyncio.sleep(random.uniform(0.5, 2))
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    tasks = [send_vibration_data(f'device_{i}') for i in range(NUM_CLIENTS)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
