from pytest import fixture, approx, raises

from RUFAS.routines.manure_management.data_models.daily_variables import DailyVariables


@fixture
def default_daily_vars_obj() -> DailyVariables:
    return DailyVariables()


def test_daily_vars_init_should_get_a_daily_vars_obj_with_zero_attrs_when_no_params_given(default_daily_vars_obj):
    attrs = ['CH4_emissions', 'TS', 'VS', 'N', 'P', 'K',
             'TS_liquid', 'VS_liquid', 'N_liquid', 'P_liquid', 'K_liquid',
             'TS_loss', 'VS_loss', 'TS_DM_effluent', 'other_solids', 'WIP', 'WOP',
             'raw_manure', 'initial_manure', 'manure_calc', 'manure_delta',
             'manure_management_balance_difference', 'manure_applied',
             'N_applied', 'P_applied']

    for attr in attrs:
        assert getattr(default_daily_vars_obj, attr) == approx(0.0)


def test_daily_vars_init_should_get_a_daily_vars_obj_with_correct_attr_values_when_a_dictionary_given():
    dv = {
        'CH4_emissions': 1.0,
        'K': 2.0,
        'raw_manure': 100.0
    }
    daily_vars = DailyVariables(**dv)
    assert daily_vars.CH4_emissions == approx(1.0)
    assert daily_vars.K == approx(2.0)
    assert daily_vars.raw_manure == approx(100.0)
    remaining_attrs = ['TS', 'VS', 'N', 'P', 'TS_liquid', 'VS_liquid', 'N_liquid',
                       'P_liquid', 'K_liquid', 'TS_loss', 'VS_loss', 'TS_DM_effluent',
                       'other_solids', 'WIP', 'WOP', 'initial_manure', 'manure_calc',
                       'manure_delta', 'manure_management_balance_difference',
                       'manure_applied', 'N_applied', 'P_applied']
    for attr in remaining_attrs:
        assert getattr(daily_vars, attr) == approx(0.0)


def test_add_should_raise_type_error_when_a_daily_vars_obj_and_a_non_daily_vars_obj_given(default_daily_vars_obj):
    with raises(TypeError, match=r'Cannot add a non-DailyVariables object to a DailyVariables object.'):
        default_daily_vars_obj + dict()


def test_add_should_return_a_different_but_equal_daily_vars_obj_when_two_default_daily_vars_objs_given(
        default_daily_vars_obj):
    total = default_daily_vars_obj + default_daily_vars_obj
    assert total is not default_daily_vars_obj
    assert total == default_daily_vars_obj


def test_add_should_return_correct_summed_attrs_when_two_valid_daily_vars_objs_given():
    daily_vars_1 = DailyVariables(CH4_emissions=1.0, K=2.0, raw_manure=100.0)
    daily_vars_2 = DailyVariables(P=4.0, raw_manure=300.0)

    total = daily_vars_1 + daily_vars_2
    assert total.CH4_emissions == approx(1.0)
    assert total.K == approx(2.0)
    assert total.P == approx(4.0)
    assert total.raw_manure == approx(400.0)
    remaining_attrs = ['TS', 'VS', 'N',
                       'TS_liquid', 'VS_liquid', 'N_liquid', 'P_liquid', 'K_liquid',
                       'TS_loss', 'VS_loss', 'TS_DM_effluent', 'other_solids', 'WIP', 'WOP',
                       'initial_manure', 'manure_calc', 'manure_delta',
                       'manure_management_balance_difference', 'manure_applied',
                       'N_applied', 'P_applied']
    for attr in remaining_attrs:
        assert getattr(total, attr) == approx(0.0)
