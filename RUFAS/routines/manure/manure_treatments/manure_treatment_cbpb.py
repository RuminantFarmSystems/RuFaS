from __future__ import annotations

from RUFAS.routines.manure.gas_emissions.calculator import (
    GasEmissionsCalculator,
)
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import (
    BaseManureTreatment,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    ManureTreatmentConfig,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import (
    ManureTreatmentDailyOutput,
)


class CompostBeddedPackBarn(BaseManureTreatment):
    """Class for the compost bedded pack barn.

    Attributes:
        All attributes inherited from BaseManureTreatment.

    """

    def __init__(
        self, weather, time, manure_treatment_config: ManureTreatmentConfig
    ) -> None:
        """Initializes the compost bedded pack barn manure treatment.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_treatment_config: A ManureTreatmentConfig object containing
                the configuration data for the manure treatment system.
        """

        super().__init__(weather, time, manure_treatment_config)

    def _calc_bedding_potassium_content(
        self,
        current_manure_bedding_mix_potassium: float,
        additional_potassium_in_manure: float,
        additional_potassium_in_bedding: float = 0,
        potassium_loss: float = 0,
    ) -> float:
        """Calculates the potassium content of the manure-bedding mixture.

        Parameters
        ----------
        current_manure_bedding_mix_potassium : float
          The current potassium content of the manure-bedding mixture.

        additional_potassium_in_manure : float
          The amount of potassium in the current day's manure production amount.

        additional_potassium_in_bedding : float
          The amount of potassium in the current day's additional bedding amount.

        potassium_loss : float
          Loss of potassium within the compost bedded pack barn.

        Returns
        -------
        float
            The total potassium within the compost bedded pack barn's manure-bedding mixture (in kg).

        """
        return (
            current_manure_bedding_mix_potassium
            + additional_potassium_in_manure
            + additional_potassium_in_bedding
            - potassium_loss
        )

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """
        Calculate the daily output of the compost bedded pack barn manure treatment system.

        Returns
        -------
        ManureTreatmentDailyOutput
            A ManureTreatmentDailyOutput object containing the daily output of the
            compost bedded pack barn manure treatment system.

        """
        daily_input = self._current_manure_treatment_daily_input
        total_nitrogen_loss = (
            GasEmissionsCalculator.total_nitrogen_loss_from_compost_bedded_pack_barn(
                daily_nitrogen_input=daily_input.liquid_manure_nitrogen,
                is_bedding_tilled=True,
            )
        )
        manure_nitrogen = daily_input.liquid_manure_nitrogen - total_nitrogen_loss
        # TODO: To be implemented further later.
        daily_output = ManureTreatmentDailyOutput(
            simulation_day=daily_input.simulation_day,
            pen_id=daily_input.pen_id,
        )
        self._accumulate_daily_output(daily_output)
        return daily_output
