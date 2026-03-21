"""
Pomodoro-style focus timer.

Manages the sequence of work sessions and breaks that make up a
Pomodoro cycle.  The timer is intentionally decoupled from any
hardware so that it can be tested on any Python environment.

State machine
-------------

    IDLE ──(start)──► WORK ──(finish/pause)──► BREAK
                        ▲                         │
                        └────────(resume)─────────┘

After ``SESSIONS_BEFORE_LONG_BREAK`` completed work sessions the next
break becomes a long break.

Usage
-----
    timer = FocusTimer()
    timer.start()
    ...
    remaining = timer.remaining_seconds()
    if timer.is_session_complete():
        timer.advance()   # move to next break / work phase
"""

from __future__ import annotations

import logging
import time
from enum import Enum, auto

from . import config

logger = logging.getLogger(__name__)


class Phase(Enum):
    IDLE = auto()
    WORK = auto()
    SHORT_BREAK = auto()
    LONG_BREAK = auto()


class FocusTimer:
    """
    Pomodoro-style timer that cycles through work and break phases.

    Parameters
    ----------
    work_duration_s:
        Length of a work session in seconds (default 25 min).
    short_break_s:
        Length of a short break in seconds (default 5 min).
    long_break_s:
        Length of a long break in seconds (default 15 min).
    sessions_before_long_break:
        Number of completed work sessions before a long break is awarded.
    """

    def __init__(
        self,
        work_duration_s: int = config.WORK_DURATION_S,
        short_break_s: int = config.SHORT_BREAK_S,
        long_break_s: int = config.LONG_BREAK_S,
        sessions_before_long_break: int = config.SESSIONS_BEFORE_LONG_BREAK,
    ) -> None:
        self._work_duration_s = work_duration_s
        self._short_break_s = short_break_s
        self._long_break_s = long_break_s
        self._sessions_before_long = sessions_before_long_break

        self._phase: Phase = Phase.IDLE
        self._start_time: float = 0.0
        self._duration_s: float = 0.0
        self._completed_sessions: int = 0
        self._paused_remaining: float | None = None

    # ------------------------------------------------------------------
    # Phase control
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin a new work session (or resume if paused)."""
        if self._paused_remaining is not None:
            # Resume from pause: preserve fractional seconds to avoid
            # accumulating rounding errors across multiple pause/resume cycles.
            self._duration_s = self._paused_remaining
            self._paused_remaining = None
        else:
            self._duration_s = self._work_duration_s
        self._phase = Phase.WORK
        self._start_time = time.monotonic()
        logger.info(
            "FocusTimer: WORK session started (%d s) – session #%d",
            self._duration_s,
            self._completed_sessions + 1,
        )

    def pause(self) -> None:
        """Pause the current work session (no effect during a break)."""
        if self._phase == Phase.WORK:
            self._paused_remaining = max(0.0, self.remaining_seconds())
            self._phase = Phase.IDLE
            logger.info(
                "FocusTimer: paused with %.0f s remaining", self._paused_remaining
            )

    def advance(self) -> Phase:
        """
        Move to the next phase.

        - If currently in WORK → move to appropriate break.
        - If currently in a break → move to IDLE (ready for next session).
        Returns the new phase.
        """
        if self._phase == Phase.WORK:
            self._completed_sessions += 1
            if self._completed_sessions % self._sessions_before_long == 0:
                self._phase = Phase.LONG_BREAK
                self._duration_s = self._long_break_s
            else:
                self._phase = Phase.SHORT_BREAK
                self._duration_s = self._short_break_s
            self._start_time = time.monotonic()
            self._paused_remaining = None
            logger.info(
                "FocusTimer: session %d complete → %s",
                self._completed_sessions,
                self._phase.name,
            )
        elif self._phase in (Phase.SHORT_BREAK, Phase.LONG_BREAK):
            self._phase = Phase.IDLE
            self._duration_s = 0
            logger.info("FocusTimer: break complete → IDLE")
        return self._phase

    def reset(self) -> None:
        """Reset timer to IDLE, clearing all session history."""
        self._phase = Phase.IDLE
        self._start_time = 0.0
        self._duration_s = 0
        self._completed_sessions = 0
        self._paused_remaining = None
        logger.info("FocusTimer: reset")

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    @property
    def phase(self) -> Phase:
        """Current phase of the timer."""
        return self._phase

    @property
    def completed_sessions(self) -> int:
        """Total number of completed work sessions since reset."""
        return self._completed_sessions

    def remaining_seconds(self) -> float:
        """
        Seconds remaining in the current phase.

        Returns 0.0 if the phase is IDLE.
        """
        if self._phase == Phase.IDLE:
            return 0.0
        elapsed = time.monotonic() - self._start_time
        return max(0.0, self._duration_s - elapsed)

    def is_session_complete(self) -> bool:
        """Return True when the current phase has expired."""
        if self._phase == Phase.IDLE:
            return False
        return self.remaining_seconds() <= 0.0

    def progress_fraction(self) -> float:
        """
        Return the fraction of the current phase that has elapsed (0.0–1.0).

        Returns 0.0 when IDLE.
        """
        if self._phase == Phase.IDLE or self._duration_s == 0:
            return 0.0
        elapsed = self._duration_s - self.remaining_seconds()
        return min(1.0, elapsed / self._duration_s)

    def format_remaining(self) -> str:
        """Return remaining time formatted as ``MM:SS``."""
        total = int(self.remaining_seconds())
        minutes, seconds = divmod(total, 60)
        return f"{minutes:02d}:{seconds:02d}"
