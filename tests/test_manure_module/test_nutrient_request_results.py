from __future__ import annotations

import pytest
from pytest import approx

from RUFAS.routines.manure.manure_nutrients.nutrient_request_results import NutrientRequestResults


def test_nutrient_request_results_default_init() -> None:
    """
    Unit test for the NutrientRequestResults class in nutrient_request_results.py.

    Test the initialization of the NutrientRequestResults dataclass and
    verify that the default values are stored correctly.

    """
    # Act
    request_results = NutrientRequestResults()

    # Assert
    assert request_results.nitrogen == approx(0.0)
    assert request_results.phosphorus == approx(0.0)
    assert request_results.total_manure_mass == approx(0.0)
    assert request_results.organic_nitrogen_fraction == approx(0.7)
    assert request_results.inorganic_nitrogen_fraction == approx(0.3)
    assert request_results.ammonium_nitrogen_fraction == approx(1.0)
    assert request_results.organic_phosphorus_fraction == approx(0.5)
    assert request_results.inorganic_phosphorus_fraction == approx(0.5)
    assert request_results.dry_matter == approx(0.0)
    assert request_results.dry_matter_fraction == approx(0.0)


@pytest.mark.parametrize(
    "nitrogen, phosphorus, total_manure_mass, "
    "organic_nitrogen_fraction, inorganic_nitrogen_fraction, ammonium_nitrogen_fraction, "
    "organic_phosphorus_fraction, inorganic_phosphorus_fraction, "
    "dry_matter, dry_matter_fraction",
    [
        (1.0, 2.0, 3.0, 0.4, 0.6, 0.7, 0.3, 0.7, 4.0, 0.5),  # All attributes have some values
        (1.0, 2.0, 3.0, 0.6, 0.4, 0.7, 0.4, 0.6, 4.0, 0.5),  # Switch organic and inorganic fractions
        (1.0, 2.0, 3.0, 0.5, 0.5, 0.5, 0.5, 0.5, 4.0, 0.5),  # All fractions are equal
        (1.0, 2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 0.0, 4.0, 0.1),  # Test extremes of fractions
        (1.0, 2.0, 3.0, 0.0, 1.0, 1.0, 0.0, 1.0, 4.0, 0.9),  # Test other extremes of fractions
    ]
)
def test_nutrient_request_results_init(
        nitrogen: float, phosphorus: float, total_manure_mass: float,
        organic_nitrogen_fraction: float, inorganic_nitrogen_fraction: float, ammonium_nitrogen_fraction: float,
        organic_phosphorus_fraction: float, inorganic_phosphorus_fraction: float,
        dry_matter: float, dry_matter_fraction: float
) -> None:
    """
    Unit test for the NutrientRequestResults class in nutrient_request_results.py.

    Test the initialization of the NutrientRequestResults dataclass and
    verify that the values are stored correctly.

    """
    # Act
    request_results = NutrientRequestResults(
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        total_manure_mass=total_manure_mass,
        organic_nitrogen_fraction=organic_nitrogen_fraction,
        inorganic_nitrogen_fraction=inorganic_nitrogen_fraction,
        ammonium_nitrogen_fraction=ammonium_nitrogen_fraction,
        organic_phosphorus_fraction=organic_phosphorus_fraction,
        inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
        dry_matter=dry_matter,
        dry_matter_fraction=dry_matter_fraction,
    )

    # Assert
    assert request_results.nitrogen == approx(nitrogen)
    assert request_results.phosphorus == approx(phosphorus)
    assert request_results.total_manure_mass == approx(total_manure_mass)
    assert request_results.organic_nitrogen_fraction == approx(organic_nitrogen_fraction)
    assert request_results.inorganic_nitrogen_fraction == approx(inorganic_nitrogen_fraction)
    assert request_results.ammonium_nitrogen_fraction == approx(ammonium_nitrogen_fraction)
    assert request_results.organic_phosphorus_fraction == approx(organic_phosphorus_fraction)
    assert request_results.inorganic_phosphorus_fraction == approx(inorganic_phosphorus_fraction)
    assert request_results.dry_matter == approx(dry_matter)
    assert request_results.dry_matter_fraction == approx(dry_matter_fraction)


@pytest.mark.parametrize(
    "field_to_test_negative", ['nitrogen', 'phosphorus', 'total_manure_mass', 'dry_matter']
)
def test_nutrient_request_results_init_with_negative_non_fractional_fields(field_to_test_negative: str) -> None:
    """
    Unit test for the __post_init__ method in the NutrientRequestResults class.

    Test the validation in the initialization of the NutrientRequestResults class,
    expecting it to raise an error when a non-fractional field is negative.

    """
    # Arrange
    # Initialize nutrient values with all values non-negative
    nutrient_values = {'nitrogen': 1.0, 'phosphorus': 2.0, 'total_manure_mass': 3.0,
                       'organic_nitrogen_fraction': 0.4, 'inorganic_nitrogen_fraction': 0.6,
                       'ammonium_nitrogen_fraction': 0.3, 'organic_phosphorus_fraction': 0.7,
                       'inorganic_phosphorus_fraction': 0.3, 'dry_matter': 4.0, 'dry_matter_fraction': 0.6}

    # Set the field to be tested to a negative value
    nutrient_values[field_to_test_negative] = -1.0

    # Act and assert
    with pytest.raises(ValueError, match=f'{field_to_test_negative} must be non-negative.'):
        NutrientRequestResults(**nutrient_values)


@pytest.mark.parametrize(
    "field_to_test_out_of_range",
    ['organic_nitrogen_fraction', 'inorganic_nitrogen_fraction',
     'ammonium_nitrogen_fraction', 'organic_phosphorus_fraction',
     'inorganic_phosphorus_fraction', 'dry_matter_fraction']
)
def test_nutrient_request_results_init_with_out_of_range_fractional_fields(field_to_test_out_of_range: str) -> None:
    """
    Unit test for the __post_init__ method in the NutrientRequestResults class.

    Test the validation in the initialization of the NutrientRequestResults class,
    expecting it to raise an error when a fractional field is not between 0 and 1.

    """
    # Arrange
    # Initialize nutrient values with all values in valid range
    nutrient_values = {'nitrogen': 1.0, 'phosphorus': 2.0, 'total_manure_mass': 3.0,
                       'organic_nitrogen_fraction': 0.4, 'inorganic_nitrogen_fraction': 0.6,
                       'ammonium_nitrogen_fraction': 0.3, 'organic_phosphorus_fraction': 0.7,
                       'inorganic_phosphorus_fraction': 0.3, 'dry_matter': 4.0, 'dry_matter_fraction': 0.6}

    values_to_test = [-100.0, -10.0, -1.0, -0.1, -0.01, -0.001, 1.001, 1.01, 1.1, 10.0, 100.0]

    for value in values_to_test:
        # Set the field to be tested to be out of range
        nutrient_values[field_to_test_out_of_range] = value

        # Act and assert
        with pytest.raises(ValueError, match=f'{field_to_test_out_of_range} must be between 0 and 1.'):
            NutrientRequestResults(**nutrient_values)


@pytest.mark.parametrize(
    "fraction_values, nutrient_type",
    [
        # Test cases for nitrogen
        ((0.3, 0.4), 'nitrogen'),  # Sum is less than 1
        ((0.6, 0.5), 'nitrogen'),  # Sum is greater than 1
        ((0.0, 0.0), 'nitrogen'),  # Sum is 0
        # Test cases for phosphorus
        ((0.3, 0.4), 'phosphorus'),  # Sum is less than 1
        ((0.6, 0.5), 'phosphorus'),  # Sum is greater than 1
        ((0.0, 0.0), 'phosphorus'),  # Sum is 0
    ],
)
def test_nutrient_request_results_init_with_unequal_fractions(fraction_values: tuple[float, float], nutrient_type: str):
    """
    Unit test for the __post_init__ method in the NutrientRequestResults class.

    Test the validation in the initialization of the NutrientRequestResults class,
    expecting it to raise an error when the sum of organic and inorganic fractions
    does not equal 1.

    """
    # Arrange
    organic_fraction, inorganic_fraction = fraction_values
    nutrient_values = {'nitrogen': 1.0, 'phosphorus': 2.0, 'total_manure_mass': 3.0,
                       'organic_nitrogen_fraction': 0.5, 'inorganic_nitrogen_fraction': 0.5,
                       'ammonium_nitrogen_fraction': 0.3, 'organic_phosphorus_fraction': 0.5,
                       'inorganic_phosphorus_fraction': 0.5, 'dry_matter': 4.0, 'dry_matter_fraction': 0.6}

    # Set the fractions for the nutrient type being tested
    nutrient_values[f'organic_{nutrient_type}_fraction'] = organic_fraction
    nutrient_values[f'inorganic_{nutrient_type}_fraction'] = inorganic_fraction

    # Act and assert
    with pytest.raises(ValueError, match=f'Sum of organic and inorganic {nutrient_type} fractions must be 1.'):
        NutrientRequestResults(**nutrient_values)
