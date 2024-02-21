from typing import List
from .tractor_implement import TractorImplement
from RUFAS.util import Utility
from RUFAS.input_manager import InputManager
from RUFAS.routines.field.crop.crop_enum import CropSpecies
from .enums import TractorSize, FieldOperationEvent, OperationType, TillageImplement

input_manager = InputManager()


class Tractor:
    """
    A class to represent the specifications of a tractor.
    The tractor's specifications are determined based on its size or the size of the herd it is intended to work with.
    """

    def __init__(
        self,
        operation_event: FieldOperationEvent,
        crop_type: CropSpecies | None = None,
        tractor_size: TractorSize | None = None,
        herd_size: int | None = None,
        application_depth: float | None = None,
        tillage_implement: TillageImplement | None = None,
    ) -> None:
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
        self.operation_event = operation_event
        self.crop_type = crop_type
        self.tractor_size = tractor_size or self.herd_size_to_tractor_size(herd_size)
        self.operation_types = self.determine_operation_type(application_depth)
        self.implements = [
            TractorImplement(
                operation_event, operation_type, crop_type, self.tractor_size, tillage_implement, application_depth
            )
            for operation_type in self.operation_types
        ]
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

    def determine_operation_type(self, application_depth: float | None = None) -> List[OperationType]:  # noqa C901
        """
        Assigns a specific field operation based on the general name for the operation and the crop type for harvest
        operations or depth for nutrient application.
        Implements Helper Function 421 in EEE Functions file.
        """
        if self.operation_event == FieldOperationEvent.HARVEST:
            if self.crop_type in [
                CropSpecies.ALFALFA_HAY,
                CropSpecies.ALFALFA_SILAGE,
                CropSpecies.ALFALFA_BALEAGE,
                CropSpecies.TALL_FESCUE_HAY,
                CropSpecies.TALL_FESCUE_SILAGE,
                CropSpecies.TALL_FESCUE_BALEAGE,
            ]:
                return [OperationType.MOWING, OperationType.WINDROWING, OperationType.COLLECTION]
            else:
                return [OperationType.COLLECTION]
        elif self.operation_event == FieldOperationEvent.FERTILIZER_APPLICATION:
            if application_depth == 0:
                return [OperationType.FERTILIZER_APPLICATION_SURFACE]
            elif application_depth > 0:
                return [OperationType.FERTILIZER_APPLICATION_BELOW_SURFACE]
        elif self.operation_event == FieldOperationEvent.MANURE_APPLICATION:
            if application_depth == 0:
                return [OperationType.LIQUID_MANURE_APPLICATION_SURFACE]
            elif application_depth > 0:
                return [OperationType.LIQUID_MANURE_APPLICATION_BELOW_SURFACE]
        elif self.operation_event == FieldOperationEvent.PLANTING:
            return [OperationType.PLANTING]
        elif self.operation_event == FieldOperationEvent.TILLING:
            return [OperationType.TILLING]

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
