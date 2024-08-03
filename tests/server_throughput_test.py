import asyncio
import json
import time

HOST = '192.168.0.162'
PORT = 8001

async def handle_client_connection(reader, writer):
    buffer = ""
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            buffer += data.decode('utf-8')
            while True:
                json_data, buffer = extract_json_from_buffer(buffer)
                if json_data:
                    try:
                        vibration_data = json.loads(json_data)
                        timestamp = vibration_data['timestamp']
                        device_id = vibration_data['device_id']
                        vibration_values = vibration_data['vibration_data']
                        
                        # Simulate some processing
                        await asyncio.sleep(0.1)
                        
                        # Send acknowledgment
                        writer.write(b"Data received")
                        await writer.drain()
                        
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e} with data: {json_data}")
                else:
                    break
    finally:
        writer.close()
        await writer.wait_closed()

def extract_json_from_buffer(buffer):
    start_idx = buffer.find('{')
    if start_idx == -1:
        return None, buffer
    end_idx = buffer.find('}', start_idx)
    if end_idx == -1:
        return None, buffer
    return buffer[start_idx:end_idx+1], buffer[end_idx+1:]

async def start_server():
    server = await asyncio.start_server(handle_client_connection, HOST, PORT)
    print(f"Server listening on {HOST}:{PORT}")

    try:
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(start_server())
