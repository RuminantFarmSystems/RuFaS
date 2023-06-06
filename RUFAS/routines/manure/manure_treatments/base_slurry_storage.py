from abc import ABC

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput


class BaseSlurryStorage(BaseManureTreatment):
    def __init__(self, weather, time, manure_treatment_config) -> None:
        """
        Call the parent class initializer and set the attributes.

        Parameters
        ----------
        weather : Weather
            A Weather object.
        time : Time
            A Time object.
        manure_treatment_config : ManureTreatmentConfig
            A ManureTreatmentConfig object containing the configuration data for the manure treatment system.

        """
        super().__init__(weather, time, manure_treatment_config)

    def _update_methane_emission(self, daily_output: ManureTreatmentDailyOutput) -> None:
        """
        Calculate the methane emission from the slurry storage system.

        Parameters
        ----------
        daily_output : ManureTreatmentDailyOutput
            A ManureTreatmentDailyOutput object containing the daily output of the slurry storage system.

        Returns
        -------
        None
            Update the `storage_methane` attribute of the daily output object.

            Update the `storage_methane` and `liquid_manure_total_volatile_solids` attributes of the accumulated
            output object.

        """
        volatile_solids_factor = 3
        methane_emission = GasEmissions.calc_methane_emission_for_slurry_storage(
            total_volatile_solids=daily_output.liquid_manure_total_volatile_solids,
            temp=self._get_current_day_average_temperature_celsius()
        )
        methane_emission = max(methane_emission, 0.0)
        daily_output.storage_methane = methane_emission
        self._accumulated_output.storage_methane += methane_emission

        new_liquid_manure_total_volatile_solids = (daily_output.liquid_manure_total_volatile_solids -
                                                   methane_emission * volatile_solids_factor)
        self._accumulated_output.liquid_manure_total_volatile_solids += new_liquid_manure_total_volatile_solids

    def _update_ammonia_emission(self, daily_output: ManureTreatmentDailyOutput) -> None:
        """
        Calculate the ammonia emission from the slurry storage system.

        Parameters
        ----------
        daily_output : ManureTreatmentDailyOutput
            A ManureTreatmentDailyOutput object containing the daily output of the slurry storage system.

        Returns
        -------
        None
            Update the `storage_ammonia` attribute of the daily output object.

            Update the `storage_ammonia` attribute of the accumulated output object.

        """
        manure_total_ammoniacal_nitrogen = (
                daily_output.liquid_manure_total_ammoniacal_nitrogen +
                self._current_pen.manure.urine_total_ammoniacal_nitrogen -
                self._manure_handler_daily_output.housing_ammonia
        )
        storage_ammonia_emission = GasEmissions.calc_storage_ammonia_emission(
            num_animals=self._current_pen.num_animals,
            manure_total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            manure_volume=daily_output.daily_final_manure_volume,
            total_solids=daily_output.liquid_manure_total_solids,
            storage_area=GasEmissionConstants.DEFAULT_STORAGE_AREA,
            temp=self._get_current_day_average_temperature_celsius(),
            pH=GasEmissionConstants.DEFAULT_PH_FOR_STORAGE_AMMONIA
        )
        daily_output.storage_ammonia = storage_ammonia_emission
        self._accumulated_output.storage_ammonia += storage_ammonia_emission

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """
        Return the daily output of a general slurry storage system.

        Returns
        -------
        ManureTreatmentDailyOutput
            A ManureTreatmentDailyOutput object containing the daily output of the
            slurry storage underfloor system.

        """
        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        self._accumulate_daily_output(daily_output)

        self._update_methane_emission(daily_output)
        self._update_ammonia_emission(daily_output)

        return daily_output
