from evdev import AbsInfo, ecodes as e

STICK = AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)
TRIGGER = AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)
HAT = AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)

PROFILE = {
    "label": "Xbox 360",
    "name": "Microsoft X-Box 360 pad",
    "vendor": 0x045E, "product": 0x028E, "version": 0x0114,
    "buttons": {
        "A": e.BTN_SOUTH, "B": e.BTN_EAST,
        "X": e.BTN_X, "Y": e.BTN_Y,
        "LB": e.BTN_TL, "RB": e.BTN_TR,
        "BACK": e.BTN_SELECT, "START": e.BTN_START, "GUIDE": e.BTN_MODE,
        "LS": e.BTN_THUMBL, "RS": e.BTN_THUMBR,
    },
    "trigger_buttons": {},
    "axes": {
        "LX": (e.ABS_X, STICK, -1, 1), "LY": (e.ABS_Y, STICK, -1, 1),
        "RX": (e.ABS_RX, STICK, -1, 1), "RY": (e.ABS_RY, STICK, -1, 1),
        "LT": (e.ABS_Z, TRIGGER, 0, 1), "RT": (e.ABS_RZ, TRIGGER, 0, 1),
        "DX": (e.ABS_HAT0X, HAT, -1, 1), "DY": (e.ABS_HAT0Y, HAT, -1, 1),
    },
}