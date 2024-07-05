import datetime
from pathlib import Path
from typing import Dict, Callable

import mock
import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines import Feed
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
    """Returns an HerdFactory object"""
    return HerdFactory()


@pytest.fixture
def mock_input_manager(mocker: MockerFixture) -> InputManager:
    """Returns an uninitialized InputManager object"""
    return InputManager()


@pytest.fixture
def mock_output_manager(mocker: MockerFixture) -> OutputManager:
    return OutputManager()


@pytest.fixture
def input_manager_original_method_states(
    mock_input_manager: InputManager,
) -> Dict[str, Callable]:
    """Fixture to store original methods of InputManager"""
    return {
        "get_data": mock_input_manager.get_data,
        "add_dict_variable_to_pool": mock_input_manager.add_dict_variable_to_pool,
    }


@pytest.fixture
def output_manager_original_method_states(
    mock_output_manager: OutputManager,
) -> Dict[str, Callable]:
    """Fixture to store original methods of OutputManager"""
    return {"dict_to_file_json": mock_output_manager.dict_to_file_json}


def test_init(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for __init__()"""
    mock_input_manager.get_data = mock.MagicMock()
    mock_animal_population_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_population.AnimalPopulation.__init__",
        return_value=None,
    )
    HerdFactory()

    assert mock_input_manager.get_data.call_count == 4
    assert mock_animal_population_init.call_count == 2

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize("calf_num", [0, 1, 8])
def test_calves_update_wean_day_true(calf_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _calves_update() with wean_day=True"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Calf.__init__",
        return_value=None,
    )
    mock_calves = [Calf(args=mock_animal_base_init_args_typed_dict) for _ in range(calf_num)]

    mock_calf_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.update", return_value=True)
    mock_get_calf_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.Calf.get_calf_values",
        return_value={},
    )
    mock_heiferI_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.__init__",
        return_value=None,
    )

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


@pytest.mark.parametrize("calf_num", [0, 1, 8])
def test_calves_update_wean_day_false(calf_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _calves_update() with wean_day=False"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Calf.__init__",
        return_value=None,
    )
    mock_calves = [Calf(args=mock_animal_base_init_args_typed_dict) for _ in range(calf_num)]

    mock_calf_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf.update", return_value=False)
    mock_get_calf_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.Calf.get_calf_values",
        return_value={},
    )
    mock_heiferI_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.__init__",
        return_value=None,
    )

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


@pytest.mark.parametrize("heiferI_num", [0, 1, 44])
def test_heiferI_update_second_stage_true(
    heiferI_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferI_update() with second_stage=True"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferI.__init__",
        return_value=None,
    )
    mock_heiferIs = [HeiferI(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferI_num)]

    mock_heiferI_update = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.update",
        return_value=True,
    )
    mock_get_heiferI_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.get_heiferI_values",
        return_value={},
    )
    mock_heiferII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.__init__",
        return_value=None,
    )

    mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalBase.config",
        return_value={
            "heifer_repro_method": None,
            "heifer_repro_programs": {
                "heifer_TAI_protocol": None,
                "heifer_synchED_protocol": None,
            },
        },
    )

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


@pytest.mark.parametrize("heiferI_num", [0, 1, 44])
def test_heiferI_update_second_stage_false(
    heiferI_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferI_update() with second_stage=False"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferI.__init__",
        return_value=None,
    )
    mock_heiferIs = [HeiferI(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferI_num)]

    mock_heiferI_update = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.update",
        return_value=False,
    )
    mock_get_heiferI_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI.get_heiferI_values",
        return_value={},
    )
    mock_heiferII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.__init__",
        return_value=None,
    )

    mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalBase.config",
        return_value={
            "heifer_repro_method": None,
            "heifer_repro_programs": {
                "heifer_TAI_protocol": None,
                "heifer_synchED_protocol": None,
            },
        },
    )

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


@pytest.mark.parametrize("heiferII_num", [0, 1, 38])
def test_heiferII_update_cull_stage_true(
    heiferII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferII_update() with cull_stage=True"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferII.__init__",
        return_value=None,
    )
    mock_heiferIIs = [HeiferII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferII_num)]

    mock_heiferII_update = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.update",
        return_value=(True, False),
    )
    mock_get_heiferII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.get_heiferII_values",
        return_value={},
    )
    mock_heiferIII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.__init__",
        return_value=None,
    )

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


@pytest.mark.parametrize("heiferII_num", [0, 1, 38])
def test_heiferII_update_cull_stage_false_third_stage_true(
    heiferII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferII_update() with cull_stage=False and third_stage=True"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferII.__init__",
        return_value=None,
    )
    mock_heiferIIs = [HeiferII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferII_num)]

    mock_heiferII_update = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.update",
        return_value=(False, True),
    )
    mock_get_heiferII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.get_heiferII_values",
        return_value={},
    )
    mock_heiferIII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.__init__",
        return_value=None,
    )

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


@pytest.mark.parametrize("heiferII_num", [0, 1, 38])
def test_heiferII_update_cull_stage_false_third_stage_false(
    heiferII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferII_update() with cull_stage=False and third_stage=False"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferII.__init__",
        return_value=None,
    )
    mock_heiferIIs = [HeiferII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferII_num)]

    mock_heiferII_update = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.update",
        return_value=(False, False),
    )
    mock_get_heiferII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII.get_heiferII_values",
        return_value={},
    )
    mock_heiferIII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.__init__",
        return_value=None,
    )

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


@pytest.mark.parametrize("heiferIII_num", [0, 1, 5])
def test_heiferIII_update_cow_stage_true_day_less_than_3000(
    heiferIII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferIII_update() with cow_stage=True and day<3000"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferIII.__init__",
        return_value=None,
    )
    mock_heiferIIIs = [HeiferIII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferIII_num)]

    mock_heiferIII_update = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.update",
        return_value=True,
    )
    mock_get_heiferIII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.get_heiferIII_values",
        return_value={},
    )
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.__init__", return_value=None)

    mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalBase.config",
        return_value={
            "cow_repro_method": None,
            "cows": {
                "presynch_protocol": None,
                "repro_sub_protocol": None,
                "resynch_protocol": None,
            },
        },
    )

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


@pytest.mark.parametrize("heiferIII_num", [0, 1, 5])
def test_heiferIII_update_cow_stage_true_day_greater_than_3000(
    heiferIII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferIII_update() with cow_stage=True and day>3000"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferIII.__init__",
        return_value=None,
    )
    mock_heiferIIIs = [HeiferIII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferIII_num)]

    mock_heiferIII_update = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.update",
        return_value=True,
    )
    mock_get_heiferIII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.get_heiferIII_values",
        return_value={},
    )
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.__init__", return_value=None)

    mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalBase.config",
        return_value={
            "cow_repro_method": None,
            "cows": {
                "presynch_protocol": None,
                "repro_sub_protocol": None,
                "resynch_protocol": None,
            },
        },
    )

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


@pytest.mark.parametrize("heiferIII_num", [0, 1, 5])
def test_heiferIII_update_cow_stage_false(
    heiferIII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferIII_update() with cow_stage=False"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferIII.__init__",
        return_value=None,
    )
    mock_heiferIIIs = [HeiferIII(args=mock_animal_base_init_args_typed_dict) for _ in range(heiferIII_num)]

    mock_heiferIII_update = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.update",
        return_value=False,
    )
    mock_get_heiferIII_values = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII.get_heiferIII_values",
        return_value={},
    )
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.__init__", return_value=None)

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
    """Function to patch attributes for mock_cow objects"""
    mock_cow.calves = calves
    mock_cow.p_animal = 0
    mock_cow.p_gest_for_calf = 0
    mock_cow.p_growth = 0
    mock_cow.dP_reserves = 0
    mock_cow.calf_birth_weight = 0
    return mock_cow


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_false_new_born_false(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=False and new_born=False"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__",
        return_value=None,
    )
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))
    for cow in mock_cows:
        cow.culled = False

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update", return_value=False)

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = "HO"
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_true(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=True"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__",
        return_value=None,
    )
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))
    for cow in mock_cows:
        cow.culled = True

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update", return_value=False)

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = "HO"
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == 0
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_false_more_than_4_calves(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=False and cow.calves>4"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__",
        return_value=None,
    )
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [5] * cow_num))
    for cow in mock_cows:
        cow.culled = False

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update", return_value=False)

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = "HO"
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == 0
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_false_new_born_true_calf_not_culled_or_sold(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=False and new_born=True, the newborn calf is not culled or sold"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__",
        return_value=None,
    )
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))
    for cow in mock_cows:
        cow.culled = False

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update", return_value=True)

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = "HO"
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == cow_num

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
    assert len(mock_herd_factory.pre_animal_population.calves) == cow_num


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_false_new_born_true_calf_culled(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=False and new_born=True, the newborn calf is culled"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__",
        return_value=None,
    )
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))
    for cow in mock_cows:
        cow.culled = False

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update", return_value=True)

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = True
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = "HO"
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == cow_num

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_false_new_born_true_calf_sold(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=False and new_born=True, the newborn calf is sold"""
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__",
        return_value=None,
    )
    mock_cows = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(cow_num)]
    mock_cows = list(map(patch_cow_attributes_for_cows_update, mock_cows, [0] * cow_num))
    for cow in mock_cows:
        cow.culled = False

    mock_cow_update = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow.update", return_value=True)

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = True
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_cows
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.breed = "HO"
    mock_herd_factory.CI = 0

    mock_herd_factory._cows_update()

    assert mock_cow_update.call_count == cow_num
    assert mock_calf_init.call_count == cow_num

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num
    assert len(mock_herd_factory.pre_animal_population.calves) == 0


@pytest.mark.parametrize(
    "initial_animal_num, simulation_days",
    [
        (0, 0),
        (1, 0),
        (10000, 0),
        (0, 1),
        (1, 1),
        (10000, 1),
        (0, 5000),
        (1, 5000),
        (10000, 5000),
    ],
)
def test_generate_animals(
    initial_animal_num: int,
    simulation_days: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _generate_animals()"""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=None)
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_population.AnimalPopulation.__init__",
        return_value=None,
    )
    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.calves = []

    mock_herd_factory.breed = "HO"
    mock_herd_factory.initial_animal_num = initial_animal_num
    mock_herd_factory.simulation_days = simulation_days
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._calves_update = mock.MagicMock()
    mock_herd_factory._heiferIs_update = mock.MagicMock()
    mock_herd_factory._heiferIIs_update = mock.MagicMock()
    mock_herd_factory._heiferIIIs_update = mock.MagicMock()
    mock_herd_factory._cows_update = mock.MagicMock()

    mock_animal_base_init_args_typed_dict_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalBaseInitArgsTypedDict",
        return_value=None,
    )
    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    result = mock_herd_factory._generate_animals()

    assert mock_animal_base_init_args_typed_dict_init.call_count == initial_animal_num
    assert mock_calf_init.call_count == initial_animal_num

    assert mock_herd_factory._calves_update.call_count == simulation_days
    assert mock_herd_factory._heiferIs_update.call_count == simulation_days
    assert mock_herd_factory._heiferIIs_update.call_count == simulation_days
    assert mock_herd_factory._heiferIIIs_update.call_count == simulation_days
    assert mock_herd_factory._cows_update.call_count == simulation_days

    assert len(result.calves) == initial_animal_num


@pytest.mark.parametrize(
    "initial_animal_num, simulation_days",
    [
        (0, 0),
        (1, 0),
        (10000, 0),
        (0, 1),
        (1, 1),
        (10000, 1),
        (0, 5000),
        (1, 5000),
        (10000, 5000),
    ],
)
def test_generate_animals_calf_culled(
    initial_animal_num: int,
    simulation_days: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _generate_animals() with calf culled"""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=None)
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_population.AnimalPopulation.__init__",
        return_value=None,
    )
    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.calves = []

    mock_herd_factory.breed = "HO"
    mock_herd_factory.initial_animal_num = initial_animal_num
    mock_herd_factory.simulation_days = simulation_days
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._calves_update = mock.MagicMock()
    mock_herd_factory._heiferIs_update = mock.MagicMock()
    mock_herd_factory._heiferIIs_update = mock.MagicMock()
    mock_herd_factory._heiferIIIs_update = mock.MagicMock()
    mock_herd_factory._cows_update = mock.MagicMock()

    mock_animal_base_init_args_typed_dict_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalBaseInitArgsTypedDict",
        return_value=None,
    )
    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = True
    mock_calf.sold = False
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    result = mock_herd_factory._generate_animals()

    assert mock_animal_base_init_args_typed_dict_init.call_count == initial_animal_num
    assert mock_calf_init.call_count == initial_animal_num

    assert mock_herd_factory._calves_update.call_count == simulation_days
    assert mock_herd_factory._heiferIs_update.call_count == simulation_days
    assert mock_herd_factory._heiferIIs_update.call_count == simulation_days
    assert mock_herd_factory._heiferIIIs_update.call_count == simulation_days
    assert mock_herd_factory._cows_update.call_count == simulation_days

    assert len(result.calves) == 0


@pytest.mark.parametrize(
    "initial_animal_num, simulation_days",
    [
        (0, 0),
        (1, 0),
        (10000, 0),
        (0, 1),
        (1, 1),
        (10000, 1),
        (0, 5000),
        (1, 5000),
        (10000, 5000),
    ],
)
def test_generate_animals_calf_sold(
    initial_animal_num: int,
    simulation_days: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _generate_animals() with calf sold"""
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=None)
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_population.AnimalPopulation.__init__",
        return_value=None,
    )
    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.calves = []

    mock_herd_factory.breed = "HO"
    mock_herd_factory.initial_animal_num = initial_animal_num
    mock_herd_factory.simulation_days = simulation_days
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._calves_update = mock.MagicMock()
    mock_herd_factory._heiferIs_update = mock.MagicMock()
    mock_herd_factory._heiferIIs_update = mock.MagicMock()
    mock_herd_factory._heiferIIIs_update = mock.MagicMock()
    mock_herd_factory._cows_update = mock.MagicMock()

    mock_animal_base_init_args_typed_dict_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalBaseInitArgsTypedDict",
        return_value=None,
    )
    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf.culled = False
    mock_calf.sold = True
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)

    result = mock_herd_factory._generate_animals()

    assert mock_animal_base_init_args_typed_dict_init.call_count == initial_animal_num
    assert mock_calf_init.call_count == initial_animal_num

    assert mock_herd_factory._calves_update.call_count == simulation_days
    assert mock_herd_factory._heiferIs_update.call_count == simulation_days
    assert mock_herd_factory._heiferIIs_update.call_count == simulation_days
    assert mock_herd_factory._heiferIIIs_update.call_count == simulation_days
    assert mock_herd_factory._cows_update.call_count == simulation_days

    assert len(result.calves) == 0


def test_init_calf_from_data(mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _init_animal_from_data() with calf"""
    dummy_animal_id = 31415
    dummy_animal_data = {"dummy": "data"}

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)
    mock_heiferI = mock.MagicMock(auto_spec=HeiferI)
    mock_heiferI_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI",
        return_value=mock_heiferI,
    )
    mock_heiferII = mock.MagicMock(auto_spec=HeiferII)
    mock_heiferII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII",
        return_value=mock_heiferII,
    )
    mock_heiferIII = mock.MagicMock(auto_spec=HeiferIII)
    mock_heiferIII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII",
        return_value=mock_heiferIII,
    )
    mock_cow = mock.MagicMock(auto_spec=Cow)
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow", return_value=mock_cow)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.next_id.return_value = dummy_animal_id

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    result = mock_herd_factory._init_animal_from_data(animal_type="calf", animal_data=dummy_animal_data)

    dummy_animal_data.update(id=dummy_animal_id)
    dummy_animal_data.update(p_init=0)

    mock_calf_init.assert_called_once_with(dummy_animal_data)
    mock_heiferI_init.assert_not_called()
    mock_heiferII_init.assert_not_called()
    mock_heiferIII_init.assert_not_called()
    mock_cow_init.assert_not_called()

    assert result == mock_calf


def test_init_heiferI_from_data(mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _init_animal_from_data() with heiferI"""
    dummy_animal_id = 31415
    dummy_animal_data = {"dummy": "data"}

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)
    mock_heiferI = mock.MagicMock(auto_spec=HeiferI)
    mock_heiferI_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI",
        return_value=mock_heiferI,
    )
    mock_heiferII = mock.MagicMock(auto_spec=HeiferII)
    mock_heiferII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII",
        return_value=mock_heiferII,
    )
    mock_heiferIII = mock.MagicMock(auto_spec=HeiferIII)
    mock_heiferIII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII",
        return_value=mock_heiferIII,
    )
    mock_cow = mock.MagicMock(auto_spec=Cow)
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow", return_value=mock_cow)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.next_id.return_value = dummy_animal_id

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    result = mock_herd_factory._init_animal_from_data(animal_type="heiferI", animal_data=dummy_animal_data)

    dummy_animal_data.update(id=dummy_animal_id)

    mock_calf_init.assert_not_called()
    mock_heiferI_init.assert_called_once_with(dummy_animal_data)
    mock_heiferII_init.assert_not_called()
    mock_heiferIII_init.assert_not_called()
    mock_cow_init.assert_not_called()

    assert result == mock_heiferI


def test_init_heiferII_from_data(mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _init_animal_from_data() with heiferII"""
    dummy_animal_id = 31415
    dummy_animal_data = {"dummy": "data"}

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)
    mock_heiferI = mock.MagicMock(auto_spec=HeiferI)
    mock_heiferI_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI",
        return_value=mock_heiferI,
    )
    mock_heiferII = mock.MagicMock(auto_spec=HeiferII)
    mock_heiferII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII",
        return_value=mock_heiferII,
    )
    mock_heiferIII = mock.MagicMock(auto_spec=HeiferIII)
    mock_heiferIII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII",
        return_value=mock_heiferIII,
    )
    mock_cow = mock.MagicMock(auto_spec=Cow)
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow", return_value=mock_cow)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.next_id.return_value = dummy_animal_id

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    result = mock_herd_factory._init_animal_from_data(animal_type="heiferII", animal_data=dummy_animal_data)

    dummy_animal_data.update(id=dummy_animal_id)

    mock_calf_init.assert_not_called()
    mock_heiferI_init.assert_not_called()
    mock_heiferII_init.assert_called_once_with(dummy_animal_data)
    mock_heiferIII_init.assert_not_called()
    mock_cow_init.assert_not_called()

    assert result == mock_heiferII


def test_init_heiferIII_from_data(mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _init_animal_from_data() with heiferIII"""
    dummy_animal_id = 31415
    dummy_animal_data = {"dummy": "data"}

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)
    mock_heiferI = mock.MagicMock(auto_spec=HeiferI)
    mock_heiferI_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI",
        return_value=mock_heiferI,
    )
    mock_heiferII = mock.MagicMock(auto_spec=HeiferII)
    mock_heiferII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII",
        return_value=mock_heiferII,
    )
    mock_heiferIII = mock.MagicMock(auto_spec=HeiferIII)
    mock_heiferIII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII",
        return_value=mock_heiferIII,
    )
    mock_cow = mock.MagicMock(auto_spec=Cow)
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow", return_value=mock_cow)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.next_id.return_value = dummy_animal_id

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    result = mock_herd_factory._init_animal_from_data(animal_type="heiferIII", animal_data=dummy_animal_data)

    dummy_animal_data.update(id=dummy_animal_id)

    mock_calf_init.assert_not_called()
    mock_heiferI_init.assert_not_called()
    mock_heiferII_init.assert_not_called()
    mock_heiferIII_init.assert_called_once_with(dummy_animal_data)
    mock_cow_init.assert_not_called()

    assert result == mock_heiferIII


def test_init_cow_from_data(mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _init_animal_from_data() with cow"""
    dummy_animal_id = 31415
    dummy_animal_data = {"dummy": "data"}

    mock_calf = mock.MagicMock(auto_spec=Calf)
    mock_calf_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Calf", return_value=mock_calf)
    mock_heiferI = mock.MagicMock(auto_spec=HeiferI)
    mock_heiferI_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferI",
        return_value=mock_heiferI,
    )
    mock_heiferII = mock.MagicMock(auto_spec=HeiferII)
    mock_heiferII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferII",
        return_value=mock_heiferII,
    )
    mock_heiferIII = mock.MagicMock(auto_spec=HeiferIII)
    mock_heiferIII_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.HeiferIII",
        return_value=mock_heiferIII,
    )
    mock_cow = mock.MagicMock(auto_spec=Cow)
    mock_cow_init = mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Cow", return_value=mock_cow)

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.next_id.return_value = dummy_animal_id

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    result = mock_herd_factory._init_animal_from_data(animal_type="cow", animal_data=dummy_animal_data)

    dummy_animal_data.update(id=dummy_animal_id)

    mock_calf_init.assert_not_called()
    mock_heiferI_init.assert_not_called()
    mock_heiferII_init.assert_not_called()
    mock_heiferIII_init.assert_not_called()
    mock_cow_init.assert_called_once_with(dummy_animal_data)

    assert result == mock_cow


@pytest.mark.parametrize(
    "num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement",
    [(1, 1, 1, 1, 1, 1), (0, 0, 0, 0, 0, 0), (8, 44, 38, 5, 100, 500)],
)
def test_initialize_herd_from_data(
    num_calf: int,
    num_heiferI: int,
    num_heiferII: int,
    num_heiferIII: int,
    num_cow: int,
    num_replacement: int,
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for _init_herd_from_data()"""
    mock_input_manager.get_data = mock.MagicMock(
        return_value={
            "calves": [{"dummy_calf"}] * num_calf,
            "heiferIs": [{"dummy_heiferI"}] * num_heiferI,
            "heiferIIs": [{"dummy_heiferII"}] * num_heiferII,
            "heiferIIIs": [{"dummy_heiferIII"}] * num_heiferIII,
            "cows": [{"dummy_cow"}] * num_cow,
            "replacement": [{"dummy_replacement"}] * num_replacement,
        }
    )

    mock_herd_factory._init_animal_from_data = mock.MagicMock(return_value=None)
    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.current_animal_id = 0
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_animal_population_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalPopulation",
        return_value=None,
    )

    mock_herd_factory._initialize_herd_from_data()

    expected_init_animal_from_data_call_count = sum(
        [num_calf, num_heiferI, num_heiferII, num_heiferIII, num_cow, num_replacement]
    )

    expected_init_animal_from_data_call_args_list = (
        [(("calf", {"dummy_calf"}),)] * num_calf
        + [(("heiferI", {"dummy_heiferI"}),)] * num_heiferI
        + [(("heiferII", {"dummy_heiferII"}),)] * num_heiferII
        + [(("heiferIII", {"dummy_heiferIII"}),)] * num_heiferIII
        + [(("cow", {"dummy_cow"}),)] * num_cow
        + [(("replacement", {"dummy_replacement"}),)] * num_replacement
    )

    mock_input_manager.get_data.assert_called_once_with("animal_population")
    assert mock_herd_factory._init_animal_from_data.call_count == expected_init_animal_from_data_call_count
    assert mock_herd_factory._init_animal_from_data.call_args_list == expected_init_animal_from_data_call_args_list
    mock_animal_population_init.assert_called_once()

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


def test_random_sample_with_replacement(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement()"""
    mock_herd_factory._random_sample_with_replacement_by_type = mock.MagicMock(return_value=None)

    mock_post_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population.current_animal_id = 0
    mock_herd_factory.post_animal_population = mock_post_animal_population

    mock_input_manager.get_data = mock.MagicMock()

    mock_animal_population_init = mocker.patch(
        "RUFAS.routines.animal.life_cycle.herd_factory.AnimalPopulation",
        return_value=None,
    )

    mock_herd_factory._random_sample_with_replacement()

    assert mock_herd_factory._random_sample_with_replacement_by_type.call_count == 6
    assert mock_animal_population_init.call_count == 1

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "pre_num, post_num",
    [
        (0, 0),
        (1, 0),
        (8, 0),
        (1, 1),
        (1, 8),
        (8, 1),
        (8, 8),
    ],
)
def test_random_sample_with_replacement_by_type_calf(
    pre_num: int,
    post_num: int,
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement_by_type() with calf"""
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Calf.__init__",
        return_value=None,
    )
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mock_pre_animals = [Calf(args=mock_animal_base_init_args_typed_dict) for _ in range(pre_num)]

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.calves = mock_pre_animals
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_post_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population_next_id_list = list(range(post_num))
    mock_post_animal_population.next_id = mocker.patch.object(
        mock_post_animal_population,
        "next_id",
        side_effct=mock_post_animal_population_next_id_list,
    )
    mock_herd_factory.post_animal_population = mock_post_animal_population

    mock_random_choices = mock.MagicMock(return_value=[0] * post_num)
    mocker.patch("random.choices", mock_random_choices)

    mock_deepcopy = mock.MagicMock()
    mocker.patch("copy.deepcopy", mock_deepcopy)

    mock_input_manager.get_data = mock.MagicMock(return_value=post_num)

    result = mock_herd_factory._random_sample_with_replacement_by_type("calf")

    mock_input_manager.get_data.assert_called_once_with("animal.herd_information.calf_num")
    mock_random_choices.assert_called_once_with(list(range(pre_num)), k=post_num)
    assert mock_deepcopy.call_count == post_num
    assert len(result) == post_num

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "pre_num, post_num",
    [
        (0, 0),
        (1, 0),
        (44, 0),
        (1, 1),
        (1, 44),
        (44, 1),
        (44, 44),
    ],
)
def test_random_sample_with_replacement_by_type_heiferI(
    pre_num: int,
    post_num: int,
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement_by_type() with heiferI"""
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferI.__init__",
        return_value=None,
    )
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mock_pre_animals = [HeiferI(args=mock_animal_base_init_args_typed_dict) for _ in range(pre_num)]

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIs = mock_pre_animals
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_post_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population_next_id_list = list(range(post_num))
    mock_post_animal_population.next_id = mocker.patch.object(
        mock_post_animal_population,
        "next_id",
        side_effct=mock_post_animal_population_next_id_list,
    )
    mock_herd_factory.post_animal_population = mock_post_animal_population

    mock_random_choices = mock.MagicMock(return_value=[0] * post_num)
    mocker.patch("random.choices", mock_random_choices)

    mock_deepcopy = mock.MagicMock()
    mocker.patch("copy.deepcopy", mock_deepcopy)

    mock_input_manager.get_data = mock.MagicMock(return_value=post_num)

    result = mock_herd_factory._random_sample_with_replacement_by_type("heiferI")

    mock_input_manager.get_data.assert_called_once_with("animal.herd_information.heiferI_num")
    mock_random_choices.assert_called_once_with(list(range(pre_num)), k=post_num)
    assert mock_deepcopy.call_count == post_num
    assert len(result) == post_num

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "pre_num, post_num",
    [
        (0, 0),
        (1, 0),
        (38, 0),
        (1, 1),
        (1, 38),
        (38, 1),
        (38, 38),
    ],
)
def test_random_sample_with_replacement_by_type_heiferII(
    pre_num: int,
    post_num: int,
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement_by_type() with heiferII"""
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferII.__init__",
        return_value=None,
    )
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mock_pre_animals = [HeiferII(args=mock_animal_base_init_args_typed_dict) for _ in range(pre_num)]

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIIs = mock_pre_animals
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_post_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population_next_id_list = list(range(post_num))
    mock_post_animal_population.next_id = mocker.patch.object(
        mock_post_animal_population,
        "next_id",
        side_effct=mock_post_animal_population_next_id_list,
    )
    mock_herd_factory.post_animal_population = mock_post_animal_population

    mock_random_choices = mock.MagicMock(return_value=[0] * post_num)
    mocker.patch("random.choices", mock_random_choices)

    mock_deepcopy = mock.MagicMock()
    mocker.patch("copy.deepcopy", mock_deepcopy)

    mock_input_manager.get_data = mock.MagicMock(return_value=post_num)

    result = mock_herd_factory._random_sample_with_replacement_by_type("heiferII")

    mock_input_manager.get_data.assert_called_once_with("animal.herd_information.heiferII_num")
    mock_random_choices.assert_called_once_with(list(range(pre_num)), k=post_num)
    assert mock_deepcopy.call_count == post_num
    assert len(result) == post_num

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "pre_num, post_num",
    [
        (0, 0),
        (1, 0),
        (5, 0),
        (1, 1),
        (1, 5),
        (5, 1),
        (5, 5),
    ],
)
def test_random_sample_with_replacement_by_type_heiferIII(
    pre_num: int,
    post_num: int,
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement_by_type() with heiferIII"""
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.HeiferIII.__init__",
        return_value=None,
    )
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mock_pre_animals = [HeiferIII(args=mock_animal_base_init_args_typed_dict) for _ in range(pre_num)]

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.heiferIIIs = mock_pre_animals
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_post_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population_next_id_list = list(range(post_num))
    mock_post_animal_population.next_id = mocker.patch.object(
        mock_post_animal_population,
        "next_id",
        side_effct=mock_post_animal_population_next_id_list,
    )
    mock_herd_factory.post_animal_population = mock_post_animal_population

    mock_random_choices = mock.MagicMock(return_value=[0] * post_num)
    mocker.patch("random.choices", mock_random_choices)

    mock_deepcopy = mock.MagicMock()
    mocker.patch("copy.deepcopy", mock_deepcopy)

    mock_input_manager.get_data = mock.MagicMock(return_value=post_num)

    result = mock_herd_factory._random_sample_with_replacement_by_type("heiferIII")

    mock_input_manager.get_data.assert_called_once_with("animal.herd_information.heiferIII_num_springers")
    mock_random_choices.assert_called_once_with(list(range(pre_num)), k=post_num)
    assert mock_deepcopy.call_count == post_num
    assert len(result) == post_num

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "pre_num, post_num",
    [
        (0, 0),
        (1, 0),
        (100, 0),
        (1, 1),
        (1, 100),
        (100, 1),
        (100, 100),
    ],
)
def test_random_sample_with_replacement_by_type_cow(
    pre_num: int,
    post_num: int,
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement_by_type() with cow"""
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__",
        return_value=None,
    )
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mock_pre_animals = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(pre_num)]

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.cows = mock_pre_animals
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_post_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population_next_id_list = list(range(post_num))
    mock_post_animal_population.next_id = mocker.patch.object(
        mock_post_animal_population,
        "next_id",
        side_effct=mock_post_animal_population_next_id_list,
    )
    mock_herd_factory.post_animal_population = mock_post_animal_population

    mock_random_choices = mock.MagicMock(return_value=[0] * post_num)
    mocker.patch("random.choices", mock_random_choices)

    mock_deepcopy = mock.MagicMock()
    mocker.patch("copy.deepcopy", mock_deepcopy)

    mock_input_manager.get_data = mock.MagicMock(return_value=post_num)

    result = mock_herd_factory._random_sample_with_replacement_by_type("cow")

    mock_input_manager.get_data.assert_called_once_with("animal.herd_information.cow_num")
    mock_random_choices.assert_called_once_with(list(range(pre_num)), k=post_num)
    assert mock_deepcopy.call_count == post_num
    assert len(result) == post_num

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "pre_num, post_num",
    [
        (0, 0),
        (1, 0),
        (100, 0),
        (1, 1),
        (1, 100),
        (100, 1),
        (100, 100),
    ],
)
def test_random_sample_with_replacement_by_type_replacement(
    pre_num: int,
    post_num: int,
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement_by_type() with replacement cows"""
    mocker.patch(
        "tests.animal_module_tests.life_cycle.test_herd_factory.Cow.__init__",
        return_value=None,
    )
    mock_animal_base_init_args_typed_dict = mock.MagicMock(auto_spec=AnimalBaseInitArgsTypedDict)
    mock_pre_animals = [Cow(args=mock_animal_base_init_args_typed_dict) for _ in range(pre_num)]

    mock_pre_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.replacement = mock_pre_animals
    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_post_animal_population = mock.MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population_next_id_list = list(range(post_num))
    mock_post_animal_population.next_id = mocker.patch.object(
        mock_post_animal_population,
        "next_id",
        side_effct=mock_post_animal_population_next_id_list,
    )
    mock_herd_factory.post_animal_population = mock_post_animal_population

    mock_random_choices = mock.MagicMock(return_value=[0] * post_num)
    mocker.patch("random.choices", mock_random_choices)

    mock_deepcopy = mock.MagicMock()
    mocker.patch("copy.deepcopy", mock_deepcopy)

    mock_input_manager.get_data = mock.MagicMock(return_value=post_num)

    result = mock_herd_factory._random_sample_with_replacement_by_type("replacement")

    mock_input_manager.get_data.assert_called_once_with("animal.herd_information.replace_num")
    mock_random_choices.assert_called_once_with(list(range(pre_num)), k=post_num)
    assert mock_deepcopy.call_count == post_num
    assert len(result) == post_num

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


def test_initialize_herd_init_herd_true_save_animals_true(
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    mock_output_manager: OutputManager,
    input_manager_original_method_states: Dict[str, Callable],
    output_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for initialize_herd() with init_herd=True and save_animals=True"""
    mock_input_manager.get_data = mock.MagicMock()
    mock_input_manager.add_dict_variable_to_pool = mock.MagicMock()

    mock_output_manager.dict_to_file_json = mock.MagicMock()

    mock_animal_manager_get_animal_config = mocker.patch(
        "RUFAS.routines.animal.animal_manager.AnimalManager.get_animal_config"
    )

    mock_feed = mock.MagicMock(auto_spec=Feed)
    mock_feed.nutrient_rqmts = "NASEM"
    mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Feed", return_value=mock_feed)

    mock_animal_base_set_config = mocker.patch("RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_config")
    mock_animal_base_set_lactation_curve_parameters = mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_lactation_curve_parameters"
    )
    mock_animal_base_set_nutrient_list = mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_nutrient_list"
    )

    mock_herd_factory.init_herd = True
    mock_herd_factory.save_animals = True
    mock_herd_factory.save_animals_path = Path("dummy_path")

    mock_herd_factory._generate_animals = mock.MagicMock()
    mock_herd_factory._initialize_herd_from_data = mock.MagicMock()
    mock_herd_factory._random_sample_with_replacement = mock.MagicMock()

    dummy_time_str = "2023-12-12 13:34:42"
    with freeze_time(dummy_time_str):
        mock_herd_factory.initialize_herd()
        dummy_time_str_strf = datetime.datetime.now().strftime("%d-%b-%Y_%a_%H-%M-%S")

    expected_save_path = Path.joinpath(Path("dummy_path"), f"animal_population-{dummy_time_str_strf}.json")

    assert mock_input_manager.get_data.call_count == 2
    mock_animal_manager_get_animal_config.assert_called_once()
    mock_animal_base_set_config.assert_called_once()
    mock_animal_base_set_lactation_curve_parameters.assert_called_once()
    mock_animal_base_set_nutrient_list.assert_called_once_with("NASEM")

    mock_herd_factory._generate_animals.assert_called_once()
    mock_herd_factory._initialize_herd_from_data.assert_not_called()
    mock_herd_factory._random_sample_with_replacement.assert_called_once()

    mock_output_manager.dict_to_file_json.assert_called_once_with(
        mock_herd_factory.pre_animal_population.__repr__(),
        expected_save_path,
        minify_output_file=True,
    )
    mock_input_manager.add_dict_variable_to_pool.assert_called_once_with(
        variable_name="runtime_animal_population",
        data=mock_herd_factory.post_animal_population.__repr__(),
        properties_blob_key="animal_population_properties",
        eager_termination=False,
    )

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]
    mock_input_manager.add_dict_variable_to_pool = input_manager_original_method_states["add_dict_variable_to_pool"]
    mock_output_manager.dict_to_file_json = output_manager_original_method_states["dict_to_file_json"]


def test_initialize_herd_init_herd_true_save_animals_false(
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    mock_output_manager: OutputManager,
    input_manager_original_method_states: Dict[str, Callable],
    output_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for initialize_herd() with init_herd=True and save_animals=False"""
    mock_input_manager.get_data = mock.MagicMock()
    mock_input_manager.add_dict_variable_to_pool = mock.MagicMock()

    mock_output_manager.dict_to_file_json = mock.MagicMock()

    mock_animal_manager_get_animal_config = mocker.patch(
        "RUFAS.routines.animal.animal_manager.AnimalManager.get_animal_config"
    )

    mock_feed = mock.MagicMock(auto_spec=Feed)
    mock_feed.nutrient_rqmts = "NASEM"
    mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Feed", return_value=mock_feed)

    mock_animal_base_set_config = mocker.patch("RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_config")
    mock_animal_base_set_nutrient_list = mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_nutrient_list"
    )
    mock_animal_base_set_lactation_curve_parameters = mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_lactation_curve_parameters"
    )

    mock_herd_factory.init_herd = True
    mock_herd_factory.save_animals = False
    mock_herd_factory.save_animals_path = Path("dummy_path")

    mock_herd_factory._generate_animals = mock.MagicMock()
    mock_herd_factory._initialize_herd_from_data = mock.MagicMock()
    mock_herd_factory._random_sample_with_replacement = mock.MagicMock()

    mock_herd_factory.initialize_herd()

    assert mock_input_manager.get_data.call_count == 2
    mock_animal_manager_get_animal_config.assert_called_once()
    mock_animal_base_set_config.assert_called_once()
    mock_animal_base_set_nutrient_list.assert_called_once_with("NASEM")
    mock_animal_base_set_lactation_curve_parameters.assert_called_once()

    mock_herd_factory._generate_animals.assert_called_once()
    mock_herd_factory._initialize_herd_from_data.assert_not_called()
    mock_herd_factory._random_sample_with_replacement.assert_called_once()

    mock_output_manager.dict_to_file_json.assert_not_called()
    mock_input_manager.add_dict_variable_to_pool.assert_called_once_with(
        variable_name="runtime_animal_population",
        data=mock_herd_factory.post_animal_population.__repr__(),
        properties_blob_key="animal_population_properties",
        eager_termination=False,
    )

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]
    mock_input_manager.add_dict_variable_to_pool = input_manager_original_method_states["add_dict_variable_to_pool"]
    mock_output_manager.dict_to_file_json = output_manager_original_method_states["dict_to_file_json"]


def test_initialize_herd_init_herd_false(
    mock_herd_factory: HerdFactory,
    mock_input_manager: InputManager,
    mock_output_manager: OutputManager,
    input_manager_original_method_states: Dict[str, Callable],
    output_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for initialize_herd() with init_herd=False"""
    mock_input_manager.get_data = mock.MagicMock()
    mock_input_manager.add_dict_variable_to_pool = mock.MagicMock()

    mock_output_manager.dict_to_file_json = mock.MagicMock()

    mock_animal_manager_get_animal_config = mocker.patch(
        "RUFAS.routines.animal.animal_manager.AnimalManager.get_animal_config"
    )

    mock_feed = mock.MagicMock(auto_spec=Feed)
    mock_feed.nutrient_rqmts = "NASEM"
    mocker.patch("RUFAS.routines.animal.life_cycle.herd_factory.Feed", return_value=mock_feed)

    mock_animal_base_set_config = mocker.patch("RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_config")
    mock_animal_base_set_nutrient_list = mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_nutrient_list"
    )
    mock_animal_base_set_lactation_curve_parameters = mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.set_lactation_curve_parameters"
    )

    mock_herd_factory.init_herd = False
    mock_herd_factory.save_animals = False
    mock_herd_factory.save_animals_path = Path("dummy_path")

    mock_herd_factory._generate_animals = mock.MagicMock()
    mock_herd_factory._initialize_herd_from_data = mock.MagicMock()
    mock_herd_factory._random_sample_with_replacement = mock.MagicMock()

    mock_herd_factory.initialize_herd()

    assert mock_input_manager.get_data.call_count == 2
    mock_animal_manager_get_animal_config.assert_called_once()
    mock_animal_base_set_config.assert_called_once()
    mock_animal_base_set_nutrient_list.assert_called_once_with("NASEM")
    mock_animal_base_set_lactation_curve_parameters.assert_called_once()

    mock_herd_factory._generate_animals.assert_not_called()
    mock_herd_factory._initialize_herd_from_data.assert_called_once()
    mock_herd_factory._random_sample_with_replacement.assert_called_once()

    mock_output_manager.dict_to_file_json.assert_not_called()
    mock_input_manager.add_dict_variable_to_pool.assert_called_once_with(
        variable_name="runtime_animal_population",
        data=mock_herd_factory.post_animal_population.__repr__(),
        properties_blob_key="animal_population_properties",
        eager_termination=False,
    )

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]
    mock_input_manager.add_dict_variable_to_pool = input_manager_original_method_states["add_dict_variable_to_pool"]
    mock_output_manager.dict_to_file_json = output_manager_original_method_states["dict_to_file_json"]
