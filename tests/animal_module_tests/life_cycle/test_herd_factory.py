import mock
import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.animal.animal_typed_dicts import AnimalBaseInitArgsTypedDict
from RUFAS.routines.animal.life_cycle.herd_factory import HerdFactory
from RUFAS.routines.animal.life_cycle.animal_population import AnimalPopulation
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII


@pytest.fixture
def mock_herd_factory(mocker: MockerFixture) -> HerdFactory:
    """Returns an uninitialized Feed object"""

    mocker.patch('RUFAS.routines.animal.life_cycle.herd_factory.HerdFactory.__init__',
                 return_value=None)
    return HerdFactory()


def test_init(mocker: MockerFixture) -> None:
    mock_im_get_data = mocker.patch("RUFAS.input_manager.InputManager.get_data",
                                    return_value=None)
    mock_animal_population_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_population.AnimalPopulation.__init__",
        return_value=None)
    HerdFactory()

    assert mock_im_get_data.call_count == 4
    assert mock_animal_population_init.call_count == 2


@pytest.mark.parametrize("calf_num", [
    0,
    1,
    8
])
def test_calves_update_wean_day_true(calf_num: int,
                                     mock_herd_factory: HerdFactory,
                                     mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Calf.__init__", return_value=None)
    mock_calves = [Calf(args=mock_animal_base_init_args_typed_dict) for _ in range(calf_num)]

    mock_calf_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.update", return_value=True)
    mock_get_calf_values = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.get_calf_values",
                                        return_value={})
    mock_heiferI_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.__init__",
                                     return_value=None)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.calves = mock_calves
    mock_pre_animal_population.heiferIs = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._calves_update()

    assert mock_calf_update.call_count == calf_num
    assert mock_get_calf_values.call_count == calf_num
    assert mock_heiferI_init.call_count == calf_num

    assert len(mock_herd_factory.pre_animal_population.calves) == 0
    assert len(mock_herd_factory.pre_animal_population.heiferIs) == calf_num


@pytest.mark.parametrize("calf_num", [
    0,
    1,
    8
])
def test_calves_update_wean_day_false(calf_num: int,
                                      mock_herd_factory: HerdFactory,
                                      mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Calf.__init__", return_value=None)
    mock_calves = [Calf(args=mock_animal_base_init_args_typed_dict) for _ in range(calf_num)]

    mock_calf_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.update", return_value=False)
    mock_get_calf_values = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.get_calf_values",
                                        return_value={})
    mock_heiferI_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.__init__",
                                     return_value=None)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.calves = mock_calves
    mock_pre_animal_population.heiferIs = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._calves_update()

    assert mock_calf_update.call_count == calf_num
    assert mock_get_calf_values.call_count == 0
    assert mock_heiferI_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.calves) == calf_num
    assert len(mock_herd_factory.pre_animal_population.heiferIs) == 0


@pytest.mark.parametrize("heiferI_num", [
    0,
    1,
    44
])
def test_heiferI_update_second_stage_true(heiferI_num: int,
                                          mock_herd_factory: HerdFactory,
                                          mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.HeiferI.__init__", return_value=None)
    mock_heiferIs = [HeiferI(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferI_num)]

    mock_heiferI_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.update",
                                       return_value=True)
    mock_get_heiferI_values = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.get_heiferI_values",
                                           return_value={})
    mock_heiferII_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.__init__",
                                      return_value=None)

    mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.AnimalBase.config",
                 return_value={
                     'heifer_repro_method': None,
                     'heifer_repro_programs': {
                         'heifer_TAI_protocol': None,
                         'heifer_synchED_protocol': None
                     }
                 })

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIs = mock_heiferIs
    mock_pre_animal_population.heiferIIs = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._heiferIs_update()

    assert mock_heiferI_update.call_count == heiferI_num
    assert mock_get_heiferI_values.call_count == heiferI_num
    assert mock_heiferII_init.call_count == heiferI_num

    assert len(mock_herd_factory.pre_animal_population.heiferIs) == 0
    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == heiferI_num


@pytest.mark.parametrize("heiferI_num", [
    0,
    1,
    44
])
def test_heiferI_update_second_stage_false(heiferI_num: int,
                                           mock_herd_factory: HerdFactory,
                                           mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.HeiferI.__init__", return_value=None)
    mock_heiferIs = [HeiferI(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferI_num)]

    mock_heiferI_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.update",
                                       return_value=False)
    mock_get_heiferI_values = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.get_heiferI_values",
                                           return_value={})
    mock_heiferII_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.__init__",
                                      return_value=None)

    mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.AnimalBase.config",
                 return_value={
                     'heifer_repro_method': None,
                     'heifer_repro_programs': {
                         'heifer_TAI_protocol': None,
                         'heifer_synchED_protocol': None
                     }
                 })

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIs = mock_heiferIs
    mock_pre_animal_population.heiferIIs = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._heiferIs_update()

    assert mock_heiferI_update.call_count == heiferI_num
    assert mock_get_heiferI_values.call_count == 0
    assert mock_heiferII_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.heiferIs) == heiferI_num
    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == 0


@pytest.mark.parametrize("heiferII_num", [
    0,
    1,
    38
])
def test_heiferII_update_cull_stage_true(heiferII_num: int,
                                         mock_herd_factory: HerdFactory,
                                         mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.HeiferII.__init__", return_value=None)
    mock_heiferIIs = [HeiferII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferII_num)]

    mock_heiferII_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.update",
                                        return_value=(True, False))
    mock_get_heiferII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.get_heiferII_values",
        return_value={})
    mock_heiferIII_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.__init__",
                                       return_value=None)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIIs = mock_heiferIIs
    mock_pre_animal_population.heiferIIIs = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._heiferIIs_update()

    assert mock_heiferII_update.call_count == heiferII_num
    assert mock_get_heiferII_values.call_count == 0
    assert mock_heiferIII_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == 0
    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == 0


@pytest.mark.parametrize("heiferII_num", [
    0,
    1,
    38
])
def test_heiferII_update_cull_stage_false_third_stage_true(heiferII_num: int,
                                                           mock_herd_factory: HerdFactory,
                                                           mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.HeiferII.__init__", return_value=None)
    mock_heiferIIs = [HeiferII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferII_num)]

    mock_heiferII_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.update",
                                        return_value=(False, True))
    mock_get_heiferII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.get_heiferII_values",
        return_value={})
    mock_heiferIII_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.__init__",
                                       return_value=None)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIIs = mock_heiferIIs
    mock_pre_animal_population.heiferIIIs = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._heiferIIs_update()

    assert mock_heiferII_update.call_count == heiferII_num
    assert mock_get_heiferII_values.call_count == heiferII_num
    assert mock_heiferIII_init.call_count == heiferII_num

    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == 0
    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == heiferII_num


@pytest.mark.parametrize("heiferII_num", [
    0,
    1,
    38
])
def test_heiferII_update_cull_stage_false_third_stage_false(heiferII_num: int,
                                                            mock_herd_factory: HerdFactory,
                                                            mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.HeiferII.__init__", return_value=None)
    mock_heiferIIs = [HeiferII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferII_num)]

    mock_heiferII_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.update",
                                        return_value=(False, False))
    mock_get_heiferII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.get_heiferII_values",
        return_value={})
    mock_heiferIII_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.__init__",
                                       return_value=None)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIIs = mock_heiferIIs
    mock_pre_animal_population.heiferIIIs = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._heiferIIs_update()

    assert mock_heiferII_update.call_count == heiferII_num
    assert mock_get_heiferII_values.call_count == 0
    assert mock_heiferIII_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == heiferII_num
    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == 0


@pytest.mark.parametrize("heiferIII_num", [
    0,
    1,
    5
])
def test_heiferIII_update_cow_stage_true_day_less_than_3000(heiferIII_num: int,
                                                            mock_herd_factory: HerdFactory,
                                                            mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.HeiferIII.__init__", return_value=None)
    mock_heiferIIIs = [HeiferIII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferIII_num)]

    mock_heiferIII_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.update",
                                         return_value=True)
    mock_get_heiferIII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.get_heiferIII_values",
        return_value={})
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.__init__",
                                 return_value=None)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIIIs = mock_heiferIIIs
    mock_pre_animal_population.cows = []
    mock_pre_animal_population.replacement = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._heiferIIIs_update(day=0)

    assert mock_heiferIII_update.call_count == heiferIII_num
    assert mock_get_heiferIII_values.call_count == heiferIII_num
    assert mock_cow_init.call_count == heiferIII_num

    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == 0
    assert len(mock_herd_factory.pre_animal_population.cows) == heiferIII_num
    assert len(mock_herd_factory.pre_animal_population.replacement) == 0


@pytest.mark.parametrize("heiferIII_num", [
    0,
    1,
    5
])
def test_heiferIII_update_cow_stage_true_day_greater_than_3000(heiferIII_num: int,
                                                               mock_herd_factory: HerdFactory,
                                                               mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.HeiferIII.__init__", return_value=None)
    mock_heiferIIIs = [HeiferIII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferIII_num)]

    mock_heiferIII_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.update",
                                         return_value=True)
    mock_get_heiferIII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.get_heiferIII_values",
        return_value={})
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.__init__",
                                 return_value=None)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIIIs = mock_heiferIIIs
    mock_pre_animal_population.cows = []
    mock_pre_animal_population.replacement = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._heiferIIIs_update(day=3001)

    assert mock_heiferIII_update.call_count == heiferIII_num
    assert mock_get_heiferIII_values.call_count == heiferIII_num
    assert mock_cow_init.call_count == heiferIII_num * 2

    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == 0
    assert len(mock_herd_factory.pre_animal_population.cows) == heiferIII_num
    assert len(mock_herd_factory.pre_animal_population.replacement) == heiferIII_num


@pytest.mark.parametrize("heiferIII_num", [
    0,
    1,
    5
])
def test_heiferIII_update_cow_stage_false(heiferIII_num: int,
                                          mock_herd_factory: HerdFactory,
                                          mocker: MockerFixture) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.HeiferIII.__init__", return_value=None)
    mock_heiferIIIs = [HeiferIII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferIII_num)]

    mock_heiferIII_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.update",
                                         return_value=False)
    mock_get_heiferIII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.get_heiferIII_values",
        return_value={})
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.__init__",
                                 return_value=None)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIIIs = mock_heiferIIIs
    mock_pre_animal_population.cows = []
    mock_pre_animal_population.replacement = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._heiferIIIs_update(day=0)

    assert mock_heiferIII_update.call_count == heiferIII_num
    assert mock_get_heiferIII_values.call_count == 0
    assert mock_cow_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == heiferIII_num
    assert len(mock_herd_factory.pre_animal_population.cows) == 0
    assert len(mock_herd_factory.pre_animal_population.replacement) == 0


def patch_cow_attributes_for_cows_update(mock_cow: Cow) -> Cow:
    mock_cow.calves = 0
    mock_cow.p_animal = 0
    mock_cow.p_gest_for_calf = 0
    mock_cow.p_growth = 0
    mock_cow.dP_reserves = 0
    mock_cow.calf_birth_weight = 0
    return mock_cow


# @pytest.mark.parametrize("cow_num", [
#     0,
#     1,
#     100
# ])
# def test_cow_update_culled_false_new_born_false(cow_num: int,
#                                                 mock_herd_factory: HerdFactory,
#                                                 mocker: MockerFixture) -> None:
#     mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
#     mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__", return_value=None)
#     mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
#     mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows))
#
#     mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update",
#                                    return_value=(None, None, None, False, True))
#
#     mocker.patch("RUFAS.routines.animal.life_cycle.calf.AnimalBase.__init__", return_value=None)
#     # mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.__init__",
#     #                               return_value=None)
#     # mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.culled", return_value=False)
#     # mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.sold", return_value=False)
#
#     mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
#     mock_pre_animal_population.cows = mock_cows
#     mock_pre_animal_population.calves = []
#
#     mock_herd_factory.pre_animal_population = mock_pre_animal_population
#     mock_herd_factory.breed = 'HO'
#     mock_herd_factory.CI = 0
#
#     mock_herd_factory._cows_update()
#
#     assert mock_cow_update.call_count == cow_num
#     # assert mock_calf_init.call_count == 0
#
#     assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
#     assert len(mock_herd_factory.pre_animal_population.calves) == 0
#
#
# animal_base_config = {
#     'breeding_start_day_h': 380,
#     'heifer_repro_method': 'TAI',
#     'cow_repro_method': 'TAI',
#     'semen_type': 'conventional',
#     'days_in_preg_when_dry': 218,
#     'heifer_repro_cull_time': 500,
#     'do_not_breed_time': 185,
#     'cull_milk_production': 30,
#     'cow_times_milked_per_day': 3,
#     'male_calf_rate_sexed_semen': 0.1,
#     'male_calf_rate_conventional_semen': 0.53,
#     'keep_female_calf_rate': 1,
#     'wean_day': 60,
#     'wean_length': 7,
#     'milk_type': 'whole',
#     'voluntary_waiting_period': 50,
#     'conception_rate_decrease': 0.026,
#     'avg_gestation_len': 278,
#     'std_gestation_len': 6,
#     'prefresh_day': 30,
#     'calving_interval': 400,
#     'heifer_repro_programs': {
#         'estrus_detection_rate': 0.6,
#         'estrus_service_rate': 1,
#         'ed_conception_rate': 0.6,
#         'heifer_TAI_protocol': 'md5CG2P',
#         'md5CG2P_conception_rate': 0.6,
#         'md5CGP_conception_rate': 0.48,
#         'heifer_synchED_protocol': '2P',
#         'estrus_detection_rate_h_synch': 0.7
#     },
#     'cow_repro_programs': {
#         'estrus_detection_rate': 0.6,
#         'estrus_service_rate': 1,
#         'ed_conception_rate': 0.6,
#         'cow_presynch_protocol': 'Double OvSynch',
#         'cow_TAI_protocol': 'OvSynch 56',
#         'ovsynch56_conception_rate': 0.6,
#         'ovsynch48_conception_rate': 0.6,
#         'cosynch72_conception_rate': 0.6,
#         'cosynch5d_conception_rate': 0.6,
#         'cow_resynch_protocol': 'TAIafterPD',
#         'tai_program_start_day': 72
#     },
#     'birth_weight_avg_ho': 43.9,
#     'birth_weight_std_ho': 1,
#     'birth_weight_avg_je': 35,
#     'birth_weight_std_je': 1,
#     'target_heifer_preg_day': 420,
#     'mature_body_weight_avg': 740.1,
#     'mature_body_weight_std': 73.5,
#     'preg_check_day_1': 32,
#     'preg_loss_rate_1': 0.02,
#     'preg_check_day_2': 60,
#     'preg_loss_rate_2': 0.096,
#     'preg_check_day_3': 200,
#     'preg_loss_rate_3': 0.017,
#     'avg_estrus_cycle_return': 23,
#     'std_estrus_cycle_return': 6,
#     'avg_estrus_cycle_heifer': 21,
#     'std_estrus_cycle_heifer': 2.5,
#     'avg_estrus_cycle_cow': 21,
#     'std_estrus_cycle_cow': 4,
#     'avg_estrus_cycle_after_pgf': 5,
#     'std_estrus_cycle_after_pgf': 2,
#     'wood_l': [[16.13, 23.61, 23.81], [14.07, 19.26, 19.21]],
#     'wood_m': [[0.235, 0.227, 0.244], [0.186, 0.173, 0.19]],
#     'wood_n': [[0.0019, 0.0032, 0.0036], [0.0021, 0.0028, 0.0032]],
#     'wood_l_std': [[0.28, 0.54, 0.51], [0.39, 0.49, 0.47]],
#     'wood_m_std': [[0.0046, 0.0064, 0.006], [0.0076, 0.0071, 0.0069]],
#     'wood_n_std': [[3.77e-05, 5.82e-05, 5.54e-05], [6.6e-05, 6.69e-05, 6.53e-05]],
#     'parity_death_prob': [0.039, 0.056, 0.085, 0.117],
#     'parity_cull_prob': [0.169, 0.233, 0.301, 0.408],
#     'injury_cull_prob': [0, 0.08, 0.18, 0.28, 0.38, 0.47, 0.56, 0.64, 0.71, 0.78, 0.85, 0.9, 0.95, 1],
#     'death_cull_prob': [0, 0.18, 0.32, 0.42, 0.48, 0.54, 0.6, 0.65, 0.7, 0.77, 0.83, 0.89, 0.95, 1],
#     'cull_day_count': [0, 5, 15, 45, 90, 135, 180, 225, 270, 330, 380, 430, 480, 530],
#     'udder_cull_prob': [0, 0.12, 0.24, 0.33, 0.41, 0.48, 0.55, 0.62, 0.68, 0.76, 0.82, 0.89, 0.95, 1],
#     'unknown_cull_prob': [0, 0.05, 0.11, 0.18, 0.27, 0.37, 0.45, 0.54, 0.62, 0.7, 0.77, 0.84, 0.92, 1],
#     'feet_leg_cull_prob': [0, 0.03, 0.08, 0.16, 0.25, 0.36, 0.48, 0.59, 0.69, 0.78, 0.85, 0.9, 0.95, 1],
#     'disease_cull_prob': [0, 0.04, 0.12, 0.24, 0.34, 0.42, 0.5, 0.57, 0.64, 0.72, 0.81, 0.89, 0.95, 1],
#     'mastitis_cull_prob': [0, 0.06, 0.12, 0.19, 0.3, 0.43, 0.56, 0.68, 0.78, 0.85, 0.9, 0.94, 0.97, 1],
#     'still_birth_rate': 0.065,
#     'nutrient_standard': 'NASEM'
# }
