import time

import serial
from evdev import AbsInfo, UInput, ecodes

# --- 1. DEFINE THE VIRTUAL GAMEPAD ---
# We tell the Linux kernel what features our fake controller has
capabilities = {
    # It has one action button (we'll map this to the standard 'A' button)
    ecodes.EV_KEY: [ecodes.BTN_SOUTH],
    # It has absolute X and Y axes (min 0, max 65535, starting at center 32768)
    # We leave fuzz/flat at 0 because the RP2040 is already doing the noise filtering!
    ecodes.EV_ABS: [
        (
            ecodes.ABS_X,
            AbsInfo(value=32768, min=0, max=65535, fuzz=0, flat=0, resolution=0),
        ),
        (
            ecodes.ABS_Y,
            AbsInfo(value=32768, min=0, max=65535, fuzz=0, flat=0, resolution=0),
        ),
    ],
}

# Create the virtual device in the operating system
try:
    gamepad = UInput(capabilities, name="RP2040 Custom Controller", version=0x3)
    print("Virtual Gamepad successfully injected into Linux kernel!")
except Exception as e:
    print(f"Error creating virtual device: {e}")
    print(
        "CRITICAL: You must run this script with 'sudo' to access the kernel uinput system."
    )
    exit()

# --- 2. CONNECT TO SERIAL ---
try:
    arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    print("Connected to RP2040. Translating data to gamepad inputs...")
except Exception as e:
    print(f"Failed to connect to Serial: {e}")
    exit()

time.sleep(1)

# --- 3. THE TRANSLATION LOOP ---
try:
    while True:
        if arduino.in_waiting > 0:
            raw_line = arduino.readline().decode("utf-8").strip()
            data = raw_line.split(",")

            if len(data) == 3:
                try:
                    x_val = int(data[0])
                    y_val = int(data[1])
                    is_pressed = int(data[2])

                    # Inject the X and Y axis positions
                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_X, x_val)
                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_Y, y_val)

                    # Inject the Button state (1 = pressed, 0 = released)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_SOUTH, is_pressed)

                    # Synchronize the events (tells Linux "this frame of input is complete")
                    gamepad.syn()

                except ValueError:
                    pass  # Ignore corrupted serial text

except KeyboardInterrupt:
    print("\nShutting down virtual controller...")
finally:
    arduino.close()
    gamepad.close()
