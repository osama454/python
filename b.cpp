#include <Arduino.h>
#include <esp_system.h>
#include <driver/adc.h>
#include <Semaphore.h>

// Define pins
#define THERMISTOR_PIN 32
#define MIC_PIN 34

// Thermistor parameters (adjust these based on your thermistor)
#define THERMISTOR_NOMINAL 100000      // Nominal resistance at 25°C
#define TEMPERATURENOMINAL 25          // Temperature for nominal resistance (25°C)
#define BCOEFFICIENT 3950              // Beta coefficient of the thermistor

// Global variables
SemaphoreHandle_t xSemaphore;
bool temp_output_enabled = false;
bool mic_output_enabled = false;

// Task handles
TaskHandle_t tempTaskHandle;
TaskHandle_t micTaskHandle;

// Function prototypes
void tempTask(void *pvParameters);
void micTask(void *pvParameters);

void setup() {
  Serial.begin(115200);

  // Initialize semaphore
  xSemaphore = xSemaphoreCreateMutex();

  // Initialize ADC for temperature sensor
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_11); // Adjust channel if necessary

  // Create tasks
  xTaskCreate(tempTask, "TempTask", 2048, NULL, 1, &tempTaskHandle);
  xTaskCreate(micTask, "MicTask", 2048, NULL, 1, &micTaskHandle);
}

void loop() {
  // Handle serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "gp") {
      // Get ESP32 information
      xSemaphoreTake(xSemaphore, portMAX_DELAY);
      Serial.printf("ESP32 Chip Revision: %d\n", ESP.getChipRevision());
      Serial.printf("CPU Frequency: %d MHz\n", ESP.getCpuFreqMHz());
      Serial.printf("Flash Chip Size: %d MB\n", ESP.getFlashChipSize() / (1024 * 1024));
      Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());
      Serial.printf("SDK Version: %s\n", ESP.getSdkVersion());
      xSemaphoreGive(xSemaphore);
    } else if (command.startsWith("tm")) {
      // Handle temperature sensor command
      int mode = command.substring(3).toInt();
      if (mode == 0) {
        temp_output_enabled = false;
        vTaskSuspend(tempTaskHandle);
      } else if (mode == 1) {
        temp_output_enabled = true;
        vTaskResume(tempTaskHandle);
      } else {
        // Read temperature once
        xSemaphoreTake(xSemaphore, portMAX_DELAY);
        int adc_reading = adc1_get_raw(ADC1_CHANNEL_6); // Adjust channel if necessary
        float voltage = (adc_reading / 4095.0) * 3.3;
        float resistance = (3.3 * (100000.0 / voltage)) - 100000.0;
        float steinhart = resistance / THERMISTOR_NOMINAL;     // (R/Ro)
        steinhart = log(steinhart);                  // ln(R/Ro)
        steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
        steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
        steinhart = 1.0 / steinhart;                 // Invert
        steinhart -= 273.15;                         // convert absolute temp to C
        Serial.printf("Temperature: %.2f °C\n", steinhart);
        xSemaphoreGive(xSemaphore);
      }
    } else if (command.startsWith("am")) {
      // Handle microphone command
      int mode = command.substring(3).toInt();
      if (mode == 0) {
        mic_output_enabled = false;
        vTaskSuspend(micTaskHandle);
      } else if (mode == 1) {
        mic_output_enabled = true;
        vTaskResume(micTaskHandle);
      } else {
        // Read microphone once
        xSemaphoreTake(xSemaphore, portMAX_DELAY);
        int mic_reading = analogRead(MIC_PIN);
        Serial.printf("Microphone Reading: %d\n", mic_reading);
        xSemaphoreGive(xSemaphore);
      }
    }
  }
}

// Task to read and output temperature
void tempTask(void *pvParameters) {
  while (true) {
    if (temp_output_enabled) {
      xSemaphoreTake(xSemaphore, portMAX_DELAY);
      int adc_reading = adc1_get_raw(ADC1_CHANNEL_6); // Adjust channel if necessary
      float voltage = (adc_reading / 4095.0) * 3.3;
      float resistance = (3.3 * (100000.0 / voltage)) - 100000.0;
      float steinhart = resistance / THERMISTOR_NOMINAL;     // (R/Ro)
      steinhart = log(steinhart);                  // ln(R/Ro)
      steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
      steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
      steinhart = 1.0 / steinhart;                 // Invert
      steinhart -= 273.15;                         // convert absolute temp to C
      Serial.printf("Temperature: %.2f °C\n", steinhart);
      xSemaphoreGive(xSemaphore);
    }
    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}

// Task to read and output microphone data
void micTask(void *pvParameters) {
  while (true) {
    if (mic_output_enabled) {
      xSemaphoreTake(xSemaphore, portMAX_DELAY);
      int mic_reading = analogRead(MIC_PIN);
      Serial.printf("Microphone Reading: %d\n", mic_reading);
      xSemaphoreGive(xSemaphore);
    }
    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}