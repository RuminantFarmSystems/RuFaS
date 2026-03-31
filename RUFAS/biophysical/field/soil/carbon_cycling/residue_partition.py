import math
from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class ResiduePartition:
    """
    Manages the partitioning of plant residues within the soil, affecting both plant-available nutrients and soil carbon
    storage.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track residue in the soil profile, creates new one if one is not
        provided.
    field_size : float, optional
        Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
        not provided (ha)

    Attributes
    ----------
    data : SoilData
        The SoilData object used by this module to track residue in the soil profile.

    References
    -------
    pseudocode_soil S.6.B

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def add_residue_to_pools(self, rainfall: float) -> None:
        """
        Adds residue to pools.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm).

        """
        self.data.plant_residue_lignin_composition = self._determine_plant_residue_lignin_composition(
            self.data.plant_residue_lignin_composition, rainfall
        )
        self.data.plant_lignin_nitrogen_ratio = self._determine_plant_lignin_nitrogen_fraction(
            self.data.plant_residue_lignin_composition,
            self.data.total_residue,
            self.data.crop_yield_nitrogen,
        )
        self.data.plant_residue_metabolic_fraction = self._determine_plant_residue_metabolic_fraction(
            self.data.plant_lignin_nitrogen_ratio
        )

        self._add_litter_to_pools()

    def partition_residue(self, rainfall: float) -> None:
        """Main routine to updates attributes by using static methods, this method should only be called (by the field/
        field manager) on the day that a cut, harvest, or kill operation occurs and should be called after that
        operation.

        Parameters
        ----------
        rainfall: float
            Amount of rain (mm).

        """
        layer = self.data.soil_layers[0]
        layer.plant_metabolic_active_carbon_usage = self._determine_plant_metabolic_active_carbon_usage(
            layer.decomposition_moisture_effect,
            layer.decomposition_temperature_effect,
            layer.metabolic_litter_amount,
        )

        layer.metabolic_litter_amount = self._determine_plant_metabolic_carbon_amount(
            layer.metabolic_litter_amount,
            layer.plant_residue_metabolic_fraction,
            layer.plant_dry_matter_residue_amount,
            layer.plant_metabolic_active_carbon_usage,
            layer.plant_metabolic_to_soil_carbon_amount,
        )

        layer.plant_structural_to_slow_or_active_rate = self._determine_plant_structural_to_slow_or_active_rate(
            self.data.plant_residue_metabolic_fraction
        )

        layer.plant_structural_active_carbon_usage = self._determine_plant_structural_to_slow_active_carbon_amount(
            layer.plant_structural_to_slow_or_active_rate,
            layer.decomposition_moisture_effect,
            layer.decomposition_temperature_effect,
            layer.structural_litter_amount,
        )

        layer.plant_structural_slow_carbon_usage = self._determine_plant_structural_to_slow_active_carbon_amount(
            layer.plant_structural_to_slow_or_active_rate,
            layer.decomposition_moisture_effect,
            layer.decomposition_temperature_effect,
            layer.structural_litter_amount,
        )

        layer.structural_litter_amount = self._determine_plant_structural_carbon_amount(
            layer.plant_dry_matter_residue_amount,
            layer.plant_residue_metabolic_fraction,
            layer.structural_carbon_transfer_amount,
            layer.plant_structural_active_carbon_usage,
            layer.plant_structural_slow_carbon_usage,
            layer.structural_litter_amount,
        )

        layer.plant_dry_matter_residue_amount = 0

        layer.weighted_residue_dry_matter_lignin_fraction = self._determine_weighted_residue_dry_matter_lignin_fraction(
            layer.soil_dry_matter_residue_amount, 0.0
        )

        for layer in self.data.soil_layers[1:]:
            layer.soil_dry_matter_residue_amount = 0

            layer.weighted_residue_dry_matter_lignin_fraction = (
                self._determine_weighted_residue_dry_matter_lignin_fraction(layer.soil_dry_matter_residue_amount, 0.0)
            )

            layer.soil_residue_lignin_fraction = self._determine_soil_residue_lignin_fraction(
                layer.weighted_residue_dry_matter_lignin_fraction, rainfall
            )

            layer.soil_lignin_to_nitrogen_fraction = self._determine_soil_lignin_to_nitrogen_fraction(
                self.data.plant_residue_metabolic_fraction,
                layer.weighted_residue_dry_matter_lignin_fraction,
                layer.soil_residue_lignin_fraction,
            )

            layer.soil_residue_metabolic_fraction = self._determine_soil_residue_metabolic_fraction(
                layer.soil_lignin_to_nitrogen_fraction
            )

            layer.soil_metabolic_active_carbon_usage = self._determine_soil_metabolic_to_active_carbon_amount(
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.metabolic_litter_amount,
            )

            layer.metabolic_litter_amount = self._determine_soil_metabolic_carbon_amount(
                layer.metabolic_litter_amount,
                layer.plant_metabolic_to_soil_carbon_amount,
                0.0,
                layer.soil_residue_metabolic_fraction,
                layer.soil_metabolic_active_carbon_usage,
            )

            layer.soil_structural_active_carbon_usage = self._determine_soil_structural_to_slow_active_carbon_amount(
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.structural_litter_amount,
                layer.soil_structural_to_slow_or_active_rate,
            )

            layer.soil_structural_slow_carbon_usage = self._determine_soil_structural_to_slow_active_carbon_amount(
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.structural_litter_amount,
                layer.soil_structural_to_slow_or_active_rate,
            )

            layer.structural_litter_amount = self._determine_soil_structural_carbon_amount(
                layer.soil_residue_metabolic_fraction,
                layer.structural_carbon_transfer_amount,
                layer.soil_structural_active_carbon_usage,
                layer.soil_structural_slow_carbon_usage,
                0.0,
                layer.structural_litter_amount,
            )

    def _add_litter_to_pools(self) -> None:
        """
        Partitions residue between metabolic and structural pools in all layers of the soil profile.

        """
        subsurface_plant_residue = self.data.get_vectorized_layer_attribute("plant_residue")
        if any(subsurface_plant_residue):
            for layer in self.data.soil_layers:
                layer.metabolic_litter_amount += self.data.plant_residue_metabolic_fraction * layer.plant_residue
                layer.structural_litter_amount += (1 - self.data.plant_residue_metabolic_fraction) * layer.plant_residue
                layer.plant_residue = 0.0
            self._set_soil_structural_litter_decomposition_rate()

    def _set_soil_structural_litter_decomposition_rate(self) -> None:
        """
        Sets the soil structural litter decomposition rate using the same methodology as the
        `_determine_plant_structural_to_slow_or_active_rate`.

        """
        structural_litter_decomposition_rate = 0.094 * math.exp(-3) * (1 - self.data.plant_residue_metabolic_fraction)
        rates = [structural_litter_decomposition_rate] * len(self.data.soil_layers)
        self.data.set_vectorized_layer_attribute("soil_structural_to_slow_or_active_rate", rates)

    @staticmethod
    def _determine_plant_residue_lignin_composition(plant_residue_lignin_composition: float, rainfall: float) -> float:
        """
        This method calculates and updates the plant_residue_lignin_composition based on the amount of rainfall.

        Parameters
        ----------
        plant_residue_lignin_composition : float
            Lignin fraction of plant residue (unitless).
        rainfall : float
            Amount of rain (mm H2O).

        Returns
        -------
        float
            The updated plant_residue_lignin_composition.

        References
        ----------
        pseudocode_soil S.6.B.I.1

        """
        plant_residue_lignin_composition += 0.12 * rainfall * 0.1
        return plant_residue_lignin_composition

    @staticmethod
    def _determine_plant_lignin_nitrogen_fraction(
        plant_residue_lignin_composition: float,
        total_residue: float,
        crop_yield_nitrogen: float,
    ) -> float:
        """
        This method calculates the plant lignin to nitrogen ratio when nitrogen in plant residue at harvest
        is greater than zero.

        Parameters
        ----------
        plant_residue_lignin_composition : float
            Lignin fraction of plant residue (unitless).
        total_residue : float
            Total amount of soil residue ever added to the field (kg/ha).
        crop_yield_nitrogen : float
            Nitrogen contained in the harvested yield (kg/ha).

        Returns
        -------
        float
            Plant lignin to nitrogen ratio (unitless).

        References
        ----------
        pseudocode_soil S.6.B.I.2

        """
        if total_residue == 0.0:
            return 0.0
        nitrogen_fraction_plant_residue = crop_yield_nitrogen / total_residue
        if 0 < nitrogen_fraction_plant_residue <= 1.0:
            return (plant_residue_lignin_composition / 100) / nitrogen_fraction_plant_residue
        elif nitrogen_fraction_plant_residue == 0:
            return 0
        else:
            raise ValueError(
                "Expected nitrogen_fraction_plant_residue be between 0.0-1.0, received "
                + str(nitrogen_fraction_plant_residue)
            )

    @staticmethod
    def _determine_plant_residue_metabolic_fraction(
        plant_lignin_nitrogen_ratio: float,
    ) -> float:
        """
        This method calculates the fraction of plant residue that is metabolic.

        Parameters
        ----------
        plant_lignin_nitrogen_ratio : float
            Plant lignin to nitrogen ratio (unitless).

        Returns
        -------
        float
            Plant residue fraction that is metabolic (unitless).


        References
        ----------
        pseudocode_soil S.6.B.I.3

        """
        return 0.85 - 0.18 * plant_lignin_nitrogen_ratio

    @staticmethod
    def _determine_plant_metabolic_carbon_amount(
        plant_metabolic_carbon_amount: float,
        plant_residue_metabolic_fraction: float,
        plant_dry_matter_residue_amount: float,
        plant_metabolic_active_carbon_usage: float,
        plant_metabolic_to_soil_carbon_amount: float,
    ) -> float:
        """
        This method calculates the updated plant metabolic carbon amount after adding the metabolic carbon
        in dry matter at harvest and reduced by the amount that's decomposed and incorporated.

        Parameters
        ----------
        plant_metabolic_carbon_amount: float
            Plant metabolic carbon amount (kg/ha).
        plant_residue_metabolic_fraction: float
            Fraction of plant residue that is metabolic (unitless).
        plant_dry_matter_residue_amount: float
            Amount of dry matter residue at harvest (kg/ha).
        plant_metabolic_active_carbon_usage: float
            Plant metabolic carbon decomposed into active carbon (kg/ha).
        plant_metabolic_to_soil_carbon_amount: float
            Metabolic carbon incorporated into soil during tillage (kg/ha).

        Returns
        -------
        float
            Updated plant metabolic carbon amount (hg/ha).

        References
        ----------
        pseudocode_soil S.6.B.I.4, S.6.B.I.7

        """
        plant_metabolic_carbon_amount += plant_dry_matter_residue_amount * plant_residue_metabolic_fraction - (
            plant_metabolic_active_carbon_usage + plant_metabolic_to_soil_carbon_amount
        )
        return plant_metabolic_carbon_amount

    @staticmethod
    def _determine_plant_metabolic_active_carbon_usage(
        decomposition_moisture_effect: float,
        decomposition_temperature_effect: float,
        plant_metabolic_carbon_amount: float,
        plant_metabolic_active_carbon_rate=0.28,
    ) -> float:
        """
        Calculates the amount of plant metabolic carbon decomposed to active carbon (kg/ha).

        Parameters
        ----------
        decomposition_moisture_effect: float
            Moisture effect on decomposition factor (unitless).
        decomposition_temperature_effect: float
            Temperature effect on decomposition factor (unitless).
        plant_metabolic_carbon_amount: float
            Plant metabolic carbon amount (kg/ha).
        plant_metabolic_active_carbon_rate: float default = 0.28 (Parton et al. 1987)
            Rate of decomposition from metabolic to active carbon (unitless).

        Returns
        -------
        float
            Above ground metabolic carbon decomposed to active carbon (kg/ha).

        References
        ----------
        pseudocode_soil S.6.B.I.5

        """
        return (
            decomposition_moisture_effect
            * decomposition_temperature_effect
            * plant_metabolic_carbon_amount
            * plant_metabolic_active_carbon_rate
        )

    @staticmethod
    def _determine_plant_structural_to_slow_or_active_rate(
        plant_residue_metabolic_fraction: float, structural_decomposition_factor=0.076
    ) -> float:
        """
        This method calculates the rate at which above ground structural carbon decomposes into slow or active carbon.

        Parameters
        ----------
        structural_decomposition_factor: float, default = 0.076 (Parton et al. 1987)
            Structural decomposition factor (unitless).
        plant_residue_metabolic_fraction: float
            Fraction of plant residue that is metabolic (unitless).

        Returns
        -------
        float
            The rate at which above ground structural carbon decomposes into slow or active carbon (unitless).

        References
        ----------
        pseudocode_soil S.6.B.I.9

        Notes
        -----
        the equation used here currently follows the old code to make mathematical sense.

        """
        return structural_decomposition_factor * math.exp(-3) * (1 - plant_residue_metabolic_fraction)

    @staticmethod
    def _determine_plant_structural_to_slow_active_carbon_amount(
        plant_structural_to_slow_or_active_rate: float,
        decomposition_moisture_effect: float,
        decomposition_temperature_effect: float,
        plant_structural_carbon_amount: float,
    ) -> float:
        """
        This method determines the amount of plant structural carbon decomposed into slow or active carbon.

        Parameters
        ----------
        plant_structural_to_slow_or_active_rate: float
            Rate at which above ground structural carbon decomposes into slow or active carbon (unitless).
        decomposition_moisture_effect: float
            Moisture effect on decomposition factor (unitless).
        decomposition_temperature_effect: float
            Temperature effect on decomposition factor (unitless).
        plant_structural_carbon_amount: float
            Plant structural carbon amount (kg/ha).

        Returns
        -------
        float
            Amount of plant structural carbon decomposed into slow or active carbon (kg/ha).

        References
        ----------
        pseudocode_soil S.6.B.I.10

        """
        return (
            plant_structural_to_slow_or_active_rate
            * decomposition_moisture_effect
            * decomposition_temperature_effect
            * plant_structural_carbon_amount
        )

    @staticmethod
    def _determine_structural_carbon_transfer_amount(
        plant_structural_carbon_amount: float, tillage_fraction: float
    ) -> float:
        """
        Determines the amount of transfer of plant structural to soil structural carbon during tillage.

        Parameters
        ----------
        plant_structural_carbon_amount: float
            Amount of plant structural carbon (kg/ha).
        tillage_fraction: float
            Fraction of metabolic carbon incorporated into soil during tillage (unitless).

        Returns
        -------
        float
            The amount of transfer of structural carbon during tillage (kg/ha).

        References
        ----------
        pseudocode_soil S.6.B.I.11

        """
        return plant_structural_carbon_amount * tillage_fraction

    @staticmethod
    def _determine_plant_structural_carbon_amount(
        plant_dry_matter_residue_amount: float,
        plant_residue_metabolic_fraction: float,
        structural_carbon_transfer_amount: float,
        plant_structural_to_active_carbon_amount: float,
        plant_structural_to_slow_carbon_amount: float,
        plant_structural_carbon_amount: float,
    ) -> float:
        """
        Calculates the updated plant structural carbon amount.

        Parameters
        ----------
        plant_dry_matter_residue_amount: float
            Amount of dry matter residue at harvest (kg/ha).
        plant_residue_metabolic_fraction: float
            Fraction of plant residue that is metabolic (unitless).
        structural_carbon_transfer_amount: float
            The amount of transfer of structural carbon during tillage (kg/ha).
        plant_structural_to_active_carbon_amount: float
            Amount of plant structural carbon decomposed into slow carbon (kg/ha).
        plant_structural_to_slow_carbon_amount: float
            Amount of plant structural carbon decomposed into active carbon (kg/ha).
        plant_structural_carbon_amount: float
            Plant structural carbon amount (kg/ha).

        Returns
        -------
        float
            Updated plant structural carbon amount (kg/ha).

        References
        ----------
        pseudocode_soil S.6.B.I.8, S.6.B.I.12

        """
        updated_amount = (
            plant_structural_carbon_amount
            + plant_dry_matter_residue_amount * (1 - plant_residue_metabolic_fraction)
            - structural_carbon_transfer_amount
            - plant_structural_to_active_carbon_amount
            - plant_structural_to_slow_carbon_amount
        )

        return updated_amount

    @staticmethod
    def _determine_weighted_residue_dry_matter_lignin_fraction(
        soil_dry_matter_residue_amount: float, root_biomass: float
    ) -> float:
        """
        Calculates the weighted fractional of lignin amount in residue dry matter.

        Parameters
        ----------
        soil_dry_matter_residue_amount: float
            The amount of soil dry matter residue at harvest (kg/ha).
        root_biomass: float
            Root biomass (kg/ha).

        Returns
        -------
        float
            The weighted fractional of lignin amount in residue dry matter (unitless).

        References
        ----------
        pseudocode_soil S.6.B.II.2

        Notes
        -----
        The referenced soil(below ground) biomass calculation was not found in the pseudocode_crop, neither is any
        mention of biomass unit.

        """
        if soil_dry_matter_residue_amount + root_biomass != 0:
            return soil_dry_matter_residue_amount / (soil_dry_matter_residue_amount + root_biomass)
        else:
            return 0

    @staticmethod
    def _determine_soil_residue_lignin_fraction(
        weighted_residue_dry_matter_lignin_fraction: float, rainfall: float
    ) -> float:
        """
        Calculates the fraction of soil residue that's comprised of lignin.

        Parameters
        ----------
        weighted_residue_dry_matter_lignin_fraction: float
            The weighted fractional of lignin amount in residue dry matter (unitless).
        rainfall: float
            Amount of rain (mm H2O).

        Returns
        -------
        float
            The fraction of soil residue that's comprised of lignin (unitless).

        References
        ----------
        pseudocode_soil S.6.B.II.3

        """
        return max(0.0, weighted_residue_dry_matter_lignin_fraction - 0.15 * rainfall * 0.01)

    @staticmethod
    def _determine_soil_lignin_to_nitrogen_fraction(
        plant_lignin_nitrogen_ratio: float,
        weighted_residue_dry_matter_lignin_fraction: float,
        soil_residue_lignin_fraction: float,
        nitrogen_fraction_plant_residue=0.4,
    ) -> float:
        """
        This method calculates the soil lignin to nitrogen fraction.

        Parameters
        ----------
        plant_lignin_nitrogen_ratio: float
            Plant lignin to nitrogen ratio (unitless).
        weighted_residue_dry_matter_lignin_fraction: float
            Weighted fraction of lignin in residue dry matter (unitless).
        soil_residue_lignin_fraction: float
            Soil residue fraction that is composed of lignin (unitless).
        nitrogen_fraction_plant_residue: float default = 0.4
            Nitrogen fraction in plant residue at harvest (unitless).

        Returns
        -------
        float
            Soil lignin to nitrogen fraction(unitless).

        References
        ----------
        pseudocode_soil S.6.B.II.4

        """
        if 0 < nitrogen_fraction_plant_residue <= 1:
            return plant_lignin_nitrogen_ratio * weighted_residue_dry_matter_lignin_fraction + (
                ((soil_residue_lignin_fraction / 100) / nitrogen_fraction_plant_residue) / 100
            ) * (1 - weighted_residue_dry_matter_lignin_fraction)
        elif nitrogen_fraction_plant_residue == 0:
            return 0
        else:
            raise ValueError(
                "Expected nitrogen_fraction_plant_residue to be between 0.0-1.0, received "
                + str(nitrogen_fraction_plant_residue)
            )

    @staticmethod
    def _determine_soil_residue_metabolic_fraction(
        soil_lignin_to_nitrogen_fraction: float,
    ) -> float:
        """
        This method calculates the fraction of soil residue that is metabolic.

        Parameters
        ----------
        soil_lignin_to_nitrogen_fraction: float
            Soil lignin to nitrogen fraction(unitless).

        Returns
        -------
        float
            The fraction of soil residue that is metabolic(unitless).

        References
        ----------
        pseudocode_soil S.6.B.II.5

        """
        return max(0.0, 0.85 - 0.18 * soil_lignin_to_nitrogen_fraction)

    @staticmethod
    def _determine_soil_metabolic_carbon_amount(
        soil_metabolic_carbon_amount: float,
        plant_metabolic_to_soil_carbon_amount: float,
        root_biomass: float,
        soil_residue_metabolic_fraction: float,
        soil_metabolic_active_carbon_usage: float,
    ) -> float:
        """
        This method updates the amount of soil metabolic carbon.

        Parameters
        ----------
        soil_metabolic_carbon_amount: float
            The amount of soil metabolic carbon (kg/ha).
        plant_metabolic_to_soil_carbon_amount: float
            The amount of metabolic carbon incorporated into soil during tillage (kg/ha).
        root_biomass: float
            Root biomass (kg/ha).
        soil_residue_metabolic_fraction: float
            The fraction of soil residue that is metabolic (unitless).
        soil_metabolic_active_carbon_usage: float
            The amount of soil metabolic carbon decomposed into active carbon (kg/ha).

        Returns
        -------
        float
            The updated amount of soil metabolic carbon (kg/ha).

        References
        ----------
        pseudocode_soil S.6.B.II.6, S.6.B.II.8

        """
        result = (
            soil_metabolic_carbon_amount
            + plant_metabolic_to_soil_carbon_amount
            + (root_biomass * soil_residue_metabolic_fraction)
            - soil_metabolic_active_carbon_usage
        )
        return result

    @staticmethod
    def _determine_soil_metabolic_to_active_carbon_amount(
        decomposition_moisture_effect: float,
        decomposition_temperature_effect: float,
        soil_metabolic_carbon_amount: float,
        soil_metabolic_active_carbon_rate=0.35,
    ) -> float:
        """
        This method calculates the amount of soil metabolic carbon decomposed into active carbon.

        Parameters
        ----------
        decomposition_moisture_effect: float
            Moisture effect on decomposition factor (unitless).
        decomposition_temperature_effect: float
            Temperature effect on decomposition factor (unitless).
        soil_metabolic_carbon_amount: float
            Soil metabolic carbon amount (kg/ha).
        soil_metabolic_active_carbon_rate: float default = 0.35
            Rate of decomposition from soil metabolic to active carbon (unitless).

        Returns
        -------
        float
            Amount of soil metabolic carbon decomposed into active carbon(kg/ha).

        References
        ----------
        pseudocode_soil S.6.B.II.7

        """
        return (
            decomposition_temperature_effect
            * decomposition_moisture_effect
            * soil_metabolic_carbon_amount
            * soil_metabolic_active_carbon_rate
        )

    @staticmethod
    def _determine_soil_structural_to_slow_active_carbon_amount(
        decomposition_moisture_effect: float,
        decomposition_temperature_effect: float,
        soil_structural_carbon_amount: float,
        soil_structural_to_slow_or_active_rate=0.094,
    ) -> float:
        """
        This method determines the amount of soil structural carbon decomposed into slow or active carbon.

        Parameters
        ----------
        soil_structural_to_slow_or_active_rate: float default = 0.094 (Parton et al. 1987)
            Rate at which soil structural carbon decomposes into slow or active carbon (unitless).
        decomposition_moisture_effect: float
            Moisture effect on decomposition factor (unitless).
        decomposition_temperature_effect: float
            Temperature effect on decomposition factor (unitless).
        soil_structural_carbon_amount: float
            Soil structural carbon amount(kg/ha).

        Returns
        -------
        float
            Amount of soil structural carbon decomposed into slow or active carbon (kg/ha).

        References
        ----------
        pseudocode_soil S.6.B.II.10

        Notes
        -----
        This method can be used for both calculating amount of soil structural carbon decomposed into slow carbon and
        amount of soil structural carbon decomposed into active carbon.

        """
        return (
            decomposition_moisture_effect
            * decomposition_temperature_effect
            * soil_structural_carbon_amount
            * soil_structural_to_slow_or_active_rate
        )

    @staticmethod
    def _determine_soil_structural_carbon_amount(
        soil_residue_metabolic_fraction: float,
        structural_carbon_transfer_amount: float,
        soil_structural_to_active_carbon_amount: float,
        soil_structural_to_slow_carbon_amount: float,
        root_biomass: float,
        soil_structural_carbon_amount: float,
    ) -> float:
        """
        Calculates the updated soil structural carbon amount.

        Parameters
        ----------
        soil_residue_metabolic_fraction: float
            Fraction of soil residue that is metabolic (unitless).
        structural_carbon_transfer_amount: float
            The amount of transfer of structural carbon during tillage (kg/ha).
        soil_structural_to_active_carbon_amount: float
            Amount of soil structural carbon decomposed into slow carbon (kg/ha).
        soil_structural_to_slow_carbon_amount: float
            Amount of soil structural carbon decomposed into active carbon (kg/ha).
        root_biomass: float
            Root biomass (kg/ha).
        soil_structural_carbon_amount: float
            Soil structural carbon amount (kg/ha).
        Returns
        -------
        float
            Updated soil structural carbon amount (kg/ha).

        References
        ----------
        pseudocode_soil S.6.B.II.9, S.6.B.II.11

        """
        updated_amount = (
            soil_structural_carbon_amount
            + structural_carbon_transfer_amount
            + root_biomass * (1 - soil_residue_metabolic_fraction)
            - soil_structural_to_active_carbon_amount
            - soil_structural_to_slow_carbon_amount
        )

        return updated_amount
