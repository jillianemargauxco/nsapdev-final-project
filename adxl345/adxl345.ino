#include <WiFi.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

// Replace with your network credentials
const char* ssid = "Home Network_Guest";

// Server details
const char* server_host = "192.168.68.114";  // Replace with your server's IP
const uint16_t server_port = 8001;

// Define the LED pin
const int ledPin = 15;

// Define vibration threshold in g-force
const float vibrationThreshold = 15.0; // Adjust the threshold as needed

// Create an ADXL345 object
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

// NTP configuration
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 3600;  // GMT offset in seconds (e.g., 3600 for +1 hour)
const int daylightOffset_sec = 0; // Daylight offset in seconds

WiFiUDP udp;
NTPClient timeClient(udp, ntpServer, gmtOffset_sec, 60000); // Update every 60 seconds

void setup() {
  Serial.begin(115200);

  // Initialize the LED pin as output
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW); // Ensure the LED is off at startup

  // Initialize the accelerometer
  if (!accel.begin()) {
    Serial.println("Failed to find ADXL345 chip");
    while (1);
  }
  accel.setRange(ADXL345_RANGE_16_G); // Set the range to +/- 16G

  // Connect to WiFi
  WiFi.begin(ssid);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");

  // Initialize NTP Client
  timeClient.begin();
}

void loop() {
  // Update time
  timeClient.update();
  unsigned long epochTime = timeClient.getEpochTime();

  // Get sensor event
  sensors_event_t event;
  accel.getEvent(&event);

  // Calculate the magnitude of the vibration
  float vibrationMagnitude = sqrt(sq(event.acceleration.x) + sq(event.acceleration.y) + sq(event.acceleration.z));

  // Check if the vibration magnitude exceeds the threshold
  if (vibrationMagnitude > vibrationThreshold) {
    Serial.println("Vibration threshold exceeded!");
  
    // Turn on the LED
    digitalWrite(ledPin, HIGH);

    // Wait for 1 second before turning off the LED
    delay(1000);
    
    // Turn off the LED
    digitalWrite(ledPin, LOW);
  }

  // Create a JSON object for the vibration data
  StaticJsonDocument<200> jsonDoc;
  jsonDoc["timestamp"] = epochTime;  // Use epoch time
  jsonDoc["device_id"] = "ESP32_ADXL345";
  JsonArray vibrationData = jsonDoc.createNestedArray("vibration_data");
  vibrationData.add(event.acceleration.x);
  vibrationData.add(event.acceleration.y);
  vibrationData.add(event.acceleration.z);

  // Serialize JSON data
  String jsonData;
  serializeJson(jsonDoc, jsonData);

  // Send data to server
  if (sendDataToServer(jsonData)) {
    Serial.println("Data sent successfully:");
    Serial.println(jsonData);
  } else {
    Serial.println("Failed to send data.");
    Serial.println(jsonData);
  }

  // Wait before sending the next data
  delay(1000); // Adjust the polling rate as needed
}

bool sendDataToServer(const String& jsonData) {
  WiFiClient client;
  if (!client.connect(server_host, server_port)) {
    Serial.println("Connection to server failed");
    return false;
  }

  // Send the JSON data
  client.println(jsonData);

  // Wait for server response with a timeout
  unsigned long startTime = millis();
  while (client.available() == 0) {
    if (millis() - startTime > 5000) { // 5 seconds timeout
      Serial.println("Server response timeout");
      client.stop();
      return false;
    }
    delay(10);
  }

  // Print server response (optional)
  while (client.available()) {
    String response = client.readStringUntil('\r');
    Serial.print(response);
  }

  client.stop();
  return true;
}
