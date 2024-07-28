import socket
import json
import csv
import time
import threading
import matplotlib.pyplot as plt

HOST = '192.168.0.162'  
PORT = 12345  

DATA_FILE = 'vibration_data.csv'

file_lock = threading.Lock()

def handle_client_connection(client_socket):
    try:
        while True:
       
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
     
            try:
                vibration_data = json.loads(data)
                timestamp = vibration_data['timestamp']
                device_id = vibration_data['device_id']
                vibration_values = vibration_data['vibration_data']
                
 
                with file_lock:
                    with open(DATA_FILE, mode='a', newline='') as file:
                        csv_writer = csv.writer(file)
                        csv_writer.writerow([timestamp, device_id, *vibration_values])
                
      
                visualize_data(timestamp, device_id, vibration_values)
                
            except json.JSONDecodeError:
                print("Received invalid JSON data.")
                
    finally:
        client_socket.close()

def visualize_data(timestamp, device_id, vibration_values):
    print(f"Timestamp: {timestamp}, Device ID: {device_id}")
    print("Vibration Data:")
    print(" | ".join(f"{value:.2f}" for value in vibration_values))
    print("-" * 40)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_socket,)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
