#include <PDM.h>

// Microphone connections (adjust pins as needed)
#define MIC1_CLK 14
#define MIC1_DATA 12
#define MIC2_CLK 27
#define MIC2_DATA 26
#define MIC3_CLK 25
#define MIC3_DATA 33

// Sampling rate and buffer size (adjust as needed)
#define SAMPLE_RATE 44100 
#define BUFFER_SIZE 512 

// PDM instances
PDM mic1(MIC1_CLK, MIC1_DATA);
PDM mic2(MIC2_CLK, MIC2_DATA);
PDM mic3(MIC3_CLK, MIC3_DATA);

// Data buffers
short mic1_buffer[BUFFER_SIZE];
short mic2_buffer[BUFFER_SIZE];
short mic3_buffer[BUFFER_SIZE];

void setup() {
  Serial.begin(115200);

  // Disable watchdog timer (if needed)
  disableCore0WDT(); 

  // Initialize microphones
  mic1.begin(SAMPLE_RATE);
  mic2.begin(SAMPLE_RATE);
  mic3.begin(SAMPLE_RATE);
}

void loop() {
  // Read microphone data
  mic1.read(mic1_buffer, BUFFER_SIZE);
  mic2.read(mic2_buffer, BUFFER_SIZE);
  mic3.read(mic3_buffer, BUFFER_SIZE);

  // Send data over WiFi (replace with your WiFi code)
  // ...

}