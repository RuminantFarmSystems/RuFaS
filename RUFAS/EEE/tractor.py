from typing import List, Any
from .tractor_implement import TractorImplement
from RUFAS.util import Utility
from RUFAS.input_manager import InputManager
from RUFAS.data_structures.tillage_implements import FieldOperationEvent, TillageImplement, TractorSize, OperationType
from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation

input_manager = InputManager()


SMALL_TRACTOR_PTO_CONSTANT_ID = 589
SMALL_TRACTOR_POWER_AVAILABLE_CONSTANT_ID = 590
SMALL_TRACTOR_MASS_CONSTANT_ID = 591
MEDIUM_TRACTOR_PTO_CONSTANT_ID = 592
MEDIUM_TRACTOR_POWER_AVAILABLE_CONSTANT_ID = 593
MEDIUM_TRACTOR_MASS_CONSTANT_ID = 594
LARGE_TRACTOR_PTO_CONSTANT_ID = 595
LARGE_TRACTOR_POWER_AVAILABLE_CONSTANT_ID = 596
LARGE_TRACTOR_MASS_CONSTANT_ID = 597
TRACTOR_SPEED_CONSTANT_ID = 598


class Tractor:
    """
    A class to represent the specifications of a tractor.
    The tractor's specifications are determined based on its size or the size of the herd it is intended to work with.
    """

    def __init__(
        self,
        operation_event: FieldOperationEvent,
        crop_type: str | None = None,
        tractor_size: TractorSize | None = None,
        herd_size: int | None = None,
        application_depth: float | None = None,
        tillage_implement: TillageImplement | None = None,
        harvest_type: HarvestOperation | None = None,
    ) -> None:
        """
        Initializes the Tractor object with the tractor size or calculates it based on the provided herd size.
        If `tractor_size` is not provided, the size is inferred using the `herd_size` argument.

        Parameters
        ----------
        operation_event : FieldOperationEvent
            The type of field operation for which the tractor is intended.
        crop_type : str | None, optional
            The type of crop for which the tractor is intended.
        tractor_size : TractorSize | None, optional
            The size of the tractor as a `TractorSize` enum value.
        herd_size : int | None, optional
            The size of the herd to determine the tractor size if `tractor_size` is not provided.
        application_depth : float | None, optional
            The depth of the application (cm).
        tillage_implement : TillageImplement | None, optional
            The type of tillage implement used for the operation.
        harvest_type : HarvestOperation | None, optional
            The type of harvest operation for the operation.

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
                operation_event,
                operation_type,
                crop_type,
                self.tractor_size,
                tillage_implement,
                application_depth,
                harvest_type,
            )
            for operation_type in self.operation_types
        ]
        constants = input_manager.get_data("EEE_constants.constants")
        self.constants_by_ID: dict[Any, dict[str, Any]] = Utility.convert_list_to_dict_by_key(constants, "ID")

    def herd_size_to_tractor_size(self, herd_size: int) -> TractorSize:
        """
        Assign a Tractor Size based on the number of cows
        Implements Helper Function 420 in EEE Functions file.
        """
        if herd_size < 0:
            raise ValueError("Herd size must be a positive integer.")
        if herd_size < 500:
            return TractorSize.SMALL
        elif herd_size < 2000:
            return TractorSize.MEDIUM
        else:
            return TractorSize.LARGE

    def determine_operation_type(self, application_depth: float | None = None) -> List[OperationType]:
        """
        Assigns a specific field operation based on the general name for the operation and the crop type for harvest
        operations or depth for nutrient application.
        Implements Helper Function 421 in EEE Functions file.
        """
        if self.operation_event == FieldOperationEvent.HARVEST:
            return self._determine_harvest_operation_types()
        elif self.operation_event == FieldOperationEvent.FERTILIZER_APPLICATION:
            return self._determine_fertilizer_application_operation_types(application_depth)
        elif self.operation_event == FieldOperationEvent.MANURE_APPLICATION:
            return self._determine_manure_application_operation_types(application_depth)
        elif self.operation_event == FieldOperationEvent.PLANTING:
            return [OperationType.PLANTING]
        elif self.operation_event == FieldOperationEvent.TILLING:
            return [OperationType.TILLING]

    def _determine_fertilizer_application_operation_types(self, application_depth: float | None) -> list[OperationType]:
        """
        Determines the types of fertilizer application operations required based on the application depth.

        Returns
        -------
        list[OperationType]
            A list of operation types required for the fertilizer application.
        """
        assert (
            application_depth is not None and application_depth >= 0
        ), "Application depth must be provided and non-negative for fertilizer application."
        if application_depth > 0:
            return [OperationType.FERTILIZER_APPLICATION_BELOW_SURFACE]
        else:
            return [OperationType.FERTILIZER_APPLICATION_SURFACE]

    def _determine_manure_application_operation_types(self, application_depth: float | None) -> list[OperationType]:
        """
        Determines the types of manure application operations required based on the application depth.

        Returns
        -------
        list[OperationType]
            A list of operation types required for the manure application.
        """
        assert (
            application_depth is not None and application_depth >= 0
        ), "Application depth must be provided and non-negative for manure application."
        if application_depth > 0:
            return [OperationType.LIQUID_MANURE_APPLICATION_BELOW_SURFACE]
        else:
            return [OperationType.LIQUID_MANURE_APPLICATION_SURFACE]

    def _determine_harvest_operation_types(self) -> list[OperationType]:
        """
        Determines the types of harvest operations required based on the crop type.

        Returns
        -------
        list[OperationType]
            A list of operation types required for harvesting the crop.
        """
        if self.crop_type in [
            "alfalfa_hay",
            "alfalfa_silage",
            "alfalfa_baleage",
            "tall_fescue_hay",
            "tall_fescue_silage",
            "tall_fescue_baleage",
        ]:
            return [OperationType.MOWING, OperationType.WINDROWING, OperationType.COLLECTION]
        else:
            return [OperationType.COLLECTION]

    @property
    def PTO_kW(self) -> float:
        """Constants 589, 592, 595 in EEE Functions file"""
        pto_mapping: dict[TractorSize, float] = {
            TractorSize.SMALL: self.constants_by_ID[SMALL_TRACTOR_PTO_CONSTANT_ID]["Value"],
            TractorSize.MEDIUM: self.constants_by_ID[MEDIUM_TRACTOR_PTO_CONSTANT_ID]["Value"],
            TractorSize.LARGE: self.constants_by_ID[LARGE_TRACTOR_PTO_CONSTANT_ID]["Value"],
        }
        return pto_mapping[self.tractor_size]

    @property
    def power_available_kW(self) -> float:
        """Constants 590, 593, 596 in EEE Functions file, calculated based on PTO"""
        return self.PTO_kW / 1.4

    @property
    def mass_kg(self) -> float:
        """Constants 591, 594, 597 in EEE Functions file"""
        mass_mapping: dict[TractorSize, float] = {
            TractorSize.SMALL: self.constants_by_ID[SMALL_TRACTOR_MASS_CONSTANT_ID]["Value"],
            TractorSize.MEDIUM: self.constants_by_ID[MEDIUM_TRACTOR_MASS_CONSTANT_ID]["Value"],
            TractorSize.LARGE: self.constants_by_ID[LARGE_TRACTOR_MASS_CONSTANT_ID]["Value"],
        }
        return mass_mapping[self.tractor_size]

    @property
    def speed_km_hr(self) -> float:
        """Constant 598 in EEE Functions file"""
        return float(self.constants_by_ID[TRACTOR_SPEED_CONSTANT_ID]["Value"])

    def calculate_axel_power(self, implement: TractorImplement) -> float:
        """
        Calculates total Axle Power (kW) required by tractor wheels to move the tractor (and implement if applicable).
        Implements Helper Function 413 in EEE Functions file.
        """
        return (self.mass_kg + implement.mass_kg) * self.speed_km_hr * 9.8 * 0.08 * 1.1 * 0.92 / 3600
