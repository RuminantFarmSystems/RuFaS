import pytest

from SC_redesign.Crop_and_Soil.soil.carbon_cycling.residue_partition import ResiduePartition


@pytest.mark.parametrize("plant_residue_lignin_composition, rainfall", [
    (3, 2),  # lower values
    (50, 6),  # higher value
    (1.8, 1.1),  # arbitrary values
])
def test_determine_plant_residue_lignin_composition(plant_residue_lignin_composition: float, rainfall: float) -> None:
    """Tests that the plant residue lignin composition will be updated correctly as the equation with given rainfall"""
    expected = plant_residue_lignin_composition + 0.12 * rainfall * 0.1
    assert expected == ResiduePartition._determine_plant_residue_lignin_composition(plant_residue_lignin_composition,
                                                                                    rainfall)


@pytest.mark.parametrize("plant_residue_lignin_composition, nitrogen_fraction_plant_residue", [
    (3, 0.4),  # default value
    (50, 0.5),  # higher value
    (1.8, 1.1),  # arbitrary values
    (2.2, 0)  # zeros
])
def test_determine_metabolic_plant_residue_ratio(plant_residue_lignin_composition: float,
                                                 nitrogen_fraction_plant_residue) -> None:
    """Test that metabolic plant residue ration is correctly determined under current nitrogen_fraction_plant_residue
    """
    if 0 < nitrogen_fraction_plant_residue < 1.0:
        expected = (plant_residue_lignin_composition / 100) / nitrogen_fraction_plant_residue
        assert expected == ResiduePartition._determine_metabolic_plant_residue_ratio(plant_residue_lignin_composition,
                                                                                     nitrogen_fraction_plant_residue)
    elif nitrogen_fraction_plant_residue == 0:
        expected = 0
        assert expected == ResiduePartition._determine_metabolic_plant_residue_ratio(plant_residue_lignin_composition,
                                                                                     nitrogen_fraction_plant_residue)
    else:
        # case of invalid input
        with pytest.raises(ValueError) as e:
            ResiduePartition._determine_metabolic_plant_residue_ratio(plant_residue_lignin_composition,
                                                                      nitrogen_fraction_plant_residue)
        expected = "Expected nitrogen_fraction_plant_residue be between 0.0-1.0, received " + \
                   str(nitrogen_fraction_plant_residue)
        assert expected == str(e.value)


@pytest.mark.parametrize("plant_lignin_nitrogen_ratio", [
    7,  # lower values
    56,  # higher values
    35.8,  # arbitrary
])
def test_determine_plant_residue_metabolic_fraction(plant_lignin_nitrogen_ratio: float) -> None:
    """Tests to see if the fraction of plant residue that is metabolic is calculated correctly"""
    expected = 0.85 - 0.18 * plant_lignin_nitrogen_ratio
    assert expected == ResiduePartition._determine_plant_residue_metabolic_fraction(plant_lignin_nitrogen_ratio)


@pytest.mark.parametrize("plant_metabolic_carbon_amount, plant_residue_metabolic_fraction,"
                         "plant_dry_matter_residue_amount, plant_metabolic_active_carbon_usage, "
                         "plant_metabolic_to_soil_carbon_amount", [
                             (3, 8, 7, 1, 2),
                             (60, 64, 85, 40, 30),
                             (1.8, 1.1, 3.2, 0.8, 0.7),
                         ])
def test_determine_plant_metabolic_carbon_amount(plant_metabolic_carbon_amount: float,
                                                 plant_residue_metabolic_fraction: float,
                                                 plant_dry_matter_residue_amount: float,
                                                 plant_metabolic_active_carbon_usage: float,
                                                 plant_metabolic_to_soil_carbon_amount: float) -> None:
    """Tests that the updated plant metabolic carbon amount is calculated correctly"""
    expected = plant_metabolic_carbon_amount + plant_dry_matter_residue_amount \
        * plant_residue_metabolic_fraction - \
        (plant_metabolic_active_carbon_usage + plant_metabolic_to_soil_carbon_amount)
    assert expected == ResiduePartition._determine_plant_metabolic_carbon_amount(plant_metabolic_carbon_amount,
                                                                                 plant_residue_metabolic_fraction,
                                                                                 plant_dry_matter_residue_amount,
                                                                                 plant_metabolic_active_carbon_usage,
                                                                                 plant_metabolic_to_soil_carbon_amount)


@pytest.mark.parametrize("decomposition_moisture_effect, decomposition_temperature_effect, "
                         "plant_metabolic_carbon_amount", [
                             (3, 8, 7),
                             (60, 64, 85),
                             (1.8, 1.1, 3.27),
                         ])
def test_determine_plant_metabolic_active_carbon_usage(decomposition_moisture_effect: float,
                                                       decomposition_temperature_effect: float,
                                                       plant_metabolic_carbon_amount: float) -> None:
    """Tests that plant metabolic active carbon usage amount was calculated correctly"""
    metabolic_active_carbon_rate = 0.28
    expected = decomposition_moisture_effect * decomposition_temperature_effect * \
        plant_metabolic_carbon_amount * metabolic_active_carbon_rate
    assert expected == ResiduePartition._determine_plant_metabolic_active_carbon_usage(decomposition_moisture_effect,
                                                                                       decomposition_temperature_effect,
                                                                                       plant_metabolic_carbon_amount)
