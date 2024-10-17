# Python code for workstation (beamforming.py)

import socket
import numpy as np
import sounddevice as sd

# Network configuration
HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

# Beamforming parameters
SAMPLE_RATE = 44100
BUFFER_LENGTH = BUFFER_LENGTH_IN_BYTES // 2  # Divide by 2 for 16-bit samples
MIC_DISTANCE = 0.1  # Distance between microphones in meters
SOUND_SPEED = 343  # Speed of sound in m/s

# Initialize audio buffers
audio_buffers = [[0] * BUFFER_LENGTH, [0] * BUFFER_LENGTH, [0] * BUFFER_LENGTH]

# Function to perform beamforming
def beamform(audio_data):
    # Calculate time delays for each microphone
    delays = [0]  # No delay for the first microphone
    for i in range(1, 3):
        angle = np.arctan2(i * MIC_DISTANCE, 0)  # Assuming mics are in a line
        delay = MIC_DISTANCE * np.cos(angle) / SOUND_SPEED
        delays.append(int(delay * SAMPLE_RATE))

    # Apply delays and sum signals
    output_data = np.zeros(BUFFER_LENGTH)
    for i, data in enumerate(audio_data):
        for j, sample in enumerate(data):
            output_data[j] += audio_data[i][j - delays[i]]

    # Normalize output
    output_data /= len(audio_data)
    return output_data

# Create a TCP/IP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn1, addr1 = s.accept()
    conn2, addr2 = s.accept()
    conn3, addr3 = s.accept()
    with conn1, conn2, conn3:
        print('Connected by', addr1, addr2, addr3)
        while True:
            try:
                # Receive audio data from ESP32s
                data1 = conn1.recv(BUFFER_LENGTH_IN_BYTES)
                data2 = conn2.recv(BUFFER_LENGTH_IN_BYTES)
                data3 = conn3.recv(BUFFER_LENGTH_IN_BYTES)

                # Convert bytes to numpy arrays
                audio_buffers[0] = np.frombuffer(data1, dtype=np.int16)
                audio_buffers[1] = np.frombuffer(data2, dtype=np.int16)
                audio_buffers[2] = np.frombuffer(data3, dtype=np.int16)

                # Perform beamforming
                output_data = beamform(audio_buffers)

                # Play audio using sounddevice
                sd.play(output_data, SAMPLE_RATE)
                sd.wait()

            except (KeyboardInterrupt, Exception) as e:
                print("Error:", e)
                break