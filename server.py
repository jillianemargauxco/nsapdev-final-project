import asyncio
import json
import csv
import time
import matplotlib.pyplot as plt
from asyncio import Queue

HOST = '10.2.201.193'
PORT = 8001

DATA_FILE = 'vibration_data.csv'

data_queue = Queue()
client_data = {}
colors = plt.cm.get_cmap('tab10', 10)  # Color map with 10 colors

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
                        
                        # Initialize client data if not already present
                        if device_id not in client_data:
                            client_data[device_id] = {'timestamps': [], 'vibration_x': [], 'vibration_y': [], 'vibration_z': []}

                        # Update client data
                        client_data[device_id]['timestamps'].append(timestamp)
                        client_data[device_id]['vibration_x'].append(vibration_values[0])
                        client_data[device_id]['vibration_y'].append(vibration_values[1])
                        client_data[device_id]['vibration_z'].append(vibration_values[2])

                        # Put data into the queue for plotting
                        await data_queue.put((device_id, timestamp, vibration_values))

                        # Save to CSV file
                        with open(DATA_FILE, mode='a', newline='') as file:
                            csv_writer = csv.writer(file)
                            csv_writer.writerow([timestamp, device_id, *vibration_values])
                        
                        # Visualize data
                        visualize_data(timestamp, device_id, vibration_values)

                        # Send acknowledgment to the client
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

async def update_plot():
    plt.ion()  # Interactive mode on
    fig, axs = plt.subplots(3, 1, figsize=(10, 6))
    
    while True:
        try:

            device_id, timestamp, vibration_values = await data_queue.get()
            if device_id not in client_data:
                client_data[device_id] = {'timestamps': [], 'vibration_x': [], 'vibration_y': [], 'vibration_z': []}
            
            # Update data
            client_data[device_id]['timestamps'].append(timestamp)
            client_data[device_id]['vibration_x'].append(vibration_values[0])
            client_data[device_id]['vibration_y'].append(vibration_values[1])
            client_data[device_id]['vibration_z'].append(vibration_values[2])

            # Clear previous plots
            axs[0].cla()
            axs[1].cla()
            axs[2].cla()

            # Plot data for each client
            for i, (client_id, data) in enumerate(client_data.items()):
                color = colors(i % 10)  # Cycle through colors
                axs[0].plot(data['timestamps'], data['vibration_x'], label=f'{client_id} X-axis', color=color)
                axs[1].plot(data['timestamps'], data['vibration_y'], label=f'{client_id} Y-axis', color=color)
                axs[2].plot(data['timestamps'], data['vibration_z'], label=f'{client_id} Z-axis', color=color)

            # Update plot labels and legend
            axs[0].set_xlabel('Timestamp')
            axs[0].set_ylabel('Vibration X')
            axs[0].legend(loc='upper right')

            axs[1].set_xlabel('Timestamp')
            axs[1].set_ylabel('Vibration Y')
            axs[1].legend(loc='upper right')

            axs[2].set_xlabel('Timestamp')
            axs[2].set_ylabel('Vibration Z')
            axs[2].legend(loc='upper right')

            plt.tight_layout()
            plt.pause(0.1)  # Pause to update the plot
        except asyncio.CancelledError:
            break

async def start_server():
    server = await asyncio.start_server(handle_client_connection, HOST, PORT)
    print(f"Server listening on {HOST}:{PORT}")

    # Start the plot update task
    plot_task = asyncio.create_task(update_plot())

    try:
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        plt.ioff()  # Interactive mode off
        plt.show()
        plot_task.cancel()
        await plot_task

if __name__ == "__main__":
    asyncio.run(start_server())
