import pytest
from math import exp, log
from unittest.mock import MagicMock, call, PropertyMock, patch

from RUFAS.routines.field.soil.nitrogen_cycling.leaching_runoff_erosion import LeachingRunoffErosion
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.layer_data import LayerData


@pytest.mark.parametrize("soluble_nitrogen_amount, soil_water_runoff_sum,saturation_content", [
    (102, 100, 99),
    (0.5, 1.8, 2.3),
    (2, 3, 4)
])
def test_determine_nitrogen_concentration(soluble_nitrogen_amount: float,
                                          soil_water_runoff_sum: float,
                                          saturation_content: float) -> None:
    """Tests that the concentration of the inorganic pools NO3/NH4 in the top soil layer was calculated correctly"""
    expected = soluble_nitrogen_amount * (1 - (exp(-soil_water_runoff_sum/saturation_content))/soil_water_runoff_sum)
    assert expected == LeachingRunoffErosion._determine_nitrogen_concentration(soluble_nitrogen_amount,
                                                                               soil_water_runoff_sum,
                                                                               saturation_content)


@pytest.mark.parametrize("nitrogen_concentration,runoff,runoff_extraction_coef", [
    (0, 56, 0.1),
    (51, 0, 0.2),
    (108, 110, 0.3),
    (54.3, 92.4, 0),
    (1, 5, 0.6)
])
def test_determine_nitrogen_runoff_amount(nitrogen_concentration: float, runoff: float,
                                          runoff_extraction_coef: float) -> None:
    """Tests that the amount of nitrogen runoff for the first layer was calculated correctly"""
    expected = nitrogen_concentration * runoff * runoff_extraction_coef
    assert expected == LeachingRunoffErosion._determine_nitrogen_runoff_amount(nitrogen_concentration,
                                                                               runoff,
                                                                               runoff_extraction_coef)


@pytest.mark.parametrize("nitrogen_content,water_content,saturation_content,runoff,extraction_coefficient", [
    (67.8, 5.66, 8.99, 3.22, 0.1),
    (35.445, 7.81, 6.54, 2.331, 1.0),
    (45.1948, 4.51, 9.44, 1.334, 0.1),
    (13.495, 5.03, 6.7, 1.4, 1.0)
])
def test_calculate_inorganic_nitrogen_loss(nitrogen_content: float, water_content: float, saturation_content: float,
                                           runoff: float, extraction_coefficient: float) -> None:
    """Tests that the correct amount of inorganic nitrogen is lost to runoff."""
    LeachingRunoffErosion._determine_nitrogen_concentration = MagicMock(return_value=30)
    LeachingRunoffErosion._determine_nitrogen_runoff_amount = MagicMock(return_value=25)

    observed = LeachingRunoffErosion._calculate_inorganic_nitrogen_loss(nitrogen_content, water_content,
                                                                        saturation_content, runoff,
                                                                        extraction_coefficient)
    expected_water_sum = water_content + runoff
    expected_nitrogen_lost = min(nitrogen_content, 25)

    LeachingRunoffErosion._determine_nitrogen_concentration.assert_called_once_with(nitrogen_content,
                                                                                    expected_water_sum,
                                                                                    saturation_content)
    LeachingRunoffErosion._determine_nitrogen_runoff_amount.assert_called_once_with(30, runoff, extraction_coefficient)
    assert observed == expected_nitrogen_lost


@pytest.mark.parametrize("nitrogen,soil_lost,enrichment_ratio", [
    (56, 1.2, 0.98),
    (34.556, 0.556, 1.022),
    (90.0294, 2.334, 1.035)
])
def test_determine_erosion_nitrogen_loss_content(nitrogen: float, soil_lost: float, enrichment_ratio: float) -> None:
    """Tests that the mass of nitrogen lost to erosion is calculated correctly."""
    observed = LeachingRunoffErosion._determine_erosion_nitrogen_loss_content(nitrogen, soil_lost, enrichment_ratio)
    expected = nitrogen * soil_lost * enrichment_ratio * 0.001
    assert pytest.approx(observed) == expected


@pytest.mark.parametrize("daily_soil_lost", [
    5,  # lower values
    100,  # higher values
    35.8  # arbitrary
])
def test_determine_enrichment_ratio(daily_soil_lost: float) -> None:
    """Tests that the enrichment ratio was calculated correctly"""
    expected = exp(1.21 - 0.16 * log(daily_soil_lost * 1000))
    assert expected == LeachingRunoffErosion._determine_enrichment_ratio(daily_soil_lost)


@pytest.mark.parametrize("nitrogen,density,depth,area,sediment", [
    (13.44, 1.82, 20, 2.11, 0.8),
    (44.996, 0.98, 25, 1.234, 0.44),
    (66.101, 1.334, 17, 0.85, 0.55),
    (5.223, 1.4, 31, 2.5, 0.76)
])
def test_calculate_eroded_organic_nitrogen(nitrogen: float, density: float, depth: float, area: float,
                                           sediment: float) -> float:
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


@pytest.mark.parametrize("nitrogen,field_capacity,percolation", [
    (33.41, 6.88, 1.44),
    (21.99, 9.664, 4.556),
    (66.887, 12.331, 9.009)
])
def test_determine_nitrogen_percolation_water_concentration(nitrogen: float, field_capacity: float,
                                                            percolation: float) -> None:
    """Tests that the correct concentration of nitrogen in soil water is determined before leaching."""
    observed = LeachingRunoffErosion._determine_nitrogen_percolation_water_concentration(nitrogen, field_capacity,
                                                                                         percolation)
    expected = nitrogen / (field_capacity + percolation)
    assert observed == expected


@pytest.mark.parametrize("active_nitrogen_concentration", [
    12.4496,
    10.4058,
    0.0,
    56.681
])
def test_adjust_active_organic_nitrogen_concentration(active_nitrogen_concentration: float) -> None:
    """Tests that the active organic nitrogen concentration is correctly adjusted."""
    observed = LeachingRunoffErosion._adjust_active_organic_nitrogen_concentration(active_nitrogen_concentration)
    expected = active_nitrogen_concentration / 50
    assert observed == expected


@pytest.mark.parametrize("nitrogen,percolation,leaching_coefficient", [
    (15.33, 1.22, 1.0),
    (22.683, 5.694, 2.5),
    (66.74, 8.5576, 1.0),
    (4.556, 0.671, 2.5)
])
def test_determine_leached_nitrogen(nitrogen: float, percolation: float, leaching_coefficient: float) -> None:
    """Tests that the amount of nitrogen calculated to percolate out of the current layer is calculated correctly."""
    observed = LeachingRunoffErosion._determine_leached_nitrogen(nitrogen, percolation, leaching_coefficient)
    expected = (nitrogen / leaching_coefficient) * percolation
    assert observed == expected


@pytest.mark.parametrize("nitrogen_content,field_capacity,percolation,extraction_coefficient,is_active", [
    (35, 10.33, 3.11, 1.0, False),
    (14.5, 6.75, 1.22, 2.5, True),
    (22.45, 8.332, 2.45, 2.5, False)
])
def test_calculate_nitrogen_lost_to_leaching(nitrogen_content: float, field_capacity: float, percolation: float,
                                             extraction_coefficient: float, is_active: bool) -> None:
    """Tests that the correct amount of nitrogen is determined to be leached out of a soil layer."""
    LeachingRunoffErosion._determine_nitrogen_percolation_water_concentration = MagicMock(return_value=46)
    LeachingRunoffErosion._adjust_active_organic_nitrogen_concentration = MagicMock(return_value=30)
    LeachingRunoffErosion._determine_leached_nitrogen = MagicMock(return_value=18)

    observed = LeachingRunoffErosion._calculate_nitrogen_lost_to_leaching(nitrogen_content, field_capacity, percolation,
                                                                          extraction_coefficient, is_active)

    LeachingRunoffErosion._determine_nitrogen_percolation_water_concentration.assert_called_once_with(nitrogen_content,
                                                                                                      field_capacity,
                                                                                                      percolation)
    if is_active:
        LeachingRunoffErosion._adjust_active_organic_nitrogen_concentration.assert_called_once_with(46)
        LeachingRunoffErosion._determine_leached_nitrogen.assert_called_once_with(30, percolation,
                                                                                  extraction_coefficient)
    else:
        LeachingRunoffErosion._adjust_active_organic_nitrogen_concentration.assert_not_called()
        LeachingRunoffErosion._determine_leached_nitrogen.assert_called_once_with(46, percolation,
                                                                                  extraction_coefficient)
    assert observed == min(nitrogen_content, 18)


@pytest.mark.parametrize("nitrates,ammonium,fresh,active,stable,field_size", [
    (78.1994, 66.391, 12.31, 16.594, 18.192, 1.8),
    (75.6, 70.8, 3.22, 10.33, 14.5, 2.3)
])
def test_erode_nitrogen(nitrates: float, ammonium: float, fresh: float, active: float, stable: float,
                        field_size: float) -> None:
    """Tests that nitrogen is properly eroded from the surface of the field."""
    with patch("RUFAS.routines.field.soil.layer_data.LayerData.saturation_content", new_callable=PropertyMock,
               return_value=8.8):
        layer = LayerData(top_depth=0, bottom_depth=20, field_size=field_size, bulk_density=1.6)
        layer.nitrate_content = nitrates
        layer.ammonium_content = ammonium
        layer.active_organic_nitrogen_content = active
        layer.stable_organic_nitrogen_content = stable
        layer.fresh_organic_nitrogen_content = fresh
        layer.water_content = 5.6
        data = SoilData(field_size=field_size, soil_layers=[layer], accumulated_runoff=2.1, eroded_sediment=0.92)
        incorp = LeachingRunoffErosion(data)

        incorp._calculate_inorganic_nitrogen_loss = MagicMock(return_value=45)
        incorp._calculate_eroded_organic_nitrogen = MagicMock(return_value=3)

        inorganic_loss_calls = [call(nitrates, 5.6, 8.8, 2.1, 0.1), call(ammonium, 5.6, 8.8, 2.1, 1.0)]
        eroded_organic_nitrogen_calls = [call(fresh, 1.6, 20, field_size, 0.92),
                                         call(stable, 1.6, 20, field_size, 0.92),
                                         call(active, 1.6, 20, field_size, 0.92)]

        incorp._erode_nitrogen(field_size)

        incorp._calculate_inorganic_nitrogen_loss.assert_has_calls(inorganic_loss_calls)
        incorp._calculate_eroded_organic_nitrogen.assert_has_calls(eroded_organic_nitrogen_calls)
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
    with patch("RUFAS.routines.field.soil.layer_data.LayerData.field_capacity_content", new_callable=PropertyMock,
               return_value=6.8):
        data = SoilData(field_size=2.0)
        incorp = LeachingRunoffErosion(data)

        incorp.data.set_vectorized_layer_attribute("nitrate_content", [40] * 4)
        incorp.data.set_vectorized_layer_attribute("ammonium_content", [35] * 4)
        incorp.data.set_vectorized_layer_attribute("active_organic_nitrogen_content", [15] * 4)
        incorp.data.set_vectorized_layer_attribute("percolated_water", [3.5, 0, 3.5, 3.5])

        LeachingRunoffErosion._calculate_nitrogen_lost_to_leaching = MagicMock(return_value=10)

        incorp._leach_nitrogen()

        top_layer_nitrogen_lost_calls = [call(40, 6.8, 3.5, 1.0, False), call(35, 6.8, 3.5, 1.0, False),
                                         call(15, 6.8, 3.5, 1.0, True)]
        lower_layer_nitrogen_lost_calls = [call(40, 6.8, 3.5, 2.5, False), call(35, 6.8, 3.5, 1.0, False),
                                           call(15, 6.8, 3.5, 1.0, True)] * 2
        all_nitrogen_lost_calls = top_layer_nitrogen_lost_calls + lower_layer_nitrogen_lost_calls
        LeachingRunoffErosion._calculate_nitrogen_lost_to_leaching.assert_has_calls(all_nitrogen_lost_calls)
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
    incorp._leach_nitrogen.assert_called_once()
