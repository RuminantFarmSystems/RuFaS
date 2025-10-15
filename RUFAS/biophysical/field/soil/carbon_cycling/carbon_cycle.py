from typing import Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.carbon_cycling.decomposition import Decomposition
from RUFAS.biophysical.field.soil.carbon_cycling.pool_gas_partition import PoolGasPartition
from RUFAS.biophysical.field.soil.carbon_cycling.residue_partition import ResiduePartition
from RUFAS.biophysical.field.soil.soil_data import SoilData


class CarbonCycling:
    """
    Manages the carbon cycling processes within a field, including the decomposition of organic matter,
    partitioning between different pools and gases, and handling of crop residues.

    Parameters
    ----------
    soil_data : Optional[SoilData], default None
        An instance of `SoilData` containing initial soil properties and state. If not provided,
        a default instance with initialized values is used.

    Attributes
    ----------
    data : SoilData
        The data structure containing soil properties, carbon pools, and other relevant information for carbon cycling.
    decomposition : Decomposition
        Handles the decomposition effect for each layer and temperature effect.
    pool_gas_partition : PoolGasPartition
        Manages the partitioning of carbon between different soil pools and the process of transfer to CO2.
    residue_partition : ResiduePartition
        Processes residues partition, including both plant and soil and also considers the case of tillage for plants.

    References
    -------
    pseudocode_soil S.6.D.1 to S.6.D.7

    Notes
    -----
    This class encapsulates the mechanisms for updating all forms of aggregated carbon in the soil,
    invoking various routines related to carbon flux and storage.

    """

    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

        self.decomposition = Decomposition(self.data)
        self.pool_gas_partition = PoolGasPartition(self.data)
        self.residue_partition = ResiduePartition(self.data)

    def cycle_carbon(self, rainfall: float, temp_average: float, field_size: float) -> None:
        """
        Main routine for carbon cycle.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm)
        temp_average : float
            Average temperature on the current day (mm)
        field_size : float
            Size of the field (ha)

        """
        self.decomposition.decompose()
        self.residue_partition.partition_residue(rainfall)
        self.pool_gas_partition.partition_pool_gas()
        self._soil_carbon_aggregation(field_size)

    def _soil_carbon_aggregation(self, field_size: float) -> None:
        """
        This method updates aggregated attributes throughout the module.

        Parameters
        ----------
        field_size: float
            Size of the field (ha)

        """
        for layer in self.data.soil_layers:
            soil_volume = self._determine_soil_volume(layer.layer_thickness, field_size)
            soil_mass = (
                self._determine_soil_mass(layer.bulk_density, soil_volume) * GeneralConstants.MEGAGRAMS_TO_KILOGRAMS
            )
            soil_active_carbon_fraction = self._determine_soil_active_carbon_fraction(
                layer.active_carbon_amount, soil_mass, field_size
            )
            soil_slow_carbon_fraction = self._determine_soil_slow_carbon_fraction(
                layer.slow_carbon_amount, soil_mass, field_size
            )
            soil_passive_carbon_fraction = self._determine_soil_passive_carbon_fraction(
                layer.passive_carbon_amount, soil_mass, field_size
            )
            layer.soil_overall_carbon_fraction = self._determine_soil_overall_carbon_fraction(
                soil_active_carbon_fraction,
                soil_slow_carbon_fraction,
                soil_passive_carbon_fraction,
            )
            layer.total_soil_carbon_amount = self._determine_total_soil_carbon_amount(
                layer.active_carbon_amount,
                layer.slow_carbon_amount,
                layer.passive_carbon_amount,
            )
            total_plant_carbon_CO2_loss = self._determine_total_plant_carbon_CO2_loss(
                layer.plant_metabolic_active_carbon_loss,
                layer.plant_structural_active_carbon_loss,
                layer.plant_structural_slow_carbon_loss,
            )
            total_soil_carbon_CO2_loss = self._determine_total_soil_carbon_CO2_loss(
                layer.soil_metabolic_active_carbon_loss,
                layer.soil_structural_active_carbon_loss,
                layer.soil_structural_slow_carbon_loss,
            )
            layer.annual_decomposition_carbon_CO2_lost = self._determine_total_decomposition_carbon_CO2_lost(
                layer.active_carbon_to_slow_loss,
                layer.slow_carbon_co2_lost_amount,
                layer.passive_carbon_co2_lost_amount,
            )
            layer.annual_carbon_CO2_lost = self._determine_total_carbon_CO2_lost(
                total_plant_carbon_CO2_loss,
                total_soil_carbon_CO2_loss,
                layer.annual_decomposition_carbon_CO2_lost,
            )

    @staticmethod
    def _determine_soil_volume(layer_thickness: float, field_size: float) -> float:
        """
        This method calculates the soil volume.

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

        """
        return (
            layer_thickness * field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
        ) * GeneralConstants.CUBIC_MILLIMETERS_TO_CUBIC_METERS

    @staticmethod
    def _determine_soil_mass(bulk_density: float, soil_volume: float) -> float:
        """
        This method calculates the mass of soil.

        Parameters
        ----------
        bulk_density: float
            bulk density of the soil layer (Megagrams per cubic meter)
        soil_volume: float
            soil volume (cubic meters)

        Returns
        -------
        float
            mass of soil (Megagrams)

        """
        return bulk_density * soil_volume

    @staticmethod
    def _determine_soil_active_carbon_fraction(
        active_carbon_amount: float, soil_mass: float, field_size: float
    ) -> float:
        """
        This method calculates the fraction of active carbon in the soil.

        Parameters
        ----------
        active_carbon_amount: float
            active carbon stored in the soil (kg/ha)
        soil_mass: float
            mass of soil (kg)
        field_size: float
            size of the field (ha)

        Returns
        -------
        float
            fraction of active carbon in the soil (unitless)

        References
        -------
        pseudoode_soil S.6.D.2

        """
        return active_carbon_amount * field_size / soil_mass

    @staticmethod
    def _determine_soil_slow_carbon_fraction(slow_carbon_amount: float, soil_mass: float, field_size: float) -> float:
        """
        This method calculates the fraction of slow carbon in the soil.

        Parameters
        ----------
        slow_carbon_amount: float
            slow carbon stored in the soil (kg/ha)
        soil_mass: float
            mass of soil (kg)
        field_size: float
            size of the field (ha)

        Returns
        -------
        float
            fraction of slow carbon in the soil (unitless)

        References
        -------
        pseudoode_soil S.6.D.2

        """
        return slow_carbon_amount * field_size / soil_mass

    @staticmethod
    def _determine_soil_passive_carbon_fraction(
        passive_carbon_amount: float, soil_mass: float, field_size: float
    ) -> float:
        """
        This method calculates the fraction of passive carbon in the soil.

        Parameters
        ----------
        passive_carbon_amount: float
            passive carbon stored in the soil (kg/ha)
        soil_mass: float
            mass of soil (kg)
        field_size: float
            size of the field (ha)

        Returns
        -------
        float
            fraction of passive carbon in the soil (unitless)

        References
        -------
        pseudoode_soil S.6.D.2

        """
        if passive_carbon_amount is None:
            return 0
        return passive_carbon_amount * field_size / soil_mass

    @staticmethod
    def _determine_soil_overall_carbon_fraction(
        soil_active_carbon_fraction: float, soil_slow_carbon_fraction: float, soil_passive_carbon_fraction: float
    ) -> float:
        """
        This method calculates the total fraction of carbon in the soil.

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
            the total fraction of carbon in the soil by mass(unitless)

        References
        -------
        pseudoode_soil S.6.D.3

        """
        return soil_active_carbon_fraction + soil_passive_carbon_fraction + soil_slow_carbon_fraction

    @staticmethod
    def _determine_total_soil_carbon_amount(
        active_carbon_amount: float, slow_carbon_amount: float, passive_carbon_amount: float
    ) -> float:
        """
        This method calculates the total amount of soil carbon.

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
    def _determine_total_plant_carbon_CO2_loss(
        plant_metabolic_active_carbon_loss: float,
        plant_structural_active_carbon_loss: float,
        plant_structural_slow_carbon_loss: float,
    ) -> float:
        """
        This method calculates the total amount plant carbon lost as CO2.

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
        return (
            plant_metabolic_active_carbon_loss + plant_structural_active_carbon_loss + plant_structural_slow_carbon_loss
        )

    @staticmethod
    def _determine_total_soil_carbon_CO2_loss(
        soil_metabolic_active_carbon_loss: float,
        soil_structural_active_carbon_loss: float,
        soil_structural_slow_carbon_loss: float,
    ) -> float:
        """
        This method calculates the total amount soil carbon lost as CO2.

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
        return soil_metabolic_active_carbon_loss + soil_structural_active_carbon_loss + soil_structural_slow_carbon_loss

    @staticmethod
    def _determine_total_decomposition_carbon_CO2_lost(
        active_carbon_to_slow_loss: float, slow_carbon_co2_lost_amount: float, passive_carbon_co2_lost_amount: float
    ) -> float:
        """
        This method calculates the total amount of carbon lost as CO2 during decomposition.

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
    def _determine_total_carbon_CO2_lost(
        total_plant_carbon_CO2_loss: float,
        total_soil_carbon_CO2_loss: float,
        total_decomposition_carbon_CO2_lost: float,
    ) -> float:
        """
        This method calculates the total amount of carbon lost as CO2.

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
        pseudocode_soil S.6.D.7

        """
        return total_decomposition_carbon_CO2_lost + total_plant_carbon_CO2_loss + total_soil_carbon_CO2_loss
