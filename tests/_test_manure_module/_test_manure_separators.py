from typing import Type

import pytest
from pytest import approx, fixture
from pytest_mock import MockFixture

from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_separators.manure_separator_classes import (
    BaseManureSeparator,
    BeltPress,
    DecantingCentrifuge,
    ManureSeparatorConfig,
    ManureSeparatorFactory,
    ManureSeparatorType,
    MechanicalSandSeparator,
    MovingDiscPress,
    RotaryScreen,
    SandLaneSystem,
    ScrewPress,
    SlopeScreen,
)
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

    def assert_manure_separator_daily_output(
        output: ManureSeparatorDailyOutput,
    ) -> None:
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
        final_solids_wet_mass=final_solids_wet_mass,
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
        "final_solids_wet_mass": final_solids_wet_mass,
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
        manure_separator_type=ManureSeparatorType.SCREW_PRESS,
        percent_dry_solids=percent_dry_solids,
        total_solids_removal_efficiency_for_separator=TS_removal_efficiency_for_separator,
        volatile_solids_removal_efficiency_for_separator=VS_removal_efficiency_for_separator,
        nitrogen_removal_efficiency_for_separator=N_removal_efficiency_for_separator,
        total_ammoniacal_nitrogen_removal_efficiency_for_separator=TAN_removal_efficiency_for_separator,
        phosphorus_removal_efficiency_for_separator=P_removal_efficiency_for_separator,
        potassium_removal_efficiency_for_separator=K_removal_efficiency_for_separator,
    )

    # Assert
    assert manure_separator_config.manure_separator_type == ManureSeparatorType.SCREW_PRESS
    assert manure_separator_config.percent_dry_solids == percent_dry_solids
    assert manure_separator_config.total_solids_removal_efficiency_for_separator == TS_removal_efficiency_for_separator
    assert (
        manure_separator_config.volatile_solids_removal_efficiency_for_separator == VS_removal_efficiency_for_separator
    )
    assert manure_separator_config.nitrogen_removal_efficiency_for_separator == N_removal_efficiency_for_separator
    assert (
        manure_separator_config.total_ammoniacal_nitrogen_removal_efficiency_for_separator
        == TAN_removal_efficiency_for_separator
    )
    assert manure_separator_config.phosphorus_removal_efficiency_for_separator == P_removal_efficiency_for_separator
    assert manure_separator_config.potassium_removal_efficiency_for_separator == K_removal_efficiency_for_separator

    # --------------------

    # Case 2: Pass in a dictionary to the initializer
    # Arrange
    data = {
        "manure_separator_type": ManureSeparatorType.ROTARY_SCREEN,
        "percent_dry_solids": percent_dry_solids,
        "total_solids_removal_efficiency_for_separator": TS_removal_efficiency_for_separator,
        "volatile_solids_removal_efficiency_for_separator": VS_removal_efficiency_for_separator,
        "nitrogen_removal_efficiency_for_separator": N_removal_efficiency_for_separator,
        "total_ammoniacal_nitrogen_removal_efficiency_for_separator": TAN_removal_efficiency_for_separator,
        "phosphorus_removal_efficiency_for_separator": P_removal_efficiency_for_separator,
        "potassium_removal_efficiency_for_separator": K_removal_efficiency_for_separator,
    }

    # Act
    manure_separator_config = ManureSeparatorConfig(**data)

    # Assert
    assert manure_separator_config.manure_separator_type == ManureSeparatorType.ROTARY_SCREEN
    assert manure_separator_config.percent_dry_solids == percent_dry_solids
    assert manure_separator_config.total_solids_removal_efficiency_for_separator == TS_removal_efficiency_for_separator
    assert (
        manure_separator_config.volatile_solids_removal_efficiency_for_separator == VS_removal_efficiency_for_separator
    )
    assert manure_separator_config.nitrogen_removal_efficiency_for_separator == N_removal_efficiency_for_separator
    assert (
        manure_separator_config.total_ammoniacal_nitrogen_removal_efficiency_for_separator
        == TAN_removal_efficiency_for_separator
    )
    assert manure_separator_config.phosphorus_removal_efficiency_for_separator == P_removal_efficiency_for_separator
    assert manure_separator_config.potassium_removal_efficiency_for_separator == K_removal_efficiency_for_separator

    # --------------------

    # Case 3: Use default values
    # Act
    manure_separator_config = ManureSeparatorConfig(manure_separator_type=ManureSeparatorType.SCREW_PRESS)

    # Assert
    assert manure_separator_config.percent_dry_solids == 1.0
    assert manure_separator_config.total_solids_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.volatile_solids_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.nitrogen_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.total_ammoniacal_nitrogen_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.phosphorus_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.potassium_removal_efficiency_for_separator == 0.0


# Test ManureSeparatorFactory
# ===========================


@fixture
def mock_manure_separator_config() -> ManureSeparatorConfig:
    """Mocks a ManureSeparatorConfig object."""
    return ManureSeparatorConfig(manure_separator_type=ManureSeparatorType.SCREW_PRESS)


@pytest.mark.parametrize(
    "name,manure_separator_type,expected_manure_separator_class",
    [
        (
            "rotary screen",
            ManureSeparatorType.ROTARY_SCREEN,
            RotaryScreen,
        ),
        (
            "screw press",
            ManureSeparatorType.SCREW_PRESS,
            ScrewPress,
        ),
        (
            "belt press",
            ManureSeparatorType.BELT_PRESS,
            BeltPress,
        ),
        (
            "decanting centrifuge",
            ManureSeparatorType.DECANTING_CENTRIFUGE,
            DecantingCentrifuge,
        ),
        (
            "moving disc press",
            ManureSeparatorType.MOVING_DISC_PRESS,
            MovingDiscPress,
        ),
        (
            "slope screen",
            ManureSeparatorType.SLOPE_SCREEN,
            SlopeScreen,
        ),
        (
            "mechanical sand separator",
            ManureSeparatorType.MECHANICAL_SAND_SEPARATOR,
            MechanicalSandSeparator,
        ),
        (
            "sand lane manure separation",
            ManureSeparatorType.SAND_LANE_MANURE_SEPARATION,
            SandLaneSystem,
        ),
        (
            "dummy",
            ManureSeparatorType.ROTARY_SCREEN,
            RotaryScreen,
        ),
    ],
)
def test_manure_separator_factory_get_instance(
    mock_manure_separator_config: ManureSeparatorConfig,
    name: str,
    manure_separator_type: ManureSeparatorType,
    expected_manure_separator_class: Type[BaseManureSeparator],
) -> None:
    """Unit test for class ManureSeparatorFactory in file manure_separator_classes.py."""
    mock_manure_separator_config.manure_separator_type = manure_separator_type

    manure_separator = ManureSeparatorFactory.get_instance(name, mock_manure_separator_config)

    assert type(manure_separator) is expected_manure_separator_class
    assert manure_separator.config == mock_manure_separator_config


# Test BaseManureSeparator's daily_update() method
# ================================================


def test_base_manure_separator_daily_update(mocker: MockFixture) -> None:
    """Unit test for BaseManureSeparator's daily_update() method."""
    # Arrange
    mock_manure_separator_config: ManureSeparatorConfig = mocker.MagicMock(spec=ManureSeparatorConfig)
    mock_manure_separator_config.total_solids_removal_efficiency_for_separator = (
        total_solids_removal_efficiency_for_separator
    ) = 0.1
    mock_manure_separator_config.percent_dry_solids = percent_dry_solids = 0.2
    mock_manure_separator_config.volatile_solids_removal_efficiency_for_separator = (
        volatile_solids_removal_efficiency_for_separator
    ) = 0.3
    mock_manure_separator_config.nitrogen_removal_efficiency_for_separator = (
        nitrogen_removal_efficiency_for_separator
    ) = 0.4
    mock_manure_separator_config.phosphorus_removal_efficiency_for_separator = (
        phosphorus_removal_efficiency_for_separator
    ) = 0.5
    mock_manure_separator_config.potassium_removal_efficiency_for_separator = (
        potassium_removal_efficiency_for_separator
    ) = 0.6
    mock_manure_separator_config.total_ammoniacal_nitrogen_removal_efficiency_for_separator = (
        total_ammoniacal_nitrogen_removal_efficiency_for_separator
    ) = 0.7

    base_manure_separator = BaseManureSeparator(name="test", manure_separator_config=mock_manure_separator_config)

    manure_separator_daily_input = mocker.MagicMock()
    manure_separator_daily_input.simulation_day = simulation_day = 1
    manure_separator_daily_input.pen_id = pen_id = 2
    manure_separator_daily_input.liquid_manure_daily_volume = liquid_manure_daily_volume = 3.0
    manure_separator_daily_input.liquid_manure_total_solids = liquid_manure_total_solids = 4.0
    manure_separator_daily_input.liquid_manure_total_volatile_solids = liquid_manure_total_volatile_solids = 5.0
    manure_separator_daily_input.liquid_manure_nitrogen = liquid_manure_nitrogen = 6.0
    manure_separator_daily_input.liquid_manure_phosphorus = liquid_manure_phosphorus = 7.0
    manure_separator_daily_input.liquid_manure_potassium = liquid_manure_potassium = 8.0
    manure_separator_daily_input.liquid_manure_total_ammoniacal_nitrogen = liquid_manure_total_ammoniacal_nitrogen = 9.0

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
        liquid_manure_total_solids * total_solids_removal_efficiency_for_separator
    )
    assert manure_separator_daily_output.solid_manure_total_volatile_solids == approx(
        liquid_manure_total_volatile_solids * volatile_solids_removal_efficiency_for_separator
    )
    assert manure_separator_daily_output.solid_manure_nitrogen == approx(
        liquid_manure_nitrogen * nitrogen_removal_efficiency_for_separator
    )
    assert manure_separator_daily_output.solid_manure_phosphorus == approx(
        liquid_manure_phosphorus * phosphorus_removal_efficiency_for_separator
    )
    assert manure_separator_daily_output.solid_manure_potassium == approx(
        liquid_manure_potassium * potassium_removal_efficiency_for_separator
    )

    assert manure_separator_daily_output.liquid_manure_total_solids == approx(
        liquid_manure_total_solids * (1 - total_solids_removal_efficiency_for_separator)
    )
    assert manure_separator_daily_output.liquid_manure_total_volatile_solids == approx(
        liquid_manure_total_volatile_solids * (1 - volatile_solids_removal_efficiency_for_separator)
    )
    assert manure_separator_daily_output.liquid_manure_nitrogen == approx(
        liquid_manure_nitrogen * (1 - nitrogen_removal_efficiency_for_separator)
    )
    assert manure_separator_daily_output.liquid_manure_phosphorus == approx(
        liquid_manure_phosphorus * (1 - phosphorus_removal_efficiency_for_separator)
    )
    assert manure_separator_daily_output.liquid_manure_potassium == approx(
        liquid_manure_potassium * (1 - potassium_removal_efficiency_for_separator)
    )
    assert manure_separator_daily_output.liquid_manure_total_ammoniacal_nitrogen == approx(
        liquid_manure_total_ammoniacal_nitrogen * (1 - total_ammoniacal_nitrogen_removal_efficiency_for_separator)
    )
