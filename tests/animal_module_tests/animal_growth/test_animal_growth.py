import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.animal_properties.growth_properties import GrowthProperties
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties, Breed, Sex
from RUFAS.biophysical.animal.animal_properties.reproduction_properties import ReproductionProperties
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.input_manager import InputManager
from RUFAS.time import Time


@pytest.fixture
def mock_general_properties() -> GeneralProperties:
    return GeneralProperties(
        animal_type=AnimalType.CALF,
        birth_date="",
        birth_weight=0,
        body_weight=0,
        breed=Breed.HO,
        culled=False,
        days_born=0,
        days_in_preg=0,
        days_in_milk=0,
        dry_off_day_of_pregnancy=0,
        events=AnimalEvents(),
        daily_milk_produced=0,
        future_cull_date=0,
        future_death_date=0,
        sex=Sex.FEMALE,
        id=0,
        mature_body_weight=0,
        nutrients=[],
        sold=False,
        sold_at_day=0,
        wean_weight=0,
        nutrient_concentrations={"a": 0},
        metabolizable_energy_intake=0,
    )


@pytest.fixture
def mock_animal_growth_properties() -> GrowthProperties:
    return GrowthProperties(daily_growth=0, tissue_changed=0)


@pytest.fixture
def mock_reproduction_properties() -> ReproductionProperties:
    return ReproductionProperties(
        gestation_length=0, conceptus_weight=0, calf_birth_weight=0, calves=0, calving_interval=0
    )


@pytest.mark.parametrize("wean_day, target_heifer_preg_day", [(10, 100), (60, 399)])
def test_initialize_animal_growth_variables(wean_day: int, target_heifer_preg_day: int, mocker: MockerFixture) -> None:
    im = InputManager()
    mock_get_data = mocker.patch.object(
        im,
        "get_data",
        return_value={"calf": {"wean_day": wean_day}, "bodyweight": {"target_heifer_preg_day": target_heifer_preg_day}},
    )

    Growth.initialize_animal_growth_variables()

    assert Growth.WEAN_DAY == wean_day
    assert Growth.TARGET_HEIFER_PREGNANT_DAY == target_heifer_preg_day
    mock_get_data.assert_called_once_with("animal.animal_config.farm_level")


@pytest.mark.parametrize(
    "animal_type, body_weight, mature_body_weight, is_pregnant",
    [
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
    ],
)
def test_daily_routines(
    animal_type: AnimalType,
    body_weight: float,
    mature_body_weight: float,
    is_pregnant: bool,
    mock_general_properties: GeneralProperties,
    mock_animal_growth_properties: GrowthProperties,
    mock_reproduction_properties: ReproductionProperties,
    mocker: MockerFixture,
) -> None:
    mock_time = mocker.MagicMock(auto_spec=Time)
    mock_time.simulation_day = 18

    mock_general_properties.animal_type = animal_type
    mock_general_properties.body_weight = body_weight
    mock_general_properties.mature_body_weight = mature_body_weight
    mock_general_properties.days_in_preg = 1 if is_pregnant else 0

    mock_reproduction_properties.conceptus_weight = 68
    mock_animal_growth_properties.tissue_changed = 88

    dummy_daily_growth = 5
    dummy_conceptus_weight = 233
    dummy_tissue_changed = 18
    mock_calf_bw_change = mocker.patch.object(
        Growth, "calculate_calf_body_weight_change", return_value=dummy_daily_growth
    )
    mock_non_preg_heifer_bw_change = mocker.patch.object(
        Growth, "calculate_non_pregnant_heifer_body_weight_change", return_value=dummy_daily_growth
    )
    mock_preg_heifer_bw_change = mocker.patch.object(
        Growth,
        "calculate_pregnant_heifer_body_weight_change",
        return_value=(dummy_daily_growth, dummy_conceptus_weight),
    )
    mock_cow_bw_change = mocker.patch.object(
        Growth,
        "calculate_cow_body_weight_change",
        return_value=(dummy_daily_growth, dummy_conceptus_weight, dummy_tissue_changed),
    )

    (result_animal_growth_properties, result_reproduction_properties, result_general_properties) = (
        Growth.evaluate_body_weight_change(
            mock_general_properties, mock_animal_growth_properties, mock_reproduction_properties, mock_time
        )
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
        mock_cow_bw_change.assert_called_once_with(
            mock_animal_growth_properties, mock_reproduction_properties, mock_general_properties
        )
        mock_calf_bw_change.assert_not_called()
        mock_non_preg_heifer_bw_change.assert_not_called()
        mock_preg_heifer_bw_change.assert_not_called()

        assert result_animal_growth_properties.daily_growth == dummy_daily_growth
        assert result_general_properties.body_weight == body_weight + dummy_daily_growth
        assert result_reproduction_properties.conceptus_weight == dummy_conceptus_weight
        assert result_animal_growth_properties.tissue_changed == dummy_tissue_changed


@pytest.mark.parametrize("birth_weight, wean_day", [(100, 25), (60, 60)])
def test_calculate_calf_body_weight_change(
    birth_weight: float, wean_day: int, mock_general_properties: GeneralProperties
) -> None:
    Growth.WEAN_DAY = wean_day
    mock_general_properties.birth_weight = birth_weight

    result = Growth.calculate_calf_body_weight_change(mock_general_properties)

    assert result == birth_weight / wean_day


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, target_heifer_pregnant_day, days_born, expected",
    [
        (15, 100, 60, 60, 38.4),
        (15, 100, 60, 50, 3.84),
        (15, 100, 60, 75, 2.56),
        (15, 100, 60, 61, 38.4),
    ],
)
def test_calculate_non_pregnant_heifer_body_weight_change(
    body_weight: float,
    mature_body_weight: float,
    target_heifer_pregnant_day: int,
    days_born: int,
    expected: float,
    mock_general_properties: GeneralProperties,
) -> None:
    Growth.TARGET_HEIFER_PREGNANT_DAY = target_heifer_pregnant_day

    mock_general_properties.days_born = days_born
    mock_general_properties.body_weight = body_weight
    mock_general_properties.mature_body_weight = mature_body_weight

    result = Growth.calculate_non_pregnant_heifer_body_weight_change(mock_general_properties)

    assert pytest.approx(result) == expected


@pytest.mark.parametrize("daily_growth, conceptus_growth", [(10, 5), (6, 8)])
def test_calculate_pregnant_heifer_body_weight_change(
    daily_growth: float,
    conceptus_growth: float,
    mock_reproduction_properties: ReproductionProperties,
    mock_general_properties: GeneralProperties,
    mocker: MockerFixture,
) -> None:
    dummy_conceptus_weight = 1.88

    mock_calculate_pregnant_heifer_target_daily_growth = mocker.patch.object(
        Growth, "_calculate_pregnant_heifer_target_daily_growth", return_value=daily_growth
    )
    mock_calculate_pregnant_heifer_conceptus_growth = mocker.patch.object(
        Growth,
        "_calculate_pregnant_heifer_conceptus_growth",
        return_value=(conceptus_growth, dummy_conceptus_weight),
    )

    (result_bw_change, result_conceptus_weight) = Growth.calculate_pregnant_heifer_body_weight_change(
        mock_reproduction_properties, mock_general_properties
    )

    assert result_bw_change == daily_growth + conceptus_growth
    assert result_conceptus_weight == dummy_conceptus_weight

    mock_calculate_pregnant_heifer_target_daily_growth.assert_called_once_with(
        mock_reproduction_properties, mock_general_properties
    )
    mock_calculate_pregnant_heifer_conceptus_growth.assert_called_once_with(
        mock_reproduction_properties, mock_general_properties
    )


@pytest.mark.parametrize("daily_growth, conceptus_growth, body_weight_tissue", [(10, 5, 6), (6, 8, 3)])
def test_calculate_cow_body_weight_change(
    daily_growth: float,
    conceptus_growth: float,
    body_weight_tissue: float,
    mock_general_properties: GeneralProperties,
    mock_reproduction_properties: ReproductionProperties,
    mock_animal_growth_properties: GrowthProperties,
    mocker: MockerFixture,
) -> None:
    dummy_conceptus_weight = 1.88
    dummy_tissue_changed = 10.24

    mock__calculate_cow_target_daily_growth = mocker.patch.object(
        Growth, "_calculate_cow_target_daily_growth", return_value=daily_growth
    )
    mock_calculate_cow_conceptus_growth = mocker.patch.object(
        Growth,
        "_calculate_cow_conceptus_growth",
        return_value=(conceptus_growth, dummy_conceptus_weight, dummy_tissue_changed),
    )
    mock_calculate_cow_body_weight_tissue_change = mocker.patch.object(
        Growth,
        "_calculate_cow_body_weight_tissue_change",
        return_value=(body_weight_tissue, dummy_tissue_changed),
    )

    (result_bw_change, result_conceptus_weight, result_tissue_changed) = Growth.calculate_cow_body_weight_change(
        mock_animal_growth_properties, mock_reproduction_properties, mock_general_properties
    )

    assert result_bw_change == daily_growth + conceptus_growth + body_weight_tissue
    assert result_conceptus_weight == dummy_conceptus_weight
    assert result_tissue_changed == dummy_tissue_changed

    mock__calculate_cow_target_daily_growth.assert_called_once_with(
        mock_reproduction_properties, mock_general_properties
    )
    mock_calculate_cow_conceptus_growth.assert_called_once_with(
        mock_animal_growth_properties, mock_reproduction_properties, mock_general_properties
    )
    mock_calculate_cow_body_weight_tissue_change.assert_called_once_with(
        mock_animal_growth_properties, mock_reproduction_properties, mock_general_properties
    )


@pytest.mark.parametrize(
    "conceptus_weight, days_in_preg, gestation_length, calf_birth_weight, expected_conceptus_growth,"
    "expected_conceptus_weight",
    [
        (12.5, 30, 60, 18.8, 0, 12.5),
        (23.8, 50, 50, 13.6, -23.8, 0),
        (33.3, 80, 276, 43.9, 0.01721806061, 33.3172180606),
    ],
)
def test_calculate_pregnant_heifer_conceptus_growth(
    conceptus_weight: float,
    days_in_preg: int,
    gestation_length: int,
    calf_birth_weight: float,
    expected_conceptus_growth: float,
    expected_conceptus_weight: float,
    mock_reproduction_properties: ReproductionProperties,
    mock_general_properties: GeneralProperties,
) -> None:
    mock_reproduction_properties.conceptus_weight = conceptus_weight
    mock_reproduction_properties.gestation_length = gestation_length
    mock_reproduction_properties.calf_birth_weight = calf_birth_weight
    mock_general_properties.days_in_preg = days_in_preg

    actual_conceptus_growth, actual_conceptus_weight = Growth._calculate_pregnant_heifer_conceptus_growth(
        mock_reproduction_properties, mock_general_properties
    )

    assert pytest.approx(actual_conceptus_growth) == expected_conceptus_growth
    assert pytest.approx(actual_conceptus_weight) == expected_conceptus_weight


@pytest.mark.parametrize(
    "days_in_preg, gestation_length, tissue_changed,"
    "expected_conceptus_growth, expected_conceptus_weight, expected_tissue_change",
    [(30, 60, 12.5, 18.8, 0, 12.5), (50, 50, 12.5, 13.6, -23.8, 0), (80, 276, 23.3, 43.9, 0.01721806061, 23.3)],
)
def test_calculate_cow_conceptus_growth(
    days_in_preg: int,
    gestation_length: int,
    tissue_changed: float,
    expected_conceptus_growth: float,
    expected_conceptus_weight: float,
    expected_tissue_change: float,
    mock_reproduction_properties: ReproductionProperties,
    mock_general_properties: GeneralProperties,
    mock_animal_growth_properties: GrowthProperties,
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(
        Growth,
        "_calculate_pregnant_heifer_conceptus_growth",
        return_value=(expected_conceptus_growth, expected_conceptus_weight),
    )

    mock_reproduction_properties.gestation_length = gestation_length
    mock_general_properties.days_in_preg = days_in_preg
    mock_animal_growth_properties.tissue_changed = tissue_changed

    (actual_conceptus_growth, actual_conceptus_weight, actual_tissue_change) = Growth._calculate_cow_conceptus_growth(
        mock_animal_growth_properties, mock_reproduction_properties, mock_general_properties
    )

    assert pytest.approx(actual_conceptus_growth) == expected_conceptus_growth
    assert pytest.approx(actual_conceptus_weight) == expected_conceptus_weight
    assert pytest.approx(actual_tissue_change) == expected_tissue_change


@pytest.mark.parametrize(
    "days_in_preg, gestation_length, mature_body_weight, body_weight, expected",
    [
        (135, 276, 740.1, 543.21, 0.4335114893617016),
        (276, 276, 740.1, 665.43, -56.20607999999993),
        (288, 276, 740.1, 654.32, -3.79504),
        (135, 276, 540.1, 543.21, -0.6830842553191498),
        (276, 276, 540.1, 665.43, -213.64607999999998),
        (288, 276, 540.1, 654.32, -16.915040000000005),
    ],
)
def test_calculate_pregnant_heifer_target_daily_growth(
    days_in_preg: int,
    gestation_length: int,
    mature_body_weight: float,
    body_weight: float,
    expected: float,
    mock_reproduction_properties: ReproductionProperties,
    mock_general_properties: GeneralProperties,
) -> None:
    mock_reproduction_properties.gestation_length = gestation_length
    mock_general_properties.days_in_preg = days_in_preg
    mock_general_properties.mature_body_weight = mature_body_weight
    mock_general_properties.body_weight = body_weight

    actual = Growth._calculate_pregnant_heifer_target_daily_growth(
        mock_reproduction_properties, mock_general_properties
    )

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "calves, days_in_preg, mature_body_weight, calving_interval, body_weight, gestation_length, expected",
    [
        (1, 0, 700, 365, 600, 280, 0.18410958904),
        (1, 50, 700, 365, 600, 280, 0.190476190476),
        (2, 0, 700, 365, 600, 280, 0.147287671232),
        (2, 50, 700, 365, 600, 280, 0.4329004329),
        (0, 100, 700, 365, 600, 280, 0),
    ],
)
def test_calculate_cow_target_daily_growth(
    calves: int,
    days_in_preg: int,
    mature_body_weight: float,
    calving_interval: float,
    body_weight: float,
    gestation_length: int,
    expected: float,
    mock_reproduction_properties: ReproductionProperties,
    mock_general_properties: GeneralProperties,
) -> None:
    mock_reproduction_properties.calves = calves
    mock_reproduction_properties.gestation_length = gestation_length
    mock_reproduction_properties.calving_interval = calving_interval
    mock_general_properties.days_in_preg = days_in_preg
    mock_general_properties.mature_body_weight = mature_body_weight
    mock_general_properties.body_weight = body_weight

    actual = Growth._calculate_cow_target_daily_growth(mock_reproduction_properties, mock_general_properties)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "calves, days_in_milk, days_in_preg, dry_off_day_of_pregnancy, tissue_changed, gestation_length,"
    "expected_body_weight_tissue, expected_updated_tissue_changed",
    [
        (1, 30, 100, 250, 5, 280, -0.2838717673265764, 5),
        (1, 50, 249, 250, 5, 280, -0.08943681914170182, 19.377977480702057),
        (2, 30, 100, 250, 5, 280, -0.578218759978826, 5),
        (2, 50, 249, 250, 5, 280, -0.2172591342771183, 38.020348498495714),
        (1, 0, 100, 250, 5, 280, 0.16666666666666666, 5),
    ],
)
def test_calculate_cow_body_weight_tissue_change(
    calves: int,
    days_in_milk: int,
    days_in_preg: int,
    dry_off_day_of_pregnancy: int,
    tissue_changed: float,
    gestation_length: int,
    expected_body_weight_tissue: float,
    expected_updated_tissue_changed: float,
    mock_animal_growth_properties: GrowthProperties,
    mock_reproduction_properties: ReproductionProperties,
    mock_general_properties: GeneralProperties,
) -> None:
    mock_reproduction_properties.calves = calves
    mock_reproduction_properties.gestation_length = gestation_length
    mock_animal_growth_properties.tissue_changed = tissue_changed
    mock_general_properties.days_in_milk = days_in_milk
    mock_general_properties.days_in_preg = days_in_preg
    mock_general_properties.dry_off_day_of_pregnancy = dry_off_day_of_pregnancy

    actual_body_weight_tissue, actual_updated_tissue_changed = Growth._calculate_cow_body_weight_tissue_change(
        mock_animal_growth_properties, mock_reproduction_properties, mock_general_properties
    )

    assert pytest.approx(actual_body_weight_tissue) == expected_body_weight_tissue
    assert pytest.approx(actual_updated_tissue_changed) == expected_updated_tissue_changed
