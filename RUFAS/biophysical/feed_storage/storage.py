from dataclasses import replace
from datetime import date
from typing import Any, List

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import CropCategory, CropType, HarvestedCrop
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather

"""
These constants define the upper and lower bounds of temperatures that allow fermentation (in degrees C), the upper and
lower fractions of dry matter that allow fermentation, and the constants that regulate how dry matter is lost to
fermentation. These values are defined in the Feed Storage Scientific Documentation, section 1.3.
"""
ALFALFA_FERMENTATION_CONSTANTS: dict[str, float] = {
    "lower_temp_limit": 5.0,
    "upper_temp_limit": 45.0,
    "lower_dry_matter_limit": 0.20,
    "upper_dry_matter_limit": 0.60,
    "loss_coefficient": 0.0364,
    "base_loss_fraction": 0.0156,
}

NON_ALFALFA_FERMENTATION_CONSTANTS: dict[str, float] = {
    "lower_temp_limit": 0.0,
    "upper_temp_limit": 40.0,
    "lower_dry_matter_limit": 0.15,
    "upper_dry_matter_limit": 0.60,
    "loss_coefficient": 0.0193,
    "base_loss_fraction": 0.00864,
}


class Storage:
    """
    Abstract class representing a general storage structure.

    Attributes
    ----------
    acceptable_crops : List[CropCategory]
        The list of crop categories that this storage can recieve.
    capacity : float
        The maximum capacity of the storage, currently set to infinity.
    stored : List[HarvestedCrop]
        A list of HarvestedCrop objects representing the crops stored.
    crude_protein_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust crude protein after dry matter loss.
    starch_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust starch after dry matter loss.
    adf_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust ADF after dry matter loss.
    ndf_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust NDF after dry matter loss.
    lignin_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust lignin after dry matter loss.
    ash_loss_coefficient : float, default 0.0
        Fractional coefficient used to adjust ash after dry matter loss.

    Methods
    -------
    stored_mass()
        The total mass (kg) of currently stored crops
    receive_crop(crop: HarvestedCrop, time: RufasTime)
        Receives a harvested crop and adds it to the storage.
    process_degradations(current_conditions: CurrentDayConditions, time: RufasTime)
        Processes the degradations and losses of the stored crops.
    give_feed(amount: float, crop_type: str)
        Gives out a specified amount of feed of a certain crop type.
    reset_mass_attributes_after_loss(self, crop: HarvestedCrop, dry_matter_loss: float, moisture_loss: float)
        Resets mass related attributes after loss of dry matter and/or moisture.
    record_stored_crops(self)
        Records information about total mass and nutrient content of the stored crops.
    calculate_dry_matter_loss_to_gas(dry_matter: float, time_in_silo: int)
        Calculates the dry matter loss to gas.
    calculate_bale_density(initial_dry_matter: float)
        Calculates the density of a bale.
    recalculate_nutrient_percentage(
        initial_nutrient_percentage: float,
        loss_coefficient: float,
        dry_matter_loss: float,
        initial_dry_matter: float
    )
        Recalculates a single nutrient percentage after dry matter loss.

    """

    def __init__(self, capacity: float = float("inf")):
        self.acceptable_crops: List[CropCategory] = []
        self.capacity = capacity
        self.stored: List[HarvestedCrop] = []
        self.crude_protein_loss_coefficient = 0.0
        self.starch_loss_coefficient = 0.0
        self.adf_loss_coefficient = 0.0
        self.ndf_loss_coefficient = 0.0
        self.lignin_loss_coefficient = 0.0
        self.ash_loss_coefficient = 0.0
        self.om = OutputManager()

    @property
    def stored_mass(self) -> float:
        """The total mass (kg) of currently stored crops"""
        return sum(crop.fresh_mass for crop in self.stored)

    def receive_crop(self, crop: HarvestedCrop) -> None:
        """
        Receives a harvested crop and adds it to the storage.

        Parameters
        ----------
        crop : HarvestedCrop
            The harvested crop to be added to the storage.

        Returns
        -------
        None

        Raises
        ------
        NotImplementedError
            If the storage's acceptable crops is not populated.
        ValueError
            If the crop's category is not compatible with the storage.
        Exception
            If adding the crop exceeds the storage's capacity.

        """
        if not self.acceptable_crops:
            raise NotImplementedError(
                "Storage.acceptable_crops is not populated, consider populating it in the child class."
            )
        if crop.category not in self.acceptable_crops:
            raise ValueError(
                f"Can't recieve the crop, the compatible crop categories are {self.acceptable_crops=},\
                    {crop.category} is not one of them."
            )
        if self.stored_mass + crop.fresh_mass > self.capacity:
            raise Exception(
                f"Adding {crop.fresh_mass} to currently stored ({self.stored_mass})\
                    exceeds the storage capacity ({self.capacity})"
            )
        self.stored.append(crop)

    def process_degradations(self, weather: Weather, time: RufasTime) -> None:
        """
        Processes the degradations and losses of nutrients and dry matter in the stored crops.

        Parameters
        ----------
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        Notes
        -----
        This method also records the total amount of gaseous dry matter loss happened from all stored crops.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.process_degradations.__name__,
            "units": MeasurementUnits.KILOGRAMS,
        }
        total_gaseous_dry_matter_loss = 0.0
        for crop in self.stored:
            degraded_crop_values = self._calculate_degradation_values(crop, weather, time)
            total_gaseous_dry_matter_loss += degraded_crop_values["gaseous_dry_matter_loss"]
            crop.crude_protein_percent = degraded_crop_values["crude_protein_percent"]
            crop.starch = degraded_crop_values["starch"]
            crop.adf = degraded_crop_values["adf"]
            crop.ndf = degraded_crop_values["ndf"]
            crop.lignin = degraded_crop_values["lignin"]
            crop.ash = degraded_crop_values["ash"]
            crop.last_time_degraded = degraded_crop_values["last_time_degraded"]
        print(f"debug_total_gaseous_dry_matter_loss from process_degradations(): {total_gaseous_dry_matter_loss}")
        self.om.add_variable("debug_gaseous_dry_matter_loss", total_gaseous_dry_matter_loss, info_map)
        self.record_stored_crops()

    def project_degradations(
        self, crops: list[HarvestedCrop], weather: Weather, time: RufasTime
    ) -> list[HarvestedCrop]:
        """
        Projects the state of crops currently stored at a given future date.

        Parameters
        ----------
        crops : list[HarvestedCrop]
            List of HarvestedCrops to project degradations for.
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance containing the date at which the state of the stored crops should be projected.

        Returns
        -------
        list[HarvestedCrop]
            Crops in the state they are projected to be in at the given date.

        """
        degraded_crops: list[HarvestedCrop] = []
        for crop in crops:
            degraded_crop_values = self._calculate_degradation_values(crop, weather, time)
            last_time_degraded = degraded_crop_values["last_time_degraded"]
            del degraded_crop_values["gaseous_dry_matter_loss"]
            del degraded_crop_values["last_time_degraded"]
            degraded_crop = replace(crop, **degraded_crop_values)
            degraded_crop.last_time_degraded = last_time_degraded
            degraded_crops.append(degraded_crop)
        return degraded_crops

    def _calculate_degradation_values(self, crop: HarvestedCrop, weather: Weather, time: RufasTime) -> dict[str, Any]:
        """
        Calculates the loss from the given crop and state of the remaining crop mass.

        Parameters
        ----------
        crop : HarvestedCrop
            Crop for which degradations are being calculated.
        weather : Weather
            Weather instance containing all weather information for the simulation.
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        Returns
        -------
        dict[str, Any]
            Mapping the attributes of the crop after degradation to their values.

        """
        weather_conditions = self._get_conditions(crop.last_time_degraded, time, weather)
        gaseous_dry_matter_loss = self.calculate_dry_matter_loss_to_gas(crop, weather_conditions, time)
        print(f"gaseous_dry_matter_loss from _calculate_degradation_values(): {gaseous_dry_matter_loss}")
        self.om.add_variable(
            "debug_gaseous_dry_matter_loss", gaseous_dry_matter_loss, {
                "class": self.__class__.__name__,
                "function": self.calculate_dry_matter_loss_to_gas.__name__, "units": MeasurementUnits.KILOGRAMS
            }
        )
        self.om.add_variable(
            "debug_weather_conditions", weather_conditions, {
                "class": self.__class__.__name__,
                "function": self._get_conditions.__name__, "units": MeasurementUnits.KILOGRAMS
            }
        )
        crude_protein_percent = self.recalculate_nutrient_percentage(
            crop.crude_protein_percent,
            self.crude_protein_loss_coefficient,
            gaseous_dry_matter_loss,
            crop.dry_matter_mass,
        )
        starch = self.recalculate_nutrient_percentage(
            crop.starch, self.starch_loss_coefficient, gaseous_dry_matter_loss, crop.dry_matter_mass
        )
        adf = self.recalculate_nutrient_percentage(
            crop.adf, self.adf_loss_coefficient, gaseous_dry_matter_loss, crop.dry_matter_mass
        )
        ndf = self.recalculate_nutrient_percentage(
            crop.ndf, self.ndf_loss_coefficient, gaseous_dry_matter_loss, crop.dry_matter_mass
        )
        lignin = self.recalculate_nutrient_percentage(
            crop.lignin, self.lignin_loss_coefficient, gaseous_dry_matter_loss, crop.dry_matter_mass
        )
        ash = self.recalculate_nutrient_percentage(
            crop.ash, self.ash_loss_coefficient, gaseous_dry_matter_loss, crop.dry_matter_mass
        )
        mass_values = self._calculate_mass_attributes_after_loss(crop, gaseous_dry_matter_loss, moisture_loss=0.0)
        last_time_degraded = time.current_date.date()

        return {
            "gaseous_dry_matter_loss": gaseous_dry_matter_loss,
            "crude_protein_percent": crude_protein_percent,
            "starch": starch,
            "adf": adf,
            "ndf": ndf,
            "lignin": lignin,
            "ash": ash,
            "fresh_mass": mass_values["fresh_mass"],
            "dry_matter_percentage": mass_values["dry_matter_percentage"],
            "last_time_degraded": last_time_degraded,
        }

    def give_feed(self, amount: float, crop_type: CropType) -> None:
        """
        Gives out a specified amount of feed of a certain crop type.

        Parameters
        ----------
        amount : float
            The amount of feed to give out.
        crop_type : CropType
            The type of crop to give out.

        """
        pass

    def remove_empty_crops(self) -> None:
        """Removes all crops with no dry matter mass left."""
        self.stored = [crop for crop in self.stored if crop.dry_matter_mass > 0.0]

    def _calculate_mass_attributes_after_loss(
        self, crop: HarvestedCrop, dry_matter_loss: float, moisture_loss: float
    ) -> dict[str, float]:
        """
        Resets the dry mass, fresh mass, and dry matter percentage attributes in a stored crop after loss of both dry
        matter and moisture.

        Parameters
        ----------
        crop : HarvestedCrop
            The stored crop that has lost dry matter.
        dry_matter_loss : float
            Amount of dry matter the crop lost on the current day (kg).
        moisture_loss : float
            Amount of moisture (water) the crop lost on the current day (kg).

        Returns
        -------
        dict[str, float]
            Fresh mass and dry matter percentage of the crop after loss (kg and percentage, respectively).

        Notes
        -----
        The amount of dry matter mass remaining is calculated first, then the remaining amount of fresh mass. After
        these two attributes have been set, the dry matter percentage is recalculated and set.

        """
        new_dry_matter_mass = crop.dry_matter_mass - dry_matter_loss
        new_fresh_mass = crop.fresh_mass - (dry_matter_loss + moisture_loss)
        if new_fresh_mass == 0.0:
            dry_matter_percentage = 0.0
        else:
            dry_matter_percentage = new_dry_matter_mass / new_fresh_mass * GeneralConstants.FRACTION_TO_PERCENTAGE
        return {"fresh_mass": new_fresh_mass, "dry_matter_percentage": dry_matter_percentage}

    def record_stored_crops(self) -> None:
        """
        Records the total mass and nutrient amounts held in storage.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.record_stored_crops.__name__,
            "units": MeasurementUnits.KILOGRAMS,
        }
        self.om.add_variable("total_fresh_mass", self.stored_mass, info_map)

        total_dry_matter_mass = sum([crop.dry_matter_mass for crop in self.stored])
        self.om.add_variable("total_dry_matter_mass", total_dry_matter_mass, info_map)

        total_digestible_dry_matter = self._get_total_nutritive_amount("dry_matter_digestibility")
        self.om.add_variable("total_digestible_dry_matter", total_digestible_dry_matter, info_map)

        total_crude_protein = self._get_total_nutritive_amount("crude_protein_percent")
        self.om.add_variable("total_crude_protein", total_crude_protein, info_map)

        total_non_protein_nitrogen = self._get_total_nutritive_amount("non_protein_nitrogen")
        self.om.add_variable("total_non_protein_nitrogen", total_non_protein_nitrogen, info_map)

        total_starch = self._get_total_nutritive_amount("starch")
        self.om.add_variable("total_starch", total_starch, info_map)

        total_adf = self._get_total_nutritive_amount("adf")
        self.om.add_variable("total_adf", total_adf, info_map)

        total_ndf = self._get_total_nutritive_amount("ndf")
        self.om.add_variable("total_ndf", total_ndf, info_map)

        total_lignin = self._get_total_nutritive_amount("lignin")
        self.om.add_variable("total_lignin", total_lignin, info_map)

        total_sugar = self._get_total_nutritive_amount("sugar")
        self.om.add_variable("total_sugar", total_sugar, info_map)

        total_ash = self._get_total_nutritive_amount("ash")
        self.om.add_variable("total_ash", total_ash, info_map)

    def _get_total_nutritive_amount(self, nutrient_name: str) -> float:
        """
        Calculates the total amount of the specifed nutrient that is currently held in storage.

        Parameters
        ----------
        nutrient_name : str
            The name of the target nutrient attribute in HarvestedCrop.

        Returns
        -------
        float
            Total amount of the target nutrient in the stored crops (kg).

        """
        total_nutrient: float = sum(
            [
                getattr(crop, nutrient_name) * GeneralConstants.PERCENTAGE_TO_FRACTION * crop.dry_matter_mass
                for crop in self.stored
            ]
        )
        return total_nutrient

    def calculate_dry_matter_loss_to_gas(
        self, crop: HarvestedCrop, weather_conditions: list[CurrentDayConditions], time: RufasTime
    ) -> float:
        """
        Calculates the dry matter loss to gas, specific to dry matter loss from fermentation.

        Parameters
        ----------
        crop : HarvestedCrop
            The stored crop that is losing dry matter.
        weather_conditions : list[CurrentDayConditions]
            List of daily weather conditions over which dry matter loss will be calculated.
        time : RufasTime
            RufasTime instance containing the time that loss should be processed up to.

        Returns
        -------
        float
            The amount of dry matter lost to gas, specific to fermentation (kg).

        References
        ----------
        .. [1] Feed Storage Scientific Documentation equations 1.3.1 and 1.3.2

        Notes
        -----
        If the ambient temperature or dry matter percentage of the crop do not fall within the acceptable ranges, then
        no dry matter loss occurs. Alfalfa uses different parameters and limits for calculating dry matter loss,
        but the structure of the loss equation remains the same.

        Note that the current time is not needed for calculating the dry matter loss to fermentation, but it allows the
        interface to remain uniform across all implementations of `calculate_dry_matter_loss_to_gas`.

        """
        dry_matter_fraction = crop.dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION

        is_alfalfa = crop.category is CropCategory.ALFALFA
        constants = ALFALFA_FERMENTATION_CONSTANTS if is_alfalfa else NON_ALFALFA_FERMENTATION_CONSTANTS
        lower_temp_limit = constants["lower_temp_limit"]
        upper_temp_limit = constants["upper_temp_limit"]
        lower_dry_matter_limit = constants["lower_dry_matter_limit"]
        upper_dry_matter_limit = constants["upper_dry_matter_limit"]
        loss_coefficient = constants["loss_coefficient"]
        base_loss_fraction = constants["base_loss_fraction"]

        dry_matter_loss_fraction = 0.0

        for day in weather_conditions:
            outside_temp_range = not lower_temp_limit <= day.mean_air_temperature <= upper_temp_limit
            outside_dry_fraction_range = not lower_dry_matter_limit <= dry_matter_fraction <= upper_dry_matter_limit
            if outside_temp_range or outside_dry_fraction_range:
                continue

            fraction_lost = base_loss_fraction - loss_coefficient * (dry_matter_fraction - lower_dry_matter_limit)
            dry_matter_loss_fraction += fraction_lost
            dry_matter_fraction -= fraction_lost

        self.om.add_variable(
            "debug_dry_matter_loss_fraction", dry_matter_loss_fraction, {
                "class": self.__class__.__name__,
                "function": self.calculate_dry_matter_loss_to_gas.__name__, "units": MeasurementUnits.UNITLESS
            }
        )

        return crop.dry_matter_mass * dry_matter_loss_fraction

    def _get_conditions(
        self, last_degradations_time: date, current_time: RufasTime, weather: Weather
    ) -> list[CurrentDayConditions]:
        """
        Gets the weather conditions for the days between the current time and the time that degradations were last
        processed.

        Parameters
        ----------
        last_degradations_time : date
            The last day a crop's degradations were processed.
        current_time : RufasTime
            RufasTime instance containing the current time of the simulation.
        weather : Weather
            Weather instance containing all weather data for the simulation.

        Notes
        -----
        If the current day is the same as or before the last day that the crop was degraded, no weather conditions will
        be returned.

        """
        time_since_last_degradation = last_degradations_time - current_time.current_date.date()
        starting_day_offset = time_since_last_degradation.days
        if starting_day_offset >= 0:
            return []

        conditions = weather.get_conditions_series(current_time, starting_day_offset + 1, 0)

        return conditions

    def _process_moisture_loss(self, time: RufasTime, loss_period: int, final_moisture_percentage: float) -> None:
        """
        Deducts and records the moisture that has been lost from all crops in storage since the last time degradations
        were processed.

        Parameters
        ----------
        time : RufasTime
            RufasTime instance containing the time that loss should be processed up to.
        loss_period : int
            Number of days over which moisture is lost after crop is stored.
        final_moisture_percentage : float
            Percentage of fresh mass that is moisture in the crop after all moisture loss has occurred.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.process_degradations.__name__,
            "units": MeasurementUnits.KILOGRAMS,
        }
        total_moisture_loss = 0.0
        for crop in self.stored:
            moisture_loss_values = self._calculate_values_after_moisture_loss(
                crop, time, loss_period, final_moisture_percentage
            )
            total_moisture_loss += moisture_loss_values["moisture_loss"]
            crop.fresh_mass = moisture_loss_values["fresh_mass"]
            crop.dry_matter_percentage = moisture_loss_values["dry_matter_percentage"]

        self.om.add_variable("total_moisture_loss", total_moisture_loss, info_map)

    def _project_moisture_loss(
        self, crops: list[HarvestedCrop], time: RufasTime, loss_period: int, final_moisture_percentage: float
    ) -> list[HarvestedCrop]:
        """
        Creates a HarvestedCrop with projected moisture loss accounted for.

        Parameters
        ----------
        crop : list[HarvestedCrop]
            HarvestedCrops to project moisture loss for.
        time : RufasTime
            RufasTime instance containing the time that loss should be processed up to.
        loss_period : int
            Number of days over which moisture is lost after crop is stored.
        final_moisture_percentage : float
            Percentage of fresh mass that is moisture in the crop after all moisture loss has occurred.

        Returns
        -------
        list[HarvestedCrop]
            Crops with the projected moisture loss incorporated into their values.

        """
        projected_crops: list[HarvestedCrop] = []
        for crop in crops:
            moisture_loss_values = self._calculate_values_after_moisture_loss(
                crop, time, loss_period, final_moisture_percentage
            )
            del moisture_loss_values["moisture_loss"]
            projected_crop = replace(crop, **moisture_loss_values)
            projected_crops.append(projected_crop)
        return projected_crops

    def _calculate_values_after_moisture_loss(
        self, crop: HarvestedCrop, time: RufasTime, loss_period: int, final_moisture_percentage: float
    ) -> dict[str, float]:
        """
        Calculates amount of moisture lost from a crop in storage since the last time degradations were processed.

        Parameters
        ----------
        crop : HarvestedCrop
            Crop for which moisture loss will be calculated.
        time : RufasTime
            RufasTime instance containing the time that loss should be calculated up to.
        loss_period : int
            Number of days over which moisture is lost after crop is stored.
        final_moisture_percentage : float
            Percentage of fresh mass that is moisture in the crop after all moisture loss has occurred.

        Returns
        -------
        dict[str, float]
            Mapping of the crop's mass values after moisture loss and the amount of moisture it lost.

        """
        processed_moisture_loss = self._calculate_moisture_loss(
            crop, crop.last_time_degraded, loss_period, final_moisture_percentage
        )
        cumulative_moisture_loss = self._calculate_moisture_loss(
            crop, time.current_date.date(), loss_period, final_moisture_percentage
        )
        actual_moisture_loss = cumulative_moisture_loss - processed_moisture_loss

        mass_after_loss = self._calculate_mass_attributes_after_loss(crop, 0.0, actual_moisture_loss)
        mass_after_loss["moisture_loss"] = actual_moisture_loss
        return mass_after_loss

    def _calculate_moisture_loss(
        self, crop: HarvestedCrop, time: date, loss_period: int, final_moisture_percentage: float
    ) -> float:
        """
        Calculates the moisture lost from a crop since it was stored.

        Parameters
        ----------
        crop : HarvestedCrop
            The  crop to process moisture loss in.
        time : date
            The date that loss should be processed up to.
        loss_period : int
            Number of days over which moisture is lost after crop is stored.
        final_moisture_percentage : float
            Percentage of moisture left in the crop after all moisture loss has occurred.

        Returns
        -------
        float
            Moisture loss from the crop that occurred in the first 30 days of storage (kg).

        References
        ----------
        .. Feed Storage Scientific Documentation, equation. 1.2.9

        """
        days_stored = (time - crop.storage_time).days
        days_in_window = min(days_stored, loss_period)
        fraction_of_total_loss = days_in_window / loss_period

        initial_moisture_percentage = 100.0 - crop.initial_dry_matter_percentage

        initial_fresh_mass = crop.initial_dry_matter_mass / (
            crop.initial_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        )
        percentage_of_fresh_mass_lost_as_moisture = max(0.0, initial_moisture_percentage - final_moisture_percentage)

        moisture_loss = (
            initial_fresh_mass
            * percentage_of_fresh_mass_lost_as_moisture
            * GeneralConstants.PERCENTAGE_TO_FRACTION
            * fraction_of_total_loss
        )

        return moisture_loss

    def recalculate_nutrient_percentage(
        self,
        initial_nutrient_percentage: float,
        loss_coefficient: float,
        dry_matter_loss: float,
        initial_dry_matter: float,
    ) -> float:
        """
        Calculates the updated relative nutrient percentage after dry matter has been lost from a stored crop.

        Parameters
        ----------
        initial_nutrient_percentage : float
            Nutrient percentage in stored crop before loss.
        loss_coefficient : float
            Fractional loss coefficient that regulates how quickly this nutrient is lost.
        dry_matter_loss : float
            Amount of dry matter lost from stored crop in kg.
        initial_dry_matter : float
            Amount of dry matter stored crop contained before loss in kg.

        Returns
        -------
        float
            The nutrient percentage after dry matter loss.

        Notes
        -----
        When stored crops lose dry matter, they do not always lose proportional amounts of the nutrients they are
        composed of. In this case, the concentration of the nutrient within the dry matter changes which is why it must
        be recalculated. If a negative nutrient percentage would be calculated after losing dry matter, the percentage
        is calculated to be 0 and a warning is logged to the OuputManager. If a negative nutrient percentage would have
        been calculated, a warning is logged to the Output Manager that the method is preventing this. If all dry matter
        is lost from the stored crop, the updated percentage of the nutrient in the dry matter is set as 0 to prevent a
        division by zero error.

        """
        dry_matter_loss_fraction = dry_matter_loss / initial_dry_matter
        initial_nutrient_fraction = initial_nutrient_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION

        if dry_matter_loss_fraction == 1.0:
            return 0.0

        fraction_of_nutrient_in_lost_dry_matter = loss_coefficient * dry_matter_loss_fraction
        if initial_nutrient_fraction < fraction_of_nutrient_in_lost_dry_matter:
            info_map = {"class": self.__class__.__name__, "function": self.recalculate_nutrient_percentage.__name__}
            warning_title = (
                f"Nutrient fraction {initial_nutrient_fraction} is less than nutrient fraction in dry matter loss "
                + f"{fraction_of_nutrient_in_lost_dry_matter}"
            )
            warning_message = "Calculating updated percentage of nutrient in stored crop dry matter to be 0"
            self.om.add_warning(warning_title, warning_message, info_map)
            return 0.0

        updated_nutrient_fraction = (initial_nutrient_fraction - fraction_of_nutrient_in_lost_dry_matter) / (
            1 - dry_matter_loss_fraction
        )
        updated_nutrient_percentage = updated_nutrient_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE

        return updated_nutrient_percentage
