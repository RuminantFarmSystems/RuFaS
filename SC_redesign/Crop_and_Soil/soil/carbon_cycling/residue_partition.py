from typing import Optional
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
import math

"""
This class contains all necessary methods that involve residue partition, including both plant and soil and also
considers the case of tillage for plants

References
-------
pseudocode_soil S.6.B
"""


class ResiduePartition:

    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not

    @staticmethod
    def _determine_plant_residue_lignin_composition(plant_residue_lignin_composition: float,
                                                    rainfall: float) -> None:
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
    def _determine_metabolic_plant_residue_ratio(plant_residue_lignin_composition: float,
                                                 nitrogen_fraction_plant_residue=0.4) -> float:
        # TODO nitrogen_fraction_plant_residue calculate in RuFaS [C.5.B.1] but not "accurate" for carbon use -
        #  GitHub Issue #163
        """This method calculates the plant lignin to nitrogen ratio when nitrogen in plant residue at harvest
        is greater than zero

        Parameters
        ----------
        plant_residue_lignin_composition : float
            lignin fraction of plant residue (unitless)
        nitrogen_fraction_plant_residue : float, default = 0.4
            Nitrogen fraction in plant residue at harvest (unitless)

        Returns
        -------
        float
            plant lignin to nitrogen ratio (Dmnl)

        References
        -------
        pseudocode_soil S.6.B.I.2
        """
        if 0 < nitrogen_fraction_plant_residue < 1.0:
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
            plant lignin to nitrogen ratio (Dimensionless unit)

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
        in dry matter at harvest and and reduced by the amount that's decomposed and incorporated

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
                                                       metabolic_active_carbon_rate=0.28) -> float:
        # TODO: Double check the metabolic_active_carbon_rate, again, pseudocode_soil differs from the original code
        #  #issue 425
        """Calculates the the amount of plant metabolic carbon decomposed to active carbon (kg/ha)
        Parameters
        ----------
        decomposition_moisture_effect: float
            moisture effect on decomposition factor (unitless)
        decomposition_temperature_effect: float
            temperature effect on decomposition factor (unitless)
        plant_metabolic_carbon_amount: float
            plant metabolic carbon amount (kg/ha)
        metabolic_active_carbon_rate: float
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
            plant_metabolic_carbon_amount * metabolic_active_carbon_rate

    @staticmethod
    def _determine_plant_metabolic_to_soil_carbon_amount(plant_metabolic_carbon_amount: float,
                                                         tillage_fraction: float) -> float:
        """This method calculates the the amount of metabolic carbon incorporated into soil during tillage (kg/ha)

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
        # TODO: check with subject expert for structural_decomposition_factor's default value. issue #428
        """This method calculates the rate at which above ground structural carbon decomposes into slow or active carbon

        Parameters
        ----------
        structural_decomposition_factor: float, default = 0.076
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
        """
        # TODO: contradiction with the equation in pseudocode_soil. issue #427
        return structural_decomposition_factor * math.exp(-3) * 1 - plant_residue_metabolic_fraction

    @staticmethod
    def _determine_plant_structural_to_slow_active_carbon_amount(plant_structural_to_slow_or_active_rate: float,
                                                                 decomposition_moisture_effect: float,
                                                                 decomposition_temperature_effect: float,
                                                                 plant_structural_carbon_amount: float) -> float:
        """This methods determines the amount of plant structural carbon decomposed into slow or active carbon

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
            * decomposition_temperature_effect\
            * plant_structural_carbon_amount

    @staticmethod
    def _determine_structural_carbon_transfer_amount(plant_structural_carbon_amount: float,
                                                     tillage_fraction: float) -> float:
        """Determines the amount of transfer of structural carbon during tillage

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
            amount of dry matter residue at harvest (kg/ha)V
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
            * (1-plant_residue_metabolic_fraction) - structural_carbon_transfer_amount \
            - plant_structural_to_active_carbon_amount \
            - plant_structural_to_slow_carbon_amount

        return updated_amount