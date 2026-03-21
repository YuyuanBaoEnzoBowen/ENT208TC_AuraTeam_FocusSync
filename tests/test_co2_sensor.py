"""Tests for the CO2 sensor mock mode and checksum helper."""

import time
import unittest

from firmware.co2_sensor import CO2Sensor, CO2SensorError, _checksum


class TestChecksum(unittest.TestCase):
    def test_known_valid_response(self) -> None:
        # Example response from MH-Z19B datasheet for 0x03E8 (1000 ppm):
        # FF 86 03 E8 00 00 00 00 CRC
        data = bytes([0xFF, 0x86, 0x03, 0xE8, 0x00, 0x00, 0x00, 0x00, 0x00])
        crc = _checksum(data)
        # checksum = (~(0x86 + 0x03 + 0xE8) + 1) & 0xFF
        expected = (~(0x86 + 0x03 + 0xE8 + 0x00 + 0x00 + 0x00 + 0x00) + 1) & 0xFF
        self.assertEqual(crc, expected)

    def test_checksum_single_byte_sum(self) -> None:
        # Verify that the function only uses bytes [1:8]
        data = bytes([0xFF, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        expected = (~0x86 + 1) & 0xFF
        self.assertEqual(_checksum(data), expected)


class TestCO2SensorMock(unittest.TestCase):
    def setUp(self) -> None:
        self.sensor = CO2Sensor(mock=True)

    def tearDown(self) -> None:
        self.sensor.close()

    def test_returns_integer(self) -> None:
        ppm = self.sensor.read_ppm()
        self.assertIsInstance(ppm, int)

    def test_returns_positive_value(self) -> None:
        ppm = self.sensor.read_ppm()
        self.assertGreater(ppm, 0)

    def test_minimum_value_is_350(self) -> None:
        # The mock clamps at 350 ppm (below outdoor ambient is unrealistic).
        ppm = self.sensor.read_ppm()
        self.assertGreaterEqual(ppm, 350)

    def test_context_manager(self) -> None:
        with CO2Sensor(mock=True) as s:
            ppm = s.read_ppm()
        self.assertGreater(ppm, 0)

    def test_mock_increases_over_time(self) -> None:
        # The mock simulation increases ppm over time (student in room).
        # We monkeypatch _mock_start to simulate 60 minutes having passed.
        self.sensor._mock_start = time.monotonic() - 3600
        ppm_after_hour = self.sensor.read_ppm()
        # After 60 min at 5 ppm/min the reading should be well above 450.
        self.assertGreater(ppm_after_hour, 700)


class TestCO2SensorHardwareErrors(unittest.TestCase):
    def test_raises_on_bad_port(self) -> None:
        with self.assertRaises(CO2SensorError):
            CO2Sensor(port="/dev/nonexistent_port_xyz", mock=False)
