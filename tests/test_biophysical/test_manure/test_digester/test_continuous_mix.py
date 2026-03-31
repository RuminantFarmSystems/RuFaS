from unittest.mock import call

import pytest
from dataclasses import replace
from datetime import datetime
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.digester.continuous_mix import ContinuousMix
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


@pytest.fixture
def conditions() -> CurrentDayConditions:
    """Current day conditions fixture for testing."""
    return CurrentDayConditions(
        incoming_light=10.0,
        min_air_temperature=12.0,
        mean_air_temperature=18.0,
        max_air_temperature=24.0,
        daylength=14.0,
        annual_mean_air_temperature=14.5,
    )


@pytest.fixture
def digester() -> ContinuousMix:
    """Anaerobic Digester fixture for testing."""
    return ContinuousMix(
        name="test",
        anaerobic_digestion_temperature_set_point=20.0,
        hydraulic_retention_time=25,
        biogas_leakage_fraction=0.02,
    )


@pytest.fixture
def manure_stream() -> ManureStream:
    """Manure Stream fixture for testing."""
    return ManureStream(
        water=100.0,
        ammoniacal_nitrogen=10.0,
        nitrogen=20.0,
        phosphorus=3.0,
        potassium=2.0,
        ash=15.0,
        non_degradable_volatile_solids=20.0,
        degradable_volatile_solids=12.0,
        total_solids=50.0,
        volume=500.0,
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10
    )


@pytest.fixture
def time() -> RufasTime:
    """RufasTime fixture for testing."""
    return RufasTime(datetime(2023, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 5))


def test_anaerobic_digester_init() -> None:
    """Test that an Anaerobic Digester is initialized correctly."""
    actual = ContinuousMix(
        name="actual",
        anaerobic_digestion_temperature_set_point=10.0,
        hydraulic_retention_time=25,
        biogas_leakage_fraction=0.01,
    )

    assert actual.is_housing_emissions_calculator is False
    assert actual._manure_in_digester.is_empty is True
    assert actual._temperature_set_point == 10.0
    assert actual._hydraulic_retention_time == 25
    assert actual._biogas_leakage_fraction == 0.01


def test_receive_manure(digester: ContinuousMix, manure_stream: ManureStream) -> None:
    """Test that manure is received correctly."""
    digester.receive_manure(manure_stream)

    assert digester._manure_in_digester == manure_stream


def test_receive_manure_error(digester: ContinuousMix, manure_stream: ManureStream) -> None:
    """Test that Anaerobic Digester raises an error when incompatible manure is passed."""
    manure_stream.pen_manure_data = PenManureData(
        100, 500.0, AnimalCombination.LAC_COW, "open lot", 1000.0, 50.0, StreamType.GENERAL
    )
    with pytest.raises(ValueError):
        digester.receive_manure(manure_stream)


def test_process_manure(
    digester: ContinuousMix,
    manure_stream: ManureStream,
    conditions: CurrentDayConditions,
    time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Test that manure is digested correctly."""
    digester._manure_in_digester = replace(manure_stream)

    manure_stream.degradable_volatile_solids, manure_stream.non_degradable_volatile_solids = 12.0, 11.0
    mock_calculate_generated_methane = mocker.patch.object(
        digester, "_calculate_generated_methane", return_value=(10.0, 18.8)
    )
    mock_calculate_generated_carbon_dioxide = mocker.patch.object(
        digester, "_calculate_generated_carbon_dioxide", return_value=(23.3, 66.6)
    )
    destroy_vol_sols = mocker.patch.object(digester, "_destroy_volatile_solids", return_value=manure_stream)
    methane_leakage = mocker.patch.object(digester, "_calculate_methane_leakage", return_value=(9.0, 19.62))
    report_outputs = mocker.patch.object(digester, "_report_continuous_mix_outputs")

    expected_volume = 499.9663636363636
    expected_ammonical_nitrogen = 10.0
    expected_manure_stream = replace(
        manure_stream, volume=expected_volume, ammoniacal_nitrogen=expected_ammonical_nitrogen
    )

    actual = digester.process_manure(conditions, time)

    assert actual["manure"] == expected_manure_stream
    mock_calculate_generated_methane.assert_called_once()
    mock_calculate_generated_carbon_dioxide.assert_called_once()
    destroy_vol_sols.assert_called_once()
    methane_leakage.assert_called_once()
    report_outputs.assert_called_once()


def test_process_manure_empty_stream(
    digester: ContinuousMix, time: RufasTime, conditions: CurrentDayConditions, mocker: MockerFixture
) -> None:
    """Test that process_manure handles no manure to be processed correctly."""
    digester._manure_in_digester = ManureStream.make_empty_manure_stream()
    mock_calculate_generated_methane = mocker.patch.object(digester, "_calculate_generated_methane")
    mock_calculate_generated_carbon_dioxide = mocker.patch.object(digester, "_calculate_generated_carbon_dioxide")
    destroy_vol_sols = mocker.patch.object(digester, "_destroy_volatile_solids")
    methane_leakage = mocker.patch.object(digester, "_calculate_methane_leakage")
    report_outputs = mocker.patch.object(digester, "_report_continuous_mix_outputs")

    actual = digester.process_manure(conditions, time)

    assert actual == {}
    report_outputs.assert_called_once()
    mock_calculate_generated_methane.assert_not_called()
    mock_calculate_generated_carbon_dioxide.assert_not_called()
    destroy_vol_sols.assert_not_called()
    methane_leakage.assert_not_called()


def test_calculate_generated_carbon_dioxide(digester: ContinuousMix) -> None:
    """Test that carbon dioxide mass and volume are calculated correctly."""
    actual_mass, actual_volume = digester._calculate_generated_carbon_dioxide(generated_methane_volume=10.0)
    assert actual_mass == 12.190655368219907
    assert actual_volume == 6.666666666666666


def test_calculate_generated_methane(digester: ContinuousMix, mocker: MockerFixture) -> None:
    """Test that carbon dioxide mass and volume are calculated correctly."""
    mock_calculate_CSTR_methane_volume = mocker.patch.object(
        digester, "_calculate_CSTR_methane_volume", return_value=10.0
    )

    actual_mass, actual_volume = digester._calculate_generated_methane()

    mock_calculate_CSTR_methane_volume.assert_called_once()
    assert actual_mass == 6.664557331501272
    assert actual_volume == 10.0


@pytest.mark.parametrize(
    "bedding_non_degradable, degradable, non_degradable, destroyed, expected_degradable, expected_non_degradable,"
    " expected_error_count",
    [(50, 100.0, 100.0, 50.0, 80.0, 80.0, 0), (50, 900.0, 100.0, 100.0, 814.2857142857143, 90.47619047619048, 0),
     (1, 50.0, 20.0, 75.0, 0.0, 0.0, 1)],
)
def test_destroy_volatile_solids(
    digester: ContinuousMix,
    time: RufasTime,
    mocker: MockerFixture,
    degradable: float,
    non_degradable: float,
    bedding_non_degradable: float,
    destroyed: float,
    expected_degradable: float,
    expected_non_degradable: float,
    expected_error_count: int,
) -> None:
    """Test that volatile solids are destroyed correctly."""
    digester._manure_in_digester.degradable_volatile_solids = degradable
    digester._manure_in_digester.non_degradable_volatile_solids = non_degradable
    digester._manure_in_digester.bedding_non_degradable_volatile_solids = bedding_non_degradable
    add_error = mocker.patch.object(digester._om, "add_error")

    actual = digester._destroy_volatile_solids(destroyed, time)

    assert actual.degradable_volatile_solids == expected_degradable
    assert pytest.approx(actual.non_degradable_volatile_solids) == expected_non_degradable
    assert add_error.call_count == expected_error_count


def test_report_continuous_mix_outputs(digester: ContinuousMix, time: RufasTime, mocker: MockerFixture) -> None:
    """Tests that output variables from an anaerobic digester are calculated correctly."""
    mock_report_manure_stream = mocker.patch.object(digester, "_report_manure_stream")
    mock_report_processor_output = mocker.patch.object(digester, "_report_processor_output")

    data_origin_function = "_report_continuous_mix_outputs"
    simulation_day = time.simulation_day
    biogas, methane, methane_leakage = 11.1, 20.0, 8.8

    digester._report_continuous_mix_outputs(
        captured_biogas_volume=biogas,
        captured_methane_volume=methane,
        methane_leakage_mass=methane_leakage,
        simulation_day=time.simulation_day,
    )

    mock_report_manure_stream.assert_called_once_with(digester._manure_in_digester, "", simulation_day)
    assert mock_report_processor_output.call_args_list == [
        call("captured_biogas_volume", biogas, data_origin_function, MeasurementUnits.CUBIC_METERS, simulation_day),
        call("captured_methane_volume", methane, data_origin_function, MeasurementUnits.CUBIC_METERS, simulation_day),
        call(
            "methane_leakage_mass",
            methane_leakage,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        ),
    ]


@pytest.mark.parametrize(
    "total_vol_sols, methane_production_potential, expected",
    [(100.0, 0.24, 24.0), (0.0, 0.24, 0.0), (100.0, 0.17, 17.0), (0.0, 0.17, 0.0)],
)
def test_calculate_CSTR_methane_volume(
    total_vol_sols: float, methane_production_potential: float, expected: float
) -> None:
    """Test that the generated methane volume is calculated correctly."""
    actual = ContinuousMix._calculate_CSTR_methane_volume(total_vol_sols, methane_production_potential)

    assert actual == expected


@pytest.mark.parametrize(
    "mass, volume, leakage, expected_mass, expected_volume",
    [
        (0.0, 0.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.2, 0.0, 0.0),
        (100.0, 88.8, 0.0, 0.0, 0.0),
        (100.0, 88.8, 0.25, 25.0, 22.2),
    ],
)
def test_calculate_methane_leakage(
    mass: float, volume: float, leakage: float, expected_mass: float, expected_volume: float
) -> None:
    """Test that methane leakage is calculated correctly."""
    actual_mass, actual_volume = ContinuousMix._calculate_methane_leakage(mass, volume, leakage)

    assert actual_mass == expected_mass
    assert actual_volume == expected_volume
