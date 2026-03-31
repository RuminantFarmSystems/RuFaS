from RUFAS.biophysical.manure.handler.handler import Handler
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


class SingleStreamHandler(Handler):
    """
    Base class for all handlers that only accept a single manure stream at a time.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.
    handler_type: str
        The manure handler sub-type class into which this handler is categorized.
    cleaning_water_use_amount : float
        Amount of cleaning water used per animal per day (L).
    cleaning_water_recycle_fraction : float
        Fraction of cleaning water that is from recycled (not fresh) water sources (unitless).
    use_parlor_flush : bool
        Indication for if a parlor flush is used in addition to routine parlor water cleaning with fresh water.

    """

    def __init__(
        self,
        name: str,
        processor_type: str,
        cleaning_water_use_amount: float,
        cleaning_water_recycle_fraction: float,
        use_parlor_flush: bool,
    ):
        super().__init__(
            name, processor_type, cleaning_water_use_amount, cleaning_water_recycle_fraction, use_parlor_flush
        )

    def receive_manure(self, manure_stream: ManureStream) -> None:
        """
        Takes in manure to be processed.

        Parameters
        ----------
        manure_stream : ManureStream
            The manure to be processed.

        Raises
        ------
        ValueError
            If the ManureStream is incompatible with the processor receiving it.

        """
        info_map = {"class": self.__class__.__name__, "function": self.receive_manure.__name__}
        super().receive_manure(manure_stream)
        if self.manure_stream is not None:
            self._om.add_error(
                "Multiple stream received.",
                f"Non parlor handler should only receive one manure stream at a time,"
                f" handler {self.name} already received a manure stream.",
                info_map,
            )
            raise ValueError("Non-parlor handler cannot receive multiple streams.")
        self.manure_stream = manure_stream

    def process_manure(self, conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """
        Executes the daily manure processing operations. This method will calculate the gas emissions then call the
        base handler's process manure.

        Parameters
        ----------
        conditions : CurrentDayConditions
            Current weather and environmental conditions that manure is being processed in.
        time : RufasTime
            RufasTime instance containing the simulations temporal information.

        Returns
        -------
        dict[str, ManureStream]
            Mapping between classification of manure coming out of this processor to the ManureStream containing the
            manure information. If the processor is a separator, the classifications are "solid" and "liquid". Otherwise
            the only classification is "manure".

        """
        if self.manure_stream is None or self.manure_stream.pen_manure_data is None:
            info_map = {"class": self.__class__.__name__, "function": self.process_manure.__name__}
            self._om.add_error(
                "None type ManureStream.",
                "The processed ManureStream or pen data of the manure stream is None type.",
                info_map,
            )
            raise TypeError("Handler tries to process 'NoneType' object ManureStream or PenManureData.")
        barn_temperature = self._determine_barn_temperature(conditions.mean_air_temperature)
        surface_area = self.manure_stream.pen_manure_data.manure_deposition_surface_area

        housing_CO2_emissions = self.determine_housing_carbon_dioxide_emissions(surface_area, barn_temperature)
        housing_methane_emissions = self.determine_housing_methane_emissions(surface_area, barn_temperature)

        self._report_gas_emissions(housing_CO2_emissions, housing_methane_emissions, time.simulation_day)

        cleaning_water_volume = self.determine_handler_cleaning_water_volume(
            self.manure_stream.pen_manure_data.num_animals,
            self.cleaning_water_use_amount,
            self.cleaning_water_recycle_fraction,
        )

        ammonia_emission = 0.0
        fresh_water_volume_used_for_milking = 0.0

        if self.handler_type in ["ManualScraper", "AlleyScraper", "FlushSystem"]:
            ammonia_emission = self._calculate_ammonia_emissions(
                self.manure_stream.ammoniacal_nitrogen,
                self.manure_stream.pen_manure_data.manure_urine_mass,
                ManureConstants.SLURRY_MANURE_DENSITY,
                barn_temperature,
                self.determine_ammonia_resistance(barn_temperature),
                surface_area,
                ManureConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
            )

        if self.__class__.__name__ == "ParlorCleaningHandler":
            num_animals = self.manure_stream.pen_manure_data.num_animals
            fresh_water_volume_used_for_milking = self.determine_fresh_water_volume_used_for_milking(num_animals)

        total_cleaning_water_volume = self.determine_total_cleaning_water_volume(
            cleaning_water_volume, fresh_water_volume_used_for_milking
        )

        self._report_processor_output(
            "total_cleaning_water_volume",
            total_cleaning_water_volume,
            self.process_manure.__name__,
            MeasurementUnits.CUBIC_METERS,
            time.simulation_day,
        )
        self._report_processor_output(
            "barn_temperature",
            barn_temperature,
            self.process_manure.__name__,
            MeasurementUnits.DEGREES_CELSIUS,
            time.simulation_day,
        )

        manure_water = self.determine_manure_water(self.manure_stream.water, total_cleaning_water_volume)

        manure_total_ammoniacal_nitrogen = max(0.0, self.manure_stream.ammoniacal_nitrogen - ammonia_emission)
        manure_total_nitrogen = max(0.0, self.manure_stream.nitrogen - ammonia_emission)
        phosphorus = self.manure_stream.phosphorus
        potassium = self.manure_stream.potassium
        ash = self.manure_stream.ash
        volume = self.manure_stream.volume + total_cleaning_water_volume
        degradable_volatile_solids, non_degradable_volatile_solids, total_solids = self._apply_volatile_solid_loss(
            housing_methane_emissions
        )
        methane_production_potential = self.manure_stream.methane_production_potential
        bedding_non_degradable_solid = self.manure_stream.bedding_non_degradable_volatile_solids

        self.manure_stream = None
        self._report_processor_output(
            "housing_ammonia_N_emissions",
            ammonia_emission,
            self.process_manure.__name__,
            MeasurementUnits.KILOGRAMS,
            time.simulation_day,
        )
        output_stream = ManureStream(
            water=manure_water,
            ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            nitrogen=manure_total_nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            ash=ash,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            degradable_volatile_solids=degradable_volatile_solids,
            volume=volume,
            total_solids=total_solids,
            methane_production_potential=methane_production_potential,
            pen_manure_data=None,
            bedding_non_degradable_volatile_solids=bedding_non_degradable_solid,
        )
        self._report_manure_stream(output_stream, "", time.simulation_day)

        return {"manure": output_stream}

    def _report_gas_emissions(
        self, housing_CO2_emissions: float, housing_methane_emissions: float, simulation_day: int
    ) -> None:
        """
        Reports the gas emissions in single stream handler.

        Parameters
        ----------
        housing_CO2_emissions : float
            The amount of housing CO2 emissions (kg).
        housing_methane_emissions : float
            The amount of housing methane emissions (kg).
        simulation_day : int
            The day of simulation.

        Returns
        -------
        None

        """
        self._report_processor_output(
            "housing_CO2_emissions",
            housing_CO2_emissions,
            self.process_manure.__name__,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_processor_output(
            "housing_methane_emissions",
            housing_methane_emissions,
            self.process_manure.__name__,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )

    def _apply_volatile_solid_loss(self, housing_methane_emission: float) -> tuple[float, float, float]:
        """
        Calculates the loss of volatile solids to methane emissions.

        Parameters
        ----------
        housing_methane_emission : float
            The amount of housing emission (kg).

        Returns
        -------
        tuple[float, float, float]
            The updated amount of degradable volatile solids (kg).
            The updated amount of non-degradable volatile solids (kg).
            The updated amount of total solids (kg).

        """
        if self.manure_stream:
            degradable_to_total_manure_volatile_solid_ratio = 0.0
            if self.manure_stream.degradable_volatile_solids + self.manure_stream.non_degradable_volatile_solids != 0.0:
                degradable_to_total_manure_volatile_solid_ratio = self.manure_stream.degradable_volatile_solids / (
                    self.manure_stream.degradable_volatile_solids + self.manure_stream.non_degradable_volatile_solids
                )
            total_volatile_solid_loss = ManureConstants.VS_TO_METHANE_LOSS_RATIO * housing_methane_emission
            degradable_volatile_solid = max(
                0.0,
                self.manure_stream.degradable_volatile_solids
                - (degradable_to_total_manure_volatile_solid_ratio * total_volatile_solid_loss),
            )
            non_degrading_volatile_solid = max(
                0.0,
                self.manure_stream.non_degradable_volatile_solids
                - ((1 - degradable_to_total_manure_volatile_solid_ratio) * total_volatile_solid_loss),
            )
            total_solids = max(0.0, self.manure_stream.total_solids - total_volatile_solid_loss)
            return degradable_volatile_solid, non_degrading_volatile_solid, total_solids
        else:
            return 0.0, 0.0, 0.0

    @staticmethod
    def determine_housing_methane_emissions(manure_deposition_surface_area: float, barn_temperature: float) -> float:
        """
        Calculates the methane housing emission.

        Parameters
        ----------
        manure_deposition_surface_area : float
            The surface area of the manure deposition area in the pen (m^2).
        barn_temperature : float
            Temperature of the barn (Celsius).

        Returns
        -------
        float
            Methane emission from manure (kg).

        """
        return max(0.0, 0.13 * barn_temperature) * manure_deposition_surface_area / 1000

    @staticmethod
    def determine_housing_carbon_dioxide_emissions(
        manure_deposition_surface_area: float, barn_temperature: float
    ) -> float:
        """
        Calculates the housing carbon dioxide housing emission.

        Parameters
        ----------
        manure_deposition_surface_area : float
            The surface area of the manure deposition area in the pen (m^2).
        barn_temperature : float
            Temperature of the barn (Celsius).

        Returns
        -------
        float
            Carbon dioxide emission from manure (kg).

        """
        return max(0.0, 0.0065 + 0.0192 * barn_temperature) * manure_deposition_surface_area
