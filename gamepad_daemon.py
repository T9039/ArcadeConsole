import time

import serial
from evdev import AbsInfo, UInput, ecodes

capabilities = {
    ecodes.EV_KEY: [
        ecodes.BTN_SELECT,  # Coin
        ecodes.BTN_START,  # Start
        ecodes.BTN_SOUTH,  # A
        ecodes.BTN_EAST,  # B
        ecodes.BTN_NORTH,  # X
        ecodes.BTN_WEST,  # Y
    ],
    # CHANGED: We are now declaring a Digital D-Pad (HAT) instead of an Analog Stick
    ecodes.EV_ABS: [
        (
            ecodes.ABS_HAT0X,
            AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0),
        ),
        (
            ecodes.ABS_HAT0Y,
            AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0),
        ),
    ],
}

try:
    gamepad = UInput(capabilities, name="RP2040 NeoGeo Digital", version=0x9)
    arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
except Exception as e:
    print(f"Startup Error: {e}")
    exit()

time.sleep(1)

try:
    while True:
        if arduino.in_waiting > 0:
            raw_line = arduino.readline().decode("utf-8").strip()
            data = raw_line.split(",")

            if len(data) == 8:
                try:
                    x_val, y_val = int(data[0]), int(data[1])
                    sel_b, start_b = int(data[2]), int(data[3])
                    a_b, b_b, x_b, y_b = (
                        int(data[4]),
                        int(data[5]),
                        int(data[6]),
                        int(data[7]),
                    )

                    # --- ANALOG TO DIGITAL CONVERSION ---
                    hat_x, hat_y = 0, 0
                    if x_val < 15000:
                        hat_x = -1  # Left
                    elif x_val > 50000:
                        hat_x = 1  # Right

                    if y_val < 15000:
                        hat_y = -1  # Up
                    elif y_val > 50000:
                        hat_y = 1  # Down

                    # Send D-Pad Data
                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_HAT0X, hat_x)
                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_HAT0Y, hat_y)

                    # Send Button Data
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_SELECT, sel_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_START, start_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_SOUTH, a_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_EAST, b_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_NORTH, x_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_WEST, y_b)

                    gamepad.syn()

                except ValueError:
                    pass

except KeyboardInterrupt:
    pass
finally:
    arduino.close()
    gamepad.close()
