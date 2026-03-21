"""
NeoPixel LED ring controller.

Provides a clean interface for setting the ring to a solid colour,
a breathing animation, or a danger-flash pattern.  A software mock
is included so that the module works on any machine that does not have
the ``rpi_ws281x`` / ``adafruit-circuitpython-neopixel`` library.

Usage
-----
    with LEDController() as leds:
        leds.set_colour((0, 200, 0))   # solid green
        leds.breathe((0, 80, 200))     # blue breathing animation (blocking)
        leds.flash_danger()            # red danger flash
        leds.off()
"""

from __future__ import annotations

import logging
import time
from typing import Tuple

logger = logging.getLogger(__name__)

Colour = Tuple[int, int, int]


class LEDController:
    """
    Controls a NeoPixel LED ring attached to a Raspberry Pi.

    Parameters
    ----------
    pin:
        GPIO (BCM) data pin number.
    count:
        Number of LEDs in the ring.
    brightness:
        Global brightness scale between 0.0 and 1.0.
    mock:
        When ``True``, no hardware library is required; LED state
        changes are simply logged.
    """

    def __init__(
        self,
        pin: int = 18,
        count: int = 12,
        brightness: float = 0.4,
        *,
        mock: bool = False,
    ) -> None:
        self._count = count
        self._brightness = max(0.0, min(1.0, brightness))
        self._mock = mock
        self._pixels: object = None
        self._current_colour: Colour = (0, 0, 0)

        if not mock:
            self._init_hardware(pin, count, brightness)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_colour(self, colour: Colour) -> None:
        """Fill every LED in the ring with *colour*."""
        self._current_colour = colour
        scaled = self._scale(colour)
        if self._mock:
            logger.debug("LED set_colour → RGB%s", scaled)
            return
        for i in range(self._count):
            self._pixels[i] = scaled  # type: ignore[index]
        self._pixels.show()  # type: ignore[union-attr]

    def off(self) -> None:
        """Turn all LEDs off."""
        self.set_colour((0, 0, 0))

    def breathe(
        self,
        colour: Colour,
        cycles: int = 1,
        period_s: float = 3.0,
        step_s: float = 0.05,
    ) -> None:
        """
        Run a smooth breathing animation.

        Parameters
        ----------
        colour:
            Peak colour of the breath.
        cycles:
            How many full in-out cycles to perform.
        period_s:
            Duration of one full cycle in seconds.
        step_s:
            Sleep between brightness steps (controls smoothness).
        """
        import math

        steps_per_cycle = max(1, int(period_s / step_s))
        for _ in range(cycles):
            for step in range(steps_per_cycle):
                phase = step / steps_per_cycle
                factor = 0.5 * (1 - math.cos(2 * math.pi * phase))
                faded: Colour = (
                    int(colour[0] * factor),
                    int(colour[1] * factor),
                    int(colour[2] * factor),
                )
                self.set_colour(faded)
                time.sleep(step_s)
        self.set_colour((0, 0, 0))

    def flash_danger(self, flashes: int = 6, on_s: float = 0.2, off_s: float = 0.2) -> None:
        """Flash the ring red to signal a CO2 danger level."""
        danger_red: Colour = (200, 0, 0)
        for _ in range(flashes):
            self.set_colour(danger_red)
            time.sleep(on_s)
            self.off()
            time.sleep(off_s)

    def flash_colour(
        self,
        colour: Colour,
        flashes: int = 3,
        on_s: float = 0.3,
        off_s: float = 0.2,
    ) -> None:
        """Flash the ring with an arbitrary colour."""
        for _ in range(flashes):
            self.set_colour(colour)
            time.sleep(on_s)
            self.off()
            time.sleep(off_s)

    def get_current_colour(self) -> Colour:
        """Return the colour most recently set (before brightness scaling)."""
        return self._current_colour

    def close(self) -> None:
        """Release hardware resources."""
        self.off()
        if not self._mock and self._pixels is not None:
            try:
                self._pixels.deinit()  # type: ignore[union-attr]
            except Exception:
                pass
        logger.info("LEDController closed")

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "LEDController":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_hardware(self, pin: int, count: int, brightness: float) -> None:
        try:
            import board  # type: ignore[import-untyped]
            import neopixel  # type: ignore[import-untyped]

            board_pin = getattr(board, f"D{pin}")
            self._pixels = neopixel.NeoPixel(
                board_pin,
                count,
                brightness=brightness,
                auto_write=False,
                pixel_order=neopixel.GRB,
            )
            logger.info("LEDController initialised: %d LEDs on pin D%d", count, pin)
        except Exception as exc:
            raise RuntimeError(
                f"Cannot initialise NeoPixel ring on pin {pin}: {exc}"
            ) from exc

    def _scale(self, colour: Colour) -> Colour:
        """Apply global brightness to a colour tuple, clamping each channel to [0, 255]."""
        return (
            min(255, max(0, int(colour[0] * self._brightness))),
            min(255, max(0, int(colour[1] * self._brightness))),
            min(255, max(0, int(colour[2] * self._brightness))),
        )
