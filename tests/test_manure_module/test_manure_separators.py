from typing import Type

import pytest
from pytest import approx
from pytest import fixture
from pytest_mock import MockFixture

from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure.manure_separators.manure_separator_classes import BeltPress
from RUFAS.routines.manure.manure_separators.manure_separator_classes import DecantingCentrifuge
from RUFAS.routines.manure.manure_separators.manure_separator_classes import DefaultManureSeparatorConfigFactory
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorConfig
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorFactory
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorType
from RUFAS.routines.manure.manure_separators.manure_separator_classes import MechanicalSandSeparator
from RUFAS.routines.manure.manure_separators.manure_separator_classes import MovingDiscPress
from RUFAS.routines.manure.manure_separators.manure_separator_classes import RotaryScreen
from RUFAS.routines.manure.manure_separators.manure_separator_classes import SandLaneSystem
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ScrewPress
from RUFAS.routines.manure.manure_separators.manure_separator_classes import SlopeScreen
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput


# Test ManureSeparatorDailyOutput
# ===============================

def test_manure_separator_daily_output() -> None:
    """Unit test for class ManureSeparatorDailyOutput in file manure_separator_classes.py."""
    # All cases
    # Arrange
    pen_id = 1
    sim_day = 1

    TS_solid = 1.0
    VS_solid = 2.0
    N_solid = 3.0
    P_solid = 4.0
    K_solid = 5.0

    TS = 6.0
    VS_total = 7.0
    N = 8.0
    TAN = 9.0
    P = 10.0
    K = 11.0

    total_daily_manure_volume = 12.0
    final_solids_wet_mass = 13.0
    expected_final_solids_wet_mass_volume = final_solids_wet_mass / ManureConstants.MANURE_SOLIDS_BEDDING_DENSITY
    expected_final_daily_volume = total_daily_manure_volume - expected_final_solids_wet_mass_volume

    def assert_manure_separator_daily_output(output: ManureSeparatorDailyOutput) -> None:
        assert output.pen_id == pen_id
        assert output.simulation_day == sim_day
        assert output.solid_manure_total_solids == TS_solid
        assert output.solid_manure_total_volatile_solids == VS_solid
        assert output.solid_manure_nitrogen == N_solid
        assert output.solid_manure_phosphorus == P_solid
        assert output.solid_manure_potassium == K_solid
        assert output.liquid_manure_total_solids == TS
        assert output.liquid_manure_total_volatile_solids == VS_total
        assert output.liquid_manure_nitrogen == N
        assert output.liquid_manure_total_ammoniacal_nitrogen == TAN
        assert output.liquid_manure_phosphorus == P
        assert output.liquid_manure_potassium == K
        assert output.total_daily_manure_volume == total_daily_manure_volume
        assert output.final_solids_wet_mass == final_solids_wet_mass
        assert output.final_solids_wet_mass_volume == approx(expected_final_solids_wet_mass_volume)
        assert output.final_daily_volume == approx(expected_final_daily_volume)
        assert output.liquid_manure_daily_volume == approx(expected_final_daily_volume)

    # --------------------

    # Case 1: Pass in all arguments to the initializer

    # Act
    manure_separator_daily_output = ManureSeparatorDailyOutput(
            pen_id=pen_id,
            simulation_day=sim_day,
            solid_manure_total_solids=TS_solid,
            solid_manure_total_volatile_solids=VS_solid,
            solid_manure_nitrogen=N_solid,
            solid_manure_phosphorus=P_solid,
            solid_manure_potassium=K_solid,
            liquid_manure_total_solids=TS,
            liquid_manure_total_volatile_solids=VS_total,
            liquid_manure_nitrogen=N,
            liquid_manure_total_ammoniacal_nitrogen=TAN,
            liquid_manure_phosphorus=P,
            liquid_manure_potassium=K,
            total_daily_manure_volume=total_daily_manure_volume,
            final_solids_wet_mass=final_solids_wet_mass
    )

    # Assert
    assert_manure_separator_daily_output(manure_separator_daily_output)

    # --------------------

    # Case 2: Pass in a dictionary to the initializer
    # Arrange
    data = {
        "pen_id": pen_id,
        "simulation_day": sim_day,
        "solid_manure_total_solids": TS_solid,
        "solid_manure_total_volatile_solids": VS_solid,
        "solid_manure_nitrogen": N_solid,
        "solid_manure_phosphorus": P_solid,
        "solid_manure_potassium": K_solid,
        "liquid_manure_total_solids": TS,
        "liquid_manure_total_volatile_solids": VS_total,
        "liquid_manure_nitrogen": N,
        "liquid_manure_total_ammoniacal_nitrogen": TAN,
        "liquid_manure_phosphorus": P,
        "liquid_manure_potassium": K,
        "total_daily_manure_volume": total_daily_manure_volume,
        "final_solids_wet_mass": final_solids_wet_mass
    }

    # Act
    manure_separator_daily_output = ManureSeparatorDailyOutput(**data)

    # Assert
    assert_manure_separator_daily_output(manure_separator_daily_output)


# Test ManureSeparatorConfig
# ==========================

def test_manure_separator_config() -> None:
    """Unit test for class ManureSeparatorConfig in file manure_separator_classes.py."""
    # Case 1: Pass in all arguments to the initializer
    # Arrange
    percent_dry_solids = 1.0
    TS_removal_efficiency_for_separator = 2.0
    VS_removal_efficiency_for_separator = 3.0
    N_removal_efficiency_for_separator = 4.0
    TAN_removal_efficiency_for_separator = 5.0
    P_removal_efficiency_for_separator = 6.0
    K_removal_efficiency_for_separator = 7.0

    # Act
    manure_separator_config = ManureSeparatorConfig(
            percent_dry_solids=percent_dry_solids,
            total_solids_removal_efficiency_for_separator=TS_removal_efficiency_for_separator,
            volatile_solids_removal_efficiency_for_separator=VS_removal_efficiency_for_separator,
            nitrogen_removal_efficiency_for_separator=N_removal_efficiency_for_separator,
            total_ammoniacal_nitrogen_removal_efficiency_for_separator=TAN_removal_efficiency_for_separator,
            phosphorus_removal_efficiency_for_separator=P_removal_efficiency_for_separator,
            potassium_removal_efficiency_for_separator=K_removal_efficiency_for_separator
    )

    # Assert
    assert manure_separator_config.percent_dry_solids == percent_dry_solids
    assert manure_separator_config.total_solids_removal_efficiency_for_separator == TS_removal_efficiency_for_separator
    assert manure_separator_config.volatile_solids_removal_efficiency_for_separator == \
           VS_removal_efficiency_for_separator
    assert manure_separator_config.nitrogen_removal_efficiency_for_separator == N_removal_efficiency_for_separator
    assert manure_separator_config.total_ammoniacal_nitrogen_removal_efficiency_for_separator == \
           TAN_removal_efficiency_for_separator
    assert manure_separator_config.phosphorus_removal_efficiency_for_separator == P_removal_efficiency_for_separator
    assert manure_separator_config.potassium_removal_efficiency_for_separator == K_removal_efficiency_for_separator

    # --------------------

    # Case 2: Pass in a dictionary to the initializer
    # Arrange
    data = {
        "percent_dry_solids": percent_dry_solids,
        "total_solids_removal_efficiency_for_separator": TS_removal_efficiency_for_separator,
        "volatile_solids_removal_efficiency_for_separator": VS_removal_efficiency_for_separator,
        "nitrogen_removal_efficiency_for_separator": N_removal_efficiency_for_separator,
        "total_ammoniacal_nitrogen_removal_efficiency_for_separator": TAN_removal_efficiency_for_separator,
        "phosphorus_removal_efficiency_for_separator": P_removal_efficiency_for_separator,
        "potassium_removal_efficiency_for_separator": K_removal_efficiency_for_separator
    }

    # Act
    manure_separator_config = ManureSeparatorConfig(**data)

    # Assert
    assert manure_separator_config.percent_dry_solids == percent_dry_solids
    assert manure_separator_config.total_solids_removal_efficiency_for_separator == \
           TS_removal_efficiency_for_separator
    assert manure_separator_config.volatile_solids_removal_efficiency_for_separator == \
           VS_removal_efficiency_for_separator
    assert manure_separator_config.nitrogen_removal_efficiency_for_separator == N_removal_efficiency_for_separator
    assert manure_separator_config.total_ammoniacal_nitrogen_removal_efficiency_for_separator == \
           TAN_removal_efficiency_for_separator
    assert manure_separator_config.phosphorus_removal_efficiency_for_separator == P_removal_efficiency_for_separator
    assert manure_separator_config.potassium_removal_efficiency_for_separator == K_removal_efficiency_for_separator

    # --------------------

    # Case 3: Use default values
    # Act
    manure_separator_config = ManureSeparatorConfig()

    # Assert
    assert manure_separator_config.percent_dry_solids == 1.0
    assert manure_separator_config.total_solids_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.volatile_solids_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.nitrogen_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.total_ammoniacal_nitrogen_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.phosphorus_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.potassium_removal_efficiency_for_separator == 0.0


# Test ManureSeparatorType
# ========================

@pytest.mark.parametrize(
        'manure_separator_type_name, expected_manure_separator_type',
        [
            ('rotary screen', ManureSeparatorType.ROTARY_SCREEN),
            ('rotary_screen', ManureSeparatorType.ROTARY_SCREEN),
            ('screw press', ManureSeparatorType.SCREW_PRESS),
            ('screw_press', ManureSeparatorType.SCREW_PRESS),
            ('belt press', ManureSeparatorType.BELT_PRESS),
            ('belt_press', ManureSeparatorType.BELT_PRESS),
            ('decanting centrifuge', ManureSeparatorType.DECANTING_CENTRIFUGE),
            ('decanting_centrifuge', ManureSeparatorType.DECANTING_CENTRIFUGE),
            ('moving disc press', ManureSeparatorType.MOVING_DISC_PRESS),
            ('moving_disc_press', ManureSeparatorType.MOVING_DISC_PRESS),
            ('slope screen', ManureSeparatorType.SLOPE_SCREEN),
            ('slope_screen', ManureSeparatorType.SLOPE_SCREEN),
            ('mechanical sand separator', ManureSeparatorType.MECHANICAL_SAND_SEPARATOR),
            ('mechanical_sand_separator', ManureSeparatorType.MECHANICAL_SAND_SEPARATOR),
            ('sand lane manure separation', ManureSeparatorType.SAND_LANE_MANURE_SEPARATION),
            ('sand_lane_manure_separation', ManureSeparatorType.SAND_LANE_MANURE_SEPARATION),
            ('dummy', ManureSeparatorType.ROTARY_SCREEN),
        ]
)
def test_manure_separator_type(manure_separator_type_name: str,
                               expected_manure_separator_type: ManureSeparatorType
                               ) -> None:
    """Unit test for class ManureSeparatorType in file manure_separator_classes.py."""
    # Assert
    assert ManureSeparatorType.get_type(manure_separator_type_name) == expected_manure_separator_type


# Test ManureSeparatorFactory
# ===========================

@fixture
def mock_manure_separator_config() -> ManureSeparatorConfig:
    """Mocks a ManureSeparatorConfig object."""
    return ManureSeparatorConfig()


@pytest.mark.parametrize(
        'manure_separator_type_name, manure_separator_type,'
        'custom_manure_separator_config,'
        'expected_manure_separator_class, expected_manure_separator_config',
        [
            ('rotary screen', ManureSeparatorType.ROTARY_SCREEN,
             None, RotaryScreen, DefaultManureSeparatorConfigFactory.ROTARY_SCREEN_CONFIG),
            ('rotary screen', ManureSeparatorType.ROTARY_SCREEN,
             mock_manure_separator_config, RotaryScreen, mock_manure_separator_config),
            ('screw press', ManureSeparatorType.SCREW_PRESS,
             None, ScrewPress, DefaultManureSeparatorConfigFactory.SCREW_PRESS_CONFIG),
            ('screw press', ManureSeparatorType.SCREW_PRESS,
             mock_manure_separator_config, ScrewPress, mock_manure_separator_config),
            ('belt press', ManureSeparatorType.BELT_PRESS,
             None, BeltPress, DefaultManureSeparatorConfigFactory.ROTARY_SCREEN_CONFIG),
            ('belt press', ManureSeparatorType.BELT_PRESS,
             mock_manure_separator_config, BeltPress, mock_manure_separator_config),
            ('decanting centrifuge', ManureSeparatorType.DECANTING_CENTRIFUGE,
             None, DecantingCentrifuge, DefaultManureSeparatorConfigFactory.ROTARY_SCREEN_CONFIG),
            ('decanting centrifuge', ManureSeparatorType.DECANTING_CENTRIFUGE,
             mock_manure_separator_config, DecantingCentrifuge, mock_manure_separator_config),
            ('moving disc press', ManureSeparatorType.MOVING_DISC_PRESS,
             None, MovingDiscPress, DefaultManureSeparatorConfigFactory.ROTARY_SCREEN_CONFIG),
            ('moving disc press', ManureSeparatorType.MOVING_DISC_PRESS,
             mock_manure_separator_config, MovingDiscPress, mock_manure_separator_config),
            ('slope screen', ManureSeparatorType.SLOPE_SCREEN,
             None, SlopeScreen, DefaultManureSeparatorConfigFactory.ROTARY_SCREEN_CONFIG),
            ('slope screen', ManureSeparatorType.SLOPE_SCREEN,
             mock_manure_separator_config, SlopeScreen, mock_manure_separator_config),
            ('mechanical sand separator', ManureSeparatorType.MECHANICAL_SAND_SEPARATOR,
             None, MechanicalSandSeparator, DefaultManureSeparatorConfigFactory.ROTARY_SCREEN_CONFIG),
            ('mechanical sand separator', ManureSeparatorType.MECHANICAL_SAND_SEPARATOR,
             mock_manure_separator_config, MechanicalSandSeparator, mock_manure_separator_config),
            ('sand lane manure separation', ManureSeparatorType.SAND_LANE_MANURE_SEPARATION,
             None, SandLaneSystem, DefaultManureSeparatorConfigFactory.ROTARY_SCREEN_CONFIG),
            ('sand lane manure separation', ManureSeparatorType.SAND_LANE_MANURE_SEPARATION,
             mock_manure_separator_config, SandLaneSystem, mock_manure_separator_config),
            ('dummy', ManureSeparatorType.ROTARY_SCREEN,
             None, RotaryScreen, DefaultManureSeparatorConfigFactory.ROTARY_SCREEN_CONFIG),
            ('dummy', ManureSeparatorType.ROTARY_SCREEN,
             mock_manure_separator_config, RotaryScreen, mock_manure_separator_config),
        ]
)
def test_manure_separator_factory_get_instance(manure_separator_type_name: str,
                                               manure_separator_type: ManureSeparatorType,
                                               custom_manure_separator_config: ManureSeparatorConfig,
                                               expected_manure_separator_class: Type[BaseManureSeparator],
                                               expected_manure_separator_config: ManureSeparatorConfig,
                                               mocker: MockFixture,
                                               ) -> None:
    """Unit test for class ManureSeparatorFactory in file manure_separator_classes.py."""
    # Arrange
    patch_for_manure_separator_get_type = mocker.patch(
            'RUFAS.routines.manure.manure_separators.manure_separator_classes.ManureSeparatorType.get_type',
            return_value=manure_separator_type
    )
    patch_for_default_manure_separator_config_factory_get_instance = mocker.patch(
            'RUFAS.routines.manure.manure_separators.manure_separator_classes.DefaultManureSeparatorConfigFactory'
            '.get_instance',
            return_value=expected_manure_separator_config
    )

    # Act
    manure_separator = ManureSeparatorFactory.get_instance(manure_separator_type_name,
                                                           custom_manure_separator_config)

    # Assert
    patch_for_manure_separator_get_type.assert_called_once_with(manure_separator_type_name)
    assert type(manure_separator) == expected_manure_separator_class
    assert manure_separator.config == expected_manure_separator_config
    if not custom_manure_separator_config:
        patch_for_default_manure_separator_config_factory_get_instance.assert_called_once_with(
                manure_separator_type
        )


# Test BaseManureSeparator's daily_update() method
# ================================================

def test_base_manure_separator_daily_update(mocker: MockFixture) -> None:
    """Unit test for BaseManureSeparator's daily_update() method."""
    # Arrange
    mock_manure_separator_config: ManureSeparatorConfig = mocker.MagicMock(spec=ManureSeparatorConfig)
    mock_manure_separator_config.total_solids_removal_efficiency_for_separator = \
        total_solids_removal_efficiency_for_separator = 0.1
    mock_manure_separator_config.percent_dry_solids = percent_dry_solids = 0.2
    mock_manure_separator_config.volatile_solids_removal_efficiency_for_separator = \
        volatile_solids_removal_efficiency_for_separator = 0.3
    mock_manure_separator_config.nitrogen_removal_efficiency_for_separator = \
        nitrogen_removal_efficiency_for_separator = 0.4
    mock_manure_separator_config.phosphorus_removal_efficiency_for_separator = \
        phosphorus_removal_efficiency_for_separator = 0.5
    mock_manure_separator_config.potassium_removal_efficiency_for_separator = \
        potassium_removal_efficiency_for_separator = 0.6
    mock_manure_separator_config.total_ammoniacal_nitrogen_removal_efficiency_for_separator = \
        total_ammoniacal_nitrogen_removal_efficiency_for_separator = 0.7

    base_manure_separator = BaseManureSeparator(mock_manure_separator_config)

    manure_separator_daily_input = mocker.MagicMock()
    manure_separator_daily_input.simulation_day = simulation_day = 1
    manure_separator_daily_input.pen_id = pen_id = 2
    manure_separator_daily_input.liquid_manure_daily_volume = liquid_manure_daily_volume = 3.0
    manure_separator_daily_input.liquid_manure_total_solids = liquid_manure_total_solids = 4.0
    manure_separator_daily_input.liquid_manure_total_volatile_solids = \
        liquid_manure_total_volatile_solids = 5.0
    manure_separator_daily_input.liquid_manure_nitrogen = liquid_manure_nitrogen = 6.0
    manure_separator_daily_input.liquid_manure_phosphorus = liquid_manure_phosphorus = 7.0
    manure_separator_daily_input.liquid_manure_potassium = liquid_manure_potassium = 8.0
    manure_separator_daily_input.liquid_manure_total_ammoniacal_nitrogen = \
        liquid_manure_total_ammoniacal_nitrogen = 9.0

    # Act
    manure_separator_daily_output = base_manure_separator.daily_update(manure_separator_daily_input)

    # Assert
    assert manure_separator_daily_output.simulation_day == simulation_day
    assert manure_separator_daily_output.pen_id == pen_id
    assert manure_separator_daily_output.total_daily_manure_volume == approx(liquid_manure_daily_volume)
    assert manure_separator_daily_output.final_solids_wet_mass == approx(
            liquid_manure_total_solids * total_solids_removal_efficiency_for_separator / percent_dry_solids
    )
    assert manure_separator_daily_output.solid_manure_total_solids == approx(
            liquid_manure_total_solids * total_solids_removal_efficiency_for_separator)
    assert manure_separator_daily_output.solid_manure_total_volatile_solids == approx(
            liquid_manure_total_volatile_solids * volatile_solids_removal_efficiency_for_separator)
    assert manure_separator_daily_output.solid_manure_nitrogen == approx(
            liquid_manure_nitrogen * nitrogen_removal_efficiency_for_separator)
    assert manure_separator_daily_output.solid_manure_phosphorus == approx(
            liquid_manure_phosphorus * phosphorus_removal_efficiency_for_separator)
    assert manure_separator_daily_output.solid_manure_potassium == approx(
            liquid_manure_potassium * potassium_removal_efficiency_for_separator)

    assert manure_separator_daily_output.liquid_manure_total_solids == approx(
            liquid_manure_total_solids * (1 - total_solids_removal_efficiency_for_separator))
    assert manure_separator_daily_output.liquid_manure_total_volatile_solids == approx(
            liquid_manure_total_volatile_solids * (1 - volatile_solids_removal_efficiency_for_separator))
    assert manure_separator_daily_output.liquid_manure_nitrogen == approx(
            liquid_manure_nitrogen * (1 - nitrogen_removal_efficiency_for_separator))
    assert manure_separator_daily_output.liquid_manure_phosphorus == approx(
            liquid_manure_phosphorus * (1 - phosphorus_removal_efficiency_for_separator))
    assert manure_separator_daily_output.liquid_manure_potassium == approx(
            liquid_manure_potassium * (1 - potassium_removal_efficiency_for_separator))
    assert manure_separator_daily_output.liquid_manure_total_ammoniacal_nitrogen == approx(
            liquid_manure_total_ammoniacal_nitrogen * (1 - total_ammoniacal_nitrogen_removal_efficiency_for_separator))
