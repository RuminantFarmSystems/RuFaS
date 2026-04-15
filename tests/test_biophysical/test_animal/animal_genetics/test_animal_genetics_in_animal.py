from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import Genetics
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.genetic_history import GeneticHistory
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.rufas_time import RufasTime


def _make_mock_animal(animal_type: AnimalType = AnimalType.LAC_COW) -> Animal:
    """Return a partial Animal mock with only the attrs needed for genetics tests."""
    animal = MagicMock(spec=Animal)
    animal.animal_type = animal_type
    animal.id = 42
    animal.genetic_history = []
    return animal


def _make_mock_time(year: int = 2020, month: int = 6, simulation_day: int = 100) -> RufasTime:
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = simulation_day
    mock_time.current_date = datetime(year, month, 1)
    return mock_time


# ---------------------------------------------------------------------------
# _initialize_newborn_calf_genetics
# ---------------------------------------------------------------------------


def test_initialize_newborn_calf_genetics_with_dam_tbv(mocker: MockerFixture) -> None:
    """simulate_genetics=True + dam TBVs present → Genetics created with initialize_new_born_calf=True."""
    AnimalConfig.simulate_genetics = True
    AnimalConfig.average_phenotype["fat_kg"] = {2020: 10.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2020: 20.0}
    AnimalConfig.top_listing_semen["estimated_fat"] = {"2020-06": 50.0}
    AnimalConfig.top_listing_semen["estimated_protein"] = {"2020-06": 25.0}

    mock_genetics_cls = mocker.patch(
        "RUFAS.biophysical.animal.animal.Genetics",
        return_value=MagicMock(spec=Genetics),
    )

    animal = _make_mock_animal(AnimalType.CALF)
    newborn_args: NewBornCalfValuesTypedDict = {
        "dam_tbv_fat": 12.0,
        "dam_tbv_protein": 8.0,
    }
    mock_time = _make_mock_time(year=2020, month=6)

    # Call the unbound method directly on mock animal
    Animal._initialize_newborn_calf_genetics(animal, newborn_args, mock_time)

    mock_genetics_cls.assert_called_once_with(
        birth_year=2020,
        birth_month=6,
        animal_type=AnimalType.CALF,
        initialize_new_born_calf=True,
        dam_tbv_fat=12.0,
        dam_tbv_protein=8.0,
    )
    assert animal.genetics == mock_genetics_cls.return_value


def test_initialize_newborn_calf_genetics_without_dam_tbv(mocker: MockerFixture) -> None:
    """simulate_genetics=True + no dam TBVs → Genetics created with initialize_new_born_calf=False."""
    AnimalConfig.simulate_genetics = True
    AnimalConfig.average_phenotype["fat_kg"] = {2020: 10.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2020: 20.0}

    mock_genetics_cls = mocker.patch(
        "RUFAS.biophysical.animal.animal.Genetics",
        return_value=MagicMock(spec=Genetics),
    )

    animal = _make_mock_animal(AnimalType.CALF)
    animal.calves = 0
    newborn_args: NewBornCalfValuesTypedDict = {}  # no dam TBV keys
    mock_time = _make_mock_time(year=2020, month=6)

    Animal._initialize_newborn_calf_genetics(animal, newborn_args, mock_time)

    mock_genetics_cls.assert_called_once_with(
        birth_year=2020,
        animal_type=AnimalType.CALF,
        initialize_new_born_calf=False,
        parity=animal.calves,
    )
    assert animal.genetics == mock_genetics_cls.return_value


def test_initialize_newborn_calf_genetics_disabled(mocker: MockerFixture) -> None:
    """simulate_genetics=False → genetics set to None, Genetics never instantiated."""
    AnimalConfig.simulate_genetics = False
    mock_genetics_cls = mocker.patch("RUFAS.biophysical.animal.animal.Genetics")

    animal = _make_mock_animal(AnimalType.CALF)
    newborn_args: NewBornCalfValuesTypedDict = {"dam_tbv_fat": 5.0, "dam_tbv_protein": 3.0}
    mock_time = _make_mock_time()

    Animal._initialize_newborn_calf_genetics(animal, newborn_args, mock_time)

    mock_genetics_cls.assert_not_called()
    assert animal.genetics is None


# ---------------------------------------------------------------------------
# update_genetic_history
# ---------------------------------------------------------------------------


def _make_genetics_mock(fat: float = 1.0, protein: float = 2.0) -> MagicMock:
    g = MagicMock(spec=Genetics)
    g.to_dict.return_value = {"TBV_fat": fat, "TBV_protein": protein}
    return g


def test_update_genetic_history_disabled() -> None:
    """simulate_genetics=False → early return, genetic_history stays empty."""
    AnimalConfig.simulate_genetics = False
    animal = _make_mock_animal()
    animal.genetics = _make_genetics_mock()

    Animal.update_genetic_history(animal, simulation_day=1)

    assert animal.genetic_history == []


def test_update_genetic_history_empty_list_appends_entry() -> None:
    """Empty history → new GeneticHistory entry appended."""
    AnimalConfig.simulate_genetics = True
    animal = _make_mock_animal()
    animal.genetics = _make_genetics_mock(fat=10.0, protein=20.0)

    Animal.update_genetic_history(animal, simulation_day=5)

    assert len(animal.genetic_history) == 1
    entry = animal.genetic_history[0]
    assert entry["start_day"] == 5
    assert entry["end_day"] == 5
    assert entry["id"] == animal.id
    assert entry["animal_type"] == animal.animal_type
    assert entry["genetics"] == {"TBV_fat": 10.0, "TBV_protein": 20.0}


def test_update_genetic_history_changed_genetics_appends_new_entry() -> None:
    """Genetics changed → new entry appended, previous entry untouched."""
    AnimalConfig.simulate_genetics = True
    animal = _make_mock_animal()
    old_genetics = {"TBV_fat": 1.0, "TBV_protein": 2.0}
    animal.genetic_history = [
        GeneticHistory(start_day=1, end_day=3, id=animal.id, animal_type=animal.animal_type, genetics=old_genetics)
    ]
    animal.genetics = _make_genetics_mock(fat=99.0, protein=88.0)

    Animal.update_genetic_history(animal, simulation_day=4)

    assert len(animal.genetic_history) == 2
    assert animal.genetic_history[1]["start_day"] == 4
    assert animal.genetic_history[1]["genetics"]["TBV_fat"] == 99.0


def test_update_genetic_history_same_genetics_extends_end_day() -> None:
    """Genetics unchanged → end_day of last entry extended, no new entry added."""
    AnimalConfig.simulate_genetics = True
    animal = _make_mock_animal()
    same_genetics = {"TBV_fat": 5.0, "TBV_protein": 6.0}
    animal.genetic_history = [
        GeneticHistory(start_day=1, end_day=3, id=animal.id, animal_type=animal.animal_type, genetics=same_genetics)
    ]
    animal.genetics = MagicMock(spec=Genetics)
    animal.genetics.to_dict.return_value = same_genetics

    Animal.update_genetic_history(animal, simulation_day=4)

    assert len(animal.genetic_history) == 1
    assert animal.genetic_history[0]["end_day"] == 4


def test_update_genetic_history_duplicate_same_day_warns(mocker: MockerFixture) -> None:
    """Same genetics + same simulation_day → warning issued, end_day unchanged."""
    AnimalConfig.simulate_genetics = True
    mock_om = mocker.patch("RUFAS.biophysical.animal.animal.OutputManager")
    animal = _make_mock_animal()
    same_genetics = {"TBV_fat": 5.0, "TBV_protein": 6.0}
    animal.genetic_history = [
        GeneticHistory(start_day=3, end_day=3, id=animal.id, animal_type=animal.animal_type, genetics=same_genetics)
    ]
    animal.genetics = MagicMock(spec=Genetics)
    animal.genetics.to_dict.return_value = same_genetics

    Animal.update_genetic_history(animal, simulation_day=3)

    mock_om.return_value.add_warning.assert_called_once()
    assert animal.genetic_history[0]["end_day"] == 3
