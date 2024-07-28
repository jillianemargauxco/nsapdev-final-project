#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>

// WiFi credentials
const char* ssid = "Chowder Main Tenda";
const char* password = "Chewy1212!";

// Server details
const char* host = "192.168.0.162";  // Replace with your server's IP address
const uint16_t port = 5001;         // Port number used by the server

// Create an ADXL345 object
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

void setup() {
  Serial.begin(115200);
  delay(100);

  // Initialize the ADXL345
  if (!accel.begin()) {
    Serial.println("Failed to initialize ADXL345!");
    while (1);
  }
  accel.setRange(ADXL345_RANGE_16_G);

  // Initialize WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
}

void loop() {
  sensors_event_t event;
  accel.getEvent(&event);

  // Collecting vibration data
  float x = event.acceleration.x;
  float y = event.acceleration.y;
  float z = event.acceleration.z;

  // Create JSON formatted data
  String data = "{";
  data += "\"timestamp\":\"" + String(millis()) + "\",";
  data += "\"device_id\":\"esp32_1\",";
  data += "\"vibration_data\":[" + String(x) + "," + String(y) + "," + String(z) + "]";
  data += "}";

  // Send data to server
  if (sendDataToServer(data)) {
    Serial.println("Data sent successfully!");
  } else {
    Serial.println("Failed to send data!");
  }

  delay(1000);  // Adjust the polling rate as needed
}

bool sendDataToServer(String data) {
  WiFiClient client;

  if (!client.connect(host, port)) {
    Serial.println("Connection to server failed");
    return false;
  }

  client.print(data);
  delay(10);  // Short delay for data transmission
  client.stop();
  return true;
}
