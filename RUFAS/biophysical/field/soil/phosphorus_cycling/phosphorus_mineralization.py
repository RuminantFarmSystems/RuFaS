from math import exp, log
from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class PhosphorusMineralization:
    """
    Manages the transfer of phosphorus between the various inorganic phosphorus pools in each soil layer, based
    on the "Inorganic Soil P Model" section of SurPhos.

    Parameters
    ----------
    soil_data : SoilData, optional
        An instance of SoilData to be used for tracking manure phosphorus activity. If not provided, a new instance
        will be created with the given field size.
    field_size : float, optional
        The size of the field (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData object that contains data and functionality related to soil and phosphorus properties.

    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def mineralize_phosphorus(self, field_size) -> None:
        """
        This method handles the daily re-averaging of the phosphorus sorption parameter, then iterates through the
        soil profile and calls the appropriate method for adjusting its phosphorus pools.

        Parameters
        ----------
        field_size : float
            Size of the field (ha).

        Notes
        -----
        The constants used in many of this module's subroutines differed between older versions of this code and the
        literature. The constants from the old code are used here.

        Sorption is the process of phosphorus mineralizing from the labile inorganic pool to the active inorganic pool,
        and desorption is the other way around.

        When sorption occurs, the program checks whether the current phosphorus imbalance is greater than it was the day
        before, and if so it resets unbalanced counter for the labile pool, which has the effect of sorping the maximum
        amount possible from the labile pool.

        """
        for layer in self.data.soil_layers:
            soil_phosphorus_content = layer.determine_soil_nutrient_concentration(
                layer.labile_inorganic_phosphorus_content,
                layer.bulk_density,
                layer.layer_thickness,
                field_size,
            )
            current_phosphorus_sorption_parameter = layer.calculate_phosphorus_sorption_parameter(
                layer.clay_fraction,
                soil_phosphorus_content,
                layer.organic_carbon_fraction,
            )
            layer.mean_phosphorus_sorption_parameter = self._recompute_mean_phosphorus_sorption_parameter(
                layer.mean_phosphorus_sorption_parameter,
                current_phosphorus_sorption_parameter,
            )

            balance = self._determine_phosphorus_imbalance(
                layer.labile_inorganic_phosphorus_content,
                layer.active_inorganic_phosphorus_content,
                layer.mean_phosphorus_sorption_parameter,
            )

            if balance < 0:
                layer.active_inorganic_unbalanced_counter += 1
                layer.labile_inorganic_unbalanced_counter = 0

                phosphorus_mineralized = self._calculate_phosphorus_desorption(
                    layer.active_inorganic_unbalanced_counter,
                    layer.mean_phosphorus_sorption_parameter,
                    balance,
                )
                phosphorus_mineralized = min(layer.active_inorganic_phosphorus_content, phosphorus_mineralized)
            elif balance > 0:
                layer.active_inorganic_unbalanced_counter = 0
                if layer.previous_phosphorus_balance is not None and layer.previous_phosphorus_balance < balance:
                    layer.labile_inorganic_unbalanced_counter = 0
                layer.labile_inorganic_unbalanced_counter += 1

                phosphorus_mineralized = self._calculate_phosphorus_sorption(
                    layer.labile_inorganic_unbalanced_counter,
                    layer.mean_phosphorus_sorption_parameter,
                    balance,
                )
                phosphorus_mineralized = min(layer.labile_inorganic_phosphorus_content, phosphorus_mineralized)
                phosphorus_mineralized *= -1
            else:
                layer.labile_inorganic_unbalanced_counter = 0
                layer.active_inorganic_unbalanced_counter = 0
                phosphorus_mineralized = 0

            layer.active_inorganic_phosphorus_content -= phosphorus_mineralized
            layer.labile_inorganic_phosphorus_content += phosphorus_mineralized

            layer.previous_phosphorus_balance = balance

            stable_to_active_mineralization_amount = self._determine_stable_to_active_phosphorus_mineralization(
                layer.stable_inorganic_phosphorus_content,
                layer.active_inorganic_phosphorus_content,
            )
            layer.stable_inorganic_phosphorus_content -= stable_to_active_mineralization_amount
            layer.active_inorganic_phosphorus_content += stable_to_active_mineralization_amount

    # --- Static methods ---
    @staticmethod
    def _recompute_mean_phosphorus_sorption_parameter(
        mean_sorption_parameter: float, current_sorption_parameter: float
    ) -> float:
        """
        Recalculates the mean sorption parameter based on current day's condition.

        Parameters
        ----------
        mean_sorption_parameter : float
            The mean phosphorus sorption parameter of the given soil layer (unitless).
        current_sorption_parameter : float
            The phosphorus sorption parameter of the given soil layer calculated with the layer's current conditions
                                                                                                            (unitless).

        Returns
        -------
        float
            The mean phosphorus sorption parameter that has been adjusted for the current day's amount of labile
            inorganic phosphorus present (unitless).

        References
        ----------
        SurPhos Fortran code, pminrl.f, lines 48 - 51

        Notes
        -----
        The phosphorus sorption parameter, in the words of Pete Vadas, "represents sort of a long term chemical
        characteristic of the soil and should NOT be calculated every day. There can be big changes in labile P when P
        is added to soils in fertilizer and manure, and we don’t want PSP changing rapidly." Be recalculating the
        phosphorus sorption parameter with this equation every day (as opposed to recalculating it with
        calculate_phosphorus_sorption_parameter() in LayerData), we keep changes in it limited. This equation
        approximates taking a weighted average over a time span that is determined by the `days_to_average_over_value`,
        currently set to the length of a year.

        """
        days_to_average_over = 365
        weighted_sum_to_average = (days_to_average_over - 1) * mean_sorption_parameter + current_sorption_parameter
        new_mean_phosphorus_sorption_parameter = weighted_sum_to_average / days_to_average_over
        return max(0.05, min(0.7, new_mean_phosphorus_sorption_parameter))

    @staticmethod
    def _determine_phosphorus_imbalance(
        labile_phosphorus: float, active_phosphorus: float, sorption_parameter: float
    ) -> float:
        """
        Calculates the imbalance of phosphorus between the labile and active inorganic pools.

        Parameters
        ----------
        labile_phosphorus : float
            Labile inorganic phosphorus content of this soil layer (kg / ha).
        active_phosphorus : float
            Active inorganic phosphorus content of this soil layer (kg / ha).
        sorption_parameter : float
            The phosphorus sorption parameter of this layer (unitless).

        Returns
        -------
        float
            A value indicating how unbalanced the labile and active inorganic phosphorus pools are (unitless).

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
    def _calculate_phosphorus_desorption(
        active_inorganic_unbalanced_counter: int,
        sorption_parameter: float,
        phosphorus_balance: float,
    ) -> float:
        """
        Calculates how much phosphorus should be desorped in the given soil layer.

        Parameters
        ----------
        active_inorganic_unbalanced_counter : int
            The number of days that the active inorganic phosphorus pool has been greater than it would be when in
            equilibrium with the labile inorganic phosphorus pool.
        sorption_parameter : float
            The mean phosphorus sorption parameter that has been adjusted for the current day's amount of labile
            inorganic phosphorus present (unitless).
        phosphorus_balance : float
            A value indicating how unbalanced the labile and active inorganic phosphorus pools are (unitless).

        Returns
        -------
        float
            The amount of phosphorus that should be removed from the active inorganic phosphorus pool to put it in
            equilibrium with the labile inorganic phosphorus pool (kg / ha).

        References
        ----------
        SurPhos pminrl.f, lines 69, 70
        Vadas P.A., Krogstad T., Sharpley A.N. (2006) Modeling phosphorus transfer between labile and nonlabile soil
            pools: Updating the EPIC model. Soil Science Society of America Journal 70:736-743. DOI:
            Doi 10.2136/Sssaj2005.0067. (Eqn. [8])

        """
        base = PhosphorusMineralization._determine_desorption_base(sorption_parameter)
        desorption_factor = base * (active_inorganic_unbalanced_counter**-0.32)
        amount_transferred = desorption_factor * phosphorus_balance * -1
        return amount_transferred

    @staticmethod
    def _determine_desorption_base(sorption_parameter: float) -> float:
        """
        This method calculates a value used to determine how much phosphorus is desorped from the active inorganic
        phosphorus pool in the labile organic phosphorus pool.

        Parameters
        ----------
        sorption_parameter : float
            The mean phosphorus sorption parameter that has been adjusted for the current day's amount of labile
            inorganic phosphorus present (unitless).

        Returns
        -------
        float
            A value (named 'base' in code and literature) that is used to determine how much phosphorus is transferred
            from the active inorganic phosphorus pool to the labile inorganic phosphorus pool (unitless).

        References
        ----------
        SurPhos pminrl.f, line 59
        Vadas P.A., Krogstad T., Sharpley A.N. (2006) Modeling phosphorus transfer between labile and nonlabile soil
            pools: Updating the EPIC model. Soil Science Society of America Journal 70:736-743. DOI:
            Doi 10.2136/Sssaj2005.0067. (Eqn. [7])

        """
        return (-1 * sorption_parameter) + 0.8

    @staticmethod
    def _calculate_phosphorus_sorption(
        labile_inorganic_unbalanced_counter: int,
        sorption_parameter: float,
        phosphorus_balance: float,
    ) -> float:
        """
        Calculates how much phosphorus should be sorped in the given soil layer.

        Parameters
        ----------
        labile_inorganic_unbalanced_counter : int
            The number of days that the labile inorganic phosphorus pool has been greater than it would be when in
            equilibrium with the labile inorganic phosphorus pool.
        sorption_parameter : float
            The mean phosphorus sorption parameter that has been adjusted for the current day's amount of labile
            inorganic phosphorus present (unitless).
        phosphorus_balance : float
            A value indicating how unbalanced the labile and active inorganic phosphorus pools are (unitless).

        Returns
        -------
        float
            The amount of phosphorus that should be removed from the labile inorganic phosphorus pool to put it in
            equilibrium with the active inorganic phosphorus pool (kg / ha).

        References
        ----------
        SurPhos pminrl.f, lines 92, 94
        Vadas P.A., Krogstad T., Sharpley A.N. (2006) Modeling phosphorus transfer between labile and nonlabile soil
            pools: Updating the EPIC model. Soil Science Society of America Journal 70:736-743. DOI:
            Doi 10.2136/Sssaj2005.0067. (Eqn. [4])

        """
        scalar = PhosphorusMineralization._determine_sorption_scalar(sorption_parameter)
        exponent = PhosphorusMineralization._determine_sorption_exponent(scalar)
        sorption_factor = scalar * (labile_inorganic_unbalanced_counter**exponent)
        amount_transferred = sorption_factor * phosphorus_balance
        return amount_transferred

    @staticmethod
    def _determine_sorption_scalar(sorption_parameter: float) -> float:
        """
        Determines the scalar used to calculate the sorption factor.

        Parameters
        ----------
        sorption_parameter : float
            The mean phosphorus sorption parameter that has been adjusted for the current day's amount of labile
            inorganic phosphorus present (unitless).

        Returns
        -------
        float
            The scalar used in determining how much phosphorus is removed from the labile inorganic phosphorus pool and
            transferred to the active inorganic phosphorus pool (unitless).

        References
        ----------
        SurPhos pminrl.f, line 56
        Vadas P.A., Krogstad T., Sharpley A.N. (2006) Modeling phosphorus transfer between labile and nonlabile soil
            pools: Updating the EPIC model. Soil Science Society of America Journal 70:736-743. DOI:
            Doi 10.2136/Sssaj2005.0067. (Eqn. [6])

        """
        return 0.918 * exp(-4.603 * sorption_parameter)

    @staticmethod
    def _determine_sorption_exponent(sorption_scalar: float) -> float:
        """
        Determines the exponential term used to calculate the sorption factor.

        Parameters
        ----------
        sorption_scalar
            The scalar used in determining how much phosphorus is removed from the labile inorganic phosphorus pool and
            transferred to the active inorganic phosphorus pool (unitless).

        Returns
        -------
        float
            A value used as an exponential term when determining the phosphorus sorption rate (unitless).

        References
        ----------
        SurPhos pminrl.f, line 57
        Vadas P.A., Krogstad T., Sharpley A.N. (2006) Modeling phosphorus transfer between labile and nonlabile soil
            pools: Updating the EPIC model. Soil Science Society of America Journal 70:736-743. DOI:
            Doi 10.2136/Sssaj2005.0067. (Eqn. [5])

        """
        return (-0.238 * log(sorption_scalar)) - 1.126

    @staticmethod
    def _determine_stable_to_active_phosphorus_mineralization(
        stable_phosphorus: float, active_phosphorus: float
    ) -> float:
        """
        Determines how much phosphorus should be transferred from the stable pool to the active pool.

        Parameters
        ----------
        stable_phosphorus : float
            Stable inorganic phosphorus content of this soil layer (kg / ha).
        active_phosphorus : float
            Active inorganic phosphorus content of this soil layer (kg / ha).

        Returns
        -------
        float
            The amount of phosphorus to be transferred from the stable inorganic phosphorus pool to the active
            phosphorus inorganic pool (kg / ha).

        References
        ----------
        SurPhos pminrl.f, lines 108 - 110

        """
        amount_to_transfer = 0.0006 * (stable_phosphorus - (4.0 * active_phosphorus))
        if amount_to_transfer > 0:
            amount_to_transfer = min(stable_phosphorus, amount_to_transfer)
        elif (-1 * amount_to_transfer) > active_phosphorus:
            amount_to_transfer = -1 * active_phosphorus
        return amount_to_transfer
