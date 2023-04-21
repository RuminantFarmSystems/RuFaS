# from . import decomposition, pool_gas_partition, residue_partition
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from typing import Optional
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import HECTARES_TO_SQUARE_MILLIMETERS,\
    CUBIC_MILLIMETERS_TO_CUBIC_METERS


class CarbonCycle:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    @staticmethod
    def _determine_soil_volume(layer_thickness: float, field_size: float) -> float:
        """This method calculates the soil volume

        Parameters
        ----------
        layer_thickness: float
            thickness of soil layer (mm)
        field_size: float
            Size of the field (ha)

        Returns
        -------
        float
            soil volume (cubic meters)

        References
        -------
        pseudoode_soil S.6.D.1
        """
        return (layer_thickness * field_size * HECTARES_TO_SQUARE_MILLIMETERS) * CUBIC_MILLIMETERS_TO_CUBIC_METERS

    @staticmethod
    def _determine_soil_mass(bulk_density: float, soil_volume: float) -> None:
        """This method calculates the mass of soil

        Parameters
        ----------
        bulk_density: float
            bulk density of the soil layer (Mg per cubic meter)
        soil_volume: float
            soil volume (cubic meters)

        Returns
        -------
        float
            mass of soil (kg)

        References
        -------
        pseudoode_soil S.6.D.1
        """
        return bulk_density * soil_volume

    @staticmethod
    def _determine_soil_active_carbon_fraction(active_carbon_amount: float, soil_mass) -> float:
        """This method calculates the fraction of active carbon in the soil

        Parameters
        ----------
        active_carbon_amount: float
            active carbon stored in the soil (kg/ha)
        soil_mass: float
            mass of soil (kg)

        Returns
        -------
        float
            fraction of active carbon in the soil (unitless)

        References
        -------
        pseudoode_soil S.6.D.2
        """
        return active_carbon_amount/soil_mass

    @staticmethod
    def _determine_soil_slow_carbon_fraction(slow_carbon_amount: float, soil_mass: float) -> float:
        """This method calculates the fraction of slow carbon in the soil

        Parameters
        ----------
        slow_carbon_amount: float
            slow carbon stored in the soil (kg/ha)
        soil_mass: float
            mass of soil (kg)

        Returns
        -------
        float
            fraction of slow carbon in the soil (unitless)

        References
        -------
        pseudoode_soil S.6.D.2
        """
        return slow_carbon_amount/soil_mass

    @staticmethod
    def _determine_soil_passive_carbon_fraction(passive_carbon_amount: float, soil_mass: float) -> float:
        """This method calculates the fraction of passive carbon in the soil

        Parameters
        ----------
        passive_carbon_amount: float
            passive carbon stored in the soil (kg/ha)
        soil_mass: float
            mass of soil (kg)

        Returns
        -------
        float
            fraction of passive carbon in the soil (unitless)

        References
        -------
        pseudoode_soil S.6.D.2
        """
        return passive_carbon_amount/soil_mass

    @staticmethod
    def _determine_soil_overall_carbon_fraction(soil_active_carbon_fraction: float,
                                                soil_slow_carbon_fraction: float,
                                                soil_passive_carbon_fraction: float) -> float:
        """This method calculates the total fraction of carbon in the soil

        Parameters
        ----------
        soil_active_carbon_fraction: float
            fraction of active carbon in the soil (unitless)
        soil_slow_carbon_fraction: float
            fraction of slow carbon in the soil (unitless)
        soil_passive_carbon_fraction: float
            fraction of passive carbon in the soil (unitless)

        Returns
        -------
        float
            the total fraction of carbon in the soil (unitless)

        References
        -------
        pseudoode_soil S.6.D.3
        """
        return soil_active_carbon_fraction + soil_passive_carbon_fraction + soil_slow_carbon_fraction

    @staticmethod
    def _determine_total_soil_carbon_amount(active_carbon_amount: float,
                                            slow_carbon_amount: float,
                                            passive_carbon_amount: float) -> float:
        """This method calculates the total amount of soil carbon

        Parameters
        ----------
        active_carbon_amount: float
            active carbon stored in the soil (kg/ha)
        slow_carbon_amount: float
            slow carbon stored in the soil (kg/ha)
        passive_carbon_amount: float
            passive carbon stored in the soil (kg/ha)

        Returns
        -------
        float
            the total amount of soil carbon (kg/ha)

        References
        -------
        pseudoode_soil S.6.D.4
        """
        return active_carbon_amount + slow_carbon_amount + passive_carbon_amount

    @staticmethod
    def _determine_total_plant_carbon_CO2_loss(plant_metabolic_active_carbon_loss: float,
                                               plant_structural_active_carbon_loss: float,
                                               plant_structural_slow_carbon_loss: float) -> float:
        """This method calculates the total amount plant carbon lost as CO2

        Parameters
        ----------
        plant_metabolic_active_carbon_loss: float
            plant metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)
        plant_structural_active_carbon_loss: float
            plant structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)
        plant_structural_slow_carbon_loss: float
            plant structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha)

        Returns
        -------
        float
            total amount plant carbon lost as CO2 (kg/ha)

        References
        -------
        pseudoode_soil S.6.D.5
        """
        return plant_metabolic_active_carbon_loss + plant_structural_active_carbon_loss + \
            plant_structural_slow_carbon_loss

    @staticmethod
    def _determine_total_soil_carbon_CO2_loss(soil_metabolic_active_carbon_loss: float,
                                              soil_structural_active_carbon_loss: float,
                                              soil_structural_slow_carbon_loss: float) -> float:
        """This method calculates the total amount soil carbon lost as CO2

        Parameters
        ----------
        soil_metabolic_active_carbon_loss: float
            soil metabolic carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)
        soil_structural_active_carbon_loss: float
            soil structural carbon being lost as carbon dioxide during decomposition into active carbon (kg/ha)
        soil_structural_slow_carbon_loss: float
            soil structural carbon being lost as carbon dioxide during decomposition into slow carbon (kg/ha)

        Returns
        -------
        float
            total amount soil carbon lost as CO2 (kg/ha)

        References
        -------
        pseudoode_soil S.6.D.5
        """
        return soil_metabolic_active_carbon_loss + soil_structural_active_carbon_loss + \
            soil_structural_slow_carbon_loss

    @staticmethod
    def _determine_total_decomposition_carbon_CO2_lost(active_carbon_to_slow_loss: float,
                                                       slow_carbon_co2_lost_amount: float,
                                                       passive_carbon_co2_lost_amount: float) -> float:
        """This method calculates the total amount of carbon lost as CO2 during decomposition

        Parameters
        ----------
        active_carbon_to_slow_loss: float
            active carbon lost as CO2 during decomposition into slow carbon (kg/ha)
        slow_carbon_co2_lost_amount: float
            slow carbon lost as CO2 during decomposition (kg/ha)
        passive_carbon_co2_lost_amount: float
            passive carbon lost as CO2 during decomposition (kg/ha)

        Returns
        -------
        float
            amount of total carbon lost as CO2 during decomposition(kg/ha)

        References
        -------
        pseudoode_soil S.6.D.6
        """
        return active_carbon_to_slow_loss + slow_carbon_co2_lost_amount + passive_carbon_co2_lost_amount

    @staticmethod
    def _determine_total_carbon_CO2_lost(total_plant_carbon_CO2_loss: float,
                                         total_soil_carbon_CO2_loss: float,
                                         total_decomposition_carbon_CO2_lost: float) -> float:
        """This method calculates the total amount of carbon lost as CO2

        Parameters
        ----------
        total_plant_carbon_CO2_loss: float
            total amount plant carbon lost as CO2 (kg/ha)
        total_soil_carbon_CO2_loss: float
            total amount soil carbon lost as CO2 (kg/ha)
        total_decomposition_carbon_CO2_lost: float
            amount of total carbon lost as CO2 during decomposition(kg/ha)
        Returns
        -------
        float
            total amount of carbon lost as CO2 (kg/ha)

        References
        -------
        pseudoode_soil S.6.D.7
        """
        return total_decomposition_carbon_CO2_lost + total_plant_carbon_CO2_loss + total_soil_carbon_CO2_loss
