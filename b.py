import serial

# Configure the serial port
ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with your serial port

def get_esp_info():
    """Sends the 'gp' command and prints the ESP32 information."""
    ser.write(b'gp\n')
    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            break
        print(line)

def control_temp_output(mode):
    """Controls the temperature output mode.
    0: Stop output
    1: Continuous output
    other: Output once
    """
    command = f'tm {mode}\n'
    ser.write(command.encode('utf-8'))
    if mode != 1:  # Only read output if not continuous mode
        print(ser.readline().decode('utf-8').strip())

def control_mic_output(mode):
    """Controls the microphone output mode.
    0: Stop output
    1: Continuous output
    other: Output once
    """
    command = f'am {mode}\n'
    ser.write(command.encode('utf-8'))
    if mode != 1:  # Only read output if not continuous mode
        print(ser.readline().decode('utf-8').strip())

if __name__ == "__main__":
    get_esp_info()
    control_temp_output(1)  # Start continuous temperature output
    