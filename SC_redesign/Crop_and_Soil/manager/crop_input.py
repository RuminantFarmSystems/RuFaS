from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, List, Tuple
from collections.abc import Sequence

from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies
from SC_redesign.Crop_and_Soil.field.harvest_operations import HarvestOperation


@dataclass(kw_only=True)
class CropScheduleSpec:
    """This class specifies a crop management schedule, to be used by the field manager to plant (initialize) and
    harvest crops at the appropriate times"""

    # TODO: This class does not yet handle heat-scheduling specifications.

    crop_reference: float = "corn"
    """A reference to the crop to be planted. Either the name of one of supported `CropSpecies` or a reference to the
    name of a custom, user-specified crop"""
    planting_years: int | Sequence[int] = (1, 2, 3)
    """the years during which the crop should be planted. For each value, a new crop will be initialized"""
    planting_days: int | Sequence[int] = 120
    """the (Julian) day on which the crop should be planted. If a single value is given, it will be repeated for
    all years. Otherwise, there should be one value for each value in `planting_years`."""
    harvest_years: int | Sequence[int] = (1, 2, 3)
    """the years during which the crop should undergo a harvest operation"""
    harvest_days: int | Sequence[int] | Sequence[Sequence[int]] = 220
    """the (Julian) day on which the crop should be harvested. If a single value/element is given, it will be repeated
    for all harvest years. Otherwise, there must be one element for each present in `harvest_years`. If multiple
    harvests can occur for the same crop instance, the corresponding element should be a list whose elements correspond.
    to separate harvest events"""
    harvest_operations: str | Sequence[str] = "default"
    """the harvest operation that should occur. If a single value is given, it will be repeated for all harvests.
    Otherwise, the structure/dimensions should correspond to those of `harvest_days`."""
    pattern_skip: Optional[int] = None
    """the number of years to wait before repeating the pattern"""
    pattern_repeat: Optional[int] = None
    """the number of times the specified crop management pattern should be repeated"""
    uses_custom_crop: bool = False
    """status variable that indicates whether the `crop_references` refers to a custom (user-defined) crop instead of
    on of the supported crop species."""

    @staticmethod
    def _convert_to_tuple(x: Any):
        """converts an input into a tuple

        If input is an iterable, it converts it into a tuple, otherwise it is encapsulated in a list and then converted
        into a tuple.

        Parameters
        ----------
        x : any
            the variable to be converted to a tuple

        Returns
        -------
            the input variable as a tuple
        """
        if hasattr(x, "__iter__") and type(x) is not str:
            return tuple(x)

        return tuple([x])

    def __post_init__(self):
        if self.crop_reference in CropSpecies.__members__:
            self.uses_custom_crop = False
        else:
            self.uses_custom_crop = True

        # convert attributes to tuples, no matter the length of the input
        self.planting_years = self._convert_to_tuple(self.planting_years)
        self.planting_days: Tuple[int] = self._convert_to_tuple(self.planting_days)
        self.harvest_years = self._convert_to_tuple(self.harvest_years)
        self.harvest_days: Tuple[int] = self._convert_to_tuple(self.harvest_days)
        self.harvest_operations = self._convert_to_tuple(self.harvest_operations)
        new_ops: List[Any] = [HarvestOperation(op) for op in self.harvest_operations]
        self.harvest_operations = tuple(new_ops)

        # expand single-length inputs to match full sequence
        if len(self.planting_days) == 1:
            self.planting_days *= len(self.planting_years)
        if len(self.harvest_days) == 1:
            self.harvest_days *= len(self.harvest_years)
        if len(self.harvest_operations) == 1:
            self.harvest_operations *= len(self.harvest_years)

        # input validation
        if len(self.planting_years) != len(self.harvest_years):
            raise Exception("planting_years must be the same length as harvest_years")
        if len(self.planting_days) != len(self.planting_years):
            raise Exception("planting_days must be either length 1 or the same length as planting_years")
        if len(self.harvest_days) != len(self.harvest_years):
            raise Exception("harvest_days must either be length 1 or the same length as harvest_years")
        if len(self.harvest_operations) != len(self.harvest_years):
            raise Exception("harvest_operations must be either length 1 or the same length of harvest_years")

        # expand further if the pattern repeats
        if self.pattern_repeat is None or self.pattern_repeat <= 0:
            return
        self.pattern_skip = self.pattern_skip or 0  # set skip to 0 if None
        self.planting_years = tuple(repeat_pattern(self.planting_years, self.pattern_skip, self.pattern_repeat))
        self.planting_days = tuple(self.planting_days * (self.pattern_repeat + 1))
        self.harvest_years = tuple(repeat_pattern(self.harvest_years, self.pattern_skip, self.pattern_repeat))
        self.harvest_days = tuple(self.harvest_days * (self.pattern_repeat + 1))
        self.harvest_operations = tuple(self.harvest_operations * (self.pattern_repeat + 1))

    def make_from_dict(self, dictionary: dict):
        pass

    def make_from_json(self, file: Path):
        pass

    def make_from_tabular(self, file: Path, extension: Optional[str] = None):
        pass


def repeat_pattern(pattern: Sequence[int] = (1, 2, 5), skip: int = 2, repeat: int = 2) -> List[int]:
    """projects a sequence of integers forward, based on a repeat pattern

    The obvious use case for this function is to build temporal patterns forward through time.

    Parameters
    ----------
    pattern : list[int] | tuple[int]
        a sequence of numbers that establishes the pattern
    skip : int
        the number of integers to skip before restarting the pattern. Positive values will ascend to the next piece
        while negative values will descend.
    repeat :
        the number of times the pattern should be repeated

    Returns
    -------
    sequence : list[int]
        the full resulting sequence of numbers
    """
    out = list(pattern)
    span = max(pattern) - min(pattern)
    for i in range(repeat):
        new = [x + ((i+1)*span) + (1+i)*(skip+1) for x in pattern]
        out = out + new
    return out
