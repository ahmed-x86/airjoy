# airjoy

Turn your smartphone into a virtual gamepad for Linux over the local network via browser.

Currently supports two controller layouts:
- **Xbox 360**
- **PS4 (DualShock 4)**

## Requirements

Install the required Python packages:

```bash
pip install aiohttp evdev
```

## Usage

Run the server with `sudo` (required for `/dev/uinput` access):

```bash
sudo python server.py -v
```

Open the IP and port displayed in the terminal on your phone's browser, choose your controller layout, and play.