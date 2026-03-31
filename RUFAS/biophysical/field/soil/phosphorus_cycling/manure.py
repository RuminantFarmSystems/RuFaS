from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class Manure:
    """
    This module adds and tracks manure phosphorus dynamics based on the SurPhos model.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
        provided.
    field_size : float, optional
        Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
        not provided (ha).
    Attributes
    ----------
    data : SoilData
        Stores the SoilData object for tracking the dynamics of manure phosphorus, including its distribution,
         transformation, and potential loss mechanisms.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def daily_manure_update(
        self,
        rainfall: float,
        runoff: float,
        field_size: float,
        mean_air_temperature: float,
    ) -> None:
        """
        This method conducts daily operations on manure including decomposition, assimilation into soil, etc.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm).
        runoff : float
            The amount of runoff from rainfall on the current day (mm).
        field_size : float
            The size of the field (ha).
        mean_air_temperature : float
            Mean air temperature on the current day (degrees C).

        Notes
        -----
        This method orchestrates the three major processes (and one more minor process) that act on manure on the manure
        on the surface of the field. The three major processes are leaching, decomposition, and assimilation. The minor
        process is the adjustment of the manure's moisture factor. Leaching is conducted first, then the adjustment of
        the moisture factors. Decomposition and assimilation occur simultaneously.

        """
        self.data.machine_manure.runoff_reset()
        self.data.grazing_manure.runoff_reset()
        if rainfall > 0:
            self._leach_and_update_phosphorus_pools(rainfall, runoff, field_size)
        machine_total = self.data.machine_manure.daily_manure_update(rainfall, field_size, mean_air_temperature)
        grazing_total = self.data.grazing_manure.daily_manure_update(rainfall, field_size, mean_air_temperature)

        total_assimilated_phosphorus = grazing_total + machine_total
        self._add_infiltrated_phosphorus_to_soil(total_assimilated_phosphorus, field_size)

    def _leach_and_update_phosphorus_pools(self, rainfall: float, runoff: float, field_size: float) -> None:
        """
        This method handles all calls to the methods that determine how much phosphorus is leached from manure, how
        that leached phosphorus is distributed, and updates the phosphorus pools based on those values.

        Parameters
        ----------
        rainfall : float
            The amount of rainfall on the current day (mm).
        runoff : float
            The amount of runoff from rainfall on the current day (mm).
        field_size : float
            The size of the field (ha).

        """
        if self.data.machine_manure.determine_phosphorus_leach():
            organic_phosphorus, inorganic_phosphorus = self.data.machine_manure.leach_phosphorus_pools(
                rainfall, runoff, field_size
            )
            self._add_infiltrated_phosphorus_to_soil(organic_phosphorus, field_size)
            self._add_infiltrated_phosphorus_to_soil(inorganic_phosphorus, field_size)

        if self.data.grazing_manure.determine_phosphorus_leach():
            organic_phosphorus, inorganic_phosphorus = self.data.grazing_manure.leach_phosphorus_pools(
                rainfall, runoff, field_size
            )
            self._add_infiltrated_phosphorus_to_soil(organic_phosphorus, field_size)
            self._add_infiltrated_phosphorus_to_soil(inorganic_phosphorus, field_size)

    def _add_infiltrated_phosphorus_to_soil(self, infiltrated_phosphorus_amount: float, field_size: float) -> None:
        """
        This method adds phosphorus that was dissolved in rainfall to the soil profile as outlined in SurPhos.

        Parameters
        ----------
        infiltrated_phosphorus_amount : float
            The amount of phosphorus to be added to the soil profile (kg).
        field_size : float
            The size of the field (ha).

        References
        ----------
        SurPhos Theoretical, page 8, paragraph below [13]

        Notes
        -----
        This method follows what is outlined in SurPhos (theoretical documentation, page 8, paragraph just below eqn.
        [13]), which is that 80% of infiltrated phosphorus stays in the top 20 mm of soil, and the rest infiltrates
        deeper.

        """
        self.data.soil_layers[0].add_to_labile_phosphorus(0.8 * infiltrated_phosphorus_amount, field_size)
        self.data.soil_layers[1].add_to_labile_phosphorus(0.2 * infiltrated_phosphorus_amount, field_size)
