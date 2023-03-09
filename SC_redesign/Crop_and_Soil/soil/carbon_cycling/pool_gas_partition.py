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

            # S.6.C.2
            self.data.active_carbon_decomposition_rate = self._active_carbon_decomposition_rate(
                self.data.silt_clay_content)

            # S.6.C.3
            layer.active_carbon_decomposition_amount = self._active_carbon_decomposition_amount(
                layer.decomposition_moisture_effect, self.data.decomposition_temperature_effect,
                layer.active_carbon_amount, self.data.active_carbon_decomposition_rate
            )

            # S.6.C.4
            layer.slow_carbon_decomposition_amount = self._slow_carbon_decomposition_amount(
                layer.decomposition_moisture_effect, self.data.decomposition_temperature_effect,
                layer.slow_carbon_amount)

            # S.6.C.5
            layer.passive_carbon_decomposition_amount = self._passive_carbon_decomposition_amount(
                layer.decomposition_moisture_effect, self.data.decomposition_temperature_effect,
                layer.passive_carbon_amount)

            # S.6.C.6
            self.data.carbon_lost_adjusted_factor = self._carbon_lost_adjusted_factor(self.data.silt_clay_content)

            # S.6.C.7
            layer.active_carbon_to_slow_amount = self._active_carbon_to_slow_amount(
                layer.active_carbon_decomposition_amount, self.data.carbon_lost_adjusted_factor)

            layer.active_carbon_to_slow_loss = self._active_carbon_to_slow_loss(
                layer.active_carbon_decomposition_amount, self.data.carbon_lost_adjusted_factor)

            # S.6.C.8
            layer.active_carbon_to_passive_amount = self._active_carbon_to_passive_amount(
                layer.active_carbon_decomposition_amount
            )
            # S.6.C.9
            layer.slow_to_active_carbon_amount = self._slow_to_active_carbon_amount(
                layer.slow_carbon_decomposition_amount)
            layer.slow_carbon_co2_lost_amount = self._slow_carbon_co2_lost_amount(
                layer.slow_carbon_decomposition_amount)
            layer.slow_to_passive_carbon_amount = self._slow_to_passive_carbon_amount(
                layer.slow_carbon_decomposition_amount)

            # S.6.C.10
            layer.passive_to_active_carbon_amount = self._passive_to_active_carbon_amount(
                layer.passive_carbon_decomposition_amount)
            layer.passive_carbon_co2_lost_amount = self._passive_carbon_co2_lost_amount(
                layer.passive_carbon_decomposition_amount)
            # active, slow and lost CO2 pools

            # aggregate active carbon pool flux
            # S.6.C.11
            layer.plant_active_decompose_carbon = self._plant_active_decompose_carbon(
                layer.plant_metabolic_active_carbon_remaining, layer.plant_structural_active_carbon_remaining)
            layer.soil_active_decompose_carbon = self._soil_active_decompose_carbon(
                layer.plant_metabolic_active_carbon_remaining, layer.soil_structural_active_carbon_remaining)
            layer.active_carbon_amount = self._soil_active_carbon_amount(
                layer.active_carbon_amount, layer.plant_active_decompose_carbon, layer.soil_active_decompose_carbon,
                layer.passive_to_active_carbon_amount, layer.slow_to_active_carbon_amount,
                layer.active_carbon_decomposition_amount)
            # aggregate slow carbon pool flux

            # S.6.C.12
            layer.slow_carbon_amount = self._soil_slow_carbon_amount(
                layer.slow_carbon_amount, layer.plant_structural_slow_carbon_remaining,
                layer.soil_structural_slow_carbon_remaining, layer.active_carbon_to_slow_amount,
                layer.slow_carbon_decomposition_amount)
            # aggregate passive carbon pool flux
            # S.6.C.13
            layer.passive_carbon_amount = self._soil_passive_carbon_amount(
                layer.passive_carbon_amount, layer.slow_to_passive_carbon_amount,
                layer.active_carbon_to_passive_amount, layer.passive_carbon_decomposition_amount)

    # ---- S.6.C.13
    @staticmethod
    def _soil_passive_carbon_amount(passive_carbon_amount: float, slow_to_passive_carbon_amount: float,
                                    active_carbon_to_passive_amount: float,
                                    passive_carbon_decomposition_amount: float) -> float:
        return passive_carbon_amount + slow_to_passive_carbon_amount + active_carbon_to_passive_amount - \
               passive_carbon_decomposition_amount

    # ---- S.6.C.12
    @staticmethod
    def _soil_slow_carbon_amount(slow_carbon_amount: float, plant_structural_slow_carbon_remaining: float,
                                 soil_structural_slow_carbon_remaining: float, active_carbon_to_slow_amount: float,
                                 slow_carbon_decomposition_amount: float):
        return slow_carbon_amount + plant_structural_slow_carbon_remaining + soil_structural_slow_carbon_remaining + \
               active_carbon_to_slow_amount - slow_carbon_decomposition_amount

    # ---- S.6.C.11
    @staticmethod
    def _plant_active_decompose_carbon(plant_metabolic_active_carbon_remaining: float,
                                       plant_structural_active_carbon_remaining: float) -> float:
        return plant_metabolic_active_carbon_remaining + plant_structural_active_carbon_remaining

    @staticmethod
    def _soil_active_decompose_carbon(soil_metabolic_active_carbon_remaining: float,
                                      soil_structural_active_carbon_remaining: float) -> float:
        return soil_metabolic_active_carbon_remaining + soil_structural_active_carbon_remaining

    @staticmethod
    def _soil_active_carbon_amount(active_carbon_amount: float, plant_active_decompose_carbon: float,
                                   soil_active_decompose_carbon: float, passive_to_active_carbon_amount: float,
                                   slow_to_active_carbon_amount: float,
                                   active_carbon_decomposition_amount: float) -> float:
        return active_carbon_amount + plant_active_decompose_carbon + soil_active_decompose_carbon \
               + slow_to_active_carbon_amount + passive_to_active_carbon_amount - active_carbon_decomposition_amount

    # ---- S.6.C.10
    @staticmethod
    def _passive_to_active_carbon_amount(passive_carbon_decomposition_amount: float,
                                         passive_carbon_co2_lost_rate=0.55) -> float:
        return passive_carbon_decomposition_amount * (1 - passive_carbon_co2_lost_rate)

    @staticmethod
    def _passive_carbon_co2_lost_amount(passive_carbon_decomposition_amount: float,
                                        passive_carbon_co2_lost_rate=0.55) -> float:
        return passive_carbon_decomposition_amount * passive_carbon_co2_lost_rate

    # ---- S.6.C.9
    # TODO: Figure out where did 0.03 and 0.55 come from
    @staticmethod
    def _slow_to_active_carbon_amount(slow_carbon_decomposition_amount: float,
                                      slow_carbon_passive_decompose_rate=0.03,
                                      slow_carbon_co2_lost_rate=0.55) -> float:
        return slow_carbon_decomposition_amount * (1 - slow_carbon_co2_lost_rate - slow_carbon_passive_decompose_rate)

    @staticmethod
    def _slow_carbon_co2_lost_amount(slow_carbon_decomposition_amount: float, slow_carbon_co2_lost_rate=0.55) -> float:
        return slow_carbon_decomposition_amount * slow_carbon_co2_lost_rate

    @staticmethod
    def _slow_to_passive_carbon_amount(slow_carbon_decomposition_amount: float,
                                       slow_carbon_passive_decompose_rate=0.03) -> float:
        return slow_carbon_decomposition_amount * slow_carbon_passive_decompose_rate

    # ---- S.6.C.5
    @staticmethod
    def _passive_carbon_decomposition_amount(
            decomposition_moisture_effect: float, decomposition_temperature_effect: float,
            passive_carbon_amount: float, passive_carbon_decomposition_factor=0.00013) -> float:
        return decomposition_moisture_effect * decomposition_temperature_effect * passive_carbon_amount * \
               passive_carbon_decomposition_factor

    # ---- S.6.C.4
    @staticmethod
    def _slow_carbon_decomposition_amount(
            decomposition_moisture_effect: float, decomposition_temperature_effect: float,
            slow_carbon_amount: float, slow_carbon_decomposition_factor=0.0038) -> float:
        return decomposition_moisture_effect * decomposition_temperature_effect * slow_carbon_amount * \
               slow_carbon_decomposition_factor

    # ---- S.6.C.8
    @staticmethod
    def _active_carbon_to_passive_amount(active_carbon_decomposition_amount: float) -> float:
        return active_carbon_decomposition_amount * 0.004

    # ---- S.6.C.7
    @staticmethod
    def _active_carbon_to_slow_loss(active_carbon_decomposition_amount: float, carbon_lost_adjusted_factor: float,
                                    ) -> float:
        return active_carbon_decomposition_amount * carbon_lost_adjusted_factor

    @staticmethod
    def _active_carbon_to_slow_amount(active_carbon_decomposition_amount: float, carbon_lost_adjusted_factor: float,
                                      ) -> float:
        return active_carbon_decomposition_amount * (1 - carbon_lost_adjusted_factor - 0.004)

    # ---- S.6.C.6
    @staticmethod
    def _carbon_lost_adjusted_factor(silt_clay_content: float) -> float:
        return 0.85 - 0.68 * silt_clay_content

    # ---- S.6.C.3
    @staticmethod
    def _active_carbon_decomposition_amount(moisture_effect: float, temperature_effect: float,
                                            active_carbon: float, active_carbon_decomposition_rate: float) -> float:
        return active_carbon_decomposition_rate * moisture_effect * temperature_effect * active_carbon

    # ---- S.6.C.2
    @staticmethod
    def _active_carbon_decomposition_rate(silt_clay_content: float,
                                          max_carbon_decomposition_rate: float = 0.14) -> float:
        return max_carbon_decomposition_rate * (1 - 0.75 * silt_clay_content)
    # TODO:---------test everything above

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
