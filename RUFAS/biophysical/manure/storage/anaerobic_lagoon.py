from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time


class AnaerobicLagoon(Storage):
    """
    Anaerobic Lagoon class

    Parameters
    ----------
    name: str
        The name of the storage.
    is_housing_emissions_calculator: bool
        True if the storage is used for housing emissions calculation.
    cover: StorageCover
        The cover for the storage.
    storage_time_period: int | None
        The storage time period.
    surface_area: float
        The surface area of the storage.
    nitrous_oxide_emissions_factor: float
        The nitrous oxide emissions factor.
    capacity: float
        The capacity of the storage.

    """

    def __init__(
        self,
        name: str,
        is_housing_emissions_calculator: bool,
        cover: StorageCover,
        storage_time_period: int | None,
        surface_area: float,
        nitrous_oxide_emissions_factor: float,
        capacity: float,
    ):
        """Initialize Anaerobic Lagoon object."""
        super().__init__(name, is_housing_emissions_calculator, cover, storage_time_period, surface_area,
                         nitrous_oxide_emissions_factor, capacity)

    def process_manure(self, current_day_conditions: CurrentDayConditions, tim: Time) -> dict[str, ManureStream]:
        # 1. CURRENT version
        # daily_input = self._current_manure_treatment_daily_input
        # daily_output = self._initialize_daily_output_during_update(daily_input)

        # REFRESH version
        # Covered by Storage.process_manure()

        # 2. CURRENT version
        # adjusted_daily_final_manure_volume = self._adjust_final_manure_volume(daily_output.daily_final_manure_volume)
        # daily_output.set_daily_final_manure_volume(adjusted_daily_final_manure_volume)

        # REFRESH version
        if self._cover in [StorageCover.NO_COVER, StorageCover.CRUST]:
            self._received_manure.volume += (
                current_day_conditions.precipitation * GeneralConstants.MM_TO_M * self._surface_area
            )
            self._received_manure.water += (
                current_day_conditions.precipitation
                * GeneralConstants.MM_TO_M
                * self._surface_area
                * GeneralConstants.WATER_DENSITY_KG_PER_M3
            )

        # 3. CURRENT version
        # self._adjust_accumulated_output(daily_output) - checks whether to empty manure stream

        # REFRESH version
        # Accomplished by Storage.process_manure()

        # 4. CURRENT version
        # self._accumulated_precipitation_volume += self.precipitation_volume

        # REFRESH version
        processed_manure = super()._process_manure(current_day_conditions, tim)

        # 5. CURRENT version
        # self._update_ammonia_emission(daily_output)
        
        # REFRESH version
        ammonia_emissions = self._calculate_ammonia_emissions(
            processed_manure.total_ammoniacal_nitrogen,
            processed)


        # methane_loss, methane_emission_from_degradable_volatile_solids = self._update_methane_emission(
        #     self._accumulated_output
        # )

        daily_output.storage_methane = methane_loss

        if self.config.manure_cover == ManureCoverEnum.COVER_AND_FLARE.value:
            daily_output.storage_methane_burned, daily_output.storage_methane = self.calculate_cover_and_flare_methane(
                methane_loss
            )

        methane_emission_from_non_degradable_volatile_solids = (
            methane_loss - methane_emission_from_degradable_volatile_solids
        )

        new_daily_output_liquid_manure_nitrogen = max(
            daily_output.liquid_manure_nitrogen - daily_output.storage_ammonia, 0.0
        )
        daily_output.liquid_manure_nitrogen = new_daily_output_liquid_manure_nitrogen

        self._accumulated_output.storage_ammonia += daily_output.storage_ammonia
        self._accumulated_output.storage_methane += daily_output.storage_methane

        new_accumulated_liquid_manure_total_solids = max(
            self._accumulated_output.liquid_manure_total_solids
            - (methane_loss * GasEmissionConstants.METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO),
            0.0,
        )
        self._accumulated_output.liquid_manure_total_solids = new_accumulated_liquid_manure_total_solids

        new_accumulated_liquid_manure_total_volatile_solids = max(
            self._accumulated_output.liquid_manure_total_volatile_solids
            - (methane_loss * GasEmissionConstants.METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO),
            0.0,
        )
        self._accumulated_output.liquid_manure_total_volatile_solids = (
            new_accumulated_liquid_manure_total_volatile_solids
        )

        new_accumulated_liquid_manure_total_degradable_volatile_solids = max(
            self._accumulated_output.liquid_manure_total_degradable_volatile_solids
            - (
                methane_emission_from_degradable_volatile_solids
                * GasEmissionConstants.METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
            ),
            0.0,
        )
        self._accumulated_output.liquid_manure_total_degradable_volatile_solids = (
            new_accumulated_liquid_manure_total_degradable_volatile_solids
        )

        new_accumulated_liquid_manure_total_non_degradable_volatile_solids = max(
            self._accumulated_output.liquid_manure_total_non_degradable_volatile_solids
            - (
                methane_emission_from_non_degradable_volatile_solids
                * GasEmissionConstants.METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
            ),
            0.0,
        )
        self._accumulated_output.liquid_manure_total_non_degradable_volatile_solids = (
            new_accumulated_liquid_manure_total_non_degradable_volatile_solids
        )

        new_accumulated_liquid_manure_nitrogen = max(
            self._accumulated_output.liquid_manure_nitrogen - daily_output.storage_ammonia,
            0.0,
        )
        self._accumulated_output.liquid_manure_nitrogen = new_accumulated_liquid_manure_nitrogen

        new_accumulated_liquid_manure_total_ammoniacal_nitrogen = max(
            self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen - daily_output.storage_ammonia,
            0.0,
        )
        self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen = (
            new_accumulated_liquid_manure_total_ammoniacal_nitrogen
        )
        emissions_factor = self._get_nitrous_oxide_emissions_factor(
            ManureTreatmentType.ANAEROBIC_LAGOON, self.config.manure_cover
        )
        daily_output.storage_nitrous_oxide = (
            GasEmissionsCalculator.calculate_empirical_nitrogen_loss_from_nitrous_oxide_emission(
                emission_factor_kg_nitrous_oxide_N_per_kg_manure_N=emissions_factor,
                manure_nitrogen_kg_N_per_day=daily_input.liquid_manure_nitrogen,
            )
        )
        daily_output.liquid_manure_nitrogen -= daily_output.storage_nitrous_oxide
        self._accumulated_output.storage_nitrous_oxide += daily_output.storage_nitrous_oxide
        self._accumulated_output.liquid_manure_nitrogen -= daily_output.storage_nitrous_oxide

        return daily_output
