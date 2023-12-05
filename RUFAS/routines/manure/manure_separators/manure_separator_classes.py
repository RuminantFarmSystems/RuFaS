from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Type

from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import (
    ManureSeparatorDailyOutput,
)
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


class ManureSeparatorType(DefaultEnum):
    """Enumerates the different types of manure separators."""

    ROTARY_SCREEN = "rotary screen"
    SCREW_PRESS = "screw press"
    BELT_PRESS = "belt press"
    DECANTING_CENTRIFUGE = "decanting centrifuge"
    MOVING_DISC_PRESS = "moving disc press"
    SLOPE_SCREEN = "slope screen"

    MECHANICAL_SAND_SEPARATOR = "mechanical sand separator"
    SAND_LANE_MANURE_SEPARATION = "sand lane manure separation"

    DEFAULT_ORGANIC = ROTARY_SCREEN
    DEFAULT_SAND = SAND_LANE_MANURE_SEPARATION

    @classmethod
    def get_default_type(cls, bedding_type="ORGANIC") -> DefaultEnum:
        """Returns the default manure separator type for the given bedding type."""
        if bedding_type == "ORGANIC":
            return cls.DEFAULT_ORGANIC
        return cls.DEFAULT_SAND


class BaseManureSeparator:
    """Base class for all manure separators.

    Attributes:
        config: ManureSeparatorConfig object containing the configuration for the manure separator.

    """

    def __init__(self, manure_separator_config: ManureSeparatorConfig) -> None:
        """Initializes the manure separator.

        Args:
            manure_separator_config: ManureSeparatorConfig object containing the
                configuration for the manure separator.

        """
        self.config = manure_separator_config

    def daily_update(
        self, manure_separator_daily_input: LiquidManurePortionProtocol
    ) -> ManureSeparatorDailyOutput:
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
            liquid_manure_nitrogen=(
                manure_separator_daily_input.liquid_manure_nitrogen
                * (1 - self.config.nitrogen_removal_efficiency_for_separator)
            ),
            liquid_manure_total_ammoniacal_nitrogen=(
                manure_separator_daily_input.liquid_manure_total_ammoniacal_nitrogen
                * (
                    1
                    - self.config.total_ammoniacal_nitrogen_removal_efficiency_for_separator
                )
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

    Attributes:
        percent_dry_solids: Percent dry content in manure solids.
        total_solids_removal_efficiency_for_separator: Percent of total solids removed from manure.
        volatile_solids_removal_efficiency_for_separator: Percent of volatile solids removed from manure.
        nitrogen_removal_efficiency_for_separator: Percent of nitrogen removed from manure.
        total_ammoniacal_nitrogen_removal_efficiency_for_separator: Percent of total ammonia nitrogen removed from
        manure.
        phosphorus_removal_efficiency_for_separator: Percent of phosphorus removed from manure.
        potassium_removal_efficiency_for_separator: Percent of potassium removed from manure.

    """

    percent_dry_solids: float = 1.0
    total_solids_removal_efficiency_for_separator: float = 0.0
    volatile_solids_removal_efficiency_for_separator: float = 0.0
    nitrogen_removal_efficiency_for_separator: float = 0.0
    total_ammoniacal_nitrogen_removal_efficiency_for_separator: float = 0.0
    phosphorus_removal_efficiency_for_separator: float = 0.0
    potassium_removal_efficiency_for_separator: float = 0.0


class DefaultManureSeparatorConfigFactory:
    """Class for creating default manure separator configuration data."""

    ROTARY_SCREEN_CONFIG = ManureSeparatorConfig(
        percent_dry_solids=0.2,
        total_solids_removal_efficiency_for_separator=0.35,
        volatile_solids_removal_efficiency_for_separator=0.40,
        nitrogen_removal_efficiency_for_separator=0.3,
        total_ammoniacal_nitrogen_removal_efficiency_for_separator=0.15,
        phosphorus_removal_efficiency_for_separator=0.4,
        potassium_removal_efficiency_for_separator=0.15,
    )
    SCREW_PRESS_CONFIG = ManureSeparatorConfig(
        percent_dry_solids=0.35,
        total_solids_removal_efficiency_for_separator=0.25,
        volatile_solids_removal_efficiency_for_separator=0.30,
        nitrogen_removal_efficiency_for_separator=0.3,
        total_ammoniacal_nitrogen_removal_efficiency_for_separator=0.10,
        phosphorus_removal_efficiency_for_separator=0.2,
        potassium_removal_efficiency_for_separator=0.23,
    )

    @classmethod
    def get_instance(
        cls, manure_separator_type: ManureSeparatorType
    ) -> ManureSeparatorConfig:
        """Return a default manure separator configuration data instance for the given separator type.

        Args:
            manure_separator_type: The type of manure separator.

        Returns:
            A default ManureSeparatorConfig object for the given manure separator type.

        """

        manure_separator_config_by_type: Dict[
            ManureSeparatorType, ManureSeparatorConfig
        ] = {
            ManureSeparatorType.ROTARY_SCREEN: cls.ROTARY_SCREEN_CONFIG,
            ManureSeparatorType.SCREW_PRESS: cls.SCREW_PRESS_CONFIG,
        }
        return manure_separator_config_by_type.get(
            manure_separator_type, ManureSeparatorConfig()
        )


class ManureSeparatorFactory:
    """A class that contains the logic for creating different types of manure separators."""

    @classmethod
    def get_instance(
        cls,
        manure_separator_type_name: str,
        custom_manure_separator_config: Optional[ManureSeparatorConfig] = None,
    ) -> BaseManureSeparator:
        """Return an instance of a specific subtype of BaseManureSeparator.

        Args:
            manure_separator_type_name: The name of the manure separator type.
            custom_manure_separator_config: A ManureSeparatorConfig object for
                a custom manure separator.

        Returns:
            An instance of a specific subtype of BaseManureSeparator.

        """
        manure_separator_class_by_type: Dict[
            ManureSeparatorType, Type[BaseManureSeparator]
        ] = {
            ManureSeparatorType.BELT_PRESS: BeltPress,
            ManureSeparatorType.DECANTING_CENTRIFUGE: DecantingCentrifuge,
            ManureSeparatorType.MOVING_DISC_PRESS: MovingDiscPress,
            ManureSeparatorType.ROTARY_SCREEN: RotaryScreen,
            ManureSeparatorType.SCREW_PRESS: ScrewPress,
            ManureSeparatorType.SLOPE_SCREEN: SlopeScreen,
            ManureSeparatorType.MECHANICAL_SAND_SEPARATOR: MechanicalSandSeparator,
            ManureSeparatorType.SAND_LANE_MANURE_SEPARATION: SandLaneSystem,
        }

        manure_separator_type = ManureSeparatorType.get_type(manure_separator_type_name)
        manure_separator_class = manure_separator_class_by_type[manure_separator_type]

        if custom_manure_separator_config:
            return manure_separator_class(custom_manure_separator_config)
        else:
            default_manure_separator_config = (
                DefaultManureSeparatorConfigFactory.get_instance(manure_separator_type)
            )
            return manure_separator_class(default_manure_separator_config)
