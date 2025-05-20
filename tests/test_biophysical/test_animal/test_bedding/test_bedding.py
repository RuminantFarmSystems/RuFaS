import pytest

from RUFAS.biophysical.animal.bedding.bedding import Bedding
from RUFAS.biophysical.animal.data_types.bedding_types import BeddingType


@pytest.fixture()
def bedding() -> Bedding:
    return Bedding(
        name="dummy_name",
        bedding_mass_per_day=1.1,
        bedding_density=2.2,
        bedding_dry_matter_content=0.33,
        bedding_carbon_fraction=0.44,
        bedding_phosphorus_content=0.55,
        bedding_type=BeddingType.STRAW,
        sand_removal_efficiency=0.66,
    )


@pytest.mark.parametrize(
    "name, bedding_mass_per_day, bedding_density, bedding_dry_matter_content, bedding_carbon_fraction,"
    "bedding_phosphorus_content, bedding_type, sand_removal_efficiency",
    [
        ("dummy_name", 1.1, 2.2, 3.3, 4.4, 5.5, BeddingType.STRAW, 6.6),
        ("dummy_name", 1.1, 2.2, 3.3, 4.4, 5.5, BeddingType.SAND, 6.6),
        ("dummy_name", 1.1, 2.2, 3.3, 4.4, 5.5, BeddingType.NONE, 6.6),
    ],
)
def test_init(
    name: str,
    bedding_mass_per_day: float,
    bedding_density: float,
    bedding_dry_matter_content: float,
    bedding_carbon_fraction: float,
    bedding_phosphorus_content: float,
    bedding_type: BeddingType,
    sand_removal_efficiency: float,
) -> None:
    bedding = Bedding(
        name,
        bedding_mass_per_day,
        bedding_density,
        bedding_dry_matter_content,
        bedding_carbon_fraction,
        bedding_phosphorus_content,
        bedding_type,
        sand_removal_efficiency,
    )
    assert bedding.name == name
    assert bedding.bedding_mass_per_day == bedding_mass_per_day
    assert bedding.bedding_density == bedding_density
    assert bedding.bedding_dry_matter_content == bedding_dry_matter_content
    assert bedding.bedding_carbon_fraction == bedding_carbon_fraction
    assert bedding.bedding_phosphorus_content == bedding_phosphorus_content
    assert bedding.bedding_type == bedding_type
    if bedding_type == BeddingType.SAND:
        assert bedding.sand_removal_efficiency == sand_removal_efficiency
    else:
        assert bedding.sand_removal_efficiency == 0.0


@pytest.mark.parametrize(
    "num_animals, bedding_type, expected_result",
    [
        (10, BeddingType.NONE, 0.0),
        (25, BeddingType.SAND, 27.5),
        (388, BeddingType.STRAW, 426.8),
    ],
)
def test_calculate_total_bedding_mass(
    num_animals: int, bedding_type: BeddingType, expected_result: float, bedding: Bedding
) -> None:
    bedding.bedding_type = bedding_type
    assert pytest.approx(bedding.calculate_total_bedding_mass(num_animals)) == expected_result


@pytest.mark.parametrize(
    "num_animals, bedding_type, expected_result",
    [
        (10, BeddingType.NONE, 0.0),
        (25, BeddingType.SAND, 12.5),
        (388, BeddingType.STRAW, 194),
    ],
)
def test_calculate_total_bedding_volume(
    num_animals: int, bedding_type: BeddingType, expected_result: float, bedding: Bedding
) -> None:
    bedding.bedding_type = bedding_type
    assert pytest.approx(bedding.calculate_total_bedding_volume(num_animals)) == expected_result


@pytest.mark.parametrize(
    "num_animals, bedding_type, expected_result",
    [
        (10, BeddingType.NONE, 0.0),
        (25, BeddingType.SAND, 9.075),
        (388, BeddingType.STRAW, 140.844),
    ],
)
def test_calculate_total_bedding_dry_solids(
    num_animals: int, bedding_type: BeddingType, expected_result: float, bedding: Bedding
) -> None:
    bedding.bedding_type = bedding_type
    assert pytest.approx(bedding.calculate_total_bedding_dry_solids(num_animals)) == expected_result


@pytest.mark.parametrize(
    "num_animals, bedding_type, expected_result",
    [
        (10, BeddingType.NONE, 0.0),
        (25, BeddingType.SAND, 18.425),
        (388, BeddingType.STRAW, 285.956),
    ],
)
def test_calculate_bedding_water(
    num_animals: int, bedding_type: BeddingType, expected_result: float, bedding: Bedding
) -> None:
    bedding.bedding_type = bedding_type
    assert pytest.approx(bedding.calculate_bedding_water(num_animals)) == expected_result
