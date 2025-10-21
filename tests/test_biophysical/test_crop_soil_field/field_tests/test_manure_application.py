from typing import List
from unittest.mock import MagicMock, call, patch

import pytest
from pytest import approx

from RUFAS.biophysical.field.field.manure_application import ManureApplication
from RUFAS.biophysical.field.soil.manure_pool import ManurePool
from RUFAS.biophysical.field.soil.soil_data import SoilData


# ---- Static method tests
@pytest.mark.parametrize(
    "field_size,mass_applied",
    [
        (3.18, 300),
        (0.65, 10000),
        (2.18, 1000),
    ],
)
def test_determine_field_coverage(field_size: float, mass_applied: float) -> None:
    """Tests that the correct fraction of field covered by the new manure application is calculated."""
    observe = ManureApplication._determine_grazing_manure_field_coverage(field_size, mass_applied)
    mass_applied_grams = 1000 * mass_applied
    area_covered = mass_applied_grams * (659 / 250)
    area_covered /= 100000000
    expect = min(1.0, area_covered / field_size)
    assert observe == expect


@pytest.mark.parametrize(
    "dry_fraction",
    [
        0.35,
        0.445,
        0.85,
        1.0,
    ],
)
def test_determine_moisture_factor(dry_fraction: float) -> None:
    """Tests that the correct moisture factor is calculated based the mass applied and amount of water in the
    application."""
    observe = ManureApplication._determine_moisture_factor(dry_fraction)
    expect = min(0.9, (1 - dry_fraction))
    assert observe == expect


@pytest.mark.parametrize(
    "mass,dry_fraction",
    [
        (500, 0),
        (400, -0.5),
        (600, 1.1),
    ],
)
def test_error_determine_moisture_factor(mass: float, dry_fraction: float) -> None:
    """Tests that correct error is raised when invalid argument is passed."""
    with pytest.raises(ValueError) as e:
        ManureApplication._determine_moisture_factor(dry_fraction)
    assert str(e.value) == f"Dry matter content must be in the range (0.0, 1.0], received: '{dry_fraction}'."


@pytest.mark.parametrize(
    "old_mass,old_moisture,old_coverage,app_mass,app_dry_fraction,app_coverage,expected_mass,expected_moisture,"
    "expected_coverage",
    [
        (1100, 0.4, 0.7, 900, 0.8, 0.88, 2000, 0.5125, 0.781),
        (400, 0.71, 0.93, 3500, 0.85, 0.95, 3900, 0.65615, 0.94794871),
        (2500, 0.888, 0.9113, 700, 0.75, 0.855, 3200, 0.8359375, 0.898984),
        (0, 0, 0, 0, 0, 0, 0, 0, 0),
    ],
)
def test_determine_weighted_manure_attributes(
    old_mass: float,
    old_moisture: float,
    old_coverage: float,
    app_mass: float,
    app_dry_fraction: float,
    app_coverage: float,
    expected_mass: float,
    expected_moisture: float,
    expected_coverage: float,
) -> None:
    """Tests that the new, weighted values for the manure phosphorus pools are calculated correctly."""
    with patch(
        "RUFAS.biophysical.field.field.manure_application.ManureApplication._determine_moisture_factor",
        new=MagicMock(return_value=0.65),
    ) as patched_moisture_factor:
        observe = ManureApplication._determine_weighted_manure_attributes(
            old_mass,
            old_moisture,
            old_coverage,
            app_mass,
            app_dry_fraction,
            app_coverage,
        )

        if (old_mass + app_mass) > 0:
            patched_moisture_factor.assert_called_once_with(app_dry_fraction)

        assert pytest.approx(observe.get("new_dry_matter_mass"), rel=1e-4) == expected_mass
        assert pytest.approx(observe.get("new_moisture_factor"), rel=1e-4) == expected_moisture
        assert pytest.approx(observe.get("new_field_coverage"), rel=1e-4) == expected_coverage


@pytest.mark.parametrize("animal_type,expected", [("CATTLE", 0.50), ("SWINE", 0.35), ("POULTRY", 0.20)])
def test_determine_water_extractable_inorganic_phosphorus_fraction_by_animal(animal_type: str, expected: float) -> None:
    """Tests that the water extractable inorganic phosphorus fraction is correctly determined based on the animal
    type"""
    actual = ManureApplication._determine_water_extractable_inorganic_phosphorus_fraction_by_animal(animal_type)
    assert actual == expected


@pytest.mark.parametrize("animal_type", ["CaTTLE", "PORK", "fish"])
def test_error_determine_water_extractable_inorganic_phosphorus_fraction_by_animal(
    animal_type: str,
) -> None:
    """Tests that errors caused by unsupported animal types are handled appropriately."""
    with pytest.raises(ValueError) as e:
        ManureApplication._determine_water_extractable_inorganic_phosphorus_fraction_by_animal(animal_type)
    assert str(e.value) == f'Expected "CATTLE", "SWINE", or "POULTRY", received \'{animal_type}\'.'


# ---- Helper function tests
@pytest.mark.parametrize(
    "dry_mass,dry_fraction,phosphorus_mass,field_coverage,depth,remainder,weiP_frac,"
    "inorganic_frac,ammonium_frac,organic_frac,subsurface_app",
    [
        (1000, 0.18, 200, 0.89, 0.0, 1.0, 0.5, 0.33, 0.51, 0.05, False),
        (955, 0.44, 100, 0.76, 100.0, 0.5, 0.47, 0.2, 0.45, 0.03, True),
        (2500, 0.411, 350, 0.96, 250.0, 0.15, 0.33, 0.15, 0.42, 0.045, True),
    ],
)
def test_apply_solid_machine_manure(
    dry_mass: float,
    dry_fraction: float,
    phosphorus_mass: float,
    field_coverage: float,
    depth: float,
    remainder: float,
    weiP_frac: float,
    inorganic_frac: float,
    ammonium_frac: float,
    organic_frac: float,
    subsurface_app: bool,
) -> None:
    """Tests that manure with greater than 15% solid matter content is added to the field correctly."""

    machine_manure_pool = ManurePool(manure_dry_mass=3000, manure_moisture_factor=0.65, manure_field_coverage=0.77)
    data = SoilData(
        machine_manure=machine_manure_pool,
        field_size=1.1,
    )
    incorp = ManureApplication(data)
    incorp._determine_weighted_manure_attributes = MagicMock(
        return_value={
            "new_dry_matter_mass": 4000,
            "new_moisture_factor": 0.83,
            "new_field_coverage": 0.93,
        }
    )
    incorp._add_nitrogen_to_soil_layer = MagicMock()
    incorp._apply_subsurface_manure = MagicMock()

    incorp.apply_machine_manure(
        dry_matter_mass=dry_mass,
        dry_matter_fraction=dry_fraction,
        total_phosphorus_mass=phosphorus_mass,
        field_coverage=field_coverage,
        application_depth=depth,
        surface_remainder_fraction=remainder,
        water_extractable_inorganic_phosphorus_fraction=weiP_frac,
        inorganic_nitrogen_fraction=inorganic_frac,
        ammonium_fraction=ammonium_frac,
        organic_nitrogen_fraction=organic_frac,
        field_size=1.1,
    )

    expected_dry_mass = dry_mass * remainder
    expected_stable_inorganic_frac = (1 - (weiP_frac + 0.05)) * 0.25
    expected_stable_organic_frac = (1 - (weiP_frac + 0.05)) * 0.75
    expected_subsurface_frac = 1.0 - remainder
    incorp._determine_weighted_manure_attributes.assert_called_once_with(
        3000, 0.65, 0.77, expected_dry_mass, dry_fraction, field_coverage
    )
    incorp._add_nitrogen_to_soil_layer.assert_called_once_with(
        0, expected_dry_mass, inorganic_frac, ammonium_frac, organic_frac, 1.1
    )
    assert incorp.data.machine_manure.water_extractable_inorganic_phosphorus == phosphorus_mass * weiP_frac * remainder
    assert incorp.data.machine_manure.water_extractable_organic_phosphorus == phosphorus_mass * 0.05 * remainder
    assert (
        incorp.data.machine_manure.stable_inorganic_phosphorus
        == phosphorus_mass * expected_stable_inorganic_frac * remainder
    )
    assert (
        pytest.approx(incorp.data.machine_manure.stable_organic_phosphorus)
        == phosphorus_mass * expected_stable_organic_frac * remainder
    )
    assert incorp.data.machine_manure.manure_dry_mass == 4000
    assert incorp.data.machine_manure.manure_moisture_factor == 0.83
    assert incorp.data.machine_manure.manure_field_coverage == 0.93
    if subsurface_app:
        incorp._apply_subsurface_manure.assert_called_once_with(
            phosphorus_mass,
            weiP_frac,
            0.05,
            expected_stable_inorganic_frac,
            expected_stable_organic_frac,
            dry_mass,
            inorganic_frac,
            ammonium_frac,
            organic_frac,
            depth,
            expected_subsurface_frac,
            1.1,
        )
    else:
        incorp._apply_subsurface_manure.assert_not_called()


@pytest.mark.parametrize(
    "dry_mass,dry_frac,phosphorus_mass,coverage,depth,remainder,area,weiP_frac,inorganic_frac,"
    "ammonium_frac,organic_frac,subsurface_app",
    [
        (1000, 0.15, 122, 0.88, 0.0, 1.0, 1.94, 0.4, 0.3, 0.39, 0.044, False),
        (1230, 0.115, 180, 0.97, 0.0, 1.0, 2.45, 0.356, 0.14, 0.5, 0.018, False),
        (2015, 0.0911, 233.2, 0.66, 100.0, 0.2, 4.8, 0.22, 0.2, 0.51, 0.023, True),
        (1780, 0.056, 345, 0.93, 80.0, 0.44, 3.81, 0.623, 0.18, 0.6, 0.033, True),
    ],
)
def test_apply_liquid_machine_manure(
    dry_mass: float,
    dry_frac: float,
    phosphorus_mass: float,
    coverage: float,
    depth: float,
    remainder: float,
    area: float,
    weiP_frac: float,
    inorganic_frac: float,
    ammonium_frac: float,
    organic_frac: float,
    subsurface_app: bool,
) -> None:
    """Tests that when manure slurry is added it correctly adds phosphorus to soil surface and subsurface pools, and
    sets surface pool characteristics.
    """
    machine_manure_pool = ManurePool(manure_dry_mass=1000, manure_moisture_factor=0.8, manure_field_coverage=0.9)
    data = SoilData(
        machine_manure=machine_manure_pool,
        field_size=area,
    )
    incorp = ManureApplication(data)
    incorp.data.soil_layers[0].add_to_labile_phosphorus = MagicMock()
    incorp.data.soil_layers[0].add_to_active_phosphorus = MagicMock()
    incorp._determine_weighted_manure_attributes = MagicMock(
        return_value={
            "new_dry_matter_mass": 2050,
            "new_moisture_factor": 0.93,
            "new_field_coverage": 0.98,
        }
    )
    incorp._add_nitrogen_to_soil_layer = MagicMock()
    incorp._apply_subsurface_manure = MagicMock()

    incorp.apply_machine_manure(
        dry_matter_mass=dry_mass,
        dry_matter_fraction=dry_frac,
        total_phosphorus_mass=phosphorus_mass,
        field_coverage=coverage,
        application_depth=depth,
        surface_remainder_fraction=remainder,
        field_size=area,
        water_extractable_inorganic_phosphorus_fraction=weiP_frac,
        inorganic_nitrogen_fraction=inorganic_frac,
        ammonium_fraction=ammonium_frac,
        organic_nitrogen_fraction=organic_frac,
    )

    is_liquid_manure = dry_frac <= 0.15
    expect_surface_dry_mass = dry_mass * remainder
    expect_adjusted_dry_mass = expect_surface_dry_mass * 0.8
    expect_adjusted_coverage = coverage * 0.5
    expect_water_extractable_inorganic = phosphorus_mass * weiP_frac * 0.4 * remainder
    expect_water_extractable_organic = phosphorus_mass * 0.05 * 0.4 * remainder
    expect_stable_inorganic_frac = (1 - (weiP_frac + 0.05)) * 0.25
    expect_stable_inorganic = phosphorus_mass * expect_stable_inorganic_frac * 0.4 * remainder
    expect_stable_organic_frac = (1 - (weiP_frac + 0.05)) * 0.75
    expect_stable_organic = phosphorus_mass * expect_stable_organic_frac * 0.4 * remainder
    expect_labile = phosphorus_mass * weiP_frac * 0.6
    expect_labile += phosphorus_mass * 0.05 * 0.6 * 0.95
    expect_labile += phosphorus_mass * (1 - (weiP_frac + 0.05)) * 0.75 * 0.6 * 0.95
    expect_labile *= remainder
    expect_active = phosphorus_mass * (1 - (weiP_frac + 0.05)) * 0.25 * 0.6 * remainder

    surface_retention = 0.4 if is_liquid_manure else 1.0
    expected_mass = expect_surface_dry_mass * surface_retention
    expected_nitrogen_calls = [
        call(0, expected_mass, inorganic_frac, ammonium_frac, organic_frac, area),
    ]
    if is_liquid_manure:
        expected_second_layer_mass = expect_surface_dry_mass * (1 - surface_retention)
        expected_nitrogen_calls.append(
            call(1, expected_second_layer_mass, inorganic_frac, ammonium_frac, organic_frac, area)
        )
    expected_subsurface_frac = 1.0 - remainder

    incorp._determine_weighted_manure_attributes.assert_called_once_with(
        1000, 0.8, 0.9, expect_adjusted_dry_mass, dry_frac, expect_adjusted_coverage
    )
    incorp._add_nitrogen_to_soil_layer.assert_has_calls(expected_nitrogen_calls)
    incorp.data.soil_layers[0].add_to_labile_phosphorus.assert_called_once_with(expect_labile, area)
    incorp.data.soil_layers[0].add_to_active_phosphorus.assert_called_once_with(expect_active, area)
    assert incorp.data.machine_manure.manure_dry_mass == 2050
    assert incorp.data.machine_manure.manure_moisture_factor == 0.93
    assert incorp.data.machine_manure.manure_field_coverage == 0.98
    assert incorp.data.machine_manure.water_extractable_inorganic_phosphorus == expect_water_extractable_inorganic
    assert incorp.data.machine_manure.water_extractable_organic_phosphorus == expect_water_extractable_organic
    assert incorp.data.machine_manure.stable_inorganic_phosphorus == expect_stable_inorganic
    assert incorp.data.machine_manure.stable_organic_phosphorus == expect_stable_organic
    if subsurface_app:
        incorp._apply_subsurface_manure.assert_called_once_with(
            phosphorus_mass,
            weiP_frac,
            0.05,
            expect_stable_inorganic_frac,
            expect_stable_organic_frac,
            dry_mass,
            inorganic_frac,
            ammonium_frac,
            organic_frac,
            depth,
            expected_subsurface_frac,
            area,
        )
    else:
        incorp._apply_subsurface_manure.assert_not_called()


@pytest.mark.parametrize(
    "total_phosphorus,wip_frac,wop_frap,sip_frac,sop_frac,dry_matter,inorganic_frac,ammonium_frac,"
    "organic_frac,depth,subsurface_frac,area,expected_labile_calls,expected_active_calls,"
    "expected_nitrogen_calls",
    [
        (
            50.0,
            0.5,
            0.05,
            0.33,
            0.12,
            100.0,
            0.4,
            0.5,
            0.1,
            65.0,
            0.5,
            1.5,
            [
                call(approx(0.826875), 1.5),
                call(approx(5.788125), 1.5),
                call(approx(9.9225), 1.5),
            ],
            [
                call(approx(0.4125), 1.5),
                call(approx(2.8875), 1.5),
                call(approx(4.95), 1.5),
            ],
            [
                call(0, 2.5, 0.4, 0.5, 0.1, 1.5),
                call(1, 17.5, 0.4, 0.5, 0.1, 1.5),
                call(2, 30, 0.4, 0.5, 0.1, 1.5),
            ],
        ),
        (
            70.0,
            0.6,
            0.03,
            0.28,
            0.09,
            125.0,
            0.5,
            0.3,
            0.08,
            100.0,
            0.8,
            2.1,
            [
                call(approx(1.9992), 2.1),
                call(approx(13.9944), 2.1),
                call(approx(23.9904), 2.1),
            ],
            [
                call(approx(0.784), 2.1),
                call(approx(5.488), 2.1),
                call(approx(9.408), 2.1),
            ],
            [
                call(0, 5, 0.5, 0.3, 0.08, 2.1),
                call(1, 35, 0.5, 0.3, 0.08, 2.1),
                call(2, 60, 0.5, 0.3, 0.08, 2.1),
            ],
        ),
    ],
)
def test_apply_subsurface_manure(
    total_phosphorus: float,
    wip_frac: float,
    wop_frap: float,
    sip_frac: float,
    sop_frac: float,
    dry_matter: float,
    inorganic_frac: float,
    ammonium_frac: float,
    organic_frac: float,
    depth: float,
    subsurface_frac: float,
    area: float,
    expected_labile_calls: list,
    expected_active_calls: list,
    expected_nitrogen_calls: list,
) -> None:
    """Tests that nutrients from injection manure applications are correctly distributed between soil layers."""
    manure_app = ManureApplication(field_size=area)
    with (
        patch(
            "RUFAS.biophysical.field.soil.soil_data.SoilData.get_vectorized_layer_attribute",
            new_callable=MagicMock,
            return_value=[20.0, 50.0, 200.0, 400.0],
        ) as layer,
        patch(
            "RUFAS.biophysical.field.field.fertilizer_application.FertilizerApplication.generate_depth_factors",
            new_callable=MagicMock,
            return_value=[0.05, 0.35, 0.6],
        ) as depth_factors,
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.add_to_labile_phosphorus",
            new_callable=MagicMock,
        ) as labile,
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.add_to_active_phosphorus",
            new_callable=MagicMock,
        ) as active,
        patch(
            "RUFAS.biophysical.field.field.manure_application.ManureApplication._add_nitrogen_to_soil_layer",
            new_callable=MagicMock,
        ) as nitrogen,
    ):
        manure_app._apply_subsurface_manure(
            total_phosphorus,
            wip_frac,
            wop_frap,
            sip_frac,
            sop_frac,
            dry_matter,
            inorganic_frac,
            ammonium_frac,
            organic_frac,
            depth,
            subsurface_frac,
            area,
        )

        layer.assert_called_once_with("bottom_depth")
        depth_factors.assert_called_once_with(depth, [20.0, 50.0, 200.0, 400.0])
        labile.assert_has_calls(expected_labile_calls)
        active.assert_has_calls(expected_active_calls)
        nitrogen.assert_has_calls(expected_nitrogen_calls)


@pytest.mark.parametrize(
    "index,mass,inorganic_frac,ammonium_frac,organic_frac,field_size,expected",
    [
        (0, 100, 0.3, 0.5, 0.08, 1.6, [15, 15, 8.0]),
        (1, 44, 0.41, 0.35, 0.075, 2.2, [11.726, 6.314, 3.3]),
        (3, 50, 0.0, 0.0, 0.0, 1.3, [0, 0, 0]),
    ],
)
def test_add_nitrogen_to_soil_layer(
    index: int,
    mass: float,
    inorganic_frac: float,
    ammonium_frac: float,
    organic_frac: float,
    field_size: float,
    expected: List[float],
) -> None:
    """Tests that nitrogen is added to the top soil layer correctly."""
    man_app = ManureApplication(field_size=field_size)
    man_app.data.soil_layers[index].nitrate_content = 5
    man_app.data.soil_layers[index].ammonium_content = 5
    man_app.data.soil_layers[index].stable_organic_nitrogen_content = 5
    man_app.data.soil_layers[index].active_organic_nitrogen_content = 5

    man_app._add_nitrogen_to_soil_layer(index, mass, inorganic_frac, ammonium_frac, organic_frac, field_size)

    active_fraction_of_organic_nitrogen = 0.9286
    expected_nitrates = 5 + (expected[0] / field_size)
    expected_ammonium = 5 + (expected[1] / field_size)
    expected_organic_stable = 5 + (expected[2] * (1 - active_fraction_of_organic_nitrogen) / field_size)
    assert pytest.approx(man_app.data.soil_layers[index].nitrate_content) == expected_nitrates
    assert man_app.data.soil_layers[index].ammonium_content == expected_ammonium
    assert man_app.data.soil_layers[index].stable_organic_nitrogen_content == expected_organic_stable
    assert man_app.data.soil_layers[index].active_organic_nitrogen_content == 5


# ---- Main routine tests
@pytest.mark.parametrize(
    "dry_mass,dry_fraction,phosphorus_mass,inorganic_frac,ammonium_frac,organic_frac,field_size",
    [
        (1000, 0.78, 150, 0.22, 0.45, 0.03, 1.8),
        (2344, 0.90, 201, 0.3, 0.39, 0.05, 2.34),
        (900, 0.688, 78, 0.29, 0.55, 0.1, 1.12),
        (1500, 0.89, 400, 0.33, 0.4, 0.09, 4.1),
    ],
)
def test_apply_grazing_manure(
    dry_mass: float,
    dry_fraction: float,
    phosphorus_mass: float,
    inorganic_frac: float,
    ammonium_frac: float,
    organic_frac: float,
    field_size: float,
) -> None:
    """Tests that the grazing manure related attributes are correctly updated when grazing manure is applied."""
    grazing_manure_pool = ManurePool(manure_dry_mass=4000, manure_moisture_factor=0.75, manure_field_coverage=0.6)
    data = SoilData(
        grazing_manure=grazing_manure_pool,
        field_size=field_size,
    )
    incorp = ManureApplication(data)
    incorp._determine_grazing_manure_field_coverage = MagicMock(return_value=0.8)
    incorp._determine_weighted_manure_attributes = MagicMock(
        return_value={
            "new_dry_matter_mass": 5000,
            "new_moisture_factor": 0.6,
            "new_field_coverage": 0.8,
        }
    )
    incorp._add_nitrogen_to_soil_layer = MagicMock()

    incorp.apply_grazing_manure(
        dry_mass,
        dry_fraction,
        phosphorus_mass,
        inorganic_frac,
        ammonium_frac,
        organic_frac,
        field_size,
    )

    incorp._determine_grazing_manure_field_coverage.assert_called_once_with(field_size, dry_mass)
    incorp._determine_weighted_manure_attributes.assert_called_once_with(4000, 0.75, 0.6, dry_mass, dry_fraction, 0.8)
    incorp._add_nitrogen_to_soil_layer.assert_called_once_with(
        0, dry_mass, inorganic_frac, ammonium_frac, organic_frac, field_size
    )
    assert incorp.data.grazing_manure.water_extractable_inorganic_phosphorus == phosphorus_mass * 0.50
    assert incorp.data.grazing_manure.water_extractable_organic_phosphorus == phosphorus_mass * 0.05
    assert incorp.data.grazing_manure.stable_inorganic_phosphorus == phosphorus_mass * 0.1125
    assert incorp.data.grazing_manure.stable_organic_phosphorus == phosphorus_mass * 0.3375
    assert incorp.data.grazing_manure.manure_dry_mass == 5000
    assert incorp.data.grazing_manure.manure_moisture_factor == 0.6
    assert incorp.data.grazing_manure.manure_field_coverage == 0.8
    assert incorp.data.grazing_manure.manure_applied_mass == dry_mass


@pytest.mark.parametrize(
    "dry_mass,dry_fraction,total_phosphorus_mass,coverage,depth,remainder,area,inorganic_frac,"
    "ammonium_frac,organic_frac,weiP_frac,source_animal,should_fail",
    [
        (1000, 0.75, 200, 0.85, 0.0, 1.0, 1.835, 0.11, 0.55, 0.01, 0.5, None, False),
        (2000, 0.44, 103.5, 0.88, 0.0, 1.0, 0.8898, 0.14, 0.44, 0.06, 0.25, "SWINE", False),
        (2500, 0.08, 175, 0.79, 50.0, 0.92, 3.4453, 0.33, 0.39, 0.09, 1.8, None, True),
        (1500, 0.60, 150, 0.75, 10.0, 0.9, 2.5, 0.25, 0.15, 0.2, None, "CATTLE", False),
    ],
)
def test_apply_machine_manure(
    dry_mass: float,
    dry_fraction: float,
    total_phosphorus_mass: float,
    coverage: float,
    depth: float,
    remainder: float,
    area: float,
    inorganic_frac: float,
    ammonium_frac: float,
    organic_frac: float,
    weiP_frac: float | None,
    source_animal: str,
    should_fail: bool,
) -> None:
    """Tests that the machine-applied manure is correctly added into existing manure on the field."""
    data = SoilData(field_size=area)
    incorp = ManureApplication(data)

    if should_fail:
        with pytest.raises(ValueError) as e:
            incorp.apply_machine_manure(
                dry_mass,
                dry_fraction,
                total_phosphorus_mass,
                coverage,
                depth,
                remainder,
                area,
                inorganic_frac,
                ammonium_frac,
                organic_frac,
                weiP_frac,
                source_animal,
            )
        assert (
            str(e.value) == f"Water extractable inorganic phosphorus fraction must be in the range [0.0, 0.95],"
            f" received '{weiP_frac}'."
        )
    else:
        incorp._determine_water_extractable_inorganic_phosphorus_fraction_by_animal = MagicMock(return_value=0.25)
        incorp.apply_machine_manure(
            dry_matter_mass=dry_mass,
            dry_matter_fraction=dry_fraction,
            total_phosphorus_mass=total_phosphorus_mass,
            field_coverage=coverage,
            application_depth=depth,
            surface_remainder_fraction=remainder,
            field_size=area,
            inorganic_nitrogen_fraction=inorganic_frac,
            ammonium_fraction=ammonium_frac,
            organic_nitrogen_fraction=organic_frac,
            water_extractable_inorganic_phosphorus_fraction=weiP_frac,
            source_animal=source_animal,
        )

        if weiP_frac is None:
            incorp._determine_water_extractable_inorganic_phosphorus_fraction_by_animal.assert_called_once_with(
                source_animal
            )
        else:
            incorp._determine_water_extractable_inorganic_phosphorus_fraction_by_animal.assert_not_called()

        assert incorp.data.machine_manure.water_extractable_inorganic_phosphorus > 0
        assert incorp.data.machine_manure.water_extractable_organic_phosphorus > 0
        assert incorp.data.machine_manure.stable_inorganic_phosphorus > 0
        assert incorp.data.machine_manure.stable_organic_phosphorus > 0
