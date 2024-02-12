from enum import Enum


class TractorSize(Enum):
    """
    Enum for Tractor Sizes.
    """

    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class TractorSpecs:
    def __init__(self, tractor_size: TractorSize | None, herd_size: int | None) -> None:
        if tractor_size:
            self.tractor_size = tractor_size
        elif herd_size:
            self.tractor_size = self.herd_size_to_tractor_size(herd_size)
        else:
            raise ValueError(
                "At least one of `tractor_size` or `herd_size` has to be given."
            )

    def herd_size_to_tractor_size(self, herd_size: int) -> TractorSize:
        "Assign a Tractor Size based on number of cows"
        if herd_size < 500:
            return TractorSize.SMALL
        if herd_size < 2000:
            return TractorSize.MEDIUM
        return TractorSize.LARGE

    @property
    def PTO_kw(self) -> float:
        # TODO get these values from IM
        """Constants 589, 592, 595 in EEE Functions file"""
        if self.tractor_size == TractorSize.SMALL:
            return 55.93
        if self.tractor_size == TractorSize.MEDIUM:
            return 208.42
        if self.tractor_size == TractorSize.LARGE:
            return 328.11

    @property
    def power_available_kw(self) -> float:
        """Constants 590, 593, 596 in EEE Functions file, calculated bsaed on PTO"""
        return self.PTO_kw / 1.4

    @property
    def mass_kg(self) -> float:
        # TODO get these values from IM
        """Constants 591, 594, 597 in EEE Functions file"""
        if self.tractor_size == TractorSize.SMALL:
            return 8_400.0
        if self.tractor_size == TractorSize.MEDIUM:
            return 12_700.0
        if self.tractor_size == TractorSize.LARGE:
            return 20_856.0
