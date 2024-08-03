import asyncio
import json
import time
import sys

SERVER_HOST = '192.168.0.162'
SERVER_PORT = 8001
TEST_DURATION = 120  # Test duration in seconds
NUM_CLIENTS = 10000  # Number of clients

async def send_data(client_id):
    reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
    
    start_time = time.time()
    end_time = start_time + TEST_DURATION
    latency_times = []

    try:
        while time.time() < end_time:
            timestamp = time.time()
            data = {
                'timestamp': timestamp,
                'device_id': client_id,
                'vibration_data': [0.1, 0.2, 0.3]  # Example data
            }
            message = json.dumps(data)
            send_time = time.time()
            writer.write(message.encode('utf-8'))
            await writer.drain()
            
            # Wait for acknowledgment
            response = await reader.read(100)
            receive_time = time.time()
            
            # Record RTT
            rtt = receive_time - send_time
            latency_times.append(rtt)
            
            await asyncio.sleep(1)  # Adjust as needed for your test
            
    finally:
        writer.close()
        await writer.wait_closed()
    
    # Return latency data for this client
    return latency_times

async def main():
    tasks = [send_data(f'client{i+1}') for i in range(NUM_CLIENTS)]
    all_latencies = await asyncio.gather(*tasks)
    
    # Flatten the list of latencies and calculate average latency
    all_latencies_flat = [rtt for latencies in all_latencies for rtt in latencies]
    
    if all_latencies_flat:
        average_latency = sum(all_latencies_flat) / len(all_latencies_flat)
        print(f"Average latency across {NUM_CLIENTS} clients over {TEST_DURATION} seconds: {average_latency:.4f} seconds")
    else:
        print("No latency data collected.")

if __name__ == "__main__":
    asyncio.run(main())
