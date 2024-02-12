from enum import Enum


class TractorSize(Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class TractorSpecs:
    def __init__(self, tractor_size: TractorSize | None, herd_size: int | None) -> None:
        if not tractor_size and not herd_size:
            raise ValueError(
                "At least one of `tractor_size` or `herd_size` must be given."
            )
        self.tractor_size = tractor_size or self.herd_size_to_tractor_size(herd_size)

    def herd_size_to_tractor_size(self, herd_size: int) -> TractorSize:
        "Assign a Tractor Size based on number of cows"
        if herd_size < 0:
            raise ValueError("Herd size must be a positive integer.")
        if herd_size < 500:
            return TractorSize.SMALL
        elif herd_size < 2000:
            return TractorSize.MEDIUM
        else:
            return TractorSize.LARGE

    @property
    def PTO_kw(self) -> float:
        # TODO get these values from IM
        """Constants 589, 592, 595 in EEE Functions file"""
        pto_mapping = {
            TractorSize.SMALL: 55.93,
            TractorSize.MEDIUM: 208.42,
            TractorSize.LARGE: 328.11,
        }
        return pto_mapping[self.tractor_size]

    @property
    def power_available_kw(self) -> float:
        """Constants 590, 593, 596 in EEE Functions file, calculated bsaed on PTO"""
        return self.PTO_kw / 1.4

    @property
    def mass_kg(self) -> float:
        # TODO get these values from IM
        """Constants 591, 594, 597 in EEE Functions file"""
        mass_mapping = {
            TractorSize.SMALL: 8_400.0,
            TractorSize.MEDIUM: 12_700.0,
            TractorSize.LARGE: 20_856.0,
        }
        return mass_mapping[self.tractor_size]

    @property
    def speed_km_hr(self) -> float:
        # TODO get these values from IM
        """Constant 598 in EEE Functions file"""
        return 10.0
