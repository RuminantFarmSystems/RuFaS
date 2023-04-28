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


@pytest.mark.parametrize("nitrate_concentration, runoff", [
    (0, 56),
    (51, 0),
    (108, 110),
    (54.3, 92.4),
    (1, 5)
])
def test_determine_NO3_runoff_amount(nitrate_concentration: float, runoff: float) -> None:
    """Tests that the amount of NO3 runoff for the first layer was calculated correctly"""
    runoff_extraction_coef = 0.1
    expected = nitrate_concentration*runoff*runoff_extraction_coef
    assert expected == LeachingRunoffErosion._determine_nitrate_runoff_amount(nitrate_concentration, runoff)


@pytest.mark.parametrize("ammonium_concentration, runoff", [
    (0, 56),
    (51, 0),
    (108, 110),
    (54.3, 92.4),
    (1, 5)
])
def test_determine_ammonium_runoff_amount(ammonium_concentration: float, runoff: float) -> None:
    """Tests that the amount of NH4 runoff for the first layer was calculated correctly"""
    runoff_extraction_coef = 1
    expected = ammonium_concentration * runoff * runoff_extraction_coef
    assert expected == LeachingRunoffErosion._determine_ammonium_runoff_amount(ammonium_concentration, runoff)


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
