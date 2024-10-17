#include <WiFi.h>
#include <WiFiUdp.h>
#include <BluetoothSerial.h>

// Environmental sensor pins (replace with your actual pins)
const int tempPin = 36; 
const int humidityPin = 39;

// Bluetooth Serial object
BluetoothSerial SerialBT;

WiFiUDP udp;

void setup() {
  Serial.begin(115200);

  // Initialize environmental sensors
  // ... sensor-specific initialization ...

  // Start Bluetooth
  SerialBT.begin("ESP32_Environmental"); // Bluetooth device name

  // Start WiFi and UDP server
  WiFi.begin("YOUR_WIFI_SSID", "YOUR_WIFI_PASSWORD");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  udp.begin(8888); // Use the same port as in the first ESP32 code
}

void loop() {
  // Receive microphone data from first ESP32
  int packetSize = udp.parsePacket();
  if (packetSize) {
    byte micData[3]; // Assuming 3 microphones
    udp.read(micData, packetSize);

    // Read environmental data
    float temperature = readTemperature(tempPin); // Replace with your sensor reading function
    float humidity = readHumidity(humidityPin);    // Replace with your sensor reading function

    // Combine data and send via Bluetooth
    String dataString = String(micData[0]) + "," + String(micData[1]) + "," + String(micData[2]) + "," + String(temperature) + "," + String(humidity);
    SerialBT.println(dataString);
  }
}