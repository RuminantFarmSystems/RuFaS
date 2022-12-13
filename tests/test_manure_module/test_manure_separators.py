from pytest import approx

# Test ManureSeparatorDailyOutput
# ===============================
from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorConfig
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput


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
        assert output.TS_solid == TS_solid
        assert output.VS_solid == VS_solid
        assert output.N_solid == N_solid
        assert output.P_solid == P_solid
        assert output.K_solid == K_solid
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
        assert output.daily_volume == approx(expected_final_daily_volume)

    # --------------------

    # Case 1: Pass in all arguments to the initializer

    # Act
    manure_separator_daily_output = ManureSeparatorDailyOutput(
            pen_id=pen_id,
            simulation_day=sim_day,
            TS_solid=TS_solid,
            VS_solid=VS_solid,
            N_solid=N_solid,
            P_solid=P_solid,
            K_solid=K_solid,
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
        "TS_solid": TS_solid,
        "VS_solid": VS_solid,
        "N_solid": N_solid,
        "P_solid": P_solid,
        "K_solid": K_solid,
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
            TS_removal_efficiency_for_separator=TS_removal_efficiency_for_separator,
            VS_removal_efficiency_for_separator=VS_removal_efficiency_for_separator,
            N_removal_efficiency_for_separator=N_removal_efficiency_for_separator,
            TAN_removal_efficiency_for_separator=TAN_removal_efficiency_for_separator,
            P_removal_efficiency_for_separator=P_removal_efficiency_for_separator,
            K_removal_efficiency_for_separator=K_removal_efficiency_for_separator
    )

    # Assert
    assert manure_separator_config.percent_dry_solids == percent_dry_solids
    assert manure_separator_config.TS_removal_efficiency_for_separator == TS_removal_efficiency_for_separator
    assert manure_separator_config.VS_removal_efficiency_for_separator == VS_removal_efficiency_for_separator
    assert manure_separator_config.N_removal_efficiency_for_separator == N_removal_efficiency_for_separator
    assert manure_separator_config.TAN_removal_efficiency_for_separator == TAN_removal_efficiency_for_separator
    assert manure_separator_config.P_removal_efficiency_for_separator == P_removal_efficiency_for_separator
    assert manure_separator_config.K_removal_efficiency_for_separator == K_removal_efficiency_for_separator

    # --------------------

    # Case 2: Pass in a dictionary to the initializer
    # Arrange
    data = {
        "percent_dry_solids": percent_dry_solids,
        "TS_removal_efficiency_for_separator": TS_removal_efficiency_for_separator,
        "VS_removal_efficiency_for_separator": VS_removal_efficiency_for_separator,
        "N_removal_efficiency_for_separator": N_removal_efficiency_for_separator,
        "TAN_removal_efficiency_for_separator": TAN_removal_efficiency_for_separator,
        "P_removal_efficiency_for_separator": P_removal_efficiency_for_separator,
        "K_removal_efficiency_for_separator": K_removal_efficiency_for_separator
    }

    # Act
    manure_separator_config = ManureSeparatorConfig(**data)

    # Assert
    assert manure_separator_config.percent_dry_solids == percent_dry_solids
    assert manure_separator_config.TS_removal_efficiency_for_separator == TS_removal_efficiency_for_separator
    assert manure_separator_config.VS_removal_efficiency_for_separator == VS_removal_efficiency_for_separator
    assert manure_separator_config.N_removal_efficiency_for_separator == N_removal_efficiency_for_separator
    assert manure_separator_config.TAN_removal_efficiency_for_separator == TAN_removal_efficiency_for_separator
    assert manure_separator_config.P_removal_efficiency_for_separator == P_removal_efficiency_for_separator
    assert manure_separator_config.K_removal_efficiency_for_separator == K_removal_efficiency_for_separator

    # --------------------

    # Case 3: Use default values
    # Act
    manure_separator_config = ManureSeparatorConfig()

    # Assert
    assert manure_separator_config.percent_dry_solids == 1.0
    assert manure_separator_config.TS_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.VS_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.N_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.TAN_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.P_removal_efficiency_for_separator == 0.0
    assert manure_separator_config.K_removal_efficiency_for_separator == 0.0
