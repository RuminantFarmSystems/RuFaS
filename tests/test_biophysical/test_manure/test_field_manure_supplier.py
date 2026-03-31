import pytest

from RUFAS.biophysical.manure.field_manure_supplier import FieldManureSupplier
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.manure_types import ManureType


@pytest.mark.parametrize(
    "nutrients,expected_result",
    [
        (
            NutrientRequest(
                nitrogen=100.0, phosphorus=50.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            NutrientRequestResults(
                nitrogen=100,
                phosphorus=40.909,
                dry_matter=2090.9,
                total_manure_mass=45454.0751,
                dry_matter_fraction=0.046000276,
            ),
        ),
        (
            NutrientRequest(
                nitrogen=100.0, phosphorus=40.0, manure_type=ManureType.SOLID, use_supplemental_manure=False
            ),
            NutrientRequestResults(
                nitrogen=80.0005924,
                phosphorus=40.0,
                dry_matter=5401.32,
                total_manure_mass=13335.85907999,
                dry_matter_fraction=0.4050222762,
            ),
        ),
        (
            NutrientRequest(
                nitrogen=100.0, phosphorus=0.0, manure_type=ManureType.SOLID, use_supplemental_manure=False
            ),
            NutrientRequestResults(
                nitrogen=100.0,
                phosphorus=49.99962972,
                dry_matter=6751.6,
                total_manure_mass=16669.7004,
                dry_matter_fraction=0.4050222762,
            ),
        ),
        (
            NutrientRequest(
                nitrogen=0.0, phosphorus=33.0, manure_type=ManureType.LIQUID, use_supplemental_manure=False
            ),
            NutrientRequestResults(
                nitrogen=80.66684202,
                phosphorus=33.0,
                dry_matter=1686.663,
                total_manure_mass=36666.366957,
                dry_matter_fraction=0.046000276,
            ),
        ),
    ],
)
def test_request_nutrients(nutrients: NutrientRequest, expected_result: NutrientRequestResults) -> None:
    """Tests that manure nutrient amounts are formulated correctly."""
    field_manure_supplier = FieldManureSupplier()

    actual = field_manure_supplier.request_nutrients(nutrients)

    assert pytest.approx(actual.nitrogen) == expected_result.nitrogen
    assert pytest.approx(actual.phosphorus) == expected_result.phosphorus
    assert pytest.approx(actual.dry_matter) == expected_result.dry_matter
    assert pytest.approx(actual.total_manure_mass) == expected_result.total_manure_mass
    assert pytest.approx(actual.dry_matter_fraction) == expected_result.dry_matter_fraction
