from dataclasses import dataclass
from enum import Enum
from typing import Optional
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits


class StreamType(Enum):
    """
    Enumeration of the types of manure streams.

    Attributes
    ----------
    PARLOR: str
        Represents manure from the parlor.
    GENERAL: str
        Represents all manure other than what is deposited in or traveling to/from the milking parlor.
    """

    PARLOR = "parlor"
    GENERAL = "general"


@dataclass
class PenManureData:
    """
    Information about the pen or pens in which the manure was produced.

    Attributes
    ----------
    num_animals : int
        The number of animals in this pen that created the manure.
    manure_deposition_surface_area : float
        The surface area of the manure deposition area in the pen (m^2).
    animal_combination : AnimalCombination
        The combination of animals in the pen.
    pen_type : str | None
        The type of pen.
    manure_urine_mass : float
        The overall mass of urine in the manure stream (kg).
    manure_urine_nitrogen : float
        The mass of nitrogen in the urine in the manure stream (kg).
    stream_type : StreamType
        The type of manure stream in the pen.
    first_processor : str
        The name of the first processor to handle the manure stream.
    total_bedding_mass: float
        The total mass of the bedding applied to the manure stream (kg).
    total_bedding_volume: float
        The total volume of the bedding applied to the manure stream (m^3).
    """

    num_animals: int
    manure_deposition_surface_area: float
    animal_combination: AnimalCombination
    pen_type: str | None
    manure_urine_mass: float
    manure_urine_nitrogen: float
    stream_type: StreamType
    first_processor: Optional[str] = None
    total_bedding_mass: Optional[float] = None
    total_bedding_volume: Optional[float] = None

    PEN_MANURE_DATA_UNITS = {
        "num_animals": MeasurementUnits.ANIMALS,
        "manure_deposition_surface_area": MeasurementUnits.SQUARE_METERS,
        "animal_combination": MeasurementUnits.UNITLESS,
        "pen_type": MeasurementUnits.UNITLESS,
        "manure_urine_mass": MeasurementUnits.KILOGRAMS,
        "manure_urine_nitrogen": MeasurementUnits.KILOGRAMS,
        "stream_type": MeasurementUnits.UNITLESS,
        "first_processor": MeasurementUnits.UNITLESS,
        "total_bedding_mass": MeasurementUnits.KILOGRAMS,
        "total_bedding_volume": MeasurementUnits.CUBIC_METERS,
    }

    def __post_init__(self) -> None:
        if self.stream_type == StreamType.PARLOR and self.animal_combination != AnimalCombination.LAC_COW:
            raise ValueError("Manure from a non-lactating pen assigned to parlor manure stream.")

    def set_first_processor(self, processor_name: str) -> None:
        self.first_processor = processor_name

    def set_bedding_mass_and_volume(self, bedding_mass: float, bedding_volume: float) -> None:
        self.total_bedding_mass = bedding_mass
        self.total_bedding_volume = bedding_volume

    def __add__(self, other: "PenManureData") -> "PenManureData":
        """
        Combines two PenManureData instances.

        Parameters
        ----------
        other : PenManureData
            The other PenManureData instance to combine with this one.

        Returns
        -------
        PenManureData
            The combined PenManureData instance.

        Raises
        ------
        ValueError
            If the stream type is ManureStreamType.GENERAL or if the animal combinations do not match.

        """
        if self.stream_type == StreamType.GENERAL or other.stream_type == StreamType.GENERAL:
            raise ValueError("Cannot combine PenManureData instances with a general manure stream type.")
        if self.animal_combination != other.animal_combination:
            raise ValueError("Cannot combine PenManureData instances with different animal combinations.")
        if self.first_processor != other.first_processor:
            raise ValueError("Cannot combine PenManureData instances with different first processors.")

        return PenManureData(
            num_animals=self.num_animals + other.num_animals,
            manure_deposition_surface_area=self.manure_deposition_surface_area + other.manure_deposition_surface_area,
            animal_combination=self.animal_combination,
            pen_type=None,
            manure_urine_mass=self.manure_urine_mass + other.manure_urine_mass,
            manure_urine_nitrogen=self.manure_urine_nitrogen + other.manure_urine_nitrogen,
            stream_type=self.stream_type,
            first_processor=self.first_processor,
            total_bedding_mass=sum(filter(None, [self.total_bedding_mass, other.total_bedding_mass])),
            total_bedding_volume=sum(filter(None, [self.total_bedding_volume, other.total_bedding_volume])),
        )


@dataclass
class ManureStream:
    """
    This class packages manure data for transfer between the Animal and Manure modules,
    as well as for transfer between Manure module processors.

    Attributes
    ----------
    water : float
        Mass of water in the manure stream (kg).
    ammoniacal_nitrogen : float
        Mass of ammoniacal nitrogen in the manure stream (kg).
    nitrogen : float
        Mass of total nitrogen in the manure stream (kg).
    phosphorus: float
        Mass of phosphorus in the manure stream (kg).
    potassium : float
        Mass of potassium in the manure stream (kg).
    ash : float
        Mass of ash in the manure stream (kg).
    non_degradable_volatile_solids : float
        Mass of non-degradable volatile solids in the manure stream (kg).
    degradable_volatile_solids : float
        Mass of degradable volatile solids in the manure stream (kg).
    total_solids : float
        Mass of total solids in the manure stream (kg).
    volume : float
        Volume of the manure stream (m^3).
    methane_production_potential : float
        Achievable emission of methane from dairy manure (m^3 methane / kg volatile solids).
    pen_manure_data : PenManureData | None
       Optional, more specific information about the manure and the pen or pens that produced it.
    bedding_non_degradable_volatile_solids : float
        Amount of bedding non-degradable volatile solids (kg).

    Class Attributes
    ----------------
    MANURE_STREAM_UNITS : dict[str, MeasurementUnits | None]
        A dictionary mapping manure stream attributes and properties to their respective measurement units.

    """

    water: float
    ammoniacal_nitrogen: float
    nitrogen: float
    phosphorus: float
    potassium: float
    ash: float
    degradable_volatile_solids: float
    non_degradable_volatile_solids: float
    bedding_non_degradable_volatile_solids: float
    total_solids: float
    volume: float
    methane_production_potential: float
    pen_manure_data: PenManureData | None

    MANURE_STREAM_UNITS = {
        "water": MeasurementUnits.KILOGRAMS,
        "ammoniacal_nitrogen": MeasurementUnits.KILOGRAMS,
        "nitrogen": MeasurementUnits.KILOGRAMS,
        "phosphorus": MeasurementUnits.KILOGRAMS,
        "potassium": MeasurementUnits.KILOGRAMS,
        "ash": MeasurementUnits.KILOGRAMS,
        "degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
        "non_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
        "bedding_non_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
        "total_solids": MeasurementUnits.KILOGRAMS,
        "volume": MeasurementUnits.CUBIC_METERS,
        "mass": MeasurementUnits.KILOGRAMS,
        "total_volatile_solids": MeasurementUnits.KILOGRAMS,
        "methane_production_potential": MeasurementUnits.CUBIC_METERS_PER_KILOGRAM,
        "pen_manure_data": None,
    }

    def __add__(self, other: "ManureStream") -> "ManureStream":
        """
        Combines two ManureStream instances.

        Parameters
        ----------
        other : ManureStream
            The other ManureStream instance to combine with this one.

        Returns
        -------
        ManureStream
            The combined ManureStream instance.
        """
        total_volatile_solids = self.total_volatile_solids + other.total_volatile_solids
        self_volatile_solids_proportion = (
            self.total_volatile_solids / total_volatile_solids if total_volatile_solids else 0.0
        )
        other_volatile_solids_proportion = (
            other.total_volatile_solids / total_volatile_solids if total_volatile_solids else 0.0
        )
        return ManureStream(
            water=self.water + other.water,
            ammoniacal_nitrogen=self.ammoniacal_nitrogen + other.ammoniacal_nitrogen,
            nitrogen=self.nitrogen + other.nitrogen,
            phosphorus=self.phosphorus + other.phosphorus,
            potassium=self.potassium + other.potassium,
            ash=self.ash + other.ash,
            non_degradable_volatile_solids=self.non_degradable_volatile_solids + other.non_degradable_volatile_solids,
            degradable_volatile_solids=self.degradable_volatile_solids + other.degradable_volatile_solids,
            total_solids=self.total_solids + other.total_solids,
            volume=self.volume + other.volume,
            methane_production_potential=(
                self.methane_production_potential * self_volatile_solids_proportion
                + other.methane_production_potential * other_volatile_solids_proportion
            ),
            pen_manure_data=(
                self.pen_manure_data + other.pen_manure_data if self.pen_manure_data and other.pen_manure_data else None
            ),
            bedding_non_degradable_volatile_solids=self.bedding_non_degradable_volatile_solids
            + other.bedding_non_degradable_volatile_solids,
        )

    @property
    def is_empty(self) -> bool:
        """
        Returns True if all nutrient, solids, and volume values are zero
        and pen_manure_data is None.
        """
        return self.pen_manure_data is None and all(
            value == 0.0
            for value in [
                self.water,
                self.ammoniacal_nitrogen,
                self.nitrogen,
                self.phosphorus,
                self.potassium,
                self.ash,
                self.non_degradable_volatile_solids,
                self.degradable_volatile_solids,
                self.total_solids,
                self.volume,
                self.bedding_non_degradable_volatile_solids,
            ]
        )

    @property
    def total_volatile_solids(self) -> float:
        """Amount of the total volatile solids (kg)."""
        return (
            self.non_degradable_volatile_solids
            + self.degradable_volatile_solids
            + self.bedding_non_degradable_volatile_solids
        )

    @property
    def mass(self) -> float:
        """Mass of the manure stream (kg)."""
        return self.water + self.total_solids

    def clear_pen_manure_data(self) -> None:
        """Clears the pen manure data instance."""
        self.pen_manure_data = None

    @classmethod
    def make_empty_manure_stream(cls) -> "ManureStream":
        """Factory method for making empty ManureStreams."""
        return ManureStream(
            water=0.0,
            ammoniacal_nitrogen=0.0,
            nitrogen=0.0,
            phosphorus=0.0,
            potassium=0.0,
            ash=0.0,
            non_degradable_volatile_solids=0.0,
            degradable_volatile_solids=0.0,
            total_solids=0.0,
            volume=0.0,
            methane_production_potential=0.0,
            pen_manure_data=None,
            bedding_non_degradable_volatile_solids=0.0,
        )

    def split_stream(
        self,
        split_ratio: float,
        stream_type: StreamType | None = None,
        manure_stream_deposition_split: float | None = None,
    ) -> "ManureStream":
        """
        Splits this manure stream using the specified ratio.

        Parameters
        ----------
        split_ratio : float
            Proportion of this stream to split into the new stream.
        stream_type : StreamType | None, default None
            Type to assign to the new manure stream's PenManureData, if applicable.
        manure_stream_deposition_split : float | None, default None
            Proportion of the manure deposition surface area to assign to the new stream's PenManureData,
            if applicable. If None, the split_ratio will be used.

        Returns
        -------
        ManureStream
            A new ManureStream instance representing the split portion.

        Raises
        ------
        ValueErrorcov
            If split_ratio is not between 0 and 1.
        """
        if not (0 < split_ratio <= 1):
            OutputManager().add_error(
                "ManureStream split ratio error",
                f"Invalid split ratio: {split_ratio}. Must be between 0 and 1.",
                info_map={
                    "class": self.__class__.__name__,
                    "function": self.split_stream.__name__,
                },
            )
            raise ValueError("Split ratio must be greater than 0 and less than 1.")

        split_pen_manure_data = None
        if self.pen_manure_data is not None and stream_type is not None:
            split_pen_manure_data = PenManureData(
                num_animals=self.pen_manure_data.num_animals,
                manure_deposition_surface_area=(
                    self.pen_manure_data.manure_deposition_surface_area * manure_stream_deposition_split
                    if manure_stream_deposition_split is not None
                    else self.pen_manure_data.manure_deposition_surface_area * split_ratio
                ),
                animal_combination=self.pen_manure_data.animal_combination,
                pen_type=self.pen_manure_data.pen_type,
                manure_urine_mass=self.pen_manure_data.manure_urine_mass * split_ratio,
                manure_urine_nitrogen=self.pen_manure_data.manure_urine_nitrogen * split_ratio,
                stream_type=stream_type,
            )

        return ManureStream(
            water=self.water * split_ratio,
            ammoniacal_nitrogen=self.ammoniacal_nitrogen * split_ratio,
            nitrogen=self.nitrogen * split_ratio,
            phosphorus=self.phosphorus * split_ratio,
            potassium=self.potassium * split_ratio,
            ash=self.ash * split_ratio,
            non_degradable_volatile_solids=self.non_degradable_volatile_solids * split_ratio,
            degradable_volatile_solids=self.degradable_volatile_solids * split_ratio,
            total_solids=self.total_solids * split_ratio,
            volume=self.volume * split_ratio,
            methane_production_potential=self.methane_production_potential,
            pen_manure_data=split_pen_manure_data,
            bedding_non_degradable_volatile_solids=self.bedding_non_degradable_volatile_solids * split_ratio,
        )
