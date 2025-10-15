from math import exp, log
from unittest.mock import MagicMock, call, patch

import pytest

from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.phosphorus_cycling.fertilizer import Fertilizer
from RUFAS.biophysical.field.soil.soil_data import SoilData


# --- Static method tests ---
@pytest.mark.parametrize("cover_factor,days", [(0.5333, 20), (0.6667, 60), (0.8, 4), (0.5333, 1_000)])
def test_determine_fraction_phosphorus_remaining(cover_factor, days):
    """Tests that the fraction of phosphorus remaining in the available pool after absorption by soil is correctly
    calculated."""
    observe = Fertilizer._determine_fraction_phosphorus_remaining(cover_factor, days)
    expect = (-0.16 * log(days)) + cover_factor
    if expect < 0:
        expect = 0
    assert observe == expect


@pytest.mark.parametrize(
    "rainfall,runoff",
    [
        (5.6, 1.2),
        (8.3, 8.3),
        (4.7, 0.8),
        (18.6, 3.4498274),
    ],
)
def test_determine_phosphorus_distribution_factor(rainfall, runoff):
    """Tests that the distribution factor for partitioning solubilized phosphorus between runoff and infiltration is
    determined correctly."""
    observe = Fertilizer._determine_phosphorus_distribution_factor(rainfall, runoff)
    expect = 0.034 * exp(3.4 * (runoff / rainfall))
    assert observe == expect


@pytest.mark.parametrize(
    "phosphorus,frac_released,distribution_factor,total_rainfall",
    [
        (10000000, 1, 0.28347283947, 12300),
        (1295043, 0.4, 0.238947265, 12320),
        (100421, 0.075, 0.3485781, 9183),
    ],
)
def test_determine_dissolved_phosphorus_concentration(phosphorus, frac_released, distribution_factor, total_rainfall):
    """Tests that the concentration of dissolved phosphorus is runoff is correctly calculated."""
    observe = Fertilizer._determine_dissolved_phosphorus_concentration(
        phosphorus, frac_released, distribution_factor, total_rainfall
    )
    expect = phosphorus * frac_released * distribution_factor / total_rainfall
    assert observe == expect


# --- Helper function tests ---
@pytest.mark.parametrize(
    "initial_pool_amount,available_pool_amount,sorption_fraction,absorbed_phos,"
    "days_since_application,cover_type,field_size",
    [
        (100, 100, 0.10, 90.0, 1, "BARE", 1.56),
        (120, 96, 0.33, 56.4, 5, "GRASSED", 2.876),
        (96, 21, 0.266, 21.0, 40, "RESIDUE_COVER", 1.243),
        (
            100,
            15,
            1.0,
            15.0,
            35,
            "GRASSED",
            2.3954,
        ),  # All phosphorus should be removed from pool
        (
            90,
            0,
            0.0,
            0.0,
            78,
            "RESIDUE_COVER",
            0.897,
        ),  # No phosphorus left in available pool
    ],
)
def test_absorb_phosphorus_from_available_pool(
    initial_pool_amount: float,
    available_pool_amount: float,
    sorption_fraction: float,
    absorbed_phos: float,
    days_since_application: int,
    cover_type: str,
    field_size: float,
) -> None:
    """Tests that soil absorbs the correct amount of phosphorus from the available phosphorus pool"""
    data = SoilData(
        full_available_phosphorus_pool=initial_pool_amount,
        available_phosphorus_pool=available_pool_amount,
        days_since_application=days_since_application,
        cover_type=cover_type,
        field_size=field_size,
    )
    fert = Fertilizer(data)

    expected_remaining_phosphorus = available_pool_amount - absorbed_phos
    with (
        patch.object(fert.data.soil_layers[0], "add_to_labile_phosphorus", new_callable=MagicMock) as add_phos,
        patch.object(
            fert,
            "_determine_fraction_phosphorus_remaining",
            new_callable=MagicMock,
            return_value=sorption_fraction,
        ) as determine_fraction,
    ):
        fert._absorb_phosphorus_from_available_pool(field_size)

    add_phos.assert_called_once_with(absorbed_phos, field_size)
    determine_fraction.assert_called_with(fert.data.cover_factor, days_since_application)
    assert fert.data.available_phosphorus_pool == expected_remaining_phosphorus


@pytest.mark.parametrize("phosphorus_added,field_size", [(100, 1.33), (20.22, 2.4), (300.1, 0.5)])
def test_add_phosphorus_to_soil_profile(phosphorus_added: float, field_size: float) -> None:
    """Tests that added phosphorus is correctly partitioned between the top two soil layers."""
    data = SoilData(field_size=field_size)
    fertilizer = Fertilizer(soil_data=data)
    expected_calls = [
        call(0.8 * phosphorus_added, field_size),
        call(0.2 * phosphorus_added, field_size),
    ]

    with patch.object(LayerData, "add_to_labile_phosphorus") as add_to_pool:
        fertilizer._add_phosphorus_to_soil(phosphorus_added, field_size)

    add_to_pool.assert_has_calls(expected_calls)


@pytest.mark.parametrize(
    "pool_amount,days_since_application,rainfall_events,rainfall,runoff,field_size",
    [
        (30, 0, 1, 30, 2, 3),
        (15.434, 1, 1, 14, 1.9899, 2.9384),
        (0.98321, 15, 1, 7, 0.35, 1.342),
        (10, 13, 2, 9, 0.818, 0.95),
        (17, 21, 3, 11, 1.3, 3.45),
    ],
)
def test_leach_phosphorus(
    pool_amount: float,
    days_since_application: int,
    rainfall_events: int,
    rainfall: float,
    runoff: float,
    field_size: float,
) -> None:
    """Tests that the correct amounts of phosphorus to be removed by runoff and soil absorption are calculated."""
    data = SoilData(
        days_since_application=days_since_application,
        field_size=field_size,
        rain_events_after_fertilizer_application=rainfall_events,
    )
    if rainfall_events == 1:
        data.available_phosphorus_pool = pool_amount
    else:
        data.recalcitrant_phosphorus_pool = pool_amount
    fert = Fertilizer(data)

    fert._determine_phosphorus_distribution_factor = MagicMock(return_value=0.05)
    fert._determine_dissolved_phosphorus_concentration = MagicMock(return_value=0.05)

    pool_amount_mg = pool_amount * 1000000
    solubilized_amount = pool_amount * fert.data.solubilizing_factor
    concentration = 0.05  # Matches what is mocked for _determine_dissolved_phosphorus_concentration()
    rainfall_liters = rainfall * (field_size * 10000000000) * (1 / 1000000)
    runoff_liters = runoff * field_size * 10000
    dissolved_phosphorus_runoff_mg = runoff_liters * concentration
    dissolved_phosphorus_runoff_kg = dissolved_phosphorus_runoff_mg / 1000000
    adsorbed_phosphorus_kg = max(0, solubilized_amount - dissolved_phosphorus_runoff_kg)
    expected = {
        "runoff_phosphorus": dissolved_phosphorus_runoff_kg,
        "absorbed_phosphorus": adsorbed_phosphorus_kg,
    }

    observed = fert._determine_leached_phosphorus(rainfall, runoff, field_size, pool_amount)

    fert._determine_phosphorus_distribution_factor.assert_called_once_with(rainfall, runoff)
    fert._determine_dissolved_phosphorus_concentration.assert_called_once_with(
        pool_amount_mg, fert.data.solubilizing_factor, 0.05, rainfall_liters
    )
    assert observed == pytest.approx(expected)


@pytest.mark.parametrize(
    "rainfall,runoff,field_size,rain_events,full_available_pool,available_pool," "days_since_application",
    [
        (0, 0, 1, 0, 100, 100, 0),  # Day of application, no rain
        (13, 0, 1.8, 1, 100, 100, 0),  # Day of application, rain but no runoff
        (13, 3, 0.95, 1, 100, 100, 0),  # Day of application, rain and runoff
        (0, 0, 3.2, 0, 100, 35.7, 3),  # Some days after application, no rain
        (
            12,
            0,
            2.85,
            1,
            100,
            46.73,
            8,
        ),  # Some days after application, rain but no runoff
        (
            12,
            1.4,
            2.123,
            1,
            100,
            25.63,
            13,
        ),  # Some days after application, rain and runoff
    ],
)
def test_update_before_and_at_first_rain(
    rainfall: float,
    runoff: float,
    field_size: float,
    rain_events: int,
    full_available_pool: float,
    available_pool: float,
    days_since_application: int,
) -> None:
    """Test that _update_before_and_at_first_rain() chooses correct operations to perform on the available phosphorus
    pool based on day's conditions and temporal counters
    """
    data = SoilData(
        rain_events_after_fertilizer_application=rain_events,
        field_size=field_size,
        full_available_phosphorus_pool=full_available_pool,
        available_phosphorus_pool=available_pool,
        days_since_application=days_since_application,
    )
    fert = Fertilizer(data)

    phos_leached = {
        "runoff_phosphorus": (0.5 * available_pool),
        "absorbed_phosphorus": (0.5 * available_pool),
    }
    with (
        patch.object(fert, "_add_phosphorus_to_soil") as add_phos,
        patch.object(fert, "_absorb_phosphorus_from_available_pool") as absorb,
        patch.object(fert, "_determine_leached_phosphorus", return_value=phos_leached) as leach_phos,
    ):
        fert._update_before_and_at_first_rain(rainfall, runoff, field_size)

    if not rainfall and not days_since_application:
        assert add_phos.call_count == 0
        assert absorb.call_count == 0
        assert leach_phos.call_count == 0
        assert fert.data.available_phosphorus_pool == full_available_pool
    elif not rainfall and days_since_application:
        assert add_phos.call_count == 0
        assert absorb.call_count == 1
        assert leach_phos.call_count == 0
    elif rainfall and not runoff and not days_since_application:
        add_phos.assert_called_once_with(available_pool, field_size)
        assert absorb.call_count == 0
        assert leach_phos.call_count == 0
        assert fert.data.available_phosphorus_pool == 0
    elif rainfall and runoff and not days_since_application:
        add_phos.assert_called_once_with(0.5 * available_pool, field_size)
        assert absorb.call_count == 0
        leach_phos.assert_called_once_with(rainfall, runoff, field_size, available_pool)
        assert fert.data.annual_runoff_fertilizer_phosphorus == 0.5 * available_pool
        assert fert.data.available_phosphorus_pool == 0


@pytest.mark.parametrize(
    "recalcitrant_pool,rain_events,rainfall,runoff,field_size",
    [
        (0, 8, 8, 0.5, 1.3),  # No phosphorus in recalcitrant pool
        (20, 5, 0, 0, 3),  # No rainfall
        (25, 2, 13, 0, 1),  # Rainfall, no runoff
        (32, 3, 11, 1.8, 0.8),  # Rainfall and runoff
    ],
)
def test_update_after_first_rain(
    recalcitrant_pool: float,
    rain_events: int,
    rainfall: float,
    runoff: float,
    field_size: float,
) -> None:
    """Test that _update_after_first_rain() correctly removes phosphorus from the recalcitrant pool and correctly calls
    all subroutines.
    """
    data = SoilData(
        recalcitrant_phosphorus_pool=recalcitrant_pool,
        field_size=field_size,
        rain_events_after_fertilizer_application=rain_events,
    )
    fert = Fertilizer(data)

    phos_leached = {
        "runoff_phosphorus": (0.5 * (recalcitrant_pool * fert.data.solubilizing_factor)),
        "absorbed_phosphorus": (0.5 * (recalcitrant_pool * fert.data.solubilizing_factor)),
    }

    with (
        patch.object(fert, "_add_phosphorus_to_soil") as add_phos,
        patch.object(fert, "_determine_leached_phosphorus", return_value=phos_leached) as leach_phos,
    ):
        fert._update_after_first_rain(rainfall, runoff, field_size)

    expected_absorbed_phos = recalcitrant_pool * fert.data.solubilizing_factor
    if not rainfall:
        assert add_phos.call_count == 0
        assert leach_phos.call_count == 0
        assert fert.data.recalcitrant_phosphorus_pool == recalcitrant_pool
    elif rainfall and not runoff:
        add_phos.assert_called_once_with(expected_absorbed_phos, field_size)
        assert leach_phos.call_count == 0
        assert fert.data.recalcitrant_phosphorus_pool == (recalcitrant_pool - expected_absorbed_phos)
    else:
        add_phos.assert_called_once_with(0.5 * expected_absorbed_phos, field_size)
        leach_phos.assert_called_once_with(rainfall, runoff, field_size, recalcitrant_pool)
        assert fert.data.recalcitrant_phosphorus_pool == (recalcitrant_pool - expected_absorbed_phos)


# --- Top-level routine tests ---
@pytest.mark.parametrize(
    "available_pool,full_available_pool,recalcitrant_pool,rain_events,days_since_application," "added_phosphorus",
    [
        (35.495, 80, 28.4, 0, 4, 75),
        (0, 70, 17.8, 1, 5, 60),
        (0, 60, 12.394, 3, 8, 35),
        (67.193, 100, 28.39, 0, 5, 0),  # No phosphorus added
    ],
)
def test_add_fertilizer_phosphorus(
    available_pool: float,
    full_available_pool: float,
    recalcitrant_pool: float,
    rain_events: int,
    days_since_application: int,
    added_phosphorus: float,
) -> None:
    """Tests that when a new application of phosphorus is applied, it correctly adds to existing pools and resets the
    temporal counters.
    """
    data = SoilData(
        available_phosphorus_pool=available_pool,
        full_available_phosphorus_pool=full_available_pool,
        recalcitrant_phosphorus_pool=recalcitrant_pool,
        field_size=1.0,
        rain_events_after_fertilizer_application=rain_events,
        days_since_application=days_since_application,
    )
    fert = Fertilizer(data)

    fert.add_fertilizer_phosphorus(added_phosphorus)

    if not added_phosphorus:
        assert fert.data.available_phosphorus_pool == available_pool
        assert fert.data.full_available_phosphorus_pool == full_available_pool
        assert fert.data.recalcitrant_phosphorus_pool == recalcitrant_pool
        assert fert.data.days_since_application == days_since_application
        assert fert.data.rain_events_after_fertilizer_application == rain_events
    else:
        assert fert.data.available_phosphorus_pool == (0.75 * added_phosphorus + available_pool)
        assert fert.data.full_available_phosphorus_pool == fert.data.available_phosphorus_pool
        assert fert.data.recalcitrant_phosphorus_pool == (0.25 * added_phosphorus + recalcitrant_pool)
        assert fert.data.days_since_application == 0
        assert fert.data.rain_events_after_fertilizer_application == 0


@pytest.mark.parametrize(
    "rain_events,days_since_application,rainfall,runoff,field_size",
    [
        (0, 0, 0, 0, 3),  # No rainfall, day of application
        (0, 0, 11, 1.8, 1.5),  # First rainfall, day of application
        (3, 7, 0, 0, 2.3),  # No rainfall, no rain events, after day of application
        (0, 5, 13, 0, 4),  # First rainfall, after day of application
        (2, 3, 17, 4, 1.8),  # Not first rainfall, after day of application
        (3, 8, 0, 0, 2.1),  # No rainfall, some rain events, after day of application
    ],
)
def test_do_fertilizer_phosphorus_operations(
    rain_events: int,
    days_since_application: int,
    rainfall: float,
    runoff: float,
    field_size: float,
) -> None:
    """Tests that correct action is taken on fertilizer phosphorus in the system, and that temporal counters are
    incremented correctly.
    """
    data = SoilData(
        rain_events_after_fertilizer_application=rain_events,
        days_since_application=days_since_application,
        field_size=field_size,
    )
    fert = Fertilizer(data)

    fert._update_before_and_at_first_rain = MagicMock()
    fert._update_after_first_rain = MagicMock()

    fert.do_fertilizer_phosphorus_operations(rainfall, runoff, field_size)

    assert fert.data.days_since_application == days_since_application + 1
    if rainfall:
        assert fert.data.rain_events_after_fertilizer_application == rain_events + 1
        rain_events += 1
    if rain_events == 0 or (rainfall and rain_events == 1):
        fert._update_before_and_at_first_rain.assert_called_with(rainfall, runoff, field_size)
        fert._update_after_first_rain.assert_not_called()
    elif rain_events >= 2:
        fert._update_before_and_at_first_rain.assert_not_called()
        fert._update_after_first_rain.assert_called_with(rainfall, runoff, field_size)
