# FocusSync — Screen-Free Physical Focus Companion

> **ENT208TC · Aura Team · XJTLU**

FocusSync is a Raspberry Pi–based desktop device that helps university
students stay focused without depending on a smartphone.  It combines a
**Pomodoro-style timer** with **real-time CO₂ monitoring** to create a
tangible, screen-free boundary between work and distraction.

---

## The Problem

Existing focus apps (Forest, Pomodoro timers) live on smartphones — the
very devices that cause distraction.  Opening the phone to start a session
exposes the student to notifications and social media.

Additionally, prolonged study in confined spaces (dormitories, libraries)
leads to elevated CO₂ levels that cause cognitive decline and drowsiness —
something no software-only tool can detect or address.

---

## Solution: FocusSync

A physical device that:

- **Requires no screen or phone** — a single button press starts a focus session.
- **Monitors room CO₂** using an MH-Z19B NDIR sensor and alerts the student when ventilation is needed.
- **Gives silent, at-a-glance feedback** through a colour-coded NeoPixel LED ring.
- **Uses a Pomodoro timer** (25 min work / 5 min break / 15 min long break after 4 sessions).

---

## Hardware at a Glance

| Component | Purpose |
|-----------|---------|
| Raspberry Pi 4 | Main controller |
| MH-Z19B CO₂ sensor | Air-quality monitoring via UART |
| 12-LED NeoPixel ring | Silent visual status feedback |
| Passive buzzer | Audio cues for session transitions |
| Push button | Start / pause / reset sessions |

See **[docs/hardware_setup.md](docs/hardware_setup.md)** for the full wiring
diagram and installation instructions.

---

## LED Colour Reference

| Colour | Meaning |
|--------|---------|
| 🟢 Green (solid) | Focus session active — good air quality (< 800 ppm CO₂) |
| 🟡 Yellow (solid) | Focus session active — moderate CO₂ (800–1000 ppm) |
| 🟠 Orange-red (solid) | Focus session active — poor CO₂ (1000–1500 ppm), open a window |
| 🔴 Red (flashing) | **Danger** — CO₂ > 1500 ppm; buzzer alert; ventilate immediately |
| 🔵 Blue (solid) | Break time |
| ⚪ White (breathing) | Idle — ready to start |
| 🟣 Purple (flash) | Session complete |

---

## Button Reference

| Press | Action |
|-------|--------|
| Short press (IDLE) | Start a new work session |
| Short press (WORK) | Pause the session |
| Short press (paused) | Resume the session |
| Short press (BREAK) | Skip the break |
| Long press ≥ 2 s | Reset everything |

---

## Repository Structure

```
ENT208TC_AuraTeam_FocusSync/
├── firmware/
│   ├── __init__.py
│   ├── config.py          # Pin assignments, thresholds, timer durations
│   ├── co2_sensor.py      # MH-Z19B UART driver (+ software mock)
│   ├── led_controller.py  # NeoPixel ring controller (+ software mock)
│   ├── buzzer.py          # Passive buzzer via GPIO PWM (+ software mock)
│   ├── focus_timer.py     # Pomodoro timer state machine
│   └── main.py            # Main application loop
├── tests/
│   ├── test_co2_sensor.py
│   ├── test_focus_timer.py
│   ├── test_led_controller.py
│   └── test_main_helpers.py
├── docs/
│   └── hardware_setup.md  # Wiring diagram & installation guide
├── requirements.txt
└── README.md
```

---

## Quick Start

### Run on real hardware (Raspberry Pi)

```bash
# Install dependencies (root required for GPIO / NeoPixel)
sudo pip3 install -r requirements.txt

# Start FocusSync
sudo python3 -m firmware.main
```

### Run in mock mode (any machine, no hardware needed)

```bash
pip install pyserial pytest
python -m firmware.main --mock
```

### Run tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Configuration

All tunable parameters are in **`firmware/config.py`**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `WORK_DURATION_S` | 1500 (25 min) | Length of one work session |
| `SHORT_BREAK_S` | 300 (5 min) | Short break duration |
| `LONG_BREAK_S` | 900 (15 min) | Long break duration |
| `SESSIONS_BEFORE_LONG_BREAK` | 4 | Pomodoros before a long break |
| `CO2_GOOD` | 800 ppm | LED turns green below this |
| `CO2_MODERATE` | 1000 ppm | LED turns yellow above this |
| `CO2_POOR` | 1500 ppm | LED flashes red above this |
| `BUTTON_PIN` | GPIO 17 | BCM pin for the push button |
| `LED_DATA_PIN` | GPIO 18 | BCM pin for NeoPixel data |
| `BUZZER_PIN` | GPIO 27 | BCM pin for buzzer |

---

## License

This project was created for the XJTLU ENT208TC module by Aura Team.
