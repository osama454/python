#include <Arduino.h>
#include <Semaphore.h>

// Define pins
#define THERMISTOR_PIN 35
#define MIC_PIN 34

// Thermistor parameters
#define THERMISTOR_NOMINAL 100000      // Nominal resistance at 25°C
#define TEMPERATURE_NOMINAL 25        // Temperature for nominal resistance (25°C)
#define BCOEFFICIENT 3950          // B coefficient of thermistor

// Semaphores for serial communication and sensor reading
SemaphoreHandle_t serialSemaphore;
SemaphoreHandle_t tempSemaphore;
SemaphoreHandle_t micSemaphore;

// Task handles
TaskHandle_t tempTaskHandle;
TaskHandle_t micTaskHandle;

// Flags for continuous sensor reading
bool continuousTempReading = false;
bool continuousMicReading = false;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Initialize semaphores
  serialSemaphore = xSemaphoreCreateMutex();
  tempSemaphore = xSemaphoreCreateBinary();
  micSemaphore = xSemaphoreCreateBinary();

  // Initialize temperature sensor
  pinMode(THERMISTOR_PIN, INPUT);

  // Initialize microphone
  pinMode(MIC_PIN, INPUT);
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    xSemaphoreTake(serialSemaphore, portMAX_DELAY);
    String command = Serial.readStringUntil('\n');
    command.trim();
    xSemaphoreGive(serialSemaphore);

    // Process commands
    if (command == "gp") {
      printGeneralInfo();
    } else if (command.startsWith("tm")) {
      handleTempCommand(command);
    } else if (command.startsWith("am")) {
      handleMicCommand(command);
    }
  }
}

// Task to read temperature sensor
void tempTask(void *pvParameters) {
  while (true) {
    if (xSemaphoreTake(tempSemaphore, portMAX_DELAY) == pdTRUE) {
      // Read temperature and output to serial port
      float temperature = readTemperature();
      xSemaphoreTake(serialSemaphore, portMAX_DELAY);
      Serial.print("Temperature: ");
      Serial.println(temperature);
      xSemaphoreGive(serialSemaphore);

      if (!continuousTempReading) {
        xSemaphoreGive(tempSemaphore);
      }
      vTaskDelay(1000 / portTICK_PERIOD_MS); // Delay for 1 second
    }
  }
}

// Task to read microphone
void micTask(void *pvParameters) {
  while (true) {
    if (xSemaphoreTake(micSemaphore, portMAX_DELAY) == pdTRUE) {
      // Read microphone level and output to serial port
      int micLevel = analogRead(MIC_PIN);
      xSemaphoreTake(serialSemaphore, portMAX_DELAY);
      Serial.print("Microphone Level: ");
      Serial.println(micLevel);
      xSemaphoreGive(serialSemaphore);

      if (!continuousMicReading) {
        xSemaphoreGive(micSemaphore);
      }
      vTaskDelay(1000 / portTICK_PERIOD_MS); // Delay for 1 second
    }
  }
}

// Handle temperature command
void handleTempCommand(String command) {
  if (command == "tm") {
    // Read temperature once
    xSemaphoreGive(tempSemaphore);
  } else if (command == "tm 1") {
    // Start continuous temperature reading
    continuousTempReading = true;
    xSemaphoreGive(tempSemaphore);
    if (tempTaskHandle == NULL) {
      xTaskCreate(tempTask, "TempTask", 2048, NULL, 1, &tempTaskHandle);
    }
  } else if (command == "tm 0") {
    // Stop continuous temperature reading
    continuousTempReading = false;
    xSemaphoreGive(tempSemaphore);
  }
}

// Handle microphone command
void handleMicCommand(String command) {
  if (command == "am") {
    // Read microphone level once
    xSemaphoreGive(micSemaphore);
  } else if (command == "am 1") {
    // Start continuous microphone reading
    continuousMicReading = true;
    xSemaphoreGive(micSemaphore);
    if (micTaskHandle == NULL) {
      xTaskCreate(micTask, "MicTask", 2048, NULL, 1, &micTaskHandle);
    }
  } else if (command == "am 0") {
    // Stop continuous microphone reading
    continuousMicReading = false;
    xSemaphoreGive(micSemaphore);
  }
}

// Read temperature from thermistor
float readTemperature() {
  int reading = analogRead(THERMISTOR_PIN);
  float resistance = 4095.0 / reading - 1.0;
  resistance = 100000.0 / resistance; // Calculate thermistor resistance

  float steinhart;
  steinhart = resistance / THERMISTOR_NOMINAL;     // (R/Ro)
  steinhart = log(steinhart);                  // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURE_NOMINAL + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Invert
  steinhart -= 273.15;                         // convert absolute temp to C

  return steinhart;
}

// Print general ESP32 information
void printGeneralInfo() {
  xSemaphoreTake(serialSemaphore, portMAX_DELAY);
  Serial.println("ESP32 General Information:");
  Serial.print("Core Count: ");
  Serial.println(xPortGetCoreID());
  Serial.print("CPU Frequency: ");
  Serial.print(ESP.getCpuFreqMHz());
  Serial.println(" MHz");
  Serial.print("Flash Chip Size: ");
  Serial.print(ESP.getFlashChipSize() / (1024 * 1024));
  Serial.println(" MB");
  Serial.print("Free Heap: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");
  Serial.println();
  xSemaphoreGive(serialSemaphore);
}