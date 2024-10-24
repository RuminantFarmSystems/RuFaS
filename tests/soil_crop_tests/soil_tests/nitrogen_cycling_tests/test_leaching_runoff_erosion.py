from math import exp, log
from unittest.mock import MagicMock, call, patch

import pytest

from RUFAS.routines.field.soil.layer_data import LayerData
from RUFAS.routines.field.soil.nitrogen_cycling.leaching_runoff_erosion import (
    ACTIVE_ORGANIC_NITROGEN_PERCOLATION_COEFFICIENT,
    AMMONIUM_PERCOLATION_COEFFICIENT,
    AMMONIUM_RUNOFF_COEFFICIENT,
    NITRATE_PERCOLATION_COEFFICIENT,
    NITRATE_RUNOFF_COEFFICIENT,
    LeachingRunoffErosion,
)
from RUFAS.routines.field.soil.soil_data import SoilData


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
    "nitrogen,water,coefficient,bulk_density,thickness,field_size,expected",
    [
        (35, 10.33, 1.8, 1.2, 20.0, 1.3, 2.231),
        (14.5, 6.75, 1.22, 1.9, 150.0, 2.9, 0.988),
        (3.5, 8.332, 0.005, 1.1, 70.0, 3.5, 0.005),
    ],
)
def test_calculate_nitrogen_removed_by_water(
    nitrogen: float,
    water: float,
    coefficient: float,
    bulk_density: float,
    thickness: float,
    field_size: float,
    expected: float,
) -> None:
    """Tests that the correct amount of nitrogen is determined to be removed from a soil layer."""
    n_concentration = 12.0

    with (patch.object(LayerData, "determine_soil_nutrient_concentration", return_value=n_concentration) as conc,):
        actual = LeachingRunoffErosion._calculate_nitrogen_removed_by_water(
            nitrogen, water, coefficient, bulk_density, thickness, field_size
        )

        assert actual == pytest.approx(expected, abs=1e-3)
        conc.assert_called_once_with(nitrogen, bulk_density, thickness, field_size)


@pytest.mark.parametrize(
    "nitrates,ammonium,fresh,active,stable,field_size",
    [
        (78.1994, 66.391, 12.31, 16.594, 18.192, 1.8),
        (75.6, 70.8, 3.22, 10.33, 14.5, 2.3),
    ],
)
def test_erode_nitrogen(
    nitrates: float,
    ammonium: float,
    fresh: float,
    active: float,
    stable: float,
    field_size: float,
) -> None:
    """Tests that nitrogen is properly eroded from the surface of the field."""
    layer = LayerData(top_depth=0, bottom_depth=20, field_size=field_size, bulk_density=1.6)
    layer.nitrate_content = nitrates
    layer.ammonium_content = ammonium
    layer.active_organic_nitrogen_content = active
    layer.stable_organic_nitrogen_content = stable
    layer.fresh_organic_nitrogen_content = fresh
    layer.water_content = 5.6
    runoff = 2.1
    data = SoilData(
        field_size=field_size,
        soil_layers=[layer],
        accumulated_runoff=runoff,
        eroded_sediment=0.92,
    )
    incorp = LeachingRunoffErosion(data)

    incorp._calculate_inorganic_nitrogen_loss = MagicMock(return_value=45)
    incorp._calculate_eroded_organic_nitrogen = MagicMock(return_value=3)

    inorganic_loss_calls = [
        call(
            nitrates,
            runoff,
            NITRATE_RUNOFF_COEFFICIENT,
            layer.bulk_density,
            layer.layer_thickness,
            field_size,
        ),
        call(
            ammonium,
            runoff,
            AMMONIUM_RUNOFF_COEFFICIENT,
            layer.bulk_density,
            layer.layer_thickness,
            field_size,
        ),
    ]
    eroded_organic_nitrogen_calls = [
        call(fresh, 1.6, 20, field_size, 0.92),
        call(stable, 1.6, 20, field_size, 0.92),
        call(active, 1.6, 20, field_size, 0.92),
    ]
    with (
        patch.object(incorp, "_calculate_nitrogen_removed_by_water", return_value=45) as calc_inorganic_loss,
        patch.object(incorp, "_calculate_eroded_organic_nitrogen", return_value=3) as calc_eroded_loss,
    ):
        incorp._erode_nitrogen(field_size)

        calc_inorganic_loss.assert_has_calls(inorganic_loss_calls)
        calc_eroded_loss.assert_has_calls(eroded_organic_nitrogen_calls)
        assert incorp.data.soil_layers[0].nitrate_content == nitrates - 45
        assert incorp.data.annual_runoff_nitrates_total == 45 * field_size
        assert incorp.data.soil_layers[0].ammonium_content == ammonium - 45
        assert incorp.data.annual_runoff_ammonium_total == 45 * field_size
        assert incorp.data.soil_layers[0].fresh_organic_nitrogen_content == fresh - 3
        assert incorp.data.annual_eroded_fresh_organic_nitrogen_total == 3 * field_size
        assert incorp.data.soil_layers[0].stable_organic_nitrogen_content == stable - 3
        assert incorp.data.annual_eroded_stable_organic_nitrogen_total == 3 * field_size
        assert incorp.data.soil_layers[0].active_organic_nitrogen_content == active - 3
        assert incorp.data.annual_eroded_active_organic_nitrogen_total == 3 * field_size


def test_leach_nitrogen() -> None:
    """Tests that nitrogen is properly removed from a layer and percolated to the next during the leaching process."""
    field_size = 2.0
    data = SoilData(field_size=field_size)
    incorp = LeachingRunoffErosion(data)

    incorp.data.set_vectorized_layer_attribute("nitrate_content", [40] * 4)
    incorp.data.set_vectorized_layer_attribute("ammonium_content", [35] * 4)
    incorp.data.set_vectorized_layer_attribute("active_organic_nitrogen_content", [15] * 4)
    incorp.data.set_vectorized_layer_attribute("percolated_water", [3.5, 0, 3.5, 3.5])

    expected_nitrogen_removed_calls = []
    for index in [0, 2, 3]:
        layer = incorp.data.soil_layers[index]
        new_calls = [
            call(
                40,
                3.5,
                NITRATE_PERCOLATION_COEFFICIENT,
                layer.bulk_density,
                layer.layer_thickness,
                field_size,
            ),
            call(
                35,
                3.5,
                AMMONIUM_PERCOLATION_COEFFICIENT,
                layer.bulk_density,
                layer.layer_thickness,
                field_size,
            ),
            call(
                15,
                3.5,
                ACTIVE_ORGANIC_NITROGEN_PERCOLATION_COEFFICIENT,
                layer.bulk_density,
                layer.layer_thickness,
                field_size,
            ),
        ]
        expected_nitrogen_removed_calls.extend(new_calls)

    LeachingRunoffErosion._calculate_nitrogen_removed_by_water = MagicMock(return_value=10)

    with patch.object(incorp, "_calculate_nitrogen_removed_by_water", return_value=10) as leach_n:
        incorp._leach_nitrogen(field_size)

        leach_n.assert_has_calls(expected_nitrogen_removed_calls)
        soil_layers = incorp.data.soil_layers + [incorp.data.vadose_zone_layer]
        for index in range(len(soil_layers)):
            if index == 0 or index == 2:
                assert soil_layers[index].nitrate_content == 30
                assert soil_layers[index].ammonium_content == 25
                assert soil_layers[index].active_organic_nitrogen_content == 5
            elif index == 1:
                assert soil_layers[index].nitrate_content == 50
                assert soil_layers[index].ammonium_content == 45
                assert soil_layers[index].active_organic_nitrogen_content == 25
            elif index == 3:
                assert soil_layers[index].nitrate_content == 40
                assert soil_layers[index].ammonium_content == 35
                assert soil_layers[index].active_organic_nitrogen_content == 15
            else:
                assert soil_layers[index].nitrate_content == 10
                assert soil_layers[index].ammonium_content == 10
                assert soil_layers[index].active_organic_nitrogen_content == 10


def test_leach_and_erode_nitrogen() -> None:
    """Tests that the top level routine of this module calls the right helper methods."""
    field_size = 2.3
    data = SoilData(field_size=2.3)
    incorp = LeachingRunoffErosion(data)

    incorp._erode_nitrogen = MagicMock()
    incorp._leach_nitrogen = MagicMock()

    incorp.leach_runoff_and_erode_nitrogen(field_size)

    incorp._erode_nitrogen.assert_called_once_with(field_size)
    incorp._leach_nitrogen.assert_called_once_with(field_size)
