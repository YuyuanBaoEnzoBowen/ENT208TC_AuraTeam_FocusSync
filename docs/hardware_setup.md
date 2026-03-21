# Hardware Setup Guide

This document describes the components required to build a FocusSync device
and explains how to connect them to a Raspberry Pi.

---

## Bill of Materials

| # | Component | Qty | Notes |
|---|-----------|-----|-------|
| 1 | Raspberry Pi 4 Model B (2 GB+) | 1 | RPi Zero 2 W also works |
| 2 | MH-Z19B NDIR CO₂ sensor | 1 | 5 V, UART interface |
| 3 | NeoPixel RGB LED ring (12 LEDs) | 1 | WS2812B, 5 V |
| 4 | Passive buzzer | 1 | 3.3 V compatible |
| 5 | Tactile push button (momentary) | 1 | Any standard 6 mm × 6 mm PCB button |
| 6 | 470 Ω resistor | 1 | In series with NeoPixel data line |
| 7 | 1000 µF / 6.3 V capacitor | 1 | Across NeoPixel 5 V and GND |
| 8 | Micro-SD card (16 GB+, Class 10) | 1 | Running Raspberry Pi OS Lite |
| 9 | 5 V / 3 A USB-C power supply | 1 | Powers both RPi and LED ring |
| 10 | Jumper wires + small breadboard | — | For prototyping |

---

## Wiring

### MH-Z19B CO₂ Sensor → Raspberry Pi

| MH-Z19B Pin | RPi Pin (physical) | GPIO (BCM) | Description |
|-------------|-------------------|------------|-------------|
| VIN (5 V)   | Pin 2 or 4        | —          | 5 V power   |
| GND         | Pin 6             | —          | Ground      |
| TXD         | Pin 10            | GPIO 15 (RX) | Sensor TX → RPi RX |
| RXD         | Pin 8             | GPIO 14 (TX) | RPi TX → Sensor RX |

> **Note:** Enable the hardware UART on the RPi by running
> `sudo raspi-config → Interface Options → Serial Port`.
> Disable the serial login shell, but **enable** the serial hardware port.
> The device will be available at `/dev/ttyS0`.

---

### NeoPixel LED Ring → Raspberry Pi

| NeoPixel Pin | RPi Pin (physical) | GPIO (BCM) |
|-------------|-------------------|------------|
| 5 V (PWR)   | Pin 4             | —          |
| GND         | Pin 14            | —          |
| DIN (Data)  | 470 Ω → Pin 12    | GPIO 18    |

Place the 1000 µF capacitor between the 5 V and GND rails **at the ring**
(not at the RPi) to prevent the power-on current surge from damaging the LEDs.

> **Why GPIO 18?** The NeoPixel library requires a hardware-PWM pin.
> GPIO 18 (physical pin 12) is the only safe choice on most Raspberry Pi models.

---

### Passive Buzzer → Raspberry Pi

| Buzzer Pin | RPi Pin (physical) | GPIO (BCM) |
|-----------|-------------------|------------|
| + (signal) | Pin 13            | GPIO 27    |
| − (GND)    | Pin 9             | —          |

The buzzer is driven by software PWM; no transistor is needed for a 3.3 V-compatible buzzer.

---

### Push Button → Raspberry Pi

| Button Pin | RPi Pin (physical) | GPIO (BCM) |
|-----------|-------------------|------------|
| One leg    | Pin 11            | GPIO 17    |
| Other leg  | Pin 25 (GND)      | —          |

The firmware enables the internal pull-up resistor, so no external resistor is required.

---

## Wiring Diagram (ASCII)

```
Raspberry Pi 4
─────────────────────────────────────────────
Pin  2 (5V)  ──────────────────┬───────── MH-Z19B VIN
Pin  4 (5V)  ─────┬────────────│────────── NeoPixel 5V (+Cap+)
Pin  6 (GND) ─────┼────────────┼────┬───── MH-Z19B GND
Pin  8 (TX)  ──────────────────│────│────── MH-Z19B RXD
Pin 10 (RX)  ──────────────────│────│────── MH-Z19B TXD
Pin 11 (GPIO17) ───────────────│────│────── Button leg A
Pin 12 (GPIO18) ──[470Ω]───────│────│────── NeoPixel DIN
Pin 13 (GPIO27) ───────────────│────│────── Buzzer +
Pin 14 (GND) ─────┼────────────│────┼────── NeoPixel GND (−Cap−)
Pin  9 (GND) ─────┼────────────│────┼────── Buzzer −
Pin 25 (GND) ─────┼────────────│────┼────── Button leg B
                   │           │   │
                  GND bus      └───┘
                             5V bus
```

---

## Software Installation

```bash
# 1. Update the OS
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3 and pip
sudo apt install python3 python3-pip git -y

# 3. Install the NeoPixel library (requires running as root for GPIO access)
sudo pip3 install rpi-ws281x adafruit-circuitpython-neopixel

# 4. Install pyserial for the CO2 sensor
sudo pip3 install pyserial

# 5. Clone the FocusSync repository
git clone https://github.com/YuyuanBaoEnzoBowen/ENT208TC_AuraTeam_FocusSync.git
cd ENT208TC_AuraTeam_FocusSync

# 6. Run the firmware (requires root for GPIO/NeoPixel)
sudo python3 -m firmware.main

# --- Development / testing (no hardware required) ---
python3 -m pytest tests/ -v
```

---

## Auto-start on Boot

To have FocusSync start automatically when the Raspberry Pi powers on,
create a systemd service:

```bash
sudo tee /etc/systemd/system/focussync.service > /dev/null <<'EOF'
[Unit]
Description=FocusSync physical focus companion
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/ENT208TC_AuraTeam_FocusSync
ExecStart=/usr/bin/python3 -m firmware.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable focussync
sudo systemctl start focussync
```

Check the service status with `sudo systemctl status focussync`.
