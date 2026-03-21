"""
Passive buzzer driver.

Generates simple tones via PWM on a GPIO pin.  A mock mode is provided
for development and testing on machines without GPIO hardware.

Usage
-----
    buzzer = Buzzer(pin=27)
    buzzer.beep(880, duration_ms=200)
    buzzer.pattern_session_start()
    buzzer.close()

    with Buzzer(mock=True) as b:
        b.pattern_session_end()
"""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


class Buzzer:
    """
    Controls a passive buzzer via GPIO PWM.

    Parameters
    ----------
    pin:
        GPIO (BCM) pin number connected to the buzzer.
    mock:
        When ``True``, no hardware library is required; tone events
        are logged instead of played.
    """

    def __init__(self, pin: int = 27, *, mock: bool = False) -> None:
        self._pin = pin
        self._mock = mock
        self._pwm: object = None

        if not mock:
            self._init_hardware(pin)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def beep(self, frequency_hz: int = 880, duration_ms: int = 200) -> None:
        """
        Play a single tone.

        Parameters
        ----------
        frequency_hz:
            Tone frequency in hertz.
        duration_ms:
            Duration in milliseconds.
        """
        if self._mock:
            logger.debug("Buzzer beep: %d Hz for %d ms", frequency_hz, duration_ms)
            return
        try:
            self._pwm.ChangeFrequency(frequency_hz)  # type: ignore[union-attr]
            self._pwm.start(50)  # type: ignore[union-attr]
            time.sleep(duration_ms / 1000.0)
            self._pwm.stop()  # type: ignore[union-attr]
        except Exception as exc:
            logger.warning("Buzzer beep failed: %s", exc)

    def pattern_session_start(self) -> None:
        """Two short ascending beeps – focus session starting."""
        self.beep(660, 150)
        time.sleep(0.05)
        self.beep(880, 250)

    def pattern_session_end(self) -> None:
        """Two short descending beeps – focus session complete."""
        self.beep(880, 150)
        time.sleep(0.05)
        self.beep(660, 300)

    def pattern_break_end(self) -> None:
        """Three quick beeps – break over, time to work."""
        for _ in range(3):
            self.beep(880, 100)
            time.sleep(0.08)

    def pattern_danger(self) -> None:
        """Rapid alternating tones – CO2 danger level."""
        for _ in range(4):
            self.beep(1_000, 150)
            time.sleep(0.05)
            self.beep(800, 150)
            time.sleep(0.05)

    def close(self) -> None:
        """Stop PWM and clean up GPIO."""
        if not self._mock and self._pwm is not None:
            try:
                self._pwm.stop()  # type: ignore[union-attr]
                import RPi.GPIO as GPIO  # type: ignore[import-untyped]

                GPIO.cleanup(self._pin)
            except Exception:
                pass
        logger.info("Buzzer closed")

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "Buzzer":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_hardware(self, pin: int) -> None:
        try:
            import RPi.GPIO as GPIO  # type: ignore[import-untyped]

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            self._pwm = GPIO.PWM(pin, 440)
            logger.info("Buzzer initialised on BCM pin %d", pin)
        except Exception as exc:
            raise RuntimeError(
                f"Cannot initialise buzzer on pin {pin}: {exc}"
            ) from exc
