import pytest

from RUFAS.biophysical.manure.digester.anaerobic_digester import AnaerobicDigester


# @pytest.mark.parametrize(
#     "temp, moisture_frac, set_point, expected",
#     [
#         (),
#     ]
# )
# def test_calculate_specific_input_energy(temp: float, moisture_frac: float, set_point: float, expected: float) -> None:
#     """Test that the specific input energy of an Anaerobic Digester is calculated correctly."""
#     actual = AnaerobicDigester._calculate_specific_input_energy(temp, moisture_frac, set_point)

#     assert actual == expected


@pytest.mark.parametrize("temp, expected", [(30.0, 30.0), (10.0, 10.0), (0.0, 4.0)])
def test_bind_influent_temperature(temp: float, expected: float) -> None:
    """Test that the influent temperature is bounded correctly."""
    actual = AnaerobicDigester._bind_influent_temperature(temp)

    assert actual == expected
