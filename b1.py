import machine
import time
import network
import socket
from machine import Pin, I2S

# I2S configuration
SCK_PIN = 32
WS_PIN = 25
SD_PIN = 33
I2S_ID = 0
BUFFER_SIZE = 1024

# WiFi configuration
SSID = "your_wifi_ssid"
PASSWORD = "your_wifi_password"

# UDP configuration
HOST = "your_workstation_ip"
PORT = 5000

# Initialize I2S
audio_in = I2S(
    I2S_ID,
    sck=Pin(SCK_PIN),
    ws=Pin(WS_PIN),
    sd=Pin(SD_PIN),
    mode=I2S.RX,
    bits=32,
    format=I2S.MONO,
    rate=44100,
    ibuf=BUFFER_SIZE,
)

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    pass
print("Connected to WiFi")

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Main loop
while True:
    try:
        # Read audio data
        samples = audio_in.read(BUFFER_SIZE)

        # Get timestamp
        timestamp = time.ticks_ms()

        # Send data and timestamp over UDP
        sock.sendto(f"{timestamp}:{samples}".encode(), (HOST, PORT))

    except Exception as e:
        print(f"Error: {e}")