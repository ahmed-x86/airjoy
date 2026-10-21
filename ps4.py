from evdev import AbsInfo, ecodes as e

STICK = AbsInfo(value=128, min=0, max=255, fuzz=0, flat=0, resolution=0)
TRIGGER = AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)
HAT = AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)

PROFILE = {
    "label": "PS4",
    "name": "Sony Interactive Entertainment Wireless Controller",
    "vendor": 0x054C, "product": 0x09CC, "version": 0x8111,
    "buttons": {
        "A": e.BTN_SOUTH, "B": e.BTN_EAST,
        "X": e.BTN_WEST, "Y": e.BTN_NORTH,
        "LB": e.BTN_TL, "RB": e.BTN_TR,
        "BACK": e.BTN_SELECT, "START": e.BTN_START, "GUIDE": e.BTN_MODE,
        "LS": e.BTN_THUMBL, "RS": e.BTN_THUMBR,
    },
    "trigger_buttons": {"LT": e.BTN_TL2, "RT": e.BTN_TR2},
    "axes": {
        "LX": (e.ABS_X, STICK, -1, 1), "LY": (e.ABS_Y, STICK, -1, 1),
        "RX": (e.ABS_Z, STICK, -1, 1), "RY": (e.ABS_RZ, STICK, -1, 1),
        "LT": (e.ABS_RX, TRIGGER, 0, 1), "RT": (e.ABS_RY, TRIGGER, 0, 1),
        "DX": (e.ABS_HAT0X, HAT, -1, 1), "DY": (e.ABS_HAT0Y, HAT, -1, 1),
    },
}