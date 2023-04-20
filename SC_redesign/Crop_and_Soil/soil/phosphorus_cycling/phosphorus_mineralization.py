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
            current_phosphorus_sorption_parameter = layer.calculate_phosphorus_sorption_parameter(
                layer.percent_clay_content, soil_phosphorus_content, layer.percent_organic_carbon_content)
            layer.mean_phosphorus_sorption_parameter = self._recompute_mean_phosphorus_sorption_parameter(
                layer.mean_phosphorus_sorption_parameter, current_phosphorus_sorption_parameter)

            balance = self._determine_phosphorus_imbalance(layer.labile_inorganic_phosphorus_content,
                                                           layer.active_inorganic_phosphorus_content,
                                                           layer.mean_phosphorus_sorption_parameter)

            if balance < 0:  # Desorption
                layer.active_inorganic_unbalanced_counter += 1
                layer.labile_inorganic_unbalanced_counter = 0

                phosphorus_amount_to_transfer = self._calculate_phosphorus_desorption(
                    layer.active_inorganic_unbalanced_counter, layer.mean_phosphorus_sorption_parameter, balance)
                phosphorus_amount_to_transfer = min(layer.active_inorganic_phosphorus_content,
                                                    phosphorus_amount_to_transfer)
            elif balance > 0:  # Sorption
                layer.active_inorganic_unbalanced_counter = 0
                layer.labile_inorganic_unbalanced_counter += 1

                phosphorus_amount_to_transfer = self._calculate_phosphorus_sorption()
            else:  # Balanced
                layer.labile_inorganic_unbalanced_counter = 0
                layer.active_inorganic_unbalanced_counter = 0
                phosphorus_amount_to_transfer = 0

            pass

    # --- Static methods ---
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
        SurPhos Fortran code, pminrl.f, lines 48 - 51

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

    @staticmethod
    def _determine_phosphorus_imbalance(labile_phosphorus: float, active_phosphorus: float,
                                        sorption_parameter: float) -> float:
        """Calculates the imbalance of phosphorus between the labile and active inorganic pools.

        Parameters
        ----------
        labile_phosphorus : float
            Labile inorganic phosphorus content of this soil layer (kg phosphorus / ha)
        active_phosphorus : float
            Active inorganic phosphorus content of this soil layer (kg phosphorus / ha)
        sorption_parameter : float
            The phosphorus sorption parameter of this layer (unitless)

        Returns
        -------
        float
            A value indicating how unbalanced the labile and active inorganic phosphorus pools are (unitless)

        References
        ----------
        SWAT eqn. 3:2.3.2, 3 (Only the conditions that proceed the 'if')

        Notes
        -----
        A negative value returned indicates that there is more active phosphorus than there should be, a positive value
        indicates that there is more labile phosphorus than there should be, and a return value of zero indicates that
        the two pools are balanced.

        """
        return labile_phosphorus - (active_phosphorus * (sorption_parameter / (1 - sorption_parameter)))

    @staticmethod
    def _calculate_phosphorus_desorption(active_inorganic_unbalanced_counter: int, sorption_parameter: float,
                                         phosphorus_balance: float) -> float:
        """Calculates how much phosphorus should be desorped in the given soil layer.

        Parameters
        ----------
        active_inorganic_unbalanced_counter : int
            The number of days that the active inorganic phosphorus pool has been greater than it would be when in
            equilibrium with the labile inorganic phosphorus pool
        sorption_parameter : float
            The mean phosphorus sorption parameter that has been adjusted for the current day's amount of labile
            inorganic phosphorus present (unitless)
        phosphorus_balance : float
            A value indicating how unbalanced the labile and active inorganic phosphorus pools are (unitless)

        Returns
        -------
        float
            The amount of phosphorus that should be removed from the active inorganic phosphorus pool to put it in
            equilibrium with the labile inorganic phosphorus pool (kg phosphorus / ha)

        References
        ----------
        SurPhos pminrl.f, lines 69, 70
        Vadas P.A., Krogstad T., Sharpley A.N. (2006) Modeling phosphorus transfer between labile and nonlabile soil
            pools: Updating the EPIC model. Soil Science Society of America Journal 70:736-743. DOI:
            Doi 10.2136/Sssaj2005.0067. (Eqn. [8])

        Notes
        -----
        The constants used differ between the old code and the literature, the constants from the old code are used
        here.

        """
        base = PhosphorusMineralization._determine_desorption_base(sorption_parameter)
        desorption_factor = base * (active_inorganic_unbalanced_counter ** -0.32)
        amount_transferred = desorption_factor * phosphorus_balance * -1
        return amount_transferred

    @staticmethod
    def _determine_desorption_base(sorption_parameter: float) -> float:
        """This method calculates a value used to determine how much phosphorus is desorped from the active inorganic
            phosphorus pool in the labile organic phosphorus pool.

        Parameters
        ----------
        sorption_parameter : float
            The mean phosphorus sorption parameter that has been adjusted for the current day's amount of labile
            inorganic phosphorus present (unitless)

        Returns
        -------
        float
            A value (named 'base' in code and literature) that is used to determine how much phosphorus is transferred
            from the active inorganic phosphorus pool to the labile inorganic phosphorus pool.

        References
        ----------
        SurPhos pminrl.f, line 59
        Vadas P.A., Krogstad T., Sharpley A.N. (2006) Modeling phosphorus transfer between labile and nonlabile soil
            pools: Updating the EPIC model. Soil Science Society of America Journal 70:736-743. DOI:
            Doi 10.2136/Sssaj2005.0067. (Eqn. [7])

        Notes
        -----
        The constants used differ between the old code and the literature, the constants from the old code are used
        here.

        """
        return (-1 * sorption_parameter) + 0.8
