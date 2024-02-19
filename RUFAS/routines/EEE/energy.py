from math import sqrt

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.crop.crop_enum import CropSpecies

from .tractor import Tractor
from .tractor_implement import TractorImplement
from .enums import TractorSize, FieldOperationEvent, TillageImplement

om = OutputManager()


class EnergyEstimator:
    """Class to esitmate energy consumption for various operations on the farm"""

    @classmethod
    def estimate_all() -> None:
        """Runs all estimation functions and performs pre/post processing for them."""
        base_info_map = {
            "class": EnergyEstimator.__name__,
            "function": EnergyEstimator.estimate_all.__name__,
            "unit": "unitless",
        }
        estimator = EnergyEstimator()
        diesel_conumption_data = estimator.parse_inputs_for_diesel_consumption_calculation()
        tractor = Tractor(
            diesel_conumption_data["operation_event"],
            diesel_conumption_data["crop_type"],
            diesel_conumption_data["tractor_size"],
            diesel_conumption_data["herd_size"],
            diesel_conumption_data["application_depth"],
        )

        diesel_consumption_tractor_implement_liter_per_ton = estimator.calculate_diesel_consumption(
            diesel_conumption_data["crop_yield"],
            diesel_conumption_data["field_production_size"],
            tractor,
            diesel_conumption_data["clay_percent"],
        )
        variable_info_map = {"unit": "liter/tone", "tractor_size": tractor.tractor_size}
        om.add_variable(
            "diesel_consumption_tractor_implement",
            diesel_consumption_tractor_implement_liter_per_ton,
            {**base_info_map, **variable_info_map},
        )

    def parse_inputs_for_diesel_consumption_calculation(self):

        from RUFAS.routines.EEE.enums import FieldOperationEvent

        filters = [
            {
                "name": FieldOperationEvent.FERTILIZER_APPLICATION,
                "use_name": True,
                "filters": ["Field._record_fertilizer_application.fertilizer_application.field='.*'"],
                "variables": ["event_type", "mass", "application_depth", "field_size", "average_clay_percent"],
            },
            {
                "name": "Tillage",
                "use_name": True,
                "filters": ["TillageApplication._record_tillage.tillage_record.field='.*'"],
                "variables": ["event_type", "tillage_depth", "implement", "field_size", "average_clay_percent"],
            },
            {
                "name": FieldOperationEvent.MANURE_APPLICATION,
                "use_name": True,
                "filters": ["Field._record_manure_application.manure_application.field='.*'"],
                "variables": [
                    "event_type",
                    "dry_matter_mass",
                    "dry_matter_fraction",
                    "application_depth",
                    "field_size",
                    "average_clay_percent",
                ],
            },
            {
                "name": FieldOperationEvent.HARVEST,
                "use_name": True,
                "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
                "variables": ["event_type", "dry_yield", "crop", "field_size"],
            },
            {
                "name": FieldOperationEvent.PLANTING,
                "use_name": True,
                "filters": ["Field._plant_crop.crop_planting.field='.*'"],
                "variables": ["event_type", "crop", "field_size", "average_clay_percent"],
            },
        ]
        # for filter in filters:
        #     result = output_manager.filter_variables_pool_complex(filter)
        #     if result["Fertilizer Application_0.event_type"][0] == FieldOperationEvent.FERTILIZER_APPLICATION:
        #         print("tr " * 50)

        for filter in filters:
            result = om.filter_variables_pool_complex(filter)
            first_key, first_value = next(iter(result.items()))
            length = len(first_value)
            key_prefix = first_key.rsplit(".", 1)[0]
            if first_key.startswith(FieldOperationEvent.FERTILIZER_APPLICATION.value):
                pass

        expected_result = [
            {
                "Fertilizer Application_0.event_type": [FieldOperationEvent.FERTILIZER_APPLICATION],
                "Fertilizer Application_0.mass": [100.0],
                "Fertilizer Application_0.application_depth": [0.0],
                "Fertilizer Application_0.field_size": [1.0],
                "Fertilizer Application_0.average_clay_percent": [20.0],
            },
            {
                "Tillage_0.event_type": [
                    FieldOperationEvent.TILLING,
                    FieldOperationEvent.TILLING,
                    FieldOperationEvent.TILLING,
                    FieldOperationEvent.TILLING,
                    FieldOperationEvent.TILLING,
                    FieldOperationEvent.TILLING,
                    FieldOperationEvent.TILLING,
                ],
                "Tillage_0.tillage_depth": [100, 150, 100, 150, 100, 150, 100],
                "Tillage_0.implement": [
                    TillageImplement.DISK_HARROW,
                    TillageImplement.DISK_HARROW,
                    TillageImplement.DISK_HARROW,
                    TillageImplement.DISK_HARROW,
                    TillageImplement.DISK_HARROW,
                    TillageImplement.DISK_HARROW,
                    TillageImplement.DISK_HARROW,
                ],
                "Tillage_0.field_size": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                "Tillage_0.average_clay_percent": [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0],
            },
            {
                "Manure Application_0.event_type": [
                    FieldOperationEvent.MANURE_APPLICATION,
                    FieldOperationEvent.MANURE_APPLICATION,
                    FieldOperationEvent.MANURE_APPLICATION,
                ],
                "Manure Application_0.dry_matter_mass": [2093.3808034402673, 1040.6356997812088, 1582.8073441422118],
                "Manure Application_0.dry_matter_fraction": [
                    0.04037844586944284,
                    0.03700154121271599,
                    0.03717672559333978,
                ],
                "Manure Application_0.application_depth": [150.0, 150.0, 150.0],
                "Manure Application_0.field_size": [1.0, 1.0, 1.0],
                "Manure Application_0.average_clay_percent": [20.0, 20.0, 20.0],
            },
            {
                "harvest_0.event_type": [
                    FieldOperationEvent.HARVEST,
                    FieldOperationEvent.HARVEST,
                    FieldOperationEvent.HARVEST,
                    FieldOperationEvent.HARVEST,
                ],
                "harvest_0.crop": [
                    CropSpecies.ALFALFA_HAY,
                    CropSpecies.ALFALFA_HAY,
                    CropSpecies.ALFALFA_HAY,
                    CropSpecies.CORN_GRAIN,
                ],
                "harvest_0.dry_yield": [2035.6063130026596, 1805.667208160874, 1947.9321959672566, 3601.7789198141386],
                "harvest_0.field_size": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "planting_0.event_type": [
                    FieldOperationEvent.PLANTING,
                    FieldOperationEvent.PLANTING,
                    FieldOperationEvent.PLANTING,
                    FieldOperationEvent.PLANTING,
                ],
                "planting_0.crop": [
                    CropSpecies.ALFALFA_HAY,
                    CropSpecies.ALFALFA_HAY,
                    CropSpecies.ALFALFA_HAY,
                    CropSpecies.CORN_GRAIN,
                ],
                "planting_0.field_size": [1.0, 1.0, 1.0, 1.0],
                "planting_0.average_clay_percent": [20.0, 20.0, 20.0, 20.0],
            },
        ]
        print(expected_result)
        crop_yield = 0  # TODO get the correct value
        field_production_size = 0  # TODO get the correct value
        operation_event = FieldOperationEvent.PLANTING  # TODO get the correct value
        crop_type = CropSpecies.ALFALFA_BALEAGE  # TODO get the correct value
        tractor_size = (
            TractorSize.SMALL
        )  # TODO get the correct value, how do we determine this? based on dataset or herdsize?
        herd_size: int = 750  # TODO get the correct value
        application_depth: float = 10  # TODO get the correct value
        clay_percent = 0  # TODO get the correct value

    def calculate_diesel_consumption(
        self,
        crop_yield: float,
        field_production_size: float,
        tractor: Tractor,
        clay_percent: float,
    ) -> float:
        """
        General estimate  how diesel fuel consumption is estimated for a given attachment type and tractor size.
        Different practices use different types of tools/implements; the equation to estimate diesel fuel consumption
        may be the same across practices but different implements have different parameter values.

        Parameters
        ----------
        crop_yield: float
            Amount of crop yielded per hectars (metric ton/ha)
        field_production_size: float
            The filed area under production (ha)
        tractor: Tractor
            The specifications of the tractor

        Returns
        -------
        float
            Diesel Consumption for Tractor-Implement (l/ton)
        """
        diesel_consumption_tractor_implement_liter_per_ton = 0
        for implement in tractor.implements:
            total_power_needed_kW = self._calculate_total_power_needed(
                tractor,
                implement,
                crop_yield,
                field_production_size,
                clay_percent,
            )
            x = total_power_needed_kW / tractor.power_available_kW  # helper function 411
            specific_fuel_consumption_liter_per_kWh = (
                (2.64 * x) + 3.91 - 0.203 * sqrt(738 * x + 172)
            )  # helper function 410
            tractor_implement_operation_time_hr = implement.calculate_operation_time_hr(
                field_production_size, crop_yield
            )
            diesel_consumption_tractor_implement_liter_per_ton += (
                specific_fuel_consumption_liter_per_kWh
                * total_power_needed_kW
                * tractor_implement_operation_time_hr
                / field_production_size
                / crop_yield
            )
        return diesel_consumption_tractor_implement_liter_per_ton

    def _calculate_total_power_needed(
        self,
        tractor: Tractor,
        implement: TractorImplement,
        crop_yield_ton_per_ha: float,
        field_production_size_ha: float,
        clay_percent: float,
    ) -> float:
        """
        Calculates the total power needed to perform the field operation by the tractor and implement where applicable.
        Implements Helper Function 412  in EEE Functions file.
        """
        tactor_axel_power = tractor.calculate_axel_power(implement)
        tractor_implement_drawbar_power = implement.calculate_drawbar_power(clay_percent)
        tractor_implement_PTO_power_needed = implement.calculate_needed_PTO(
            crop_yield_ton_per_ha, field_production_size_ha
        )
        return tactor_axel_power + tractor_implement_drawbar_power + tractor_implement_PTO_power_needed
