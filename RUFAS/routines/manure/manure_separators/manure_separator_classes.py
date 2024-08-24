from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict
from typing import Type

from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import (
    ManureSeparatorDailyOutput,
)
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


class ManureSeparatorType(Enum):
    """Enumerates the different types of manure separators.

    Attributes
    ----------
    ROTARY_SCREEN : str
        The rotary screen method of manure separation.
    SCREW_PRESS : str
        The screw press method of manure separation.
    BELT_PRESS : str
        The belt press method of manure separation.
    DECANTING_CENTRIFUGE : str
        The decanting centrifuge method of manure separation.
    MOVING_DISC_PRESS : str
        The moving disc press method of manure separation.
    SLOPE_SCREEN : str
        The slope screen method of manure separation.
    MECHANICAL_SAND_SEPARATOR : str
        The mechanical sand separator method of sand-manure separation.
    SAND_LANE_MANURE_SEPARATION : str
        The sand lane method of sand-manure separation.

    """

    ROTARY_SCREEN = "rotary screen"
    SCREW_PRESS = "screw press"
    BELT_PRESS = "belt press"
    DECANTING_CENTRIFUGE = "decanting centrifuge"
    MOVING_DISC_PRESS = "moving disc press"
    SLOPE_SCREEN = "slope screen"
    MECHANICAL_SAND_SEPARATOR = "mechanical sand separator"
    SAND_LANE_MANURE_SEPARATION = "sand lane manure separation"


class BaseManureSeparator:
    """Base class for all manure separators.

    Attributes
    ----------
    name : str
        The unique name for the separator configuration used in this separator.
    config : ManureSeparatorConfig
        The configuration for the manure separator.

    """

    def __init__(self, name: str, manure_separator_config: ManureSeparatorConfig) -> None:
        self.name = name
        self.config = manure_separator_config

    def daily_update(self, manure_separator_daily_input: LiquidManurePortionProtocol) -> ManureSeparatorDailyOutput:
        """Calculates the daily output of the manure separator.

        Notes:
            "pseudocode_manure_management" MS.4

        Args:
            manure_separator_daily_input: A daily output object that can come from a reception pit
            or an anaerobic digester.

        Returns:
            ManureSeparatorDailyOutput object containing the daily output of the manure separator.

        """
        daily_output = ManureSeparatorDailyOutput(
            simulation_day=manure_separator_daily_input.simulation_day,
            pen_id=manure_separator_daily_input.pen_id,
            total_daily_manure_volume=manure_separator_daily_input.liquid_manure_daily_volume,
            final_solids_wet_mass=(
                manure_separator_daily_input.liquid_manure_total_solids
                * self.config.total_solids_removal_efficiency_for_separator
                / self.config.percent_dry_solids
            ),
            solid_manure_total_solids=(
                manure_separator_daily_input.liquid_manure_total_solids
                * self.config.total_solids_removal_efficiency_for_separator
            ),
            solid_manure_total_volatile_solids=(
                manure_separator_daily_input.liquid_manure_total_volatile_solids
                * self.config.volatile_solids_removal_efficiency_for_separator
            ),
            solid_manure_nitrogen=(
                manure_separator_daily_input.liquid_manure_nitrogen
                * self.config.nitrogen_removal_efficiency_for_separator
            ),
            solid_manure_phosphorus=(
                manure_separator_daily_input.liquid_manure_phosphorus
                * self.config.phosphorus_removal_efficiency_for_separator
            ),
            solid_manure_potassium=(
                manure_separator_daily_input.liquid_manure_potassium
                * self.config.potassium_removal_efficiency_for_separator
            ),
            liquid_manure_total_solids=(
                manure_separator_daily_input.liquid_manure_total_solids
                * (1 - self.config.total_solids_removal_efficiency_for_separator)
            ),
            liquid_manure_total_volatile_solids=(
                manure_separator_daily_input.liquid_manure_total_volatile_solids
                * (1 - self.config.volatile_solids_removal_efficiency_for_separator)
            ),
            liquid_manure_total_degradable_volatile_solids=(
                manure_separator_daily_input.liquid_manure_total_degradable_volatile_solids
                * (1 - self.config.volatile_solids_removal_efficiency_for_separator)
            ),
            liquid_manure_total_non_degradable_volatile_solids=(
                manure_separator_daily_input.liquid_manure_total_non_degradable_volatile_solids
                * (1 - self.config.volatile_solids_removal_efficiency_for_separator)
            ),
            liquid_manure_nitrogen=(
                manure_separator_daily_input.liquid_manure_nitrogen
                * (1 - self.config.nitrogen_removal_efficiency_for_separator)
            ),
            liquid_manure_total_ammoniacal_nitrogen=(
                manure_separator_daily_input.liquid_manure_total_ammoniacal_nitrogen
                * (1 - self.config.total_ammoniacal_nitrogen_removal_efficiency_for_separator)
            ),
            liquid_manure_phosphorus=(
                manure_separator_daily_input.liquid_manure_phosphorus
                * (1 - self.config.phosphorus_removal_efficiency_for_separator)
            ),
            liquid_manure_potassium=(
                manure_separator_daily_input.liquid_manure_potassium
                * (1 - self.config.potassium_removal_efficiency_for_separator)
            ),
        )
        return daily_output


class BeltPress(BaseManureSeparator):
    """Class for a belt press manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class DecantingCentrifuge(BaseManureSeparator):
    """Class for a decanting centrifuge manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class MechanicalSeparator(BaseManureSeparator):
    """Class for a mechanical separator manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class MovingDiscPress(BaseManureSeparator):
    """Class for a moving disc press manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class RotaryScreen(BaseManureSeparator):
    """Class for a rotary screen manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class ScrewPress(BaseManureSeparator):
    """Class for a screw press manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class Sedimentation(BaseManureSeparator):
    """Class for a sedimentation manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class SlopeScreen(BaseManureSeparator):
    """Class for a slope screen manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class SandLaneSystem(BaseManureSeparator):
    """Class for a sand lane system manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


class MechanicalSandSeparator(BaseManureSeparator):
    """Class for a mechanical sand separator manure separator.

    Attributes:
        All inherited from BaseManureSeparator.

    """

    pass


@dataclass
class ManureSeparatorConfig:
    """Class for storing manure separator configuration data.

    Attributes
    ----------
    manure_separator_type : ManureSeparatorType
        The type of manure separator that will be created with this configuration.
    percent_dry_solids : float, default 1.0
        Percent dry content in manure solids.
    total_solids_removal_efficiency_for_separator : float, default 0.0
        Percent of total solids removed from manure.
    volatile_solids_removal_efficiency_for_separator : float, default 0.0
        Percent of volatile solids removed from manure.
    nitrogen_removal_efficiency_for_separator : float, default 0.0
        Percent of nitrogen removed from manure.
    total_ammoniacal_nitrogen_removal_efficiency_for_separator : float, default 0.0
        Percent of total ammonia nitrogen removed from manure.
    phosphorus_removal_efficiency_for_separator : float, default 0.0
        Percent of phosphorus removed from manure.
    potassium_removal_efficiency_for_separator : float, default 0.0
        Percent of potassium removed from manure.

    """

    manure_separator_type: ManureSeparatorType
    percent_dry_solids: float = 1.0
    total_solids_removal_efficiency_for_separator: float = 0.0
    volatile_solids_removal_efficiency_for_separator: float = 0.0
    nitrogen_removal_efficiency_for_separator: float = 0.0
    total_ammoniacal_nitrogen_removal_efficiency_for_separator: float = 0.0
    phosphorus_removal_efficiency_for_separator: float = 0.0
    potassium_removal_efficiency_for_separator: float = 0.0


class ManureSeparatorFactory:
    """A class that contains the logic for creating different types of manure separators."""

    @classmethod
    def get_instance(
        cls,
        configuration_name: str,
        manure_separator_config: ManureSeparatorConfig,
    ) -> BaseManureSeparator:
        """Return an instance of a specific subtype of BaseManureSeparator.

        Parameters
        ----------
        configuration_name : str
            The name of the manure separator type.
        manure_separator_config : ManureSeparatorConfig
            A manure separator config to be used to manufacture the separator.

        Returns
        -------
        BaseManureSeparator
            An instance of a specific subtype of BaseManureSeparator.

        """
        manure_separator_class_by_type: Dict[ManureSeparatorType, Type[BaseManureSeparator]] = {
            ManureSeparatorType.BELT_PRESS: BeltPress,
            ManureSeparatorType.DECANTING_CENTRIFUGE: DecantingCentrifuge,
            ManureSeparatorType.MOVING_DISC_PRESS: MovingDiscPress,
            ManureSeparatorType.ROTARY_SCREEN: RotaryScreen,
            ManureSeparatorType.SCREW_PRESS: ScrewPress,
            ManureSeparatorType.SLOPE_SCREEN: SlopeScreen,
            ManureSeparatorType.MECHANICAL_SAND_SEPARATOR: MechanicalSandSeparator,
            ManureSeparatorType.SAND_LANE_MANURE_SEPARATION: SandLaneSystem,
        }

        manure_separator_class = manure_separator_class_by_type[manure_separator_config.manure_separator_type]

        return manure_separator_class(configuration_name, manure_separator_config)
