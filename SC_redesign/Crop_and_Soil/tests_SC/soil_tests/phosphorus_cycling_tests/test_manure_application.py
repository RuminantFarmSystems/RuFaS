import pytest

from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure_application import ManureApplication


# ---- Static method tests
@pytest.mark.parametrize("animal_type, expected_value", [
    ("CATTLE", 0.50),
    ("SWINE", 0.35),
    ("POULTRY", 0.20),
    (None, 0.45),
])
def test_determine_water_extractable_inorganic_phosphorus_fraction_by_animal(animal_type: str,
                                                                             expected_value: float) -> None:
    """Test that the right fraction of water extractable inorganic phosphorus is returned for the passed animal."""
    observe = ManureApplication._determine_water_extractable_inorganic_phosphorus_fraction_by_animal(animal_type)
    assert observe == expected_value


@pytest.mark.parametrize("animal_type", [
    "",
    "Crap",
    "Cattle",
])
def test_error_determine_water_extractable_inorganic_phosphorus_fraction_by_animal(animal_type: str) -> None:
    """Test that errors are properly raised when an invalid animal type is passed."""
    with pytest.raises(ValueError) as e:
        ManureApplication._determine_water_extractable_inorganic_phosphorus_fraction_by_animal(animal_type)
    assert str(e.value) == f"Expected manure source animal to be 'CATTLE', 'SWINE', 'POULTRY', or None, received: " \
                           f"'{animal_type}'."
