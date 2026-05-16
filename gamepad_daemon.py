import time

import serial
from evdev import AbsInfo, UInput, ecodes

capabilities = {
    ecodes.EV_KEY: [
        ecodes.BTN_SOUTH,  # Joystick Click ('A' Button)
        ecodes.BTN_EAST,  # SunFounder Button ('B' Button)
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
    gamepad = UInput(capabilities, name="RP2040 Arcade Controller", version=0x4)
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

            if len(data) == 4:
                try:
                    x_val, y_val = int(data[0]), int(data[1])
                    joy_pressed, b_pressed = int(data[2]), int(data[3])

                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_X, x_val)
                    gamepad.write(ecodes.EV_ABS, ecodes.ABS_Y, y_val)

                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_SOUTH, joy_pressed)
                    gamepad.write(ecodes.EV_KEY, ecodes.BTN_EAST, b_pressed)

                    gamepad.syn()

                except ValueError:
                    pass

except KeyboardInterrupt:
    pass
finally:
    arduino.close()
    gamepad.close()
