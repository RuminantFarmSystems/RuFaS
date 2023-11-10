from typing import Optional
from RUFAS.routines.field.soil.soil_data import SoilData
import math

"""
This class contains all necessary methods that involve residue partition, including both plant and soil and also
considers the case of tillage for plants

References
-------
pseudocode_soil S.6.B
"""


class ResiduePartition:

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track residue in the soil profile, creates new one if one is not
            provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def add_residue_to_pools(self, rainfall: float) -> None:
        """
        Adds residue to pools.
        """
        self.data.plant_residue_lignin_composition = self._determine_plant_residue_lignin_composition(
            self.data.plant_residue_lignin_composition, rainfall)
        self.data.plant_lignin_nitrogen_ratio = self._determine_plant_lignin_nitrogen_fraction(
            self.data.plant_residue_lignin_composition, self.data.all_residue, self.data.crop_yield_nitrogen)
        self.data.plant_residue_metabolic_fraction = self._determine_plant_residue_metabolic_fraction(
            self.data.plant_lignin_nitrogen_ratio)

        self._add_litter_to_pools()

    def partition_residue(self, rainfall: float) -> None:
        """Main routine to updates attributes by using static methods, this method should only be called (by the field/
        field manager) on the day that a cut, harvest, or kill operation occurs and should be called after that
        operation.

        Parameters
        ----------
        rainfall: float
            amount of rain (mm)
        """
        layer = self.data.soil_layers[0]
        layer.plant_metabolic_active_carbon_usage = self._determine_plant_metabolic_active_carbon_usage(
            layer.decomposition_moisture_effect,
            self.data.decomposition_temperature_effect,
            layer.metabolic_litter_amount)

        layer.soil_dry_matter_residue_amount = self._determine_soil_dry_matter_residue_amount(
            self.data.crop_root_depth,
            self.data.plant_root_residue,
            layer.bottom_depth,
            layer.top_depth,
            layer.layer_thickness
        )

        layer.metabolic_litter_amount = self._determine_plant_metabolic_carbon_amount(
            layer.metabolic_litter_amount,
            layer.plant_residue_metabolic_fraction,
            layer.plant_dry_matter_residue_amount,
            layer.plant_metabolic_active_carbon_usage,
            layer.plant_metabolic_to_soil_carbon_amount)

        layer.plant_structural_to_slow_or_active_rate = self._determine_plant_structural_to_slow_or_active_rate(
            self.data.plant_residue_metabolic_fraction)

        layer.structural_litter_amount = self._determine_plant_structural_carbon_amount(
            layer.plant_dry_matter_residue_amount,
            layer.plant_residue_metabolic_fraction,
            layer.structural_carbon_transfer_amount,
            layer.plant_structural_active_carbon_usage,
            layer.plant_structural_slow_carbon_usage,
            layer.structural_litter_amount)

        layer.plant_dry_matter_residue_amount = 0

        layer.plant_structural_active_carbon_usage = \
            self._determine_plant_structural_to_slow_active_carbon_amount(
                layer.plant_structural_to_slow_or_active_rate,
                layer.decomposition_moisture_effect,
                self.data.decomposition_temperature_effect,
                layer.structural_litter_amount)

        layer.plant_structural_slow_carbon_usage = \
            self._determine_plant_structural_to_slow_active_carbon_amount(
                layer.plant_structural_to_slow_or_active_rate,
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.structural_litter_amount)

        layer.weighted_residue_dry_matter_lignin_fraction = \
            self._determine_weighted_residue_dry_matter_lignin_fraction(layer.soil_dry_matter_residue_amount,
                                                                        self.data.plant_root_residue)

        for layer in self.data.soil_layers[1:]:
            layer.soil_dry_matter_residue_amount = 0

            layer.soil_residue_lignin_fraction = self._determine_soil_residue_lignin_fraction(
                layer.weighted_residue_dry_matter_lignin_fraction,
                rainfall
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
                self.data.plant_root_residue,
                layer.soil_residue_metabolic_fraction,
                layer.soil_metabolic_active_carbon_usage
            )

            layer.soil_structural_active_carbon_usage = self._determine_soil_structural_to_slow_active_carbon_amount(
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.structural_litter_amount
            )

            layer.soil_structural_slow_carbon_usage = self._determine_soil_structural_to_slow_active_carbon_amount(
                layer.decomposition_moisture_effect,
                layer.decomposition_temperature_effect,
                layer.structural_litter_amount
            )

            layer.structural_litter_amount = self._determine_soil_structural_carbon_amount(
                layer.soil_residue_metabolic_fraction,
                layer.structural_carbon_transfer_amount,
                layer.soil_structural_active_carbon_usage,
                layer.soil_structural_slow_carbon_usage,
                self.data.plant_root_residue,
                layer.structural_litter_amount
            )

    def _add_litter_to_pools(self) -> None:
        """
        Partitions residue between metabolic and structural pools in all layers of the soil profile.
        """
        if self.data.plant_surface_residue > 0.0:
            self.data.soil_layers[0].metabolic_litter_amount += \
                self.data.plant_surface_residue * self.data.plant_residue_metabolic_fraction
            self.data.soil_layers[0].structural_litter_amount += \
                self.data.plant_surface_residue * (1 - self.data.plant_residue_metabolic_fraction)
            self.data.plant_surface_residue = 0.0

        if self.data.plant_root_residue != 0.0 and self.data.crop_root_depth != 0.0:
            self._add_subsurface_residue(self.data.plant_root_residue, self.data.crop_root_depth)
            self.data.plant_root_residue = 0.0
            self.data.crop_root_depth = 0.0

    def _add_subsurface_residue(self, root_residue: float, root_depth: float) -> None:
        """
        Add residue from roots into structural and metabolic pools of subsurface soil layers.

        Parameters
        ----------
        root_residue : float
            Amount of residue from root biomass (kg / ha).
        root_depth : float
            Depth of root growth (mm).

        Notes
        -----
        This method divides residue between subsurface layers proportionally based on how much of the root depth was
        contained in the soil layer.

        """
        for layer in self.data.soil_layers:
            litter_amount = self._determine_soil_dry_matter_residue_amount(root_depth, root_residue,
                                                                           layer.bottom_depth, layer.top_depth,
                                                                           layer.layer_thickness)
            layer.metabolic_litter_amount += self.data.plant_residue_metabolic_fraction * litter_amount
            layer.structural_litter_amount += (1 - self.data.plant_residue_metabolic_fraction) * litter_amount

    @staticmethod
    def _determine_soil_dry_matter_residue_amount(root_depth: float, plant_root_residue: float, layer_bottom: float,
                                                  layer_top: float, layer_thickness: float) -> float:
        """Determine the amount of dry matter residue in each layer according to the portion of root in such layer

        Parameters
        ----------
        root_depth : float
            Root depth of the crop harvested (mm)
        plant_root_residue : float
            plant residue below the surface of the soil (kg/ha)
        layer_bottom : float
            bottom depth of the layer (mm)
        layer_top : float
            top depth of the layer (mm)
        layer_thickness : float
            Thickness of the soil layer (mm)

        Returns
        -------
        float
            the amount of dry matter residue in the layer
        """
        if layer_top >= root_depth:
            return 0
        elif layer_bottom <= root_depth:
            return plant_root_residue * layer_thickness / root_depth
        else:
            return plant_root_residue * (root_depth - layer_top) / root_depth

    @staticmethod
    def _determine_plant_residue_lignin_composition(plant_residue_lignin_composition: float,
                                                    rainfall: float) -> float:
        """This method calculates and updates the plant_residue_lignin_composition based on the amount of rainfall

        Parameters
        ----------
        plant_residue_lignin_composition : float
            lignin fraction of plant residue (unitless)
        rainfall : float
            amount of rain (mm H2O)

        Returns
        -------
        float
            The updated plant_residue_lignin_composition

        References
        -------
        pseudocode_soil S.6.B.I.1
        """
        plant_residue_lignin_composition += 0.12 * rainfall * 0.1
        return plant_residue_lignin_composition
        # TODO: check source, 0.1 or 0.01, ask Hector about the value

    @staticmethod
    def _determine_plant_lignin_nitrogen_fraction(plant_residue_lignin_composition: float,
                                                  total_residue: float,
                                                  crop_yield_nitrogen: float) -> float:
        # TODO nitrogen_fraction_plant_residue calculate in RuFaS [C.5.B.1] but not "accurate" for carbon use -
        #  GitHub Issue #163
        """This method calculates the plant lignin to nitrogen ratio when nitrogen in plant residue at harvest
        is greater than zero

        Parameters
        ----------
        plant_residue_lignin_composition : float
            lignin fraction of plant residue (unitless)
        total_residue : float
            total amount of soil residue ever added to the field (kg/ha)
        crop_yield_nitrogen : float
            nitrogen contained in the harvested yield (kg/ha)

        Returns
        -------
        float
            plant lignin to nitrogen ratio (unitless)

        References
        -------
        pseudocode_soil S.6.B.I.2
        """
        nitrogen_fraction_plant_residue = crop_yield_nitrogen / total_residue
        if 0 < nitrogen_fraction_plant_residue <= 1.0:
            return (plant_residue_lignin_composition / 100) / nitrogen_fraction_plant_residue
        elif nitrogen_fraction_plant_residue == 0:
            return 0
        else:
            raise ValueError("Expected nitrogen_fraction_plant_residue be between 0.0-1.0, received "
                             + str(nitrogen_fraction_plant_residue))

    @staticmethod
    def _determine_plant_residue_metabolic_fraction(plant_lignin_nitrogen_ratio: float) -> float:
        """This method calculates the fraction of plant residue that is metabolic

        Parameters
        ----------
        plant_lignin_nitrogen_ratio : float
            plant lignin to nitrogen ratio (unitless)

        Returns
        -------
        float
            plant residue fraction that is metabolic (unitless)


        References
        -------
        pseudocode_soil S.6.B.I.3
        """
        return 0.85 - 0.18 * plant_lignin_nitrogen_ratio

    @staticmethod
    def _determine_plant_metabolic_carbon_amount(plant_metabolic_carbon_amount: float,
                                                 plant_residue_metabolic_fraction: float,
                                                 plant_dry_matter_residue_amount: float,
                                                 plant_metabolic_active_carbon_usage: float,
                                                 plant_metabolic_to_soil_carbon_amount: float) -> float:
        """This method calculates the updated plant metabolic carbon amount after adding the metabolic carbon
        in dry matter at harvest and reduced by the amount that's decomposed and incorporated

        Parameters
        ----------
        plant_metabolic_carbon_amount: float
            plant metabolic carbon amount (kg/ha)
        plant_residue_metabolic_fraction: float
            fraction of plant residue that is metabolic (unitless)
        plant_dry_matter_residue_amount: float
            amount of dry matter residue at harvest (kg/ha)
        plant_metabolic_active_carbon_usage: float
            plant metabolic carbon decomposed into active carbon (kg/ha)
        plant_metabolic_to_soil_carbon_amount: float
            metabolic carbon incorporated into soil during tillage (kg/ha)

        Returns
        -------
        float
            updated plant metabolic carbon amount (hg/ha)

        References
        -------
        pseudocode_soil S.6.B.I.4, S.6.B.I.7

        """
        plant_metabolic_carbon_amount += plant_dry_matter_residue_amount \
                                         * plant_residue_metabolic_fraction - \
                                         (plant_metabolic_active_carbon_usage + plant_metabolic_to_soil_carbon_amount)
        return plant_metabolic_carbon_amount

    @staticmethod
    def _determine_plant_metabolic_active_carbon_usage(decomposition_moisture_effect: float,
                                                       decomposition_temperature_effect: float,
                                                       plant_metabolic_carbon_amount: float,
                                                       plant_metabolic_active_carbon_rate=0.28) -> float:
        """Calculates the amount of plant metabolic carbon decomposed to active carbon (kg/ha)
        Parameters
        ----------
        decomposition_moisture_effect: float
            moisture effect on decomposition factor (unitless)
        decomposition_temperature_effect: float
            temperature effect on decomposition factor (unitless)
        plant_metabolic_carbon_amount: float
            plant metabolic carbon amount (kg/ha)
        plant_metabolic_active_carbon_rate: float default = 0.28 (Parton et al. 1987)
            rate of decomposition from metabolic to active carbon (unitless)

        Returns
        -------
        float
            above ground metabolic carbon decomposed to active carbon (kg/ha)

        References
        -------
        pseudocode_soil S.6.B.I.5
        """
        return decomposition_moisture_effect * decomposition_temperature_effect * \
               plant_metabolic_carbon_amount * plant_metabolic_active_carbon_rate

    @staticmethod
    def _determine_plant_metabolic_to_soil_carbon_amount(plant_metabolic_carbon_amount: float,
                                                         tillage_fraction: float) -> float:
        """This method calculates the amount of metabolic carbon incorporated into soil during tillage (kg/ha)

        Parameters
        ----------
        plant_metabolic_carbon_amount: float
            amount of metabolic carbon in plant (kg/ha)
        tillage_fraction: float
            Fraction of metabolic carbon incorporated into soil during tillage (unitless)
        Returns
        -------
        float
            the amount of metabolic carbon incorporated into soil during tillage (kg/ha)

        References
        -------
        pseudocode_soil S.6.B.I.6
        """
        return plant_metabolic_carbon_amount * tillage_fraction

    @staticmethod
    def _determine_plant_structural_to_slow_or_active_rate(plant_residue_metabolic_fraction: float,
                                                           structural_decomposition_factor=0.076) -> float:
        """This method calculates the rate at which above ground structural carbon decomposes into slow or active carbon

        Parameters
        ----------
        structural_decomposition_factor: float, default = 0.076 (Parton et al. 1987)
            structural decomposition factor (unitless)
        plant_residue_metabolic_fraction: float
            fraction of plant residue that is metabolic (unitless)
        Returns
        -------
        float
            the rate at which above ground structural carbon decomposes into slow or active carbon (unitless)

        References
        -------
        pseudocode_soil S.6.B.I.9

        Notes
        -------
        the equation used here currently follows the old code to make mathematical sense
        """
        return structural_decomposition_factor * math.exp(-3) * (1 - plant_residue_metabolic_fraction)

    @staticmethod
    def _determine_plant_structural_to_slow_active_carbon_amount(plant_structural_to_slow_or_active_rate: float,
                                                                 decomposition_moisture_effect: float,
                                                                 decomposition_temperature_effect: float,
                                                                 plant_structural_carbon_amount: float) -> float:
        """This method determines the amount of plant structural carbon decomposed into slow or active carbon

        Parameters
        ----------
        plant_structural_to_slow_or_active_rate: float
            rate at which above ground structural carbon decomposes into slow or active carbon (unitless)
        decomposition_moisture_effect: float
            moisture effect on decomposition factor (unitless)
        decomposition_temperature_effect: float
            temperature effect on decomposition factor (unitless)
        plant_structural_carbon_amount: float
            pant structural carbon amount(kg/ha)

        Returns
        -------
        float
            amount of plant structural carbon decomposed into slow or active carbon (kg/ha)

        References
        -------
        pseudocode_soil S.6.B.I.10
        """
        return plant_structural_to_slow_or_active_rate * decomposition_moisture_effect \
               * decomposition_temperature_effect \
               * plant_structural_carbon_amount

    @staticmethod
    def _determine_structural_carbon_transfer_amount(plant_structural_carbon_amount: float,
                                                     tillage_fraction: float) -> float:
        """Determines the amount of transfer of plant structural to soil structural carbon during tillage

        Parameters
        ----------
        plant_structural_carbon_amount: float
            amount of plant structural carbon (kg/ha)
        tillage_fraction: float
            fraction of metabolic carbon incorporated into soil during tillage (unitless)

        Returns
        -------
        float
        the amount of transfer of structural carbon during tillage (kg/ha)

        References
        -------
        pseudocode_soil S.6.B.I.11
        """
        return plant_structural_carbon_amount * tillage_fraction

    @staticmethod
    def _determine_plant_structural_carbon_amount(plant_dry_matter_residue_amount: float,
                                                  plant_residue_metabolic_fraction: float,
                                                  structural_carbon_transfer_amount: float,
                                                  plant_structural_to_active_carbon_amount: float,
                                                  plant_structural_to_slow_carbon_amount: float,
                                                  plant_structural_carbon_amount: float) -> float:
        """Calculates the updated plant structural carbon amount

        Parameters
        ----------
        plant_dry_matter_residue_amount: float
            amount of dry matter residue at harvest (kg/ha)
        plant_residue_metabolic_fraction: float
            fraction of plant residue that is metabolic (unitless)
        structural_carbon_transfer_amount: float
            the amount of transfer of structural carbon during tillage (kg/ha)
        plant_structural_to_active_carbon_amount: float
            amount of plant structural carbon decomposed into slow carbon (kg/ha)
        plant_structural_to_slow_carbon_amount: float
            amount of plant structural carbon decomposed into active carbon (kg/ha)
        plant_structural_carbon_amount: float
            plant structural carbon amount (kg/ha)
        Returns
        -------
        float
            updated plant structural carbon amount (kg/ha)

        References
        -------
        pseudocode_soil S.6.B.I.8, S.6.B.I.12
        """
        updated_amount = plant_structural_carbon_amount + plant_dry_matter_residue_amount \
                         * (1 - plant_residue_metabolic_fraction) - structural_carbon_transfer_amount \
                         - plant_structural_to_active_carbon_amount \
                         - plant_structural_to_slow_carbon_amount

        return updated_amount

    @staticmethod
    def _determine_weighted_residue_dry_matter_lignin_fraction(soil_dry_matter_residue_amount: float,
                                                               root_biomass: float) -> float:
        """Calculates the weighted fractional of lignin amount in residue dry matter

        Parameters
        ----------
        soil_dry_matter_residue_amount: float
            the amount of soil dry matter residue at harvest (kg/ha)
        root_biomass: float
            root biomass (kg/ha)

        Returns
        -------
        float
            the weighted fractional of lignin amount in residue dry matter (unitless)

        References
        -------
        pseudocode_soil S.6.B.II.2

        Notes
        -------
        the referenced soil(below ground) biomass calculation was not found in the pseudocode_crop, neither is any
        mention of biomass unit
        """
        if soil_dry_matter_residue_amount + root_biomass != 0:
            return soil_dry_matter_residue_amount / (soil_dry_matter_residue_amount + root_biomass)
        else:
            return 0

    @staticmethod
    def _determine_soil_residue_lignin_fraction(weighted_residue_dry_matter_lignin_fraction: float,
                                                rainfall: float) -> float:
        """Calculates the fraction of soil residue that's comprised of lignin

        Parameters
        ----------
        weighted_residue_dry_matter_lignin_fraction: float
            the weighted fractional of lignin amount in residue dry matter (unitless)
        rainfall: float
            amount of rain (mm H2O)

        Returns
        -------
        float
            the fraction of soil residue that's comprised of lignin (unitless)

        References
        -------
        pseudocode_soil S.6.B.II.3
        """
        # TODO: Check where the 0.15 and 0.01 factors came from issue #445
        return max(0.0, weighted_residue_dry_matter_lignin_fraction - 0.15 * rainfall * 0.01)

    @staticmethod
    def _determine_soil_lignin_to_nitrogen_fraction(plant_lignin_nitrogen_ratio: float,
                                                    weighted_residue_dry_matter_lignin_fraction: float,
                                                    soil_residue_lignin_fraction: float,
                                                    nitrogen_fraction_plant_residue=0.4) -> float:
        """This method calculates the soil lignin to nitrogen fraction

        Parameters
        ----------
        plant_lignin_nitrogen_ratio: float
            plant lignin to nitrogen ratio (unitless)
        weighted_residue_dry_matter_lignin_fraction: float
            weighted fraction of lignin in residue dry matter (unitless)
        soil_residue_lignin_fraction: float
            soil residue fraction that is composed of lignin (unitless)
        nitrogen_fraction_plant_residue: float default = 0.4
            nitrogen fraction in plant residue at harvest (unitless)

        Returns
        -------
        float
            soil lignin to nitrogen fraction(unitless)

        References
        -------
        pseudocode_soil S.6.B.II.4
        """
        if 0 < nitrogen_fraction_plant_residue <= 1:
            return plant_lignin_nitrogen_ratio * weighted_residue_dry_matter_lignin_fraction + \
                   (((soil_residue_lignin_fraction / 100) / nitrogen_fraction_plant_residue) / 100) \
                   * (1 - weighted_residue_dry_matter_lignin_fraction)
        elif nitrogen_fraction_plant_residue == 0:
            return 0
        else:
            raise ValueError("Expected nitrogen_fraction_plant_residue to be between 0.0-1.0, received "
                             + str(nitrogen_fraction_plant_residue))

    @staticmethod
    def _determine_soil_residue_metabolic_fraction(soil_lignin_to_nitrogen_fraction: float) -> float:
        """This method calculates the fraction of soil residue that is metabolic

        Parameters
        ----------
        soil_lignin_to_nitrogen_fraction: float
            soil lignin to nitrogen fraction(unitless)

        Returns
        -------
        float
            the fraction of soil residue that is metabolic(unitless)

        References
        -------
        pseudocode_soil S.6.B.II.5
        """
        return max(0.0, 0.85 - 0.18 * soil_lignin_to_nitrogen_fraction)

    @staticmethod
    def _determine_soil_metabolic_carbon_amount(soil_metabolic_carbon_amount: float,
                                                plant_metabolic_to_soil_carbon_amount: float,
                                                root_biomass: float,
                                                soil_residue_metabolic_fraction: float,
                                                soil_metabolic_active_carbon_usage: float) -> float:
        """This method updates the amount of soil metabolic carbon

        Parameters
        ----------
        soil_metabolic_carbon_amount: float
            the amount of soil metabolic carbon (kg/ha)
        plant_metabolic_to_soil_carbon_amount: float
            the amount of metabolic carbon incorporated into soil during tillage (kg/ha)
        root_biomass: float
            root biomass (kg/ha)
        soil_residue_metabolic_fraction: float
            the fraction of soil residue that is metabolic (unitless)
        soil_metabolic_active_carbon_usage: float
            the amount of soil metabolic carbon decomposed into active carbon (kg/ha)

        Returns
        -------
        float
            the updated amount of soil metabolic carbon (kg/ha)

        References
        -------
        pseudocode_soil S.6.B.II.6, S.6.B.II.8
        """
        result = soil_metabolic_carbon_amount + plant_metabolic_to_soil_carbon_amount + \
                 (root_biomass * soil_residue_metabolic_fraction) - soil_metabolic_active_carbon_usage
        return result

    @staticmethod
    def _determine_soil_metabolic_to_active_carbon_amount(decomposition_moisture_effect: float,
                                                          decomposition_temperature_effect: float,
                                                          soil_metabolic_carbon_amount: float,
                                                          soil_metabolic_active_carbon_rate=0.35) -> float:
        """This method calculates the amount of soil metabolic carbon decomposed into active carbon

        Parameters
        ----------
        decomposition_moisture_effect: float
            moisture effect on decomposition factor (unitless)
        decomposition_temperature_effect: float
            temperature effect on decomposition factor (unitless)
        soil_metabolic_carbon_amount: float
            soil metabolic carbon amount (kg/ha)
        soil_metabolic_active_carbon_rate: float default = 0.35
            rate of decomposition from soil metabolic to active carbon (unitless)

        Returns
        -------
        float
            amount of soil metabolic carbon decomposed into active carbon(kg/ha)

        References:
        -------
        pseudocode_soil S.6.B.II.7

        """
        return decomposition_temperature_effect * decomposition_moisture_effect * soil_metabolic_carbon_amount * \
               soil_metabolic_active_carbon_rate

    @staticmethod
    def _determine_soil_structural_to_slow_active_carbon_amount(decomposition_moisture_effect: float,
                                                                decomposition_temperature_effect: float,
                                                                soil_structural_carbon_amount: float,
                                                                soil_structural_to_slow_or_active_rate=0.094) -> float:
        """This method determines the amount of soil structural carbon decomposed into slow or active carbon

        Parameters
        ----------
        soil_structural_to_slow_or_active_rate: float default = 0.094 (Parton et al. 1987)
            rate at which soil structural carbon decomposes into slow or active carbon (unitless)
        decomposition_moisture_effect: float
            moisture effect on decomposition factor (unitless)
        decomposition_temperature_effect: float
            temperature effect on decomposition factor (unitless)
        soil_structural_carbon_amount: float
            soil structural carbon amount(kg/ha)

        Returns
        -------
        float
            amount of soil structural carbon decomposed into slow or active carbon (kg/ha)

        References
        -------
        pseudocode_soil S.6.B.II.10

        Notes
        -------
        This method can be used for both calculating amount of soil structural carbon decomposed into slow carbon and
        amount of soil structural carbon decomposed into active carbon.
        """
        return decomposition_moisture_effect * decomposition_temperature_effect * soil_structural_carbon_amount * \
               soil_structural_to_slow_or_active_rate

    @staticmethod
    def _determine_soil_structural_carbon_amount(soil_residue_metabolic_fraction: float,
                                                 structural_carbon_transfer_amount: float,
                                                 soil_structural_to_active_carbon_amount: float,
                                                 soil_structural_to_slow_carbon_amount: float,
                                                 root_biomass: float,
                                                 soil_structural_carbon_amount: float) -> float:
        """Calculates the updated soil structural carbon amount

        Parameters
        ----------
        soil_residue_metabolic_fraction: float
            fraction of soil residue that is metabolic (unitless)
        structural_carbon_transfer_amount: float
            the amount of transfer of structural carbon during tillage (kg/ha)
        soil_structural_to_active_carbon_amount: float
            amount of soil structural carbon decomposed into slow carbon (kg/ha)
        soil_structural_to_slow_carbon_amount: float
            amount of soil structural carbon decomposed into active carbon (kg/ha)
        root_biomass: float
            root biomass (kg/ha)
        soil_structural_carbon_amount: float
            soil structural carbon amount (kg/ha)
        Returns
        -------
        float
            updated soil structural carbon amount (kg/ha)

        References
        -------
        pseudocode_soil S.6.B.II.9, S.6.B.II.11
        """
        updated_amount = soil_structural_carbon_amount + structural_carbon_transfer_amount + root_biomass * \
                         (1 - soil_residue_metabolic_fraction) - soil_structural_to_active_carbon_amount - \
                         soil_structural_to_slow_carbon_amount

        return updated_amount
