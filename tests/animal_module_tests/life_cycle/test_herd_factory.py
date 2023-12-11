from unittest.mock import patch

import mock
import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.animal.animal_typed_dicts import AnimalBaseInitArgsTypedDict
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
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


def patch_cow_attributes_for_cows_update(mock_cow: Cow, calves: int) -> Cow:
    mock_cow.calves = calves
    mock_cow.p_animal = 0
    mock_cow.p_gest_for_calf = 0
    mock_cow.p_growth = 0
    mock_cow.dP_reserves = 0
    mock_cow.calf_birth_weight = 0
    return mock_cow


@pytest.mark.parametrize("cow_num", [
    0,
    1,
    100
])
def test_cow_update_culled_false_new_born_false(cow_num: int,
                                                mock_herd_factory: HerdFactory,
                                                mocker: MockerFixture,
                                                ) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__", return_value=None)
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update",
                                   return_value=(None, None, None, False, False))

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf",
                                  return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = 'HO'
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize("cow_num", [
    0,
    1,
    100
])
def test_cow_update_culled_true(cow_num: int,
                                mock_herd_factory: HerdFactory,
                                mocker: MockerFixture,
                                ) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__", return_value=None)
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update",
                                   return_value=(None, None, None, True, False))

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf",
                                  return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = 'HO'
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == 0
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize("cow_num", [
    0,
    1,
    100
])
def test_cow_update_culled_false_more_than_4_calves(cow_num: int,
                                                    mock_herd_factory: HerdFactory,
                                                    mocker: MockerFixture,
                                                    ) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__", return_value=None)
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [5] * cow_num))

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update",
                                   return_value=(None, None, None, False, False))

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf",
                                  return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = 'HO'
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == 0
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize("cow_num", [
    0,
    1,
    100
])
def test_cow_update_culled_false_new_born_true_calf_not_culled_or_sold(cow_num: int,
                                                                       mock_herd_factory: HerdFactory,
                                                                       mocker: MockerFixture,
                                                                       ) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__", return_value=None)
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update",
                                   return_value=(None, None, None, False, True))

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf",
                                  return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = 'HO'
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == cow_num

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
    assert len(mock_herd_factory.pre_animal_population.calves) == cow_num


@pytest.mark.parametrize("cow_num", [
    0,
    1,
    100
])
def test_cow_update_culled_false_new_born_true_calf_culled(cow_num: int,
                                                                       mock_herd_factory: HerdFactory,
                                                                       mocker: MockerFixture,
                                                                       ) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__", return_value=None)
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update",
                                   return_value=(None, None, None, False, True))

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = True
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf",
                                  return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = 'HO'
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == cow_num

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize("cow_num", [
    0,
    1,
    100
])
def test_cow_update_culled_false_new_born_true_calf_sold(cow_num: int,
                                                                       mock_herd_factory: HerdFactory,
                                                                       mocker: MockerFixture,
                                                                       ) -> None:
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch("tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__", return_value=None)
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update",
                                   return_value=(None, None, None, False, True))

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = True
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf",
                                  return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = 'HO'
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == cow_num

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
    assert len(mock_herd_factory.pre_animal_population.calves) == 0
