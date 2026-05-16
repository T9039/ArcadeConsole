import time

import serial

# Open the serial port
# 115200 is the standard baud rate, and timeout=1 prevents the script from hanging forever
try:
    arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    print("Successfully connected to RP2040!")
except Exception as e:
    print(f"Failed to connect: {e}")
    print("Check your USB connection and port name.")
    exit()

# Give the serial connection a second to stabilize
time.sleep(1)

print("Listening for joystick data... (Press Ctrl+C to stop)")

try:
    while True:
        # Check if there is data waiting in the serial buffer
        if arduino.in_waiting > 0:
            # Read the line, decode the bytes to string, and strip the \r\n newline characters
            raw_line = arduino.readline().decode("utf-8").strip()

            # Split the string "32768,32768,0" into a list ["32768", "32768", "0"]
            data = raw_line.split(",")

            # Ensure we got exactly 3 pieces of data before trying to parse them
            # This prevents crashes if a garbled half-message comes through
            if len(data) == 3:
                try:
                    x_val = int(data[0])
                    y_val = int(data[1])
                    is_pressed = bool(int(data[2]))

                    # --- YOUR PI LOGIC GOES HERE ---
                    # You now have clean Python variables to use for your project!
                    # For now, let's just print them to verify:
                    print(
                        f"Pi Received -> X: {x_val:05d} | Y: {y_val:05d} | Button: {is_pressed}"
                    )

                except ValueError:
                    # Ignore frames where the data got corrupted in transit
                    pass

except KeyboardInterrupt:
    print("\nClosing connection...")
finally:
    # Always cleanly close the serial port when exiting
    arduino.close()
