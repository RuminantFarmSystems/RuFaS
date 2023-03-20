import pytest
from unittest.mock import MagicMock, patch

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


@pytest.mark.parametrize("field_size,mass_applied", [
    (3.18, 300),
    (0.65, 10000),
    (2.18, 1000),
])
def test_determine_field_coverage(field_size: float, mass_applied: float) -> None:
    """Tests that the correct fraction of field covered by the new manure application is calculated."""
    observe = ManureApplication._determine_grazing_manure_field_coverage(field_size, mass_applied)
    mass_applied_grams = 1000 * mass_applied
    area_covered = mass_applied_grams * (659 / 250)
    area_covered /= 100000000
    expect = min(1.0, area_covered / field_size)
    assert observe == expect


@pytest.mark.parametrize("mass,dry_content", [
    (300, 0.35),
    (800, 0.445),
    (1200, 0.85),
    (900, 1.0),
])
def test_determine_moisture_factor(mass: float, dry_content: float) -> None:
    """Tests that the correct moisture factor is calculated based the mass applied and amount of water in the
        application."""
    observe = ManureApplication._determine_moisture_factor(mass, dry_content)
    expect = (1 - dry_content) * mass
    assert observe == expect


@pytest.mark.parametrize("mass,dry_content", [
    (500, 0),
    (400, -0.5),
    (600, 1.1),
])
def test_error_determine_moisture_factor(mass: float, dry_content: float) -> None:
    """Tests that correct error is raised when invalid argument is passed."""
    with pytest.raises(ValueError) as e:
        ManureApplication._determine_moisture_factor(mass, dry_content)
    assert str(e.value) == f"Dry matter content must be in the range (0.0, 1.0], received: '{dry_content}'."


@pytest.mark.parametrize("old_mass,old_moisture,old_coverage,app_mass,app_dry_content,app_coverage", [
    (1100, 0.4, 0.7, 900, 0.8, 0.88),
    (400, 0.71, 0.93, 3500, 0.85, 0.95),
    (2500, 0.888, 0.9113, 700, 0.75, 0.855)
])
def test_determine_weighted_manure_attributes(old_mass: float, old_moisture: float, old_coverage: float,
                                              app_mass: float, app_dry_content: float, app_coverage: float) -> None:
    """Tests that the new, weighted values for the manure phosphorus pools are calculated correctly."""
    with patch(
            "SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure_application.ManureApplication"
            "._determine_moisture_factor", new=MagicMock(return_value=0.65)):
        observe = ManureApplication._determine_weighted_manure_attributes(old_mass, old_moisture, old_coverage,
                                                                          app_mass, app_dry_content, app_coverage)
        new_mass = old_mass + app_mass
        new_moisture = (old_moisture * old_mass) / new_mass + (0.65 * app_mass) / new_mass
        new_coverage = (old_coverage * old_mass) / new_mass + (app_coverage * app_mass) / new_mass

        ManureApplication._determine_moisture_factor.assert_called_once_with(app_mass, app_dry_content)
        assert observe.get("new_dry_matter_mass") == new_mass
        assert observe.get("new_moisture_factor") == new_moisture
        assert observe.get("new_field_coverage") == new_coverage
