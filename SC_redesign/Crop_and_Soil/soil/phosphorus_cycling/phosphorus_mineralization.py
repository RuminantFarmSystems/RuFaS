from typing import Optional

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module manages transferring phosphorus between the various inorganic phosphorus pools in each soil layer, based on
the "Inorganic Soil P Model" section of SurPhos.
"""


class PhosphorusMineralization:

    def __init__(self, soil_data: Optional[SoilData] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track manure phosphorus activity, creates new one if one is not
            provided.

        """
        self.data = soil_data or SoilData()

    def mineralize_phosphorus(self, field_size) -> None:
        """This method handles the daily re-averaging of the phosphorus sorption parameter, then iterates through the
            soil profile and calls the appropriate method for adjusting its phosphorus pools.

        Parameters
        ----------
        field_size : float
            Size of the field (ha)

        """
        for layer in self.data.soil_layers:
            soil_phosphorus_content = layer.determine_soil_phosphorus_concentration(
                layer.labile_inorganic_phosphorus_content, layer.bulk_density, layer.layer_thickness, field_size)
            phosphorus_sorption_parameter_today = layer.calculate_phosphorus_sorption_parameter(
                layer.percent_clay_content, soil_phosphorus_content, layer.percent_organic_carbon_content)

    @staticmethod
    def _recompute_mean_phosphorus_sorption_parameter(mean_sorption_parameter: float,
                                                      current_sorption_parameter: float) -> float:
        """Recalculates the mean sorption parameter based on current day's condition.

        Parameters
        ----------
        mean_sorption_parameter : float
            The mean phosphorus sorption parameter of the given soil layer (unitless)
        current_sorption_parameter : float
            The phosphorus sorption parameter of the given soil layer calculated with the layer's current conditions
                                                                                                            (unitless)

        Returns
        -------
        float
            The mean phosphorus sorption parameter that has been adjusted for the current day's amount of labile
            inorganic phosphorus present (unitless)

        References
        ----------
        Surphos Fortran code, pminrl.f, lines 48 - 51

        Notes
        -----
        The phosphorus sorption parameter, in the words of Pete Vadas, "represents sort of a long term chemical
        characteristic of the soil and should NOT be calculated every day. There can be big changes in labile P when P
        is added to soils in fertilizer and manure, and we don’t want PSP changing rapidly." Be recalculating the
        phosphorus sorption parameter with this equation every day (as opposed to recalculating it with
        calculate_phosphorus_sorption_parameter() in LayerData), we keep changes in it limited.

        """
        new_mean_phosphorus_sorption_parameter = ((29 * mean_sorption_parameter) + current_sorption_parameter) / 30
        return max(0.05, min(0.7, new_mean_phosphorus_sorption_parameter))
