import time

import serial
from evdev import AbsInfo, UInput, ecodes

capabilities = {
    ecodes.EV_KEY: [
        ecodes.BTN_SELECT,  # Joystick Click (Coin)
        ecodes.BTN_START,  # SunFounder (Start)
        ecodes.BTN_SOUTH,  # G1 (A)
        ecodes.BTN_EAST,  # G2 (B)
        ecodes.BTN_NORTH,  # G3 (X)
        ecodes.BTN_WEST,  # G4 (Y)
    ],
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

try:
    gamepad = UInput(capabilities, name="RP2040 NeoGeo Controller", version=0x8)
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

            # Expecting exactly 8 data points
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

                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_X, x_val)
                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_Y, y_val)

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
