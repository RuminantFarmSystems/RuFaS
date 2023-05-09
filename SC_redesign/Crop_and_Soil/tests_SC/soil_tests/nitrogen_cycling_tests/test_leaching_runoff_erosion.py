import pytest
from math import exp, log
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.leaching_runoff_erosion import LeachingRunoffErosion
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


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
    (45.1948, 4.51, 9.44, 1.334, 0.1)
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

    LeachingRunoffErosion._determine_nitrogen_concentration.assert_called_once_with(nitrogen_content,
                                                                                    expected_water_sum,
                                                                                    saturation_content)
    LeachingRunoffErosion._determine_nitrogen_runoff_amount.assert_called_once_with(30, runoff, extraction_coefficient)
    assert observed == 25


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
