from math import cos, sin
from typing import Dict
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

IM = InputManager()
OM = OutputManager()


class EconomyEneregyEmission:
    def __init__(self) -> None:
        pass

    def _calculate_diesel_consumption(
        self,
        acre_size: float,
        drawbar_speed: float,
        field_capacity: float,
        functional_draft: float,
        harvest_yield: float,
        IFSM_operation_data_E: float,
        IFMS_operation_data_F: float,
        IFSM_operation_data_G: float,
        IFSM_operation_data_width: float,
        implement_mass: float,
        total_time: float,
        tractor_mass: float,
        tractor_PTO: float,
        tractor_speed: float,
    ) -> float:
        """
        Calculate the diesel consumption for a given crop management practice.

        Parameters
        ----------
        acre_size : float
            Size of the production area in acres.
        drawbar_speed : float
            Drawbar speed in kilometers per hour (km/hr).
        field_capacity : float
            Field capacity determined by implement constants sourced from IFSM.
        functional_draft : float
            Functional draft in Newtons (N).
        harvest_yield : float
            Crop yield in tons per acre (tons/acre).
        IFSM_operation_data_E : float
            IFSM operation data parameter E.
        IFMS_operation_data_F : float
            IFSM operation data parameter F.
        IFSM_operation_data_G : float
            IFSM operation data parameter G.
        IFSM_operation_data_width : float
            IFSM operation data parameter Width in meters (m).
        implement_mass : float
            Mass of the implement in kilograms (kg).
        total_time : float
            Total time of tractor operation for primary and secondary tillage in hours (hrs).
        tractor_mass : float
            Mass of the tractor in kilograms (kg).
        tractor_PTO : float
            Tractor power take-off (PTO) in kilowatts (kW).
        tractor_speed : float
            Tractor speed in kilometers per hour (km/hr).

        Returns
        -------
        float
            Estimated diesel consumption in liters per ton (l/ton) for the crop management practice.
        """
        PTO_power = (
            IFSM_operation_data_E
            + IFMS_operation_data_F * IFSM_operation_data_width
            + (IFSM_operation_data_G * harvest_yield * acre_size / total_time)
        )
        axle_power = (
            9.8 * tractor_mass
            + implement_mass
            * (0.08 * cos(0) + sin(0))
            * tractor_speed
            * 1.1
            * 1.2
            / 3600
        )
        drawbar_power = functional_draft * drawbar_speed * 1.2 / 3600
        power_needed = axle_power + drawbar_power + PTO_power
        power_available = tractor_PTO / 1.4
        x = power_needed / power_available
        specific_fuel_consumption = 2.64 * x + 3.91 - 0.203 * pow(738 * x + 173, 0.5)
        operation_time = acre_size / field_capacity
        consumed_diesel = (
            specific_fuel_consumption
            * power_needed
            * operation_time
            / acre_size
            / harvest_yield
        )
        return consumed_diesel

    def run_crop_management_fuel_consumption_scenarios(self) -> None:
        """
        Run crop management fuel consumption scenarios and store the results.

        This method retrieves crop management fuel consumption scenarios from InputManager,
        calculates the diesel consumption for each scenario using the private method _calculate_diesel_consumption,
        and reports the results to the OutputManager.

        Returns
        -------
        None

        Notes
        -----
        This method assumes that the instance of the class has access to a data source with fuel consumption scenarios,
        and the scenarios are stored as a dictionary where the keys are scenario names and the values are dictionaries
        containing the details required for calculating diesel consumption. The format of the scenarios dictionary
        should be:

        scenarios = {
            "scenario_name_1": {
                "acre_size": value_1,
                "drawbar_speed": value_2,
                "field_capacity": value_3,
                "functional_draft": value_4,
                "harvest_yield": value_5,
                "IFSM_operation_data_E": value_6,
                "IFMS_operation_data_F": value_7,
                "IFSM_operation_data_G": value_8,
                "IFSM_operation_data_width": value_9,
                "implement_mass": value_10,
                "total_time": value_11,
                "tractor_mass": value_12,
                "tractor_PTO": value_13,
                "tractor_speed": value_14,
            },
            "scenario_name_2": {
                # details for scenario 2
            },
            # more scenarios...
        }
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.run_crop_management_fuel_consumption_scenarios.__name__,
        }
        scenarios: Dict[str, dict[str, float]] = IM.get_data(
            "EEE.crop_management_fuel_consumption_scenarios"
        )
        for scenario, details in scenarios.items():
            consumed_diesel = self._calculate_diesel_consumption(**details)
            OM.add_variable(scenario, consumed_diesel, info_map)
