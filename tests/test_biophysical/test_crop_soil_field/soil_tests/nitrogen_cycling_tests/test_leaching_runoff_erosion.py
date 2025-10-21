from math import exp, log
from unittest.mock import MagicMock, call, patch

import pytest

from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.nitrogen_cycling.leaching_runoff_erosion import (
    AMMONIUM_RUNOFF_COEFFICIENT,
    NITRATE_RUNOFF_COEFFICIENT,
    LeachingRunoffErosion,
)
from RUFAS.biophysical.field.soil.soil_data import SoilData


@pytest.mark.parametrize(
    "nitrogen,soil_lost,enrichment_ratio",
    [(56, 1.2, 0.98), (34.556, 0.556, 1.022), (90.0294, 2.334, 1.035)],
)
def test_determine_erosion_nitrogen_loss_content(nitrogen: float, soil_lost: float, enrichment_ratio: float) -> None:
    """Tests that the mass of nitrogen lost to erosion is calculated correctly."""
    observed = LeachingRunoffErosion._determine_erosion_nitrogen_loss_content(nitrogen, soil_lost, enrichment_ratio)
    expected = nitrogen * soil_lost * enrichment_ratio * 0.001
    assert pytest.approx(observed) == expected


@pytest.mark.parametrize("daily_soil_lost", [5, 100, 35.8])  # lower values  # higher values  # arbitrary
def test_determine_enrichment_ratio(daily_soil_lost: float) -> None:
    """Tests that the enrichment ratio was calculated correctly"""
    expected = exp(1.21 - 0.16 * log(daily_soil_lost * 1000))
    assert expected == LeachingRunoffErosion._determine_enrichment_ratio(daily_soil_lost)


@pytest.mark.parametrize(
    "nitrogen,density,depth,area,sediment",
    [
        (13.44, 1.82, 20, 2.11, 0.8),
        (44.996, 0.98, 25, 1.234, 0.44),
        (66.101, 1.334, 17, 0.85, 0.55),
        (5.223, 1.4, 31, 2.5, 0.76),
    ],
)
def test_calculate_eroded_organic_nitrogen(
    nitrogen: float, density: float, depth: float, area: float, sediment: float
) -> None:
    """Tests that the amount of organic nitrogen lost to eroded sediment is calculated correctly."""
    LayerData.determine_soil_nutrient_concentration = MagicMock(return_value=26)
    LeachingRunoffErosion._determine_enrichment_ratio = MagicMock(return_value=2.5)
    LeachingRunoffErosion._determine_erosion_nitrogen_loss_content = MagicMock(return_value=33)

    observed = LeachingRunoffErosion._calculate_eroded_organic_nitrogen(nitrogen, density, depth, area, sediment)
    expected_sediment_per_ha = sediment / area
    expected_lost_nitrogen = min(nitrogen, 33)

    LayerData.determine_soil_nutrient_concentration.assert_called_once_with(nitrogen, density, depth, area)
    LeachingRunoffErosion._determine_enrichment_ratio.assert_called_once_with(expected_sediment_per_ha)
    LeachingRunoffErosion._determine_erosion_nitrogen_loss_content(26, expected_sediment_per_ha, 2.5)
    assert observed == expected_lost_nitrogen


@pytest.mark.parametrize(
    "nitrogen_content, runoff_water_amount, percolated_water_amount, soil_saturation_point, expected_concentration",
    [
        (100.0, 10.0, 5.0, 50.0, 1.72788),
        (50.0, 0.0, 0.0, 30.0, None),
        (100.0, 1000.0, 1000.0, 100.0, 0.05),
        (100.0, 0.001, 0.001, 50.0, 2.0),
    ],
)
def test_calculate_nitrogen_conc_in_mobile_water(
    nitrogen_content: float,
    runoff_water_amount: float,
    percolated_water_amount: float,
    soil_saturation_point: float,
    expected_concentration: float | None,
) -> None:
    if expected_concentration is None:
        with pytest.raises(ZeroDivisionError):
            LeachingRunoffErosion._calculate_nitrogen_conc_in_mobile_water(
                nitrogen_content=nitrogen_content,
                runoff_water_amount=runoff_water_amount,
                percolated_water_amount=percolated_water_amount,
                soil_saturation_point=soil_saturation_point,
            )
    else:
        result = LeachingRunoffErosion._calculate_nitrogen_conc_in_mobile_water(
            nitrogen_content=nitrogen_content,
            runoff_water_amount=runoff_water_amount,
            percolated_water_amount=percolated_water_amount,
            soil_saturation_point=soil_saturation_point,
        )
        assert result == pytest.approx(expected_concentration, rel=1e-4)


@pytest.mark.parametrize(
    "nitrates, ammonium, fresh, active, stable, field_size",
    [
        (78.1994, 66.391, 12.31, 16.594, 18.192, 1.8),
        (75.6, 70.8, 3.22, 10.33, 14.5, 2.3),
    ],
)
def test_erode_nitrogen_updated(
    nitrates: float,
    ammonium: float,
    fresh: float,
    active: float,
    stable: float,
    field_size: float,
) -> None:
    layer = LayerData(top_depth=0, bottom_depth=20, field_size=field_size, bulk_density=1.6)
    layer.nitrate_content = nitrates
    layer.ammonium_content = ammonium
    layer.fresh_organic_nitrogen_content = fresh
    layer.stable_organic_nitrogen_content = stable
    layer.active_organic_nitrogen_content = active
    layer.percolated_water = 0.0
    runoff = 2.1

    data = SoilData(
        field_size=field_size,
        soil_layers=[layer],
        accumulated_runoff=runoff,
        eroded_sediment=0.92,
    )
    incorp = LeachingRunoffErosion(data)

    conc_return = 45.0
    organic_return = 3.0

    with (
        patch.object(incorp, "_calculate_nitrogen_conc_in_mobile_water", return_value=conc_return) as mock_calc_conc,
        patch.object(incorp, "_calculate_eroded_organic_nitrogen", return_value=organic_return) as mock_calc_org,
    ):
        incorp._erode_nitrogen(field_size)

    expected_conc_calls = [
        call(nitrates, runoff, layer.percolated_water, layer.saturation_content),
        call(ammonium, runoff, layer.percolated_water, layer.saturation_content),
    ]
    assert mock_calc_conc.call_args_list == expected_conc_calls

    expected_org_calls = [
        call(fresh, layer.bulk_density, layer.layer_thickness, field_size, data.eroded_sediment),
        call(stable, layer.bulk_density, layer.layer_thickness, field_size, data.eroded_sediment),
        call(active, layer.bulk_density, layer.layer_thickness, field_size, data.eroded_sediment),
    ]
    assert mock_calc_org.call_args_list == expected_org_calls

    expected_nitrate_loss = NITRATE_RUNOFF_COEFFICIENT * conc_return * runoff
    expected_ammonium_loss = AMMONIUM_RUNOFF_COEFFICIENT * conc_return * runoff

    assert layer.nitrate_content == pytest.approx(nitrates - expected_nitrate_loss)
    assert data.nitrate_runoff == pytest.approx(expected_nitrate_loss)
    assert data.annual_runoff_nitrates_total == pytest.approx(expected_nitrate_loss * field_size)

    assert layer.ammonium_content == pytest.approx(ammonium - expected_ammonium_loss)
    assert data.ammonium_runoff == pytest.approx(expected_ammonium_loss)
    assert data.annual_runoff_ammonium_total == pytest.approx(expected_ammonium_loss * field_size)

    assert layer.fresh_organic_nitrogen_content == pytest.approx(fresh - organic_return)
    assert data.eroded_fresh_organic_nitrogen == pytest.approx(organic_return)
    assert data.annual_eroded_fresh_organic_nitrogen_total == pytest.approx(organic_return * field_size)

    assert layer.stable_organic_nitrogen_content == pytest.approx(stable - organic_return)
    assert data.eroded_stable_organic_nitrogen == pytest.approx(organic_return)
    assert data.annual_eroded_stable_organic_nitrogen_total == pytest.approx(organic_return * field_size)

    assert layer.active_organic_nitrogen_content == pytest.approx(active - organic_return)
    assert data.eroded_active_organic_nitrogen == pytest.approx(organic_return)
    assert data.annual_eroded_active_organic_nitrogen_total == pytest.approx(organic_return * field_size)


def test_leach_nitrogen() -> None:
    """Tests that nitrogen is properly removed from a layer and percolated to the next during the leaching process."""
    field_size = 2.0
    data = SoilData(field_size=field_size)
    incorp = LeachingRunoffErosion(data)

    incorp.data.set_vectorized_layer_attribute("nitrate_content", [40, 40, 40, 40])
    incorp.data.set_vectorized_layer_attribute("ammonium_content", [35, 35, 35, 35])
    incorp.data.set_vectorized_layer_attribute("percolated_water", [3.5, 0, 3.5, 3.5])
    incorp.data.accumulated_runoff = 5.0

    with patch.object(incorp, "_calculate_nitrogen_conc_in_mobile_water", return_value=2.0):
        incorp._leach_nitrogen()

    soil_layers = incorp.data.soil_layers + [incorp.data.vadose_zone_layer]

    assert soil_layers[0].nitrate_content == pytest.approx(33.0)
    assert soil_layers[0].ammonium_content == pytest.approx(28.0)
    assert soil_layers[1].nitrate_content == pytest.approx(47.0)
    assert soil_layers[1].ammonium_content == pytest.approx(42.0)
    assert soil_layers[2].nitrate_content == pytest.approx(33.0)
    assert soil_layers[2].ammonium_content == pytest.approx(28.0)
    assert soil_layers[3].nitrate_content == pytest.approx(40.0)
    assert soil_layers[3].ammonium_content == pytest.approx(35.0)
    assert soil_layers[4].nitrate_content == pytest.approx(7.0)
    assert soil_layers[4].ammonium_content == pytest.approx(7.0)


def test_leach_and_erode_nitrogen() -> None:
    """Tests that the top level routine of this module calls the right helper methods."""
    field_size = 2.3
    data = SoilData(field_size=2.3)
    incorp = LeachingRunoffErosion(data)

    incorp._erode_nitrogen = MagicMock()
    incorp._leach_nitrogen = MagicMock()

    incorp.leach_runoff_and_erode_nitrogen(field_size)

    incorp._erode_nitrogen.assert_called_once_with(field_size)
    incorp._leach_nitrogen.assert_called_once()
