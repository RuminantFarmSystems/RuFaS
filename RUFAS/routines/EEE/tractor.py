from .tractor_implement import TractorImplement
from RUFAS.util import Utility
from RUFAS.input_manager import InputManager
from .enums import TractorSize

input_manager = InputManager()


class Tractor:
    """
    A class to represent the specifications of a tractor.
    The tractor's specifications are determined based on its size or the size of the herd it is intended to work with.
    """

    def __init__(self, tractor_size: TractorSize | None = None, herd_size: int | None = None) -> None:
        """
        Initializes the Tractor object with the tractor size or calculates it based on the provided herd size.
        If `tractor_size` is not provided, the size is inferred using the `herd_size` argument.

        Parameters
        ----------
        tractor_size : TractorSize | None, optional
            The size of the tractor as a `TractorSize` enum value.
        herd_size : int | None, optional
            The size of the herd to determine the tractor size if `tractor_size` is not provided.

        Raises
        ------
        ValueError
            If neither `tractor_size` nor `herd_size` is provided.
        """
        if not tractor_size and not herd_size:
            raise ValueError("At least one of `tractor_size` or `herd_size` must be given.")
        self.tractor_size = tractor_size or self.herd_size_to_tractor_size(herd_size)
        constants = input_manager.get_data("EEE_constants.constants")
        self.constants_by_ID = Utility.convert_list_to_dict_by_key(constants, "ID")

    def herd_size_to_tractor_size(self, herd_size: int) -> TractorSize:
        """
        Assign a Tractor Size based on number of cows
        Implements Helper Function 420  in EEE Functions file.
        """
        if herd_size < 0:
            raise ValueError("Herd size must be a positive integer.")
        if herd_size < 500:
            return TractorSize.SMALL
        elif herd_size < 2000:
            return TractorSize.MEDIUM
        else:
            return TractorSize.LARGE

    @property
    def PTO_kW(self) -> float:
        """Constants 589, 592, 595 in EEE Functions file"""
        pto_mapping = {
            TractorSize.SMALL: self.constants_by_ID[589]["Value"],
            TractorSize.MEDIUM: self.constants_by_ID[592]["Value"],
            TractorSize.LARGE: self.constants_by_ID[595]["Value"],
        }
        return pto_mapping[self.tractor_size]

    @property
    def power_available_kW(self) -> float:
        """Constants 590, 593, 596 in EEE Functions file, calculated bsaed on PTO"""
        return self.PTO_kW / 1.4

    @property
    def mass_kg(self) -> float:
        """Constants 591, 594, 597 in EEE Functions file"""
        mass_mapping = {
            TractorSize.SMALL: self.constants_by_ID[591]["Value"],
            TractorSize.MEDIUM: self.constants_by_ID[594]["Value"],
            TractorSize.LARGE: self.constants_by_ID[597]["Value"],
        }
        return mass_mapping[self.tractor_size]

    @property
    def speed_km_hr(self) -> float:
        """Constant 598 in EEE Functions file"""
        return self.constants_by_ID[598]["Value"]

    def calculate_axel_power(self, implement: TractorImplement) -> float:
        """
        Calculates total Axle Power (kW) required by tractor wheels to move the tractor (and implement if applicable).
        Implements Helper Function 413  in EEE Functions file.
        """
        return (self.mass_kg + implement.mass_kg) * self.speed_km_hr * 9.8 * 0.08 * 1.1 * 1.2 / 3600
