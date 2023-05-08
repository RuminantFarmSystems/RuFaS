import pytest
from math import exp, log
from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.leaching_runoff_erosion import LeachingRunoffErosion


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


@pytest.mark.parametrize("nitrogen_concentration, runoff, runoff_extraction_coef", [
    (0, 56, 0.1),
    (51, 0, 0.2),
    (108, 110, 0.3),
    (54.3, 92.4, 0),
    (1, 5, 0.6)
])
def test_determine_nitrate_runoff_amount(nitrogen_concentration: float, runoff: float,
                                         runoff_extraction_coef: float) -> None:
    """Tests that the amount of nitrate runoff for the first layer was calculated correctly"""
    expected = nitrogen_concentration * runoff * runoff_extraction_coef
    assert expected == LeachingRunoffErosion._determine_nitrate_runoff_amount(nitrogen_concentration,
                                                                              runoff,
                                                                              runoff_extraction_coef)


@pytest.mark.parametrize("nitrogen_amount, layer_thickness,bulk_density", [
    (102, 100, 99),
    (0.5, 1.8, 2.3),
    (2, 3, 4),
    (0, 3, 4)
])
def test_determine_nitrogen_erosion_concentration(nitrogen_amount: float,
                                                  layer_thickness: float,
                                                  bulk_density: float) -> None:
    """Tests that the soil nitrogen concentrations for the Fresh, Active, and Stable pools are calculated correctly"""
    expected = (100 * nitrogen_amount) / (bulk_density * layer_thickness)
    assert expected == LeachingRunoffErosion._determine_nitrogen_erosion_concentration(nitrogen_amount,
                                                                                       layer_thickness,
                                                                                       bulk_density)


@pytest.mark.parametrize("daily_soil_lost", [
    5,  # lower values
    100,  # higher values
    35.8  # arbitrary
])
def test_determine_enrichment_ratio(daily_soil_lost: float) -> None:
    """Tests that the enrichment ratio was calculated correctly"""
    expected = exp(1.21 - 0.16 * log(daily_soil_lost * 1000))
    assert expected == LeachingRunoffErosion._determine_enrichment_ratio(daily_soil_lost)


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
def test_determine_leached_nitrogen(nitrogen: float, percolation: float, leaching_coefficient: float) -> float:
    """Tests that the amount of nitrogen calculated to percolate out of the current layer is calculated correctly."""
    observed = LeachingRunoffErosion._determine_leached_nitrogen(nitrogen, percolation, leaching_coefficient)
    expected = (nitrogen / leaching_coefficient) * percolation
    assert observed == expected
