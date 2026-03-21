"""
FocusSync main application loop.

Ties together the CO2 sensor, LED ring, buzzer, physical button, and
Pomodoro timer into the complete FocusSync device behaviour.

Run with::

    python -m firmware.main          # real hardware
    python -m firmware.main --mock   # software mock (no GPIO / sensor)

Button behaviour
----------------
* **Single press** while IDLE → start a new work session.
* **Single press** while in WORK → pause the session.
* **Single press** while paused (IDLE with saved time) → resume the session.
* **Long press (≥ 2 s)** → reset everything and return to IDLE.
* **Single press** while in a break → skip the break and return to IDLE.

LED feedback
------------
+-------------------+------------------------------------------+
| State             | LED colour                               |
+===================+==========================================+
| IDLE              | Soft white breathing                     |
+-------------------+------------------------------------------+
| WORK – good CO2   | Solid green                              |
+-------------------+------------------------------------------+
| WORK – moderate   | Solid yellow                             |
+-------------------+------------------------------------------+
| WORK – poor CO2   | Solid orange-red                         |
+-------------------+------------------------------------------+
| WORK – danger CO2 | Flashing red + buzzer                    |
+-------------------+------------------------------------------+
| Break             | Solid blue                               |
+-------------------+------------------------------------------+
| Session complete  | Brief purple flash then break colour     |
+-------------------+------------------------------------------+
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from . import config
from .buzzer import Buzzer
from .co2_sensor import CO2Sensor, CO2SensorError
from .focus_timer import FocusTimer, Phase
from .led_controller import LEDController

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# How long (seconds) the main loop sleeps between iterations.
_LOOP_INTERVAL_S: float = 0.25

# Long-press threshold in seconds.
_LONG_PRESS_S: float = 2.0


def _co2_colour(ppm: int) -> tuple[int, int, int]:
    """Map a CO2 reading to the appropriate LED colour."""
    if ppm < config.CO2_GOOD:
        return config.COLOUR_GOOD
    if ppm < config.CO2_MODERATE:
        return config.COLOUR_MODERATE
    if ppm < config.CO2_POOR:
        return config.COLOUR_POOR
    return config.COLOUR_DANGER


def _is_danger(ppm: int) -> bool:
    return ppm >= config.CO2_POOR


def run(mock: bool = False) -> None:
    """
    Entry point for the FocusSync device.

    Parameters
    ----------
    mock:
        When ``True``, all hardware is replaced with software mocks.
    """
    logger.info("FocusSync starting (mock=%s)", mock)

    with (
        CO2Sensor(
            port=config.CO2_SERIAL_PORT,
            baud_rate=config.CO2_BAUD_RATE,
            mock=mock,
        ) as sensor,
        LEDController(
            pin=config.LED_DATA_PIN,
            count=config.LED_COUNT,
            brightness=config.LED_BRIGHTNESS,
            mock=mock,
        ) as leds,
        Buzzer(pin=config.BUZZER_PIN, mock=mock) as buzzer,
    ):
        timer = FocusTimer()
        button = _ButtonMonitor(pin=config.BUTTON_PIN, mock=mock)

        # Show idle breathing animation on startup.
        leds.breathe(config.COLOUR_IDLE, cycles=1)

        last_co2_time: float = 0.0
        last_ppm: int = 400
        last_co2_colour = config.COLOUR_GOOD

        logger.info("FocusSync ready. Press the button to start a session.")

        try:
            while True:
                # ---- Button handling ----------------------------------------
                press = button.check()

                if press == "long":
                    _handle_long_press(timer, leds, buzzer)

                elif press == "short":
                    _handle_short_press(timer, leds, buzzer)

                # ---- Timer completion check ----------------------------------
                if timer.is_session_complete():
                    _handle_phase_complete(timer, leds, buzzer)

                # ---- Periodic CO2 reading ------------------------------------
                now = time.monotonic()
                if now - last_co2_time >= config.CO2_READ_INTERVAL_S:
                    last_co2_time = now
                    try:
                        last_ppm = sensor.read_ppm()
                        last_co2_colour = _co2_colour(last_ppm)
                        logger.info("CO2: %d ppm → %s", last_ppm, last_co2_colour)
                    except CO2SensorError as exc:
                        logger.warning("CO2 read error: %s", exc)

                # ---- Update LED based on current state ----------------------
                _update_leds(timer, leds, buzzer, last_ppm, last_co2_colour)

                time.sleep(_LOOP_INTERVAL_S)

        except KeyboardInterrupt:
            logger.info("FocusSync stopped by user")
        finally:
            leds.off()
            button.close()


# ---------------------------------------------------------------------------
# Phase transition helpers
# ---------------------------------------------------------------------------


def _handle_short_press(
    timer: FocusTimer,
    leds: LEDController,
    buzzer: Buzzer,
) -> None:
    phase = timer.phase

    if phase == Phase.IDLE:
        timer.start()
        buzzer.pattern_session_start()
        logger.info("Session started")

    elif phase == Phase.WORK:
        timer.pause()
        # Show breathing animation so the student gets visual confirmation
        # that the session is paused (non-blocking: 1 short cycle).
        leds.breathe(config.COLOUR_IDLE, cycles=1, period_s=1.5, step_s=0.05)
        logger.info("Session paused")

    elif phase in (Phase.SHORT_BREAK, Phase.LONG_BREAK):
        timer.advance()
        leds.set_colour(config.COLOUR_IDLE)
        logger.info("Break skipped, returning to IDLE")


def _handle_long_press(
    timer: FocusTimer,
    leds: LEDController,
    buzzer: Buzzer,
) -> None:
    timer.reset()
    leds.flash_colour(config.COLOUR_IDLE, flashes=3)
    logger.info("Timer reset via long press")


def _handle_phase_complete(
    timer: FocusTimer,
    leds: LEDController,
    buzzer: Buzzer,
) -> None:
    phase = timer.phase

    if phase == Phase.WORK:
        buzzer.pattern_session_end()
        leds.flash_colour(config.COLOUR_SESSION_END, flashes=3)
        timer.advance()
        leds.set_colour(config.COLOUR_BREAK)
        logger.info("Work session complete → break")

    elif phase in (Phase.SHORT_BREAK, Phase.LONG_BREAK):
        buzzer.pattern_break_end()
        timer.advance()
        leds.set_colour(config.COLOUR_IDLE)
        logger.info("Break complete → IDLE")


def _update_leds(
    timer: FocusTimer,
    leds: LEDController,
    buzzer: Buzzer,
    ppm: int,
    co2_colour: tuple[int, int, int],
) -> None:
    phase = timer.phase

    if phase == Phase.IDLE:
        pass  # breathing is triggered on transition; no continuous update needed

    elif phase == Phase.WORK:
        if _is_danger(ppm):
            leds.flash_danger(flashes=1, on_s=0.1, off_s=0.1)
            buzzer.pattern_danger()
        else:
            leds.set_colour(co2_colour)

    elif phase in (Phase.SHORT_BREAK, Phase.LONG_BREAK):
        leds.set_colour(config.COLOUR_BREAK)


# ---------------------------------------------------------------------------
# Button monitor (with GPIO mock)
# ---------------------------------------------------------------------------


class _ButtonMonitor:
    """
    Detects single and long presses on a physical push button.

    Returns
    -------
    ``"short"`` / ``"long"`` / ``None`` on each call to :py:meth:`check`.
    """

    def __init__(self, pin: int, mock: bool = False) -> None:
        self._mock = mock
        self._pin = pin
        self._gpio: object = None
        self._press_start: float | None = None

        if not mock:
            try:
                import RPi.GPIO as GPIO  # type: ignore[import-untyped]

                GPIO.setmode(GPIO.BCM)
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                self._gpio = GPIO
                logger.info("Button initialised on BCM pin %d", pin)
            except Exception as exc:
                logger.warning("Button init failed: %s", exc)

    def check(self) -> str | None:
        """Poll the button and return the press type (or None)."""
        if self._mock:
            return None  # In mock mode no button events are generated

        if self._gpio is None:
            return None

        is_pressed = self._gpio.input(self._pin) == 0  # active-low

        now = time.monotonic()
        if is_pressed and self._press_start is None:
            self._press_start = now
        elif not is_pressed and self._press_start is not None:
            duration = now - self._press_start
            self._press_start = None
            if duration >= _LONG_PRESS_S:
                return "long"
            return "short"
        return None

    def close(self) -> None:
        if not self._mock and self._gpio is not None:
            try:
                self._gpio.cleanup(self._pin)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FocusSync – screen-free physical focus companion"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run with software mocks instead of real GPIO / sensor hardware",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(mock=args.mock)
