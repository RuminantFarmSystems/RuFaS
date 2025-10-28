from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class PoolGasPartition:
    """
    Manages the partitioning of carbon between different soil pools and the atmosphere,
    contributing to the overall carbon cycling within a field.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track carbon in the soil profile, creates new one if one is not
        provided.
    field_size : float, optional
        Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
        not provided (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData object used by this module to track carbon in the soil profile, creates new one if one is not
        provided.

    References
    -------
    pseudocode_soil S.6.C.1 to S.6.C.13

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def partition_pool_gas(self):
        """
        Main routine to update variables associated with gas partitioning in all layers.

        Notes
        ------
        This method applies all the gas-partitioning sub routines to each layer of soil that is present in the soil
        `data` object.

        """
        layer = self.data.soil_layers[0]
        layer.active_carbon_decomposition_rate = self._determine_active_carbon_decomposition_rate(
            layer.silt_clay_content
        )

        layer.carbon_lost_adjusted_factor = self._determine_carbon_lost_adjusted_factor(layer.silt_clay_content)

        # ---- plants
        layer.plant_metabolic_active_carbon_loss = self._determine_plant_metabolic_active_carbon_loss(
            layer.plant_metabolic_active_carbon_usage
        )
        layer.plant_metabolic_active_carbon_remaining = self._determine_plant_metabolic_active_carbon_remaining(
            layer.plant_metabolic_active_carbon_usage
        )

        # above ground structural C
        layer.plant_structural_active_carbon_loss = self._determine_plant_structural_active_carbon_loss(
            layer.plant_structural_active_carbon_usage
        )
        layer.plant_structural_active_carbon_remaining = self._determine_plant_structural_active_carbon_remaining(
            layer.plant_structural_active_carbon_usage
        )

        layer.plant_structural_slow_carbon_loss = self._determine_plant_structural_slow_carbon_loss(
            layer.plant_structural_slow_carbon_usage
        )
        layer.plant_structural_slow_carbon_remaining = self._determine_plant_structural_slow_carbon_remaining(
            layer.plant_structural_slow_carbon_usage
        )

        layer.active_carbon_decomposition_amount = self._determine_active_carbon_decomposition_amount(
            layer.decomposition_moisture_effect,
            layer.decomposition_temperature_effect,
            layer.active_carbon_amount,
            layer.active_carbon_decomposition_rate,
        )

        layer.slow_carbon_decomposition_amount = self._determine_slow_carbon_decomposition_amount(
            layer.decomposition_moisture_effect,
            layer.decomposition_temperature_effect,
            layer.slow_carbon_amount,
        )

        layer.passive_carbon_decomposition_amount = 0.0

        layer.active_carbon_to_slow_amount = self._determine_active_carbon_to_slow_amount(
            layer.active_carbon_decomposition_amount,
            layer.carbon_lost_adjusted_factor,
        )

        layer.active_carbon_to_slow_loss = self._determine_active_carbon_to_slow_loss(
            layer.active_carbon_decomposition_amount, layer.carbon_lost_adjusted_factor
        )

        layer.slow_to_active_carbon_amount = self._determine_slow_to_active_carbon_amount(
            layer.slow_carbon_decomposition_amount
        )
        layer.slow_carbon_co2_lost_amount = self._determine_slow_carbon_co2_lost_amount(
            layer.slow_carbon_decomposition_amount
        )

        # aggregate active carbon pool flux
        layer.plant_active_decompose_carbon = self._determine_plant_active_decompose_carbon(
            layer.plant_metabolic_active_carbon_remaining,
            layer.plant_structural_active_carbon_remaining,
        )
        layer.soil_active_decompose_carbon = 0.0
        layer.active_carbon_amount = self._determine_soil_active_carbon_amount(
            layer.active_carbon_amount,
            layer.plant_active_decompose_carbon,
            layer.soil_active_decompose_carbon,
            layer.passive_to_active_carbon_amount,
            layer.slow_to_active_carbon_amount,
            layer.active_carbon_decomposition_amount,
        )
        # aggregate slow carbon pool flux

        layer.slow_carbon_amount = self._determine_soil_slow_carbon_amount(
            layer.slow_carbon_amount,
            layer.plant_structural_slow_carbon_remaining,
            layer.soil_structural_slow_carbon_remaining,
            layer.active_carbon_to_slow_amount,
            layer.slow_carbon_decomposition_amount,
        )

        for layer in self.data.soil_layers[1:]:
            layer.active_carbon_decomposition_rate = self._determine_active_carbon_decomposition_rate(
                layer.silt_clay_content
            )

            layer.carbon_lost_adjusted_factor = self._determine_carbon_lost_adjusted_factor(layer.silt_clay_content)

            # ----- soil
            layer.soil_metabolic_active_carbon_loss = self._determine_soil_metabolic_active_carbon_loss(
                layer.soil_metabolic_active_carbon_usage
            )
            layer.soil_metabolic_active_carbon_remaining = self._determine_soil_metabolic_active_carbon_remaining(
                layer.soil_metabolic_active_carbon_usage
            )

            # below ground structural C
            layer.soil_structural_active_carbon_loss = self._determine_soil_structural_active_carbon_loss(
                layer.soil_structural_active_carbon_usage
            )
            layer.soil_structural_active_carbon_remaining = self._determine_soil_structural_active_carbon_remaining(
                layer.soil_structural_active_carbon_usage
            )

            layer.soil_structural_slow_carbon_loss = self._determine_soil_structural_slow_carbon_loss(
                layer.soil_structural_slow_carbon_usage
            )
            layer.soil_structural_slow_carbon_remaining = self._determine_soil_structural_slow_carbon_remaining(
                layer.soil_structural_slow_carbon_usage
            )

            layer.active_carbon_decomposition_amount = self._determine_active_carbon_decomposition_amount(
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.active_carbon_amount,
                layer.active_carbon_decomposition_rate,
            )

            layer.slow_carbon_decomposition_amount = self._determine_slow_carbon_decomposition_amount(
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.slow_carbon_amount,
            )

            layer.passive_carbon_decomposition_amount = self._determine_passive_carbon_decomposition_amount(
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.passive_carbon_amount,
            )

            layer.active_carbon_to_slow_amount = self._determine_active_carbon_to_slow_amount(
                layer.active_carbon_decomposition_amount,
                layer.carbon_lost_adjusted_factor,
            )

            layer.active_carbon_to_slow_loss = self._determine_active_carbon_to_slow_loss(
                layer.active_carbon_decomposition_amount,
                layer.carbon_lost_adjusted_factor,
            )

            layer.active_carbon_to_passive_amount = self._determine_active_carbon_to_passive_amount(
                layer.active_carbon_decomposition_amount
            )

            layer.slow_to_active_carbon_amount = self._determine_slow_to_active_carbon_amount(
                layer.slow_carbon_decomposition_amount
            )
            layer.slow_carbon_co2_lost_amount = self._determine_slow_carbon_co2_lost_amount(
                layer.slow_carbon_decomposition_amount
            )
            layer.slow_to_passive_carbon_amount = self._determine_slow_to_passive_carbon_amount(
                layer.slow_carbon_decomposition_amount
            )

            layer.passive_to_active_carbon_amount = self._determine_passive_to_active_carbon_amount(
                layer.passive_carbon_decomposition_amount
            )
            layer.passive_carbon_co2_lost_amount = self._determine_passive_carbon_co2_lost_amount(
                layer.passive_carbon_decomposition_amount
            )
            # active, slow and lost CO2 pools

            # aggregate active carbon pool flux
            layer.plant_active_decompose_carbon = self._determine_plant_active_decompose_carbon(
                layer.plant_metabolic_active_carbon_remaining,
                layer.plant_structural_active_carbon_remaining,
            )
            layer.soil_active_decompose_carbon = self._determine_soil_active_decompose_carbon(
                layer.plant_metabolic_active_carbon_remaining,
                layer.soil_structural_active_carbon_remaining,
            )
            layer.active_carbon_amount = self._determine_soil_active_carbon_amount(
                layer.active_carbon_amount,
                layer.plant_active_decompose_carbon,
                layer.soil_active_decompose_carbon,
                layer.passive_to_active_carbon_amount,
                layer.slow_to_active_carbon_amount,
                layer.active_carbon_decomposition_amount,
            )
            # aggregate slow carbon pool flux

            layer.slow_carbon_amount = self._determine_soil_slow_carbon_amount(
                layer.slow_carbon_amount,
                layer.plant_structural_slow_carbon_remaining,
                layer.soil_structural_slow_carbon_remaining,
                layer.active_carbon_to_slow_amount,
                layer.slow_carbon_decomposition_amount,
            )
            # aggregate passive carbon pool flux
            layer.passive_carbon_amount = self._determine_soil_passive_carbon_amount(
                layer.passive_carbon_amount,
                layer.slow_to_passive_carbon_amount,
                layer.active_carbon_to_passive_amount,
                layer.passive_carbon_decomposition_amount,
            )

    @staticmethod
    def _determine_soil_passive_carbon_amount(
        passive_carbon_amount: float,
        slow_to_passive_carbon_amount: float,
        active_carbon_to_passive_amount: float,
        passive_carbon_decomposition_amount: float,
    ) -> float:
        """
        Aggregate the total amount of passive carbon in the layer.

        This function updates the passive carbon stored in the soil based on the provided inputs.

        Parameters
        ----------
        passive_carbon_amount : float
            Passive carbon stored in the soil (kg/ha).
        slow_to_passive_carbon_amount : float
            Slow carbon decomposed into passive carbon (kg/ha).
        active_carbon_to_passive_amount : float
            Active carbon decomposed into passive carbon (kg/ha).
        passive_carbon_decomposition_amount : float
            Passive carbon decomposed into active or passive carbon and CO2 (kg/ha).

        Returns
        -------
        float
            Updated passive carbon stored in the soil (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.13.

        """
        return (
            passive_carbon_amount
            + slow_to_passive_carbon_amount
            + active_carbon_to_passive_amount
            - passive_carbon_decomposition_amount
        )

    # ---- S.6.C.12
    @staticmethod
    def _determine_soil_slow_carbon_amount(
        slow_carbon_amount: float,
        plant_structural_slow_carbon_remaining: float,
        soil_structural_slow_carbon_remaining: float,
        active_carbon_to_slow_amount: float,
        slow_carbon_decomposition_amount: float,
    ):
        """
        Aggregate the total amount of slow carbon in the layer.

        This function updates the slow carbon stored in the soil based on the provided inputs.

        Parameters
        ----------
        slow_carbon_amount : float
            Slow carbon stored in the soil (kg/ha).
        plant_structural_slow_carbon_remaining : float
            Plant metabolic carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha).
        soil_structural_slow_carbon_remaining : float
            Soil structural carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha).
        active_carbon_to_slow_amount : float
            Active carbon decomposed into slow carbon (kg/ha).
        slow_carbon_decomposition_amount : float
            Slow carbon decomposed into active or passive carbon and CO2 (kg/ha).

        Returns
        -------
        float
            Updated slow carbon stored in the soil (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.12.

        """
        return (
            slow_carbon_amount
            + plant_structural_slow_carbon_remaining
            + soil_structural_slow_carbon_remaining
            + active_carbon_to_slow_amount
            - slow_carbon_decomposition_amount
        )

    # ---- S.6.C.11
    @staticmethod
    def _determine_plant_active_decompose_carbon(
        plant_metabolic_active_carbon_remaining: float,
        plant_structural_active_carbon_remaining: float,
    ) -> float:
        """
        Calculate plant carbon decomposed into the active carbon pool in the layer (kg/ha).

        Parameters
        ----------
        plant_metabolic_active_carbon_remaining : float
            Plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).
        plant_structural_active_carbon_remaining : float
            Plant structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).

        Returns
        -------
        float
            Plant carbon decomposed into the active carbon pool (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.11.

        """
        return plant_metabolic_active_carbon_remaining + plant_structural_active_carbon_remaining

    @staticmethod
    def _determine_soil_active_decompose_carbon(
        soil_metabolic_active_carbon_remaining: float,
        soil_structural_active_carbon_remaining: float,
    ) -> float:
        """
        Calculate soil carbon decomposed into the active carbon pool in the layer (kg/ha).

        Parameters
        ----------
        soil_metabolic_active_carbon_remaining : float
            Soil metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).
        soil_structural_active_carbon_remaining : float
            Soil structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).

        Returns
        -------
        float
            Soil carbon decomposed into the active carbon pool (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.11.

        """
        return soil_metabolic_active_carbon_remaining + soil_structural_active_carbon_remaining

    @staticmethod
    def _determine_soil_active_carbon_amount(
        active_carbon_amount: float,
        plant_active_decompose_carbon: float,
        soil_active_decompose_carbon: float,
        passive_to_active_carbon_amount: float,
        slow_to_active_carbon_amount: float,
        active_carbon_decomposition_amount: float,
    ) -> float:
        """
        Aggregate the total amount of active carbon in the layer.

        Parameters
        ----------
        active_carbon_amount : float
            Active carbon stored in the soil (kg/ha).
        plant_active_decompose_carbon : float
            Plant carbon decomposed into the active carbon pool (kg/ha).
        soil_active_decompose_carbon : float
            Soil carbon decomposed into the active carbon pool (kg/ha).
        passive_to_active_carbon_amount : float
            Passive carbon decomposed into active carbon (kg/ha).
        slow_to_active_carbon_amount : float
            Slow carbon decomposed into active carbon (kg/ha).
        active_carbon_decomposition_amount : float
            Active carbon decomposed into slow or passive carbon and CO2 (kg/ha).

        Returns
        -------
        float
            Updated active carbon stored in the soil (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.11.

        """
        return (
            active_carbon_amount
            + plant_active_decompose_carbon
            + soil_active_decompose_carbon
            + slow_to_active_carbon_amount
            + passive_to_active_carbon_amount
            - active_carbon_decomposition_amount
        )

    @staticmethod
    def _determine_passive_to_active_carbon_amount(
        passive_carbon_decomposition_amount: float, passive_carbon_loss_rate=0.55
    ) -> float:
        """
        Calculate passive carbon decomposed into active carbon in the layer (kg/ha).

        Parameters
        ----------
        passive_carbon_decomposition_amount : float
            Passive carbon decomposed into active or passive carbon and CO2 (kg/ha).
        passive_carbon_loss_rate : float
            Fraction of passive carbon lost as CO2 during decomposition (unitless).

        Returns
        -------
        float
            Passive carbon decomposed into active carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.10.

        """
        return passive_carbon_decomposition_amount * (1 - passive_carbon_loss_rate)

    @staticmethod
    def _determine_passive_carbon_co2_lost_amount(
        passive_carbon_decomposition_amount: float, passive_carbon_loss_rate=0.55
    ) -> float:
        """
        Calculate passive carbon lost as CO2 during decomposition in the layer (kg/ha).

        Parameters
        ----------
        passive_carbon_decomposition_amount : float
            Passive carbon decomposed into active or passive carbon and CO2 (kg/ha).
        passive_carbon_loss_rate : float
            Fraction of passive carbon lost as CO2 during decomposition (unitless).

        Returns
        -------
        float
            Passive carbon lost as CO2 during decomposition (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.10.

        """
        return passive_carbon_decomposition_amount * passive_carbon_loss_rate

    @staticmethod
    def _determine_slow_to_active_carbon_amount(
        slow_carbon_decomposition_amount: float,
        slow_carbon_passive_decompose_rate=0.03,
        slow_carbon_loss_rate=0.55,
    ) -> float:
        """
        Calculate slow carbon decomposed into active carbon in the layer (kg/ha).

        Parameters
        ----------
        slow_carbon_decomposition_amount : float
            Slow carbon decomposed into active or passive carbon and CO2 (kg/ha).
        slow_carbon_passive_decompose_rate : float
            Fraction of slow carbon decomposed into passive carbon (unitless).
        slow_carbon_loss_rate : float
            Fraction of slow carbon lost as CO2 during decomposition (unitless).

        Returns
        -------
        float
            Slow carbon decomposed into active carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.9.

        """
        return slow_carbon_decomposition_amount * (1 - slow_carbon_loss_rate - slow_carbon_passive_decompose_rate)

    @staticmethod
    def _determine_slow_carbon_co2_lost_amount(
        slow_carbon_decomposition_amount: float, slow_carbon_loss_rate=0.55
    ) -> float:
        """
        Calculate slow carbon lost as CO2 during decomposition in the layer (kg/ha).

        Parameters
        ----------
        slow_carbon_decomposition_amount : float
            Slow carbon decomposed into active or passive carbon and CO2 (kg/ha).
        slow_carbon_loss_rate : float
            Fraction of slow carbon lost as CO2 during decomposition (unitless).

        Returns
        -------
        float
            Slow carbon lost as CO2 during decomposition (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.9.

        """
        return slow_carbon_decomposition_amount * slow_carbon_loss_rate

    @staticmethod
    def _determine_slow_to_passive_carbon_amount(
        slow_carbon_decomposition_amount: float, slow_carbon_passive_decompose_rate=0.03
    ) -> float:
        """
        Calculate slow carbon decomposed into passive carbon in the layer (kg/ha).

        Parameters
        ----------
        slow_carbon_decomposition_amount : float
            Slow carbon decomposed into active or passive carbon and CO2 (kg/ha).
        slow_carbon_passive_decompose_rate : float
            Fraction of slow carbon decomposed into passive carbon (unitless).

        Returns
        -------
        float
            Slow carbon decomposed into passive carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.9.

        """
        return slow_carbon_decomposition_amount * slow_carbon_passive_decompose_rate

    @staticmethod
    def _determine_active_carbon_to_passive_amount(
        active_carbon_decomposition_amount: float,
    ) -> float:
        """
        Calculate active carbon decomposed into passive carbon in the layer (kg/ha).

        Parameters
        ----------
        active_carbon_decomposition_amount : float
            Active carbon decomposed into slow or passive carbon and CO2 (kg/ha).

        Returns
        -------
        float
            Active carbon decomposed into passive carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.8.

        """
        return active_carbon_decomposition_amount * 0.004

    @staticmethod
    def _determine_active_carbon_to_slow_loss(
        active_carbon_decomposition_amount: float,
        carbon_lost_adjusted_factor: float,
    ) -> float:
        """
        Calculate active carbon lost as CO2 during decomposition into slow carbon in the layer (kg/ha).

        Parameters
        ----------
        active_carbon_decomposition_amount : float
            Active carbon decomposed into slow or passive carbon and CO2 (kg/ha).
        carbon_lost_adjusted_factor : float
            Adjusted factor of CO2 loss from the decomposition of active carbon.

        Returns
        -------
        float
            Active carbon lost as CO2 during decomposition into slow carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.7.

        """
        return active_carbon_decomposition_amount * carbon_lost_adjusted_factor

    @staticmethod
    def _determine_active_carbon_to_slow_amount(
        active_carbon_decomposition_amount: float,
        carbon_lost_adjusted_factor: float,
    ) -> float:
        """
        Calculate active carbon decomposed into slow carbon in the layer (kg/ha).

        Parameters
        ----------
        active_carbon_decomposition_amount : float
            Active carbon decomposed into slow or passive carbon and CO2 (kg/ha).
        carbon_lost_adjusted_factor : float
            Adjusted factor of CO2 loss from the decomposition of active carbon.

        Returns
        -------
        float
            Active carbon decomposed into slow carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.7.

        """
        return active_carbon_decomposition_amount * (1 - carbon_lost_adjusted_factor - 0.004)

    @staticmethod
    def _determine_carbon_lost_adjusted_factor(silt_clay_content: float) -> float:
        """
        Calculate the adjusted factor of CO2 loss from the decomposition of active carbon in the layer.

        Parameters
        ----------
        silt_clay_content : float
            Fraction of silt and clay content in the soil (unitless).

        Returns
        -------
        float
            Adjusted factor of CO2 loss from the decomposition of active carbon.

        References
        ----------
        pseudocode_soil Reference: S.6.C.6.

        """
        return 0.85 - 0.68 * silt_clay_content

    @staticmethod
    def _determine_passive_carbon_decomposition_amount(
        decomposition_moisture_effect: float,
        decomposition_temperature_effect: float,
        passive_carbon_amount: float,
        passive_carbon_decomposition_factor=0.00013,
    ) -> float:
        """
        Calculate passive carbon decomposed into active or passive carbon and CO2 in the layer (kg/ha).

        Parameters
        ----------
        decomposition_moisture_effect : float
            Moisture effect on decomposition factor (unitless) (pseudocode_soil S.6.A.2).
        decomposition_temperature_effect : float
            Temperature effect on decomposition factor (unitless) (pseudocode_soil S.6.A.1).
        passive_carbon_amount : float
            Passive carbon stored in the soil (kg/ha).
        passive_carbon_decomposition_factor : float
            Passive carbon decomposition factor.

        Returns
        -------
        float
            Passive carbon decomposed into active or passive carbon and CO2 (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.5.

        """
        return (
            decomposition_moisture_effect
            * decomposition_temperature_effect
            * passive_carbon_amount
            * passive_carbon_decomposition_factor
        )

    # ---- S.6.C.4
    @staticmethod
    def _determine_slow_carbon_decomposition_amount(
        decomposition_moisture_effect: float,
        decomposition_temperature_effect: float,
        slow_carbon_amount: float,
        slow_carbon_decomposition_factor=0.0038,
    ) -> float:
        """
        Calculate slow carbon decomposed into active or passive carbon and CO2 in the layer (kg/ha).

        Parameters
        ----------
        decomposition_moisture_effect : float
            Moisture effect on decomposition factor (unitless) (pseudocode_soil S.6.A.2).
        decomposition_temperature_effect : float
            Temperature effect on decomposition factor (unitless) (pseudocode_soil S.6.A.1).
        slow_carbon_amount : float
            Slow carbon stored in the soil (kg/ha).
        slow_carbon_decomposition_factor : float
            Slow carbon decomposition factor.

        Returns
        -------
        float
            Slow carbon decomposed into active or passive carbon and CO2 (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.4.

        """
        return (
            decomposition_moisture_effect
            * decomposition_temperature_effect
            * slow_carbon_amount
            * slow_carbon_decomposition_factor
        )

    # ---- S.6.C.3
    @staticmethod
    def _determine_active_carbon_decomposition_amount(
        moisture_effect: float,
        temperature_effect: float,
        active_carbon: float,
        active_carbon_decomposition_rate: float,
    ) -> float:
        """
        Calculate active carbon decomposed into slow or passive carbon and CO2 in the layer (kg/ha).

        Parameters
        ----------
        moisture_effect : float
            Moisture effect on decomposition factor (unitless) (pseudocode_soil S.6.A.2).
        temperature_effect : float
            Temperature effect on decomposition factor (unitless) (pseudocode_soil S.6.A.1).
        active_carbon : float
            Active carbon stored in the soil (kg/ha).
        active_carbon_decomposition_rate : float
            Active carbon decomposition factor (unitless).

        Returns
        -------
        float
            Active carbon decomposed into slow or passive carbon and CO2 (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.3.

        """
        return active_carbon_decomposition_rate * moisture_effect * temperature_effect * active_carbon

    # ---- S.6.C.2
    @staticmethod
    def _determine_active_carbon_decomposition_rate(
        silt_clay_content: float, max_carbon_decomposition_rate: float = 0.14
    ) -> float:
        """
        Calculate the rate at which active carbon is decomposed into slow or passive carbon and CO2 in the layer
        (unitless).

        Parameters
        ----------
        silt_clay_content : float
            Silt and clay content in the soil (%).
        max_carbon_decomposition_rate : float
            Maximum rate of carbon decomposition (unitless).

        Returns
        -------
        float
            Rate at which active carbon is decomposed into slow or passive carbon and CO2 (unitless).

        References
        ----------
        pseudocode_soil Reference: S.6.C.2.

        """
        return max_carbon_decomposition_rate * (1 - 0.75 * silt_clay_content)

    # ----  S.6.C.1
    @staticmethod
    def _determine_plant_metabolic_active_carbon_loss(
        plant_metabolic_active_carbon_usage: float,
        metabolic_active_carbon_loss_rate: float = 0.55,
    ) -> float:
        """
        Calculate plant metabolic carbon being lost as carbon dioxide during decomposition into active carbon in the
        Parameters
        ----------
        plant_metabolic_active_carbon_usage : float
            Plant metabolic carbon decomposed into active carbon (kg/ha).
        metabolic_active_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of metabolic to active carbon.

        Returns
        -------
        float
            Plant metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return plant_metabolic_active_carbon_usage * metabolic_active_carbon_loss_rate

    @staticmethod
    def _determine_plant_metabolic_active_carbon_remaining(
        plant_metabolic_active_carbon_usage: float,
        metabolic_active_carbon_loss_rate: float = 0.55,
    ) -> float:
        """
        Calculate plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss in the
        layer (kg/ha).

        Parameters
        ----------
        plant_metabolic_active_carbon_usage : float
            Plant metabolic carbon decomposed into active carbon (kg/ha).
        metabolic_active_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of metabolic to active carbon.

        Returns
        -------
        float
            Plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return plant_metabolic_active_carbon_usage * (1 - metabolic_active_carbon_loss_rate)

    @staticmethod
    def _determine_plant_structural_active_carbon_loss(
        plant_structural_active_carbon_usage: float,
        structural_active_carbon_loss_rate: float = 0.45,
    ) -> float:
        """
        Calculate plant structural carbon being lost as carbon dioxide during decomposition into active carbon in the
        layer (kg/ha).

        Parameters
        ----------
        plant_structural_active_carbon_usage : float
            Plant structural carbon decomposed into active carbon (kg/ha).
        structural_active_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of structural to active carbon.

        Returns
        -------
        float
            Plant structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return plant_structural_active_carbon_usage * structural_active_carbon_loss_rate

    @staticmethod
    def _determine_plant_structural_active_carbon_remaining(
        plant_structural_active_carbon_usage: float,
        structural_active_carbon_loss_rate: float = 0.45,
    ) -> float:
        """
        Calculate plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss in the
        layer (kg/ha).

        Parameters
        ----------
        plant_structural_active_carbon_usage : float
            Plant metabolic carbon decomposed into active carbon (kg/ha).
        structural_active_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of structural to active carbon.

        Returns
        -------
        float
            Plant metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return plant_structural_active_carbon_usage * (1 - structural_active_carbon_loss_rate)

    @staticmethod
    def _determine_plant_structural_slow_carbon_loss(
        plant_structural_slow_carbon_usage: float,
        structural_slow_carbon_loss_rate: float = 0.3,
    ) -> float:
        """
        Calculate plant structural carbon being lost as carbon dioxide during decomposition into slow carbon in the
        layer (kg/ha).

        Parameters
        ----------
        plant_structural_slow_carbon_usage : float
            Plant structural carbon decomposed into slow carbon (kg/ha).
        structural_slow_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of structural to slow carbon.

        Returns
        -------
        float
            Plant structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return plant_structural_slow_carbon_usage * structural_slow_carbon_loss_rate

    @staticmethod
    def _determine_plant_structural_slow_carbon_remaining(
        plant_structural_slow_carbon_usage: float,
        structural_slow_carbon_loss_rate: float = 0.3,
    ) -> float:
        """
        Calculate plant metabolic carbon decomposed to slow carbon after accounting for carbon dioxide loss in the
        layer (kg/ha).

        Parameters
        ----------
        plant_structural_slow_carbon_usage : float
            Plant metabolic carbon decomposed into slow carbon (kg/ha).
        structural_slow_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of structural to slow carbon.

        Returns
        -------
        float
            Plant metabolic carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return plant_structural_slow_carbon_usage * (1 - structural_slow_carbon_loss_rate)

    @staticmethod
    def _determine_soil_metabolic_active_carbon_loss(
        soil_metabolic_active_carbon_usage: float,
        metabolic_active_carbon_loss_rate: float = 0.55,
    ) -> float:
        """
        Calculate soil metabolic carbon being lost as carbon dioxide during decomposition into active carbon in the
        layer (kg/ha).

        Parameters
        ----------
        soil_metabolic_active_carbon_usage : float
            Soil metabolic carbon decomposed into active carbon (kg/ha).
        metabolic_active_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of metabolic to active carbon.

        Returns
        -------
        float
            Soil metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return soil_metabolic_active_carbon_usage * metabolic_active_carbon_loss_rate

    @staticmethod
    def _determine_soil_metabolic_active_carbon_remaining(
        soil_metabolic_active_carbon_usage: float,
        metabolic_active_carbon_loss_rate: float = 0.55,
    ) -> float:
        """
        Calculate soil metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss in the
        layer (kg/ha).

        Parameters
        ----------
        soil_metabolic_active_carbon_usage : float
            Soil metabolic carbon decomposed into active carbon (kg/ha).
        metabolic_active_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of metabolic to active carbon.

        Returns
        -------
        float
            Soil metabolic carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return soil_metabolic_active_carbon_usage * (1 - metabolic_active_carbon_loss_rate)

    @staticmethod
    def _determine_soil_structural_active_carbon_loss(
        soil_structural_active_carbon_usage: float,
        structural_active_carbon_loss_rate: float = 0.45,
    ) -> float:
        """
        Calculate soil structural carbon being lost as carbon dioxide during decomposition into active carbon in the
        layer (kg/ha).

        Parameters
        ----------
        soil_structural_active_carbon_usage : float
            Soil structural carbon decomposed into active carbon (kg/ha).
        structural_active_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of structural to active carbon.

        Returns
        -------
        float
            Soil structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return soil_structural_active_carbon_usage * structural_active_carbon_loss_rate

    @staticmethod
    def _determine_soil_structural_active_carbon_remaining(
        soil_structural_active_carbon_usage: float,
        structural_active_carbon_loss_rate: float = 0.45,
    ) -> float:
        """
        Calculate soil structural carbon decomposed to active carbon after accounting for carbon dioxide loss in the
        layer (kg/ha).

        Parameters
        ----------
        soil_structural_active_carbon_usage : float
            Soil structural carbon decomposed into active carbon (kg/ha).
        structural_active_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of structural to active carbon.

        Returns
        -------
        float
            Soil structural carbon decomposed to active carbon after accounting for carbon dioxide loss (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return soil_structural_active_carbon_usage * (1 - structural_active_carbon_loss_rate)

    @staticmethod
    def _determine_soil_structural_slow_carbon_loss(
        soil_structural_slow_carbon_usage: float,
        structural_slow_carbon_loss_rate: float = 0.3,
    ) -> float:
        """
        Calculate soil structural carbon being lost as carbon dioxide during decomposition into slow carbon in the
        layer (kg/ha).

        Parameters
        ----------
        soil_structural_slow_carbon_usage : float
            Soil structural carbon decomposed into slow carbon (kg/ha).
        structural_slow_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of structural to slow carbon.

        Returns
        -------
        float
            Soil structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return soil_structural_slow_carbon_usage * structural_slow_carbon_loss_rate

    @staticmethod
    def _determine_soil_structural_slow_carbon_remaining(
        soil_structural_slow_carbon_usage: float,
        structural_slow_carbon_loss_rate: float = 0.3,
    ) -> float:
        """
        Calculate soil structural carbon decomposed to slow carbon after accounting for carbon dioxide loss in the
        layer (kg/ha).

        Parameters
        ----------
        soil_structural_slow_carbon_usage : float
            Soil structural carbon decomposed into slow carbon (kg/ha).
        structural_slow_carbon_loss_rate : float
            Rate of carbon dioxide loss during transformation of structural to slow carbon (unitless).

        Returns
        -------
        float
            Soil structural carbon decomposed to slow carbon after accounting for carbon dioxide loss (kg/ha).

        References
        ----------
        pseudocode_soil Reference: S.6.C.1.

        """
        return soil_structural_slow_carbon_usage * (1 - structural_slow_carbon_loss_rate)
