import gc
import sys
import time

from machine import ADC, Pin

# Hardware Init
x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))
btn = Pin(25, Pin.IN, Pin.PULL_UP)

# Grid Constants
W, H = 31, 15
CX, CY = W // 2, H // 2

# ANSI Colors & Commands
RST = "\033[0m"
CYN = "\033[38;5;51m"
BLU = "\033[38;5;24m"
GRN = "\033[38;5;46m"
RED = "\033[38;5;196m"
GRY = "\033[38;5;236m"
WHT = "\033[38;5;255m"
YLW = "\033[38;5;226m"


def draw_static_background():
    write = sys.stdout.write
    write("\033[?25l\033[2J\033[H")

    write(f"{CYN}╔" + ("═" * 64) + f"╗{RST}\r\n")
    write(
        f"{CYN}║{WHT}                  RP2040 DELTA-RENDER ENGINE                    {CYN}║{RST}\r\n"
    )
    write(f"{CYN}╠" + ("═" * 64) + f"╣{RST}\r\n")
    write("\r\n\r\n")
    write(f"{CYN}╠" + ("═" * 64) + f"╣{RST}\r\n")

    for row in range(H):
        line = [f"{CYN}║ {RST}"]
        for col in range(W):
            if row == CY and col == CX:
                line.append(f"{WHT}╂─{RST}")
            elif row == CY:
                line.append(f"{BLU}──{RST}")
            elif col == CX:
                line.append(f"{BLU}│ {RST}")
            else:
                line.append(f"{GRY}· {RST}")
        line.append(f"{CYN} ║{RST}\r\n")
        write("".join(line))

    write(f"{CYN}╚" + ("═" * 64) + f"╝{RST}\r\n")


@micropython.native
def run_telemetry():
    write = sys.stdout.write
    read_x = x_axis.read_u16
    read_y = y_axis.read_u16
    read_btn = btn.value
    sleep = time.sleep

    # Filter Tuning
    NOISE_THRESH = 350
    DEADZONE = 2500
    CENTER_VAL = 32768

    stable_x, stable_y = CENTER_VAL, CENTER_VAL
    prev_gx, prev_gy = -1, -1
    prev_btn_state = -1
    prev_x_raw, prev_y_raw = -1, -1

    # Heartbeat counter added here
    frame_count = 0

    gc.disable()
    draw_static_background()

    try:
        while True:
            raw_x = read_x()
            raw_y = read_y()
            is_pressed = not read_btn()

            # 1. Hysteresis
            if abs(raw_x - stable_x) > NOISE_THRESH:
                stable_x = raw_x
            if abs(raw_y - stable_y) > NOISE_THRESH:
                stable_y = raw_y

            # 2. Deadzone
            if abs(stable_x - CENTER_VAL) < DEADZONE:
                final_x = CENTER_VAL
            else:
                final_x = stable_x

            if abs(stable_y - CENTER_VAL) < DEADZONE:
                final_y = CENTER_VAL
            else:
                final_y = stable_y

            gx = (final_x * 30) // 65535
            gy = (final_y * 14) // 65535

            out = []

            # DELTA UPDATE: Stats Panel
            if (
                final_x != prev_x_raw
                or final_y != prev_y_raw
                or is_pressed != prev_btn_state
            ):
                x_fill = (final_x * 14) // 65535
                y_fill = (final_y * 14) // 65535

                out.append(
                    f"\033[4;1H{CYN}║{RST}  X:[{WHT}{'█' * x_fill}{'─' * (14 - x_fill)}{RST}] {YLW}{final_x:05d}{RST}   Y:[{WHT}{'█' * y_fill}{'─' * (14 - y_fill)}{RST}] {YLW}{final_y:05d}{RST} {CYN}║{RST}"
                )

                status_str = (
                    f"{RED}PRESSED {RST}" if is_pressed else f"{GRN}RELEASED{RST}"
                )
                out.append(
                    f"\033[5;1H{CYN}║{RST}  STATUS: {status_str}                                           {CYN}║{RST}"
                )

                prev_x_raw, prev_y_raw = final_x, final_y

            # DELTA UPDATE: Grid Cursor
            if gx != prev_gx or gy != prev_gy or is_pressed != prev_btn_state:
                if prev_gx != -1:
                    t_row = prev_gy + 7
                    t_col = (prev_gx * 2) + 3

                    if prev_gy == CY and prev_gx == CX:
                        bg_char = f"{WHT}╂─{RST}"
                    elif prev_gy == CY:
                        bg_char = f"{BLU}──{RST}"
                    elif prev_gx == CX:
                        bg_char = f"{BLU}│ {RST}"
                    else:
                        bg_char = f"{GRY}· {RST}"

                    out.append(f"\033[{t_row};{t_col}H{bg_char}")

                t_row = gy + 7
                t_col = (gx * 2) + 3
                cursor_char = f"{RED}╬╬{RST}" if is_pressed else f"{GRN}██{RST}"
                out.append(f"\033[{t_row};{t_col}H{cursor_char}")

                prev_gx, prev_gy = gx, gy
                prev_btn_state = is_pressed

            # Write to stdout if there's an update
            if out:
                write("".join(out))

            # --- THE FIX: HEARTBEAT GC ---
            frame_count += 1
            if frame_count >= 60:
                gc.collect()
                frame_count = 0

            sleep(0.008)

    except KeyboardInterrupt:
        pass
    finally:
        gc.enable()
        write("\033[23;1H\033[?25h\r\nEngine stopped cleanly.\r\n")


# Execute
run_telemetry()
