import socket
import json
import time
import random

SERVER_HOST = '192.168.1.103'  
SERVER_PORT = 8001     

def generate_vibration_data():
    return [random.uniform(-1.0, 1.0) for _ in range(3)]

def send_vibration_data():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
    
    try:
        while True:
            # Create a data packet
            data_packet = {
                'timestamp': time.time(),
                'device_id': 'ESP32_02',
                'vibration_data': generate_vibration_data()
            }
            
            client.sendall(json.dumps(data_packet).encode('utf-8'))
            
            time.sleep(1)  
    finally:
        client.close()

if __name__ == "__main__":
    send_vibration_data()
