import pytest
from dataclasses import replace
from datetime import datetime
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.digester.anaerobic_digester import AnaerobicDigester
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.enums import AnimalCombination
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
def digester() -> AnaerobicDigester:
    """Anaerobic Digester fixture for testing."""
    return AnaerobicDigester(
        name="test",
        temperature_set_point=20.0,
        hydraulic_retention_time=25,
        top_cover_volume_fraction=0.1,
        methane_leakage_fraction=0.02,
        evaporation_fraction=0.01,
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
        pen_manure_data=None,
    )


@pytest.fixture
def time() -> RufasTime:
    """RufasTime fixture for testing."""
    return RufasTime(datetime(2023, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 5))


def test_anaerobic_digester_init() -> None:
    """Test that an Anaerobic Digester is initialized correctly."""
    actual = AnaerobicDigester(
        name="actual",
        temperature_set_point=10.0,
        hydraulic_retention_time=25,
        top_cover_volume_fraction=0.02,
        methane_leakage_fraction=0.01,
        evaporation_fraction=0.001,
    )

    assert actual.is_housing_emissions_calculator is False
    assert actual._manure_in_digester.is_empty is True
    assert actual._temperature_set_point == 10.0
    assert actual._hydraulic_retention_time == 25
    assert actual._top_cover_volume_fraction == 0.02
    assert actual._methane_leakage_fraction == 0.01
    assert actual._evaporation_fraction == 0.001


def test_receive_manure(digester: AnaerobicDigester, manure_stream: ManureStream) -> None:
    """Test that manure is received correctly."""
    digester.receive_manure(manure_stream)

    assert digester._manure_in_digester == manure_stream


def test_receive_manure_error(digester: AnaerobicDigester, manure_stream: ManureStream) -> None:
    """Test that Anaerobic Digester raises an error when incompatible manure is passed."""
    manure_stream.pen_manure_data = PenManureData(
        100, 500.0, AnimalCombination.LAC_COW, "open lot", 1000.0, 50.0, StreamType.GENERAL
    )
    with pytest.raises(ValueError):
        digester.receive_manure(manure_stream)


def test_process_manure(
    digester: AnaerobicDigester,
    manure_stream: ManureStream,
    conditions: CurrentDayConditions,
    time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Test that manure is digested correctly."""
    digester._manure_in_digester = replace(manure_stream)
    manure_stream.degradable_volatile_solids, manure_stream.non_degradable_volatile_solids = 12.0, 11.0
    specific_energy_input = mocker.patch.object(digester, "_calculate_specific_input_energy", return_value=3.0)
    methane_volume = mocker.patch.object(digester, "_calculate_CSTR_methane_volume", return_value=10.0)
    destroy_vol_sols = mocker.patch.object(digester, "_destroy_volatile_solids", return_value=manure_stream)
    methane_leakage = mocker.patch.object(digester, "_calculate_methane_leakage", return_value=9.0)
    methane_energy = mocker.patch.object(digester, "_calculate_methane_energy_content", return_value=8.0)
    report_outputs = mocker.patch.object(digester, "_report_anaerobic_digester_outputs")
    expected_volume = manure_stream.volume - 0.01790909090909  # Expected reduction in volume calculated manually.
    expected_manure_stream = replace(manure_stream, volume=expected_volume)

    actual = digester.process_manure(conditions, time)

    assert actual["manure"] == expected_manure_stream
    specific_energy_input.assert_called_once()
    methane_volume.assert_called_once()
    destroy_vol_sols.assert_called_once()
    methane_leakage.assert_called_once()
    methane_energy.assert_called_once()
    report_outputs.assert_called_once()


def test_process_manure_empty_stream(
    digester: AnaerobicDigester, time: RufasTime, conditions: CurrentDayConditions, mocker: MockerFixture
) -> None:
    """Test that process_manure handles no manure to be processed correctly."""
    digester._manure_in_digester = ManureStream.make_empty_manure_stream()
    report_outputs = mocker.patch.object(digester, "_report_anaerobic_digester_outputs")

    actual = digester.process_manure(conditions, time)

    assert actual == {}
    report_outputs.assert_called_once()


@pytest.mark.parametrize(
    "degradable, non_degradable, destroyed, expected_degradable, expected_non_degradable, expected_error_count",
    [(100.0, 100.0, 50.0, 75.0, 75.0, 0), (900.0, 100.0, 100.0, 810.0, 90.0, 0), (50.0, 20.0, 75.0, 0.0, 0.0, 1)],
)
def test_destroy_volatile_solids(
    digester: AnaerobicDigester,
    time: RufasTime,
    mocker: MockerFixture,
    degradable: float,
    non_degradable: float,
    destroyed: float,
    expected_degradable: float,
    expected_non_degradable: float,
    expected_error_count: int,
) -> None:
    """Test that volatile solids are destroyed correctly."""
    digester._manure_in_digester.degradable_volatile_solids = degradable
    digester._manure_in_digester.non_degradable_volatile_solids = non_degradable
    add_error = mocker.patch.object(digester._om, "add_error")

    actual = digester._destroy_volatile_solids(destroyed, time)

    assert actual.degradable_volatile_solids == expected_degradable
    assert actual.non_degradable_volatile_solids == expected_non_degradable
    assert add_error.call_count == expected_error_count


def test_report_anaerobic_digester_outputs(digester: AnaerobicDigester, time: RufasTime, mocker: MockerFixture) -> None:
    """Tests that output variables from an anaerobic digester are calculated correctly."""
    add_var = mocker.patch.object(digester._om, "add_variable")
    expected_info_map = {
        "class": "AnaerobicDigester",
        "function": "_report_anaerobic_digester_outputs",
        "prefix": "Manure.Digester.AnaerobicDigester.test",
        "simulation_day": time.simulation_day,
        "units": MeasurementUnits.CUBIC_METERS,
    }
    methane = 20.0

    digester._report_anaerobic_digester_outputs(
        biogas=0.0,
        biogas_energy_content=0.0,
        evaporated_water=0.0,
        heating_input_energy=0.0,
        methane_generation_volume=methane,
        methane_leakage_mass=0.0,
        minimum_digester_volume=0.0,
        top_cover_volume=0.0,
        simulation_day=time.simulation_day,
    )

    assert add_var.call_count == 20
    add_var.assert_any_call("methane_generation_volume", methane, expected_info_map)


@pytest.mark.parametrize(
    "set_point, effluent_temp, influent_heat, heat_capacity, expected",
    [(20.0, 15.0, 1.8, 1.9, 9.25), (17.0, 22.0, 1.2, 1.8, -7.5)],
)
def test_calculate_specific_input_energy(
    mocker: MockerFixture,
    set_point: float,
    effluent_temp: float,
    influent_heat: float,
    heat_capacity: float,
    expected: float,
) -> None:
    """Test that the specific input energy of an Anaerobic Digester is calculated correctly."""
    mocker.patch.object(AnaerobicDigester, "_bind_influent_temperature", return_value=effluent_temp)
    mocker.patch.object(
        AnaerobicDigester, "_calculate_manure_heat_capacity", side_effect=[influent_heat, heat_capacity]
    )

    actual = AnaerobicDigester._calculate_specific_input_energy(17.0, 0.93, set_point)

    assert actual == expected


@pytest.mark.parametrize("temp, expected", [(30.0, 30.0), (10.0, 10.0), (0.0, 4.0)])
def test_bind_influent_temperature(temp: float, expected: float) -> None:
    """Test that the influent temperature is bounded correctly."""
    actual = AnaerobicDigester._bind_influent_temperature(temp)

    assert actual == expected


@pytest.mark.parametrize("temp, moisture_frac, expected", [(20.0, 0.5, 1.84922), (5.0, 0.9, 1.98669)])
def test_calculate_manure_heat_capacity(temp: float, moisture_frac: float, expected: float) -> None:
    """Test that the heat capacity of manure is calculated correctly."""
    actual = AnaerobicDigester._calculate_manure_heat_capacity(temp, moisture_frac)

    assert actual == expected


@pytest.mark.parametrize("total_vol_sols, expected", [(100.0, 24.0), (0.0, 0.0)])
def test_calculate_CSTR_methane_volume(total_vol_sols: float, expected: float) -> None:
    """Test that the generated methane volume is calculated correctly."""
    actual = AnaerobicDigester._calculate_CSTR_methane_volume(total_vol_sols)

    assert actual == expected


@pytest.mark.parametrize(
    "methane, leakage, expected", [(0.0, 0.0, 0.0), (0.0, 0.2, 0.0), (100.0, 0.0, 0.0), (100.0, 0.25, 25.0)]
)
def test_calculate_methane_leakage(methane: float, leakage: float, expected: float) -> None:
    """Test that methane leakage is calculated correctly."""
    actual = AnaerobicDigester._calculate_methane_leakage(methane, leakage)

    assert actual == expected


@pytest.mark.parametrize("methane, expected", [(100.0, 5500.0), (0.0, 0.0)])
def test_calculate_methane_energy_content(methane: float, expected: float) -> None:
    """Test that the energy content of methane is calculated correctly."""
    actual = AnaerobicDigester._calculate_methane_energy_content(methane)

    assert actual == expected
