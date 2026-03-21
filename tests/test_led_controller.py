"""Tests for the LED controller mock mode."""

import time
import unittest

from firmware.led_controller import LEDController


class TestLEDControllerMock(unittest.TestCase):
    def setUp(self) -> None:
        self.leds = LEDController(mock=True)

    def tearDown(self) -> None:
        self.leds.close()

    def test_set_colour_stores_current_colour(self) -> None:
        self.leds.set_colour((0, 200, 0))
        self.assertEqual(self.leds.get_current_colour(), (0, 200, 0))

    def test_off_sets_colour_to_black(self) -> None:
        self.leds.set_colour((100, 100, 100))
        self.leds.off()
        self.assertEqual(self.leds.get_current_colour(), (0, 0, 0))

    def test_flash_danger_ends_with_off(self) -> None:
        self.leds.flash_danger(flashes=2, on_s=0.01, off_s=0.01)
        self.assertEqual(self.leds.get_current_colour(), (0, 0, 0))

    def test_flash_colour_ends_with_off(self) -> None:
        self.leds.flash_colour((0, 0, 200), flashes=2, on_s=0.01, off_s=0.01)
        self.assertEqual(self.leds.get_current_colour(), (0, 0, 0))

    def test_breathe_ends_with_off(self) -> None:
        self.leds.breathe((80, 80, 80), cycles=1, period_s=0.1, step_s=0.01)
        self.assertEqual(self.leds.get_current_colour(), (0, 0, 0))

    def test_context_manager(self) -> None:
        with LEDController(mock=True) as leds:
            leds.set_colour((255, 0, 0))
            colour = leds.get_current_colour()
        self.assertEqual(colour, (255, 0, 0))

    def test_brightness_clipped_to_valid_range(self) -> None:
        # Should not raise even with out-of-range values
        leds_high = LEDController(brightness=2.0, mock=True)
        leds_low = LEDController(brightness=-1.0, mock=True)
        self.assertLessEqual(leds_high._brightness, 1.0)
        self.assertGreaterEqual(leds_low._brightness, 0.0)
        leds_high.close()
        leds_low.close()

    def test_scale_clips_to_255(self) -> None:
        leds = LEDController(brightness=1.0, mock=True)
        # With brightness=1.0 values above 255 should be clamped to 255.
        scaled = leds._scale((300, 300, 300))
        for channel in scaled:
            self.assertLessEqual(channel, 255)
            self.assertGreaterEqual(channel, 0)
        leds.close()

    def test_scale_does_not_go_below_zero(self) -> None:
        leds = LEDController(brightness=1.0, mock=True)
        scaled = leds._scale((0, 0, 0))
        self.assertEqual(scaled, (0, 0, 0))
        leds.close()
