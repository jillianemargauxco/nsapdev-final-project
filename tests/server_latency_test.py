import asyncio
import json
import csv
from asyncio import Queue
import time  # Import time for latency measurement

HOST = '192.168.0.162'
PORT = 8001

DATA_FILE = 'vibration_data.csv'
LATENCY_FILE = 'latency_data.csv'  # File to save latency data

data_queue = Queue()
client_data = {}

def visualize_data(timestamp, device_id, vibration_values):
    print(f"Timestamp: {timestamp}, Device ID: {device_id}")
    print("Vibration Data:")
    print(" | ".join(f"{value:.2f}" for value in vibration_values))
    print("-" * 40)

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
                        
                        # Measure latency
                        receive_time = time.time()
                        
                        # Initialize client data if not already present
                        if device_id not in client_data:
                            client_data[device_id] = {'timestamps': [], 'vibration_x': [], 'vibration_y': [], 'vibration_z': []}

                        # Update client data
                        client_data[device_id]['timestamps'].append(timestamp)
                        client_data[device_id]['vibration_x'].append(vibration_values[0])
                        client_data[device_id]['vibration_y'].append(vibration_values[1])
                        client_data[device_id]['vibration_z'].append(vibration_values[2])

                        # Put data into the queue
                        await data_queue.put((device_id, timestamp, vibration_values))

                        # Save to CSV file
                        with open(DATA_FILE, mode='a', newline='') as file:
                            csv_writer = csv.writer(file)
                            csv_writer.writerow([timestamp, device_id, *vibration_values])
                        
                        # Visualize data
                        visualize_data(timestamp, device_id, vibration_values)

                        # Send acknowledgment and measure the time
                        send_time = time.time()
                        writer.write(b"Data received")
                        await writer.drain()

                        # Record latency
                        latency = send_time - receive_time
                        with open(LATENCY_FILE, mode='a', newline='') as file:
                            csv_writer = csv.writer(file)
                            csv_writer.writerow([device_id, receive_time, send_time, latency])
                        
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
        # Close the server
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
