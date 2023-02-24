import math
from typing import Optional, List
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class PoolGasPartition:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    def partition(self):
        """
        Description:
            This function does the partitioning of carbon into pools or gas loss
            "pseudocode_soil" S.6.C
        Args:
            soil: an instance of the Soil class defined in soil.py
        """
        for layer in self.data.soil_layers:
            # ---- plants
            layer.plant_metabolic_active_carbon_loss = self._plant_metabolic_active_carbon_loss(
                layer.plant_metabolic_active_carbon_usage)
            layer.plant_metabolic_active_carbon_remaining = self._plant_metabolic_active_carbon_remaining(
                layer.plant_metabolic_active_carbon_usage)

            # above ground structural C
            layer.plant_structural_active_carbon_loss = self._plant_structural_active_carbon_loss(
                layer.plant_structural_active_carbon_usage)
            layer.plant_structural_active_carbon_remaining = self._plant_structural_active_carbon_remaining(
                layer.plant_structural_active_carbon_usage)

            layer.plant_structural_slow_carbon_loss = self._plant_structural_slow_carbon_loss(
                layer.plant_structural_slow_carbon_usage)
            layer.plant_structural_slow_carbon_remaining = self._plant_structural_slow_carbon_remaining(
                layer.plant_structural_slow_carbon_usage)

            # ----- soil
            layer.soil_metabolic_active_carbon_loss = self._soil_metabolic_active_carbon_loss(
                layer.soil_metabolic_active_carbon_usage)
            layer.soil_metabolic_active_carbon_remaining = self._soil_metabolic_active_carbon_remaining(
                layer.soil_metabolic_active_carbon_usage)

            # below ground structural C
            layer.soil_structural_active_carbon_loss = self._soil_structural_active_carbon_loss(
                layer.soil_structural_active_carbon_usage)
            layer.soil_structural_active_carbon_remaining = self._soil_structural_active_carbon_remaining(
                layer.soil_structural_active_carbon_usage)

            layer.soil_structural_slow_carbon_loss = self._soil_structural_slow_carbon_loss(
                layer.soil_structural_slow_carbon_usage)
            layer.soil_structural_slow_carbon_remaining = self._soil_structural_slow_carbon_remaining(
                layer.soil_structural_slow_carbon_usage)

            # S.6.C.4
            K6 = 0.0038
            C_slow_decomp = K6 * layer.M_d * soil.T_d * layer.C_slow

            # S.6.C.5
            K7 = 0.00013
            C_passive_decomp = K7 * layer.M_d * soil.T_d * layer.C_passive

            # S.6.C.7
            layer.active_carbon_to_slow_amount = self._active_carbon_to_slow_ampunt(
                layer.decomposition_moisture_effect,
                self.data. decomposition_temperature_effect,
                layer.active_carbon_amount,
                self.data.silt_clay_content)

            layer.active_carbon_to_slow_loss = self._active_carbon_to_slow_loss(
                layer.decomposition_moisture_effect,
                self.data.decomposition_temperature_effect,
                layer.active_carbon_amount,
                self.data.silt_clay_content
            )

            # S.6.C.8
            layer.active_carbon_to_passive_amount = self._active_carbon_to_passive_amount(
                layer.decomposition_moisture_effect,
                self.data.decomposition_temperature_effect,
                layer.active_carbon_amount,
                self.data.silt_clay_content
            )

            percent_CO2_to_C_slow_loss = 0.55
            percent_C_slow_to_passive = 0.03

            # S.6.C.9
            layer.C_slow_to_active = C_slow_decomp * (1 - percent_CO2_to_C_slow_loss - percent_C_slow_to_passive)
            layer.C_slow_loss = C_slow_decomp * percent_CO2_to_C_slow_loss
            layer.C_slow_to_passive = C_slow_decomp * percent_C_slow_to_passive

            percent_CO2_to_C_passive_loss = 0.55

            # S.6.C.10
            layer.C_passive_to_active = C_passive_decomp * (1 - percent_CO2_to_C_passive_loss)
            layer.C_passive_loss = C_passive_decomp * percent_CO2_to_C_passive_loss

            # active, slow and lost CO2 pools

            # aggregate active carbon pool flux
            # S.6.C.11
            layer.C_active += (
                                      layer.plant_metabolic_active_carbon_remaining + layer.plant_structural_active_carbon_remaining +
                                      layer.BG_met_to_C_active_act + layer.BG_struct_to_C_active_act +
                                      layer.C_passive_to_active + layer.C_slow_to_active) - layer.C_active_decomp

            # aggregate slow carbon pool flux
            # S.6.C.12
            layer.C_slow += (layer.AG_struct_to_C_slow_act + layer.BG_struct_to_C_slow_act +
                             layer.C_active_to_slow) - C_slow_decomp

            # aggregate passive carbon pool flux
            # S.6.C.13
            layer.C_passive += (layer.C_slow_to_passive + layer.C_active_to_passive) - C_passive_decomp

    @staticmethod
    def __slow_carbon_to_active_amount() -> float:

        return slow_carbon_to_active_passive_co2 * (1 - percent_CO2_to_C_slow_loss - percent_C_slow_to_passive)

    # ---- S.6.C.8
    @staticmethod
    def _active_carbon_to_passive_amount(moisture_effect: float, temperature_effect: float, active_carbon: float,
                                         silt_clay_content: float,
                                         max_carbon_decomposition_rate: float = 0.14) -> float:
        # S.6.C.2
        active_carbon_to_slow_rate = max_carbon_decomposition_rate * (1 - 0.75 * silt_clay_content)
        # S.6.C.3
        active_carbon_decomposition_amount = \
            active_carbon_to_slow_rate * moisture_effect * temperature_effect * active_carbon

        return active_carbon_decomposition_amount * 0.004

    # ---- S.6.C.7
    @staticmethod
    def _active_carbon_to_slow_loss(moisture_effect: float, temperature_effect: float, active_carbon: float,
                                    silt_clay_content: float, max_carbon_decomposition_rate: float = 0.14) -> float:
        # S.6.C.2
        active_carbon_to_slow_rate = max_carbon_decomposition_rate * (1 - 0.75 * silt_clay_content)
        # S.6.C.3
        active_carbon_decomposition_amount = \
            active_carbon_to_slow_rate * moisture_effect * temperature_effect * active_carbon
        # S.6.C.4
        carbon_lost_adjusted_factor = 0.85 - 0.68 * silt_clay_content

        return active_carbon_decomposition_amount * carbon_lost_adjusted_factor

    # ---- S.6.C.7
    @staticmethod
    def _active_carbon_to_slow_amount(moisture_effect: float, temperature_effect: float, active_carbon: float,
                                      silt_clay_content: float, max_carbon_decomposition_rate: float = 0.14) -> float:
        # S.6.C.2
        active_carbon_to_slow_rate = max_carbon_decomposition_rate * (1 - 0.75 * silt_clay_content)
        # S.6.C.3
        active_carbon_decomposition_amount = \
            active_carbon_to_slow_rate * moisture_effect * temperature_effect * active_carbon
        # S.6.C.4
        carbon_lost_adjusted_factor = 0.85 - 0.68 * silt_clay_content

        return active_carbon_decomposition_amount * (1 - carbon_lost_adjusted_factor - 0.004)

    # ----  S.6.C.1
    @staticmethod
    def _plant_metabolic_active_carbon_loss(plant_metabolic_active_carbon_usage: float,
                                            metabolic_active_carbon_loss_rate: float = 0.55) -> float:
        return plant_metabolic_active_carbon_usage * metabolic_active_carbon_loss_rate

    @staticmethod
    def _plant_metabolic_active_carbon_remaining(plant_metabolic_active_carbon_usage: float,
                                                 metabolic_active_carbon_loss_rate: float = 0.55) -> float:
        return plant_metabolic_active_carbon_usage * (1 - metabolic_active_carbon_loss_rate)

    @staticmethod
    def _plant_structural_active_carbon_loss(plant_structural_active_carbon_usage: float,
                                             structural_active_carbon_loss_rate: float = 0.45) -> float:
        return plant_structural_active_carbon_usage * structural_active_carbon_loss_rate

    @staticmethod
    def _plant_structural_active_carbon_remaining(plant_structural_active_carbon_usage: float,
                                                  structural_active_carbon_loss_rate: float = 0.45) -> float:
        return plant_structural_active_carbon_usage * (1 - structural_active_carbon_loss_rate)

    @staticmethod
    def _plant_structural_slow_carbon_loss(plant_structural_slow_carbon_usage: float,
                                           structural_slow_carbon_loss_rate: float = 0.3) -> float:
        return plant_structural_slow_carbon_usage * structural_slow_carbon_loss_rate

    @staticmethod
    def _plant_structural_slow_carbon_remaining(plant_structural_slow_carbon_usage: float,
                                                structural_slow_carbon_loss_rate: float = 0.3) -> float:
        return plant_structural_slow_carbon_usage * (1 - structural_slow_carbon_loss_rate)

    @staticmethod
    def _soil_metabolic_active_carbon_loss(soil_metabolic_active_carbon_usage: float,
                                           metabolic_active_carbon_loss_rate: float = 0.55) -> float:
        return soil_metabolic_active_carbon_usage * metabolic_active_carbon_loss_rate

    @staticmethod
    def _soil_metabolic_active_carbon_remaining(soil_metabolic_active_carbon_usage: float,
                                                metabolic_active_carbon_loss_rate: float = 0.55) -> float:
        return soil_metabolic_active_carbon_usage * (1 - metabolic_active_carbon_loss_rate)

    @staticmethod
    def _soil_structural_active_carbon_loss(soil_structural_active_carbon_usage: float,
                                            structural_active_carbon_loss_rate: float = 0.45) -> float:
        return soil_structural_active_carbon_usage * structural_active_carbon_loss_rate

    @staticmethod
    def _soil_structural_active_carbon_remaining(soil_structural_active_carbon_usage: float,
                                                 structural_active_carbon_loss_rate: float = 0.45) -> float:
        return soil_structural_active_carbon_usage * (1 - structural_active_carbon_loss_rate)

    @staticmethod
    def _soil_structural_slow_carbon_loss(soil_structural_slow_carbon_usage: float,
                                          structural_slow_carbon_loss_rate: float = 0.3) -> float:
        return soil_structural_slow_carbon_usage * structural_slow_carbon_loss_rate

    @staticmethod
    def _soil_structural_slow_carbon_remaining(soil_structural_slow_carbon_usage: float,
                                               structural_slow_carbon_loss_rate: float = 0.3) -> float:
        return soil_structural_slow_carbon_usage * (1 - structural_slow_carbon_loss_rate)
