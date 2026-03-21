"""
MH-Z19B CO2 sensor driver.

The MH-Z19B communicates over UART using a simple 9-byte request/response
protocol.  This module wraps that protocol and adds a software mock so that
the rest of the code base (and tests) can run without physical hardware.

Usage
-----
    sensor = CO2Sensor()          # real hardware
    sensor = CO2Sensor(mock=True) # returns synthetic values
    ppm = sensor.read_ppm()
    sensor.close()

    # Or use as a context manager:
    with CO2Sensor() as sensor:
        ppm = sensor.read_ppm()
"""

from __future__ import annotations

import logging
import struct
import time
from typing import Optional

logger = logging.getLogger(__name__)

# MH-Z19B UART command bytes
_CMD_READ_CO2 = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
_RESPONSE_LEN = 9


def _checksum(data: bytes) -> int:
    """Compute the MH-Z19B single-byte checksum."""
    return (~sum(data[1:8]) + 1) & 0xFF


class CO2SensorError(Exception):
    """Raised when a valid reading cannot be obtained from the sensor."""


class CO2Sensor:
    """
    Driver for the MH-Z19B NDIR CO2 sensor.

    Parameters
    ----------
    port:
        Serial port path (e.g. ``"/dev/ttyS0"``).  Ignored in mock mode.
    baud_rate:
        UART baud rate (default 9600).  Ignored in mock mode.
    mock:
        When ``True`` no serial hardware is required; ``read_ppm`` returns
        a synthetic value that slowly climbs over time to simulate a
        worsening room environment.
    """

    def __init__(
        self,
        port: str = "/dev/ttyS0",
        baud_rate: int = 9_600,
        *,
        mock: bool = False,
    ) -> None:
        self._mock = mock
        self._serial: Optional[object] = None
        self._mock_ppm: float = 450.0   # starting value for simulation
        self._mock_start: float = time.monotonic()

        if not mock:
            try:
                import serial  # type: ignore[import-untyped]

                self._serial = serial.Serial(
                    port,
                    baud_rate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=2,
                )
                logger.info("CO2Sensor opened %s at %d baud", port, baud_rate)
            except Exception as exc:
                raise CO2SensorError(
                    f"Cannot open CO2 sensor on {port}: {exc}"
                ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read_ppm(self) -> int:
        """
        Return the current CO2 concentration in parts per million (ppm).

        Raises
        ------
        CO2SensorError
            If the sensor returns an invalid or corrupt response.
        """
        if self._mock:
            return self._mock_read()
        return self._hardware_read()

    def close(self) -> None:
        """Release the serial port."""
        if self._serial is not None:
            try:
                self._serial.close()  # type: ignore[union-attr]
            except Exception:
                pass
            self._serial = None
            logger.info("CO2Sensor serial port closed")

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "CO2Sensor":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _hardware_read(self) -> int:
        """Send the read command and parse the 9-byte UART response."""
        assert self._serial is not None
        self._serial.write(_CMD_READ_CO2)  # type: ignore[union-attr]
        response = self._serial.read(_RESPONSE_LEN)  # type: ignore[union-attr]

        if len(response) != _RESPONSE_LEN:
            raise CO2SensorError(
                f"Short response from sensor: {len(response)}/{_RESPONSE_LEN} bytes"
            )
        if response[0] != 0xFF or response[1] != 0x86:
            raise CO2SensorError(
                f"Unexpected response header: {response[0]:02X} {response[1]:02X}"
            )
        expected_crc = _checksum(response)
        if response[8] != expected_crc:
            raise CO2SensorError(
                f"CRC mismatch: got {response[8]:02X}, expected {expected_crc:02X}"
            )

        high, low = response[2], response[3]
        ppm = (high << 8) | low
        logger.debug("CO2 reading: %d ppm", ppm)
        return ppm

    def _mock_read(self) -> int:
        """
        Return a simulated CO2 value.

        Starts at ~450 ppm (typical outdoor level) and increases by ~5 ppm per
        minute to mimic a student working in a confined space.  A small
        sinusoidal variation (±20 ppm, period ~12 min) is added for realism.
        """
        import math

        _MOCK_BASELINE_PPM = 450       # starting concentration (ppm)
        _MOCK_INCREASE_PER_MIN = 5     # linear rise rate (ppm per minute)
        _MOCK_VARIATION_AMPLITUDE = 20 # sinusoidal noise amplitude (ppm)
        _MOCK_VARIATION_FREQ = 0.5     # angular frequency of noise oscillation

        elapsed_min = (time.monotonic() - self._mock_start) / 60.0
        ppm = (
            _MOCK_BASELINE_PPM
            + elapsed_min * _MOCK_INCREASE_PER_MIN
            + _MOCK_VARIATION_AMPLITUDE * math.sin(elapsed_min * _MOCK_VARIATION_FREQ)
        )
        result = max(350, int(ppm))
        logger.debug("CO2 mock reading: %d ppm", result)
        return result
