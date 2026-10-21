from evdev import AbsInfo, ecodes as e

STICK = AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)
TRIGGER = AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)
HAT = AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)

# خريطة أزرار الكيبورد المدعومة في وضع Steam Input
KEYS = {
    "ESC": e.KEY_ESC, "TAB": e.KEY_TAB, "ENTER": e.KEY_ENTER,
    "BACKSPACE": e.KEY_BACKSPACE, "SPACE": e.KEY_SPACE,
    "SHIFT": e.KEY_LEFTSHIFT, "CTRL": e.KEY_LEFTCTRL,
    "ALT": e.KEY_LEFTALT, "META": e.KEY_LEFTMETA,
    "UP": e.KEY_UP, "DOWN": e.KEY_DOWN, "LEFT": e.KEY_LEFT, "RIGHT": e.KEY_RIGHT,
    "F1": e.KEY_F1, "F2": e.KEY_F2, "F3": e.KEY_F3, "F4": e.KEY_F4,
    "F5": e.KEY_F5, "F6": e.KEY_F6, "F7": e.KEY_F7, "F8": e.KEY_F8,
    "F9": e.KEY_F9, "F10": e.KEY_F10, "F11": e.KEY_F11, "F12": e.KEY_F12,
    "1": e.KEY_1, "2": e.KEY_2, "3": e.KEY_3, "4": e.KEY_4, "5": e.KEY_5,
    "6": e.KEY_6, "7": e.KEY_7, "8": e.KEY_8, "9": e.KEY_9, "0": e.KEY_0,
    "Q": e.KEY_Q, "W": e.KEY_W, "E": e.KEY_E, "R": e.KEY_R, "T": e.KEY_T,
    "Y": e.KEY_Y, "U": e.KEY_U, "I": e.KEY_I, "O": e.KEY_O, "P": e.KEY_P,
    "A": e.KEY_A, "S": e.KEY_S, "D": e.KEY_D, "F": e.KEY_F, "G": e.KEY_G,
    "H": e.KEY_H, "J": e.KEY_J, "K": e.KEY_K, "L": e.KEY_L,
    "Z": e.KEY_Z, "X": e.KEY_X, "C": e.KEY_C, "V": e.KEY_V, "B": e.KEY_B,
    "N": e.KEY_N, "M": e.KEY_M,
    "-": e.KEY_MINUS, "=": e.KEY_EQUAL, "[": e.KEY_LEFTBRACE, "]": e.KEY_RIGHTBRACE,
    ";": e.KEY_SEMICOLON, "'": e.KEY_APOSTROPHE, ",": e.KEY_COMMA,
    ".": e.KEY_DOT, "/": e.KEY_SLASH, "\\": e.KEY_BACKSLASH, "`": e.KEY_GRAVE,
}

# تحويل الرموز المكتوبة من كيبورد الهاتف التي تتطلب زر Shift
SHIFT_CHARS = {
    "!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8", "(": "9", ")": "0",
    "_": "-", "+": "=", "{": "[", "}": "]", ":": ";", '"': "'", "<": ",", ">": ".", "?": "/", "|": "\\", "~": "`"
}

PROFILE = {
    "label": "Steam Input",
    "name": "Valve Software Steam Virtual Gamepad",
    "vendor": 0x28DE, "product": 0x11FF, "version": 0x0001,
    "buttons": {
        "A": e.BTN_SOUTH, "B": e.BTN_EAST,
        "X": e.BTN_X, "Y": e.BTN_Y,
        "LB": e.BTN_TL, "RB": e.BTN_TR,
        "BACK": e.BTN_SELECT, "START": e.BTN_START, "GUIDE": e.BTN_MODE,
        "LS": e.BTN_THUMBL, "RS": e.BTN_THUMBR,
        "L4": e.BTN_TRIGGER_HAPPY1, "R4": e.BTN_TRIGGER_HAPPY2,
    },
    "trigger_buttons": {"LT": e.BTN_TL2, "RT": e.BTN_TR2},
    "axes": {
        "LX": (e.ABS_X, STICK, -1, 1), "LY": (e.ABS_Y, STICK, -1, 1),
        "RX": (e.ABS_RX, STICK, -1, 1), "RY": (e.ABS_RY, STICK, -1, 1),
        "LT": (e.ABS_Z, TRIGGER, 0, 1), "RT": (e.ABS_RZ, TRIGGER, 0, 1),
        "DX": (e.ABS_HAT0X, HAT, -1, 1), "DY": (e.ABS_HAT0Y, HAT, -1, 1),
    },
    "keys": KEYS,
    "shift_chars": SHIFT_CHARS,
    "mouse_buttons": {
        "M_LEFT": e.BTN_LEFT,
        "M_RIGHT": e.BTN_RIGHT,
    },
}