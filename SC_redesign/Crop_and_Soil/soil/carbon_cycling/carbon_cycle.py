#from . import decomposition, pool_gas_partition, residue_partition
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from typing import Optional
from from SC_redesign.Crop_and_Soil.crop_and_soil_constants import *


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
    def _determine_soil_slow_carbon_fraction(slow_carbon_amount: float, soil_mass) -> float:
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
    def _determine_soil_passive_carbon_fraction(passive_carbon_amount: float, soil_mass) -> float:
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
    def _determine_total_soil_carbon_amount_mg(total_soil_carbon_amount: float):
        """This method calculates the total amount of soil carbon in mg

        Parameters
        ----------
        total_soil_carbon_amount: float
            the total amount of soil carbon (kg/ha)

        Returns
        -------
        float
            the total amount of soil carbon (mg/ha)

        References
        -------
        pseudoode_soil S.6.D.4
        """
        return total_soil_carbon_amount * KILOGRAMS_TO_MILLIGRAMS

    @staticmethod
    def _determine_total_soil_carbon_amount_g(total_soil_carbon_amount: float):
        """This method calculates the total amount of soil carbon in g

        Parameters
        ----------
        total_soil_carbon_amount: float
            the total amount of soil carbon (kg/ha)

        Returns
        -------
        float
            the total amount of soil carbon (g/ha)

        References
        -------
        pseudoode_soil S.6.D.4
        """
        return total_soil_carbon_amount * KILOGRAMS_TO_GRAMS
