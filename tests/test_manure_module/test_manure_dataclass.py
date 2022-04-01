import pytest

from RUFAS.routines.manure_management.data_models.manure import Manure


@pytest.fixture
def default_manure_obj() -> Manure:
    return Manure()


def test_construct_a_default_manure_object(default_manure_obj):
    assert default_manure_obj.U == 0
    assert default_manure_obj.TAN_s == 0
    assert default_manure_obj.MN == 0
    assert default_manure_obj.Mkg == 0
    assert default_manure_obj.TSd == 0
    assert default_manure_obj.VSd == 0
    assert default_manure_obj.VSnd == 0
    assert default_manure_obj.WIP_frac == 0
    assert default_manure_obj.WOP_frac == 0
    assert default_manure_obj.p_excrt_manure == 0
    assert default_manure_obj.p_frac == 0
    assert default_manure_obj.K_manure == 0
    assert default_manure_obj.CH4_manure == 0


def test_construct_a_manure_object_from_dictionary():
    d = {
        "U": 1,
        "TAN_s": 2,
        "MN": 3,
        "Mkg": 0,
        "TSd": 0,
        "VSd": 6,
        "VSnd": 0,
        "WIP_frac": 0,
        "WOP_frac": 0,
        "p_excrt_manure": 0,
        "p_frac": 0,
        "K_manure": 0,
        "CH4_manure": 0
    }
    manure = Manure(**d)
    assert manure.U == 1
    assert manure.TAN_s == 2
    assert manure.MN == 3
    assert manure.VSd == 6
    remaining_attrs = ['Mkg', 'TSd', 'VSnd', 'WIP_frac',
                       'WOP_frac', 'p_excrt_manure', 'p_frac',
                       'K_manure', 'CH4_manure']
    for attr in remaining_attrs:
        assert getattr(manure, attr) == 0


def test_add_a_manure_to_a_non_manure_should_fail(default_manure_obj):
    with pytest.raises(TypeError, match=r'Cannot add a non-Manure object to a Manure object.'):
        default_manure_obj + dict()


def test_add_two_default_manure_objects_should_return_a_different_but_equal_manure_object(default_manure_obj):
    total = default_manure_obj + default_manure_obj
    assert total is not default_manure_obj
    assert total == default_manure_obj


def test_add_two_valid_manure_objects_should_return_correct_sum():
    manure1 = Manure(U=1, TAN_s=2, MN=3)
    manure2 = Manure(U=4, MN=6)
    total = manure1 + manure2
    assert total.U == 5
    assert total.TAN_s == 2
    assert total.MN == 9
    remaining_attrs = ['Mkg', 'TSd', 'VSd', 'VSnd', 'WIP_frac',
                       'WOP_frac', 'p_excrt_manure', 'p_frac',
                       'K_manure', 'CH4_manure']
    for attr in remaining_attrs:
        assert getattr(total, attr) == 0
