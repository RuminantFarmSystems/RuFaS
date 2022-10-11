from typing import Callable
from typing import Dict
from typing import List

import pytest
from pytest import approx
from pytest import fixture
from pytest_mock import MockerFixture

from RUFAS.routines import AnimalManagement
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure.constants.constants import ManureManagementConstants
from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum
from RUFAS.routines.manure.manure.manure import Manure
from RUFAS.routines.manure.manure_handlers.bedding_classes import BeddingConfig
from RUFAS.routines.manure.manure_handlers.bedding_classes import BeddingFactory
from RUFAS.routines.manure.manure_handlers.bedding_classes import BeddingType
from RUFAS.routines.manure.manure_handlers.bedding_classes import DefaultBeddingConfigFactory
from RUFAS.routines.manure.manure_handlers.bedding_classes import ManureSolidsBedding
from RUFAS.routines.manure.manure_handlers.bedding_classes import SandBedding
from RUFAS.routines.manure.manure_handlers.bedding_classes import SawdustBedding
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_handlers.milking_center import MilkingCenter
from RUFAS.routines.manure.manure_management import ManureManagement
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen


# Test fixtures

@fixture
def mock_calf(mocker: MockerFixture) -> Calf:
    """Returns a Calf mocker object"""

    return mocker.MagicMock(autospec=Calf)


@fixture
def mock_heiferI(mocker: MockerFixture) -> HeiferI:
    """Returns a HeiferI mocker object"""

    return mocker.MagicMock(autospec=HeiferI)


@fixture
def mock_heiferII(mocker: MockerFixture) -> HeiferII:
    """Returns a HeiferII mocker object"""

    return mocker.MagicMock(autospec=HeiferII)


@fixture
def mock_heiferIII(mocker: MockerFixture) -> HeiferIII:
    """Returns a HeiferIII mocker object"""

    return mocker.MagicMock(autospec=HeiferIII)


@fixture
def mock_cow(mocker: MockerFixture) -> Cow:
    """Returns a Cow mocker object"""

    return mocker.MagicMock(autospec=Cow)


@fixture
def manure_attributes() -> List[str]:
    """Returns a list of manure attributes"""

    return ['U', 'TAN_s', 'MN', 'Mkg', 'TSd',
            'VSd', 'VSnd', 'WIP_frac', 'WOP_frac', 'p_excrt_manure',
            'K_manure', 'CH4_manure']


@fixture
def generate_animal_manure(manure_attributes) -> Callable[[float], Dict[str, float]]:
    """Returns a function that generates a dictionary of animal manure attributes"""

    def generate(dummy_val=2.0):
        """Generates a dictionary of animal manure attributes with dummy values"""

        return {attr: dummy_val for attr in manure_attributes}

    return generate


@fixture
def mock_pen(mocker: MockerFixture,
             mock_calf: Calf,
             mock_heiferI: HeiferI,
             mock_heiferII: HeiferII,
             mock_heiferIII: HeiferIII,
             mock_cow: Cow,
             generate_animal_manure: Callable[[float], Dict[str, float]]) -> Pen:
    """Returns a Pen mocker object"""

    mock_pen: Pen = mocker.MagicMock(autospec=Pen)
    mock_pen.id = 1
    mock_pen.animals_in_pen = [mock_cow] * 5
    mock_pen.classes_in_pen = {'Cow'}
    mock_pen.animal_combination = Pen.AnimalCombination.LAC_COW
    mock_pen.housing_type = 'free stall'
    mock_pen.bedding_type = 'sand'
    mock_pen.manure_handling = 'manual scraping'
    mock_pen.manure_separator = 'sand lane'
    mock_pen.manure_storage = 'storage pit'
    mock_pen.manure = generate_animal_manure(0.0)
    return mock_pen


@fixture
def mock_animal_management(mocker: MockerFixture) -> AnimalManagement:
    """Returns a AnimalManagement fixture object"""

    return mocker.MagicMock(autospec=AnimalManagement)


# Test ManureManagementConstants class
# ====================================

def test_manure_management_constants_class() -> None:
    constants = ManureManagementConstants
    assert constants.LITERS_TO_CUBIC_METERS == approx(0.001)
    assert constants.KG_TO_CUBIC_METERS == approx(0.001)
    assert constants.CUBIC_METERS_TO_LITERS == approx(1000.0)
    assert constants.GRAMS_TO_KG == approx(0.001)

    assert constants.UREA_MOLAR_MASS == approx(60.06)
    assert constants.UREA_DENSITY == approx(1.32)
    assert constants.TAN_MOLAR_MASS == approx(17.0306)
    assert constants.METHANE_ENERGY_DENSITY == approx(55)
    assert constants.METHANE_DENSITY == approx(0.657)

    assert constants.WATER_DENSITY_KG_PER_LITER == approx(0.997)
    assert constants.WATER_DENSITY_KG_PER_M3 == approx(9.97e-4)
    assert constants.DAYS_PER_YEAR == 365


# Test DefaultEnum class
# ======================

class DummyDefaultEnumWithDefault(DefaultEnum):
    SUCCESS = 1
    FAILED = 2
    DEFAULT = SUCCESS


class DummyDefaultEnumNoDefault(DefaultEnum):
    SUCCESS = 1
    FAILED = 2


@pytest.mark.parametrize(
        "enum_type, expected_default",
        [(DummyDefaultEnumWithDefault, DummyDefaultEnumWithDefault.SUCCESS),
         (DummyDefaultEnumNoDefault, DummyDefaultEnumNoDefault.SUCCESS),
         ])
def test_get_default_type(enum_type: DefaultEnum, expected_default: DefaultEnum) -> None:
    """Unit test for function get_default_type in file default_enum.py"""

    assert enum_type.get_default_type() is expected_default


@pytest.mark.parametrize(
        "enum_type, lookup_member, expected_type",
        [(DummyDefaultEnumWithDefault, 'success', DummyDefaultEnumWithDefault.SUCCESS),
         (DummyDefaultEnumWithDefault, 'failed', DummyDefaultEnumWithDefault.FAILED),
         (DummyDefaultEnumWithDefault, 'dummy', DummyDefaultEnumWithDefault.DEFAULT),
         (DummyDefaultEnumNoDefault, 'success', DummyDefaultEnumNoDefault.SUCCESS),
         (DummyDefaultEnumNoDefault, 'failed', DummyDefaultEnumNoDefault.FAILED),
         (DummyDefaultEnumNoDefault, 'dummy', DummyDefaultEnumNoDefault.SUCCESS),
         ])
def test_get_type(enum_type: DefaultEnum, lookup_member: str, expected_type: DefaultEnum) -> None:
    """Unit test for function get_type in file default_enum.py"""

    assert enum_type.get_type(lookup_member) is expected_type


class DummyDefaultEnumWithNoMembers(DefaultEnum):
    pass


def test_get_type_no_members() -> None:
    """Unit test for function get_type() in file default_enum.py"""

    with pytest.raises(IndexError):
        DummyDefaultEnumWithNoMembers.get_type('dummy')


# Test Manure class
# =================

def test_manure_init(manure_attributes: List[str],
                     generate_animal_manure: Callable[[float], Dict[str, float]]) -> None:
    """Unit test for function __init__ in file manure.py"""

    # Given no arguments, a new Manure object should have all attributes
    # initially set to 0.
    manure = Manure()
    for attr in manure_attributes:
        assert hasattr(manure, attr)
        assert getattr(manure, attr) == approx(0.0)

    # Given a dictionary of arguments, a new Manure object should have all attributes
    # initially set to the correct values.
    manure_data = generate_animal_manure(0.0)
    manure = Manure(**manure_data)
    for attr in manure_attributes:
        assert hasattr(manure, attr)
        assert getattr(manure, attr) == approx(0.0)

    # Given one or more arguments, a new Manure object should either set
    # the corresponding attributes to the given values or do some calculations.
    manure = Manure(
            # The following attributes should be modified via unit conversion.
            U=2.0,
            TAN_s=3.0,
            MN=4.0,
            VSd=5.0,
            VSnd=6.0,
            p_excrt_manure=7.0,
            K_manure=8.0,

            # The following attributes should stay the same.
            # Only pick two as an example.
            Mkg=10.0,
            CH4_manure=10.0
    )
    constants = ManureManagementConstants
    assert manure.U == approx(2.0 * constants.UREA_MOLAR_MASS)
    assert manure.TAN_s == approx(3.0 * constants.TAN_MOLAR_MASS)
    assert manure.MN == approx(4.0 * constants.GRAMS_TO_KG)
    assert manure.VSd == approx(5.0 * constants.GRAMS_TO_KG)
    assert manure.VSnd == approx(6.0 * constants.GRAMS_TO_KG)
    assert manure.p_excrt_manure == approx(7.0 * constants.GRAMS_TO_KG)
    assert manure.K_manure == approx(8.0 * constants.GRAMS_TO_KG)

    assert manure.Mkg == approx(10.0)
    assert manure.CH4_manure == approx(10.0)

    # The remaining attributes should be set to the default value of 0.
    assert manure.TSd == approx(0.0)
    assert manure.WIP_frac == approx(0.0)
    assert manure.WOP_frac == approx(0.0)
    assert manure.p_frac == approx(0.0)


# Test ManureManagement class
# ===========================

def test_manure_management_init(mocker: MockerFixture, mock_animal_management: AnimalManagement) -> None:
    """Unit test for function __init__ in file manure_management.py"""

    # Arrange
    mock_set_up_components = mocker.patch('RUFAS.routines.manure.manure_management.ManureManagement'
                                          '._setup_manure_management_components', return_value=None)

    # Act
    manure_management = ManureManagement(mock_animal_management)

    # Assert
    assert manure_management.manure_handlers == {}
    assert manure_management.reception_pits == {}
    assert manure_management.manure_separators == {}
    assert manure_management.manure_treatments == {}
    assert manure_management.all_data == {}
    mock_set_up_components.assert_called_once_with(mock_animal_management)


def test_setup_manure_management_components(mocker: MockerFixture,
                                            mock_animal_management: AnimalManagement) -> None:
    """Unit test for function _setup_manure_management_components in file manure_management.py"""

    # Arrange
    num_pens = 3
    mock_pens = [mocker.MagicMock(autospec=Pen) for _ in range(num_pens)]
    for i in range(num_pens):
        mock_pens[i].id = i
    mock_animal_management.all_pens = mock_pens

    # Act
    manure_management = ManureManagement(mock_animal_management)

    # Assert
    assert len(manure_management.manure_handlers) == num_pens
    assert len(manure_management.reception_pits) == num_pens
    assert len(manure_management.manure_separators) == num_pens
    assert len(manure_management.manure_treatments) == num_pens


def test_manure_management_update(mocker: MockerFixture,
                                  mock_animal_management: AnimalManagement) -> None:
    """Unit test for function update in file manure_management.py"""

    # Arrange
    num_pens = 3
    mock_pens = [mocker.MagicMock(autospec=Pen) for _ in range(num_pens)]
    for i in range(num_pens):
        mock_pens[i].id = i
    mock_animal_management.all_pens = mock_pens

    # Act
    manure_management = ManureManagement(mock_animal_management)
    manure_management.update(mock_animal_management)

    # Assert
    assert len(manure_management.manure_handlers) == num_pens
    assert len(manure_management.reception_pits) == num_pens
    assert len(manure_management.manure_separators) == num_pens
    assert len(manure_management.manure_treatments) == num_pens
    assert len(manure_management.all_data) == num_pens


# Test ManureManagementPen class
# ==============================

def test_manure_management_pen_init(mock_pen: Pen,
                                    mock_calf: Calf,
                                    mock_heiferI: HeiferI,
                                    mock_heiferII: HeiferII,
                                    mock_heiferIII: HeiferIII,
                                    mock_cow: Cow,
                                    generate_animal_manure: Callable[[float], Dict[str, float]]) -> None:
    """Unit test for function __init__ in file manure_management_pen.py"""

    # Arrange
    mock_pen.manure['Mkg'] = 100.0
    dummy_manure_data = generate_animal_manure(0.0)
    dummy_manure_data['Mkg'] = 100.0

    # Act
    pen = ManureManagementPen(mock_pen)

    # Assert
    assert pen.id == 1
    assert pen.animals_in_pen == [mock_cow] * len(mock_pen.animals_in_pen)
    assert pen.classes_in_pen == {'Cow'}
    assert pen.animal_combination is Pen.AnimalCombination.LAC_COW
    assert pen.housing_type == 'free stall'
    assert pen.bedding_type == 'sand'
    assert pen.manure_handler == 'manual scraping'
    assert pen.manure_separator == 'sand lane'
    assert pen.manure_treatment == 'storage pit'
    assert pen.num_animals == len(mock_pen.animals_in_pen)
    assert pen.manure_density == 990.0  # kg/m3
    assert pen.manure == Manure(**dummy_manure_data)
    assert pen.manure_mass == approx(100.0)
    assert pen.manure_volume == approx(100.0 / 990.0)


@pytest.mark.parametrize(
        "has_cows, has_heiferIIs, expected_area",
        [(True, False, 3.5),
         (False, True, 2.5),
         (True, True, 3.5),
         (False, False, 2.0),
         ])
def test_housing_area_for_NH3_emission(has_cows,
                                       has_heiferIIs,
                                       expected_area,
                                       mock_pen: Pen,
                                       mock_calf: Calf,
                                       mock_heiferII: HeiferII,
                                       mock_cow: Cow) -> None:
    """Unit test for property housing_area_for_NH3_emission in file manure_management_pen.py"""

    # Arrange
    animals_in_pen = []
    classes_in_pen = set()

    if has_cows:
        animals_in_pen.append(mock_cow)
        classes_in_pen.add('Cow')
    if has_heiferIIs:
        animals_in_pen.append(mock_heiferII)
        classes_in_pen.add('HeiferII')
    if not has_cows and not has_heiferIIs:
        animals_in_pen.append(mock_calf)
        classes_in_pen.add('Calf')

    mock_pen.animals_in_pen = animals_in_pen
    mock_pen.classes_in_pen = classes_in_pen

    # Act
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.housing_area_for_NH3_emission == approx(expected_area)


@pytest.mark.parametrize(
        "housing_type, has_cows, expected_area",
        [('tie stall', True, 1.2),
         ('tie stall', False, 1.0),
         ('bedded pack', True, 5.0),
         ('bedded pack', False, 3.0),
         ('free stall', True, 3.5),
         ('free stall', False, 2.5),
         ])
def test_barn_area(housing_type,
                   has_cows,
                   expected_area,
                   mock_pen: Pen,
                   mock_cow: Cow,
                   mock_calf: Calf) -> None:
    """Unit test for property barn_area in file manure_management_pen.py"""

    # Arrange
    mock_pen.housing_type = housing_type
    mock_pen.animals_in_pen = [mock_cow] if has_cows else [mock_calf]
    mock_pen.classes_in_pen = {'Cow'} if has_cows else {'Calf'}

    # Act
    mm_pen = ManureManagementPen(mock_pen)

    # Assert
    assert mm_pen.barn_area == approx(expected_area)


# Test bedding classes
# ====================

@pytest.mark.parametrize(
        "bedding_type_name, expected_bedding_type",
        [('sawdust', BeddingType.SAWDUST),
         ('manure solids', BeddingType.MANURE_SOLIDS),
         ('sand', BeddingType.SAND),
         ('dummy', BeddingType.DEFAULT),
         ('dummy', BeddingType.SAND),
         ('default', BeddingType.SAND),
         ])
def test_bedding_type(bedding_type_name, expected_bedding_type) -> None:
    """Unit test for class BeddingType in file bedding_classes.py"""

    # Act
    bedding_type = BeddingType.get_type(bedding_type_name)

    # Assert
    assert bedding_type == expected_bedding_type


# Test BeddingConfig class
# ========================

def test_bedding_config_init() -> None:
    """Unit test for BeddingConfig dataclass in file bedding_classes.py"""

    # Act
    bedding_config = BeddingConfig(
            bedding_mass_per_day=1.0,
            bedding_density=2.0,
            bedding_dry_matter=3.0,
            bedding_washed_percent=4.0,
            bedding_type=BeddingType.DEFAULT,
            sand_removal_efficiency=5.0,
    )

    # Assert
    assert bedding_config.bedding_mass_per_day == 1.0
    assert bedding_config.bedding_density == 2.0
    assert bedding_config.bedding_dry_matter == 3.0
    assert bedding_config.bedding_washed_percent == 4.0
    assert bedding_config.bedding_type == BeddingType.DEFAULT
    assert bedding_config.sand_removal_efficiency == 5.0


# Test DefaultBeddingConfigFactory class
# ======================================

@pytest.mark.parametrize(
        "bedding_config, expected_bedding_mass_per_day, expected_bedding_density, "
        "expected_bedding_dry_matter, expected_bedding_washed_percent, "
        "expected_bedding_type, expected_sand_removal_efficiency",
        [(DefaultBeddingConfigFactory.SAWDUST_BEDDING_CONFIG, 1.97, 250.0, 0.9, 1.0, BeddingType.SAWDUST, 0.0),
         (DefaultBeddingConfigFactory.MANURE_SOLIDS_BEDDING_CONFIG, 1.97, 250.0, 0.9, 1.0, BeddingType.MANURE_SOLIDS,
          0.0),
         (DefaultBeddingConfigFactory.SAND_BEDDING_CONFIG, 25.0, 1500.0, 0.9, 25.0, BeddingType.SAND, 0.5),
         ])
def test_default_bedding_config_values(bedding_config,
                                       expected_bedding_mass_per_day,
                                       expected_bedding_density,
                                       expected_bedding_dry_matter,
                                       expected_bedding_washed_percent,
                                       expected_bedding_type,
                                       expected_sand_removal_efficiency) -> None:
    """Unit test for  default bedding config values in file bedding_classes.py"""

    # Assert
    assert bedding_config.bedding_mass_per_day == approx(expected_bedding_mass_per_day)
    assert bedding_config.bedding_density == approx(expected_bedding_density)
    assert bedding_config.bedding_dry_matter == approx(expected_bedding_dry_matter)
    assert bedding_config.bedding_washed_percent == approx(expected_bedding_washed_percent)
    assert bedding_config.bedding_type is expected_bedding_type
    assert bedding_config.sand_removal_efficiency == approx(expected_sand_removal_efficiency)


@pytest.mark.parametrize(
        "bedding_type, expected_default_bedding_config",
        [(BeddingType.SAWDUST, DefaultBeddingConfigFactory.SAWDUST_BEDDING_CONFIG),
         (BeddingType.MANURE_SOLIDS, DefaultBeddingConfigFactory.MANURE_SOLIDS_BEDDING_CONFIG),
         (BeddingType.SAND, DefaultBeddingConfigFactory.SAND_BEDDING_CONFIG)
         ])
def test_default_bedding_config_factory_get_instance(bedding_type, expected_default_bedding_config) -> None:
    """Unit test for class DefaultBeddingConfigFactory in file bedding_classes.py"""

    # Act
    default_bedding_config = DefaultBeddingConfigFactory.get_instance(bedding_type)

    # Assert
    assert default_bedding_config == expected_default_bedding_config


# Test BeddingFactory class
# =========================

@pytest.fixture
def dummy_bedding_config() -> BeddingConfig:
    """Fixture for BeddingConfig dataclass in file bedding_classes.py"""

    return BeddingConfig(
            bedding_mass_per_day=1.0,
            bedding_density=2.0,
            bedding_dry_matter=3.0,
            bedding_washed_percent=4.0,
            bedding_type=BeddingType.DEFAULT,
            sand_removal_efficiency=5.0,
    )


@pytest.mark.parametrize(
        "bedding_type_name, expected_bedding",
        [('sawdust', SawdustBedding),
         ('manure solids', ManureSolidsBedding),
         ('sand', SandBedding),
         ])
def test_bedding_factory_get_instance(bedding_type_name,
                                      expected_bedding,
                                      dummy_bedding_config) -> None:
    """Unit test for class BeddingFactory in file bedding_classes.py"""

    # Use default bedding configs
    # Act
    bedding = BeddingFactory.get_instance(bedding_type_name)

    # Assert
    assert isinstance(bedding, expected_bedding)
    assert bedding.bedding_type == BeddingType.get_type(bedding_type_name)

    default_bedding_config = DefaultBeddingConfigFactory.get_instance(bedding.bedding_type)
    assert bedding.bedding_mass_per_day == default_bedding_config.bedding_mass_per_day
    assert bedding.bedding_density == default_bedding_config.bedding_density
    assert bedding.bedding_dry_matter == default_bedding_config.bedding_dry_matter
    assert bedding.bedding_washed_percent == default_bedding_config.bedding_washed_percent
    assert bedding.bedding_type is default_bedding_config.bedding_type

    if isinstance(bedding, SandBedding):
        assert bedding.sand_removal_efficiency == default_bedding_config.sand_removal_efficiency

    # Use custom bedding configs
    # Act
    bedding = BeddingFactory.get_instance(bedding_type_name, dummy_bedding_config)

    # Assert
    assert isinstance(bedding, expected_bedding)
    assert bedding.bedding_mass_per_day == dummy_bedding_config.bedding_mass_per_day
    assert bedding.bedding_density == dummy_bedding_config.bedding_density
    assert bedding.bedding_dry_matter == dummy_bedding_config.bedding_dry_matter
    assert bedding.bedding_washed_percent == dummy_bedding_config.bedding_washed_percent
    assert bedding.bedding_type is dummy_bedding_config.bedding_type

    if isinstance(bedding, SandBedding):
        assert bedding.sand_removal_efficiency == dummy_bedding_config.sand_removal_efficiency


@pytest.mark.parametrize(
        "bedding_type_name, bedding_config",
        [('sawdust', DefaultBeddingConfigFactory.SAWDUST_BEDDING_CONFIG),
         ('manure solids', DefaultBeddingConfigFactory.MANURE_SOLIDS_BEDDING_CONFIG),
         ('sand', DefaultBeddingConfigFactory.SAND_BEDDING_CONFIG),
         ])
def test_total_bedding_mass_and_volume(bedding_type_name, bedding_config, mock_pen: Pen) -> None:
    """Unit test for total_bedding_mass and total_bedding_volume in file bedding_classes.py"""

    # Arrange
    pen = ManureManagementPen(mock_pen)
    num_animals = pen.num_animals
    bedding_mass_per_day = bedding_config.bedding_mass_per_day
    sand_removal_efficiency = bedding_config.sand_removal_efficiency
    expected_total_bedding_mass = num_animals * bedding_mass_per_day * \
                                  (1 - sand_removal_efficiency)

    bedding_density = bedding_config.bedding_density
    expected_total_bedding_volume = expected_total_bedding_mass / bedding_density

    bedding_washed_percent = bedding_config.bedding_washed_percent
    expected_total_bedding_washed = expected_total_bedding_mass * bedding_washed_percent

    # Act
    bedding = BeddingFactory.get_instance(bedding_type_name)
    total_bedding_mass = bedding.total_bedding_mass(pen)
    total_bedding_volume = bedding.total_bedding_volume(pen)
    total_bedding_washed = bedding.total_bedding_washed(pen)

    # Assert
    assert total_bedding_mass == approx(expected_total_bedding_mass)
    assert total_bedding_volume == approx(expected_total_bedding_volume)
    assert total_bedding_washed == approx(expected_total_bedding_washed)


# Test MilkingCenter class
# ========================

@pytest.fixture
def mock_milking_center() -> MilkingCenter:
    """Fixture for MilkingCenter class in file milking_center.py"""

    return MilkingCenter(
            num_milkings=3,
            minutes_spent_in_holding_area=30.0,
            minutes_spent_per_milking=10.0,
            wash_water_use_rate=20.0,
            fresh_water_use_rate=10.0
    )


def test_milking_center_init(mock_milking_center: MilkingCenter) -> None:
    """Unit test for __init__() of class MilkingCenter in file milking_center.py"""

    # Assert
    assert mock_milking_center.num_milkings == 3
    assert mock_milking_center.minutes_spent_in_holding_area == 30.0
    assert mock_milking_center.minutes_spent_per_milking == 10.0
    assert mock_milking_center.wash_water_use_rate == 20.0
    assert mock_milking_center.fresh_water_use_rate == 10.0


def test_milking_center_total_minutes_spent_in_holding_area(mock_milking_center: MilkingCenter) -> None:
    """Unit test for total_minutes_spent_in_holding_area() of class MilkingCenter in file milking_center.py"""

    # Arrange
    expected_total_minutes_spent_in_holding_area = mock_milking_center.num_milkings * \
                                                   mock_milking_center.minutes_spent_in_holding_area

    # Act
    total_minutes_spent_in_holding_area = mock_milking_center.total_minutes_spent_in_holding_area

    # Assert
    assert total_minutes_spent_in_holding_area == approx(expected_total_minutes_spent_in_holding_area)


def test_milking_center_total_minutes_spent_milking(mock_milking_center: MilkingCenter) -> None:
    """Unit test for total_minutes_spent_milking() of class MilkingCenter in file milking_center.py"""

    # Arrange
    expected_total_minutes_spent_milking = mock_milking_center.num_milkings * \
                                           mock_milking_center.minutes_spent_per_milking

    # Act
    total_minutes_spent_milking = mock_milking_center.total_minutes_spent_milking

    # Assert
    assert total_minutes_spent_milking == approx(expected_total_minutes_spent_milking)


def test_has_lac_cow_in_pen(mock_pen: Pen, mock_calf: Calf, mock_cow: Cow) -> None:
    """Unit test for _has_lac_cow_in_pen() of class MilkingCenter in file milking_center.py"""

    # Case 1: There are lactating cows in pen.
    # Arrange
    pen = ManureManagementPen(mock_pen)
    pen.animals_in_pen = [mock_cow] * 5
    pen.classes_in_pen = {'Cow'}
    pen.animal_combination = Pen.AnimalCombination.LAC_COW

    # Act
    has_lac_cow_in_pen = MilkingCenter._has_lac_cow_in_pen(pen)

    # Assert
    assert has_lac_cow_in_pen

    # Case 2: There are no lactating cows in pen.
    # Arrange
    pen = ManureManagementPen(mock_pen)
    pen.animals_in_pen = [mock_calf] * 5
    pen.classes_in_pen = {'Calf'}
    pen.animal_combination = Pen.AnimalCombination.CALF

    # Act
    has_lac_cow_in_pen = MilkingCenter._has_lac_cow_in_pen(pen)

    # Assert
    assert not has_lac_cow_in_pen


def test_milking_center_wash_water_volume_used_in_holding_area(mock_milking_center: MilkingCenter,
                                                               mock_pen: Pen) -> None:
    """Unit test for wash_water_volume_used_in_holding_area() of class MilkingCenter in file
    milking_center.py"""

    # Case 1: There are lactating cows in the pen.
    # Arrange
    pen = ManureManagementPen(mock_pen)
    expected_wash_water_volume_used_in_holding_area = pen.num_animals * \
                                                      mock_milking_center.wash_water_use_rate

    # Act
    wash_water_volume_used_in_holding_area = mock_milking_center.wash_water_volume_used_in_holding_area(pen)

    # Assert
    assert pen.animal_combination is Pen.AnimalCombination.LAC_COW
    assert wash_water_volume_used_in_holding_area == approx(expected_wash_water_volume_used_in_holding_area)

    # Case 2: There are no cows in the pen.
    # Arrange
    mock_pen.animals_in_pen = [mock_calf] * 5
    mock_pen.classes_in_pen = {'Calf'}
    mock_pen.animal_combination = Pen.AnimalCombination.CALF
    pen = ManureManagementPen(mock_pen)
    expected_wash_water_volume_used_in_holding_area = 0.0

    # Act
    wash_water_volume_used_in_holding_area = mock_milking_center.wash_water_volume_used_in_holding_area(pen)

    # Assert
    assert pen.animal_combination is Pen.AnimalCombination.CALF
    assert wash_water_volume_used_in_holding_area == approx(expected_wash_water_volume_used_in_holding_area)


def test_milking_center_fresh_water_volume_used_for_milking(mock_milking_center: MilkingCenter,
                                                            mock_pen: Pen,
                                                            mock_calf: Calf) -> None:
    """Unit test for fresh_water_volume_used_for_milking() of class MilkingCenter in file milking_center.py"""

    # Case 1: There are lactating cows in the pen
    # Arrange
    pen = ManureManagementPen(mock_pen)
    expected_fresh_water_volume_used_for_milking = pen.num_animals * \
                                                   mock_milking_center.fresh_water_use_rate

    # Act
    fresh_water_volume_used_for_milking = mock_milking_center.fresh_water_volume_used_for_milking(pen)

    # Assert
    assert pen.animal_combination is Pen.AnimalCombination.LAC_COW
    assert fresh_water_volume_used_for_milking == approx(expected_fresh_water_volume_used_for_milking)

    # Case 2: There are no lactating cows in the pen
    # Arrange
    mock_pen.animals_in_pen = [mock_calf] * 5
    mock_pen.classes_in_pen = {'Calf'}
    mock_pen.animal_combination = Pen.AnimalCombination.CALF
    pen = ManureManagementPen(mock_pen)
    expected_fresh_water_volume_used_for_milking = 0.0

    # Act
    fresh_water_volume_used_for_milking = mock_milking_center.fresh_water_volume_used_for_milking(pen)

    # Assert
    assert pen.animal_combination is Pen.AnimalCombination.CALF
    assert fresh_water_volume_used_for_milking == approx(expected_fresh_water_volume_used_for_milking)


def test_total_minutes_spent_in_milking_center(mock_milking_center: MilkingCenter,
                                               mock_pen: Pen) -> None:
    """Unit test for total_minutes_spent_in_milking_center() of class MilkingCenter in file
    milking_center.py"""

    # Arrange
    total_minutes_spent_in_holding_area = mock_milking_center.total_minutes_spent_in_holding_area
    total_minutes_spent_milking = mock_milking_center.total_minutes_spent_milking
    expected_total_minutes_spent_in_milking_center = \
        total_minutes_spent_in_holding_area + total_minutes_spent_milking

    # Act
    total_minutes_spent_in_milking_center = mock_milking_center.total_minutes_spent_in_milking_center

    # Assert
    assert total_minutes_spent_in_milking_center == approx(expected_total_minutes_spent_in_milking_center)


def test_total_water_volume_used_in_milking_center(mock_milking_center: MilkingCenter,
                                                   mock_pen: Pen) -> None:
    """Unit test for total_water_volume_used_in_milking_center() of class MilkingCenter in file
    milking_center.py"""

    # Case 1: There are lactating cows in the pen.
    # Arrange
    pen = ManureManagementPen(mock_pen)
    wash_water_volume_used_in_holding_area = \
        mock_milking_center.wash_water_volume_used_in_holding_area(pen)
    fresh_water_volume_used_for_milking = \
        mock_milking_center.fresh_water_volume_used_for_milking(pen)
    expected_total_water_volume_used_in_milking_center = \
        wash_water_volume_used_in_holding_area + fresh_water_volume_used_for_milking

    # Act
    total_water_volume_used_in_milking_center = mock_milking_center.total_water_volume_used_in_milking_center(pen)

    # Assert
    assert total_water_volume_used_in_milking_center == approx(expected_total_water_volume_used_in_milking_center)

    # Case 2: There are no lactating cows in the pen.
    # Arrange
    mock_pen.animals_in_pen = [mock_calf] * 5
    mock_pen.classes_in_pen = {'Calf'}
    mock_pen.animal_combination = Pen.AnimalCombination.CALF
    pen = ManureManagementPen(mock_pen)

    # Act
    total_water_volume_used_in_milking_center = mock_milking_center.total_water_volume_used_in_milking_center(pen)

    # Assert
    assert pen.animal_combination is Pen.AnimalCombination.CALF
    assert total_water_volume_used_in_milking_center == approx(0.0)


@pytest.mark.parametrize(
        'minutes, expected_percent_of_day',
        [(0, 0.0),
         (1440.0, 100.0),
         (720.0, 50.0),
         (360.0, 25.0),
         ])
def test_calc_percent_of_day_from_minutes(minutes, expected_percent_of_day) -> None:
    """Unit test for calc_percent_of_day_from_minutes() of class MilkingCenter in file milking_center.py"""

    assert MilkingCenter._calc_percent_of_day_from_minutes(minutes) == approx(expected_percent_of_day)


def test_percent_of_day_spent_in_holding_area(mock_milking_center: MilkingCenter) -> None:
    """Unit test for percent_of_day_spent_in_holding_area() of class MilkingCenter in file milking_center.py"""

    # Arrange
    total_minutes_spent_in_holding_area = mock_milking_center.total_minutes_spent_in_holding_area
    expected_percent_of_day_spent_in_holding_area = \
        MilkingCenter._calc_percent_of_day_from_minutes(total_minutes_spent_in_holding_area)

    # Act
    percent_of_day_spent_in_holding_area = mock_milking_center.percent_of_day_spent_in_holding_area

    # Assert
    assert percent_of_day_spent_in_holding_area == approx(expected_percent_of_day_spent_in_holding_area)


def test_percent_of_day_spent_milking(mock_milking_center: MilkingCenter) -> None:
    """Unit test for percent_of_day_spent_milking() of class MilkingCenter in file milking_center.py"""

    # Arrange
    total_minutes_spent_milking = mock_milking_center.total_minutes_spent_milking
    expected_percent_of_day_spent_milking = \
        MilkingCenter._calc_percent_of_day_from_minutes(total_minutes_spent_milking)

    # Act
    percent_of_day_spent_milking = mock_milking_center.percent_of_day_spent_milking

    # Assert
    assert percent_of_day_spent_milking == approx(expected_percent_of_day_spent_milking)


def test_total_percent_of_day_spent_in_milking_center(mock_milking_center: MilkingCenter) -> None:
    """Unit test for total_percent_of_day_spent_in_milking_center() of class MilkingCenter in file
    milking_center.py"""

    # Arrange
    percent_of_day_spent_in_holding_area = mock_milking_center.percent_of_day_spent_in_holding_area
    percent_of_day_spent_milking = mock_milking_center.percent_of_day_spent_milking
    expected_total_percent_of_day_spent_in_milking_center = \
        percent_of_day_spent_in_holding_area + percent_of_day_spent_milking

    # Act
    total_percent_of_day_spent_in_milking_center = mock_milking_center.total_percent_of_day_spent_in_milking_center

    # Assert
    assert total_percent_of_day_spent_in_milking_center == approx(expected_total_percent_of_day_spent_in_milking_center)


def test_manure_mass_deposited_in_milking_center(mock_milking_center: MilkingCenter,
                                                 mock_pen: Pen) -> None:
    """Unit test for manure_mass_deposited_in_milking_center() in file milking_center.py"""

    # Case 1: There are cows in the pen.
    # Arrange
    pen = ManureManagementPen(mock_pen)
    pen.manure.Mkg = 100.0
    expected_manure_mass_deposited_in_milking_center = \
        pen.manure.Mkg * mock_milking_center.total_percent_of_day_spent_in_milking_center / 100.0

    # Act
    manure_mass_deposited_in_milking_center = mock_milking_center.manure_mass_deposited_in_milking_center(pen)

    # Assert
    assert manure_mass_deposited_in_milking_center == approx(expected_manure_mass_deposited_in_milking_center)

    # Case 2: There are no cows in the pen.
    # Arrange
    pen = ManureManagementPen(mock_pen)
    pen.animals_in_pen = [mock_calf] * 5
    pen.classes_in_pen = {'Calf'}
    expected_manure_mass_deposited_in_milking_center = 0.0

    # Act
    manure_mass_deposited_in_milking_center = mock_milking_center.manure_mass_deposited_in_milking_center(pen)

    # Assert
    assert manure_mass_deposited_in_milking_center == approx(expected_manure_mass_deposited_in_milking_center)


def test_manure_volume_deposited_in_milking_center(mock_milking_center: MilkingCenter,
                                                   mock_pen: Pen) -> None:
    """Unit test for manure_volume_deposited_in_milking_center() in file milking_center.py"""

    # Case 1: There are cows in the pen.
    # Arrange
    pen = ManureManagementPen(mock_pen)
    expected_manure_volume_deposited_in_milking_center = \
        mock_milking_center.manure_mass_deposited_in_milking_center(pen) / pen.manure_density

    # Act
    manure_volume_deposited_in_milking_center = mock_milking_center.manure_volume_deposited_in_milking_center(pen)

    # Assert
    assert manure_volume_deposited_in_milking_center == approx(expected_manure_volume_deposited_in_milking_center)

    # Case 2: There are no cows in the pen.
    # Arrange
    pen = ManureManagementPen(mock_pen)
    pen.animals_in_pen = [mock_calf] * 5
    pen.classes_in_pen = {'Calf'}
    expected_manure_volume_deposited_in_milking_center = 0.0

    # Act
    manure_volume_deposited_in_milking_center = mock_milking_center.manure_volume_deposited_in_milking_center(pen)

    # Assert
    assert manure_volume_deposited_in_milking_center == approx(expected_manure_volume_deposited_in_milking_center)


# Test ManureHandlerOutput

def test_manure_handler_output_init() -> None:
    """Unit test for __init__() of class ManureHandlerDailyOutput in file manure_handler_daily_output.py"""

    # Act
    manure_handler_output = ManureHandlerDailyOutput(
            simulation_day=1,
            pen_id=1,
            urea=1.0,
            TAN_s=2.0,
            manure_nitrogen=3.0,
            TSd=4.0,
            VSd=5.0,
            VSnd=6.0,
            WIP_frac=0.70,
            WOP_frac=0.80,
            p_excrt_manure=9.0,
            K_manure=10.0,
            CH4_floor=11.0,
            CO2_floor=12.0,
            NH3_floor=13.0,
            raw_manure=14.0,
            cleaning_water=15.0,
            total_bedding_mass=16.0,
            total_water_volume_in_milking_center=17.0
    )

    # Assert
    assert manure_handler_output.simulation_day == 1
    assert manure_handler_output.pen_id == 1
    assert manure_handler_output.urea == approx(1.0)
    assert manure_handler_output.TAN_s == approx(2.0)
    assert manure_handler_output.manure_nitrogen == approx(3.0)
    assert manure_handler_output.TSd == approx(4.0)
    assert manure_handler_output.VSd == approx(5.0)
    assert manure_handler_output.VSnd == approx(6.0)
    assert manure_handler_output.VS_total == approx(5.0 + 6.0)
    assert manure_handler_output.WIP_frac == approx(0.70)
    assert manure_handler_output.WOP_frac == approx(0.80)
    assert manure_handler_output.p_excrt_manure == approx(9.0)
    assert manure_handler_output.K_manure == approx(10.0)
    assert manure_handler_output.CH4_floor == approx(11.0)
    assert manure_handler_output.CO2_floor == approx(12.0)
    assert manure_handler_output.NH3_floor == approx(13.0)
    assert manure_handler_output.raw_manure == approx(14.0)
    assert manure_handler_output.cleaning_water == approx(15.0)
    assert manure_handler_output.total_bedding_mass == approx(16.0)
    assert manure_handler_output.total_water_volume_in_milking_center == approx(17.0)
    assert manure_handler_output.total_daily_mass == approx(14.0 + 15.0 + 16.0 + 17.0)

