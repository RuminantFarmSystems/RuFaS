"""Single home for all female-calf retention logic (keep vs. sell).

Two user-selectable methods are supported (see issue #3055 and the design doc):

* ``"rate"`` (Option 1, the historical default): each live female calf is kept with
  probability :attr:`AnimalConfig.keep_female_calf_rate`.
* ``"count"`` (Option 2): the user specifies a target number of female calves to keep
  per year (:attr:`AnimalConfig.keep_female_calf_num_annual`). That target is spread
  evenly across the simulation year as "keep tags"; each live female calf born consumes
  an outstanding tag and is kept, otherwise it is sold. Tags left unfulfilled at year
  end trigger a warning.

Consolidating both methods here is deliberate. The keep/sell decision previously lived
inside ``Animal._initialize_newborn_calf`` with no access to herd-level, per-year state,
which made the count-based option impossible to express. Owning the decision (and the
annual schedule) in one place lets ``HerdManager`` drive it and makes the logic
unit-testable in isolation.
"""

from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.util import Utility

if TYPE_CHECKING:
    from RUFAS.biophysical.animal.animal import Animal

RETENTION_METHOD_RATE = "rate"
RETENTION_METHOD_COUNT = "count"

UNFULFILLED_TAG_ERROR_FRACTION = 0.20


class CalfRetentionPolicy:
    """Decide whether each newborn female calf is kept on-farm or sold.

    A single instance is owned by :class:`HerdManager` for the live simulation. The
    rate-based decision is also exposed as a class method for herd initialization
    (spin-up), where the simulation clock does not advance.

    Attributes
    ----------
    om : OutputManager
        Used to emit the year-end "insufficient female calves" warning (count method).

    """

    def __init__(self) -> None:
        self.om = OutputManager()
        self._scheduled_year: int | None = None
        self._daily_tag_release: dict[int, int] = {}
        self._outstanding_tags: int = 0
        self._target_tags_this_year: int = 0
        self._tags_fulfilled_this_year: int = 0

    @property
    def is_count_based(self) -> bool:
        """Whether the count-based (Option 2) method is selected."""
        return AnimalConfig.calf_retention_method == RETENTION_METHOD_COUNT

    def begin_day(self, time: RufasTime) -> None:
        """Release the keep tags scheduled for the current day (count method only).

        Parameters
        ----------
        time : RufasTime
            Current simulation time. Used to detect year rollovers and to look up the
            current Julian day in the annual schedule.

        Notes
        -----
        Must be called once per simulation day *before* births are processed, so that
        tags released today are available to calves born today.

        """
        if not self.is_count_based:
            return
        if self._scheduled_year != time.current_simulation_year:
            self._start_new_year(time)
        self._outstanding_tags += self._daily_tag_release.get(time.current_julian_day, 0)

    def finalize_day(self, time: RufasTime) -> None:
        """
        Run the year-end keep-target check on the last day of a simulation year (count method).

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Raises
        ------
        RuntimeError
            If at least ``UNFULFILLED_TAG_ERROR_FRACTION`` of the annual target went
            unfulfilled (the simulation is stopped).

        Notes
        -----
        Must be called once per simulation day *after* births are processed, so that
        calves born on the final day have already had a chance to fulfill tags.

        """
        if not self.is_count_based:
            return
        if time.current_julian_day == time.year_end_day:
            self._check_year_end_target(time)

    def apply(self, calf: "Animal", simulation_day: int) -> None:
        """Apply the configured retention decision to a newborn calf.

        Sets ``calf.sold_at_day`` when the calf is not kept; leaves it untouched (``None``)
        when the calf is kept.

        Parameters
        ----------
        calf : Animal
            The freshly created newborn calf (sex and stillborn status already assigned).
        simulation_day : int
            The current simulation day, recorded as the sale day when the calf is sold.
        """
        is_sold = self._is_sold_count_based(calf) if self.is_count_based else self._is_sold_rate_based(calf)
        if is_sold:
            calf.sold_at_day = simulation_day

    @classmethod
    def apply_rate_based(cls, calf: "Animal", simulation_day: int) -> None:
        """Apply rate-based (Option 1) retention regardless of the configured method.

        Used during herd initialization (spin-up). The spin-up clock does not advance, so
        the count-based annual schedule cannot be built there; the initial herd is instead
        stocked with the historical rate-based behavior, and the count-based target then
        governs intake once the main simulation begins.

        Parameters
        ----------
        calf : Animal
            The freshly created newborn calf.
        simulation_day : int
            The current simulation day, recorded as the sale day when the calf is sold.

        """
        if cls._is_sold_rate_based(calf):
            calf.sold_at_day = simulation_day

    @staticmethod
    def _is_sold_rate_based(calf: "Animal") -> bool:
        """
        Option 1: sell males; keep each live female with probability keep_female_calf_rate.

        Notes
        -----
        A ``random()`` draw is taken for every non-male calf, matching the original logic so
        the global RNG stream -- and therefore reproducibility of existing rate-based runs --
        is preserved.

        """
        return calf.sex == Sex.MALE or random() > AnimalConfig.keep_female_calf_rate

    def _is_sold_count_based(self, calf: "Animal") -> bool:
        """Option 2: keep a live female calf only if an outstanding keep tag is available."""
        if calf.sex == Sex.MALE or calf.stillborn:
            return True
        if self._outstanding_tags > 0:
            self._outstanding_tags -= 1
            self._tags_fulfilled_this_year += 1
            return False
        return True

    def _start_new_year(self, time: RufasTime) -> None:
        """Rebuild the keep-tag schedule and reset the ledger for a new simulation year."""
        self._scheduled_year = time.current_simulation_year
        self._daily_tag_release = self._build_year_schedule(time)
        self._target_tags_this_year = sum(self._daily_tag_release.values())
        self._outstanding_tags = 0
        self._tags_fulfilled_this_year = 0

    @staticmethod
    def _build_year_schedule(time: RufasTime) -> dict[int, int]:
        """Spread the annual keep target evenly across the simulated days of the current year.

        Returns a mapping of Julian day -> number of keep tags released that day. The annual
        target is prorated for partial first/last simulation years (a half-year of operation
        keeps roughly half the annual target). Tags are distributed deterministically with a
        cumulative-floor (Bresenham-style) sweep, so the schedule sums exactly to the
        (prorated) target and never depends on the RNG.

        Notes
        -----
        The design doc suggests randomly rounding the ``days / target`` spacing. A
        deterministic even spread is used instead for reproducibility and testability (the
        codebase has known PYTHONHASHSEED-sensitive behavior). The temporal distribution is
        equivalent in aggregate; this choice is flagged for SME review.

        """
        target_annual = AnimalConfig.keep_female_calf_num_annual
        start_day = time.year_start_day
        end_day = time.year_end_day
        days_available = end_day - start_day + 1
        if target_annual <= 0 or days_available <= 0:
            return {}

        full_year_length = (
            GeneralConstants.LEAP_YEAR_LENGTH
            if Utility.is_leap_year(time.current_calendar_year)
            else GeneralConstants.YEAR_LENGTH
        )
        target = round(target_annual * days_available / full_year_length)

        schedule: dict[int, int] = {}
        for offset in range(days_available):
            tags_today = (target * (offset + 1)) // days_available - (target * offset) // days_available
            if tags_today:
                schedule[start_day + offset] = tags_today
        return schedule

    def _check_year_end_target(self, time: RufasTime) -> None:
        """
        React to keep tags left unfulfilled by the count-based target at year end.

        Any leftover tags emit a warning. A shortfall of at least
        ``UNFULFILLED_TAG_ERROR_FRACTION`` of the annual target raises a ``RuntimeError``,
        stopping the simulation so the user can adjust inputs (the female-calf supply cannot
        meet the requested target).

        Parameters
        ----------
        time : RufasTime
            Current simulation time.

        Raises
        ------
        RuntimeError
            If the unfulfilled fraction reaches ``UNFULFILLED_TAG_ERROR_FRACTION``.

        """
        unfulfilled = self._outstanding_tags
        if unfulfilled <= 0:
            return

        info_map = {
            "class": self.__class__.__name__,
            "function": self._check_year_end_target.__name__,
            "simulation_day": time.simulation_day,
        }
        shortfall = (
            f"Simulation year {time.current_simulation_year}: {unfulfilled} of "
            f"{self._target_tags_this_year} female-calf keep tags went unfulfilled "
            f"(kept {self._tags_fulfilled_this_year}). Fewer female calves were kept than the "
            f"target keep_female_calf_num_annual={AnimalConfig.keep_female_calf_num_annual}."
        )

        if unfulfilled >= self._target_tags_this_year * UNFULFILLED_TAG_ERROR_FRACTION:
            message = (
                f"{shortfall} At least {round(UNFULFILLED_TAG_ERROR_FRACTION * 100)}% of the annual "
                "target could not be met, so the simulation is stopped. Increase the number of "
                "female calves born (for example, lower the male calf rate or use sexed semen) or "
                "lower keep_female_calf_num_annual. To avoid this error, use the 'rate' retention method."
            )
            self.om.add_error("Female-calf keep target unreachable", message, info_map)
            raise RuntimeError(message)

        self.om.add_warning(
            "Insufficient female calves to meet keep target",
            f"{shortfall} Consider lowering the male calf rate to increase the number of female calves born.",
            info_map,
        )
