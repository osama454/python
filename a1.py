# Micropython code for ESP-WROOM-32 (mic1.py, mic2.py, mic3.py)

import time
import socket
import machine
from machine import Pin, I2S

# I2S configuration (adjust as needed)
SCK_PIN = 32
WS_PIN = 25
SD_PIN = 33
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 1024

# Network configuration
HOST = 'your_computer_ip'  # Replace with your workstation's IP address
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

# Initialize I2S
audio_in = I2S(
    I2S_ID,
    sck=Pin(SCK_PIN),
    ws=Pin(WS_PIN),
    sd=Pin(SD_PIN),
    mode=I2S.RX,
    bits=16,
    format=I2S.MONO,
    rate=44100,
    ibuf=BUFFER_LENGTH_IN_BYTES,
)

# Initialize network socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    while True:
        try:
            # Read audio data from I2S
            audio_samples = audio_in.read(BUFFER_LENGTH_IN_BYTES)
            
            # Send audio data over the network
            s.sendall(audio_samples) 

        except (KeyboardInterrupt, Exception) as e:
            print("Error:", e)
            break

    s.close()