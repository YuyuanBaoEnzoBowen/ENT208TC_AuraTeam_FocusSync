"""
FocusSync configuration constants.

Centralises all hardware pin assignments, timing parameters, and
CO2 thresholds so that a single file needs updating when the wiring
or desired behaviour changes.
"""

# ---------------------------------------------------------------------------
# Hardware – Raspberry Pi GPIO (BCM numbering)
# ---------------------------------------------------------------------------

# Physical button: one side to this pin, other side to GND.
# Internal pull-up is enabled so the pin reads HIGH when the button is open
# and LOW when pressed.
BUTTON_PIN: int = 17

# Passive buzzer (driven via PWM).
BUZZER_PIN: int = 27

# NeoPixel data line (must be a hardware-PWM-capable pin on RPi).
LED_DATA_PIN: int = 18
LED_COUNT: int = 12          # Number of NeoPixel LEDs in the ring
LED_BRIGHTNESS: float = 0.4  # 0.0 – 1.0

# MH-Z19B CO2 sensor connected to the first UART port.
CO2_SERIAL_PORT: str = "/dev/ttyS0"
CO2_BAUD_RATE: int = 9_600
CO2_READ_INTERVAL_S: float = 10.0   # Seconds between CO2 readings

# ---------------------------------------------------------------------------
# CO2 thresholds (ppm)
# ---------------------------------------------------------------------------

CO2_GOOD: int = 800        # Below this → good air quality (green)
CO2_MODERATE: int = 1_000  # 800–1000 → moderate (yellow)
CO2_POOR: int = 1_500      # 1000–1500 → poor (orange-red)
                            # Above 1500 → dangerous (flashing red + buzzer)

# ---------------------------------------------------------------------------
# Pomodoro timer durations (seconds)
# ---------------------------------------------------------------------------

WORK_DURATION_S: int = 25 * 60      # 25 minutes
SHORT_BREAK_S: int = 5 * 60         # 5 minutes
LONG_BREAK_S: int = 15 * 60         # 15 minutes
SESSIONS_BEFORE_LONG_BREAK: int = 4

# ---------------------------------------------------------------------------
# LED colours  (R, G, B) tuples used throughout the codebase
# ---------------------------------------------------------------------------

COLOUR_OFF = (0, 0, 0)
COLOUR_IDLE = (80, 80, 80)           # Soft white – standby / idle
COLOUR_GOOD = (0, 200, 0)            # Green – good air quality
COLOUR_MODERATE = (200, 200, 0)      # Yellow – moderate CO2
COLOUR_POOR = (200, 80, 0)           # Orange-red – poor CO2
COLOUR_DANGER = (200, 0, 0)          # Red – dangerous CO2
COLOUR_BREAK = (0, 80, 200)          # Blue – break time
COLOUR_SESSION_END = (200, 0, 200)   # Purple – session complete

# ---------------------------------------------------------------------------
# Buzzer tones (Hz)
# ---------------------------------------------------------------------------

BUZZ_SESSION_START_HZ: int = 880    # A5
BUZZ_SESSION_END_HZ: int = 660      # E5
BUZZ_BREAK_END_HZ: int = 880
BUZZ_DANGER_HZ: int = 1_000         # Warning tone
BUZZ_DURATION_MS: int = 200         # Duration of each beep
