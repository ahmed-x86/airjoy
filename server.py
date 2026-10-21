#!/usr/bin/env python3
"""Phone Pad: use phones as virtual gamepads on Linux (Xbox 360, PS4, or Steam Input)."""
import argparse
import json
import socket
import os

from aiohttp import WSMsgType, web
from evdev import UInput
from evdev import ecodes as e

import xbox
import ps4
import steam

MAX_PADS = 4

PROFILES = {
    "xbox": xbox.PROFILE,
    "ps4": ps4.PROFILE,
    "steam": steam.PROFILE,
}
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


def make_km(index, prof):
    if "keys" not in prof:
        return None
    keys = list(prof["keys"].values()) + list(prof.get("mouse_buttons", {}).values())
    caps = {
        e.EV_KEY: keys,
        e.EV_REL: [e.REL_X, e.REL_Y],
    }
    return UInput(
        caps,
        name=f"{prof['name']} Keyboard/Mouse",
        vendor=prof["vendor"],
        product=prof["product"] + 1,
        version=prof["version"],
        bustype=e.BUS_USB,
        phys=f"phonepad_km/{index}",
    )


def scale(v, lo, hi, info):
    v = max(lo, min(hi, float(v)))
    return round(info.min + (v - lo) / (hi - lo) * (info.max - info.min))


def type_char(km, prof, ch):
    keys = prof["keys"]
    shifts = prof.get("shift_chars", {})
    if ch == "\n":
        code, need_shift = keys["ENTER"], False
    elif ch == " ":
        code, need_shift = keys["SPACE"], False
    elif ch in shifts:
        code, need_shift = keys.get(shifts[ch]), True
    else:
        up = ch.upper()
        code = keys.get(up)
        need_shift = ch.isalpha() and ch.isupper()

    if not code:
        return
    if need_shift:
        km.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
    km.write(e.EV_KEY, code, 1)
    km.syn()
    km.write(e.EV_KEY, code, 0)
    if need_shift:
        km.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
    km.syn()


def apply(pad, km, prof, msg):
    pad_dirty = False
    km_dirty = False

    for key, v in msg.items():
        axis = prof["axes"].get(key)
        if axis:
            code, info, lo, hi = axis
            pad.write(e.EV_ABS, code, scale(v, lo, hi, info))
            btn = prof["trigger_buttons"].get(key)
            if btn:
                pad.write(e.EV_KEY, btn, 1 if float(v) > 0.05 else 0)
            pad_dirty = True
        elif key in prof["buttons"]:
            pad.write(e.EV_KEY, prof["buttons"][key], 1 if v else 0)
            pad_dirty = True
        elif km and key == "TEXT":
            for ch in str(v):
                type_char(km, prof, ch)
        elif km and key in prof.get("keys", {}):
            km.write(e.EV_KEY, prof["keys"][key], 1 if v else 0)
            km_dirty = True
        elif km and key in prof.get("mouse_buttons", {}):
            km.write(e.EV_KEY, prof["mouse_buttons"][key], 1 if v else 0)
            km_dirty = True
        elif km and key == "MX":
            km.write(e.EV_REL, e.REL_X, int(v))
            km_dirty = True
        elif km and key == "MY":
            km.write(e.EV_REL, e.REL_Y, int(v))
            km_dirty = True

    if pad_dirty:
        pad.syn()
    if km and km_dirty:
        km.syn()


def neutral(pad, prof):
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
    mode = request.query.get("mode", "xbox")
    if mode not in PROFILES:
        mode = "xbox"

    prof = PROFILES[mode]

    try:
        pad = make_pad(i, prof)
        km = make_km(i, prof)
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
                    apply(pad, km, prof, json.loads(msg.data))
                except (ValueError, TypeError):
                    pass
    finally:
        slots[i] = None
        pad.close()
        if km:
            km.close()
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

    app.router.add_get("/", lambda r: web.FileResponse(os.path.join(base_dir, "index.html")))
    app.router.add_get("/style.css", lambda r: web.FileResponse(os.path.join(base_dir, "style.css")))
    app.router.add_get("/script.js", lambda r: web.FileResponse(os.path.join(base_dir, "script.js")))
    app.router.add_get("/ws", ws_handler)

    print(f"\nOpen on your phones: http://{lan_ip()}:{args.port}\n")
    web.run_app(app, host="0.0.0.0", port=args.port, print=None)


if __name__ == "__main__":
    main()