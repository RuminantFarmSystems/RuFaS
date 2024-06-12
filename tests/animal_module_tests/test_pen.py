from __future__ import annotations

from statistics import mean
from typing import Set, List, Dict, Tuple
from unittest.mock import MagicMock

import pytest
from pytest_lazyfixture import lazy_fixture
from pytest_mock.plugin import MockerFixture

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.animal_combinations import AnimalCombination


@pytest.fixture
def pen() -> Pen:
    id_number = 0
    pen_name = ""
    vert_dist = 0.1
    horiz_dist = 1.6
    num_stalls = 100
    housing_type = "open air barn"
    bedding_type = "sand"
    pen_type = "freestall"
    manure_handling = "manual_scraping"
    manure_separator = "sedimentation"
    manure_separator_after_digestion = "screw_press"
    manure_storage = "storage_pit"
    animal_combination = AnimalCombination.CALF
    max_stocking_density = 1.2

    pen = Pen(
        id_number,
        pen_name,
        vert_dist,
        horiz_dist,
        num_stalls,
        housing_type,
        bedding_type,
        pen_type,
        manure_handling,
        manure_separator,
        manure_separator_after_digestion,
        manure_storage,
        animal_combination,
        max_stocking_density,
    )

    return pen


@pytest.fixture
def mock_animal_list() -> List[MagicMock]:
    animal_i = MagicMock()
    animal_ii = MagicMock()
    animal_iii = MagicMock()

    return [animal_i, animal_ii, animal_iii]


@pytest.fixture
def mock_animal_list_ii() -> List[MagicMock]:
    animal_iv = MagicMock()
    animal_v = MagicMock()
    animal_vi = MagicMock()

    return [animal_iv, animal_v, animal_vi]


@pytest.fixture
def mock_animal_list_combined(mock_animal_list, mock_animal_list_ii) -> List[MagicMock]:
    return mock_animal_list + mock_animal_list_ii


@pytest.fixture
def pen_with_animals(pen: Pen, mock_animal_list: List[MagicMock]) -> Pen:
    for animal in mock_animal_list:
        pen.animals_in_pen[animal.id] = animal
    # pen.animals_in_pen = mock_animal_list

    return pen


def animal_list(mocker: MockerFixture) -> List[Calf | Cow | HeiferI | HeiferII | HeiferIII]:
    """Returns a list of Calf, HeiferI, HeiferII, Cow and HeiferIII objects for testing purposes"""

    mocker.patch(
        "RUFAS.routines.animal.life_cycle.life_cycle.AnimalBase.nutrients",
        new_callable=mocker.PropertyMock,
        return_value=[],
    )

    animal_config = {
        "wean_day": 10,
        "semen_type": "conventional",
        "male_calf_rate_conventional_semen": 2.0,
        "male_calf_rate_sexed_semen": 3.0,
        "still_birth_rate": 1.0,
        "birth_weight": 0,
        "keep_female_calf_rate": 2.0,
        "mature_body_weight_avg": 1.0,
        "mature_body_weight_std": 1.0,
    }
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.life_cycle.AnimalBase.config",
        new_callable=mocker.PropertyMock,
        return_value=animal_config,
    )
    args = {
        "id": 2,
        "breed": 1,
        "birth_date": 1,
        "events": "3: simulation_day=0, event",
        "mature_body_weight": 2000.0,
        "wean_weight": 10.0,
        "days_born": 20,
        "birth_weight": 200,
        "p_init": 1,
        "repro_program": "ED",
        "repro_sub_protocol": "2P",
        "tai_method_h": "5dCG2P",
        "synch_ed_method_h": "2P",
        "calf_birth_weight": 200,
        "presynch_method": "Presynch",
        "resynch_method": "PGFatPD",
        "tai_method_c": "OvSynch 56",
    }
    calf = Calf(args)
    calf.id = 1
    heiferI = HeiferI(args)
    heiferII = HeiferII(args)
    heiferII.id = 3
    heiferIII = HeiferIII(args)
    heiferIII.id = 4
    cow1 = Cow(args)
    cow1.id = 5
    cow2 = Cow(args)
    cow2.id = 6
    cow1.is_milking = True
    cow2.is_milking = False

    return [heiferI, heiferII, heiferIII, calf, cow1, cow2]


@pytest.mark.parametrize(
    "pen_to_test, new_animals, expected_animals_in_pen",
    [
        (
            lazy_fixture("pen"),
            lazy_fixture("mock_animal_list"),
            lazy_fixture("mock_animal_list"),
        ),
        (
            lazy_fixture("pen_with_animals"),
            lazy_fixture("mock_animal_list_ii"),
            lazy_fixture("mock_animal_list_combined"),
        ),
    ],
)
def test_add_new_animals(
    pen_to_test: Pen,
    mock_animal_list,
    new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII],
    expected_animals_in_pen: List[Calf | Cow | HeiferI | HeiferII | HeiferIII],
) -> None:
    """Unit test for function add_new_animals in file routines/animal/pen.py"""

    pen_to_test.add_new_animals(new_animals)
    pen_values = list(pen_to_test.animals_in_pen.values())
    assert pen_values == expected_animals_in_pen


@pytest.mark.parametrize(
    "pen_to_test, expected_stocking_density",
    [
        (lazy_fixture("pen"), 0),
        (lazy_fixture("pen_with_animals"), 0.03),
    ],
)
def test_current_stocking_density(pen_to_test: Pen, expected_stocking_density: float) -> None:
    """Unit test for function update_stocking_density in file routines/animal/pen.py"""

    assert pen_to_test.current_stocking_density == expected_stocking_density


@pytest.mark.parametrize(
    "animal_combination ",
    [
        AnimalCombination.CALF,
        AnimalCombination.GROWING,
        AnimalCombination.LAC_COW,
        AnimalCombination.CLOSE_UP,
        AnimalCombination.GROWING_AND_CLOSE_UP,
    ],
)
def test_update_animal_combination(pen: Pen, animal_combination: AnimalCombination) -> None:
    """Unit test for function update_animal_combination in file routines/animal/pen.py"""
    pen.update_animal_combination(animal_combination)

    assert pen.animal_combination == animal_combination


def test_update_animals(pen: Pen, mocker: MockerFixture) -> None:
    """Unit test for function update_animals in file routines/animal/pen.py"""

    mocker.patch("RUFAS.routines.animal.pen.Pen.add_new_animals")
    mocker.patch("RUFAS.routines.animal.pen.Pen.update_animal_combination")
    mocker.patch("RUFAS.routines.animal.pen.Pen.calc_daily_walking_dist")
    mocker.patch("RUFAS.routines.animal.pen.Pen.update_classes_in_pen")

    pen.update_animals(MagicMock(), MagicMock())

    pen.add_new_animals.assert_called_once()
    pen.update_animal_combination.assert_called_once()
    pen.calc_daily_walking_dist.assert_called_once()
    pen.update_classes_in_pen.assert_called_once()


def test_set_avg_nutrient_rqmts(pen: Pen) -> None:
    """Unit test for function set_avg_nutrient_rqmts in file routines/animal/pen.py"""
    avg_nutrient_rqmts = {
        "NEmaint_requirement": 22.739694446587276,
        "NEa_requirement": 0,
        "NEg_requirement": 0.0,
        "NEpreg_requirement": 0.8809032714863911,
        "NEl_requirement": 0,
        "MP_requirement": 169.60219829211576,
        "Ca_requirement": 8.551061771355254,
        "P_requirement": 0.8978663353409345,
        "DMIest_requirement": 0,
        "avg_BW": 445.74074026264447,
    }

    pen.set_avg_nutrient_rqmts(avg_nutrient_rqmts)

    assert pen.avg_nutrient_rqmts == avg_nutrient_rqmts


def test_set_milk_avgs(pen: Pen) -> None:
    """Unit test for function set_milk_avgs in file routines/animal/pen.py"""
    avg_milk = 40.362
    avg_CP_milk = 3.196
    avg_milk_production_reduction = 1.5

    pen.set_milk_avgs(avg_milk, avg_CP_milk, avg_milk_production_reduction)

    assert pen.avg_milk == avg_milk and pen.avg_CP_milk == avg_CP_milk and pen.avg_milk_production_reduction == 1.5


@pytest.mark.parametrize(
    "pen_to_test",
    [
        (lazy_fixture("pen")),
    ],
)
def test_calc_manure(pen_to_test: Pen, mocker: MockerFixture) -> None:
    """Unit test for function calc_manure in file routines/animal/pen.py"""

    animals = animal_list(mocker)
    man_sums = mocker.patch.object(Pen, "manure_sums")
    man_sums.return_value = (mocker.MagicMock(), mocker.MagicMock())
    pen_to_test.add_new_animals(animals)
    patches = {}
    methane_model = mocker.MagicMock()
    feed = mocker.MagicMock(spec="Feed")
    feed.available_feeds = mocker.MagicMock()

    for animal in animals:
        animal_type = type(animal)
        patches[animal_type] = mocker.patch.object(animal_type, "calc_manure_excretion")

    # act
    Pen.calc_manure(pen_to_test, feed, methane_model)

    # assert
    for animal in patches:
        if animal == Cow:
            patches[animal].assert_called_with(feed, methane_model, pen_to_test.MEdiet)
        else:
            patches[animal].assert_called_once_with(feed, methane_model)
    man_sums.assert_called()


def test_reset_manure(pen: Pen) -> None:
    """Unit test for function reset_manure in file routines/animal/pen.py"""
    pen.manure = {}
    pen.calf_total = {}
    pen.heifer_total = {}
    pen.dry_total = {}
    pen.lactating_total = {}

    expected = AnimalManureExcretions(
        urea=0.0,
        urine=0.0,
        total_ammoniacal_nitrogen_concentration=0.0,
        urine_nitrogen=0.0,
        manure_nitrogen=0.0,
        manure_mass=0.0,
        total_solids=0.0,
        degradable_volatile_solids=0.0,
        non_degradable_volatile_solids=0.0,
        inorganic_phosphorus_fraction=0.0,
        organic_phosphorus_fraction=0.0,
        non_water_inorganic_phosphorus_fraction=0.0,
        non_water_organic_phosphorus_fraction=0.0,
        phosphorus=0.0,
        phosphorus_fraction=0.0,
        potassium=0.0,
        enteric_methane_g=0.0,
    )

    pen.reset_manure()

    assert pen.manure == expected
    assert pen.calf_total == expected
    assert pen.heifer_total == expected
    assert pen.dry_total == expected
    assert pen.lactating_total == expected


@pytest.fixture
def mock_calves_with_daily_growth(
    calf_daily_growth_values: List[float],
) -> List[MagicMock]:
    calves = [MagicMock() for i in range(3)]

    for calf, daily_growth in zip(calves, calf_daily_growth_values):
        calf.daily_growth = daily_growth

    return calves


@pytest.fixture
def calf_daily_growth_values() -> List[float]:
    return [
        0.7445883642358595,
        0.7254529863013488,
        0.7342433606191534,
    ]


@pytest.fixture
def avg_calf_daily_growth_values(calf_daily_growth_values: List[float]) -> float:
    return mean(calf_daily_growth_values)


@pytest.mark.parametrize(
    "pen_animals, expected",
    [
        (
            lazy_fixture("mock_calves_with_daily_growth"),
            lazy_fixture("avg_calf_daily_growth_values"),
        ),
        ([], 0),
    ],
)
def test_calc_avg_growth(pen: Pen, pen_animals, expected) -> None:
    """Unit test for function calc_avg_growth in file routines/animal/pen.py"""
    for animal in pen_animals:
        pen.animals_in_pen[animal.id] = animal
    # pen.animals_in_pen = pen_animals
    pen.calc_avg_growth()

    actual = pen.avg_growth

    assert actual == expected


def test_daily_p_update():
    """Unit test for function daily_p_update in file routines/animal/pen.py"""


def test_clear(pen: Pen) -> None:
    """Unit test for function clear in file routines/animal/pen.py"""
    calves = {0: MagicMock()}
    pen.animals_in_pen = calves
    assert pen.is_populated is True
    pen.avg_p_animal = 1.0

    pen.clear()

    assert pen.animals_in_pen == {}
    assert pen.is_populated is False
    assert pen.avg_p_animal == 0


def feed_allocations() -> Dict[AnimalCombination, Set[int]]:
    calf = {155, 156, 157}
    growing = {2, 51, 86, 136}
    close_up = {2, 26, 86, 118, 136, 139}
    lac_cow = {26, 86, 103, 118, 136, 139}

    return {
        AnimalCombination.CALF: calf,
        AnimalCombination.GROWING: growing,
        AnimalCombination.CLOSE_UP: close_up,
        AnimalCombination.GROWING_AND_CLOSE_UP: growing | close_up,
        AnimalCombination.LAC_COW: lac_cow,
    }


def dict_to_tuple_list(d: Dict) -> List[Tuple]:
    return list(d.items())


@pytest.mark.parametrize(
    "test_animal_combination, expected_feed_allocation",
    dict_to_tuple_list(feed_allocations()),
)
def test_subset_class_feeds(
    pen: Pen,
    test_animal_combination: AnimalCombination,
    expected_feed_allocation: Set[int],
) -> None:
    """Unit test for function subset_class_feeds in file routines/animal/pen.py"""

    feed = MagicMock()
    feed.input_feed_combinations = feed_allocations()

    pen.animal_combination = test_animal_combination
    pen.subset_class_feeds(feed)
    assert pen.allocated_feeds == expected_feed_allocation


@pytest.mark.parametrize(
    "animal_type, is_lactating_cow, expected_prefix",
    [
        # Testing with each animal type and its corresponding prefix
        (Calf, False, "daily_aggregate_calf"),
        (HeiferI, False, "daily_aggregate_heifer"),
        (HeiferII, False, "daily_aggregate_heifer"),
        (HeiferIII, False, "daily_aggregate_heifer"),
        (Cow, False, "daily_aggregate_dry_cow"),
        # Testing with a lactating cow, which should have a different prefix compared to a dry cow
        (Cow, True, "daily_aggregate_lactating_cow"),
        # Edge case: Unrecognized animal type
        (MagicMock, False, ValueError),
    ],
)
def test_get_prefix_and_default_manure_excretion(
    mocker: MockerFixture,
    animal_type: Calf | HeiferI | HeiferII | HeiferIII | Cow | MagicMock,
    is_lactating_cow: bool,
    expected_prefix: str | ValueError,
) -> None:
    """
    Unit test for the static method _get_prefix_and_default_manure_excretion in pen.py.

    This test verifies that the method correctly returns the prefix and default manure excretion value
    based on the given animal type and whether it's a lactating cow.

    """
    # Arrange
    animal = MagicMock(spec=animal_type)
    animal.__class__.__name__ = animal_type.__name__
    mock_default_manure = mocker.MagicMock()
    patch_for_get_default_animal_manure_excretions = mocker.patch(
        "RUFAS.routines.animal.pen.get_default_animal_manure_excretions",
        return_value=mock_default_manure,
    )

    # Act and assert
    if expected_prefix is ValueError:
        with pytest.raises(ValueError, match=f"Unrecognized animal type: {type(animal)}"):
            Pen._get_prefix_and_default_manure_excretion(animal, is_lactating_cow)
    else:
        prefix, manure = Pen._get_prefix_and_default_manure_excretion(animal, is_lactating_cow)
        assert prefix == expected_prefix
        assert manure == mock_default_manure
        patch_for_get_default_animal_manure_excretions.assert_called_once()


@pytest.mark.parametrize(
    "animal_class, is_lactating",
    [
        (Calf, False),
        (HeiferI, False),
        (HeiferII, False),
        (HeiferIII, False),
        (Cow, False),
        (Cow, True),
    ],
)
def test_calc_animal_manure_excretion(
    mocker: MockerFixture,
    animal_class: Calf | HeiferI | HeiferII | HeiferIII | Cow | MagicMock,
    is_lactating: bool,
) -> None:
    """
    Unit test for the _calc_animal_manure_excretion method in pen.py.

    This test verifies that the method correctly calculates the manure excretion for a given animal
    and returns the appropriate prefix and excretions. It tests different animal types and whether the animal
    is lactating or not.

    """
    # Arrange
    animal = mocker.MagicMock(spec=animal_class)
    animal.is_lactating = is_lactating
    animal.__class__.__name__ = animal_class.__name__
    mock_prefix = mocker.MagicMock()
    mock_default_manure = mocker.MagicMock()
    mocker.patch("RUFAS.routines.animal.pen.Pen.__init__", return_value=None)
    pen = Pen()  # type: ignore
    patch_for_get_prefix_and_default_manure_excretion = mocker.patch.object(
        Pen,
        "_get_prefix_and_default_manure_excretion",
        return_value=(mock_prefix, mock_default_manure),
    )
    pen.MEdiet = mock_MEdiet = mocker.MagicMock()
    pen.ration_nutrient_amount = mock_ration_nutrient_amount = mocker.MagicMock()
    pen.ration_nutrient_conc = mock_ration_nutrient_conc = mocker.MagicMock()
    mock_methane_model = mocker.MagicMock()
    mock_methane_mitigation_method = mocker.MagicMock()
    mock_methane_mitigation_additive_amount = mocker.MagicMock()

    # Act
    actual_prefix, actual_manure = pen._calc_animal_manure_excretion(
        animal,
        mock_methane_model,
        mock_methane_mitigation_method,
        mock_methane_mitigation_additive_amount,
    )

    # Assert
    assert actual_prefix == mock_prefix
    assert actual_manure == mock_default_manure
    patch_for_get_prefix_and_default_manure_excretion.assert_called_once_with(animal, is_lactating)
    if animal_class.__name__ == "Cow":
        animal.calc_manure_excretion.assert_called_once_with(
            mock_methane_model,
            mock_methane_mitigation_method,
            mock_methane_mitigation_additive_amount,
            mock_MEdiet,
            nutrient_amount=mock_ration_nutrient_amount,
            nutrient_conc=mock_ration_nutrient_conc,
        )
    else:
        animal.calc_manure_excretion.assert_called_once_with(
            mock_methane_model,
            nutrient_amount=mock_ration_nutrient_amount,
            nutrient_conc=mock_ration_nutrient_conc,
        )


@pytest.mark.parametrize(
    "initial_dict, prefix, default_manure, initial_pen_manure, animal_manure_excretion, expected_dict, expected_manure",
    [
        # Existing Prefix
        (
            {"test_prefix": {"prefix": "nested_test_prefix", "manure": "test_manure"}},
            "test_prefix",
            "default_manure",
            "initial_manure",
            "animal_manure_excretion",
            {
                "test_prefix": {
                    "prefix": "nested_test_prefix",
                    "manure": "test_manure_animal_manure_excretion",
                }
            },
            "initial_manure_animal_manure_excretion",
        ),
        # New Prefix
        (
            {},
            "new_prefix",
            "default_manure",
            "initial_manure",
            "animal_manure_excretion",
            {
                "new_prefix": {
                    "prefix": "new_prefix",
                    "manure": "default_manure_animal_manure_excretion",
                }
            },
            "initial_manure_animal_manure_excretion",
        ),
        # Multiple Existing Prefixes
        (
            {
                "prefix1": {"prefix": "prefix1", "manure": "manure1"},
                "prefix2": {"prefix": "prefix2", "manure": "manure2"},
            },
            "prefix1",
            "default_manure",
            "initial_manure",
            "animal_manure_excretion",
            {
                "prefix1": {
                    "prefix": "prefix1",
                    "manure": "manure1_animal_manure_excretion",
                },
                "prefix2": {"prefix": "prefix2", "manure": "manure2"},
            },
            "initial_manure_animal_manure_excretion",
        ),
        # Empty Manure for Specific Prefix
        (
            {"test_prefix": {"prefix": "nested_test_prefix", "manure": ""}},
            "test_prefix",
            "default_manure",
            "initial_manure",
            "animal_manure_excretion",
            {
                "test_prefix": {
                    "prefix": "nested_test_prefix",
                    "manure": "_animal_manure_excretion",
                }
            },
            "initial_manure_animal_manure_excretion",
        ),
    ],
)
def test_update_animal_manure_excretion_data(
    mocker: MockerFixture,
    initial_dict: dict,
    prefix: str,
    default_manure: str,
    initial_pen_manure: str,
    animal_manure_excretion: str,
    expected_dict: dict,
    expected_manure: str,
) -> None:
    """
    Unit test for the _update_animal_manure_excretion_data method in pen.py.

    This test verifies that the method correctly updates the manure excretion dictionaries and
    the `self.manure` variable according to the given parameters.

    """
    # Arrange
    is_prefix_in_dict = prefix in initial_dict  # Need to save this check before update
    initial_animal_manure = initial_dict[prefix]["manure"] if is_prefix_in_dict else ""
    mock_animal = mocker.MagicMock()
    mock_animal.manure_excretion = animal_manure_excretion
    patch_for_add_animal_manure_excretions = mocker.patch(
        "RUFAS.routines.animal.pen.add_animal_manure_excretions",
        side_effect=lambda x, y: x + "_" + y,
    )

    # Act
    Pen._update_animal_manure_excretion_data(initial_dict, prefix, default_manure, mock_animal)  # type: ignore

    # Assert
    assert initial_dict == expected_dict

    if is_prefix_in_dict:
        patch_for_add_animal_manure_excretions.assert_has_calls(
            [mocker.call(initial_animal_manure, animal_manure_excretion)]
        )
    else:
        patch_for_add_animal_manure_excretions.assert_has_calls([mocker.call(default_manure, animal_manure_excretion)])


@pytest.mark.parametrize(
    "is_populated, animals_in_pen, mock_pen_manure",
    [
        # Testing with two distinct animal types and two manure properties
        (
            True,
            {0: MagicMock(spec=Calf), 1: MagicMock(spec=HeiferI)},
            {"property1": "value1", "property2": "value2"},
        ),
        # Testing with three distinct animal types (Calf, HeiferI, and Cow) and a single manure property
        (
            True,
            {
                0: MagicMock(spec=Calf),
                1: MagicMock(spec=HeiferI),
                2: MagicMock(spec=Cow),
            },
            {"property3": "value3"},
        ),
        # Testing with an empty pen and no manure properties
        (False, {}, {}),
        # Testing with an empty pen but with one manure property
        (False, {}, {"property4": "value4"}),
        # Testing with empty manure dictionary but populated pen
        (True, {0: MagicMock(spec=Calf)}, {}),
        # Testing with a single animal type in pen
        (True, {0: MagicMock(spec=Calf)}, {"property1": "value1"}),
        # Testing with mixed animal types in the pen
        (
            True,
            {
                0: MagicMock(spec=Calf),
                1: MagicMock(spec=HeiferI),
                2: MagicMock(spec=Cow),
            },
            {"property1": "value1", "property2": "value2"},
        ),
        # Testing with multiple similar animals in the pen
        (
            True,
            {0: MagicMock(spec=Calf), 1: MagicMock(spec=Calf)},
            {"property1": "value1"},
        ),
        # Testing with null or None values within manure properties
        (True, {0: MagicMock(spec=Calf)}, {"property1": None}),
    ],
)
def test_calc_total_manure(
    mocker: MockerFixture,
    is_populated: bool,
    animals_in_pen: dict[int, MagicMock],
    mock_pen_manure: dict[str, str],
) -> None:
    """
    Unit test for method calc_total_manure in file pen.py.
    """

    # Arrange
    mocker.patch("RUFAS.routines.animal.pen.Pen.__init__", return_value=None)
    pen = Pen()  # type: ignore
    pen.id = "mock_pen_id"
    pen.manure = mock_pen_manure
    mocker.patch.object(Pen, "is_populated", return_value=is_populated, new_callable=mocker.PropertyMock)
    for animal in list(animals_in_pen.values()):
        animal.manure_excretion = MagicMock(spec=AnimalManureExcretions)
    pen.animals_in_pen = animals_in_pen
    methane_model = mocker.MagicMock()
    methane_mitigation_method = mocker.MagicMock()
    methane_mitigation_additive_amount = mocker.MagicMock()
    manure_excretions_output_data = mocker.MagicMock()
    mock_prefixes = [mocker.MagicMock() for _ in range(len(animals_in_pen))]
    mock_animal_manure_excretions = [mocker.MagicMock() for _ in range(len(animals_in_pen))]
    patch_for_calc_animal_manure_excretion = mocker.patch.object(
        pen,
        "_calc_animal_manure_excretion",
        side_effect=zip(mock_prefixes, mock_animal_manure_excretions),
    )
    patch_for_update_animal_manure_excretion_data = mocker.patch.object(pen, "_update_animal_manure_excretion_data")
    patch_for_add_animal_manure_excretions = mocker.patch(
        "RUFAS.routines.animal.pen.add_animal_manure_excretions",
        return_value=mock_pen_manure,
    )
    patch_for_get_default_animal_manure_excretions = mocker.patch(
        "RUFAS.routines.animal.pen.get_default_animal_manure_excretions",
        return_value=mock_pen_manure,
    )

    # Act
    pen.calc_total_manure(
        methane_model,
        methane_mitigation_method,
        methane_mitigation_additive_amount,
        manure_excretions_output_data,
    )

    if is_populated:
        patch_for_get_default_animal_manure_excretions.assert_called_once()
        for animal in list(animals_in_pen.values()):
            patch_for_calc_animal_manure_excretion.assert_has_calls(
                [
                    mocker.call(
                        animal,
                        methane_model,
                        methane_mitigation_method,
                        methane_mitigation_additive_amount,
                    )
                ]
            )
            patch_for_add_animal_manure_excretions.assert_has_calls(
                [mocker.call(mock_pen_manure, animal.manure_excretion)]
            )
        assert patch_for_update_animal_manure_excretion_data.call_count == len(animals_in_pen)
    else:
        patch_for_get_default_animal_manure_excretions.assert_not_called()
        patch_for_calc_animal_manure_excretion.assert_not_called()
        patch_for_add_animal_manure_excretions.assert_not_called()
        patch_for_update_animal_manure_excretion_data.assert_not_called()


@pytest.mark.parametrize(
    "pen_to_test, ration, expected",
    [
        (lazy_fixture("pen"), {}, False),
        (lazy_fixture("pen"), {"something": 1, "something2": "value"}, False),
        (lazy_fixture("pen_with_animals"), {}, True),
        (lazy_fixture("pen_with_animals"), {"something": 1, "something2": "value"}, False),
    ],
)
def test_needs_ration_formulation(
    pen_to_test: Pen, ration: Dict[str, float | str], expected: bool
) -> None:
    """Unit test for needs_ration_formulation property in file pen.py."""
    pen_to_test.ration = ration
    assert pen_to_test.needs_ration_formulation == expected
