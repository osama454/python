import socket
import numpy as np
from scipy.signal import correlate

# UDP configuration
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5000

# Beamforming parameters
SPEED_OF_SOUND = 343  # m/s
MIC_DISTANCE = 0.1  # Distance between microphones in meters

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

# Initialize buffers for audio data and timestamps
buffers = [{}, {}, {}]

def align_audio(data1, data2, sr):
    """Align two audio signals using cross-correlation."""
    corr = correlate(data1, data2)
    delay = (corr.argmax() - (len(data1) - 1)) / sr
    return delay

def beamform(data1, data2, data3, delays):
    """Apply delay-and-sum beamforming."""
    # Apply delays
    aligned_data1 = np.roll(data1, int(delays[0] * sr))
    aligned_data2 = np.roll(data2, int(delays[1] * sr))
    aligned_data3 = np.roll(data3, int(delays[2] * sr))

    # Sum the aligned signals
    output = (aligned_data1 + aligned_data2 + aligned_data3) / 3
    return output

# Main loop
while True:
    try:
        # Receive data from ESP32s
        data, addr = sock.recvfrom(2048)
        timestamp, samples = data.decode().split(":")
        esp_id = addr[0]  # Identify the ESP32

        # Store data in buffers
        buffers[esp_id][timestamp] = samples

        # Check if all buffers have data for the same timestamp
        if all(timestamp in buffer for buffer in buffers.values()):
            # Extract data for the current timestamp
            data1 = buffers[0][timestamp]
            data2 = buffers[1][timestamp]
            data3 = buffers[2][timestamp]

            # Align audio data
            delay12 = align_audio(data1, data2, sr)
            delay13 = align_audio(data1, data3, sr)
            delays = [0, delay12, delay13]

            # Apply beamforming
            output = beamform(data1, data2, data3, delays)

            # Process or play output audio
            # ...

    except Exception as e:
        print(f"Error: {e}")