import asyncio
import json
import time

SERVER_HOST = '192.168.0.162'
SERVER_PORT = 8001
TEST_DURATION = 120  # Test duration in seconds
DATA_SIZE = 1024  # Size of each data packet in bytes

async def send_data(client_id):
    reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
    
    start_time = time.time()
    end_time = start_time + TEST_DURATION
    total_bytes_sent = 0

    try:
        while time.time() < end_time:
            timestamp = time.time()
            data = {
                'timestamp': timestamp,
                'device_id': client_id,
                'vibration_data': [0.1, 0.2, 0.3]  # Example data
            }
            message = json.dumps(data)
            message_bytes = message.encode('utf-8')
            
            writer.write(message_bytes)
            await writer.drain()
            
            total_bytes_sent += len(message_bytes)
            
            # Wait for acknowledgment
            await reader.read(100)
            
            await asyncio.sleep(1)  # Adjust as needed for your test
            
    finally:
        writer.close()
        await writer.wait_closed()
    
    # Calculate and return throughput
    elapsed_time = time.time() - start_time
    throughput = total_bytes_sent * 8 / elapsed_time  # Convert to bits per second
    return throughput

async def main():
    NUM_CLIENTS = 1000  # Number of clients
    tasks = [send_data(f'client{i+1}') for i in range(NUM_CLIENTS)]
    throughputs = await asyncio.gather(*tasks)
    
    # Calculate average throughput
    if throughputs:
        average_throughput = sum(throughputs) / len(throughputs)
        print(f"Average throughput across {NUM_CLIENTS} clients over {TEST_DURATION} seconds: {average_throughput:.2f} bps")
    else:
        print("No throughput data collected.")

if __name__ == "__main__":
    asyncio.run(main())
