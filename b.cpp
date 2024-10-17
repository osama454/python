#include <WiFi.h>

// Define microphone pins
const int micPins[] = {32, 33, 34}; // Replace with your actual pins
const int numMics = sizeof(micPins) / sizeof(micPins[0]);

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Second ESP32 IP address
const char* esp32_2_ip = "SECOND_ESP32_IP_ADDRESS";

// Disable watchdog timer (optional, for lowest latency)
#ifdef ESP32
  disableCore0WDT();
  disableCore1WDT();
#endif

void setup() {
  Serial.begin(115200);

  // Initialize microphones (refer to your microphone library for specific setup)
  for (int i = 0; i < numMics; i++) {
    pinMode(micPins[i], INPUT);
    // ... microphone-specific initialization ...
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Sample microphones
  byte micData[numMics];
  for (int i = 0; i < numMics; i++) {
    micData[i] = digitalRead(micPins[i]); // Simplified PDM reading
  }

  // Send data to second ESP32 via UDP
  WiFiUDP udp;
  udp.beginPacket(esp32_2_ip, 8888); // Replace 8888 with your desired port
  udp.write(micData, sizeof(micData));
  udp.endPacket();
}