import socket
import json
import time
import datetime

HOST = '192.168.56.1'
PORT = 5000

def send_vibration_data():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    try:
        for _ in range(5):  # Send 5 batches of data
            timestamp = datetime.datetime.now().isoformat()
            device_id = 'device_1'
            vibration_data = [0.1, 0.2, 0.3, 0.4, 0.5]  # Example vibration data

            data = {
                'timestamp': timestamp,
                'device_id': device_id,
                'vibration_data': vibration_data
            }

            json_data = json.dumps(data)
            client_socket.sendall(json_data.encode('utf-8'))

            time.sleep(1)  # Wait 1 second before sending the next batch

    finally:
        client_socket.close()

if __name__ == '__main__':
    send_vibration_data()
