import serial

# Configure the serial port
ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with your serial port

def send_command(command):
  """Sends a command to the ESP32."""
  ser.write(command.encode() + b'\n')
  response = ser.readline().decode().strip()
  print(response)

# Send commands
send_command("gp")  # Get general ESP32 information
send_command("tm")  # Get temperature reading once
send_command("tm 1")  # Start continuous temperature reading
# ... wait for some time ...
send_command("tm 0")  # Stop continuous temperature reading
send_command("am")  # Get microphone level once
send_command("am 1")  # Start continuous microphone level reading
# ... wait for some time ...
send_command("am 0")  # Stop continuous microphone level reading

# Close the serial port
ser.close()