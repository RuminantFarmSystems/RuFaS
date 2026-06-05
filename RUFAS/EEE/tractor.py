from typing import Any
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
    Represents the specifications of a tractor.

    Parameters
    ----------
    operation_event : FieldOperationEvent
        The type of field operation for which the tractor is intended.
    crop_type : str | None, optional
        The type of crop for which the tractor is intended.
    tractor_size : TractorSize | None, optional
        The size of the tractor as a ``TractorSize`` enum value.
    herd_size : int | None, optional
        The size of the herd, used to determine the tractor size if ``tractor_size`` is not provided.
    application_depth : float | None, optional
        The depth of the application (cm).
    tillage_implement : TillageImplement | None, optional
        The type of tillage implement used for the operation.
    harvest_type : HarvestOperation | None, optional
        The type of harvest operation for the operation.

    Attributes
    ----------
    operation_event : FieldOperationEvent
        The type of field operation for which the tractor is intended.
    crop_type : str | None
        The type of crop for which the tractor is intended.
    tractor_size : TractorSize
        The size of the tractor.
    operation_types : list[OperationType]
        The operation types the tractor performs for the operation event.
    implements : list[TractorImplement]
        The tractor implements used for each operation type.
    constants_by_ID : dict[Any, dict[str, Any]]
        The EEE constants data keyed by their ID.

    Raises
    ------
    ValueError
        If neither ``tractor_size`` nor ``herd_size`` is provided.

    Notes
    -----
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
        """Initializes the Tractor object with the tractor size, or calculates it based on the provided herd size."""
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
        Assigns a tractor size based on the number of cows in the herd.

        Parameters
        ----------
        herd_size : int
            The number of cows in the herd.

        Returns
        -------
        TractorSize
            The tractor size assigned for the given herd size.

        Raises
        ------
        ValueError
            If ``herd_size`` is negative.

        References
        ----------
        Implements Helper Function 420 in the EEE Functions file.
        """
        if herd_size < 0:
            raise ValueError("Herd size must be a positive integer.")
        if herd_size < 500:
            return TractorSize.SMALL
        elif herd_size < 2000:
            return TractorSize.MEDIUM
        else:
            return TractorSize.LARGE

    def determine_operation_type(self, application_depth: float | None = None) -> list[OperationType]:
        """
        Assigns the specific field operations based on the operation event, and the crop type for harvest operations
        or the application depth for nutrient applications.

        Parameters
        ----------
        application_depth : float | None, optional
            The depth of the application (cm), used for nutrient application operations.

        Returns
        -------
        list[OperationType]
            The operation types required for the field operation event.

        References
        ----------
        Implements Helper Function 421 in the EEE Functions file.
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

        Parameters
        ----------
        application_depth : float | None
            The depth of the fertilizer application (cm).

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

        Parameters
        ----------
        application_depth : float | None
            The depth of the manure application (cm).

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
        """
        Power take-off (PTO) power available from the tractor based on its size (kW).

        References
        ----------
        Constants 589, 592, and 595 in the EEE Functions file.
        """
        pto_mapping: dict[TractorSize, float] = {
            TractorSize.SMALL: self.constants_by_ID[SMALL_TRACTOR_PTO_CONSTANT_ID]["Value"],
            TractorSize.MEDIUM: self.constants_by_ID[MEDIUM_TRACTOR_PTO_CONSTANT_ID]["Value"],
            TractorSize.LARGE: self.constants_by_ID[LARGE_TRACTOR_PTO_CONSTANT_ID]["Value"],
        }
        return pto_mapping[self.tractor_size]

    @property
    def power_available_kW(self) -> float:
        """
        Power available from the tractor based on its size, derived from the PTO power (kW).

        References
        ----------
        Constants 590, 593, and 596 in the EEE Functions file.
        """
        return self.PTO_kW / 1.4

    @property
    def mass_kg(self) -> float:
        """
        Mass of the tractor based on its size (kg).

        References
        ----------
        Constants 591, 594, and 597 in the EEE Functions file.
        """
        mass_mapping: dict[TractorSize, float] = {
            TractorSize.SMALL: self.constants_by_ID[SMALL_TRACTOR_MASS_CONSTANT_ID]["Value"],
            TractorSize.MEDIUM: self.constants_by_ID[MEDIUM_TRACTOR_MASS_CONSTANT_ID]["Value"],
            TractorSize.LARGE: self.constants_by_ID[LARGE_TRACTOR_MASS_CONSTANT_ID]["Value"],
        }
        return mass_mapping[self.tractor_size]

    @property
    def speed_km_hr(self) -> float:
        """
        Travel speed of the tractor (km/hr).

        References
        ----------
        Constant 598 in the EEE Functions file.
        """
        return float(self.constants_by_ID[TRACTOR_SPEED_CONSTANT_ID]["Value"])

    def calculate_axel_power(self, implement: TractorImplement) -> float:
        """
        Calculates the total axle power required by the tractor wheels to move the tractor and implement where
        applicable.

        Parameters
        ----------
        implement : TractorImplement
            The specifications of the implement.

        Returns
        -------
        float
            The total axle power required to move the tractor and implement (kW).

        References
        ----------
        Implements Helper Function 413 in the EEE Functions file.
        """
        return (self.mass_kg + implement.mass_kg) * self.speed_km_hr * 9.8 * 0.08 * 1.1 * 0.92 / 3600
