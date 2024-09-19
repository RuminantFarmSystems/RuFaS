import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_growth.animal_growth import AnimalGrowth
from RUFAS.biophysical.animal.animal_properties.animal_growth_properties import AnimalGrowthProperties
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.reproduction_properties import ReproductionProperties
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.input_manager import InputManager
from RUFAS.time import Time


@pytest.fixture
def mock_general_properties(mocker: MockerFixture) -> GeneralProperties:
    return mocker.MagicMock(auto_spec=GeneralProperties)


@pytest.fixture
def mock_animal_growth_properties(mocker: MockerFixture) -> AnimalGrowthProperties:
    return mocker.MagicMock(auto_spec=AnimalGrowthProperties)


@pytest.fixture
def mock_reproduction_properties(mocker: MockerFixture) -> ReproductionProperties:
    return mocker.MagicMock(auto_spec=ReproductionProperties)


@pytest.mark.parametrize(
    "wean_day, target_heifer_preg_day",
    [
        (10, 100),
        (60, 399)
    ]
)
def test_initialize_class_variables(wean_day: int, target_heifer_preg_day: int, mocker: MockerFixture) -> None:
    im = InputManager()
    mock_get_data = mocker.patch.object(im, "get_data",
                                        return_value={
                                            "calf": {"wean_day": wean_day},
                                            "bodyweight": {"target_heifer_preg_day": target_heifer_preg_day}
                                        })

    AnimalGrowth.initialize_class_variables()

    assert AnimalGrowth.wean_day == wean_day
    assert AnimalGrowth.target_heifer_pregnant_day == target_heifer_preg_day
    mock_get_data.assert_called_once_with("animal.animal_config.farm_level")

# body_weight: float, target_adg_calf: float, days_born: int, mature_body_weight:float,
#                         days_in_preg: int, gestation_length: int, conceptus_weight: float, calf_birth_weight: float,
#                         calves: int, days_in_milk: int, calving_interval: float


@pytest.mark.parametrize(
    "animal_type, body_weight, mature_body_weight, is_pregnant", [
        (AnimalType.CALF, 10, 100, False),
        (AnimalType.HEIFER_I, 10, 100, False),
        (AnimalType.HEIFER_II, 10, 100, False),
        (AnimalType.HEIFER_II, 100, 100, False),
        (AnimalType.HEIFER_II, 110, 100, False),
        (AnimalType.HEIFER_II, 10, 100, True),
        (AnimalType.HEIFER_II, 100, 100, True),
        (AnimalType.HEIFER_II, 110, 100, True),
        (AnimalType.HEIFER_III, 10, 100, True),
        (AnimalType.HEIFER_III, 100, 100, True),
        (AnimalType.HEIFER_III, 110, 100, True),
        (AnimalType.DRY_COW, 10, 100, False),
        (AnimalType.LAC_COW, 10, 100, False),
    ]
)
def test_daily_routines(animal_type: AnimalType, body_weight: float, mature_body_weight: float, is_pregnant: bool,
                        mock_general_properties: GeneralProperties,
                        mock_animal_growth_properties: AnimalGrowthProperties,
                        mock_reproduction_properties: ReproductionProperties, mocker: MockerFixture) -> None:
    mock_time = mocker.MagicMock(auto_spec=Time)
    mock_time.simulation_day = 18

    mock_general_properties.animal_type = animal_type
    mock_general_properties.body_weight = body_weight
    mock_general_properties.mature_body_weight = mature_body_weight
    mock_general_properties.is_pregnant = is_pregnant

    mock_reproduction_properties.conceptus_weight = 68
    mock_animal_growth_properties.tissue_changed = 88

    dummy_daily_growth = 5
    dummy_conceptus_weight = 233
    dummy_tissue_changed = 18
    mock_calf_bw_change = mocker.patch.object(AnimalGrowth, "calculate_calf_body_weight_change",
                                              return_value=dummy_daily_growth)
    mock_non_preg_heifer_bw_change = mocker.patch.object(AnimalGrowth,
                                                         "calculate_non_pregnant_heifer_body_weight_change",
                                                         return_value=dummy_daily_growth)
    mock_preg_heifer_bw_change = mocker.patch.object(AnimalGrowth, "calculate_pregnant_heifer_body_weight_change",
                                                     return_value=(dummy_daily_growth, dummy_conceptus_weight))
    mock_cow_bw_change = mocker.patch.object(
        AnimalGrowth,
        "calculate_cow_body_weight_change",
        return_value=(dummy_daily_growth, dummy_conceptus_weight, dummy_tissue_changed))

    (
        result_animal_growth_properties, result_reproduction_properties, result_general_properties
    ) = AnimalGrowth.daily_routines(
        mock_general_properties, mock_animal_growth_properties, mock_reproduction_properties, mock_time
    )

    assert result_animal_growth_properties == mock_animal_growth_properties
    assert result_reproduction_properties == mock_reproduction_properties
    assert result_general_properties == mock_general_properties

    if animal_type == AnimalType.CALF:
        mock_calf_bw_change.assert_called_once_with(mock_general_properties)
        mock_non_preg_heifer_bw_change.assert_not_called()
        mock_preg_heifer_bw_change.assert_not_called()
        mock_cow_bw_change.assert_not_called()

        assert result_animal_growth_properties.daily_growth == dummy_daily_growth
        assert result_general_properties.body_weight == body_weight + dummy_daily_growth

    elif animal_type == AnimalType.HEIFER_I or (animal_type == AnimalType.HEIFER_II and not is_pregnant):
        mock_non_preg_heifer_bw_change.assert_called_once_with(mock_general_properties)
        mock_calf_bw_change.assert_not_called()
        mock_preg_heifer_bw_change.assert_not_called()
        mock_cow_bw_change.assert_not_called()

        assert result_animal_growth_properties.daily_growth == dummy_daily_growth
        assert result_general_properties.body_weight == body_weight + dummy_daily_growth

    elif animal_type == AnimalType.HEIFER_III or (animal_type == AnimalType.HEIFER_II and is_pregnant):
        if body_weight < mature_body_weight:
            mock_preg_heifer_bw_change.assert_called_once_with(mock_reproduction_properties, mock_general_properties)
            mock_calf_bw_change.assert_not_called()
            mock_non_preg_heifer_bw_change.assert_not_called()
            mock_cow_bw_change.assert_not_called()

            assert result_animal_growth_properties.daily_growth == dummy_daily_growth
            assert result_general_properties.body_weight == body_weight + dummy_daily_growth
            assert result_reproduction_properties.conceptus_weight == dummy_conceptus_weight
        else:
            mock_calf_bw_change.assert_not_called()
            mock_non_preg_heifer_bw_change.assert_not_called()
            mock_preg_heifer_bw_change.assert_not_called()
            mock_cow_bw_change.assert_not_called()

            assert result_general_properties.body_weight == mature_body_weight

    else:
        mock_cow_bw_change.assert_called_once_with(mock_animal_growth_properties, mock_reproduction_properties,
                                                   mock_general_properties)
        mock_calf_bw_change.assert_not_called()
        mock_non_preg_heifer_bw_change.assert_not_called()
        mock_preg_heifer_bw_change.assert_not_called()

        assert result_animal_growth_properties.daily_growth == dummy_daily_growth
        assert result_general_properties.body_weight == body_weight + dummy_daily_growth
        assert result_reproduction_properties.conceptus_weight == dummy_conceptus_weight
        assert result_animal_growth_properties.tissue_changed == dummy_tissue_changed


@pytest.mark.parametrize(
    "birth_weight, wean_day", [
        (100, 25),
        (60, 60)
    ]
)
def test_calculate_calf_body_weight_change(birth_weight: float, wean_day: int,
                                           mock_general_properties: GeneralProperties) -> None:
    AnimalGrowth.wean_day = wean_day
    mock_general_properties.birth_weight = birth_weight

    result = AnimalGrowth.calculate_calf_body_weight_change(mock_general_properties)

    assert result == birth_weight / wean_day


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, target_heifer_pregnant_day, days_born, expected", [
        (15, 100, 60, 60, 38.4),
        (15, 100, 60, 50, 3.84),
        (15, 100, 60, 75, 2.56),
        (15, 100, 60, 61, 38.4),
    ]
)
def test_calculate_non_pregnant_heifer_body_weight_change(
        body_weight: float, mature_body_weight: float, target_heifer_pregnant_day: int, days_born: int, expected: float,
        mock_general_properties: GeneralProperties) -> None:
    AnimalGrowth.target_heifer_pregnant_day = target_heifer_pregnant_day

    mock_general_properties.days_born = days_born
    mock_general_properties.body_weight = body_weight
    mock_general_properties.mature_body_weight = mature_body_weight

    result = AnimalGrowth.calculate_non_pregnant_heifer_body_weight_change(mock_general_properties)

    assert pytest.approx(result) == expected


@pytest.mark.parametrize(
    "daily_growth, conceptus_growth", [
        (10, 5),
        (6, 8)
    ]
)
def test_calculate_pregnant_heifer_body_weight_change(
        daily_growth: float, conceptus_growth: float, mock_reproduction_properties: ReproductionProperties,
        mock_general_properties: GeneralProperties, mocker: MockerFixture
) -> None:
    dummy_conceptus_weight = 1.88

    mock_calculate_pregnant_heifer_target_daily_growth = mocker.patch.object(
        AnimalGrowth, "_calculate_pregnant_heifer_target_daily_growth", return_value=daily_growth)
    mock_calculate_pregnant_heifer_conceptus_growth = mocker.patch.object(
        AnimalGrowth, "_calculate_pregnant_heifer_conceptus_growth",
        return_value=(conceptus_growth, dummy_conceptus_weight))

    (
        result_bw_change, result_conceptus_weight
    ) = AnimalGrowth.calculate_pregnant_heifer_body_weight_change(mock_reproduction_properties, mock_general_properties)

    assert result_bw_change == daily_growth + conceptus_growth
    assert result_conceptus_weight == dummy_conceptus_weight

    mock_calculate_pregnant_heifer_target_daily_growth.assert_called_once_with(mock_reproduction_properties,
                                                                               mock_general_properties)
    mock_calculate_pregnant_heifer_conceptus_growth.assert_called_once_with(mock_reproduction_properties,
                                                                            mock_general_properties)


@pytest.mark.parametrize(
    "daily_growth, conceptus_growth, body_weight_tissue", [
        (10, 5, 6),
        (6, 8, 3)
    ]
)
def test_calculate_cow_body_weight_change(
        daily_growth: float, conceptus_growth: float, body_weight_tissue: float,
        mock_general_properties: GeneralProperties, mock_reproduction_properties: ReproductionProperties,
        mock_animal_growth_properties: AnimalGrowthProperties, mocker: MockerFixture
) -> None:
    dummy_conceptus_weight = 1.88
    dummy_tissue_changed = 10.24

    mock__calculate_cow_target_daily_growth = mocker.patch.object(
        AnimalGrowth, "_calculate_cow_target_daily_growth", return_value=daily_growth)
    mock_calculate_cow_conceptus_growth = mocker.patch.object(
        AnimalGrowth, "_calculate_cow_conceptus_growth",
        return_value=(conceptus_growth, dummy_conceptus_weight, dummy_tissue_changed))
    mock_calculate_cow_body_weight_tissue_change = mocker.patch.object(
        AnimalGrowth, "_calculate_cow_body_weight_tissue_change",
        return_value=(body_weight_tissue, dummy_tissue_changed))

    (
        result_bw_change, result_conceptus_weight, result_tissue_changed
    ) = AnimalGrowth.calculate_cow_body_weight_change(mock_animal_growth_properties, mock_reproduction_properties,
                                                      mock_general_properties)

    assert result_bw_change == daily_growth + conceptus_growth + body_weight_tissue
    assert result_conceptus_weight == dummy_conceptus_weight
    assert result_tissue_changed == dummy_tissue_changed

    mock__calculate_cow_target_daily_growth.assert_called_once_with(mock_reproduction_properties,
                                                                    mock_general_properties)
    mock_calculate_cow_conceptus_growth.assert_called_once_with(mock_animal_growth_properties,
                                                                mock_reproduction_properties,
                                                                mock_general_properties)
    mock_calculate_cow_body_weight_tissue_change.assert_called_once_with(mock_animal_growth_properties,
                                                                         mock_reproduction_properties,
                                                                         mock_general_properties)
