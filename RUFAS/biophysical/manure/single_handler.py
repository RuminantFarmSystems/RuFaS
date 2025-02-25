from RUFAS.biophysical.manure.handler import Handler, HandlerConfig
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.enums import AnimalCombination
from RUFAS.time import Time


class SingleHandler(Handler):
    def __init__(self, name: str, is_housing_emissions_calculator: bool, config: HandlerConfig):
        super().__init__(name, is_housing_emissions_calculator, config)

    def receive_manure(self, manure_stream: ManureStream) -> None:
        """
        Takes in manure to be processed.

        Parameters
        ----------
        manure : ManureStream
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
            raise ValueError("Handler cannot receive multiple streams.")
        self.manure_stream = manure_stream

    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        barn_temperature = self.determine_barn_temperature(conditions.mean_air_temperature)
        surface_area = self.determine_barn_area(
            self.manure_stream.pen_manure_data.animal_combination,
            self.manure_stream.pen_manure_data.pen_type,
            self.manure_stream.pen_manure_data.num_stalls,
        )
        self.ammonia_emission = self._calculate_ammonia_emissions(
            self.manure_stream.ammoniacal_nitrogen,
            self.manure_stream.volume,
            990.0,
            barn_temperature,
            self.determine_ammonia_resistance(barn_temperature),
            surface_area,
            7.7,
        )
        return super().process_manure(conditions, time)

    @classmethod
    def determine_methane_emissions(
        cls, animal_combination: AnimalCombination, pen_type: str, num_stalls: int, barn_temperature: float
    ) -> float:
        """
        Calculates the methane housing emission.

        Parameters
        ----------
        animal_combination : AnimalCombination
        pen_type : str
        num_stalls : int
        barn_temperature : float

        Returns
        -------
        float
            Methane emission from manure (kg).

        """
        barn_area = cls.determine_barn_area(animal_combination, pen_type, num_stalls)

        return max(0.0, 0.13 * barn_temperature) * barn_area / 1000

    @classmethod
    def determine_carbon_dioxide_emissions(
        cls, animal_combination: AnimalCombination, pen_type: str, num_stalls: int, barn_temperature: float
    ) -> float:
        """
        Calculates the carbon dioxide housing emission.

        Parameters
        ----------
        animal_combination : AnimalCombination
        pen_type : str
        num_stalls : int
        barn_temperature : float

        Returns
        -------
        float
            Carbon dioxide emission from manure (kg).

        """
        barn_area = cls.determine_barn_area(animal_combination, pen_type, num_stalls)
        return max(0.0, 0.0065 + 0.0192 * barn_temperature) * barn_area / 1000

    @staticmethod
    def determine_ammonia_resistance(temp: float, hsc: float = 260) -> float:
        """
        Calculate resistance of ammonia transport to the atmosphere in a barn.

        Parameters
        ----------
        temp : float
            Temperature in Celsius (C).
        hsc : float, optional, default = 260
            Housing specific constant (s/m).

        Returns
        -------
        float
            Resistance of ammonia transport to the atmosphere in a barn (s/m).

        """
        return hsc * (1 - 0.027 * (20.0 - max(temp, -15.0)))
