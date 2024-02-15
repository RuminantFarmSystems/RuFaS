from typing import List
from RUFAS.util import Utility
from RUFAS.input_manager import InputManager
from .enums import FieldOperationEvent, CropType, OperationType, TractorSize

input_manager = InputManager()


class TractorImplement:
    def __init__(
        self,
        operation_event: FieldOperationEvent,
        crop_type: CropType,
        tractor_size: TractorSize,
    ) -> None:
        self.operation_event = operation_event
        self.crop_type = crop_type
        constants = input_manager.get_data("EEE_constants.constants")
        self.constants_by_ID = Utility.convert_list_to_dict_by_key(constants, "ID")

    def determine_implement_parameters(
        self, crop_type: CropType, tractor_size: TractorSize, operation_type: OperationType
    ) -> None:
        """
        Assign a tractor implement based on the operation, tractor size, and crop type where applicable. Not all
        operations are depended on crop type.
        Implements Helper Function 419 in EEE Functions file.
        """
        dataset_raw = input_manager.get_data("tractor_dataset")
        dataset = Utility.convert_dict_of_lists_to_list_of_dicts(dataset_raw)
        for data_entry in dataset:
            if (
                data_entry.get("Crop Type or Tillage Implement").lower() == crop_type.value.lower()
                and data_entry.get("Tractor Size").lower() == tractor_size.value.lower()
                and data_entry.get("Operation").lower() == operation_type.value.lower()
            ):
                self.implement_name = data_entry["Tractor Implement"]
                self.A = data_entry["Tractor A (unitless)"]
                self.B = data_entry["Tractor B (unitless)"]
                self.C = data_entry["Tractor C (unitless)"]
                self.E = data_entry["Tractor E (unitless)"]
                self.F = data_entry["Tractor F (unitless)"]
                self.G = data_entry["Tractor G (unitless)"]
                self.width_m = data_entry["Tractor Implement Width (m)"]
                self.mass_kg = data_entry["Tractor Implement Mass (kg)"]
                self.throughput = data_entry["Max Throughput (tons dm/hour)"]
                self.is_depth_relevant = data_entry["is depth relevant"]
                break

    def determine_operation_type(self, application_depth: float | None = None) -> List[OperationType]:  # noqa C901
        """
        Assigns a specific field operation based on the general name for the operation and the crop type for harvest
        operations or depth for nutrient application.
        Implements Helper Function 421 in EEE Functions file.
        """
        if self.operation_event == FieldOperationEvent.HARVEST:
            if self.crop_type in [
                CropType.ALFALFA_HAY,
                CropType.ALFALFA_SILAGE,
                CropType.ALFALFA_BALEAGE,
                CropType.TALL_FESCUE_HAY,
                CropType.TALL_FESCUE_SILAGE,
                CropType.TALL_FESCUE_BALEAGE,
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

    def field_capacity_ha_per_hr(self, crop_yield_ton_per_ha: float | None) -> float:
        """
        Calculates the Field Capacity for a specific crop, field operation and tractor implement.
        Implements Helper Functions 418a and 418b  in EEE Functions file.
        """
        field_efficiency = self.constants_by_ID[587]["Value"]  # Constant 587 in EEE Functions file
        if crop_yield_ton_per_ha:  # TODO this is not correct, the decision should be made based on operation type
            crop_yield_kg_per_ha = crop_yield_ton_per_ha * 1000
            return crop_yield_kg_per_ha / self.throughput * 1000 * field_efficiency
        field_speed_km_per_hr = self.constants_by_ID[585]["Value"]  # Constant 585 in EEE Functions file
        return 0.1 * field_speed_km_per_hr * self.width_m * field_efficiency

    def calculate_operation_time_hr(
        self, field_production_size_ha: float, crop_yield_ton_per_ha: float | None
    ) -> float:
        """
        Calculates number of hours taken by tractor given other factors like implement size to perform the operation.
        Implements Helper Function 416  in EEE Functions file.
        """
        return field_production_size_ha / self.field_capacity_ha_per_hr(crop_yield_ton_per_ha)

    def calculate_drawbar_power(self) -> float:
        """
        Calculates Drawbar Power (kW) which is the power required by the implement for propulsion forward if it
        requires a transfer of tractor power to its wheel drives for this purpose.
        Implements Helper Function 414  in EEE Functions file.
        """
        field_speed_km_per_hr = self.constants_by_ID[585]["Value"]  # Constant 585 in EEE Functions file
        functional_draft = self.calculate_functional_draft()
        return functional_draft * field_speed_km_per_hr * 1.2 / 3600

    def calculate_functional_draft(self, crop_type: CropType) -> float:  # TODO implement
        """
        Calculatse Functional draft in Newtons, the force required for pulling various planting implements and
        minor tillage tools operated at shallow depths.
        Implements Helper Function 417  in EEE Functions file.
        """
        """
        self.width_m*[(Operation Depth)*I(Operation Depth)+(1-I(Operation Depth)]*(Fi)*[A + B*(Field Speed)+ C *[(Field Speed)^2)]
                      

        2) Operation Type  in {planting,tilling, liquid manure -surface, liquid manure - below surface, fertilizer, mowing, windrowing, collection} [HF #421] 
        3) Fi soil texture adjustment parameter (unitless)  {HF #422} 
        4) Operation Depth (cm) [C&S for tillage and manure application] [Dataset Tractor for planting]
        5) A (unitless) [Dataset Tractor (Value(Tractor Implement), Column F)]
        6) B (unitless) [Dataset Tractor (Value(Tractor Implement), Column G)]
        7) C (unitless) [Dataset Tractor (Value(Tractor Implement), Column H)]
        8) Field Speed (km/h) [Constant # 585]
        9) Tractor Implement Width (m) [Dataset Tractor (Value(Tractor Implement), Column G)]
        10) I(Operation Depth) (unitless) [=1 if there is Operation Depth, =0 else]
        """
        pass

    def calculate_needed_PTO(self, crop_yield_ton_per_ha: float, field_production_size_ha: float) -> float:
        """
        Calculates PTO_Power (kW) from the tractor to power the implement's operation.
        Implements Helper Function 415  in EEE Functions file.
        """

        return (
            self.E
            + (self.F * self.width_m)
            + (
                self.G
                * crop_yield_ton_per_ha
                * field_production_size_ha
                / self.calculate_operation_time_hr(field_production_size_ha, crop_yield_ton_per_ha)
            )
        )
