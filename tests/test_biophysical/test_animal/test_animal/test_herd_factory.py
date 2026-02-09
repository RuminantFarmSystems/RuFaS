from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from unittest.mock import call, MagicMock

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, Breed
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput

from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime


@pytest.fixture
def mock_herd_factory(mocker: MockerFixture) -> HerdFactory:
    """Returns an HerdFactory object"""
    mocker.patch("RUFAS.rufas_time.RufasTime.__init__", return_value=None)
    mock_im_get_data([], mocker)
    mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.AnimalGenetics.initialize_class_variables",
        return_value=None,
    )
    return HerdFactory()


@pytest.fixture
def mock_time() -> RufasTime:
    return MagicMock(auto_spec=RufasTime)


def mock_im_get_data(side_effect: list[Any], mocker: MockerFixture) -> MagicMock:
    im = InputManager()
    get_data_side_effect = ["HO", AnimalConfig.calving_interval, 10000, 50000] + side_effect
    mock_get_data = mocker.patch.object(im, "get_data", side_effect=get_data_side_effect)
    return mock_get_data


def mock_animal(animal_type: AnimalType, animal_id: int, mocker: MockerFixture) -> Animal:
    animal: Animal = mocker.MagicMock(auto_spec=Animal)
    animal.animal_type = animal_type
    animal.id = animal_id
    return animal


def mock_animals(animal_type: AnimalType, number_of_animals: int, mocker: MockerFixture) -> list[Animal]:
    return [mock_animal(animal_type=animal_type, animal_id=i, mocker=mocker) for i in range(number_of_animals)]


def animal_update_side_effect(animal: Animal) -> DailyRoutinesOutput:
    next_life_stage_by_animal_type: dict[AnimalType, AnimalType] = {
        AnimalType.CALF: AnimalType.HEIFER_I,
        AnimalType.HEIFER_I: AnimalType.HEIFER_II,
        AnimalType.HEIFER_II: AnimalType.HEIFER_III,
        AnimalType.HEIFER_III: AnimalType.LAC_COW,
        AnimalType.LAC_COW: AnimalType.DRY_COW,
        AnimalType.DRY_COW: AnimalType.LAC_COW,
    }
    setattr(animal, "animal_type", next_life_stage_by_animal_type[animal.animal_type])
    return DailyRoutinesOutput(
        animal_status=AnimalStatus.LIFE_STAGE_CHANGED, herd_reproduction_statistics=HerdReproductionStatistics()
    )


def test_init(
    mocker: MockerFixture,
) -> None:
    """Unit test for __init__()"""
    mock_time_init = mocker.patch("RUFAS.rufas_time.RufasTime.__init__", return_value=None)
    mock_get_data = mock_im_get_data([], mocker)
    mock_animal_genetics_initialize_class_variables = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.AnimalGenetics.initialize_class_variables",
        return_value=None,
    )
    mock_animal_population_init = mocker.patch(
        "RUFAS.biophysical.animal.data_types.animal_population.AnimalPopulation.__init__",
        return_value=None,
    )

    HerdFactory()

    mock_time_init.assert_called_once_with()
    assert mock_get_data.call_args_list == [
        call("animal.herd_information.breed"),
        call("animal.animal_config.farm_level.repro.calving_interval"),
        call("animal.herd_initialization.initial_animal_num"),
        call("animal.herd_initialization.simulation_days"),
    ]
    mock_animal_genetics_initialize_class_variables.assert_called_once_with()
    assert mock_animal_population_init.call_args_list == [
        call(
            calves=[],
            heiferIs=[],
            heiferIIs=[],
            heiferIIIs=[],
            cows=[],
            replacement=[],
            current_animal_id=0,
        )
    ]


@pytest.mark.parametrize(
    "animal_type, days_in_pregnancy, is_ready_for_cow_stage",
    [
        (AnimalType.CALF, 0, False),
        (AnimalType.HEIFER_I, 0, False),
        (AnimalType.HEIFER_II, 0, False),
        (AnimalType.HEIFER_II, 10, False),
        (AnimalType.HEIFER_III, 0, True),
        (AnimalType.HEIFER_III, 10, True),
        (AnimalType.HEIFER_III, 0, False),
        (AnimalType.HEIFER_III, 10, False),
        (AnimalType.LAC_COW, 10, False),
        (AnimalType.LAC_COW, 0, False),
        (AnimalType.DRY_COW, 10, False),
        (AnimalType.DRY_COW, 0, False),
    ],
)
def test_animal_update_functions(
    animal_type: AnimalType,
    days_in_pregnancy: int,
    is_ready_for_cow_stage: bool,
    mock_herd_factory: HerdFactory,
    mock_time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Unit test for _heiferII_update()"""
    mock_herd_factory.time = mock_time

    animal = mock_animal(animal_type=animal_type, animal_id=8, mocker=mocker)
    animal.days_born = 15
    animal.days_in_pregnancy = days_in_pregnancy
    is_animal_pregnant = True if days_in_pregnancy > 0 else False
    setattr(animal, "is_pregnant", is_animal_pregnant)

    mock_daily_growth_update = mocker.patch.object(animal, "daily_growth_update")
    mock_daily_milking_update = mocker.patch.object(animal, "daily_milking_update")
    mock_daily_reproduction_update = mocker.patch.object(
        animal, "daily_reproduction_update", return_value=(None, HerdReproductionStatistics)
    )
    mock_evaluate_heiferIII_for_cow = mocker.patch.object(
        animal, "evaluate_heiferIII_for_cow", return_value=is_ready_for_cow_stage
    )
    mock_animal_life_stage_update = mocker.patch.object(
        animal, "animal_life_stage_update", return_value=(AnimalStatus.LIFE_STAGE_CHANGED, None)
    )

    type_error_to_function_call_map_by_animal_type: dict[
        AnimalType, dict[Callable[[Animal], DailyRoutinesOutput], bool]
    ] = {
        AnimalType.CALF: {
            mock_herd_factory._calf_and_heiferI_update: False,
            mock_herd_factory._heiferII_update: True,
            mock_herd_factory._heiferIII_update: True,
            mock_herd_factory._cow_update: True,
        },
        AnimalType.HEIFER_I: {
            mock_herd_factory._calf_and_heiferI_update: False,
            mock_herd_factory._heiferII_update: True,
            mock_herd_factory._heiferIII_update: True,
            mock_herd_factory._cow_update: True,
        },
        AnimalType.HEIFER_II: {
            mock_herd_factory._calf_and_heiferI_update: True,
            mock_herd_factory._heiferII_update: False,
            mock_herd_factory._heiferIII_update: True,
            mock_herd_factory._cow_update: True,
        },
        AnimalType.HEIFER_III: {
            mock_herd_factory._calf_and_heiferI_update: True,
            mock_herd_factory._heiferII_update: True,
            mock_herd_factory._heiferIII_update: False,
            mock_herd_factory._cow_update: True,
        },
        AnimalType.LAC_COW: {
            mock_herd_factory._calf_and_heiferI_update: True,
            mock_herd_factory._heiferII_update: True,
            mock_herd_factory._heiferIII_update: True,
            mock_herd_factory._cow_update: False,
        },
        AnimalType.DRY_COW: {
            mock_herd_factory._calf_and_heiferI_update: True,
            mock_herd_factory._heiferII_update: True,
            mock_herd_factory._heiferIII_update: True,
            mock_herd_factory._cow_update: False,
        },
    }

    expected_sub_module_update_function_calls_by_animal_type: dict[AnimalType, list[MagicMock]] = {
        AnimalType.CALF: [mock_daily_growth_update, mock_animal_life_stage_update],
        AnimalType.HEIFER_I: [mock_daily_growth_update, mock_animal_life_stage_update],
        AnimalType.HEIFER_II: [mock_daily_growth_update, mock_daily_reproduction_update, mock_animal_life_stage_update],
        AnimalType.HEIFER_III: [mock_daily_growth_update, mock_evaluate_heiferIII_for_cow],
        AnimalType.LAC_COW: [
            mock_daily_milking_update,
            mock_daily_growth_update,
            mock_daily_reproduction_update,
            mock_animal_life_stage_update,
        ],
        AnimalType.DRY_COW: [
            mock_daily_milking_update,
            mock_daily_growth_update,
            mock_daily_reproduction_update,
            mock_animal_life_stage_update,
        ],
    }

    for function_call, should_raise_type_error in type_error_to_function_call_map_by_animal_type[animal_type].items():
        if should_raise_type_error:
            with pytest.raises(TypeError):
                function_call(animal)
        else:
            result = function_call(animal)
            assert animal.days_born == 16

            for sub_module_function_call in expected_sub_module_update_function_calls_by_animal_type[animal_type]:
                sub_module_function_call.assert_called_once()

            if animal_type == AnimalType.HEIFER_III:
                if is_ready_for_cow_stage:
                    assert result.animal_status == AnimalStatus.LIFE_STAGE_CHANGED
                else:
                    assert result.animal_status == AnimalStatus.REMAIN
                    if is_animal_pregnant:
                        assert animal.days_in_pregnancy == days_in_pregnancy + 1
                    else:
                        assert animal.days_in_pregnancy == 0


@pytest.mark.parametrize("calf_num", [0, 1, 8])
def test_calves_update_wean_day_true(calf_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _calves_update() with wean_day=True"""
    mock_calves = mock_animals(animal_type=AnimalType.CALF, number_of_animals=calf_num, mocker=mocker)

    mock_calf_and_heiferI_update_update = mocker.patch.object(
        mock_herd_factory, "_calf_and_heiferI_update", side_effect=animal_update_side_effect
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=mock_calves, heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=[], replacement=[]
    )

    mock_herd_factory._calves_update()

    assert mock_calf_and_heiferI_update_update.call_count == calf_num
    assert len(mock_herd_factory.pre_animal_population.calves) == 0
    assert len(mock_herd_factory.pre_animal_population.heiferIs) == calf_num

    assert [calf.animal_type for calf in mock_herd_factory.pre_animal_population.calves] == []
    assert [heiferI.animal_type for heiferI in mock_herd_factory.pre_animal_population.heiferIs] == [
        AnimalType.HEIFER_I
    ] * calf_num


@pytest.mark.parametrize("calf_num", [0, 1, 8])
def test_calves_update_wean_day_false(calf_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _calves_update() with wean_day=False"""
    mock_calves = mock_animals(animal_type=AnimalType.CALF, number_of_animals=calf_num, mocker=mocker)

    mock_calf_and_heiferI_update_update = mocker.patch.object(
        mock_herd_factory,
        "_calf_and_heiferI_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.REMAIN, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=mock_calves, heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=[], replacement=[]
    )

    mock_herd_factory._calves_update()

    assert mock_calf_and_heiferI_update_update.call_count == calf_num
    assert len(mock_herd_factory.pre_animal_population.calves) == calf_num
    assert len(mock_herd_factory.pre_animal_population.heiferIs) == 0

    assert [calf.animal_type for calf in mock_herd_factory.pre_animal_population.calves] == [AnimalType.CALF] * calf_num
    assert [heiferI.animal_type for heiferI in mock_herd_factory.pre_animal_population.heiferIs] == []


@pytest.mark.parametrize("heiferI_num", [0, 1, 44])
def test_heiferI_update_second_stage_true(
    heiferI_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferI_update() with second_stage=True"""
    mock_heiferIs = mock_animals(animal_type=AnimalType.HEIFER_I, number_of_animals=heiferI_num, mocker=mocker)

    mock_calf_and_heiferI_update_update = mocker.patch.object(
        mock_herd_factory, "_calf_and_heiferI_update", side_effect=animal_update_side_effect
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=mock_heiferIs, heiferIIs=[], heiferIIIs=[], cows=[], replacement=[]
    )

    mock_herd_factory._heiferIs_update()

    assert mock_calf_and_heiferI_update_update.call_count == heiferI_num
    assert len(mock_herd_factory.pre_animal_population.heiferIs) == 0
    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == heiferI_num

    assert [heiferI.animal_type for heiferI in mock_herd_factory.pre_animal_population.heiferIs] == []
    assert [heiferII.animal_type for heiferII in mock_herd_factory.pre_animal_population.heiferIIs] == [
        AnimalType.HEIFER_II
    ] * heiferI_num


@pytest.mark.parametrize("heiferI_num", [0, 1, 44])
def test_heiferI_update_second_stage_false(
    heiferI_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferI_update() with second_stage=False"""
    mock_heiferIs = mock_animals(animal_type=AnimalType.HEIFER_I, number_of_animals=heiferI_num, mocker=mocker)

    mock_calf_and_heiferI_update_update = mocker.patch.object(
        mock_herd_factory,
        "_calf_and_heiferI_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.REMAIN, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=mock_heiferIs, heiferIIs=[], heiferIIIs=[], cows=[], replacement=[]
    )

    mock_herd_factory._heiferIs_update()

    assert mock_calf_and_heiferI_update_update.call_count == heiferI_num
    assert len(mock_herd_factory.pre_animal_population.heiferIs) == heiferI_num
    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == 0

    assert [heiferI.animal_type for heiferI in mock_herd_factory.pre_animal_population.heiferIs] == [
        AnimalType.HEIFER_I
    ] * heiferI_num
    assert [heiferII.animal_type for heiferII in mock_herd_factory.pre_animal_population.heiferIIs] == []


@pytest.mark.parametrize("heiferII_num", [0, 1, 38])
def test_heiferII_update_cull_stage_true(
    heiferII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferII_update() with cull_stage=True"""
    mock_heiferIIs = mock_animals(animal_type=AnimalType.HEIFER_II, number_of_animals=heiferII_num, mocker=mocker)

    mock_heiferII_update_update = mocker.patch.object(
        mock_herd_factory,
        "_heiferII_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.SOLD, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=mock_heiferIIs, heiferIIIs=[], cows=[], replacement=[]
    )

    mock_herd_factory._heiferIIs_update()

    assert mock_heiferII_update_update.call_count == heiferII_num
    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == 0
    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == 0

    assert [heiferII.animal_type for heiferII in mock_herd_factory.pre_animal_population.heiferIIs] == []
    assert [heiferIII.animal_type for heiferIII in mock_herd_factory.pre_animal_population.heiferIIIs] == []


@pytest.mark.parametrize("heiferII_num", [0, 1, 38])
def test_heiferII_update_cull_stage_false_third_stage_true(
    heiferII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferII_update() with cull_stage=False and third_stage=True"""
    mock_heiferIIs = mock_animals(animal_type=AnimalType.HEIFER_II, number_of_animals=heiferII_num, mocker=mocker)

    mock_heiferII_update_update = mocker.patch.object(
        mock_herd_factory, "_heiferII_update", side_effect=animal_update_side_effect
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=mock_heiferIIs, heiferIIIs=[], cows=[], replacement=[]
    )

    mock_herd_factory._heiferIIs_update()

    assert mock_heiferII_update_update.call_count == heiferII_num
    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == 0
    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == heiferII_num

    assert [heiferII.animal_type for heiferII in mock_herd_factory.pre_animal_population.heiferIIs] == []
    assert [heiferIII.animal_type for heiferIII in mock_herd_factory.pre_animal_population.heiferIIIs] == [
        AnimalType.HEIFER_III
    ] * heiferII_num


@pytest.mark.parametrize("heiferII_num", [0, 1, 38])
def test_heiferII_update_cull_stage_false_third_stage_false(
    heiferII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferII_update() with cull_stage=False and third_stage=False"""
    mock_heiferIIs = mock_animals(animal_type=AnimalType.HEIFER_II, number_of_animals=heiferII_num, mocker=mocker)

    mock_heiferII_update_update = mocker.patch.object(
        mock_herd_factory,
        "_heiferII_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.REMAIN, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=mock_heiferIIs, heiferIIIs=[], cows=[], replacement=[]
    )

    mock_herd_factory._heiferIIs_update()

    assert mock_heiferII_update_update.call_count == heiferII_num
    assert len(mock_herd_factory.pre_animal_population.heiferIIs) == heiferII_num
    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == 0

    assert [heiferII.animal_type for heiferII in mock_herd_factory.pre_animal_population.heiferIIs] == [
        AnimalType.HEIFER_II
    ] * heiferII_num
    assert [heiferIII.animal_type for heiferIII in mock_herd_factory.pre_animal_population.heiferIIIs] == []


@pytest.mark.parametrize("is_calf_sold", [True, False])
def test_cow_give_birth(is_calf_sold: bool, mock_herd_factory: HerdFactory, mocker: MockerFixture) -> None:
    """Unit test for _cow_give_birth() if the newborn calf is not sold"""
    dam_cow = mock_animal(AnimalType.DRY_COW, 6, mocker)
    dam_cow.breed = Breed.HO
    dam_cow.net_merit = 99.9
    dam_cow.nutrients.total_phosphorus_in_animal = 88.8
    dam_cow.nutrients.phosphorus_for_growth = 66.6
    dam_cow.nutrients.phosphorus_reserves = 23.3
    dam_cow.nutrients.phosphorus_for_gestation_required_for_calf = 8.8
    dam_cow.reproduction.calf_birth_weight = 18.8

    mock_calf = MagicMock(auto_spec=Animal)
    mock_calf.breed = dam_cow.breed
    mock_calf.sold = is_calf_sold
    mock_calf_init = mocker.patch("RUFAS.biophysical.animal.herd_factory.Animal", return_value=mock_calf)
    mock_calf.net_merit = 108.8

    mock_time = MagicMock(auto_spec=RufasTime)
    mock_herd_factory.time = mock_time

    mock_genetics_assign_net_merit_value_to_newborn_calf = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics."
        "AnimalGenetics.assign_net_merit_value_to_newborn_calf",
        return_value=108.8,
    )

    mock_pre_animal_population = AnimalPopulation(
        calves=[],
        heiferIs=[],
        heiferIIs=[],
        heiferIIIs=[],
        cows=[],
        replacement=[],
        current_animal_id=0,
    )
    mock_pre_animal_population.calves = []

    mock_herd_factory.pre_animal_population = mock_pre_animal_population

    mock_herd_factory._cow_give_birth(dam_cow)

    assert dam_cow.nutrients.total_phosphorus_in_animal == 169.9
    assert dam_cow.nutrients.phosphorus_for_gestation_required_for_calf == 0.0
    assert dam_cow.reproduction.calf_birth_weight == 0.0

    mock_calf_init.assert_called_once_with(
        NewBornCalfValuesTypedDict(
            id=AnimalPopulation.current_animal_id,
            breed=Breed.HO.name,
            birth_date="",
            days_born=0,
            initial_phosphorus=8.8,
            birth_weight=18.8,
            net_merit=0.0,
            animal_type=AnimalType.CALF.value,
        )
    )
    if is_calf_sold:
        mock_genetics_assign_net_merit_value_to_newborn_calf.assert_not_called()
        assert mock_herd_factory.pre_animal_population.calves == []
    else:
        mock_genetics_assign_net_merit_value_to_newborn_calf.assert_called_once_with(mock_time, Breed.HO, 99.9)
        assert mock_herd_factory.pre_animal_population.calves == [mock_calf]


@pytest.mark.parametrize(
    "heiferIII_num, simulation_day",
    [
        (0, 0),
        (1, 0),
        (5, 0),
        (0, 1888),
        (1, 1888),
        (5, 1888),
        (0, 3000),
        (1, 3000),
        (5, 3000),
        (0, 5888),
        (1, 5888),
        (5, 5888),
    ],
)
def test_heiferIII_update_cow_stage_true(
    heiferIII_num: int, simulation_day: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferIII_update() with cow_stage=True"""
    mock_heiferIIIs = mock_animals(animal_type=AnimalType.HEIFER_III, number_of_animals=heiferIII_num, mocker=mocker)

    mock_heiferIII_update_update = mocker.patch.object(
        mock_herd_factory,
        "_heiferIII_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.LIFE_STAGE_CHANGED, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )
    mock_cow_give_birth = mocker.patch.object(
        mock_herd_factory,
        "_cow_give_birth",
        side_effect=lambda animal: setattr(animal, "animal_type", AnimalType.LAC_COW),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=mock_heiferIIIs, cows=[], replacement=[]
    )

    mock_herd_factory._heiferIIIs_update(simulation_day)

    assert mock_heiferIII_update_update.call_count == heiferIII_num
    assert mock_cow_give_birth.call_count == heiferIII_num

    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == 0
    assert len(mock_herd_factory.pre_animal_population.cows) == heiferIII_num

    assert [heiferIII.animal_type for heiferIII in mock_herd_factory.pre_animal_population.heiferIIIs] == []
    assert [cow.animal_type for cow in mock_herd_factory.pre_animal_population.cows] == [
        AnimalType.LAC_COW
    ] * heiferIII_num

    if simulation_day < 3000:
        assert len(mock_herd_factory.pre_animal_population.replacement) == 0
        assert [heiferIII.animal_type for heiferIII in mock_herd_factory.pre_animal_population.replacement] == []
    else:

        assert len(mock_herd_factory.pre_animal_population.replacement) == heiferIII_num
        assert [heiferIII.animal_type for heiferIII in mock_herd_factory.pre_animal_population.replacement] == [
            AnimalType.HEIFER_III
        ] * heiferIII_num


@pytest.mark.parametrize("heiferIII_num", [0, 1, 5])
def test_heiferIII_update_cow_stage_false(
    heiferIII_num: int, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _heiferIII_update() with cow_stage=False"""
    mock_heiferIIIs = mock_animals(animal_type=AnimalType.HEIFER_III, number_of_animals=heiferIII_num, mocker=mocker)

    mock_heiferIII_update_update = mocker.patch.object(
        mock_herd_factory,
        "_heiferIII_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.REMAIN, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )
    mock_cow_give_birth = mocker.patch.object(
        mock_herd_factory,
        "_cow_give_birth",
        side_effect=lambda animal: setattr(animal, "animal_type", AnimalType.LAC_COW),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=mock_heiferIIIs, cows=[], replacement=[]
    )

    mock_herd_factory._heiferIIIs_update(3888)

    assert mock_heiferIII_update_update.call_count == heiferIII_num
    assert mock_cow_give_birth.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.heiferIIIs) == heiferIII_num
    assert len(mock_herd_factory.pre_animal_population.cows) == 0
    assert len(mock_herd_factory.pre_animal_population.replacement) == 0

    assert [heiferIII.animal_type for heiferIII in mock_herd_factory.pre_animal_population.heiferIIIs] == [
        AnimalType.HEIFER_III
    ] * heiferIII_num
    assert [cow.animal_type for cow in mock_herd_factory.pre_animal_population.cows] == []
    assert [heiferIII.animal_type for heiferIII in mock_herd_factory.pre_animal_population.replacement] == []


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_false_new_born_false(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=False and new_born=False"""
    mock_cows = mock_animals(animal_type=AnimalType.DRY_COW, number_of_animals=cow_num, mocker=mocker)
    for cow in mock_cows:
        cow.reproduction.calves = 1

    mock_cow_update_update = mocker.patch.object(
        mock_herd_factory,
        "_cow_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.REMAIN, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )
    mock_cow_give_birth = mocker.patch.object(
        mock_herd_factory,
        "_cow_give_birth",
        side_effect=lambda animal: setattr(animal, "animal_type", AnimalType.LAC_COW),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=mock_cows, replacement=[]
    )

    mock_herd_factory._cows_update()

    assert mock_cow_update_update.call_count == cow_num
    assert mock_cow_give_birth.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_true(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=True"""
    mock_cows = mock_animals(animal_type=AnimalType.DRY_COW, number_of_animals=cow_num, mocker=mocker)
    for cow in mock_cows:
        cow.reproduction.calves = 1

    mock_cow_update_update = mocker.patch.object(
        mock_herd_factory,
        "_cow_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.SOLD, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )
    mock_cow_give_birth = mocker.patch.object(
        mock_herd_factory,
        "_cow_give_birth",
        side_effect=lambda animal: setattr(animal, "animal_type", AnimalType.LAC_COW),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=mock_cows, replacement=[]
    )

    mock_herd_factory._cows_update()

    assert mock_cow_update_update.call_count == cow_num
    assert mock_cow_give_birth.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == 0


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_false_more_than_5_calves(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=False and cow.calves>4"""
    mock_cows = mock_animals(animal_type=AnimalType.DRY_COW, number_of_animals=cow_num, mocker=mocker)
    for cow in mock_cows:
        cow.reproduction.calves = 6

    mock_cow_update_update = mocker.patch.object(
        mock_herd_factory,
        "_cow_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.REMAIN, herd_reproduction_statistics=HerdReproductionStatistics()
        ),
    )
    mock_cow_give_birth = mocker.patch.object(
        mock_herd_factory,
        "_cow_give_birth",
        side_effect=lambda animal: setattr(animal, "animal_type", AnimalType.LAC_COW),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=mock_cows, replacement=[]
    )

    mock_herd_factory._cows_update()

    assert mock_cow_update_update.call_count == cow_num
    assert mock_cow_give_birth.call_count == 0

    assert len(mock_herd_factory.pre_animal_population.cows) == 0


@pytest.mark.parametrize("cow_num", [0, 1, 100])
def test_cow_update_culled_false_new_born_true(
    cow_num: int,
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _cow_update() with culled=False and new_born=True, the newborn calf is not culled or sold"""
    mock_cows = mock_animals(animal_type=AnimalType.DRY_COW, number_of_animals=cow_num, mocker=mocker)
    for cow in mock_cows:
        cow.reproduction.calves = 1

    mock_cow_update_update = mocker.patch.object(
        mock_herd_factory,
        "_cow_update",
        return_value=DailyRoutinesOutput(
            animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
            newborn_calf_config=NewBornCalfValuesTypedDict(
                id=1,
                breed=Breed.HO.name,
                birth_date="",
                days_born=0,
                initial_phosphorus=18.8,
                birth_weight=28.8,
                net_merit=0.0,
                animal_type=AnimalType.CALF.value,
            ),
            herd_reproduction_statistics=HerdReproductionStatistics(),
        ),
    )
    mock_cow_give_birth = mocker.patch.object(
        mock_herd_factory,
        "_cow_give_birth",
        side_effect=lambda animal: setattr(animal, "animal_type", AnimalType.LAC_COW),
    )

    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=mock_cows, replacement=[]
    )

    mock_herd_factory._cows_update()

    assert mock_cow_update_update.call_count == cow_num
    assert mock_cow_give_birth.call_count == cow_num

    assert len(mock_herd_factory.pre_animal_population.cows) == cow_num


@pytest.mark.parametrize(
    "initial_animal_num, simulation_days, is_calf_sold, is_calf_stillborn",
    [
        (0, 0, False, False),
        (1, 0, False, False),
        (10000, 0, False, False),
        (0, 1, False, False),
        (1, 1, False, False),
        (10000, 1, False, False),
        (0, 5000, False, False),
        (1, 5000, False, False),
        (10000, 5000, False, False),
        (0, 0, True, False),
        (1, 0, True, False),
        (10000, 0, True, False),
        (0, 1, True, False),
        (1, 1, True, False),
        (10000, 1, True, False),
        (0, 5000, True, False),
        (1, 5000, True, False),
        (10000, 5000, True, False),
    ],
)
def test_generate_animals(
    initial_animal_num: int,
    simulation_days: int,
    is_calf_sold: bool,
    is_calf_stillborn: bool,
    mock_herd_factory: HerdFactory,
    mock_time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Unit test for _generate_animals()"""
    mock_time.current_date = datetime.today()

    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=None)
    mock_genetics_assign_net_merit_value_to_newborn_calf = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics."
        "AnimalGenetics.assign_net_merit_value_to_animals_entering_herd",
        return_value=108.8,
    )

    mock_herd_factory.time = mock_time
    mock_herd_factory.breed = Breed.HO
    mock_herd_factory.initial_animal_num = initial_animal_num
    mock_herd_factory.simulation_days = simulation_days
    mock_herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=[], replacement=[]
    )

    mock_calves_update = mocker.patch.object(mock_herd_factory, "_calves_update")
    mock_heiferIs_update = mocker.patch.object(mock_herd_factory, "_heiferIs_update")
    mock_heiferIIs_update = mocker.patch.object(mock_herd_factory, "_heiferIIs_update")
    mock_heiferIIIs_update = mocker.patch.object(mock_herd_factory, "_heiferIIIs_update")
    mock_cows_update = mocker.patch.object(mock_herd_factory, "_cows_update")

    mock_calf = MagicMock(auto_spec=Animal)
    mock_calf.sold = is_calf_sold
    mock_calf.stillborn = is_calf_stillborn
    mock_calf_init = mocker.patch("RUFAS.biophysical.animal.herd_factory.Animal", return_value=mock_calf)

    result = mock_herd_factory._generate_animals()

    assert mock_calf_init.call_count == initial_animal_num

    assert mock_calves_update.call_count == simulation_days
    assert mock_heiferIs_update.call_count == simulation_days
    assert mock_heiferIIs_update.call_count == simulation_days
    assert mock_heiferIIIs_update.call_count == simulation_days
    assert mock_cows_update.call_count == simulation_days

    if is_calf_sold:
        assert mock_genetics_assign_net_merit_value_to_newborn_calf.call_count == 0
        assert mock_genetics_assign_net_merit_value_to_newborn_calf.call_count == 0
        assert len(result.calves) == 0
    else:
        assert mock_genetics_assign_net_merit_value_to_newborn_calf.call_count == initial_animal_num
        assert mock_genetics_assign_net_merit_value_to_newborn_calf.call_count == initial_animal_num
        assert len(result.calves) == initial_animal_num


@pytest.mark.parametrize(
    "days_born, expected_birth_date_str",
    [
        # No offset
        (0, "2025-02-27"),
        # Simple small offset
        (1, "2025-02-26"),
        # About a month offset
        (30, "2025-01-28"),
        # Exactly one year (365 days) - note 2024 is a leap year
        (365, "2024-02-28"),
        # 366 days to check leap-year boundary
        (366, "2024-02-27"),
        # Multiple years (2 * 365 + 1 for the leap year in between)
        (731, "2023-02-27"),
        # (Optional) Test negative days if you want to ensure the function
        # handles them gracefully
        (-1, "2025-02-28"),
    ],
)
def test_backtrack_animal_birth_date(
    days_born: int, expected_birth_date_str: str, mock_herd_factory: HerdFactory, mocker: MockerFixture
) -> None:
    """Unit test for _backtrack_animal_birth_date()"""
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.start_date = datetime(2025, 2, 27)

    result = mock_herd_factory._backtrack_animal_birth_date(days_born, mock_time)

    assert result == expected_birth_date_str


@pytest.mark.parametrize("animal_type", ["calf", "heiferI", "heiferII", "heiferIII", "cow"])
def test_init_animal_from_data(
    animal_type: str, mock_herd_factory: HerdFactory, mock_time: RufasTime, mocker: MockerFixture
) -> None:
    """Unit test for _init_animal_from_data() with heiferI"""
    dummy_animal_id = 31415
    dummy_animal_data = {"dummy": "data", "breed": "dummy", "days_born": 15}

    mock_genetics_assignment = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics."
        "AnimalGenetics.assign_net_merit_value_to_animals_entering_herd",
        return_value=0.0,
    )

    mocked_animal = MagicMock(auto_spec=Animal)
    mocked_animal.breed = Breed.HO
    mock_animal_init = mocker.patch("RUFAS.biophysical.animal.herd_factory.Animal", return_value=mocked_animal)

    mock_backtrack_animal_birth_date = mocker.patch.object(
        mock_herd_factory, "_backtrack_animal_birth_date", return_value=""
    )

    mock_pre_animal_population = MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.next_id.return_value = dummy_animal_id

    mock_herd_factory.pre_animal_population = mock_pre_animal_population
    mock_herd_factory.time = mock_time

    result = mock_herd_factory._init_animal_from_data(animal_type=animal_type, animal_data=dummy_animal_data)

    dummy_animal_data.update(id=dummy_animal_id)
    if animal_type == "calf":
        dummy_animal_data.update(p_init=0)

    mock_animal_init.assert_called_once_with(dummy_animal_data)
    mock_backtrack_animal_birth_date.assert_called_once_with(dummy_animal_data["days_born"], mock_time)
    mock_genetics_assignment.assert_called_once_with(birth_date="", breed=Breed.HO)

    assert result == mocked_animal


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
    mocker: MockerFixture,
) -> None:
    """Unit test for _init_herd_from_data()"""
    mocker.patch("RUFAS.rufas_time.RufasTime.__init__", return_value=None)
    mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.AnimalGenetics.initialize_class_variables",
        return_value=None,
    )
    mock_get_data = mock_im_get_data(
        [
            {
                "calves": [{"dummy_calf"}] * num_calf,
                "heiferIs": [{"dummy_heiferI"}] * num_heiferI,
                "heiferIIs": [{"dummy_heiferII"}] * num_heiferII,
                "heiferIIIs": [{"dummy_heiferIII"}] * num_heiferIII,
                "cows": [{"dummy_cow"}] * num_cow,
                "replacement": [{"dummy_replacement"}] * num_replacement,
            }
        ],
        mocker,
    )

    herd_factory = HerdFactory()

    mock_init_animal_from_data = mocker.patch.object(herd_factory, "_init_animal_from_data")
    herd_factory.pre_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=[], replacement=[]
    )
    AnimalPopulation.set_current_max_animal_id(0)

    mock_animal_population_init = mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.AnimalPopulation",
        return_value=None,
    )

    herd_factory._initialize_herd_from_data()

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

    assert mock_get_data.call_args_list == [
        call("animal.herd_information.breed"),
        call("animal.animal_config.farm_level.repro.calving_interval"),
        call("animal.herd_initialization.initial_animal_num"),
        call("animal.herd_initialization.simulation_days"),
        call("animal_population"),
    ]
    assert mock_init_animal_from_data.call_count == expected_init_animal_from_data_call_count
    assert mock_init_animal_from_data.call_args_list == expected_init_animal_from_data_call_args_list
    mock_animal_population_init.assert_called_once()


def test_random_sample_with_replacement(
    mock_herd_factory: HerdFactory,
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement()"""
    mock_random_sample_with_replacement_by_type = mocker.patch.object(
        mock_herd_factory, "_random_sample_with_replacement_by_type", return_value=[]
    )

    mock_herd_factory.post_animal_population = AnimalPopulation(
        calves=[], heiferIs=[], heiferIIs=[], heiferIIIs=[], cows=[], replacement=[]
    )
    AnimalPopulation.set_current_max_animal_id(0)

    mock_animal_population_init = mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.AnimalPopulation",
        return_value=None,
    )

    mock_herd_factory._random_sample_with_replacement()

    assert mock_random_sample_with_replacement_by_type.call_count == 15
    assert mock_animal_population_init.call_count == 1


@pytest.mark.parametrize(
    "pre_num, post_num, animal_type",
    [
        (0, 0, AnimalType.CALF),
        (1, 0, AnimalType.CALF),
        (8, 0, AnimalType.CALF),
        (1, 1, AnimalType.CALF),
        (1, 8, AnimalType.CALF),
        (8, 1, AnimalType.CALF),
        (8, 8, AnimalType.CALF),
        (0, 0, AnimalType.HEIFER_I),
        (1, 0, AnimalType.HEIFER_I),
        (8, 0, AnimalType.HEIFER_I),
        (1, 1, AnimalType.HEIFER_I),
        (1, 8, AnimalType.HEIFER_I),
        (8, 1, AnimalType.HEIFER_I),
        (8, 8, AnimalType.HEIFER_I),
        (0, 0, AnimalType.HEIFER_II),
        (1, 0, AnimalType.HEIFER_II),
        (8, 0, AnimalType.HEIFER_II),
        (1, 1, AnimalType.HEIFER_II),
        (1, 8, AnimalType.HEIFER_II),
        (8, 1, AnimalType.HEIFER_II),
        (8, 8, AnimalType.HEIFER_II),
        (0, 0, AnimalType.HEIFER_III),
        (1, 0, AnimalType.HEIFER_III),
        (8, 0, AnimalType.HEIFER_III),
        (1, 1, AnimalType.HEIFER_III),
        (1, 8, AnimalType.HEIFER_III),
        (8, 1, AnimalType.HEIFER_III),
        (8, 8, AnimalType.HEIFER_III),
        (0, 0, AnimalType.DRY_COW),
        (1, 0, AnimalType.DRY_COW),
        (8, 0, AnimalType.DRY_COW),
        (1, 1, AnimalType.DRY_COW),
        (1, 8, AnimalType.DRY_COW),
        (8, 1, AnimalType.DRY_COW),
        (8, 8, AnimalType.DRY_COW),
        (0, 0, AnimalType.LAC_COW),
        (1, 0, AnimalType.LAC_COW),
        (8, 0, AnimalType.LAC_COW),
        (1, 1, AnimalType.LAC_COW),
        (1, 8, AnimalType.LAC_COW),
        (8, 1, AnimalType.LAC_COW),
        (8, 8, AnimalType.LAC_COW),
    ],
)
def test_random_sample_with_replacement_by_type(
    pre_num: int,
    post_num: int,
    animal_type: AnimalType,
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement_by_type() with calf"""
    TEST_CONFIG_BY_ANIMAL_TYPE: dict[AnimalType, dict[str, str]] = {
        AnimalType.CALF: {
            "animal_type_string": "calf",
            "animal_population_attribute": "calves",
        },
        AnimalType.HEIFER_I: {
            "animal_type_string": "heiferI",
            "animal_population_attribute": "heiferIs",
        },
        AnimalType.HEIFER_II: {
            "animal_type_string": "heiferII",
            "animal_population_attribute": "heiferIIs",
        },
        AnimalType.HEIFER_III: {
            "animal_type_string": "heiferIII",
            "animal_population_attribute": "heiferIIIs",
        },
        AnimalType.LAC_COW: {
            "animal_type_string": "cow",
            "animal_population_attribute": "cows",
        },
        AnimalType.DRY_COW: {
            "animal_type_string": "cow",
            "animal_population_attribute": "cows",
        },
    }
    ANIMAL_NUM_KEY: dict[str, str] = {
        "calf": "animal.herd_information.calf_num",
        "heiferI": "animal.herd_information.heiferI_num",
        "heiferII": "animal.herd_information.heiferII_num",
        "heiferIII": "animal.herd_information.heiferIII_num_springers",
        "cow": "animal.herd_information.cow_num",
        "replacement": "animal.herd_information.replace_num",
    }

    mocker.patch("RUFAS.rufas_time.RufasTime.__init__", return_value=None)
    mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.AnimalGenetics.initialize_class_variables",
        return_value=None,
    )
    mock_get_data = mock_im_get_data([post_num], mocker)

    herd_factory = HerdFactory()

    mock_pre_animals = mock_animals(animal_type=animal_type, number_of_animals=pre_num, mocker=mocker)

    mock_pre_animal_population = MagicMock(auto_spec=AnimalPopulation)
    setattr(
        mock_pre_animal_population,
        TEST_CONFIG_BY_ANIMAL_TYPE[animal_type]["animal_population_attribute"],
        mock_pre_animals,
    )
    herd_factory.pre_animal_population = mock_pre_animal_population

    mock_post_animal_population = MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population_next_id_list = list(range(post_num))
    mock_post_animal_population.next_id = mocker.patch.object(
        mock_post_animal_population,
        "next_id",
        side_effct=mock_post_animal_population_next_id_list,
    )
    herd_factory.post_animal_population = mock_post_animal_population

    mock_random_choices = MagicMock(return_value=[0] * post_num)
    mocker.patch("random.choices", mock_random_choices)

    mock_deepcopy = MagicMock()
    mocker.patch("copy.deepcopy", mock_deepcopy)

    result = herd_factory._random_sample_with_replacement_by_type(
        TEST_CONFIG_BY_ANIMAL_TYPE[animal_type]["animal_type_string"]
    )

    assert mock_get_data.call_args_list == [
        call("animal.herd_information.breed"),
        call("animal.animal_config.farm_level.repro.calving_interval"),
        call("animal.herd_initialization.initial_animal_num"),
        call("animal.herd_initialization.simulation_days"),
        call(ANIMAL_NUM_KEY[TEST_CONFIG_BY_ANIMAL_TYPE[animal_type]["animal_type_string"]]),
    ]
    mock_random_choices.assert_called_once_with(list(range(pre_num)), k=post_num)
    assert mock_deepcopy.call_count == post_num
    assert len(result) == post_num


@pytest.mark.parametrize(
    "animal_type_str, parity_key, milking_fraction, is_milking, expected_k",
    [
        # milking cows: use milking_fraction as-is
        ("cows_parity_1_milking", "1", 0.5, True, 1),
        # not-milking cows: use (1 - milking_fraction)
        ("cows_parity_1_not_milking", "1", 0.6, False, 1),
    ],
)
def test_random_sample_with_replacement_by_type_parity_branches(
    mocker: MockerFixture,
    animal_type_str: str,
    parity_key: str,
    milking_fraction: float,
    is_milking: bool,
    expected_k: int,
) -> None:
    """Covers the parity/milking branch, including inversion of milking fraction for non-milking cows."""
    mocker.patch("RUFAS.biophysical.animal.herd_factory.HerdFactory.__init__", return_value=None)
    herd_factory = HerdFactory()

    pre_animals = [MagicMock() for _ in range(5)]
    pre_pop = MagicMock()
    pre_pop.filter_cow_status.return_value = pre_animals
    herd_factory.pre_animal_population = pre_pop

    mock_im = MagicMock()
    herd_factory.im = mock_im

    parity_input_name = f"animal.herd_information.parity_fractions.{parity_key}"

    def get_data_side_effect(key: str) -> float:
        if key == "animal.herd_information.milking_cow_fraction":
            return milking_fraction
        if key == parity_input_name:
            return 0.2 if is_milking else 0.25
        if key == "animal.herd_information.cow_num":
            return 10
        raise KeyError(key)

    mock_im.get_data.side_effect = get_data_side_effect

    mock_choices = mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.random.choices",
        return_value=[0] * expected_k,
    )
    mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.copy.deepcopy",
        side_effect=lambda x: x,
    )
    mocker.patch.object(AnimalPopulation, "next_id", return_value=1)

    result = herd_factory._random_sample_with_replacement_by_type(animal_type_str)

    pre_pop.filter_cow_status.assert_any_call(int(parity_key), is_milking)
    mock_choices.assert_called_once()
    assert len(result) == expected_k


def test_random_sample_with_replacement_by_type_exception_zero_animals_logs_missing_group_warning(
    mocker: MockerFixture,
) -> None:
    """Covers except-block branch where animal_num == 0."""
    mocker.patch("RUFAS.biophysical.animal.herd_factory.HerdFactory.__init__", return_value=None)
    herd_factory = HerdFactory()

    herd_factory.pre_animal_population = MagicMock()
    herd_factory.pre_animal_population.calves = [MagicMock()]

    mock_im = MagicMock()
    herd_factory.im = mock_im
    mock_im.get_data.return_value = 0

    mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.random.choices",
        side_effect=RuntimeError("boom"),
    )

    mock_om = mocker.patch("RUFAS.biophysical.animal.herd_factory.om")

    result = herd_factory._random_sample_with_replacement_by_type("calf")

    assert result == []
    mock_om.add_warning.assert_called_once()
    args, kwargs = mock_om.add_warning.call_args
    assert "Missing calf" in args[0]
    assert "No animals sampled for calf." in args[1]


def test_random_sample_with_replacement_by_type_exception_nonzero_animals_logs_population_file_warning(
    mocker: MockerFixture,
) -> None:
    """Covers except-block branch where animal_num > 0."""
    mocker.patch("RUFAS.biophysical.animal.herd_factory.HerdFactory.__init__", return_value=None)
    herd_factory = HerdFactory()

    herd_factory.pre_animal_population = MagicMock()
    herd_factory.pre_animal_population.calves = [MagicMock()]

    mock_im = MagicMock()
    herd_factory.im = mock_im
    mock_im.get_data.return_value = 5

    mocker.patch(
        "RUFAS.biophysical.animal.herd_factory.random.choices",
        side_effect=RuntimeError("boom"),
    )

    mock_om = mocker.patch("RUFAS.biophysical.animal.herd_factory.om")

    result = herd_factory._random_sample_with_replacement_by_type("calf")

    assert result == []
    mock_om.add_warning.assert_called_once()
    args, kwargs = mock_om.add_warning.call_args
    assert "Missing calf animal population file" in args[0]
    assert "No animals in group calf found in animal population file." in args[1]
    assert "Full error" in args[1]


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
    mocker: MockerFixture,
) -> None:
    """Unit test for _random_sample_with_replacement_by_type() with replacement cows"""
    mocker.patch("RUFAS.rufas_time.RufasTime.__init__", return_value=None)
    mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.AnimalGenetics.initialize_class_variables",
        return_value=None,
    )
    mock_get_data = mock_im_get_data([post_num], mocker)

    herd_factory = HerdFactory()

    mock_pre_animals = mock_animals(animal_type=AnimalType.HEIFER_III, number_of_animals=pre_num, mocker=mocker)

    mock_pre_animal_population = MagicMock(auto_spec=AnimalPopulation)
    mock_pre_animal_population.replacement = mock_pre_animals
    herd_factory.pre_animal_population = mock_pre_animal_population

    mock_post_animal_population = MagicMock(auto_spec=AnimalPopulation)
    mock_post_animal_population_next_id_list = list(range(post_num))
    mock_post_animal_population.next_id = mocker.patch.object(
        mock_post_animal_population,
        "next_id",
        side_effct=mock_post_animal_population_next_id_list,
    )
    herd_factory.post_animal_population = mock_post_animal_population

    mock_random_choices = MagicMock(return_value=[0] * post_num)
    mocker.patch("random.choices", mock_random_choices)

    mock_deepcopy = MagicMock()
    mocker.patch("copy.deepcopy", mock_deepcopy)

    result = herd_factory._random_sample_with_replacement_by_type("replacement")

    assert mock_get_data.call_args_list == [
        call("animal.herd_information.breed"),
        call("animal.animal_config.farm_level.repro.calving_interval"),
        call("animal.herd_initialization.initial_animal_num"),
        call("animal.herd_initialization.simulation_days"),
        call("animal.herd_information.replace_num"),
    ]
    mock_random_choices.assert_called_once_with(list(range(pre_num)), k=post_num)
    assert mock_deepcopy.call_count == post_num
    assert len(result) == post_num


def test_initialize_herd_init_herd_true_save_animals_true(
    mock_herd_factory: HerdFactory,
    mock_time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Unit test for initialize_herd() with init_herd=True and save_animals=True"""

    mock_om_dict_to_file_json = mocker.patch("RUFAS.output_manager.OutputManager.dict_to_file_json")
    mock_om_create_directory = mocker.patch("RUFAS.output_manager.OutputManager.create_directory")

    mock_initialize_animal_config = mocker.patch(
        "RUFAS.biophysical.animal.animal_config.AnimalConfig.initialize_animal_config"
    )
    mock_animal_set_lactation_curve_parameters = mocker.patch(
        "RUFAS.biophysical.animal.animal.Animal.setup_lactation_curve_parameters"
    )
    mock_set_milk_quality = mocker.patch(
        "RUFAS.biophysical.animal.milk.milk_production.MilkProduction.set_milk_quality"
    )

    mock_herd_factory.init_herd = True
    mock_herd_factory.save_animals = True
    mock_herd_factory.save_animals_path = Path("dummy_path")
    mock_herd_factory.time = mock_time

    mock_generate_animals = mocker.patch.object(mock_herd_factory, "_generate_animals")
    mock_initialize_herd_from_data = mocker.patch.object(mock_herd_factory, "_initialize_herd_from_data")
    mock_random_sample_with_replacement = mocker.patch.object(mock_herd_factory, "_random_sample_with_replacement")
    mock_report_animal_population_statistics = mocker.patch.object(
        AnimalModuleReporter, "report_animal_population_statistics"
    )

    dummy_time_str = "2023-12-12 13:34:42"
    with freeze_time(dummy_time_str):
        mock_herd_factory.initialize_herd()
        dummy_time_str_strf = datetime.now().strftime("%d-%b-%Y_%a_%H-%M-%S")

    expected_save_path = Path.joinpath(Path("dummy_path"), f"animal_population-{dummy_time_str_strf}.json")

    mock_initialize_animal_config.assert_called_once()
    mock_animal_set_lactation_curve_parameters.assert_called_once_with(mock_time)
    mock_set_milk_quality.assert_called_once_with(
        AnimalConfig.milk_fat_percent, AnimalConfig.true_protein_percent, AnimalModuleConstants.MILK_LACTOSE
    )

    mock_generate_animals.assert_called_once()
    mock_initialize_herd_from_data.assert_not_called()
    mock_random_sample_with_replacement.assert_called_once()
    assert mock_report_animal_population_statistics.call_count == 2

    mock_om_create_directory.assert_called_once_with(Path("dummy_path"))
    mock_om_dict_to_file_json.assert_called_once_with(
        mock_herd_factory.pre_animal_population.__repr__(),
        expected_save_path,
        minify_output_file=True,
    )


def test_initialize_herd_init_herd_true_save_animals_false(
    mock_herd_factory: HerdFactory,
    mock_time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Unit test for initialize_herd() with init_herd=True and save_animals=False"""
    mock_om_dict_to_file_json = mocker.patch("RUFAS.output_manager.OutputManager.dict_to_file_json")

    mock_initialize_animal_config = mocker.patch(
        "RUFAS.biophysical.animal.animal_config.AnimalConfig.initialize_animal_config"
    )
    mock_animal_set_lactation_curve_parameters = mocker.patch(
        "RUFAS.biophysical.animal.animal.Animal.setup_lactation_curve_parameters"
    )
    mock_set_milk_quality = mocker.patch(
        "RUFAS.biophysical.animal.milk.milk_production.MilkProduction.set_milk_quality"
    )

    mock_herd_factory.init_herd = True
    mock_herd_factory.save_animals = False
    mock_herd_factory.save_animals_path = Path("dummy_path")
    mock_herd_factory.time = mock_time

    mock_generate_animals = mocker.patch.object(mock_herd_factory, "_generate_animals")
    mock_initialize_herd_from_data = mocker.patch.object(mock_herd_factory, "_initialize_herd_from_data")
    mock_random_sample_with_replacement = mocker.patch.object(mock_herd_factory, "_random_sample_with_replacement")
    mock_report_animal_population_statistics = mocker.patch.object(
        AnimalModuleReporter, "report_animal_population_statistics"
    )

    mock_herd_factory.initialize_herd()

    mock_initialize_animal_config.assert_called_once()
    mock_animal_set_lactation_curve_parameters.assert_called_once_with(mock_time)
    mock_set_milk_quality.assert_called_once_with(
        AnimalConfig.milk_fat_percent, AnimalConfig.true_protein_percent, AnimalModuleConstants.MILK_LACTOSE
    )

    mock_generate_animals.assert_called_once()
    mock_initialize_herd_from_data.assert_not_called()
    mock_random_sample_with_replacement.assert_called_once()
    assert mock_report_animal_population_statistics.call_count == 2

    mock_om_dict_to_file_json.assert_not_called()


def test_initialize_herd_init_herd_with_sexed_semen_save_animals_false(
    mock_herd_factory: HerdFactory, mock_time: RufasTime, mocker: MockerFixture
) -> None:
    """Unit test for initialize_herd() with init_herd=True and save_animals=False"""
    mock_om_dict_to_file_json = mocker.patch("RUFAS.output_manager.OutputManager.dict_to_file_json")

    mock_initialize_animal_config = mocker.patch(
        "RUFAS.biophysical.animal.animal_config.AnimalConfig.initialize_animal_config"
    )
    mock_animal_set_lactation_curve_parameters = mocker.patch(
        "RUFAS.biophysical.animal.animal.Animal.setup_lactation_curve_parameters"
    )
    mock_set_milk_quality = mocker.patch(
        "RUFAS.biophysical.animal.milk.milk_production.MilkProduction.set_milk_quality"
    )

    mock_warning = mocker.patch.object(OutputManager, "add_warning")

    mock_herd_factory.init_herd = True
    mock_herd_factory.save_animals = False
    mock_herd_factory.save_animals_path = Path("dummy_path")
    mock_herd_factory.time = mock_time

    mock_generate_animals = mocker.patch.object(mock_herd_factory, "_generate_animals")
    mock_initialize_herd_from_data = mocker.patch.object(mock_herd_factory, "_initialize_herd_from_data")
    mock_random_sample_with_replacement = mocker.patch.object(mock_herd_factory, "_random_sample_with_replacement")
    mock_report_animal_population_statistics = mocker.patch.object(
        AnimalModuleReporter, "report_animal_population_statistics"
    )
    AnimalConfig.semen_type = "sexed"

    mock_herd_factory.initialize_herd()

    mock_initialize_animal_config.assert_called_once()
    mock_animal_set_lactation_curve_parameters.assert_called_once_with(mock_time)
    mock_set_milk_quality.assert_called_once_with(
        AnimalConfig.milk_fat_percent, AnimalConfig.true_protein_percent, AnimalModuleConstants.MILK_LACTOSE
    )

    mock_generate_animals.assert_called_once()
    mock_initialize_herd_from_data.assert_not_called()
    mock_random_sample_with_replacement.assert_called_once()
    assert mock_report_animal_population_statistics.call_count == 2
    mock_warning.assert_called_once()
    mock_om_dict_to_file_json.assert_not_called()


def test_initialize_herd_init_herd_false(
    mock_herd_factory: HerdFactory,
    mock_time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Unit test for initialize_herd() with init_herd=False"""
    mock_om_dict_to_file_json = mocker.patch("RUFAS.output_manager.OutputManager.dict_to_file_json")

    mock_initialize_animal_config = mocker.patch(
        "RUFAS.biophysical.animal.animal_config.AnimalConfig.initialize_animal_config"
    )
    mock_animal_set_lactation_curve_parameters = mocker.patch(
        "RUFAS.biophysical.animal.animal.Animal.setup_lactation_curve_parameters"
    )
    mock_set_milk_quality = mocker.patch(
        "RUFAS.biophysical.animal.milk.milk_production.MilkProduction.set_milk_quality"
    )

    mock_herd_factory.init_herd = False
    mock_herd_factory.save_animals = False
    mock_herd_factory.save_animals_path = Path("dummy_path")
    mock_herd_factory.time = mock_time

    mock_generate_animals = mocker.patch.object(mock_herd_factory, "_generate_animals")
    mock_initialize_herd_from_data = mocker.patch.object(mock_herd_factory, "_initialize_herd_from_data")
    mock_random_sample_with_replacement = mocker.patch.object(mock_herd_factory, "_random_sample_with_replacement")
    mock_report_animal_population_statistics = mocker.patch.object(
        AnimalModuleReporter, "report_animal_population_statistics"
    )

    mock_herd_factory.initialize_herd()

    mock_initialize_animal_config.assert_called_once()
    mock_animal_set_lactation_curve_parameters.assert_called_once_with(mock_time)
    mock_set_milk_quality.assert_called_once_with(
        AnimalConfig.milk_fat_percent, AnimalConfig.true_protein_percent, AnimalModuleConstants.MILK_LACTOSE
    )

    mock_generate_animals.assert_not_called()
    mock_initialize_herd_from_data.assert_called_once()
    mock_random_sample_with_replacement.assert_called_once()
    assert mock_report_animal_population_statistics.call_count == 2

    mock_om_dict_to_file_json.assert_not_called()
