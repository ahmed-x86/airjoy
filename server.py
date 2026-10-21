#!/usr/bin/env python3
"""Phone Pad: use phones as virtual gamepads on Linux (Xbox 360 or PS4 style)."""
import argparse
import json
import socket
import os

from aiohttp import WSMsgType, web
from evdev import AbsInfo, UInput
from evdev import ecodes as e

MAX_PADS = 4

STICK_XBOX = AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)
STICK_PS4 = AbsInfo(value=128, min=0, max=255, fuzz=0, flat=0, resolution=0)
TRIGGER = AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)
HAT = AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)

XBOX = {
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
        "LX": (e.ABS_X, STICK_XBOX, -1, 1), "LY": (e.ABS_Y, STICK_XBOX, -1, 1),
        "RX": (e.ABS_RX, STICK_XBOX, -1, 1), "RY": (e.ABS_RY, STICK_XBOX, -1, 1),
        "LT": (e.ABS_Z, TRIGGER, 0, 1), "RT": (e.ABS_RZ, TRIGGER, 0, 1),
        "DX": (e.ABS_HAT0X, HAT, -1, 1), "DY": (e.ABS_HAT0Y, HAT, -1, 1),
    },
}

PS4 = {
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
        "LX": (e.ABS_X, STICK_PS4, -1, 1), "LY": (e.ABS_Y, STICK_PS4, -1, 1),
        "RX": (e.ABS_Z, STICK_PS4, -1, 1), "RY": (e.ABS_RZ, STICK_PS4, -1, 1),
        "LT": (e.ABS_RX, TRIGGER, 0, 1), "RT": (e.ABS_RY, TRIGGER, 0, 1),
        "DX": (e.ABS_HAT0X, HAT, -1, 1), "DY": (e.ABS_HAT0Y, HAT, -1, 1),
    },
}

PROFILES = {"xbox": XBOX, "ps4": PS4}
slots = [None] * MAX_PADS


def make_pad(index, prof):
    keys = list(prof["buttons"].values()) + list(prof["trigger_buttons"].values())
    caps = {
        e.EV_KEY: keys,
        e.EV_ABS: [(code, info) for code, info, _, _ in prof["axes"].values()],
    }
    return UInput(
        caps,
        name=prof["name"],
        vendor=prof["vendor"],
        product=prof["product"],
        version=prof["version"],
        bustype=e.BUS_USB,
        phys=f"phonepad/{index}",
    )


def scale(v, lo, hi, info):
    v = max(lo, min(hi, float(v)))
    return round(info.min + (v - lo) / (hi - lo) * (info.max - info.min))


def apply(pad, prof, msg):
    for key, v in msg.items():
        axis = prof["axes"].get(key)
        if axis:
            code, info, lo, hi = axis
            pad.write(e.EV_ABS, code, scale(v, lo, hi, info))
            btn = prof["trigger_buttons"].get(key)
            if btn:
                pad.write(e.EV_KEY, btn, 1 if float(v) > 0.05 else 0)
        elif key in prof["buttons"]:
            pad.write(e.EV_KEY, prof["buttons"][key], 1 if v else 0)
    pad.syn()


def neutral(pad, prof):
    """Write the resting position of every axis so apps see a clean initial state."""
    for code, info, lo, hi in prof["axes"].values():
        pad.write(e.EV_ABS, code, scale(0, lo, hi, info))
    pad.syn()


def devnode(pad):
    try:
        return pad.device.path
    except Exception:
        return "?"


async def ws_handler(request):
    app = request.app
    ws = web.WebSocketResponse(heartbeat=10)
    await ws.prepare(request)

    if None not in slots:
        await ws.send_json({"error": f"All {MAX_PADS} pads are in use"})
        await ws.close()
        return ws

    i = slots.index(None)
    # تحديد نوع يد التحكم من الجوال
    mode = request.query.get("mode", "xbox")
    if mode not in PROFILES:
        mode = "xbox"
    
    prof = PROFILES[mode]
    
    try:
        pad = make_pad(i, prof)
    except PermissionError:
        await ws.send_json({"error": "No access to /dev/uinput. Run with sudo."})
        await ws.close()
        return ws

    slots[i] = pad
    neutral(pad, prof)
    print(f"[+] pad {i + 1} ({prof['label']}) connected from {request.remote} -> {devnode(pad)}")
    await ws.send_json({"player": i + 1})
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if app["verbose"]:
                    print(f"    pad {i + 1}: {msg.data}")
                try:
                    apply(pad, prof, json.loads(msg.data))
                except (ValueError, TypeError):
                    pass
    finally:
        slots[i] = None
        pad.close()
        print(f"[-] pad {i + 1} disconnected")
    return ws


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def main():
    ap = argparse.ArgumentParser(description="Use phones as virtual gamepads.")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("-v", "--verbose", action="store_true", help="print every message from the phones")
    args = ap.parse_args()

    app = web.Application()
    app["verbose"] = args.verbose
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # توجيه الروابط إلى الملفات المفصولة
    app.router.add_get("/", lambda r: web.FileResponse(os.path.join(base_dir, "index.html")))
    app.router.add_get("/style.css", lambda r: web.FileResponse(os.path.join(base_dir, "style.css")))
    app.router.add_get("/script.js", lambda r: web.FileResponse(os.path.join(base_dir, "script.js")))
    app.router.add_get("/ws", ws_handler)

    print(f"\nOpen on your phones: http://{lan_ip()}:{args.port}\n")
    web.run_app(app, host="0.0.0.0", port=args.port, print=None)


if __name__ == "__main__":
    main()