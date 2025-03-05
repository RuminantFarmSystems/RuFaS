import pytest
from datetime import datetime
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.digester.anaerobic_digester import AnaerobicDigester
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


@pytest.fixture
def digester() -> AnaerobicDigester:
    """Anaerobic Digester fixture for testing."""
    return AnaerobicDigester(
        name="test",
        temperature_set_point=20.0,
        hydraulic_retention_time=25.0,
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
        pen_manure_data=None
    )


@pytest.fixture
def time() -> Time:
    """Time fixture for testing."""
    return Time(datetime(2023, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 5))


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

    assert actual._manure_to_digest.is_empty is True
    assert actual._temperature_set_point == 10.0
    assert actual._hydraulic_retention_time == 25
    assert actual._top_cover_volume_fraction == 0.02
    assert actual._methane_leakage_fraction == 0.01
    assert actual._evaporation_fraction == 0.001


def test_receive_manure(digester: AnaerobicDigester, manure_stream: ManureStream) -> None:
    """Test that manure is received correctly."""
    digester.receive_manure(manure_stream)

    assert digester._manure_to_digest == manure_stream


@pytest.mark.parametrize(
    "degradable, non_degradable, destroyed, expected_degradable, expected_non_degradable, expected_error_count",
    [(100.0, 100.0, 50.0, 75.0, 75.0, 0), (900.0, 100.0, 100.0, 810.0, 90.0, 0), (50.0, 20.0, 75.0, 0.0, 0.0, 1)],
)
def test_destroy_volatile_solids(
    digester: AnaerobicDigester,
    time: Time,
    mocker: MockerFixture,
    degradable: float,
    non_degradable: float,
    destroyed: float,
    expected_degradable: float,
    expected_non_degradable: float,
    expected_error_count: int,
) -> None:
    """Test that volatile solids are destroyed correctly."""
    digester._manure_to_digest.degradable_volatile_solids = degradable
    digester._manure_to_digest.non_degradable_volatile_solids = non_degradable
    add_error = mocker.patch.object(digester._om, "add_error")

    actual = digester._destroy_volatile_solids(destroyed, time)

    assert actual.degradable_volatile_solids == expected_degradable
    assert actual.non_degradable_volatile_solids == expected_non_degradable
    assert add_error.call_count == expected_error_count


def test_report_anaerobic_digester_outputs(digester: AnaerobicDigester, time: Time, mocker: MockerFixture) -> None:
    """Tests that output variables from an anaerobic digester are calculated correctly."""
    add_var = mocker.patch.object(digester._om, "add_variable")
    expected_info_map = {
        "class": "AnaerobicDigester",
        "function": "_report_anaerobic_digester_outputs",
        "prefix": "AnaerobicDigester.test",
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
        time=time,
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
