import socket
import json
import time
import random

SERVER_HOST = '192.168.0.162'
SERVER_PORT = 8001     

def generate_vibration_data():
    return [random.uniform(-1.0, 1.0) for _ in range(3)]

def send_vibration_data():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))

    # Get and print the local IP address and port of the client
    local_ip, local_port = client.getsockname()
    print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")
    print(f"Client local address: {local_ip}:{local_port}")
    
    try:
        while True:
            # Create a data packet
            data_packet = {
                'timestamp': time.time(),
                'device_id': 'ESP32_01',
                'vibration_data': generate_vibration_data()
            }
            
            # Send the data packet
            client.sendall(json.dumps(data_packet).encode('utf-8'))
            
            # Receive acknowledgment from the server
            acknowledgment = client.recv(1024).decode('utf-8')
            print(f"Acknowledgment from server: {acknowledgment}")
            
            time.sleep(1)  
    finally:
        client.close()

if __name__ == "__main__":
    send_vibration_data()
