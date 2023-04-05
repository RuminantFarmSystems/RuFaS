from typing import Optional
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

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
