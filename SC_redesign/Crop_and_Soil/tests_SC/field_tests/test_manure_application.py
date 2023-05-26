import pytest
from unittest.mock import MagicMock, patch

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.field.manure_application import ManureApplication


# ---- Static method tests
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


@pytest.mark.parametrize("dry_fraction", [
    0.35,
    0.445,
    0.85,
    1.0,
])
def test_determine_moisture_factor(dry_fraction: float) -> None:
    """Tests that the correct moisture factor is calculated based the mass applied and amount of water in the
        application."""
    observe = ManureApplication._determine_moisture_factor(dry_fraction)
    expect = min(0.9, (1 - dry_fraction))
    assert observe == expect


@pytest.mark.parametrize("mass,dry_fraction", [
    (500, 0),
    (400, -0.5),
    (600, 1.1),
])
def test_error_determine_moisture_factor(mass: float, dry_fraction: float) -> None:
    """Tests that correct error is raised when invalid argument is passed."""
    with pytest.raises(ValueError) as e:
        ManureApplication._determine_moisture_factor(dry_fraction)
    assert str(e.value) == f"Dry matter content must be in the range (0.0, 1.0], received: '{dry_fraction}'."


@pytest.mark.parametrize("old_mass,old_moisture,old_coverage,app_mass,app_dry_fraction,app_coverage", [
    (1100, 0.4, 0.7, 900, 0.8, 0.88),
    (400, 0.71, 0.93, 3500, 0.85, 0.95),
    (2500, 0.888, 0.9113, 700, 0.75, 0.855)
])
def test_determine_weighted_manure_attributes(old_mass: float, old_moisture: float, old_coverage: float,
                                              app_mass: float, app_dry_fraction: float, app_coverage: float) -> None:
    """Tests that the new, weighted values for the manure phosphorus pools are calculated correctly."""
    with patch(
            "SC_redesign.Crop_and_Soil.field.manure_application.ManureApplication._determine_moisture_factor",
            new=MagicMock(return_value=0.65)) as patched_moisture_factor:
        observe = ManureApplication._determine_weighted_manure_attributes(old_mass, old_moisture, old_coverage,
                                                                          app_mass, app_dry_fraction, app_coverage)
        new_mass = old_mass + app_mass
        new_moisture = (old_moisture * old_mass) / new_mass + (0.65 * app_mass) / new_mass
        new_coverage = (old_coverage * old_mass) / new_mass + (app_coverage * app_mass) / new_mass

        patched_moisture_factor.assert_called_once_with(app_dry_fraction)
        assert observe.get("new_dry_matter_mass") == new_mass
        assert observe.get("new_moisture_factor") == new_moisture
        assert observe.get("new_field_coverage") == new_coverage


@pytest.mark.parametrize("dry_mass,dry_fraction,coverage,area", [
    (1000, 0.15, 0.85, 3.86),
    (2500, 0.115, 0.88, 2.56),
    (1394.2943, 0.085643, 0.788184, 1.97482),
])
def test_determine_wet_rate_factor(dry_mass: float, dry_fraction: float, coverage: float, area: float) -> None:
    """Tests that the wet rate factor is calculated correctly based on the mass applied, fraction of solids in
        application, and area of coverage of the field.
    """
    observe = ManureApplication._determine_wet_rate_factor(dry_mass, dry_fraction, coverage, area)
    expect = dry_mass * (1 / (dry_fraction * (coverage * area)))
    assert pytest.approx(observe) == expect


@pytest.mark.parametrize("wet_rate", [
    0,
    1500,
    14000,
    2043,
    8945.29032,
])
def test_determine_infiltration_factor(wet_rate: float) -> None:
    """Tests that the infiltration rate is correctly calculated based on the wet rate."""
    observe = ManureApplication._determine_infiltration_factor(wet_rate)
    expect = 1.0 - min(0.9, 0.000002 * wet_rate + 0.267)
    assert observe == expect


# ---- Helper function tests
@pytest.mark.parametrize("dry_mass,dry_fraction,phosphorus_mass,field_coverage,weiP_frac", [
    (1000, 0.18, 200, 0.89, 0.5),
    (955, 0.44, 100, 0.76, 0.47),
    (2500, 0.411, 350, 0.96, 0.33),
])
def test_apply_solid_machine_manure(dry_mass: float, dry_fraction: float, phosphorus_mass: float, field_coverage: float,
                                    weiP_frac: float) -> None:
    """Tests that manure with greater than 15% solid matter content is added to the field correctly."""
    data = SoilData(machine_manure_dry_mass=3000, machine_manure_moisture_factor=0.65,
                    machine_manure_field_coverage=0.77, field_size=1.1)
    incorp = ManureApplication(data)
    incorp._determine_weighted_manure_attributes = MagicMock(return_value={"new_dry_matter_mass": 4000,
                                                                           "new_moisture_factor": 0.83,
                                                                           "new_field_coverage": 0.93})

    incorp._apply_solid_machine_manure(dry_mass, dry_fraction, phosphorus_mass, field_coverage, weiP_frac)

    incorp._determine_weighted_manure_attributes.assert_called_once_with(3000, 0.65, 0.77, dry_mass, dry_fraction,
                                                                         field_coverage)
    assert incorp.data.machine_water_extractable_inorganic_phosphorus == phosphorus_mass * weiP_frac
    assert incorp.data.machine_water_extractable_organic_phosphorus == phosphorus_mass * 0.05
    assert incorp.data.machine_stable_inorganic_phosphorus == \
        (phosphorus_mass * (1 - (weiP_frac + 0.05))) * 0.25
    assert pytest.approx(incorp.data.machine_stable_organic_phosphorus) == \
        (phosphorus_mass * (1 - (weiP_frac + 0.05))) * 0.75
    assert incorp.data.machine_manure_dry_mass == 4000
    assert incorp.data.machine_manure_moisture_factor == 0.83
    assert incorp.data.machine_manure_field_coverage == 0.93


@pytest.mark.parametrize("dry_mass,dry_frac,phosphorus_mass,coverage,area,weiP_frac", [
    (1000, 0.15, 122, 0.88, 1.94, 0.4),
    (1230, 0.115, 180, 0.97, 2.45, 0.356),
    (2015, 0.0911, 233.2, 0.66, 4.8, 0.22),
    (1780, 0.056, 345, 0.93, 3.81, 0.623),
])
def test_apply_liquid_machine_manure(dry_mass: float, dry_frac: float, phosphorus_mass: float, coverage: float,
                                     area: float, weiP_frac: float) -> None:
    """Tests that when manure slurry is added it correctly adds phosphorus to soil surface and subsurface pools, and
        sets surface pool characteristics.
    """
    data = SoilData(machine_manure_dry_mass=1000, machine_manure_moisture_factor=0.8, machine_manure_field_coverage=0.9,
                    field_size=1.1)
    incorp = ManureApplication(data)
    incorp._determine_wet_rate_factor = MagicMock(return_value=2000)
    incorp._determine_infiltration_factor = MagicMock(return_value=0.5)
    incorp.data.soil_layers[0].add_to_labile_phosphorus = MagicMock()
    incorp.data.soil_layers[0].add_to_active_phosphorus = MagicMock()
    incorp._determine_weighted_manure_attributes = MagicMock(return_value={"new_dry_matter_mass": 2050,
                                                                           "new_moisture_factor": 0.93,
                                                                           "new_field_coverage": 0.98})

    incorp._apply_liquid_machine_manure(dry_mass, dry_frac, phosphorus_mass, coverage, area, weiP_frac)

    expect_adjusted_dry_mass = dry_mass * 0.8
    expect_adjusted_coverage = coverage * 0.5
    expect_water_extractable_inorganic = phosphorus_mass * weiP_frac * 0.5
    expect_water_extractable_organic = phosphorus_mass * 0.05 * 0.5
    expect_stable_inorganic = phosphorus_mass * (1 - (weiP_frac + 0.05)) * 0.25 * 0.5
    expect_stable_organic = phosphorus_mass * (1 - (weiP_frac + 0.05)) * 0.75 * 0.5
    expect_labile = phosphorus_mass * weiP_frac * 0.5
    expect_labile += phosphorus_mass * 0.05 * 0.5 * 0.95
    expect_labile += phosphorus_mass * (1 - (weiP_frac + 0.05)) * 0.75 * 0.5 * 0.95
    expect_active = phosphorus_mass * (1 - (weiP_frac + 0.05)) * 0.25 * 0.5

    incorp._determine_wet_rate_factor.assert_called_once_with(dry_mass, dry_frac, coverage, area)
    incorp._determine_infiltration_factor.assert_called_once_with(2000)
    incorp._determine_weighted_manure_attributes.assert_called_once_with(1000, 0.8, 0.9, expect_adjusted_dry_mass,
                                                                         dry_frac, expect_adjusted_coverage)
    incorp.data.soil_layers[0].add_to_labile_phosphorus.assert_called_once_with(expect_labile, area)
    incorp.data.soil_layers[0].add_to_active_phosphorus.assert_called_once_with(expect_active, area)
    assert incorp.data.machine_manure_dry_mass == 2050
    assert incorp.data.machine_manure_moisture_factor == 0.93
    assert incorp.data.machine_manure_field_coverage == 0.98
    assert incorp.data.machine_water_extractable_inorganic_phosphorus == expect_water_extractable_inorganic
    assert incorp.data.machine_water_extractable_organic_phosphorus == expect_water_extractable_organic
    assert incorp.data.machine_stable_inorganic_phosphorus == expect_stable_inorganic
    assert incorp.data.machine_stable_organic_phosphorus == expect_stable_organic


# ---- Main routine tests
@pytest.mark.parametrize("dry_mass,dry_fraction,phosphorus_mass,field_size", [
    (1000, 0.78, 150, 1.8),
    (2344, 0.90, 201, 2.34),
    (900, 0.688, 78, 1.12),
    (1500, 0.89, 400, 4.1),
])
def test_apply_grazing_manure(dry_mass: float, dry_fraction: float, phosphorus_mass: float, field_size: float) -> None:
    """Tests that the grazing manure related attributes are correctly updated when grazing manure is applied."""
    data = SoilData(grazing_manure_dry_mass=4000, grazing_manure_moisture_factor=0.75, field_size=field_size,
                    grazing_manure_field_coverage=0.6)
    incorp = ManureApplication(data)
    incorp._determine_grazing_manure_field_coverage = MagicMock(return_value=0.8)
    incorp._determine_weighted_manure_attributes = MagicMock(return_value={"new_dry_matter_mass": 5000,
                                                                           "new_moisture_factor": 0.6,
                                                                           "new_field_coverage": 0.8})

    incorp.apply_grazing_manure(dry_mass, dry_fraction, phosphorus_mass, field_size)

    incorp._determine_grazing_manure_field_coverage.assert_called_once_with(field_size, dry_mass)
    incorp._determine_weighted_manure_attributes.assert_called_once_with(4000, 0.75, 0.6, dry_mass, dry_fraction,
                                                                         0.8)
    assert incorp.data.grazing_water_extractable_inorganic_phosphorus == phosphorus_mass * 0.50
    assert incorp.data.grazing_water_extractable_organic_phosphorus == phosphorus_mass * 0.05
    assert incorp.data.grazing_stable_inorganic_phosphorus == phosphorus_mass * 0.1125
    assert incorp.data.grazing_stable_organic_phosphorus == phosphorus_mass * 0.3375
    assert incorp.data.grazing_manure_dry_mass == 5000
    assert incorp.data.grazing_manure_moisture_factor == 0.6
    assert incorp.data.grazing_manure_field_coverage == 0.8
    assert incorp.data.grazing_manure_applied_mass == dry_mass


@pytest.mark.parametrize("dry_mass,dry_fraction,total_phosphorus_mass,coverage,area,weiP_frac,source_animal", [
    (1000, 0.75, 200, 0.85, 1.835, 0.5, None),
    (3000, 0.10, 150, 0.975, 2.2254, None, "CATTLE"),
    (2000, 0.44, 103.5, 0.88, 0.8898, 0.25, "SWINE"),
    (2500, 0.08, 175, 0.79, 3.4453, None, None),
])
def test_apply_machine_manure(dry_mass: float, dry_fraction: float, total_phosphorus_mass: float, coverage: float,
                              area: float, weiP_frac: float, source_animal: str) -> None:
    """Tests that the machine-applied manure is correctly added into existing manure on the field."""
    data = SoilData(field_size=1.1)
    incorp = ManureApplication(data)

    incorp._determine_water_extractable_inorganic_phosphorus_fraction_by_animal = MagicMock(return_value=0.25)
    incorp._apply_liquid_machine_manure = MagicMock()
    incorp._apply_solid_machine_manure = MagicMock()

    incorp.apply_machine_manure(dry_mass, dry_fraction, total_phosphorus_mass, coverage, area, weiP_frac, source_animal)

    expected_weiP_frac = weiP_frac
    if weiP_frac is None:
        incorp._determine_water_extractable_inorganic_phosphorus_fraction_by_animal.assert_called_once_with(
            source_animal)
        expected_weiP_frac = 0.25
    else:
        incorp._determine_water_extractable_inorganic_phosphorus_fraction_by_animal.assert_not_called()

    if dry_fraction <= 0.15:
        incorp._apply_liquid_machine_manure.assert_called_once_with(dry_mass, dry_fraction, total_phosphorus_mass,
                                                                    coverage, area, expected_weiP_frac)
    else:
        incorp._apply_solid_machine_manure.assert_called_once_with(dry_mass, dry_fraction, total_phosphorus_mass,
                                                                   coverage, expected_weiP_frac)
    assert incorp.data.machine_manure_applied_mass == dry_mass
