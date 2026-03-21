"""Tests for main.py helper functions (mock mode, no hardware required)."""

import unittest

from firmware import config
from firmware.main import _co2_colour, _is_danger


class TestCO2ColourMapping(unittest.TestCase):
    def test_below_good_threshold_is_green(self) -> None:
        colour = _co2_colour(config.CO2_GOOD - 1)
        self.assertEqual(colour, config.COLOUR_GOOD)

    def test_moderate_range_is_yellow(self) -> None:
        colour = _co2_colour(config.CO2_GOOD)
        self.assertEqual(colour, config.COLOUR_MODERATE)

    def test_poor_range_is_orange_red(self) -> None:
        colour = _co2_colour(config.CO2_MODERATE)
        self.assertEqual(colour, config.COLOUR_POOR)

    def test_danger_range_is_red(self) -> None:
        colour = _co2_colour(config.CO2_POOR)
        self.assertEqual(colour, config.COLOUR_DANGER)

    def test_above_danger_threshold_is_red(self) -> None:
        colour = _co2_colour(config.CO2_POOR + 500)
        self.assertEqual(colour, config.COLOUR_DANGER)


class TestIsDanger(unittest.TestCase):
    def test_below_poor_threshold_is_not_danger(self) -> None:
        self.assertFalse(_is_danger(config.CO2_POOR - 1))

    def test_at_poor_threshold_is_danger(self) -> None:
        self.assertTrue(_is_danger(config.CO2_POOR))

    def test_above_poor_threshold_is_danger(self) -> None:
        self.assertTrue(_is_danger(config.CO2_POOR + 100))
