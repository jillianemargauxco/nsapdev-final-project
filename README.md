# Vibration Monitoring System

## Overview

This project demonstrates a vibration monitoring system using an ESP32 microcontroller and an ADXL345 accelerometer sensor. The system collects and transmits vibration data to a server, which processes and visualizes the data in real time. The project includes client and server applications, data visualization, and performance tests.

## Components

1. **ADXL345 Accelerometer Sensor**: Measures vibrations along the X, Y, and Z axes.
2. **ESP32 Microcontroller**: Collects sensor data and transmits it to a server.
3. **Server Application**: Receives and processes vibration data, visualizes it in real-time, and generates CSV files.
4. **Client Application**: Simulates data transmission to the server.

## Files and Directories

- **`adxl345`**: Contains the code for interfacing with the ADXL345 accelerometer sensor.
  
- **`results/`**: Contains CSV files with vibration data collected from the sensor. These files include timestamped vibration measurements along X, Y, and Z axes.

- **`results_epoch/`**: Contains CSV files similar to `results/` but with timestamps converted to epoch time.

- **`tests/`**: Contains performance test scripts for latency, throughput, and load testing of the server.
  

## Running the System

1. **Setup the Hardware**:
   - Connect the ADXL345 accelerometer to the ESP32 microcontroller.
   - Ensure proper wiring and power supply.

2. **Run the Server Application**:
   - Navigate to the directory containing `server.py`.
   - Execute the server script with `python server.py`.
   - The server will start listening for connections and processing incoming data.

3. **Run the Client Application**:
   - Navigate to the directory containing `client.py`.
   - Execute the client script with `python client.py`.
   - The client will start sending simulated vibration data to the server.

4. **Check Results**:
   - The server application will generate CSV files in the `results/` and `results_epoch/` directories.
   - CSV files will contain timestamped vibration data.

## Configuration

- **Server Configuration**: Adjust the `HOST` and `PORT` variables in `server.py` to match your network setup.
- **Client Configuration**: Adjust the `SERVER_HOST` and `SERVER_PORT` variables in `client.py` to point to the server's IP address and port.
