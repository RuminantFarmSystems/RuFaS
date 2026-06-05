import math
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.crop_management import CropManagement
from RUFAS.biophysical.field.soil.carbon_cycling.residue_partition import ResiduePartition
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.fixture
def soil_data(mocker: MockerFixture) -> SoilData:
    mocker.patch.object(SoilData, "__init__", return_value=None)
    mocker.patch.object(LayerData, "__init__", return_value=None)
    soil_data = SoilData()
    soil_data.soil_layers = [LayerData(), LayerData(), LayerData()]
    return soil_data


@pytest.mark.parametrize(
    "plant_residue_lignin_composition, rainfall",
    [
        (3, 0.4),  # default
        (50, 0.5),  # higher plant_residue_lignin_composition
        (1.8, 55),  # higher rainfall
        (0, 0),  # neither
        (3, 0),  # no rainfall
        (0, 3),  # no plant_residue_lignin_composition
    ],
)
def test_determine_plant_residue_lignin_composition(plant_residue_lignin_composition: float, rainfall: float) -> None:
    """Tests that the plant residue lignin composition will be updated correctly as the equation with given rainfall"""
    expected = plant_residue_lignin_composition + 0.12 * rainfall * 0.1
    assert expected == ResiduePartition._determine_plant_residue_lignin_composition(
        plant_residue_lignin_composition, rainfall
    )


@pytest.mark.parametrize(
    "plant_residue_lignin_composition, total_residue, crop_yield_nitrogen," "expected_result",
    [
        (0.5, 50, 20, 0.0125),  # default
        (0.5, 50, 0, 0),  # no nitrogen
        (0.5, 50, -50, 0),  # negative case
        (0.0, 0.0, 0.0, 0.0),
    ],
)
def test_determine_plant_lignin_nitrogen_fraction(
    plant_residue_lignin_composition: float,
    total_residue: float,
    crop_yield_nitrogen: float,
    expected_result: float,
) -> None:
    """Test that metabolic plant residue ration is correctly determined under current nitrogen_fraction_plant_residue"""
    if total_residue:
        nitrogen_fraction_plant_residue = crop_yield_nitrogen / total_residue
    else:
        nitrogen_fraction_plant_residue = 0.0

    if 0 < nitrogen_fraction_plant_residue <= 1.0:
        assert expected_result == pytest.approx(
            ResiduePartition._determine_plant_lignin_nitrogen_fraction(
                plant_residue_lignin_composition, total_residue, crop_yield_nitrogen
            )
        )
    elif nitrogen_fraction_plant_residue == 0:
        assert expected_result == ResiduePartition._determine_plant_lignin_nitrogen_fraction(
            plant_residue_lignin_composition, total_residue, crop_yield_nitrogen
        )
    else:
        # case of invalid input
        with pytest.raises(ValueError) as e:
            ResiduePartition._determine_plant_lignin_nitrogen_fraction(
                plant_residue_lignin_composition, total_residue, crop_yield_nitrogen
            )
        expected = "Expected nitrogen_fraction_plant_residue be between 0.0-1.0, received " + str(
            nitrogen_fraction_plant_residue
        )
        assert expected == str(e.value)


@pytest.mark.parametrize(
    "plant_lignin_nitrogen_ratio",
    [
        7,  # lower values
        56,  # higher values
        35.8,  # arbitrary
    ],
)
def test_determine_plant_residue_metabolic_fraction(
    plant_lignin_nitrogen_ratio: float,
) -> None:
    """Tests to see if the fraction of plant residue that is metabolic is calculated correctly"""
    expected = 0.85 - 0.18 * plant_lignin_nitrogen_ratio
    assert expected == ResiduePartition._determine_plant_residue_metabolic_fraction(plant_lignin_nitrogen_ratio)


@pytest.mark.parametrize(
    "plant_metabolic_carbon_amount, plant_residue_metabolic_fraction,"
    "plant_dry_matter_residue_amount, plant_metabolic_active_carbon_usage, "
    "plant_metabolic_to_soil_carbon_amount",
    [
        (3, 8, 7, 1, 2),
        (60, 64, 85, 40, 30),
        (1.8, 1.1, 3.2, 0.8, 0.7),
    ],
)
def test_determine_plant_metabolic_carbon_amount(
    plant_metabolic_carbon_amount: float,
    plant_residue_metabolic_fraction: float,
    plant_dry_matter_residue_amount: float,
    plant_metabolic_active_carbon_usage: float,
    plant_metabolic_to_soil_carbon_amount: float,
) -> None:
    """Tests that the updated plant metabolic carbon amount is calculated correctly"""
    expected = (
        plant_metabolic_carbon_amount
        + plant_dry_matter_residue_amount * plant_residue_metabolic_fraction
        - (plant_metabolic_active_carbon_usage + plant_metabolic_to_soil_carbon_amount)
    )
    assert expected == ResiduePartition._determine_plant_metabolic_carbon_amount(
        plant_metabolic_carbon_amount,
        plant_residue_metabolic_fraction,
        plant_dry_matter_residue_amount,
        plant_metabolic_active_carbon_usage,
        plant_metabolic_to_soil_carbon_amount,
    )


@pytest.mark.parametrize(
    "decomposition_moisture_effect, decomposition_temperature_effect, " "plant_metabolic_carbon_amount",
    [
        (3, 8, 7),
        (60, 64, 85),
        (1.8, 1.1, 3.27),
    ],
)
def test_determine_plant_metabolic_active_carbon_usage(
    decomposition_moisture_effect: float,
    decomposition_temperature_effect: float,
    plant_metabolic_carbon_amount: float,
) -> None:
    """Tests that plant metabolic active carbon usage amount was calculated correctly"""
    metabolic_active_carbon_rate = 0.28
    expected = (
        decomposition_moisture_effect
        * decomposition_temperature_effect
        * plant_metabolic_carbon_amount
        * metabolic_active_carbon_rate
    )
    assert expected == ResiduePartition._determine_plant_metabolic_active_carbon_usage(
        decomposition_moisture_effect,
        decomposition_temperature_effect,
        plant_metabolic_carbon_amount,
    )


@pytest.mark.parametrize(
    "plant_residue_metabolic_fraction",
    [
        0.1,  # low fraction
        0.9,  # high fraction
        0,  # no fraction
    ],
)
def test_determine_plant_structural_to_slow_or_active_rate(
    plant_residue_metabolic_fraction: float,
) -> None:
    """Tests that the rate at which above ground structural carbon decomposes into slow or active carbon was calculated
    correctly"""
    structural_decomposition_factor = 0.076
    expected = structural_decomposition_factor * math.exp(-3) * (1 - plant_residue_metabolic_fraction)
    assert expected == ResiduePartition._determine_plant_structural_to_slow_or_active_rate(
        plant_residue_metabolic_fraction
    )


@pytest.mark.parametrize(
    "plant_structural_to_slow_or_active_rate, decomposition_moisture_effect,"
    "decomposition_temperature_effect, plant_structural_carbon_amount",
    [
        (3, 8, 7, 1),
        (60, 64, 85, 41),
        (1.8, 1.1, 3.2, 0.8),
    ],
)
def test_determine_plant_structural_to_slow_active_carbon_amount(
    plant_structural_to_slow_or_active_rate: float,
    decomposition_moisture_effect: float,
    decomposition_temperature_effect: float,
    plant_structural_carbon_amount: float,
) -> None:
    """Tests that the amount of plant structural carbon decomposed into slow or active carbon was calculated
    correctly"""
    expected = (
        plant_structural_to_slow_or_active_rate
        * decomposition_moisture_effect
        * decomposition_temperature_effect
        * plant_structural_carbon_amount
    )
    assert expected == ResiduePartition._determine_plant_structural_to_slow_active_carbon_amount(
        plant_structural_to_slow_or_active_rate,
        decomposition_moisture_effect,
        decomposition_temperature_effect,
        plant_structural_carbon_amount,
    )


@pytest.mark.parametrize(
    "plant_structural_carbon_amount, tillage_fraction",
    [
        (3, 0.4),  # default
        (50, 0.4),  # increased carbon
        (3, 1.0),  # increased tillage
        (1.8, 0.33),  # decreased carbon & tillage
        (0, 0.4),  # no carbon
        (3, 0),  # no tillage
        (0, 0),  # neither
    ],
)
def test_determine_structural_carbon_transfer_amount(
    plant_structural_carbon_amount: float, tillage_fraction: float
) -> None:
    """Tests that the amount of transfer of structural carbon during tillage was calculated correctly"""
    expected = plant_structural_carbon_amount * tillage_fraction
    assert expected == ResiduePartition._determine_structural_carbon_transfer_amount(
        plant_structural_carbon_amount, tillage_fraction
    )


@pytest.mark.parametrize(
    "plant_dry_matter_residue_amount, plant_residue_metabolic_fraction,"
    "structural_carbon_transfer_amount, plant_structural_to_slow_carbon_amount, "
    "plant_structural_carbon_amount, plant_structural_to_active_carbon_amount",
    [
        (3, 8, 7, 1, 2, 5),
        (60, 64, 85, 40, 30, 99),
        (1.8, 1.1, 3.2, 0.8, 0.7, 0.3),
    ],
)
def test_determine_plant_structural_carbon_amount(
    plant_dry_matter_residue_amount: float,
    plant_residue_metabolic_fraction: float,
    structural_carbon_transfer_amount: float,
    plant_structural_to_active_carbon_amount: float,
    plant_structural_to_slow_carbon_amount: float,
    plant_structural_carbon_amount: float,
) -> None:
    """Tests that plant_structural_carbon_amount was updated correctly"""
    expected = (
        plant_structural_carbon_amount
        + plant_dry_matter_residue_amount * (1 - plant_residue_metabolic_fraction)
        - structural_carbon_transfer_amount
        - plant_structural_to_active_carbon_amount
        - plant_structural_to_slow_carbon_amount
    )
    assert expected == ResiduePartition._determine_plant_structural_carbon_amount(
        plant_dry_matter_residue_amount,
        plant_residue_metabolic_fraction,
        structural_carbon_transfer_amount,
        plant_structural_to_active_carbon_amount,
        plant_structural_to_slow_carbon_amount,
        plant_structural_carbon_amount,
    )


@pytest.mark.parametrize(
    "soil_dry_matter_residue_amount, root_biomass",
    [
        (15, 14),  # default
        (50, 2.2),  # increased soil_dry_matter_residue_amount
        (3, 24),  # increased root_biomass
        (1.8, 0.01),  # decreased soil_dry_matter_residue_amount & root_biomass
        (0, 0.4),  # no soil_dry_matter_residue_amount
        (2, 0),  # no root_biomass
        (0, 0),  # neither
    ],
)
def test_determine_weighted_residue_dry_matter_lignin_fraction(
    soil_dry_matter_residue_amount: float, root_biomass: float
) -> None:
    """Tests that the weighted fractional of lignin amount in residue dry matter was calculated correctly under each
    condition"""
    if soil_dry_matter_residue_amount + root_biomass != 0:
        expected = soil_dry_matter_residue_amount / (soil_dry_matter_residue_amount + root_biomass)
    else:
        expected = 0

    assert expected == ResiduePartition._determine_weighted_residue_dry_matter_lignin_fraction(
        soil_dry_matter_residue_amount, root_biomass
    )


@pytest.mark.parametrize(
    "weighted_residue_dry_matter_lignin_fraction, rainfall",
    [
        (0.5, 20),  # default
        (1, 2.2),  # increased weighted_residue_dry_matter_lignin_fraction
        (0.5, 60),  # increased rainfall
        (0.01, 0.3),  # decreased weighted_residue_dry_matter_lignin_fraction & rainfall
        (0, 20),  # no weighted_residue_dry_matter_lignin_fraction
        (0.6, 0),  # no rainfall
        (0, 0),  # neither
    ],
)
def test_determine_soil_residue_lignin_fraction(
    weighted_residue_dry_matter_lignin_fraction: float, rainfall: float
) -> None:
    """Tests that the the fraction of soil residue that's comprised of lignin was calculated correctly"""
    expected = max(0.0, weighted_residue_dry_matter_lignin_fraction - 0.15 * rainfall * 0.01)
    assert expected == ResiduePartition._determine_soil_residue_lignin_fraction(
        weighted_residue_dry_matter_lignin_fraction, rainfall
    )


@pytest.mark.parametrize(
    "plant_lignin_nitrogen_ratio, weighted_residue_dry_matter_lignin_fraction, "
    "soil_residue_lignin_fraction, nitrogen_fraction_plant_residue",
    [
        (0.6, 0.5, 0.45, 0.4),  # default
        (0.1, 0.05, 0.045, 0.4),  # lower ratio
        (0, 0, 0, 0.4),  # no ratio
        (0.6, 0.5, 0.45, 0),  # zero nitrogen_fraction_plant_residue
        (0.6, 0.5, 0.45, -1),  # invalid nitrogen_fraction_plant_residue
    ],
)
def test_determine_soil_lignin_to_nitrogen_ratio(
    plant_lignin_nitrogen_ratio: float,
    weighted_residue_dry_matter_lignin_fraction: float,
    soil_residue_lignin_fraction: float,
    nitrogen_fraction_plant_residue: float,
) -> None:
    """Tests that the soil lignin to nitrogen fraction is calculated correctly"""
    if 0 < nitrogen_fraction_plant_residue <= 1:
        expected = plant_lignin_nitrogen_ratio * weighted_residue_dry_matter_lignin_fraction + (
            ((soil_residue_lignin_fraction / 100) / nitrogen_fraction_plant_residue) / 100
        ) * (1 - weighted_residue_dry_matter_lignin_fraction)
        assert expected == ResiduePartition._determine_soil_lignin_to_nitrogen_fraction(
            plant_lignin_nitrogen_ratio,
            weighted_residue_dry_matter_lignin_fraction,
            soil_residue_lignin_fraction,
            nitrogen_fraction_plant_residue,
        )
    elif nitrogen_fraction_plant_residue == 0:
        expected = 0
        assert expected == ResiduePartition._determine_soil_lignin_to_nitrogen_fraction(
            plant_lignin_nitrogen_ratio,
            weighted_residue_dry_matter_lignin_fraction,
            soil_residue_lignin_fraction,
            nitrogen_fraction_plant_residue,
        )
    else:
        # case of invalid input
        with pytest.raises(ValueError) as e:
            ResiduePartition._determine_soil_lignin_to_nitrogen_fraction(
                plant_lignin_nitrogen_ratio,
                weighted_residue_dry_matter_lignin_fraction,
                soil_residue_lignin_fraction,
                nitrogen_fraction_plant_residue,
            )
        expected = "Expected nitrogen_fraction_plant_residue to be between 0.0-1.0, received " + str(
            nitrogen_fraction_plant_residue
        )
        assert expected == str(e.value)


@pytest.mark.parametrize(
    "soil_lignin_to_nitrogen_ratio",
    [7, 56, 35.8, 0],  # lower values  # higher values  # arbitrary  # zero ratio
)
def test_determine_soil_residue_metabolic_fraction(
    soil_lignin_to_nitrogen_ratio: float,
) -> None:
    """test that the fraction of soil residue that is metabolic was calculated correctly"""
    expected = max(0.0, 0.85 - 0.18 * soil_lignin_to_nitrogen_ratio)
    assert expected == ResiduePartition._determine_soil_residue_metabolic_fraction(soil_lignin_to_nitrogen_ratio)


@pytest.mark.parametrize(
    "soil_metabolic_carbon_amount, plant_metabolic_to_soil_carbon_amount,"
    "root_biomass, soil_residue_metabolic_fraction, "
    "soil_metabolic_to_active_carbon_amount",
    [
        (50, 60, 70, 0.55, 0.5),  # larger amount
        (15, 16, 17, 0.96, 0.99),  # larger fraction
        (0, 14, 12, 0.8, 0.7),  # no soil_metabolic_carbon_amount at all
    ],
)
def test_determine_soil_metabolic_carbon_amount(
    soil_metabolic_carbon_amount: float,
    plant_metabolic_to_soil_carbon_amount: float,
    root_biomass: float,
    soil_residue_metabolic_fraction: float,
    soil_metabolic_to_active_carbon_amount: float,
) -> None:
    """Test that the amount of soil metabolic carbon was updated correctly"""
    expected = (
        soil_metabolic_carbon_amount
        + plant_metabolic_to_soil_carbon_amount
        + (root_biomass * soil_residue_metabolic_fraction)
        - soil_metabolic_to_active_carbon_amount
    )

    assert expected == ResiduePartition._determine_soil_metabolic_carbon_amount(
        soil_metabolic_carbon_amount,
        plant_metabolic_to_soil_carbon_amount,
        root_biomass,
        soil_residue_metabolic_fraction,
        soil_metabolic_to_active_carbon_amount,
    )


@pytest.mark.parametrize(
    "decomposition_moisture_effect, decomposition_temperature_effect, " "soil_metabolic_carbon_amount",
    [
        (3, 8, 7),
        (60, 64, 85),
        (1.8, 1.1, 3.27),
    ],
)
def test_determine_soil_metabolic_to_active_carbon_amount(
    decomposition_moisture_effect: float,
    decomposition_temperature_effect: float,
    soil_metabolic_carbon_amount: float,
) -> None:
    """Tests that the amount of soil metabolic carbon decomposed into active carbon was calculated correctly"""
    soil_metabolic_active_carbon_rate = 0.35
    expected = (
        decomposition_temperature_effect
        * decomposition_moisture_effect
        * soil_metabolic_carbon_amount
        * soil_metabolic_active_carbon_rate
    )
    assert expected == ResiduePartition._determine_soil_metabolic_to_active_carbon_amount(
        decomposition_moisture_effect,
        decomposition_temperature_effect,
        soil_metabolic_carbon_amount,
    )


@pytest.mark.parametrize(
    "soil_structural_carbon_amount, decomposition_moisture_effect," "decomposition_temperature_effect",
    [
        (3, 8, 7),
        (60, 64, 85),
        (1.8, 1.1, 3.2),
    ],
)
def test_determine_soil_structural_to_slow_active_carbon_amount(
    decomposition_moisture_effect: float,
    decomposition_temperature_effect: float,
    soil_structural_carbon_amount: float,
) -> None:
    """Tests that the amount of soil structural carbon decomposed into slow or active carbon was calculated correctly"""
    soil_structural_to_slow_or_active_rate = 0.094
    expected = (
        decomposition_moisture_effect
        * decomposition_temperature_effect
        * soil_structural_carbon_amount
        * soil_structural_to_slow_or_active_rate
    )
    assert expected == ResiduePartition._determine_soil_structural_to_slow_active_carbon_amount(
        decomposition_moisture_effect,
        decomposition_temperature_effect,
        soil_structural_carbon_amount,
    )


@pytest.mark.parametrize(
    "soil_residue_metabolic_fraction, structural_carbon_transfer_amount,"
    "soil_structural_to_active_carbon_amount, soil_structural_to_slow_carbon_amount, "
    "root_biomass, soil_structural_carbon_amount",
    [
        (3, 8, 7, 1, 2, 5),
        (60, 64, 85, 40, 30, 99),
        (1.8, 1.1, 3.2, 0.8, 0.7, 0.3),
    ],
)
def test_determine_soil_structural_carbon_amount(
    soil_residue_metabolic_fraction: float,
    structural_carbon_transfer_amount: float,
    soil_structural_to_active_carbon_amount: float,
    soil_structural_to_slow_carbon_amount: float,
    root_biomass: float,
    soil_structural_carbon_amount: float,
) -> None:
    """Tests that the updated soil structural carbon amount is calculated correctly"""
    expected = (
        soil_structural_carbon_amount
        + structural_carbon_transfer_amount
        + root_biomass * (1 - soil_residue_metabolic_fraction)
        - soil_structural_to_active_carbon_amount
        - soil_structural_to_slow_carbon_amount
    )

    assert expected == ResiduePartition._determine_soil_structural_carbon_amount(
        soil_residue_metabolic_fraction,
        structural_carbon_transfer_amount,
        soil_structural_to_active_carbon_amount,
        soil_structural_to_slow_carbon_amount,
        root_biomass,
        soil_structural_carbon_amount,
    )


@pytest.mark.parametrize(
    "residues,metabolic_frac,expected_metabolic,expected_structural,decomp_rate_set",
    [
        ([10.0] * 3, 0.5, [5.0] * 3, [5.0] * 3, True),
        ([10.0, 50.0, 30.0], 0.25, [2.5, 12.5, 7.5], [7.5, 37.5, 22.5], True),
        ([0.0] * 3, 0.4, [0.0] * 3, [0.0] * 3, False),
    ],
)
def test_add_litter_to_pools(
    mocker: MockerFixture,
    soil_data: SoilData,
    residues: list[float],
    metabolic_frac: float,
    expected_metabolic: list[float],
    expected_structural: list[float],
    decomp_rate_set: bool,
) -> None:
    """Tests that litter is partitioned correctly between metabolic and structural pools."""
    soil_data.set_vectorized_layer_attribute("plant_residue", residues)
    soil_data.plant_residue_metabolic_fraction = metabolic_frac
    partitioner = ResiduePartition(soil_data)
    set_decomp_rate = mocker.patch.object(ResiduePartition, "_set_soil_structural_litter_decomposition_rate")

    partitioner._add_litter_to_pools()

    actual_metabolic = soil_data.get_vectorized_layer_attribute("metabolic_litter_amount")
    actual_structural = soil_data.get_vectorized_layer_attribute("structural_litter_amount")
    assert actual_metabolic == expected_metabolic
    assert actual_structural == expected_structural
    set_decomp_rate.assert_called_once() if decomp_rate_set else set_decomp_rate.assert_not_called()


@pytest.mark.parametrize("rainfall", [0.0, 1.0, 12.0])
def test_add_residue_to_pools(rainfall: float) -> None:
    """Tests that residue is correctly added to pools."""
    data = MagicMock(SoilData)
    data.plant_residue_lignin_composition = 25.0
    data.plant_residue_lignin_composition = 0.3
    data.plant_residue_metabolic_fraction = 0.5
    data.all_residue = 100.0
    data.crop_yield_nitrogen = 50.0
    partitioner = ResiduePartition(data)

    with (
        patch.object(
            ResiduePartition,
            "_determine_plant_residue_lignin_composition",
            new_callable=MagicMock,
            return_value=20.0,
        ) as lignin,
        patch.object(
            ResiduePartition,
            "_determine_plant_lignin_nitrogen_fraction",
            new_callable=MagicMock,
            return_value=0.4,
        ) as lignin_nitrogen_frac,
        patch.object(
            ResiduePartition,
            "_determine_plant_residue_metabolic_fraction",
            new_callable=MagicMock,
            return_value=0.6,
        ) as metabolic_fraction,
        patch.object(ResiduePartition, "_add_litter_to_pools") as add_litter,
    ):
        partitioner.add_residue_to_pools(rainfall)

    assert data.plant_residue_lignin_composition == 20.0
    assert data.plant_lignin_nitrogen_ratio == 0.4
    assert data.plant_residue_metabolic_fraction == 0.6
    assert lignin.call_count == 1
    assert lignin_nitrogen_frac.call_count == 1
    assert metabolic_fraction.call_count == 1
    assert add_litter.call_count == 1


@pytest.mark.parametrize(
    "layers",
    [
        [
            LayerData(
                top_depth=0,
                bottom_depth=40,
                soil_water_concentration=1.8,
                field_capacity_water_concentration=1.6,
                wilting_point_water_concentration=0.9,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
            LayerData(
                top_depth=40,
                bottom_depth=120,
                soil_water_concentration=0.9,
                field_capacity_water_concentration=1.2,
                wilting_point_water_concentration=0.8,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
            LayerData(
                top_depth=120,
                bottom_depth=200,
                soil_water_concentration=0.8,
                field_capacity_water_concentration=0.8,
                wilting_point_water_concentration=0.3,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
        ],
        [
            LayerData(
                top_depth=0,
                bottom_depth=30,
                soil_water_concentration=2.8,
                field_capacity_water_concentration=2.3,
                wilting_point_water_concentration=1.8,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
            LayerData(
                top_depth=30,
                bottom_depth=150,
                soil_water_concentration=1.9,
                field_capacity_water_concentration=1.8,
                wilting_point_water_concentration=0.8,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
            LayerData(
                top_depth=150,
                bottom_depth=220,
                soil_water_concentration=0.8,
                field_capacity_water_concentration=1,
                wilting_point_water_concentration=0.2,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
        ],
        [
            LayerData(
                top_depth=0,
                bottom_depth=80,
                soil_water_concentration=2.3,
                field_capacity_water_concentration=2.9,
                wilting_point_water_concentration=1.8,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
            LayerData(
                top_depth=80,
                bottom_depth=200,
                soil_water_concentration=1.4,
                field_capacity_water_concentration=1.8,
                wilting_point_water_concentration=0.8,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
            LayerData(
                top_depth=200,
                bottom_depth=220,
                soil_water_concentration=0.8,
                field_capacity_water_concentration=1,
                wilting_point_water_concentration=0.6,
                tillage_fraction=0.2,
                field_size=1.1,
            ),
        ],
    ],
)
def test_partition_residue(layers: list[LayerData], mock_crop_data: CropData) -> None:
    """Testing if main routine correctly updates the attributes."""
    data = SoilData(soil_layers=layers, field_size=1.1)
    crop_management = CropManagement(crop_data=mock_crop_data)
    data.plant_surface_residue = crop_management.yield_residue or 0
    data.plant_root_residue = mock_crop_data.root_biomass or 0
    partition = ResiduePartition(data)
    rainfall = 10

    ResiduePartition._determine_plant_metabolic_active_carbon_usage = MagicMock(return_value=2.1)
    ResiduePartition._determine_plant_metabolic_carbon_amount = MagicMock(return_value=2.4)
    ResiduePartition._determine_plant_structural_to_slow_or_active_rate = MagicMock(return_value=0.58)
    ResiduePartition._determine_plant_structural_carbon_amount = MagicMock(return_value=2.5)
    ResiduePartition._determine_plant_structural_to_slow_active_carbon_amount = MagicMock(return_value=2.6)
    ResiduePartition._determine_weighted_residue_dry_matter_lignin_fraction = MagicMock(return_value=0.59)
    ResiduePartition._determine_soil_residue_lignin_fraction = MagicMock(return_value=0.6)
    ResiduePartition._determine_soil_lignin_to_nitrogen_fraction = MagicMock(return_value=0.61)
    ResiduePartition._determine_soil_residue_metabolic_fraction = MagicMock(return_value=0.62)
    ResiduePartition._determine_soil_metabolic_to_active_carbon_amount = MagicMock(return_value=2.7)
    ResiduePartition._determine_soil_metabolic_carbon_amount = MagicMock(return_value=2.8)
    ResiduePartition._determine_soil_structural_to_slow_active_carbon_amount = MagicMock(return_value=2.9)
    ResiduePartition._determine_soil_structural_carbon_amount = MagicMock(return_value=3)

    # first_layer_yield_residue_value = crop.yield_residue
    partition.partition_residue(rainfall)

    # Checking if methods are called correct number of times
    assert ResiduePartition._determine_plant_metabolic_active_carbon_usage.call_count == 1

    assert ResiduePartition._determine_plant_metabolic_carbon_amount.call_count == 1
    assert ResiduePartition._determine_plant_structural_to_slow_or_active_rate.call_count == 1
    assert ResiduePartition._determine_plant_structural_carbon_amount.call_count == 1
    assert ResiduePartition._determine_plant_structural_to_slow_active_carbon_amount.call_count == 2
    assert ResiduePartition._determine_weighted_residue_dry_matter_lignin_fraction.call_count == len(layers)
    assert ResiduePartition._determine_soil_residue_lignin_fraction.call_count == len(layers) - 1
    assert ResiduePartition._determine_soil_lignin_to_nitrogen_fraction.call_count == len(layers) - 1
    assert ResiduePartition._determine_soil_residue_metabolic_fraction.call_count == len(layers) - 1
    assert ResiduePartition._determine_soil_metabolic_to_active_carbon_amount.call_count == len(layers) - 1
    assert ResiduePartition._determine_soil_metabolic_carbon_amount.call_count == len(layers) - 1
    assert ResiduePartition._determine_soil_structural_to_slow_active_carbon_amount.call_count == (len(layers) - 1) * 2
    assert ResiduePartition._determine_soil_structural_carbon_amount.call_count == len(layers) - 1

    layer = data.soil_layers[0]
    assert layer.plant_metabolic_active_carbon_usage == 2.1
    assert layer.plant_metabolic_to_soil_carbon_amount == 0.0
    assert layer.structural_carbon_transfer_amount == 0.0
    assert layer.soil_dry_matter_residue_amount == 0.0
    assert layer.metabolic_litter_amount == 2.4
    assert layer.plant_structural_to_slow_or_active_rate == 0.58
    assert layer.structural_litter_amount == 2.5
    assert layer.plant_structural_active_carbon_usage == 2.6
    assert layer.plant_structural_slow_carbon_usage == 2.6
    assert layer.weighted_residue_dry_matter_lignin_fraction == 0.59
    assert layer.soil_residue_lignin_fraction == 0.17
    assert layer.soil_lignin_to_nitrogen_fraction == 0.0
    assert layer.soil_residue_metabolic_fraction == 0.0
    assert layer.soil_metabolic_active_carbon_usage == 0.0
    assert layer.soil_metabolic_carbon_amount == 0.0
    assert layer.soil_structural_active_carbon_usage == 0.0
    assert layer.soil_structural_slow_carbon_usage == 0.0
    assert layer.soil_structural_carbon_amount == 0.0

    for layer in data.soil_layers[1:]:
        assert layer.plant_metabolic_active_carbon_usage == 0.0
        assert layer.plant_metabolic_to_soil_carbon_amount == 0.0
        assert layer.structural_carbon_transfer_amount == 0.0
        assert layer.soil_dry_matter_residue_amount == 0.0
        assert layer.metabolic_litter_amount == 2.8
        assert layer.plant_structural_to_slow_or_active_rate == 0.0
        assert layer.structural_litter_amount == 3
        assert layer.plant_structural_active_carbon_usage == 0.0
        assert layer.plant_structural_slow_carbon_usage == 0.0
        assert layer.weighted_residue_dry_matter_lignin_fraction == 0.59
        assert layer.soil_residue_lignin_fraction == 0.6
        assert layer.soil_lignin_to_nitrogen_fraction == 0.61
        assert layer.soil_residue_metabolic_fraction == 0.62
        assert layer.soil_metabolic_active_carbon_usage == 2.7
        assert layer.soil_metabolic_carbon_amount == 0.0
        assert layer.soil_structural_active_carbon_usage == 2.9
        assert layer.soil_structural_slow_carbon_usage == 2.9
        assert layer.soil_structural_carbon_amount == 0.0
