import math
from typing import Optional, List
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


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
        """This method calculates the plant lignin to nitrogen ratio when nitrogen in plant residue at harvest
        is greater than zero

        Parameters
        ----------
        plant_residue_lignin_composition : float
            lignin fraction of plant residue (unitless)
        nitrogen_fraction_plant_residue : float
            Nitrogen fraction in plant residue at harvest (unitless)

        Returns
        -------
        float
            plant lignin to nitrogen ratio (Dmnl)

        References
        -------
        pseudocode_soil S.6.B.I.2
        """
        if nitrogen_fraction_plant_residue != 0:
            return (plant_residue_lignin_composition / 100) / nitrogen_fraction_plant_residue
        else:
            return 0

    @staticmethod
    def _determine_plant_resdiue_metabolic_fraction(metabolic_plant_residue_ratio: float) -> float:
        """This method calculates the fraction of plant residue that is metabolic

        Parameters
        ----------
        metabolic_plant_residue_ratio : float
            plant lignin to nitrogen ratio (Dmnl)

        Returns
        -------
        float
            plant residue fraction that is metabolic (unitless)


        References
        -------
        pseudocode_soil S.6.B.I.3
        """
        return 0.85 - 0.18 * metabolic_plant_residue_ratio
