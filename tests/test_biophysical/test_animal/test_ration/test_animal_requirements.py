import math
from unittest.mock import MagicMock
import numpy as np
import pytest
from pytest_mock import MockerFixture
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.animal_requirements import AnimalRequirements


def test_default_initialization() -> None:
    """
    Test the default initialization of the AnimalRequirements class.

    This test checks that when a AnimalRequirements object is instantiated without
    any parameters, all its attributes are correctly set to their default values.

    """

    # Act
    animal_requirements = AnimalRequirements()

    # Assert
    assert animal_requirements.NEmaint_requirement == 0
    assert animal_requirements.NEa_requirement == 0
    assert animal_requirements.NEg_requirement == 0
    assert animal_requirements.NEpreg_requirement == 0
    assert animal_requirements.NEl_requirement == 0
    assert animal_requirements.MP_requirement == 0
    assert animal_requirements.Ca_requirement == 0
    assert animal_requirements.P_requirement == 0
    assert animal_requirements.DMIest_requirement == 0
    assert animal_requirements.avg_BW == 0
    assert animal_requirements.avg_milk == 0
    assert animal_requirements.avg_CP_milk == 0
    assert animal_requirements.avg_milk_production_reduction is None
    assert animal_requirements.avg_essential_amino_acid_requirement == EssentialAminoAcidRequirements(
        histidine=0.0,
        isoleucine=0.0,
        leucine=0.0,
        lysine=0.0,
        methionine=0.0,
        phenylalanine=0.0,
        threonine=0.0,
        thryptophan=0.0,
        valine=0.0,
    )


@pytest.fixture
def animal_requirements() -> AnimalRequirements:
    """Fixture to provide an instance of AnimalRequirements."""
    return AnimalRequirements()


def test_calc_pen_requirements_mean(animal_requirements: AnimalRequirements) -> None:
    """Test calc_pen_requirements using mean calculation method."""

    # Sample input data
    energy_values: list[float] = [10.0, 20.0, 30.0]
    protein_values: list[float] = [5.0, 15.0, 25.0]
    calcium_values: list[float] = [1.0, 2.0, 3.0]
    phosphorus_values: list[float] = [0.5, 1.0, 1.5]
    weight_values: list[float] = [500.0, 600.0, 700.0]
    milk_values: list[float] = [20.0, 25.0, 30.0]
    milk_cp_values: list[float] = [3.0, 3.2, 3.5]
    milk_reduction_values: list[float] = [0.1, 0.2, 0.3]

    # Sample amino acid requirements
    essential_amino_acid_values: list[EssentialAminoAcidRequirements] = [
        EssentialAminoAcidRequirements(
            histidine=1.0,
            isoleucine=1.5,
            leucine=2.0,
            lysine=2.5,
            methionine=0.8,
            phenylalanine=1.2,
            threonine=1.3,
            thryptophan=0.5,
            valine=1.4,
        ),
        EssentialAminoAcidRequirements(
            histidine=1.1,
            isoleucine=1.6,
            leucine=2.1,
            lysine=2.6,
            methionine=0.9,
            phenylalanine=1.3,
            threonine=1.4,
            thryptophan=0.6,
            valine=1.5,
        ),
        EssentialAminoAcidRequirements(
            histidine=1.2,
            isoleucine=1.7,
            leucine=2.2,
            lysine=2.7,
            methionine=1.0,
            phenylalanine=1.4,
            threonine=1.5,
            thryptophan=0.7,
            valine=1.6,
        ),
    ]

    # Call the function with mean calculation
    animal_requirements.calc_pen_requirements(
        NEmaint_requirement_list=energy_values,
        NEa_requirement_list=energy_values,
        NEg_requirement_list=energy_values,
        NEpreg_requirement_list=energy_values,
        NEl_requirement_list=energy_values,
        MP_requirement_list=protein_values,
        Ca_requirement_list=calcium_values,
        P_requirement_list=phosphorus_values,
        P_requirement_process_list=phosphorus_values,
        DMIest_requirement_list=protein_values,
        BW=weight_values,
        milk=milk_values,
        CP_milk=milk_cp_values,
        milk_production_reduction=milk_reduction_values,
        essential_amino_acid_requirement_list=essential_amino_acid_values,
        calc_method="mean",
    )

    # Assert calculated means
    assert animal_requirements.NEmaint_requirement == np.mean(energy_values)
    assert animal_requirements.MP_requirement == np.mean(protein_values)
    assert animal_requirements.Ca_requirement == np.mean(calcium_values)
    assert animal_requirements.P_requirement == np.mean(phosphorus_values)
    assert animal_requirements.avg_BW == np.mean(weight_values)
    assert animal_requirements.avg_milk == np.mean(milk_values)
    assert animal_requirements.avg_CP_milk == np.mean(milk_cp_values)
    assert animal_requirements.avg_milk_production_reduction == np.mean(milk_reduction_values)

    # Assert essential amino acid calculations
    assert animal_requirements.avg_essential_amino_acid_requirement.histidine == np.mean(
        [eaa.histidine for eaa in essential_amino_acid_values]
    )
    assert animal_requirements.avg_essential_amino_acid_requirement.isoleucine == np.mean(
        [eaa.isoleucine for eaa in essential_amino_acid_values]
    )
    assert animal_requirements.avg_essential_amino_acid_requirement.leucine == np.mean(
        [eaa.leucine for eaa in essential_amino_acid_values]
    )
    assert animal_requirements.avg_essential_amino_acid_requirement.lysine == np.mean(
        [eaa.lysine for eaa in essential_amino_acid_values]
    )
    assert animal_requirements.avg_essential_amino_acid_requirement.methionine == np.mean(
        [eaa.methionine for eaa in essential_amino_acid_values]
    )
    assert animal_requirements.avg_essential_amino_acid_requirement.phenylalanine == np.mean(
        [eaa.phenylalanine for eaa in essential_amino_acid_values]
    )
    assert animal_requirements.avg_essential_amino_acid_requirement.threonine == np.mean(
        [eaa.threonine for eaa in essential_amino_acid_values]
    )
    assert animal_requirements.avg_essential_amino_acid_requirement.thryptophan == np.mean(
        [eaa.thryptophan for eaa in essential_amino_acid_values]
    )
    assert animal_requirements.avg_essential_amino_acid_requirement.valine == np.mean(
        [eaa.valine for eaa in essential_amino_acid_values]
    )


@pytest.fixture
def mock_requirements_lists() -> dict[str, list[float | EssentialAminoAcidRequirements]]:
    """Returns a mock dictionary of requirements lists."""
    return {
        "NEmaint_requirement": [10.0, 20.0, 30.0],
        "NEa_requirement": [5.0, 10.0, 15.0],
        "NEg_requirement": [2.0, 4.0, 6.0],
        "NEpreg_requirement": [1.0, 2.0, 3.0],
        "NEl_requirement": [8.0, 16.0, 24.0],
        "MP_requirement": [100.0, 200.0, 300.0],
        "Ca_requirement": [10.0, 20.0, 30.0],
        "P_requirement": [5.0, 10.0, 15.0],
        "P_requirement_process": [3.0, 6.0, 9.0],
        "DMIest_requirement": [12.0, 24.0, 36.0],
        "BW": [500.0, 600.0, 700.0],
        "milk": [20.0, 25.0, 30.0],
        "milk_production_reduction": [0.1, 0.2, 0.3],
        "CP_milk": [3.0, 3.2, 3.5],
        "essential_amino_acid_requirement": [
            EssentialAminoAcidRequirements(
                histidine=1.0,
                isoleucine=1.5,
                leucine=2.0,
                lysine=2.5,
                methionine=0.8,
                phenylalanine=1.2,
                threonine=1.3,
                thryptophan=0.5,
                valine=1.4,
            ),
            EssentialAminoAcidRequirements(
                histidine=1.1,
                isoleucine=1.6,
                leucine=2.1,
                lysine=2.6,
                methionine=0.9,
                phenylalanine=1.3,
                threonine=1.4,
                thryptophan=0.6,
                valine=1.5,
            ),
            EssentialAminoAcidRequirements(
                histidine=1.2,
                isoleucine=1.7,
                leucine=2.2,
                lysine=2.7,
                methionine=1.0,
                phenylalanine=1.4,
                threonine=1.5,
                thryptophan=0.7,
                valine=1.6,
            ),
        ],
    }


@pytest.mark.parametrize(
    "recalc, expected_method", [(True, "recalculate_requirements"), (False, "use_existing_requirements")]
)
def test_set_requirements(
    animal_requirements: AnimalRequirements,
    mock_requirements_lists: dict[str, list[float | EssentialAminoAcidRequirements]],
    recalc: bool,
    expected_method: str,
    mocker: MockerFixture,
) -> None:
    """Test set_requirements with both recalculation enabled and disabled."""
    mock_pen = MagicMock()
    mock_animal_grouping_scenario = MagicMock()
    mock_method = MagicMock(return_value=mock_requirements_lists)
    setattr(animal_requirements, expected_method, mock_method)
    mock_calc_pen_requirements = mocker.patch.object(animal_requirements, "calc_pen_requirements")

    animal_requirements.set_requirements(mock_pen, mock_animal_grouping_scenario, recalc=recalc)

    mock_method.assert_called_once()
    mock_calc_pen_requirements.assert_called_once_with(
        mock_requirements_lists["NEmaint_requirement"],
        mock_requirements_lists["NEa_requirement"],
        mock_requirements_lists["NEg_requirement"],
        mock_requirements_lists["NEpreg_requirement"],
        mock_requirements_lists["NEl_requirement"],
        mock_requirements_lists["MP_requirement"],
        mock_requirements_lists["Ca_requirement"],
        mock_requirements_lists["P_requirement"],
        mock_requirements_lists["P_requirement_process"],
        mock_requirements_lists["DMIest_requirement"],
        mock_requirements_lists["BW"],
        mock_requirements_lists["milk"],
        mock_requirements_lists["CP_milk"],
        mock_requirements_lists["milk_production_reduction"],
        mock_requirements_lists["essential_amino_acid_requirement"],
        "mean",
    )

    mock_pen.set_avg_nutrient_rqmts.assert_called_once()
    mock_pen.set_milk_avgs.assert_called_once_with(
        animal_requirements.avg_milk, animal_requirements.avg_CP_milk, animal_requirements.avg_milk_production_reduction
    )


@pytest.fixture
def mock_pen() -> MagicMock:
    """Mock the Pen class."""
    pen = MagicMock()
    pen.animals_in_pen = {}
    pen.vertical_dist_to_parlor = 5.0
    pen.horizontal_dist_to_parlor = 10.0
    pen.housing_type = "freestall"
    return pen


@pytest.fixture
def mock_empty_requirements_lists() -> dict[str, list[float | EssentialAminoAcidRequirements]]:
    """Returns a mock dictionary of requirements lists with initial empty values."""
    return {
        "NEmaint_requirement": [],
        "NEa_requirement": [],
        "NEg_requirement": [],
        "NEpreg_requirement": [],
        "NEl_requirement": [],
        "MP_requirement": [],
        "Ca_requirement": [],
        "P_requirement": [],
        "P_requirement_process": [],
        "DMIest_requirement": [],
        "BW": [],
        "milk": [],
        "milk_production_reduction": [],
        "CP_milk": [],
        "essential_amino_acid_requirement": [],
    }


@pytest.mark.parametrize(
    "animal_type, should_have_milk",
    [
        (AnimalType.HEIFER_I, False),
        (AnimalType.HEIFER_II, False),
        (AnimalType.HEIFER_III, False),
        (AnimalType.DRY_COW, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_recalculate_requirements(
    animal_requirements: AnimalRequirements,
    mock_empty_requirements_lists: dict[str, list[float | EssentialAminoAcidRequirements]],
    mock_pen: MagicMock,
    animal_type: AnimalType,
    should_have_milk: bool,
    mocker: MockerFixture,
) -> None:
    """Test recalculate_requirements with various animal types."""
    mock_animal_grouping_scenario = MagicMock()

    mock_animal = MagicMock()
    mock_animal.body_weight = 600.0
    mock_animal.mature_body_weight = 700.0
    mock_animal.daily_growth = 1.2
    mock_animal.days_in_preg = 120
    mock_animal.calves = 2
    mock_animal.CI = 365
    mock_animal.mPrt = 3.2
    mock_animal.fat_percent = 4.0
    mock_animal.lactose_milk = 5.0
    mock_animal.estimated_daily_milk_produced = 30.0
    mock_animal.days_in_milk = 150
    mock_animal.milking = True
    mock_animal.milk_production_reduction = 0.2
    mock_animal.CP_milk = 3.5
    mock_animal.p_req = 2.5
    mock_animal.essential_amino_acid_requirement = EssentialAminoAcidRequirements(
        histidine=1.0,
        isoleucine=1.5,
        leucine=2.0,
        lysine=2.5,
        methionine=0.8,
        phenylalanine=1.2,
        threonine=1.3,
        thryptophan=0.5,
        valine=1.4,
    )
    mock_pen.animals_in_pen = {1: mock_animal}
    mock_animal_grouping_scenario.get_animal_type.return_value = animal_type
    mock_requirements = {
        "NEmaint_requirement": 10.0,
        "NEg_requirement": 5.0,
        "NEpreg_requirement": 3.0,
        "NEl_requirement": 8.0,
        "MP_requirement": 12.0,
        "Ca_requirement": 1.5,
        "P_requirement": 0.8,
        "DMIest_requirement": 25.0,
        "essential_amino_acid_requirement": mock_animal.essential_amino_acid_requirement,
    }
    mock_calc_rqmts = mocker.patch.object(animal_requirements, "calc_rqmts", return_value=mock_requirements)
    mock_energy_activity_rqmts = mocker.patch.object(animal_requirements, "energy_activity_rqmts", return_value=2.0)

    updated_requirements = animal_requirements.recalculate_requirements(
        mock_pen, mock_animal_grouping_scenario, mock_empty_requirements_lists
    )

    mock_calc_rqmts.assert_called_once()
    if animal_type == AnimalType.LAC_COW:
        mock_energy_activity_rqmts.assert_called_once()
    assert updated_requirements["NEmaint_requirement"] == [10.0]
    assert updated_requirements["NEg_requirement"] == [5.0]
    assert updated_requirements["NEpreg_requirement"] == [3.0]
    assert updated_requirements["NEl_requirement"] == [8.0]
    assert updated_requirements["MP_requirement"] == [12.0]
    assert updated_requirements["Ca_requirement"] == [1.5]
    assert updated_requirements["P_requirement"] == [0.8]
    assert updated_requirements["DMIest_requirement"] == [25.0]
    assert updated_requirements["P_requirement_process"] == [2.5]
    assert updated_requirements["BW"] == [600.0]
    assert updated_requirements["essential_amino_acid_requirement"] == [mock_animal.essential_amino_acid_requirement]
    if should_have_milk:
        assert updated_requirements["milk"] == [30.0]
        assert updated_requirements["milk_production_reduction"] == [0.2]
        assert updated_requirements["CP_milk"] == [3.5]
    else:
        assert updated_requirements["milk"] == []
        assert updated_requirements["milk_production_reduction"] == []
        assert updated_requirements["CP_milk"] == []


@pytest.mark.parametrize(
    "animal_type, should_have_milk",
    [
        (AnimalType.HEIFER_I, False),
        (AnimalType.HEIFER_II, False),
        (AnimalType.HEIFER_III, False),
        (AnimalType.DRY_COW, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_use_existing_requirements(
    animal_requirements: AnimalRequirements,
    mock_pen: MagicMock,
    mock_empty_requirements_lists: dict[str, list[float | EssentialAminoAcidRequirements]],
    animal_type: AnimalType,
    should_have_milk: bool,
    mocker: MockerFixture,
) -> None:
    mock_animal_grouping_scenario = MagicMock()
    mock_animal = MagicMock()
    mock_animal.body_weight = 600.0
    mock_animal.NEmaint_requirement = 10.0
    mock_animal.NEg_requirement = 5.0
    mock_animal.NEpreg_requirement = 3.0
    mock_animal.NEl_requirement = 8.0
    mock_animal.MP_requirement = 12.0
    mock_animal.Ca_requirement = 1.5
    mock_animal.P_requirement = 0.8
    mock_animal.p_req = 2.5
    mock_animal.DMIest_requirement = 25.0
    mock_animal.essential_amino_acid_requirement = EssentialAminoAcidRequirements(
        histidine=1.0,
        isoleucine=1.5,
        leucine=2.0,
        lysine=2.5,
        methionine=0.8,
        phenylalanine=1.2,
        threonine=1.3,
        thryptophan=0.5,
        valine=1.4,
    )

    if should_have_milk:
        mock_animal.estimated_daily_milk_produced = 30.0
        mock_animal.milk_production_reduction = 0.2
        mock_animal.CP_milk = 3.5
        mock_animal.calc_daily_walking_dist = MagicMock()
        mock_energy_activity_rqmts = mocker.patch.object(animal_requirements, "energy_activity_rqmts", return_value=2.0)
    else:
        mock_animal.estimated_daily_milk_produced = None
        mock_animal.milk_production_reduction = None
        mock_animal.CP_milk = None

    mock_pen.animals_in_pen = {1: mock_animal}
    mock_animal_grouping_scenario.get_animal_type.return_value = animal_type

    updated_requirements = animal_requirements.use_existing_requirements(
        mock_pen, mock_animal_grouping_scenario, mock_empty_requirements_lists
    )

    assert updated_requirements["NEmaint_requirement"] == [10.0]
    assert updated_requirements["NEg_requirement"] == [5.0]
    assert updated_requirements["NEpreg_requirement"] == [3.0]
    assert updated_requirements["NEl_requirement"] == [8.0]
    assert updated_requirements["MP_requirement"] == [12.0]
    assert updated_requirements["Ca_requirement"] == [1.5]
    assert updated_requirements["P_requirement"] == [0.8]
    assert updated_requirements["P_requirement_process"] == [2.5]
    assert updated_requirements["DMIest_requirement"] == [25.0]
    assert updated_requirements["BW"] == [600.0]
    assert updated_requirements["essential_amino_acid_requirement"] == [mock_animal.essential_amino_acid_requirement]

    if should_have_milk:
        assert updated_requirements["milk"] == [30.0]
        assert updated_requirements["milk_production_reduction"] == [0.2]
        assert updated_requirements["CP_milk"] == [3.5]
        mock_animal.calc_daily_walking_dist.assert_called_once()
        mock_energy_activity_rqmts.assert_called_once()
    else:
        assert updated_requirements["milk"] == []
        assert updated_requirements["milk_production_reduction"] == []
        assert updated_requirements["CP_milk"] == []


@pytest.mark.parametrize(
    "nutrient_standard, should_raise_error", [("NRC", False), ("NASEM", False), ("Unsupported", True)]
)
def test_calc_rqmts(
    animal_requirements: AnimalRequirements, nutrient_standard: str, should_raise_error: bool, mocker: MockerFixture
) -> None:
    Animal.config = {"nutrient_standard": nutrient_standard, "ration": {"phosphorus_requirement_buffer": 10}}

    mock_body_weight = 600.0
    mock_mature_body_weight = 700.0
    mock_day_of_pregnancy = 120
    mock_animal_type = AnimalType.LAC_COW
    mock_parity = 2
    mock_calving_interval = 365
    mock_milk_true_protein = 3.2
    mock_milk_fat = 4.0
    mock_milk_lactose = 5.0
    mock_milk_production = 30.0
    mock_days_in_milk = 150
    mock_lactating = True
    mock_body_condition_score_5 = 3
    mock_previous_temperature = 15.0
    mock_average_daily_gain_heifer = 1.2
    mock_NDF_conc = 0.3
    mock_TDN_conc = 0.7
    mock_net_energy_diet_concentration = 1.0
    mock_days_born = 100

    mocker.patch.object(
        animal_requirements, "calculate_NRC_energy_maintenance_requirements", return_value=(10.0, 2.0, 40.0)
    )
    mocker.patch.object(animal_requirements, "calculate_NRC_energy_growth_requirements", return_value=(5.0, 1.2, 30.0))
    mocker.patch.object(animal_requirements, "calculate_NRC_energy_pregnancy_requirements", return_value=3.0)
    mocker.patch.object(animal_requirements, "calculate_NRC_energy_lactation_requirements", return_value=8.0)
    mocker.patch.object(animal_requirements, "calculate_NRC_DMI", return_value=25.0)
    mocker.patch.object(animal_requirements, "calculate_NRC_protein_requirements", return_value=12.0)
    mocker.patch.object(animal_requirements, "calculate_NRC_calcium_requirements", return_value=1.5)
    mocker.patch.object(animal_requirements, "calculate_NRC_phosphorus_requirements", return_value=0.8)
    mocker.patch.object(
        animal_requirements, "calculate_NASEM_energy_maintenance_requirements", return_value=(10.0, 2.0, 1.5)
    )
    mocker.patch.object(
        animal_requirements, "calculate_NASEM_energy_growth_requirements", return_value=(5.0, 1.2, 30.0)
    )
    mocker.patch.object(animal_requirements, "calculate_NASEM_energy_pregnancy_requirements", return_value=(3.0, 2.5))
    mocker.patch.object(animal_requirements, "calculate_NASEM_energy_lactation_requirements", return_value=8.0)
    mocker.patch.object(animal_requirements, "calculate_NASEM_DMI", return_value=25.0)
    mocker.patch.object(animal_requirements, "calculate_NASEM_protein_requirements", return_value=12.0)
    mocker.patch.object(animal_requirements, "calculate_NASEM_calcium_requirements", return_value=1.5)
    mocker.patch.object(animal_requirements, "calculate_NASEM_phosphorus_requirements", return_value=0.8)

    mock_amino_acid_calculator = mocker.patch("RUFAS.biophysical.animal.ration.amino_acid.AminoAcidCalculator")
    mock_amino_acid_calculator.calculate_essential_amino_acid_requirements.return_value = (
        EssentialAminoAcidRequirements(
            histidine=77.6472,
            isoleucine=136.5188,
            leucine=248.1471,
            lysine=218.7945,
            methionine=68.46508,
            phenylalanine=146.9849,
            threonine=142.1294,
            thryptophan=33.286381,
            valine=161.06672,
        )
    )

    if should_raise_error:
        with pytest.raises(ValueError):
            mocker.patch(
                "RUFAS.biophysical.animal.ration.animal_requirements.OutputManager.__init__", return_value=None
            )
            mock_add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
            animal_requirements.calc_rqmts(
                body_weight=mock_body_weight,
                mature_body_weight=mock_mature_body_weight,
                day_of_pregnancy=mock_day_of_pregnancy,
                animal_type=mock_animal_type,
                parity=mock_parity,
                calving_interval=mock_calving_interval,
                milk_true_protein=mock_milk_true_protein,
                milk_fat=mock_milk_fat,
                milk_lactose=mock_milk_lactose,
                milk_production=mock_milk_production,
                days_in_milk=mock_days_in_milk,
                lactating=mock_lactating,
                body_condition_score_5=mock_body_condition_score_5,
                previous_temperature=mock_previous_temperature,
                average_daily_gain_heifer=mock_average_daily_gain_heifer,
                NDF_conc=mock_NDF_conc,
                TDN_conc=mock_TDN_conc,
                net_energy_diet_concentration=mock_net_energy_diet_concentration,
                days_born=mock_days_born,
            )
            mock_add_error.assert_called_once_with(
                "nutrient_standard_error",
                f"Nutrient Standard {nutrient_standard} not supported",
                {"function": animal_requirements.calc_rqmts},
            )
    else:
        result = animal_requirements.calc_rqmts(
            body_weight=mock_body_weight,
            mature_body_weight=mock_mature_body_weight,
            day_of_pregnancy=mock_day_of_pregnancy,
            animal_type=mock_animal_type,
            parity=mock_parity,
            calving_interval=mock_calving_interval,
            milk_true_protein=mock_milk_true_protein,
            milk_fat=mock_milk_fat,
            milk_lactose=mock_milk_lactose,
            milk_production=mock_milk_production,
            days_in_milk=mock_days_in_milk,
            lactating=mock_lactating,
            body_condition_score_5=mock_body_condition_score_5,
            previous_temperature=mock_previous_temperature,
            average_daily_gain_heifer=mock_average_daily_gain_heifer,
            NDF_conc=mock_NDF_conc,
            TDN_conc=mock_TDN_conc,
            net_energy_diet_concentration=mock_net_energy_diet_concentration,
            days_born=mock_days_born,
        )

        assert result["NEmaint_requirement"] == 10.0
        assert result["NEg_requirement"] == 5.0
        assert result["NEpreg_requirement"] == 3.0
        assert result["NEl_requirement"] == 8.0
        assert result["MP_requirement"] == 12.0
        assert result["Ca_requirement"] == 1.5
        assert result["P_requirement"] == pytest.approx(0.88)
        assert result["DMIest_requirement"] == 25.0

        if nutrient_standard == "NASEM":
            for attr in EssentialAminoAcidRequirements.__annotations__.keys():
                assert getattr(result["essential_amino_acid_requirement"], attr) == pytest.approx(
                    getattr(mock_amino_acid_calculator.calculate_essential_amino_acid_requirements.return_value, attr)
                )

        else:
            assert result["essential_amino_acid_requirement"] == EssentialAminoAcidRequirements(
                histidine=0.0,
                isoleucine=0.0,
                leucine=0.0,
                lysine=0.0,
                methionine=0.0,
                phenylalanine=0.0,
                threonine=0.0,
                thryptophan=0.0,
                valine=0.0,
            )


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, body_condition_score_5, previous_temperature, animal_type, "
    "expected_net_energy_maintenance, expected_conceptus_weight, expected_calf_birth_weight",
    [
        (600.0, 700.0, 200, 3, 15.0, AnimalType.LAC_COW, 9.4052, 24.0611, 43.925),
        (500.0, 650.0, 210, 4, 10.0, AnimalType.DRY_COW, 8.0963, 28.3699, 40.7875),
        (400.0, 600.0, None, 2, 20.0, AnimalType.HEIFER_I, 6.9228, 0.0, 0.0),
        (450.0, 620.0, 195, 3, 10.0, AnimalType.HEIFER_II, 8.1499, 18.4366, 38.905),
        (480.0, 630.0, 205, 3, 18.0, AnimalType.HEIFER_III, 8.4797, 24.57603, 39.5325),
    ],
)
def test_calculate_NRC_energy_maintenance_requirements(
    animal_requirements: AnimalRequirements,
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int,
    body_condition_score_5: int,
    previous_temperature: float,
    animal_type: AnimalType,
    expected_net_energy_maintenance: float,
    expected_conceptus_weight: float,
    expected_calf_birth_weight: float,
) -> None:
    result_net_energy_maintenance, result_conceptus_weight, result_calf_birth_weight = (
        animal_requirements.calculate_NRC_energy_maintenance_requirements(
            body_weight,
            mature_body_weight,
            day_of_pregnancy,
            body_condition_score_5,
            previous_temperature,
            animal_type,
        )
    )

    assert result_net_energy_maintenance == pytest.approx(expected_net_energy_maintenance, rel=1e-3)
    assert result_conceptus_weight == pytest.approx(expected_conceptus_weight, rel=1e-3)
    assert result_calf_birth_weight == pytest.approx(expected_calf_birth_weight, rel=1e-3)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, days_in_milk, expected_gravid_uterine_weight,"
    "expected_uterine_weight",
    [
        # Non-pregnant case (default uterine weights should be 0)
        (600.0, 700.0, None, None, 0.0, 0.0),
        # Pregnant case (gravid uterine weight and uterine weight calculated)
        (
            600.0,
            700.0,
            200,
            None,
            (700.0 * 0.06275 * 1.825) * math.exp(-(0.0243 - (0.0000245 * 200)) * (280 - 200)),
            ((700.0 * 0.06275 * 0.2288 - 0.204) * math.exp(-0.2 * 0)) + 0.204,
        ),
        # Lactating case (days_in_milk > 0 affects uterine weight)
        (
            600.0,
            700.0,
            200,
            100,
            (700.0 * 0.06275 * 1.825) * math.exp(-(0.0243 - (0.0000245 * 200)) * (280 - 200)),
            ((700.0 * 0.06275 * 0.2288 - 0.204) * math.exp(-0.2 * 100)) + 0.204,
        ),
    ],
)
def test_calculate_NASEM_energy_maintenance_requirements(
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int,
    days_in_milk: int,
    expected_gravid_uterine_weight: float,
    expected_uterine_weight: float,
) -> None:
    animal_requirements = AnimalRequirements()

    net_energy_maintenance, gravid_uterine_weight, uterine_weight = (
        animal_requirements.calculate_NASEM_energy_maintenance_requirements(
            body_weight, mature_body_weight, day_of_pregnancy, days_in_milk
        )
    )

    expected_net_energy_maintenance = (
        0.10 * (body_weight - expected_gravid_uterine_weight - expected_uterine_weight) ** 0.75
    )

    if day_of_pregnancy is None:
        expected_net_energy_maintenance = 0.10 * body_weight**0.75

    assert math.isclose(net_energy_maintenance, expected_net_energy_maintenance, rel_tol=1e-6)
    assert math.isclose(gravid_uterine_weight, expected_gravid_uterine_weight, rel_tol=1e-6)
    assert math.isclose(uterine_weight, expected_uterine_weight, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, conceptus_weight, animal_type, parity, calving_interval,"
    "average_daily_gain_heifer, expected_avg_daily_gain",
    [
        # Parity 1, valid calving interval
        (600.0, 700.0, 50.0, AnimalType.LAC_COW, 1, 365, None, 0.18410958),
        # Parity 2, valid calving interval
        (600.0, 700.0, 50.0, AnimalType.DRY_COW, 2, 365, None, 0.14728767),
        # Parity > 2, calving interval ignored
        (600.0, 700.0, 50.0, AnimalType.LAC_COW, 3, 365, None, 0.0),
        # Heifer I with a positive daily gain
        (400.0, 600.0, 30.0, AnimalType.HEIFER_I, 0, None, 1.2, 1.2),
        # Heifer III with a negative daily gain (should be set to 0)
        (500.0, 650.0, 40.0, AnimalType.HEIFER_III, 0, None, -0.5, 0.0),
    ],
)
def test_calculate_NRC_energy_growth_requirements(
    body_weight: float,
    mature_body_weight: float,
    conceptus_weight: float,
    animal_type: AnimalType,
    parity: int,
    calving_interval: int | None,
    average_daily_gain_heifer: float | None,
    expected_avg_daily_gain: float,
) -> None:
    animal_requirements = AnimalRequirements()
    MSBW = 0.96 * mature_body_weight
    SBW = 0.96 * body_weight
    equivalent_shrunk_body_weight = (SBW - conceptus_weight) * (478 / MSBW)

    EQEBG = 0.956 * expected_avg_daily_gain
    EQEBW = 0.891 * equivalent_shrunk_body_weight
    expected_net_energy_growth = 0.0635 * EQEBW**0.75 * EQEBG**1.097

    net_energy_growth, avg_daily_gain, equiv_shrunk_body_weight = (
        animal_requirements.calculate_NRC_energy_growth_requirements(
            body_weight,
            mature_body_weight,
            conceptus_weight,
            animal_type,
            parity,
            calving_interval,
            average_daily_gain_heifer,
        )
    )

    assert math.isclose(net_energy_growth, expected_net_energy_growth, rel_tol=1e-6)
    assert math.isclose(avg_daily_gain, expected_avg_daily_gain, rel_tol=1e-6)
    assert math.isclose(equiv_shrunk_body_weight, equivalent_shrunk_body_weight, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, average_daily_gain_heifer, animal_type, parity, calving_interval, "
    "expected_avg_daily_gain, expected_net_energy_growth, expected_frame_weight_gain",
    [
        # Parity 1, valid calving interval
        (600.0, 700.0, None, AnimalType.LAC_COW, 1, 365, 0.18410958904109606, 1.1240441230631046, 0.44199999999999995),
        # Parity 2, valid calving interval
        (600.0, 700.0, None, AnimalType.DRY_COW, 2, 365, 0.14728767123287664, 0.8992352984504822, 0.44199999999999995),
        # Parity > 2, calving interval ignored (no growth)
        (600.0, 700.0, None, AnimalType.LAC_COW, 3, 365, 1e-05, 0.0, 0.0),
        # Heifer I with a positive daily gain
        (400.0, 600.0, 1.2, AnimalType.HEIFER_I, 0, None, 1.2, 6.346824590163934, 0.39440000000000003),
        # Heifer III with a negative daily gain
        (500.0, 650.0, -0.5, AnimalType.HEIFER_III, 0, None, 1e-05, 0.0, 0.0),
        # Edge case: average_daily_gain == 0
        (500.0, 650.0, 0.0, AnimalType.HEIFER_II, 0, None, 1e-05, 0.0, 0.0),
        # Edge case: CALF AnimalType
        (500.0, 650.0, 0.0, AnimalType.CALF, 0, None, 1e-05, 0.0, 0.0),
    ],
)
def test_calculate_NASEM_energy_growth_requirements(
    body_weight: float,
    mature_body_weight: float,
    average_daily_gain_heifer: float | None,
    animal_type: AnimalType,
    parity: int,
    calving_interval: int | None,
    expected_avg_daily_gain: float,
    expected_net_energy_growth: float,
    expected_frame_weight_gain: float,
) -> None:
    animal_requirements = AnimalRequirements()
    net_energy_growth, avg_daily_gain, frame_weight_gain_calc = (
        animal_requirements.calculate_NASEM_energy_growth_requirements(
            body_weight, mature_body_weight, average_daily_gain_heifer, animal_type, parity, calving_interval
        )
    )

    assert math.isclose(net_energy_growth, expected_net_energy_growth, rel_tol=1e-6)
    assert math.isclose(avg_daily_gain, expected_avg_daily_gain, rel_tol=1e-6)
    assert math.isclose(frame_weight_gain_calc, expected_frame_weight_gain, rel_tol=1e-6)


@pytest.mark.parametrize(
    "day_of_pregnancy, calf_birth_weight, expected_net_energy_pregnancy",
    [
        # Case 1: day_of_pregnancy is None → should return 0.0
        (None, 40.0, 0.0),
        # Case 2: day_of_pregnancy ≤ 190 → should return 0.0
        (150, 40.0, 0.0),
        # Case 3: day_of_pregnancy exactly 190 → should return 0.0
        (190, 40.0, 0.0),
        # Case 4: day_of_pregnancy > 190, valid calf birth weight
        (220, 45.0, 3.037257142857143),
        # Case 5: day_of_pregnancy > 190, different calf birth weight
        (250, 50.0, 3.8593015873015872),
        # Case 6: Large day_of_pregnancy, large calf birth weight
        (280, 55.0, 4.778260317460317),
    ],
)
def test_calculate_NRC_energy_pregnancy_requirements(
    day_of_pregnancy: int | None, calf_birth_weight: float, expected_net_energy_pregnancy: float
) -> None:
    animal_requirements = AnimalRequirements()

    net_energy_pregnancy = animal_requirements.calculate_NRC_energy_pregnancy_requirements(
        day_of_pregnancy, calf_birth_weight
    )

    assert math.isclose(net_energy_pregnancy, expected_net_energy_pregnancy, rel_tol=1e-6)


@pytest.mark.parametrize(
    "lactating, day_of_pregnancy, days_in_milk, gravid_uterine_weight, uterine_weight, "
    "expected_net_energy_pregnancy, expected_gravid_uterine_weight_gain",
    [
        # Case 1: Lactating cow with days in milk
        (True, None, 150, 10.0, 0.5, -55.944, -8.88),
        # Case 2: Not lactating, day_of_pregnancy is None → should return 0.0
        (False, None, None, 12.0, 0.6, 0.0, 0.0),
        # Case 3: Not lactating, early pregnancy
        (False, 120, None, 15.0, 0.7, 1.3322231999999998, 0.32039999999999996),
        # Case 4: Not lactating, mid-pregnancy
        (False, 200, None, 20.0, 0.8, 1.613304, 0.388),
        # Case 5: Not lactating, late pregnancy
        (False, 280, None, 25.0, 0.9, 1.8128879999999998, 0.43599999999999994),
    ],
)
def test_calculate_NASEM_energy_pregnancy_requirements(
    lactating: bool,
    day_of_pregnancy: int | None,
    days_in_milk: int | None,
    gravid_uterine_weight: float,
    uterine_weight: float,
    expected_net_energy_pregnancy: float,
    expected_gravid_uterine_weight_gain: float,
) -> None:
    """Unit test for `calculate_NASEM_energy_pregnancy_requirements`."""

    animal_requirements = AnimalRequirements()

    net_energy_pregnancy, gravid_uterine_weight_gain = (
        animal_requirements.calculate_NASEM_energy_pregnancy_requirements(
            lactating, day_of_pregnancy, days_in_milk, gravid_uterine_weight, uterine_weight
        )
    )

    assert math.isclose(net_energy_pregnancy, expected_net_energy_pregnancy, rel_tol=1e-6)
    assert math.isclose(gravid_uterine_weight_gain, expected_gravid_uterine_weight_gain, rel_tol=1e-6)


@pytest.mark.parametrize(
    "animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production, expected_net_energy_lactation",
    [
        # Lactating cow with standard milk composition
        (AnimalType.LAC_COW, 3.5, 3.2, 4.8, 30.0, 21.088951612903227),
        # Higher milk fat percentage
        (AnimalType.LAC_COW, 4.5, 3.0, 5.0, 25.0, 19.800040322580646),
        # Lower milk fat and protein
        (AnimalType.LAC_COW, 2.5, 2.8, 4.5, 35.0, 20.114086021505376),
        # Edge case: Zero milk production → should return 0.0
        (AnimalType.LAC_COW, 3.8, 3.1, 4.9, 0.0, 0.0),
        # Non-lactating cow → should return 0.0
        (AnimalType.DRY_COW, 3.5, 3.2, 4.8, 30.0, 0.0),
    ],
)
def test_calculate_NRC_energy_lactation_requirements(
    animal_type: AnimalType,
    milk_fat: float,
    milk_true_protein: float,
    milk_lactose: float,
    milk_production: float,
    expected_net_energy_lactation: float,
) -> None:
    """Unit test for `calculate_NRC_energy_lactation_requirements`."""

    animal_requirements = AnimalRequirements()

    net_energy_lactation = animal_requirements.calculate_NRC_energy_lactation_requirements(
        animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production
    )

    assert math.isclose(net_energy_lactation, expected_net_energy_lactation, rel_tol=1e-6)


@pytest.mark.parametrize(
    "animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production, expected_net_energy_lactation",
    [
        # Standard lactating cow case
        (AnimalType.LAC_COW, 3.5, 3.2, 4.8, 30.0, 21.088951612903227),
        # Higher milk fat percentage
        (AnimalType.LAC_COW, 4.5, 3.0, 5.0, 25.0, 19.800040322580646),
        # Lower milk fat and protein
        (AnimalType.LAC_COW, 2.5, 2.8, 4.5, 35.0, 20.114086021505376),
        # Edge case: Zero milk production (should return 0.0)
        (AnimalType.LAC_COW, 3.8, 3.1, 4.9, 0.0, 0.0),
        # Non-lactating cow (should return 0.0)
        (AnimalType.DRY_COW, 3.5, 3.2, 4.8, 30.0, 0.0),
    ],
)
def test_calculate_NASEM_energy_lactation_requirements(
    animal_type: AnimalType,
    milk_fat: float,
    milk_true_protein: float,
    milk_lactose: float,
    milk_production: float,
    expected_net_energy_lactation: float,
) -> None:
    """Unit test for `calculate_NASEM_energy_lactation_requirements`."""

    animal_requirements = AnimalRequirements()

    net_energy_lactation = animal_requirements.calculate_NASEM_energy_lactation_requirements(
        animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production
    )

    assert math.isclose(net_energy_lactation, expected_net_energy_lactation, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, conceptus_weight, day_of_pregnancy, animal_type, milk_production, milk_true_protein, "
    "calf_birth_weight, net_energy_growth, average_daily_gain, equivalent_shrunk_body_weight, "
    "dry_matter_intake_estimate, TDN_conc, expected_metabolizable_protein_requirement",
    [
        # Lactating cow with standard parameters
        (600.0, 20.0, 200, AnimalType.LAC_COW, 30.0, 3.2, 40.0, 5.0, 1.2, 480.0, 25.0, 0.7, 2725.35853013262),
        # Heifer with moderate weight and growth
        (400.0, 0.0, None, AnimalType.HEIFER_I, 0.0, 0.0, 0.0, 4.0, 1.0, 350.0, 18.0, 0.65, 747.5941288630154),
        # Dry cow, no milk production
        (700.0, 30.0, 220, AnimalType.DRY_COW, 0.0, 0.0, 45.0, 0.0, 0.0, 500.0, 20.0, 0.68, 696.2100142176303),
        # Edge case: No pregnancy, no lactation, no growth (minimal maintenance requirement)
        (500.0, 0.0, None, AnimalType.HEIFER_II, 0.0, 0.0, 0.0, 0.0, 0.0, 400.0, 22.0, 0.72, 434.63451275656166),
        # High-yielding lactating cow with more milk production
        (650.0, 25.0, 210, AnimalType.LAC_COW, 40.0, 3.5, 42.0, 6.0, 1.5, 490.0, 27.0, 0.7, 3622.928769416475),
        # Days of pregnancy < 190, high calf birth weight
        (650.0, 25.0, 150, AnimalType.LAC_COW, 40.0, 3.5, 42.0, 6.0, 1.5, 490.0, 27.0, 0.7, 3408.827759315465),
    ],
)
def test_calculate_NRC_protein_requirements(
    body_weight: float,
    conceptus_weight: float,
    day_of_pregnancy: int | None,
    animal_type: AnimalType,
    milk_production: float,
    milk_true_protein: float,
    calf_birth_weight: float,
    net_energy_growth: float,
    average_daily_gain: float,
    equivalent_shrunk_body_weight: float,
    dry_matter_intake_estimate: float,
    TDN_conc: float,
    expected_metabolizable_protein_requirement: float,
) -> None:
    animal_requirements = AnimalRequirements()

    metabolizable_protein_requirement = animal_requirements.calculate_NRC_protein_requirements(
        body_weight,
        conceptus_weight,
        day_of_pregnancy,
        animal_type,
        milk_production,
        milk_true_protein,
        calf_birth_weight,
        net_energy_growth,
        average_daily_gain,
        equivalent_shrunk_body_weight,
        dry_matter_intake_estimate,
        TDN_conc,
    )

    assert math.isclose(metabolizable_protein_requirement, expected_metabolizable_protein_requirement, rel_tol=1e-6)


@pytest.mark.parametrize(
    "lactating, body_weight, frame_weight_gain, gravid_uterine_weight_gain, dry_matter_intake_estimate, "
    "milk_true_protein, milk_production, NDF_conc, expected_metabolizable_protein_requirement",
    [
        # Lactating cow with moderate milk production
        (True, 600.0, 1.2, 0.8, 25.0, 3.2, 30.0, 0.3, 2213.0947138191523),
        # Dry cow, no lactation, with pregnancy
        (False, 700.0, 0.0, 1.2, 20.0, 0.0, 0.0, 0.4, 945.977494653607),
        # Heifer with growth and maintenance needs
        (False, 400.0, 1.0, 0.0, 18.0, 0.0, 0.0, 0.35, 363.8857525946213),
        # High-yielding lactating cow
        (True, 650.0, 1.5, 1.0, 27.0, 3.5, 40.0, 0.32, 2968.448844988763),
        # Minimal requirement case (no pregnancy, lactation, or growth)
        (False, 500.0, 0.0, 0.0, 22.0, 0.0, 0.0, 0.38, 447.5259818303129),
    ],
)
def test_calculate_NASEM_protein_requirements(
    lactating: bool,
    body_weight: float,
    frame_weight_gain: float,
    gravid_uterine_weight_gain: float,
    dry_matter_intake_estimate: float,
    milk_true_protein: float,
    milk_production: float,
    NDF_conc: float,
    expected_metabolizable_protein_requirement: float,
) -> None:
    animal_requirements = AnimalRequirements()

    metabolizable_protein_requirement = animal_requirements.calculate_NASEM_protein_requirements(
        lactating,
        body_weight,
        frame_weight_gain,
        gravid_uterine_weight_gain,
        dry_matter_intake_estimate,
        milk_true_protein,
        milk_production,
        NDF_conc,
    )

    assert math.isclose(metabolizable_protein_requirement, expected_metabolizable_protein_requirement, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, animal_type, average_daily_gain, milk_production,"
    "expected_calcium_requirement",
    [
        # Lactating cow with moderate milk production
        (600.0, 700.0, None, AnimalType.LAC_COW, 1.2, 30.0, 68.39135432053915),
        # Dry cow with pregnancy requirement
        (700.0, 800.0, 200, AnimalType.DRY_COW, 0.0, 0.0, 14.231023287762723),
        # Heifer in early growth stage
        (400.0, 600.0, None, AnimalType.HEIFER_I, 1.0, 0.0, 17.674955247096364),
        # High milk-producing lactating cow
        (650.0, 750.0, None, AnimalType.LAC_COW, 1.5, 40.0, 85.32061375661556),
        # Minimal requirement case (no pregnancy, lactation, or growth)
        (500.0, 650.0, None, AnimalType.DRY_COW, 0.0, 0.0, 8.1),
        # Days of pregnancy < 190
        (500.0, 650.0, 150, AnimalType.DRY_COW, 0.0, 0.0, 8.1),
    ],
)
def test_calculate_NRC_calcium_requirements(
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int | None,
    animal_type: AnimalType,
    average_daily_gain: float,
    milk_production: float,
    expected_calcium_requirement: float,
) -> None:
    animal_requirements = AnimalRequirements()

    calcium_requirement = animal_requirements.calculate_NRC_calcium_requirements(
        body_weight, mature_body_weight, day_of_pregnancy, animal_type, average_daily_gain, milk_production
    )

    assert math.isclose(calcium_requirement, expected_calcium_requirement, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, average_daily_gain, dry_matter_intake_estimate, "
    "milk_true_protein, milk_production, parity, expected_calcium_requirement",
    [
        # Lactating cow with moderate milk production
        (600.0, 700.0, None, 1.2, 20.0, 3.2, 30.0, 3, 49.794),
        # Dry cow in mid-pregnancy
        (700.0, 800.0, 200, 0.0, 15.0, 0.0, 0.0, 2, 18.536263391747113),
        # Heifer in early growth stage
        (400.0, 600.0, None, 1.0, 12.0, 0.0, 0.0, 1, 11.444031403832113),
        # High milk-yielding lactating cow
        (650.0, 750.0, None, 1.5, 22.0, 3.5, 40.0, 3, 65.06),
        # Minimal requirement case (no pregnancy, lactation, or growth)
        (500.0, 650.0, None, 0.0, 10.0, 0.0, 0.0, 2, 9.0),
    ],
)
def test_calculate_NASEM_calcium_requirements(
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int | None,
    average_daily_gain: float,
    dry_matter_intake_estimate: float,
    milk_true_protein: float,
    milk_production: float,
    parity: int,
    expected_calcium_requirement: float,
) -> None:
    animal_requirements = AnimalRequirements()

    calcium_requirement = animal_requirements.calculate_NASEM_calcium_requirements(
        body_weight,
        mature_body_weight,
        day_of_pregnancy,
        average_daily_gain,
        dry_matter_intake_estimate,
        milk_true_protein,
        milk_production,
        parity,
    )

    assert math.isclose(calcium_requirement, expected_calcium_requirement, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, day_of_pregnancy, milk_production, animal_type, "
    "average_daily_gain, dry_matter_intake_estimate, expected_phosphorus_requirement",
    [
        # Lactating cow with moderate milk production
        (600.0, 700.0, None, 30.0, AnimalType.LAC_COW, 1.2, 20.0, 55.69360399549328),
        # Dry cow in mid-pregnancy
        (700.0, 800.0, 200, 0.0, AnimalType.DRY_COW, 0.0, 15.0, 15.559901209143101),
        # Heifer in early growth stage
        (400.0, 600.0, None, 0.0, AnimalType.HEIFER_I, 1.0, 12.0, 16.928597921698035),
        # High milk-yielding lactating cow
        (650.0, 750.0, None, 40.0, AnimalType.LAC_COW, 1.5, 22.0, 68.64881431962493),
        # Minimal requirement case (no pregnancy, lactation, or growth)
        (500.0, 650.0, None, 0.0, AnimalType.DRY_COW, 0.0, 10.0, 9.0),
        # Days of pregnancy < 190
        (500.0, 650.0, 150, 0.0, AnimalType.DRY_COW, 0.0, 10.0, 9.0),
    ],
)
def test_calculate_NRC_phosphorus_requirements(
    body_weight: float,
    mature_body_weight: float,
    day_of_pregnancy: int | None,
    milk_production: float,
    animal_type: AnimalType,
    average_daily_gain: float,
    dry_matter_intake_estimate: float,
    expected_phosphorus_requirement: float,
) -> None:
    animal_requirements = AnimalRequirements()

    phosphorus_requirement = animal_requirements.calculate_NRC_phosphorus_requirements(
        body_weight,
        mature_body_weight,
        day_of_pregnancy,
        milk_production,
        animal_type,
        average_daily_gain,
        dry_matter_intake_estimate,
    )

    assert math.isclose(phosphorus_requirement, expected_phosphorus_requirement, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, animal_type, day_of_pregnancy, average_daily_gain, "
    "dry_matter_intake_estimate, milk_true_protein, milk_production, parity, expected_phosphorus_requirement",
    [
        # Lactating cow with moderate milk production
        (600.0, 700.0, AnimalType.LAC_COW, None, 1.2, 20.0, 3.2, 30.0, 3, 47.54),
        # Dry cow in late pregnancy
        (700.0, 800.0, AnimalType.DRY_COW, 210, 0.0, 15.0, None, None, 3, 14.964159),
        # Heifer in early growth stage
        (400.0, 600.0, AnimalType.HEIFER_I, None, 1.0, 12.0, None, None, 1, 16.107454),
        # High-yielding lactating cow
        (650.0, 750.0, AnimalType.LAC_COW, None, 1.5, 22.0, 3.5, 40.0, 2, 69.1648617),
        # Minimal requirement case (no pregnancy, lactation, or growth)
        (500.0, 650.0, AnimalType.DRY_COW, None, 0.0, 10.0, None, None, 3, 8.3),
        # Days of pregnancy < 190
        (500.0, 650.0, AnimalType.DRY_COW, 150, 0.0, 10.0, None, None, 3, 8.3),
        # Calf case
        (150.0, 200.0, AnimalType.CALF, None, 0.0, 2.0, None, None, 0, 0.0),
    ],
)
def test_calculate_NASEM_phosphorus_requirements(
    body_weight: float,
    mature_body_weight: float,
    animal_type: AnimalType,
    day_of_pregnancy: int | None,
    average_daily_gain: float,
    dry_matter_intake_estimate: float,
    milk_true_protein: float | None,
    milk_production: float | None,
    parity: int,
    expected_phosphorus_requirement: float,
) -> None:
    animal_requirements = AnimalRequirements()

    phosphorus_requirement = animal_requirements.calculate_NASEM_phosphorus_requirements(
        body_weight,
        mature_body_weight,
        animal_type,
        day_of_pregnancy,
        average_daily_gain,
        dry_matter_intake_estimate,
        milk_true_protein,
        milk_production,
        parity,
    )

    assert math.isclose(phosphorus_requirement, expected_phosphorus_requirement, rel_tol=1e-6)


@pytest.mark.parametrize(
    "animal_type, body_weight, day_of_pregnancy, days_in_milk, milk_production, milk_fat, "
    "net_energy_diet_concentration, days_born, expected_dry_matter_intake",
    [
        # Lactating cow, early lactation
        (AnimalType.LAC_COW, 650.0, None, 30, 35.0, 3.8, 1.4, None, 19.643986),
        # Lactating cow, mid-lactation
        (AnimalType.LAC_COW, 700.0, None, 150, 40.0, 4.0, 1.5, None, 27.8268862),
        # Dry cow, late pregnancy
        (AnimalType.DRY_COW, 750.0, 250, None, 0.0, 0.0, 1.3, None, 14.728707),
        # Heifer, over one year old
        (AnimalType.HEIFER_II, 400.0, None, None, 0.0, 0.0, 1.2, 500, 8.370049),
        # Heifer, under one year old
        (AnimalType.HEIFER_I, 300.0, None, None, 0.0, 0.0, 1.3, 200, 8.367106),
        # Late pregnancy adjustment for heifer
        (AnimalType.HEIFER_III, 500.0, 220, None, 0.0, 0.0, 1.1, 600, 8.509043),
        # Minimum DMI enforced
        (AnimalType.HEIFER_III, 100.0, None, None, 0.0, 0.0, 1.2, 100, 3.641784),
        # Net energy diet concentration < 1.0
        (AnimalType.HEIFER_III, 500.0, None, None, 0.0, 0.0, 0.9, 600, 8.511115),
    ],
)
def test_calculate_NRC_DMI(
    animal_type: AnimalType,
    body_weight: float,
    day_of_pregnancy: int,
    days_in_milk: int | None,
    milk_production: float,
    milk_fat: float,
    net_energy_diet_concentration: float,
    days_born: float,
    expected_dry_matter_intake: float,
) -> None:
    animal_requirements = AnimalRequirements()

    dry_matter_intake = animal_requirements.calculate_NRC_DMI(
        animal_type,
        body_weight,
        day_of_pregnancy,
        days_in_milk,
        milk_production,
        milk_fat,
        net_energy_diet_concentration,
        days_born,
    )

    assert math.isclose(dry_matter_intake, expected_dry_matter_intake, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, mature_body_weight, days_in_milk, lactating, net_energy_lactation, "
    "parity, body_condition_score_5, NDF_conc, expected_dry_matter_intake",
    [
        # Lactating cow, first parity, early lactation
        (650.0, 700.0, 30, True, 30.0, 1, 3, 30.0, 23.9986059),
        # Lactating cow, multiple parity, mid-lactation
        (700.0, 750.0, 150, True, 40.0, 2, 2, 28.0, 31.8780872),
        # Lactating cow, multiple parity, late lactation
        (720.0, 780.0, 250, True, 35.0, 3, 3, 32.0, 28.2379827),
        # Growing heifer, low NDF concentration
        (400.0, 600.0, None, False, 0.0, 0, 0, 20.0, 10.671114),
        # Growing heifer, high NDF concentration
        (500.0, 650.0, None, False, 0.0, 0, 0, 40.0, 10.610064),
        # Minimum DMI enforced (small animal)
        (100.0, 250.0, None, False, 0.0, 0, 0, 35.0, 2.971308),
    ],
)
def test_calculate_NASEM_DMI(
    body_weight: float,
    mature_body_weight: float,
    days_in_milk: int | None,
    lactating: bool,
    net_energy_lactation: float,
    parity: int,
    body_condition_score_5: int,
    NDF_conc: float,
    expected_dry_matter_intake: float,
) -> None:
    animal_requirements = AnimalRequirements()

    dry_matter_intake = animal_requirements.calculate_NASEM_DMI(
        body_weight,
        mature_body_weight,
        days_in_milk,
        lactating,
        net_energy_lactation,
        parity,
        body_condition_score_5,
        NDF_conc,
    )

    assert math.isclose(dry_matter_intake, expected_dry_matter_intake, rel_tol=1e-6)


@pytest.mark.parametrize(
    "body_weight, housing, distance, nutrient_standard, expected_net_energy_activity, should_raise",
    [
        # NRC - Barn, no walking
        (600.0, "Barn", 0.0, "NRC", 0.0, False),
        # NRC - Barn, some walking
        (600.0, "Barn", 1000.0, "NRC", 0.27, False),
        # NRC - Grazing, no walking
        (600.0, "Grazing", 0.0, "NRC", 0.72, False),
        # NRC - Grazing, some walking
        (600.0, "Grazing", 1000.0, "NRC", 0.99, False),
        # NASEM - Barn, no walking
        (600.0, "Barn", 0.0, "NASEM", 0.0, False),
        # NASEM - Barn, some walking
        (600.0, "Barn", 1000.0, "NASEM", 0.21, False),
        # NASEM - Grazing, no walking
        (600.0, "Grazing", 0.0, "NASEM", 0.0, False),
        # NASEM - Grazing, some walking
        (600.0, "Grazing", 1000.0, "NASEM", 441.0, False),
        # NASEM - Neither barn nor grazing
        (600.0, "Other", 1000.0, "NASEM", 0.0, False),
        # Unsupported nutrient standard
        (600.0, "Barn", 0.0, "Unsupported", 0.0, True),
    ],
)
def test_energy_activity_rqmts(
    body_weight: float,
    housing: str,
    distance: float,
    nutrient_standard: str,
    expected_net_energy_activity: float,
    should_raise: bool,
    mocker: MockerFixture,
) -> None:
    animal_requirements = AnimalRequirements()

    Animal.config = {"nutrient_standard": nutrient_standard}

    if should_raise:
        mocker.patch("RUFAS.biophysical.animal.ration.animal_requirements.OutputManager.__init__", return_value=None)
        mock_add_error = mocker.patch("RUFAS.e2e_test_results_handler.OutputManager.add_error")
        with pytest.raises(ValueError):
            animal_requirements.energy_activity_rqmts(body_weight, housing, distance)
            mock_add_error.assert_called_once_with(
                "nutrient_standard_error",
                f"Nutrient Standard {nutrient_standard} not supported",
                {"function": animal_requirements.calc_rqmts},
            )

    else:
        net_energy_activity = animal_requirements.energy_activity_rqmts(body_weight, housing, distance)

        assert math.isclose(net_energy_activity, expected_net_energy_activity, rel_tol=1e-6)
