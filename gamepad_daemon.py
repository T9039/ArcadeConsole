import time

import serial
from evdev import AbsInfo, UInput, ecodes

capabilities = {
    ecodes.EV_KEY: [
        ecodes.BTN_SELECT,  # Joy Click (Coin)
        ecodes.BTN_START,  # SunFounder (Start)
        ecodes.BTN_SOUTH,  # G1 ('A' / Shoot)
        ecodes.BTN_EAST,  # G2 ('B' / Jump)
        ecodes.BTN_NORTH,  # G3 ('X' / Grenade)
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
    gamepad = UInput(capabilities, name="RP2040 Arcade Pro", version=0x6)
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

            if len(data) == 7:
                try:
                    x_val, y_val = int(data[0]), int(data[1])
                    joy_b, start_b = int(data[2]), int(data[3])
                    g1_b, g2_b, g3_b = int(data[4]), int(data[5]), int(data[6])

                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_X, x_val)
                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_Y, y_val)

                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_SELECT, joy_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_START, start_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_SOUTH, g1_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_EAST, g2_b)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_NORTH, g3_b)

                    gamepad.syn()

                except ValueError:
                    pass

except KeyboardInterrupt:
    pass
finally:
    arduino.close()
    gamepad.close()
