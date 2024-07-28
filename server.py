import socket
import json
import datetime
import threading
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import matplotlib.backends.backend_svg as svg

# Configuration
HOST = '192.168.56.1'
PORT = 5000
BUFFER_SIZE = 1024  # Size of each data packet received

# File for saving data
DATA_FILE = 'vibration_data.csv'

# Function to visualize the data in text mode
def visualize_data(vibration_data):
    # Simple text-based visualization: print basic statistics
    min_vibration = min(vibration_data)
    max_vibration = max(vibration_data)
    avg_vibration = sum(vibration_data) / len(vibration_data)

    print(f"Min Vibration: {min_vibration}")
    print(f"Max Vibration: {max_vibration}")
    print(f"Avg Vibration: {avg_vibration}")

    # Optional: ASCII art graph (for very simple visualization)
    print("\nVibration Data Plot:")
    scale_factor = 50 / max_vibration  # Scale data to fit 50-character width
    for value in vibration_data:
        bar_length = int(value * scale_factor)
        print(f"{'=' * bar_length} {value}")

def handle_client(connection, address):
    print(f"Connection established with {address}")
    with open(DATA_FILE, 'a') as file:
        while True:
            data = connection.recv(BUFFER_SIZE)
            if not data:
                break

            # Parse the incoming data (assuming JSON format)
            try:
                json_data = json.loads(data.decode('utf-8'))
                timestamp = json_data['timestamp']
                device_id = json_data['device_id']
                vibration_data = json_data['vibration_data']  # List of vibration readings

                # Write the data to the file
                for vibration in vibration_data:
                    file.write(f"{timestamp},{device_id},{vibration}\n")

                # Visualize the data
                visualize_data(vibration_data)

            except json.JSONDecodeError:
                print("Received malformed data")

    print(f"Connection closed with {address}")
    connection.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server listening on {HOST}:{PORT}")
    
    while True:
        connection, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(connection, address))
        client_thread.start()

if __name__ == '__main__':
    start_server()
