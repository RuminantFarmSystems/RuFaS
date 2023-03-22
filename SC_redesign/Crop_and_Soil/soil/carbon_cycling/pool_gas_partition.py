import math
from typing import Optional, List
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class PoolGasPartition:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    def partition_pool_gas(self):
        """
        main routine to update variable in all layers

        Returns: None

        """
        self.data.active_carbon_decomposition_rate = self._active_carbon_decomposition_rate(
            self.data.silt_clay_content)

        self.data.carbon_lost_adjusted_factor = self._carbon_lost_adjusted_factor(self.data.silt_clay_content)

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

            layer.active_carbon_decomposition_amount = self._active_carbon_decomposition_amount(
                layer.decomposition_moisture_effect, self.data.decomposition_temperature_effect,
                layer.active_carbon_amount, self.data.active_carbon_decomposition_rate
            )

            layer.slow_carbon_decomposition_amount = self._slow_carbon_decomposition_amount(
                layer.decomposition_moisture_effect, self.data.decomposition_temperature_effect,
                layer.slow_carbon_amount)

            layer.passive_carbon_decomposition_amount = self._passive_carbon_decomposition_amount(
                layer.decomposition_moisture_effect, self.data.decomposition_temperature_effect,
                layer.passive_carbon_amount)

            layer.active_carbon_to_slow_amount = self._active_carbon_to_slow_amount(
                layer.active_carbon_decomposition_amount, self.data.carbon_lost_adjusted_factor)

            layer.active_carbon_to_slow_loss = self._active_carbon_to_slow_loss(
                layer.active_carbon_decomposition_amount, self.data.carbon_lost_adjusted_factor)

            layer.active_carbon_to_passive_amount = self._active_carbon_to_passive_amount(
                layer.active_carbon_decomposition_amount
            )

            layer.slow_to_active_carbon_amount = self._slow_to_active_carbon_amount(
                layer.slow_carbon_decomposition_amount)
            layer.slow_carbon_co2_lost_amount = self._slow_carbon_co2_lost_amount(
                layer.slow_carbon_decomposition_amount)
            layer.slow_to_passive_carbon_amount = self._slow_to_passive_carbon_amount(
                layer.slow_carbon_decomposition_amount)

            layer.passive_to_active_carbon_amount = self._passive_to_active_carbon_amount(
                layer.passive_carbon_decomposition_amount)
            layer.passive_carbon_co2_lost_amount = self._passive_carbon_co2_lost_amount(
                layer.passive_carbon_decomposition_amount)
            # active, slow and lost CO2 pools

            # aggregate active carbon pool flux
            layer.plant_active_decompose_carbon = self._plant_active_decompose_carbon(
                layer.plant_metabolic_active_carbon_remaining, layer.plant_structural_active_carbon_remaining)
            layer.soil_active_decompose_carbon = self._soil_active_decompose_carbon(
                layer.plant_metabolic_active_carbon_remaining, layer.soil_structural_active_carbon_remaining)
            layer.active_carbon_amount = self._soil_active_carbon_amount(
                layer.active_carbon_amount, layer.plant_active_decompose_carbon, layer.soil_active_decompose_carbon,
                layer.passive_to_active_carbon_amount, layer.slow_to_active_carbon_amount,
                layer.active_carbon_decomposition_amount)
            # aggregate slow carbon pool flux

            layer.slow_carbon_amount = self._soil_slow_carbon_amount(
                layer.slow_carbon_amount, layer.plant_structural_slow_carbon_remaining,
                layer.soil_structural_slow_carbon_remaining, layer.active_carbon_to_slow_amount,
                layer.slow_carbon_decomposition_amount)
            # aggregate passive carbon pool flux
            layer.passive_carbon_amount = self._soil_passive_carbon_amount(
                layer.passive_carbon_amount, layer.slow_to_passive_carbon_amount,
                layer.active_carbon_to_passive_amount, layer.passive_carbon_decomposition_amount)

    @staticmethod
    def _soil_passive_carbon_amount(passive_carbon_amount: float, slow_to_passive_carbon_amount: float,
                                    active_carbon_to_passive_amount: float,
                                    passive_carbon_decomposition_amount: float) -> float:
        """
        Aggregate the total amount of passive carbon in the layer

        Args:
            passive_carbon_amount: passive carbon stored in the soil (kg/ha)
            slow_to_passive_carbon_amount: slow carbon decomposed into passive carbon (kg/ha)
            active_carbon_to_passive_amount: active carbon decomposed into passive carbon (kg/ha)
            passive_carbon_decomposition_amount: passive carbon decomposed into active or passive carbon and CO2 (kg/ha)

        Returns: Updated passive carbon stored in the soil (kg/ha)

        pseudocode_soil Reference: S.6.C.13

        """
        return passive_carbon_amount + slow_to_passive_carbon_amount + active_carbon_to_passive_amount - \
               passive_carbon_decomposition_amount

    # ---- S.6.C.12
    @staticmethod
    def _soil_slow_carbon_amount(slow_carbon_amount: float, plant_structural_slow_carbon_remaining: float,
                                 soil_structural_slow_carbon_remaining: float, active_carbon_to_slow_amount: float,
                                 slow_carbon_decomposition_amount: float):
        """
        Aggregate the total amount of slow carbon in the layer

        Args:
            slow_carbon_amount: slow carbon stored in the soil (kg/ha)
            plant_structural_slow_carbon_remaining:
                    plant metabolic carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha)
            soil_structural_slow_carbon_remaining:
                    soil structural carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha)
            active_carbon_to_slow_amount: active carbon decomposed into slow carbon (kg/ha)
            slow_carbon_decomposition_amount: slow carbon decomposed into active or passive carbon and CO2 (kg/ha)

        Returns: Updated slow carbon stored in the soil (kg/ha)

        pseudocode_soil Reference: S.6.C.12

        """
        return slow_carbon_amount + plant_structural_slow_carbon_remaining + soil_structural_slow_carbon_remaining + \
               active_carbon_to_slow_amount - slow_carbon_decomposition_amount

    # ---- S.6.C.11
    @staticmethod
    def _plant_active_decompose_carbon(plant_metabolic_active_carbon_remaining: float,
                                       plant_structural_active_carbon_remaining: float) -> float:
        """
        Calculates plant carbon decomposed into the active carbon pool (kg/ha)

        Args:
            plant_metabolic_active_carbon_remaining:
                    plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)
            plant_structural_active_carbon_remaining:
                    plant structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)

        Returns: Plant carbon decomposed into the active carbon pool (kg/ha)

        pseudocode_soil Reference: S.6.C.11
        """
        return plant_metabolic_active_carbon_remaining + plant_structural_active_carbon_remaining

    @staticmethod
    def _soil_active_decompose_carbon(soil_metabolic_active_carbon_remaining: float,
                                      soil_structural_active_carbon_remaining: float) -> float:
        """
        Calculates soil carbon decomposed into the active carbon pool (kg/ha)
        Args:
            soil_metabolic_active_carbon_remaining:
                    soil metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)
            soil_structural_active_carbon_remaining:
                    soil structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)

        Returns: Soil carbon decomposed into the active carbon pool (kg/ha)

        pseudocode_soil Reference: S.6.C.11
        """
        return soil_metabolic_active_carbon_remaining + soil_structural_active_carbon_remaining

    @staticmethod
    def _soil_active_carbon_amount(active_carbon_amount: float, plant_active_decompose_carbon: float,
                                   soil_active_decompose_carbon: float, passive_to_active_carbon_amount: float,
                                   slow_to_active_carbon_amount: float,
                                   active_carbon_decomposition_amount: float) -> float:
        """
        Aggregate the total amount of active carbon in the layer

        Args:
            active_carbon_amount: active carbon stored in the soil (kg/ha)
            plant_active_decompose_carbon: plant carbon decomposed into the active carbon pool (kg/ha)
            soil_active_decompose_carbon: soil carbon decomposed into the active carbon pool (kg/ha)
            passive_to_active_carbon_amount: passive carbon decomposed into active carbon (kg/ha)
            slow_to_active_carbon_amount: slow carbon decomposed into active carbon (kg/ha)
            active_carbon_decomposition_amount: active carbon decomposed into slow or passive carbon and CO2 (kg/ha)

        Returns: Updated active carbon stored in the soil (kg/ha)

        pseudocode_soil Reference: S.6.C.11
        """
        return active_carbon_amount + plant_active_decompose_carbon + soil_active_decompose_carbon \
               + slow_to_active_carbon_amount + passive_to_active_carbon_amount - active_carbon_decomposition_amount

    @staticmethod
    def _passive_to_active_carbon_amount(passive_carbon_decomposition_amount: float,
                                         passive_carbon_co2_lost_rate=0.55) -> float:
        """
        Calculates passive carbon decomposed into active carbon (kg/ha)

        Args:
            passive_carbon_decomposition_amount: passive carbon decomposed into active or passive carbon and CO2 (kg/ha)
            passive_carbon_co2_lost_rate: fraction of passive carbon lost as CO2 during decomposition (unitless)

        Returns: passive carbon decomposed into active carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.10
        """
        return passive_carbon_decomposition_amount * (1 - passive_carbon_co2_lost_rate)

    @staticmethod
    def _passive_carbon_co2_lost_amount(passive_carbon_decomposition_amount: float,
                                        passive_carbon_co2_lost_rate=0.55) -> float:
        """
        Calculates passive carbon lost as CO2 during decomposition (kg/ha)
        Args:
            passive_carbon_decomposition_amount: passive carbon decomposed into active or passive carbon and CO2 (kg/ha)
            passive_carbon_co2_lost_rate: fraction of passive carbon lost as CO2 during decomposition (unitless)

        Returns: passive carbon lost as CO2 during decomposition (kg/ha)
        pseudocode_soil Reference: S.6.C.10
        """
        return passive_carbon_decomposition_amount * passive_carbon_co2_lost_rate

    # TODO: Figure out where did 0.03 and 0.55 come from -- issue #398
    @staticmethod
    def _slow_to_active_carbon_amount(slow_carbon_decomposition_amount: float,
                                      slow_carbon_passive_decompose_rate=0.03,
                                      slow_carbon_co2_lost_rate=0.55) -> float:
        """
        Calculates slow carbon decomposed into active carbon (kg/ha)
        Args:
            slow_carbon_decomposition_amount: slow carbon decomposed into active or passive carbon and CO2 (kg/ha)
            slow_carbon_passive_decompose_rate: fraction of slow carbon decomposed into passive carbon (unitless)
            slow_carbon_co2_lost_rate: fraction of slow carbon lost as CO2 during decomposition (unitless)

        Returns: slow carbon decomposed into active carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.9
        """
        return slow_carbon_decomposition_amount * (1 - slow_carbon_co2_lost_rate - slow_carbon_passive_decompose_rate)

    @staticmethod
    def _slow_carbon_co2_lost_amount(slow_carbon_decomposition_amount: float, slow_carbon_co2_lost_rate=0.55) -> float:
        """
        Calculates slow carbon lost as CO2 during decomposition (kg/ha)
        Args:
            slow_carbon_decomposition_amount: slow carbon decomposed into active or passive carbon and CO2 (kg/ha)
            slow_carbon_co2_lost_rate: fraction of slow carbon lost as CO2 during decomposition (unitless)

        Returns: slow carbon lost as CO2 during decomposition (kg/ha)

        pseudocode_soil Reference: S.6.C.9
        """
        return slow_carbon_decomposition_amount * slow_carbon_co2_lost_rate

    @staticmethod
    def _slow_to_passive_carbon_amount(slow_carbon_decomposition_amount: float,
                                       slow_carbon_passive_decompose_rate=0.03) -> float:
        """
        Calculates slow carbon decomposed into passive carbon (kg/ha)
        Args:
            slow_carbon_decomposition_amount: slow carbon decomposed into active or passive carbon and CO2 (kg/ha)
            slow_carbon_passive_decompose_rate: fraction of slow carbon decomposed into passive carbon (unitless)

        Returns: slow carbon decomposed into passive carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.9
        """
        return slow_carbon_decomposition_amount * slow_carbon_passive_decompose_rate

    @staticmethod
    def _active_carbon_to_passive_amount(active_carbon_decomposition_amount: float) -> float:
        """
        Calculates active carbon decomposed into passive carbon (kg/ha)
        Args:
            active_carbon_decomposition_amount: active carbon decomposed into slow or passive carbon and CO2 (kg/ha)

        Returns: active carbon decomposed into passive carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.8
        """
        return active_carbon_decomposition_amount * 0.004

    # ---- S.6.C.7
    @staticmethod
    def _active_carbon_to_slow_loss(active_carbon_decomposition_amount: float, carbon_lost_adjusted_factor: float,
                                    ) -> float:
        """
        Calculate active carbon lost as CO2 during decomposition into slow carbon (kg/ha)
        Args:
            active_carbon_decomposition_amount: active carbon decomposed into slow or passive carbon and CO2 (kg/ha)
            carbon_lost_adjusted_factor: adjusted factor of CO2 loss from the decomposition of active carbon

        Returns: active carbon lost as CO2 during decomposition into slow carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.7
        """
        return active_carbon_decomposition_amount * carbon_lost_adjusted_factor

    @staticmethod
    def _active_carbon_to_slow_amount(active_carbon_decomposition_amount: float, carbon_lost_adjusted_factor: float,
                                      ) -> float:
        """
        Calculate active carbon decomposed into slow carbon (kg/ha)
        Args:
            active_carbon_decomposition_amount: active carbon decomposed into slow or passive carbon and CO2 (kg/ha)
            carbon_lost_adjusted_factor: adjusted factor of CO2 loss from the decomposition of active carbon

        Returns: active carbon decomposed into slow carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.7
        """
        return active_carbon_decomposition_amount * (1 - carbon_lost_adjusted_factor - 0.004)

    @staticmethod
    def _carbon_lost_adjusted_factor(silt_clay_content: float) -> float:
        """
        Calculates adjusted factor of CO2 loss from the decomposition of active carbon
        Args:
            silt_clay_content: fraction of silt and clay content in the soil (unitless)

        Returns: adjusted factor of CO2 loss from the decomposition of active carbon

        pseudocode_soil Reference: S.6.C.6
        """
        return 0.85 - 0.68 * silt_clay_content

    # ---- S.6.C.5
    @staticmethod
    def _passive_carbon_decomposition_amount(
            decomposition_moisture_effect: float, decomposition_temperature_effect: float,
            passive_carbon_amount: float, passive_carbon_decomposition_factor=0.00013) -> float:
        """
        Caluculates passive carbon decomposed into active or passive carbon and CO2 (kg/ha)
        Args:
            decomposition_moisture_effect: moisture effect on decomposition factor (unitless) (pseudocode_soil S.6.A.2)
            decomposition_temperature_effect:
                                        temperature effect on decomposition factor (unitless) (pseudocode_soil S.6.A.1)
            passive_carbon_amount: passive carbon stored in the soil (kg/ha)
            passive_carbon_decomposition_factor: passive carbon decomposition factor

        Returns: passive carbon decomposed into active or passive carbon and CO2 (kg/ha)

        pseudocode_soil Reference: S.6.C.5
        """
        return decomposition_moisture_effect * decomposition_temperature_effect * passive_carbon_amount * \
               passive_carbon_decomposition_factor

    # ---- S.6.C.4
    @staticmethod
    def _slow_carbon_decomposition_amount(
            decomposition_moisture_effect: float, decomposition_temperature_effect: float,
            slow_carbon_amount: float, slow_carbon_decomposition_factor=0.0038) -> float:
        """
        Calculates slow carbon decomposed into active or passive carbon and CO2 (kg/ha)
        Args:
            decomposition_moisture_effect: moisture effect on decomposition factor (unitless) (pseudocode_soil S.6.A.2)
            decomposition_temperature_effect:
                                        temperature effect on decomposition factor (unitless) (pseudocode_soil S.6.A.1)
            slow_carbon_amount: slow carbon stored in the soil (kg/ha)
            slow_carbon_decomposition_factor: slow carbon decomposition factor

        Returns: slow carbon decomposed into active or passive carbon and CO2 (kg/ha)

        pseudocode_soil Reference: S.6.C.4
        """
        return decomposition_moisture_effect * decomposition_temperature_effect * slow_carbon_amount * \
               slow_carbon_decomposition_factor

    # ---- S.6.C.3
    @staticmethod
    def _active_carbon_decomposition_amount(moisture_effect: float, temperature_effect: float,
                                            active_carbon: float, active_carbon_decomposition_rate: float) -> float:
        """
        Calculates active carbon decomposed into slow or passive carbon and CO2 (kg/ha)
        Args:
            moisture_effect: moisture effect on decomposition factor (unitless) (pseudocode_soil S.6.A.2)
            temperature_effect: temperature effect on decomposition factor (unitless) (pseudocode_soil S.6.A.1)
            active_carbon: active carbon stored in the soil (kg/ha)
            active_carbon_decomposition_rate: active carbon decomposition factor (unitless)

        Returns: active carbon decomposed into slow or passive carbon and CO2 (kg/ha)

        pseudocode_soil Reference: S.6.C.3
        """
        return active_carbon_decomposition_rate * moisture_effect * temperature_effect * active_carbon

    # ---- S.6.C.2
    @staticmethod
    def _active_carbon_decomposition_rate(silt_clay_content: float,
                                          max_carbon_decomposition_rate: float = 0.14) -> float:
        """
        Calculates rate at which active carbon is decomposed into slow or passive carbon and CO2
        Args:
            silt_clay_content: silt and clay content in the soil (%)
            max_carbon_decomposition_rate: maximum rate of carbon decomposition (unitless)

        Returns: rate at which active carbon is decomposed into slow or passive carbon and CO2 (unitless)

        pseudocode_soil Reference: S.6.C.2
        """
        return max_carbon_decomposition_rate * (1 - 0.75 * silt_clay_content)

    # ----  S.6.C.1
    @staticmethod
    def _plant_metabolic_active_carbon_loss(plant_metabolic_active_carbon_usage: float,
                                            metabolic_active_carbon_loss_rate: float = 0.55) -> float:
        """
        Calculates plant metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)
        Args:
            plant_metabolic_active_carbon_usage: plant metabolic carbon decomposed into active carbon (kg/ha)
            metabolic_active_carbon_loss_rate: rate of carbon dioxide loss during transformation of metabolic to
                                                                                                        active carbon

        Returns: plant metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return plant_metabolic_active_carbon_usage * metabolic_active_carbon_loss_rate

    @staticmethod
    def _plant_metabolic_active_carbon_remaining(plant_metabolic_active_carbon_usage: float,
                                                 metabolic_active_carbon_loss_rate: float = 0.55) -> float:
        """
        Calculates plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)
        Args:
            plant_metabolic_active_carbon_usage: plant metabolic carbon decomposed into active carbon (kg/ha)
            metabolic_active_carbon_loss_rate: rate of carbon dioxide loss during transformation of metabolic to
                                                                                                        active carbon

        Returns: plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return plant_metabolic_active_carbon_usage * (1 - metabolic_active_carbon_loss_rate)

    @staticmethod
    def _plant_structural_active_carbon_loss(plant_structural_active_carbon_usage: float,
                                             structural_active_carbon_loss_rate: float = 0.45) -> float:
        """
        Calculates plant structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)
        Args:
            plant_structural_active_carbon_usage: plant structural carbon decomposed into active carbon (kg/ha)
            structural_active_carbon_loss_rate: rate of carbon dioxide loss during transformation of structural to
                                                                                                        active carbon

        Returns: plant structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return plant_structural_active_carbon_usage * structural_active_carbon_loss_rate

    @staticmethod
    def _plant_structural_active_carbon_remaining(plant_structural_active_carbon_usage: float,
                                                  structural_active_carbon_loss_rate: float = 0.45) -> float:
        """
        Calculates plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)
        Args:
            plant_structural_active_carbon_usage: plant structural carbon decomposed into active carbon (kg/ha)
            structural_active_carbon_loss_rate:  rate of carbon dioxide loss during transformation of structural to
                                                                                                        active carbon

        Returns: plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return plant_structural_active_carbon_usage * (1 - structural_active_carbon_loss_rate)

    @staticmethod
    def _plant_structural_slow_carbon_loss(plant_structural_slow_carbon_usage: float,
                                           structural_slow_carbon_loss_rate: float = 0.3) -> float:
        """
        Calculates plant structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha)
        Args:
            plant_structural_slow_carbon_usage: plant structural carbon decomposed into slow carbon (kg/ha)
            structural_slow_carbon_loss_rate:  rate of carbon dioxide loss during transformation of structural to
                                                                                                            slow carbon

        Returns: plant structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return plant_structural_slow_carbon_usage * structural_slow_carbon_loss_rate

    @staticmethod
    def _plant_structural_slow_carbon_remaining(plant_structural_slow_carbon_usage: float,
                                                structural_slow_carbon_loss_rate: float = 0.3) -> float:
        """
        Calculates plant metabolic carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha)
        Args:
            plant_structural_slow_carbon_usage: plant structural carbon decomposed into slow carbon (kg/ha)
            structural_slow_carbon_loss_rate: rate of carbon dioxide loss during transformation of structural to
                                                                                                            slow carbon

        Returns: plant metabolic carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return plant_structural_slow_carbon_usage * (1 - structural_slow_carbon_loss_rate)

    @staticmethod
    def _soil_metabolic_active_carbon_loss(soil_metabolic_active_carbon_usage: float,
                                           metabolic_active_carbon_loss_rate: float = 0.55) -> float:
        """
        Calculates soil metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)
        Args:
            soil_metabolic_active_carbon_usage: soil metabolic carbon decomposed into active carbon (kg/ha)
            metabolic_active_carbon_loss_rate:  rate of carbon dioxide loss during transformation of metabolic to
                                                                                                        active carbon

        Returns: soil metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return soil_metabolic_active_carbon_usage * metabolic_active_carbon_loss_rate

    @staticmethod
    def _soil_metabolic_active_carbon_remaining(soil_metabolic_active_carbon_usage: float,
                                                metabolic_active_carbon_loss_rate: float = 0.55) -> float:
        """
        Calculates soil metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)
        Args:
           soil_metabolic_active_carbon_usage: soil metabolic carbon decomposed into active carbon (kg/ha)
            metabolic_active_carbon_loss_rate:  rate of carbon dioxide loss during transformation of metabolic to
                                                                                                        active carbon

        Returns: soil metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return soil_metabolic_active_carbon_usage * (1 - metabolic_active_carbon_loss_rate)

    @staticmethod
    def _soil_structural_active_carbon_loss(soil_structural_active_carbon_usage: float,
                                            structural_active_carbon_loss_rate: float = 0.45) -> float:
        """
        Calculates soil structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)
        Args:
            soil_structural_active_carbon_usage: soil structural carbon decomposed into active carbon (kg/ha)
            structural_active_carbon_loss_rate: rate of carbon dioxide loss during transformation of structural to
                                                                                                        active carbon

        Returns: soil structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return soil_structural_active_carbon_usage * structural_active_carbon_loss_rate

    @staticmethod
    def _soil_structural_active_carbon_remaining(soil_structural_active_carbon_usage: float,
                                                 structural_active_carbon_loss_rate: float = 0.45) -> float:
        """
        Calculates soil structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)
        Args:
            soil_structural_active_carbon_usage: soil structural carbon decomposed into active carbon (kg/ha)
            structural_active_carbon_loss_rate: rate of carbon dioxide loss during transformation of structural to
                                                                                                        active carbon
        Returns: soil structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return soil_structural_active_carbon_usage * (1 - structural_active_carbon_loss_rate)

    @staticmethod
    def _soil_structural_slow_carbon_loss(soil_structural_slow_carbon_usage: float,
                                          structural_slow_carbon_loss_rate: float = 0.3) -> float:
        """
        Calculates soil structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha)
        Args:
            soil_structural_slow_carbon_usage: soil structural carbon decomposed into slow carbon (kg/ha)
            structural_slow_carbon_loss_rate: rate of carbon dioxide loss during transformation of structural to
                                                                                                            slow carbon

        Returns: soil structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return soil_structural_slow_carbon_usage * structural_slow_carbon_loss_rate

    @staticmethod
    def _soil_structural_slow_carbon_remaining(soil_structural_slow_carbon_usage: float,
                                               structural_slow_carbon_loss_rate: float = 0.3) -> float:
        """
        Calculates soil structural carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha)
        Args:
            soil_structural_slow_carbon_usage: soil structural carbon decomposed into slow carbon (kg/ha)
            structural_slow_carbon_loss_rate: rate of carbon dioxide loss during transformation of structural to
                                                                                                slow carbon (unitless)

        Returns: soil structural carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha)

        pseudocode_soil Reference: S.6.C.1
        """
        return soil_structural_slow_carbon_usage * (1 - structural_slow_carbon_loss_rate)
