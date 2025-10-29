from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.data_structures.tillage_implements import FieldOperationEvent, TractorSize, TillageImplement, OperationType
from RUFAS.general_constants import GeneralConstants
from RUFAS.util import Utility
from RUFAS.input_manager import InputManager

input_manager = InputManager()

FIELD_SPEED_CONSTANT_ID = 585
FIELD_EFFICIENCY_CONSTANT_ID = 587


class TractorImplement:
    def __init__(
        self,
        operation_event: FieldOperationEvent,
        operation_type: OperationType,
        crop_type: str | None,
        tractor_size: TractorSize,
        tillage_implement: TillageImplement | None,
        application_depth: float | None,
        harvest_type: HarvestOperation | None = None
    ) -> None:
        """
        Initializes the TractorImplement object with the specifications of the tractor implement.

        Parameters
        ----------
        operation_event : FieldOperationEvent
            The event type of the field operation.
        operation_type : OperationType
            The type of operation to perform.
        crop_type : str | None, optional
            The type of crop to perform the operation on.
        tractor_size : TractorSize
            The size of the tractor.
        tillage_implement : TillageImplement | None, optional
            The type of tillage implement used for the operation.
        application_depth : float | None, optional
            The depth of the application (cm).
        harvest_type : HarvestOperation | None, optional
            The type of harvest operation for the operation.
        """
        self.operation_event = operation_event
        self.operation_type = operation_type
        self.crop_type = crop_type
        self.tractor_size = tractor_size
        self.tillage_implement = tillage_implement
        self.harvest_type = harvest_type if self.operation_event == FieldOperationEvent.HARVEST else None
        constants = input_manager.get_data("EEE_constants.constants")
        constants_by_ID = Utility.convert_list_to_dict_by_key(constants, "ID")
        self.field_speed_km_per_hr: float = constants_by_ID[FIELD_SPEED_CONSTANT_ID][
            "Value"
        ]  # Constant 585 in EEE Functions file
        self.field_efficiency: float = constants_by_ID[FIELD_EFFICIENCY_CONSTANT_ID][
            "Value"
        ]  # Constant 587 in EEE Functions file
        self.determine_implement_parameters(application_depth)

    def determine_implement_parameters(self, application_depth: float | None) -> None:
        """
        Assign a tractor implement based on the operation, tractor size, and crop type where applicable. Not all
        operations depend on the crop type.

        Parameters
        ----------
        application_depth : float | None
            The depth (in cm) to be used for certain operations that require it, such as fertilizer application.
            If not applicable, this can be None.

        Reference
        ---------
        Helper Function 419 in EEE Functions file.
        """
        dataset_raw = input_manager.get_data("tractor_dataset")
        dataset = Utility.convert_dict_of_lists_to_list_of_dicts(dataset_raw)
        if self.operation_type == OperationType.TILLING:
            crop_type_or_tillage_implement = self.tillage_implement.value.lower()
        else:
            crop_type_or_tillage_implement = self.crop_type.lower() if self.crop_type is not None else "none"
        if self.operation_event == FieldOperationEvent.HARVEST and self.harvest_type == HarvestOperation.KILL_ONLY:
            self.operation_type = OperationType.MOWING
        for data_entry in dataset:
            if (
                data_entry.get("Crop Type or Tillage Implement").lower() in [crop_type_or_tillage_implement, "none"]
                and data_entry.get("Tractor Size").lower() == self.tractor_size.value.lower()
                and data_entry.get("Operation").lower() == self.operation_type.value.lower()
            ):
                self.implement_name: str = data_entry["Tractor Implement"]
                self.A: float = data_entry["Tractor A (unitless)"]
                self.B: float = data_entry["Tractor B (unitless)"]
                self.C: float = data_entry["Tractor C (unitless)"]
                self.E: float = data_entry["Tractor E (unitless)"]
                self.F: float = data_entry["Tractor F (unitless)"]
                self.G: float = data_entry["Tractor G (unitless)"]
                self.width_m: float = data_entry["Tractor Implement Width (m)"]
                self.mass_kg: float = data_entry["Tractor Implement Mass (kg)"]
                self.throughput: float = data_entry["Max Throughput (tons dm/hour)"]
                if self.operation_type in [
                    OperationType.TILLING,
                    OperationType.FERTILIZER_APPLICATION_BELOW_SURFACE,
                    OperationType.FERTILIZER_APPLICATION_SURFACE,
                    OperationType.LIQUID_MANURE_APPLICATION_BELOW_SURFACE,
                    OperationType.LIQUID_MANURE_APPLICATION_SURFACE,
                ]:
                    self.depth_cm: float = application_depth * GeneralConstants.MM_TO_CM
                else:
                    self.depth_cm = data_entry["Depth"]
                self.is_depth_relevant: bool = data_entry["is depth relevant"]
                break

    def field_capacity_ha_per_hr(
        self, crop_yield_ton_per_ha: float | None, application_mass: float | None = None
    ) -> float:
        """
        Calculates the Field Capacity for a specific crop, field operation and tractor implement.
        Implements Helper Functions 418a and 418b in EEE Functions file.
        """
        if self.operation_type == OperationType.COLLECTION and self.harvest_type != HarvestOperation.KILL_ONLY:  # 418b
            return (self.throughput / crop_yield_ton_per_ha) * self.field_efficiency
        elif self.operation_type in [
            OperationType.LIQUID_MANURE_APPLICATION_BELOW_SURFACE,
            OperationType.LIQUID_MANURE_APPLICATION_SURFACE,
        ]:      # 418c
            return (self.throughput / application_mass) * self.field_efficiency

        return (
            self.field_speed_km_per_hr
            * GeneralConstants.KM_TO_M
            * self.width_m
            * self.field_efficiency
            * GeneralConstants.SQUARE_METERS_TO_HECTARES
        )       # 418a

    def calculate_operation_time_hr(
        self,
        field_production_size_ha: float,
        crop_yield_ton_per_ha: float | None,
        application_mass: float | None = None,
    ) -> float:
        """
        Calculates the number of hours taken by a tractor given other factors like implement size to perform the
        operation.
        Implements Helper Function 416 in EEE Functions file.
        """
        field_capacity = self.field_capacity_ha_per_hr(crop_yield_ton_per_ha, application_mass)
        return field_production_size_ha / field_capacity

    def calculate_drawbar_power(self, clay_percent: float) -> float:
        """
        Calculates Drawbar Power (kW) which is the power required by the implement for propulsion forward if it
        requires a transfer of tractor power to its wheel drives for this purpose.
        Implements Helper Function 414 in EEE Functions file.
        """
        functional_draft = self.calculate_functional_draft(clay_percent)
        return functional_draft * self.field_speed_km_per_hr * 1.2 / 3600

    def calculate_functional_draft(self, clay_percent: float) -> float:
        """
        Calculate Functional draft in Newtons, the force required for pulling various planting implements and
        minor tillage tools operated at shallow depths.
        Implements Helper Functions 417 and 421 in EEE Functions file.
        """
        soil_texture_adjustment = (
            3 if clay_percent < 20 else 2 if clay_percent < 50 else 1 if clay_percent <= 100 else "Invalid"
        )
        effective_depth = self.depth_cm if self.is_depth_relevant and self.depth_cm > 0 else 1
        return (
            self.width_m
            * effective_depth
            * soil_texture_adjustment
            * (self.A + self.B * self.field_speed_km_per_hr + self.C * self.field_speed_km_per_hr**2)
        )

    def calculate_needed_PTO(
        self,
        crop_yield_ton_per_ha: float,
        field_production_size_ha: float,
        application_mass: float | None = None,
    ) -> float:
        """
        Calculates PTO_Power (kW) from the tractor to power the implement's operation.
        Implements Helper Function 415 in EEE Functions file.
        """
        coefficient_to_use = (
            application_mass
            if self.operation_type
            in [OperationType.LIQUID_MANURE_APPLICATION_BELOW_SURFACE, OperationType.LIQUID_MANURE_APPLICATION_SURFACE]
            else crop_yield_ton_per_ha
        )

        return (
            self.E
            + (self.F * self.width_m)
            + (
                self.G
                * coefficient_to_use
                * field_production_size_ha
                / self.calculate_operation_time_hr(field_production_size_ha, crop_yield_ton_per_ha, application_mass)
            )
        )
