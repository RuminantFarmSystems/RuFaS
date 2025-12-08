import sys
from datetime import datetime
from typing import Any

import pytest
from unittest.mock import MagicMock, call, PropertyMock
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Breed, Sex, AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import (
    NewBornCalfValuesTypedDict,
    CalfValuesTypedDict,
    HeiferIValuesTypedDict,
    HeiferIIValuesTypedDict,
    HeiferIIIValuesTypedDict,
    CowValuesTypedDict,
)
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.digestive_system import DigestiveSystemInputs
from RUFAS.biophysical.animal.data_types.growth import GrowthOutputs
from RUFAS.biophysical.animal.data_types.milk_production import (
    MilkProductionInputs,
    MilkProductionOutputs,
    MilkProductionStatistics,
)
from RUFAS.biophysical.animal.data_types.nutrients import NutrientsInputs
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply, NutritionRequirements
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
    CowTAISubProtocol,
    CowPreSynchSubProtocol,
    CowReproductionProtocol,
    CowReSynchSubProtocol,
)
from RUFAS.biophysical.animal.data_types.reproduction import (
    ReproductionOutputs,
    HerdReproductionStatistics,
    AnimalReproductionStatistics,
)
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.calf_ration_manager import CalfRationManager
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard
from RUFAS.rufas_time import RufasTime


def mock_submodule_init(mocker: MockerFixture) -> None:
    mocker.patch("RUFAS.biophysical.animal.growth.growth.Growth", return_value=MagicMock(auto_spec=Growth))

    mocker.patch(
        "RUFAS.biophysical.animal.digestive_system.digestive_system.DigestiveSystem",
        return_value=MagicMock(auto_spec=DigestiveSystem),
    )

    mocker.patch(
        "RUFAS.biophysical.animal.milk.milk_production.MilkProduction", return_value=MagicMock(auto_spec=MilkProduction)
    )

    mocker.patch("RUFAS.biophysical.animal.nutrients.nutrients.Nutrients", return_value=MagicMock(auto_spec=Nutrients))

    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.Reproduction",
        return_value=MagicMock(auto_spec=Reproduction),
    )


def mock_animal_init_methods(mocker: MockerFixture) -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
    mock_initialize_newborn_calf = mocker.patch("RUFAS.biophysical.animal.animal.Animal._initialize_newborn_calf")
    mock_initialize_calf_or_heiferI = mocker.patch("RUFAS.biophysical.animal.animal.Animal._initialize_calf_or_heiferI")
    mock_initialize_heiferII_or_heiferIII = mocker.patch(
        "RUFAS.biophysical.animal.animal.Animal._initialize_heiferII_or_heiferIII"
    )
    mock_initialize_cow = mocker.patch("RUFAS.biophysical.animal.animal.Animal._initialize_cow")
    return (
        mock_initialize_newborn_calf,
        mock_initialize_calf_or_heiferI,
        mock_initialize_heiferII_or_heiferIII,
        mock_initialize_cow,
    )


def assert_animal_init_properties(
    result: Animal,
    args: (
        NewBornCalfValuesTypedDict
        | CalfValuesTypedDict
        | HeiferIValuesTypedDict
        | HeiferIIValuesTypedDict
        | HeiferIIIValuesTypedDict
        | CowValuesTypedDict
    ),
) -> None:
    assert result.id == args["id"]
    assert result.breed == Breed(Breed[args["breed"]])
    assert result.animal_type == AnimalType(args["animal_type"])
    assert result.days_born == args["days_born"]
    assert result.birth_weight == args["birth_weight"]
    assert result.net_merit == args["net_merit"]
    assert result.cull_reason == ""


@pytest.mark.parametrize(
    "args",
    [
        NewBornCalfValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="Calf",
            birth_date="2023-01-01",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            initial_phosphorus=10.0,
        )
    ],
)
def test_init_newborn_calf(args: NewBornCalfValuesTypedDict, mocker: MockerFixture) -> None:
    mock_submodule_init(mocker)

    (
        mock_initialize_newborn_calf,
        mock_initialize_calf_or_heiferI,
        mock_initialize_heiferII_or_heiferIII,
        mock_initialize_cow,
    ) = mock_animal_init_methods(mocker)

    result = Animal(args)

    assert_animal_init_properties(result, args)

    mock_initialize_newborn_calf.assert_called_once()
    mock_initialize_calf_or_heiferI.assert_not_called()
    mock_initialize_heiferII_or_heiferIII.assert_not_called()
    mock_initialize_cow.assert_not_called()


@pytest.mark.parametrize(
    "args, semen_type, sex, culled, sold",
    [
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "conventional",
            Sex.FEMALE,
            False,
            False,
        ),
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "sexed",
            Sex.FEMALE,
            False,
            False,
        ),
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "conventional",
            Sex.MALE,
            False,
            True,
        ),
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "sexed",
            Sex.MALE,
            False,
            True,
        ),
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "random",
            Sex.MALE,
            False,
            True,
        ),
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "conventional",
            Sex.FEMALE,
            True,
            False,
        ),
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "sexed",
            Sex.FEMALE,
            True,
            False,
        ),
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "conventional",
            Sex.MALE,
            True,
            True,
        ),
        (
            NewBornCalfValuesTypedDict(
                id=1,
                breed="HO",
                animal_type="Calf",
                birth_date="2023-01-01",
                days_born=10,
                birth_weight=10.0,
                net_merit=10.0,
                initial_phosphorus=10.0,
            ),
            "sexed",
            Sex.MALE,
            True,
            True,
        ),
    ],
)
def test_initialize_newborn_calf(
    args: NewBornCalfValuesTypedDict, semen_type: str, sex: Sex, culled: bool, sold: bool, mocker: MockerFixture
) -> None:
    original_semen_type = AnimalConfig.semen_type
    AnimalConfig.semen_type = semen_type

    if not (semen_type in ["conventional", "sexed"]):
        with pytest.raises(ValueError):
            Animal(args)
        return
    male_calf_rate = (
        AnimalConfig.male_calf_rate_conventional_semen
        if semen_type == "conventional"
        else AnimalConfig.male_calf_rate_sexed_semen
    )

    sex_random_value = male_calf_rate + 0.01 if sex == Sex.FEMALE else male_calf_rate - 0.01
    culled_random_value = AnimalConfig.still_birth_rate - 0.01 if culled else AnimalConfig.still_birth_rate + 0.01
    sold_random_value = AnimalConfig.keep_female_calf_rate + 0.01 if sold else AnimalConfig.keep_female_calf_rate - 0.01

    mocker.patch(
        "RUFAS.biophysical.animal.animal.random", side_effect=[sex_random_value, culled_random_value, sold_random_value]
    )
    mock_rvs = mocker.patch("RUFAS.biophysical.animal.animal.truncnorm.rvs", return_value=600)

    animal = Animal(args)
    assert animal.sex == sex
    assert animal.sold == sold
    assert animal.birth_weight == args["birth_weight"]
    assert animal.body_weight == args["birth_weight"]
    assert animal.wean_weight == 0.0
    assert animal.mature_body_weight == 600
    assert animal.nutrients.total_phosphorus_in_animal == args["initial_phosphorus"]
    mock_rvs.assert_called_once_with(
        -animal_constants.STDI,
        animal_constants.STDI,
        AnimalConfig.average_mature_body_weight,
        AnimalConfig.std_mature_body_weight,
    )

    AnimalConfig.semen_type = original_semen_type


@pytest.mark.parametrize(
    "args",
    [
        CalfValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="Calf",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
        )
    ],
)
def test_init_calf(args: CalfValuesTypedDict, mocker: MockerFixture) -> None:
    mock_submodule_init(mocker)

    (
        mock_initialize_newborn_calf,
        mock_initialize_calf_or_heiferI,
        mock_initialize_heiferII_or_heiferIII,
        mock_initialize_cow,
    ) = mock_animal_init_methods(mocker)

    result = Animal(args)

    assert_animal_init_properties(result, args)

    mock_initialize_newborn_calf.assert_not_called()
    mock_initialize_calf_or_heiferI.assert_called_once()
    mock_initialize_heiferII_or_heiferIII.assert_not_called()
    mock_initialize_cow.assert_not_called()


@pytest.mark.parametrize(
    "args",
    [
        HeiferIValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="HeiferI",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
        )
    ],
)
def test_init_heiferI(args: HeiferIValuesTypedDict, mocker: MockerFixture) -> None:
    mock_submodule_init(mocker)

    (
        mock_initialize_newborn_calf,
        mock_initialize_calf_or_heiferI,
        mock_initialize_heiferII_or_heiferIII,
        mock_initialize_cow,
    ) = mock_animal_init_methods(mocker)

    result = Animal(args)

    assert_animal_init_properties(result, args)

    mock_initialize_newborn_calf.assert_not_called()
    mock_initialize_calf_or_heiferI.assert_called_once()
    mock_initialize_heiferII_or_heiferIII.assert_not_called()
    mock_initialize_cow.assert_not_called()


@pytest.mark.parametrize(
    "args",
    [
        CalfValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="Calf",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
        ),
        HeiferIValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="HeiferI",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
        ),
    ],
)
def test_initialize_calf_or_heiferI(args: CalfValuesTypedDict | HeiferIValuesTypedDict, mocker: MockerFixture) -> None:
    mock_init_events_from_string = mocker.patch(
        "RUFAS.biophysical.animal.data_types.animal_events.AnimalEvents.init_from_string"
    )

    animal = Animal(args)
    assert animal.sex == Sex.FEMALE
    assert animal.sold is False
    assert animal.birth_weight == args["birth_weight"]
    assert animal.body_weight == args["body_weight"]
    assert animal.wean_weight == args["wean_weight"]
    assert animal.mature_body_weight == args["mature_body_weight"]
    mock_init_events_from_string.assert_called_once_with(args["events"])


@pytest.mark.parametrize(
    "args",
    [
        HeiferIIValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="HeiferII",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
        )
    ],
)
def test_init_heiferII(args: HeiferIIValuesTypedDict, mocker: MockerFixture) -> None:
    mock_submodule_init(mocker)

    (
        mock_initialize_newborn_calf,
        mock_initialize_calf_or_heiferI,
        mock_initialize_heiferII_or_heiferIII,
        mock_initialize_cow,
    ) = mock_animal_init_methods(mocker)

    result = Animal(args)

    assert_animal_init_properties(result, args)

    mock_initialize_newborn_calf.assert_not_called()
    mock_initialize_calf_or_heiferI.assert_not_called()
    mock_initialize_heiferII_or_heiferIII.assert_called_once()
    mock_initialize_cow.assert_not_called()


@pytest.mark.parametrize(
    "args",
    [
        HeiferIIIValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="HeiferII",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
        )
    ],
)
def test_init_heiferIII(args: HeiferIIIValuesTypedDict, mocker: MockerFixture) -> None:
    mock_submodule_init(mocker)

    (
        mock_initialize_newborn_calf,
        mock_initialize_calf_or_heiferI,
        mock_initialize_heiferII_or_heiferIII,
        mock_initialize_cow,
    ) = mock_animal_init_methods(mocker)

    result = Animal(args)

    assert_animal_init_properties(result, args)

    mock_initialize_newborn_calf.assert_not_called()
    mock_initialize_calf_or_heiferI.assert_not_called()
    mock_initialize_heiferII_or_heiferIII.assert_called_once()
    mock_initialize_cow.assert_not_called()


@pytest.mark.parametrize(
    "args",
    [
        HeiferIIValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="HeiferII",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
        ),
        HeiferIIIValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="HeiferIII",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
        ),
        HeiferIIValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="HeiferII",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            days_in_pregnancy=10,
        ),
        HeiferIIIValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="HeiferIII",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            phosphorus_for_gestation_required_for_calf=23.3,
        ),
    ],
)
def test_initialize_heiferII_or_heiferIII(
    args: HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict, mocker: MockerFixture
) -> None:
    mock_init_events_from_string = mocker.patch(
        "RUFAS.biophysical.animal.data_types.animal_events.AnimalEvents.init_from_string"
    )
    mock_reproduction_init = mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.Reproduction.__init__", return_value=None
    )

    expected_days_in_pregnancy = args.get("days_in_pregnancy", 0)
    expected_p_calf = args.get("phosphorus_for_gestation_required_for_calf", 0)
    expected_repro_sub_program = (
        HeiferTAISubProtocol(args["heifer_reproduction_sub_protocol"])
        if args["heifer_reproduction_program"] == "TAI"
        else HeiferSynchEDSubProtocol(args["heifer_reproduction_sub_protocol"])
    )

    animal = Animal(args)

    assert animal.days_in_pregnancy == expected_days_in_pregnancy
    assert animal.nutrients.phosphorus_for_gestation_required_for_calf == expected_p_calf

    mock_init_events_from_string.assert_called_once_with(args["events"])
    assert mock_reproduction_init.call_args_list == [
        call(),
        call(
            heifer_reproduction_program=HeiferReproductionProtocol(args["heifer_reproduction_program"]),
            heifer_reproduction_sub_program=expected_repro_sub_program,
            ai_day=args.get("ai_day", 0),
            estrus_count=args.get("estrus_count", 0),
            estrus_day=args.get("estrus_day", 0),
            abortion_day=args.get("abortion_day", 0),
            conception_rate=args.get("conception_rate", 0),
            gestation_length=args.get("gestation_length", 0),
            calf_birth_weight=args.get("calf_birth_weight", 0),
        ),
    ]


@pytest.mark.parametrize(
    "args",
    [
        CowValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="DryCow",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            cow_reproduction_program="TAI",
            cow_ovsynch_program="OvSynch 56",
            cow_presynch_program="PreSynch",
            cow_resynch_program="TAIbeforePD",
            calf_birth_weight=15.0,
        ),
        CowValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="LacCow",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            cow_reproduction_program="TAI",
            cow_ovsynch_program="OvSynch 56",
            cow_presynch_program="PreSynch",
            cow_resynch_program="TAIbeforePD",
            calf_birth_weight=15.0,
        ),
    ],
)
def test_init_cow(args: CowValuesTypedDict, mocker: MockerFixture) -> None:
    mock_submodule_init(mocker)

    (
        mock_initialize_newborn_calf,
        mock_initialize_calf_or_heiferI,
        mock_initialize_heiferII_or_heiferIII,
        mock_initialize_cow,
    ) = mock_animal_init_methods(mocker)

    result = Animal(args)

    assert_animal_init_properties(result, args)

    mock_initialize_newborn_calf.assert_not_called()
    mock_initialize_calf_or_heiferI.assert_not_called()
    mock_initialize_heiferII_or_heiferIII.assert_not_called()
    mock_initialize_cow.assert_called_once()


@pytest.mark.parametrize(
    "args",
    [
        CowValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="DryCow",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            cow_reproduction_program="TAI",
            cow_ovsynch_program="OvSynch 56",
            cow_presynch_program="PreSynch",
            cow_resynch_program="TAIbeforePD",
            calf_birth_weight=15.0,
        ),
        CowValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="LacCow",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            cow_reproduction_program="TAI",
            cow_ovsynch_program="OvSynch 56",
            cow_presynch_program="PreSynch",
            cow_resynch_program="TAIbeforePD",
            calf_birth_weight=15.0,
        ),
        CowValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="DryCow",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            cow_reproduction_program="TAI",
            cow_ovsynch_program="OvSynch 56",
            cow_presynch_program="PreSynch",
            cow_resynch_program="TAIbeforePD",
            calf_birth_weight=15.0,
        ),
        CowValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="LacCow",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            cow_reproduction_program="TAI",
            cow_ovsynch_program="OvSynch 56",
            cow_presynch_program="PreSynch",
            cow_resynch_program="TAIbeforePD",
            calf_birth_weight=15.0,
            days_in_milk=10,
        ),
        CowValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="DryCow",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            cow_reproduction_program="TAI",
            cow_ovsynch_program="OvSynch 56",
            cow_presynch_program="PreSynch",
            cow_resynch_program="TAIbeforePD",
            calf_birth_weight=15.0,
            parity=3,
        ),
        CowValuesTypedDict(
            id=1,
            breed="HO",
            animal_type="LacCow",
            days_born=10,
            birth_weight=10.0,
            net_merit=10.0,
            mature_body_weight=10.0,
            body_weight=12.3,
            wean_weight=10.0,
            events="",
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            cow_reproduction_program="TAI",
            cow_ovsynch_program="OvSynch 56",
            cow_presynch_program="PreSynch",
            cow_resynch_program="TAIbeforePD",
            calf_birth_weight=15.0,
            calving_interval=45,
        ),
    ],
)
def test_initialize_cow(args: HeiferIIValuesTypedDict | HeiferIIIValuesTypedDict, mocker: MockerFixture) -> None:
    mock_init_events_from_string = mocker.patch(
        "RUFAS.biophysical.animal.data_types.animal_events.AnimalEvents.init_from_string"
    )
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.Reproduction.__init__", return_value=None)
    mocker.patch("RUFAS.biophysical.animal.milk.lactation_curve.LactationCurve.get_wood_parameters")

    expected_days_in_milk = args.get("days_in_milk", 0)
    expected_calves = args.get("parity", 0)
    expected_calving_interval = args.get("calving_interval", AnimalConfig.calving_interval)

    animal = Animal(args)

    assert animal.days_in_milk == expected_days_in_milk
    assert animal.reproduction.calves == expected_calves
    assert animal.reproduction.calving_interval == expected_calving_interval

    mock_init_events_from_string.assert_called_once_with(args["events"])


@pytest.fixture
def mock_calf() -> Animal:
    args = CalfValuesTypedDict(
        id=1,
        breed="HO",
        animal_type="Calf",
        days_born=10,
        birth_weight=10.0,
        net_merit=10.0,
        mature_body_weight=10.0,
        body_weight=12.3,
        wean_weight=10.0,
        events="",
    )
    return Animal(args)


@pytest.fixture
def mock_heiferI() -> Animal:
    args = HeiferIValuesTypedDict(
        id=1,
        breed="HO",
        animal_type="HeiferI",
        days_born=10,
        birth_weight=10.0,
        net_merit=10.0,
        mature_body_weight=10.0,
        body_weight=12.3,
        wean_weight=10.0,
        events="",
    )
    return Animal(args)


@pytest.fixture
def mock_heiferII(mocker: MockerFixture) -> Animal:
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.Reproduction.__init__", return_value=None)
    args = HeiferIIValuesTypedDict(
        id=1,
        breed="HO",
        animal_type="HeiferII",
        days_born=10,
        birth_weight=10.0,
        net_merit=10.0,
        mature_body_weight=10.0,
        body_weight=12.3,
        wean_weight=10.0,
        events="",
        heifer_reproduction_program="TAI",
        heifer_reproduction_sub_protocol="5dCG2P",
        days_in_pregnancy=10,
    )
    return Animal(args)


@pytest.fixture
def mock_heiferIII(mocker: MockerFixture) -> Animal:
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.Reproduction.__init__", return_value=None)
    args = HeiferIIIValuesTypedDict(
        id=1,
        breed="HO",
        animal_type="HeiferIII",
        days_born=10,
        birth_weight=10.0,
        net_merit=10.0,
        mature_body_weight=10.0,
        body_weight=12.3,
        wean_weight=10.0,
        events="",
        heifer_reproduction_program="TAI",
        heifer_reproduction_sub_protocol="5dCG2P",
        days_in_pregnancy=10,
    )
    return Animal(args)


@pytest.fixture
def mock_lactating_cow(mocker: MockerFixture) -> Animal:
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.Reproduction.__init__", return_value=None)
    args = CowValuesTypedDict(
        id=1,
        breed="HO",
        animal_type="LacCow",
        days_born=10,
        birth_weight=10.0,
        net_merit=10.0,
        mature_body_weight=10.0,
        body_weight=12.3,
        wean_weight=10.0,
        events="",
        heifer_reproduction_program="TAI",
        heifer_reproduction_sub_protocol="5dCG2P",
        cow_reproduction_program="TAI",
        cow_ovsynch_program="OvSynch 56",
        cow_presynch_program="PreSynch",
        cow_resynch_program="TAIbeforePD",
        calf_birth_weight=15.0,
        days_in_milk=10,
    )
    return Animal(args)


@pytest.fixture
def mock_dry_cow(mocker: MockerFixture) -> Animal:
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.Reproduction.__init__", return_value=None)
    args = CowValuesTypedDict(
        id=1,
        breed="HO",
        animal_type="DryCow",
        days_born=10,
        birth_weight=10.0,
        net_merit=10.0,
        mature_body_weight=10.0,
        body_weight=12.3,
        wean_weight=10.0,
        events="",
        heifer_reproduction_program="TAI",
        heifer_reproduction_sub_protocol="5dCG2P",
        cow_reproduction_program="TAI",
        cow_ovsynch_program="OvSynch 56",
        cow_presynch_program="PreSynch",
        cow_resynch_program="TAIbeforePD",
        calf_birth_weight=15.0,
        parity=3,
    )
    return Animal(args)


def test_setup_lactation_curve_parameters(mocker: MockerFixture) -> None:
    mock_set_lactation_parameters = mocker.patch(
        "RUFAS.biophysical.animal.milk.lactation_curve.LactationCurve.set_lactation_parameters"
    )
    mock_time = mocker.MagicMock(auto_spec=RufasTime)

    Animal.setup_lactation_curve_parameters(time=mock_time)

    mock_set_lactation_parameters.assert_called_once_with(mock_time)


@pytest.mark.parametrize("is_cow", [True, False])
def test_days_in_milk(is_cow: bool, mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    expected_days_in_milk = 10 if is_cow else 0
    animal = mock_lactating_cow
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    assert animal.days_in_milk == expected_days_in_milk


@pytest.mark.parametrize("is_cow", [True, False])
def test_days_in_milk_setter(is_cow: bool, mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    expected_days_in_milk = 10 if is_cow else 0
    animal = mock_lactating_cow
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    animal.days_in_milk = 10
    assert animal.days_in_milk == expected_days_in_milk


@pytest.mark.parametrize(
    "animal_type, expected_days",
    [
        (AnimalType.CALF, 0),
        (AnimalType.HEIFER_I, 0),
        (AnimalType.LAC_COW, 15),
    ],
)
def test_days_in_pregnancy(animal_type: AnimalType, expected_days: int, mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    animal._days_in_pregnancy = 15
    animal.animal_type = animal_type
    assert mock_lactating_cow.days_in_pregnancy == expected_days


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_days_in_pregnancy_setter(animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    animal._days_in_pregnancy = 15
    animal.animal_type = animal_type
    if setter_allowed:
        mock_lactating_cow.days_in_pregnancy = 25
        assert mock_lactating_cow._days_in_pregnancy == 25
        assert mock_lactating_cow.days_in_pregnancy == 25
    else:
        with pytest.raises(TypeError):
            mock_lactating_cow.days_in_pregnancy = 25


@pytest.mark.parametrize(
    "animal_type, days_in_pregnancy, expected",
    [
        (AnimalType.CALF, 10, False),
        (AnimalType.HEIFER_I, 5, False),
        (AnimalType.LAC_COW, 0, False),
        (AnimalType.LAC_COW, 15, True),
    ],
)
def test_is_pregnant(
    animal_type: AnimalType, days_in_pregnancy: int, expected: bool, mock_lactating_cow: Animal
) -> None:
    animal = mock_lactating_cow
    animal.animal_type = animal_type
    animal._days_in_pregnancy = days_in_pregnancy
    assert animal.is_pregnant == expected


@pytest.mark.parametrize(
    "is_cow, days_in_milk, expected",
    [
        (False, 0, False),
        (False, 10, False),
        (True, 0, False),
        (True, 5, True),
    ],
)
def test_is_milking(
    is_cow: bool, days_in_milk: int, expected: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    animal = mock_lactating_cow
    animal._days_in_milk = days_in_milk
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    assert animal.is_milking == expected


@pytest.mark.parametrize(
    "is_cow, future_cull_value, expected",
    [
        (False, 1000, sys.maxsize),
        (True, 1000, 1000),
    ],
)
def test_future_cull_date(
    is_cow: bool, future_cull_value: int, expected: int, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    animal = mock_lactating_cow
    animal._future_cull_date = future_cull_value
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    assert animal.future_cull_date == expected


@pytest.mark.parametrize(
    "is_cow, setter_allowed",
    [
        (False, False),
        (True, True),
    ],
)
def test_future_cull_date_setter(
    is_cow: bool, setter_allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    animal = mock_lactating_cow
    animal._future_cull_date = 999
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if setter_allowed:
        animal.future_cull_date = 2000
        assert animal._future_cull_date == 2000
        assert animal.future_cull_date == 2000
    else:
        with pytest.raises(TypeError):
            animal.future_cull_date = 2000


@pytest.mark.parametrize(
    "is_cow, future_death_value, expected",
    [
        (False, 1000, sys.maxsize),
        (True, 1000, 1000),
    ],
)
def test_future_death_date(
    is_cow: bool, future_death_value: int, expected: int, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    animal = mock_lactating_cow
    animal._future_death_date = future_death_value
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    assert animal.future_death_date == expected


@pytest.mark.parametrize(
    "is_cow, setter_allowed",
    [
        (False, False),
        (True, True),
    ],
)
def test_future_death_date_setter(
    is_cow: bool, setter_allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    animal = mock_lactating_cow
    animal._future_death_date = 999
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if setter_allowed:
        animal.future_death_date = 2000
        assert animal._future_death_date == 2000
        assert animal.future_death_date == 2000
    else:
        with pytest.raises(TypeError):
            animal.future_death_date = 2000


@pytest.mark.parametrize(
    "is_cow, daily_distance, expected",
    [
        (True, 5.5, 5.5),
    ],
)
def test_daily_horizontal_distance_success(
    is_cow: bool, daily_distance: float, expected: float, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    animal = mock_lactating_cow
    animal._daily_horizontal_distance = daily_distance
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    assert animal.daily_horizontal_distance == expected


def test_daily_horizontal_distance_typeerror(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal._daily_horizontal_distance = 5.5
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=False)
    with pytest.raises(TypeError):
        _ = animal.daily_horizontal_distance


@pytest.mark.parametrize(
    "is_cow, setter_allowed, new_distance, expected",
    [
        (True, True, 10.5, 10.5),
        (False, False, 10.5, None),
    ],
)
def test_daily_horizontal_distance_setter(
    is_cow: bool,
    setter_allowed: bool,
    new_distance: float,
    expected: float,
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
) -> None:
    animal = mock_lactating_cow
    animal._daily_horizontal_distance = 5.5
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if setter_allowed:
        animal.daily_horizontal_distance = new_distance
        assert animal._daily_horizontal_distance == expected
        assert animal.daily_horizontal_distance == expected
    else:
        with pytest.raises(TypeError):
            animal.daily_horizontal_distance = new_distance


@pytest.mark.parametrize(
    "is_cow, vertical_distance, expected",
    [
        (True, 8.2, 8.2),
    ],
)
def test_daily_vertical_distance_success(
    is_cow: bool, vertical_distance: float, expected: float, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    animal = mock_lactating_cow
    animal._daily_vertical_distance = vertical_distance
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    assert animal.daily_vertical_distance == expected


def test_daily_vertical_distance_typeerror(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal._daily_vertical_distance = 8.2
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=False)
    with pytest.raises(TypeError):
        _ = animal.daily_vertical_distance


@pytest.mark.parametrize(
    "is_cow, setter_allowed, new_distance, expected",
    [
        (True, True, 12.5, 12.5),
        (False, False, 12.5, None),
    ],
)
def test_daily_vertical_distance_setter(
    is_cow: bool,
    setter_allowed: bool,
    new_distance: float,
    expected: float,
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
) -> None:
    animal = mock_lactating_cow
    animal._daily_vertical_distance = 7.0
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if setter_allowed:
        animal.daily_vertical_distance = new_distance
        assert animal._daily_vertical_distance == expected
        assert animal.daily_vertical_distance == expected
    else:
        with pytest.raises(TypeError):
            animal.daily_vertical_distance = new_distance


@pytest.mark.parametrize(
    "is_cow, is_milking_value, stored_distance, expected_distance",
    [
        (True, True, 100.0, 100.0),
        (True, False, 50.0, 50.0),
        (False, True, 80.0, 0.0),
        (False, False, 90.0, 90.0),
    ],
)
def test_daily_distance(
    is_cow: bool,
    is_milking_value: bool,
    stored_distance: float,
    expected_distance: float,
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
) -> None:
    animal = mock_lactating_cow
    animal._daily_distance = stored_distance
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    mocker.patch.object(Animal, "is_milking", new_callable=PropertyMock, return_value=is_milking_value)
    assert animal.daily_distance == expected_distance


@pytest.mark.parametrize(
    "is_cow, setter_allowed, new_distance, expected",
    [
        (True, True, 120.5, 120.5),
        (False, False, 120.5, None),
    ],
)
def test_daily_distance_setter(
    is_cow: bool,
    setter_allowed: bool,
    new_distance: float,
    expected: float,
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
) -> None:
    animal = mock_lactating_cow
    animal._daily_distance = 50.0
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if setter_allowed:
        animal.daily_distance = new_distance
        assert animal._daily_distance == expected
        assert animal.daily_distance == expected
    else:
        with pytest.raises(TypeError):
            animal.daily_distance = new_distance


def test_reproduction_getter(mock_lactating_cow: Animal) -> None:
    reproduction_obj = Reproduction()
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    assert animal.reproduction == reproduction_obj


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_reproduction_setter(animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal) -> None:
    reproduction_obj = Reproduction()
    animal = mock_lactating_cow
    animal.animal_type = animal_type
    if setter_allowed:
        animal.reproduction = reproduction_obj
        assert animal._reproduction == reproduction_obj
        assert animal.reproduction == reproduction_obj
    else:
        with pytest.raises(TypeError):
            animal.reproduction = reproduction_obj


@pytest.mark.parametrize(
    "is_cow, reproduction_calves, expected",
    [
        (True, 3, 3),
        (False, 5, 0),
    ],
)
def test_calves(
    is_cow: bool, reproduction_calves: int, expected: int, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.calves = reproduction_calves
    mock_lactating_cow._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    assert mock_lactating_cow.calves == expected


@pytest.mark.parametrize(
    "is_cow, setter_allowed, new_calves, expected",
    [
        (True, True, 4, 4),
        (False, False, 4, None),
    ],
)
def test_calves_setter(
    is_cow: bool,
    setter_allowed: bool,
    new_calves: int,
    expected: int,
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.calves = 3
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if setter_allowed:
        animal.calves = new_calves
        assert animal.reproduction.calves == expected
    else:
        with pytest.raises(TypeError):
            animal.calves = new_calves


@pytest.mark.parametrize(
    "animal_type, reproduction_calving_interval, expected",
    [
        (AnimalType.CALF, 300, 0),
        (AnimalType.HEIFER_I, 350, 0),
        (AnimalType.LAC_COW, 400, 400),
    ],
)
def test_calving_interval_getter(
    animal_type: AnimalType, reproduction_calving_interval: int, expected: int, mock_lactating_cow: Animal
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.calving_interval = reproduction_calving_interval
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    assert animal.calving_interval == expected


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_calving_interval_setter(animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.calving_interval = 300
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    if setter_allowed:
        animal.calving_interval = 450
        assert animal.reproduction.calving_interval == 450
        assert animal.calving_interval == 450
    else:
        with pytest.raises(TypeError):
            animal.calving_interval = 450


@pytest.mark.parametrize(
    "animal_type, reproduction_conceptus_weight, expected",
    [
        (AnimalType.CALF, 500.0, 0.0),
        (AnimalType.HEIFER_I, 600.0, 0.0),
        (AnimalType.LAC_COW, 700.0, 700.0),
    ],
)
def test_conceptus_weight_getter(
    animal_type: AnimalType, reproduction_conceptus_weight: float, expected: float, mock_lactating_cow: Animal
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.conceptus_weight = reproduction_conceptus_weight
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    assert animal.conceptus_weight == expected


@pytest.mark.parametrize("new_weight", [750.0, 800.0])
def test_conceptus_weight_setter(new_weight: float, mock_lactating_cow: Animal) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.conceptus_weight = 700.0
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.conceptus_weight = new_weight
    assert animal.reproduction.conceptus_weight == new_weight
    assert animal.conceptus_weight == new_weight


@pytest.mark.parametrize(
    "animal_type, reproduction_gestation, expected",
    [
        (AnimalType.CALF, 280, 0),
        (AnimalType.HEIFER_I, 290, 0),
        (AnimalType.LAC_COW, 300, 300),
    ],
)
def test_gestation_length_getter(
    animal_type: AnimalType, reproduction_gestation: int, expected: int, mock_lactating_cow: Animal
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.gestation_length = reproduction_gestation
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    assert animal.gestation_length == expected


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_gestation_length_setter(animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.gestation_length = 300
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    if setter_allowed:
        animal.gestation_length = 320
        assert animal.reproduction.gestation_length == 320
        assert animal.gestation_length == 320
    else:
        with pytest.raises(TypeError):
            animal.gestation_length = 320


@pytest.mark.parametrize(
    "animal_type, reproduction_birth_weight, expected",
    [
        (AnimalType.CALF, 40.0, 0.0),
        (AnimalType.HEIFER_I, 45.0, 0.0),
        (AnimalType.LAC_COW, 50.0, 50.0),
    ],
)
def test_calf_birth_weight_getter(
    animal_type: AnimalType, reproduction_birth_weight: float, expected: float, mock_lactating_cow: Animal
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.calf_birth_weight = reproduction_birth_weight
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    assert animal.calf_birth_weight == expected


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_calf_birth_weight_setter(animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.calf_birth_weight = 40.0
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    new_weight = 45.0
    if setter_allowed:
        animal.calf_birth_weight = new_weight
        assert animal.reproduction.calf_birth_weight == new_weight
    else:
        with pytest.raises(TypeError):
            animal.calf_birth_weight = new_weight


@pytest.mark.parametrize(
    "is_cow, calving_history, expected",
    [
        (True, [300, 310, 320], [300, 310, 320]),
    ],
)
def test_calving_interval_history_getter_success(
    is_cow: bool, calving_history: list[int], expected: list[int], mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.calving_interval_history = calving_history
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    assert animal.calving_interval_history == expected


@pytest.mark.parametrize("is_cow", [False])
def test_calving_interval_history_getter_type_error(
    is_cow: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.calving_interval_history = [300, 310]
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    with pytest.raises(TypeError):
        _ = animal.calving_interval_history


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_heifer_reproduction_program_getter(
    animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.heifer_reproduction_program = HeiferReproductionProtocol.TAI
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    if setter_allowed:
        assert animal.heifer_reproduction_program == reproduction_obj.heifer_reproduction_program
    else:
        with pytest.raises(TypeError):
            _ = animal.heifer_reproduction_program


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_heifer_reproduction_program_setter(
    animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.heifer_reproduction_program = HeiferReproductionProtocol.TAI
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    new_program = HeiferReproductionProtocol.TAI
    if setter_allowed:
        animal.heifer_reproduction_program = new_program
        assert animal.reproduction.heifer_reproduction_program == new_program
    else:
        with pytest.raises(TypeError):
            animal.heifer_reproduction_program = new_program


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_heifer_reproduction_sub_program_getter(
    animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.heifer_reproduction_sub_program = HeiferTAISubProtocol.TAI_5dCG2P
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    if setter_allowed:
        assert animal.heifer_reproduction_sub_program == reproduction_obj.heifer_reproduction_sub_program
    else:
        with pytest.raises(TypeError):
            _ = animal.heifer_reproduction_sub_program


@pytest.mark.parametrize(
    "animal_type, setter_allowed",
    [
        (AnimalType.CALF, False),
        (AnimalType.HEIFER_I, False),
        (AnimalType.LAC_COW, True),
    ],
)
def test_heifer_reproduction_sub_program_setter(
    animal_type: AnimalType, setter_allowed: bool, mock_lactating_cow: Animal
) -> None:
    reproduction_obj = Reproduction()
    reproduction_obj.heifer_reproduction_sub_program = HeiferTAISubProtocol.SynchED_CP
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    animal.animal_type = animal_type
    new_sub_program = HeiferSynchEDSubProtocol.SynchED_2P
    if setter_allowed:
        animal.heifer_reproduction_sub_program = new_sub_program
        assert animal.reproduction.heifer_reproduction_sub_program == new_sub_program
    else:
        with pytest.raises(TypeError):
            animal.heifer_reproduction_sub_program = new_sub_program


@pytest.mark.parametrize(
    "is_cow, allowed",
    [
        (True, True),
        (False, False),
    ],
)
def test_cow_reproduction_program_getter(
    is_cow: bool, allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    cow_program = CowReproductionProtocol.ED
    reproduction_obj.cow_reproduction_program = cow_program
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if allowed:
        assert animal.cow_reproduction_program == cow_program
    else:
        with pytest.raises(TypeError):
            _ = animal.cow_reproduction_program


@pytest.mark.parametrize(
    "is_cow, allowed",
    [
        (True, True),
        (False, False),
    ],
)
def test_cow_reproduction_program_setter(
    is_cow: bool, allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    new_program = CowReproductionProtocol.TAI
    if allowed:
        animal.cow_reproduction_program = new_program
        assert animal.reproduction.cow_reproduction_program == new_program
    else:
        with pytest.raises(TypeError):
            animal.cow_reproduction_program = new_program


@pytest.mark.parametrize(
    "is_cow, allowed",
    [
        (True, True),
        (False, False),
    ],
)
def test_cow_presynch_program_getter(
    is_cow: bool, allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    presynch_program = CowPreSynchSubProtocol.Presynch_PreSynch
    reproduction_obj.cow_presynch_program = presynch_program
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if allowed:
        assert animal.cow_presynch_program == presynch_program
    else:
        with pytest.raises(TypeError):
            _ = animal.cow_presynch_program


@pytest.mark.parametrize(
    "is_cow, allowed",
    [
        (True, True),
        (False, False),
    ],
)
def test_cow_presynch_program_setter(
    is_cow: bool, allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    new_presynch = CowPreSynchSubProtocol.Presynch_PreSynch
    if allowed:
        animal.cow_presynch_program = new_presynch
        assert animal.reproduction.cow_presynch_program == new_presynch
    else:
        with pytest.raises(TypeError):
            animal.cow_presynch_program = new_presynch


@pytest.mark.parametrize(
    "is_cow, allowed",
    [
        (True, True),
        (False, False),
    ],
)
def test_cow_ovsynch_program_getter(
    is_cow: bool, allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    ovsynch_program = CowTAISubProtocol.TAI_OvSynch_56
    reproduction_obj.cow_ovsynch_program = ovsynch_program
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if allowed:
        assert animal.cow_ovsynch_program == ovsynch_program
    else:
        with pytest.raises(TypeError):
            _ = animal.cow_ovsynch_program


@pytest.mark.parametrize(
    "is_cow, allowed",
    [
        (True, True),
        (False, False),
    ],
)
def test_cow_ovsynch_program_setter(
    is_cow: bool, allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    new_ovsynch = CowTAISubProtocol.TAI_OvSynch_48
    if allowed:
        animal.cow_ovsynch_program = new_ovsynch
        assert animal.reproduction.cow_ovsynch_program == new_ovsynch
    else:
        with pytest.raises(TypeError):
            animal.cow_ovsynch_program = new_ovsynch


@pytest.mark.parametrize(
    "is_cow, allowed",
    [
        (True, True),
        (False, False),
    ],
)
def test_cow_resynch_program_getter(
    is_cow: bool, allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    cow_resynch = CowReSynchSubProtocol.Resynch_TAIafterPD
    reproduction_obj.cow_resynch_program = cow_resynch
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    if allowed:
        assert animal.cow_resynch_program == cow_resynch
    else:
        with pytest.raises(TypeError):
            _ = animal.cow_resynch_program


@pytest.mark.parametrize(
    "is_cow, allowed",
    [
        (True, True),
        (False, False),
    ],
)
def test_cow_resynch_program_setter(
    is_cow: bool, allowed: bool, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    reproduction_obj = Reproduction()
    animal = mock_lactating_cow
    animal._reproduction = reproduction_obj
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=is_cow)
    new_program = CowReSynchSubProtocol.Resynch_TAIafterPD
    if allowed:
        animal.cow_resynch_program = new_program
        assert animal.reproduction.cow_resynch_program == new_program
    else:
        with pytest.raises(TypeError):
            animal.cow_resynch_program = new_program


@pytest.mark.parametrize(
    "sold_at_day, expected",
    [
        (None, False),
        (-1, False),
        (0, True),
        (10, True),
    ],
)
def test_sold_property(sold_at_day: int | None, expected: bool, mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    animal.sold_at_day = sold_at_day
    assert animal.sold == expected


@pytest.mark.parametrize(
    "stillborn_at_day, expected",
    [
        (None, False),
        (-1, False),
        (0, True),
        (10, True),
    ],
)
def test_stillborn_property(stillborn_at_day: int | None, expected: bool, mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    animal.stillborn_day = stillborn_at_day
    assert animal.stillborn == expected


@pytest.mark.parametrize(
    "dead_at_day, expected",
    [
        (None, False),
        (-1, False),
        (0, True),
        (20, True),
    ],
)
def test_dead_property(dead_at_day: int | None, expected: bool, mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    animal.dead_at_day = dead_at_day
    assert animal.dead == expected


def test_milk_statistics_raises_for_non_cow(mock_calf: Animal) -> None:
    """milk_statistics should raise TypeError when called on a non-cow animal."""
    with pytest.raises(TypeError):
        _ = mock_calf.milk_statistics


def test_milk_statistics_returns_expected_values_for_cow(mock_lactating_cow: Animal) -> None:
    """milk_statistics should return a correctly populated MilkProductionStatistics for cows."""
    cow = mock_lactating_cow

    cow.id = 123
    cow.days_in_milk = 42
    cow.calves = 3
    cow.pen_history = [{"pen": 1, "start_date": 0, "end_date": 100, "animal_types_in_pen": [AnimalType.LAC_COW]}]

    milk_prod = MagicMock()
    milk_prod.daily_milk_produced = 35.5
    milk_prod.true_protein_content = 3.1
    milk_prod.fat_content = 4.0
    milk_prod.lactose_content = 4.8
    cow.milk_production = milk_prod

    stats = cow.milk_statistics

    assert isinstance(stats, MilkProductionStatistics)
    assert stats.cow_id == 123
    assert stats.pen_id == 1
    assert stats.days_in_milk == 42
    assert stats.estimated_daily_milk_produced == 35.5
    assert stats.milk_protein == 3.1
    assert stats.milk_fat == 4.0
    assert stats.milk_lactose == 4.8
    assert stats.parity == 3


def test_daily_nutrients_update(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_perform_daily_phosphorus_update = mocker.patch.object(Nutrients, "perform_daily_phosphorus_update")
    mock_lactating_cow._daily_nutrients_update()

    mock_perform_daily_phosphorus_update.assert_called_once_with(
        NutrientsInputs(
            AnimalType.LAC_COW,
            body_weight=12.3,
            mature_body_weight=10.0,
            daily_growth=0.0,
            days_in_pregnancy=0,
            days_in_milk=10,
            daily_milk_produced=0.0,
        )
    )


def test_daily_digestive_system_update(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_process_digestion = mocker.patch.object(DigestiveSystem, "process_digestion")
    MilkProduction.set_milk_quality(fat_percent=0.0, true_protein_percent=0.0, lactose_percent=0.0)
    mock_lactating_cow._daily_digestive_system_update()
    mock_process_digestion.assert_called_once_with(
        DigestiveSystemInputs(
            AnimalType.LAC_COW,
            body_weight=12.3,
            nutrients=NutritionSupply(
                metabolizable_energy=0.0,
                maintenance_energy=0.0,
                lactation_energy=0.0,
                growth_energy=0.0,
                metabolizable_protein=0.0,
                calcium=0.0,
                phosphorus=0.0,
                dry_matter=10.0,
                wet_matter=0.0,
                ndf_supply=0.0,
                forage_ndf_supply=0.0,
                fat_supply=0.0,
                crude_protein=0.0,
                adf_supply=0.0,
                digestible_energy_supply=0.0,
                tdn_supply=0.0,
                lignin_supply=0.0,
                ash_supply=0.0,
                potassium_supply=0.0,
                starch_supply=0.0,
                byproduct_supply=0.0,
            ),
            days_in_milk=10,
            metabolizable_energy_intake=0.0,
            phosphorus_intake=0.0,
            phosphorus_requirement=0.0,
            phosphorus_reserves=0.0,
            phosphorus_endogenous_loss=0.0,
            daily_milk_produced=0.0,
            fat_content=0.0,
            protein_content=0.0,
        )
    )


def test_daily_milking_update_not_cow(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_perform_daily_milking_update = mocker.patch.object(MilkProduction, "perform_daily_milking_update")
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=False)
    mock_lactating_cow.daily_milking_update(MagicMock(RufasTime))
    mock_perform_daily_milking_update.assert_not_called()


def test_daily_milking_update_is_cow(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    events = AnimalEvents()
    mock_perform_daily_milking_update = mocker.patch.object(
        MilkProduction,
        "perform_daily_milking_update",
        return_value=MilkProductionOutputs(events=events, days_in_milk=0),
    )
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=True)
    mock_time = MagicMock(RufasTime)

    mock_lactating_cow.daily_milking_update(mock_time)

    mock_perform_daily_milking_update.assert_called_once_with(
        MilkProductionInputs(days_in_milk=10, days_born=10, days_in_pregnancy=0), mock_time
    )
    assert mock_lactating_cow._milk_production_output_days_in_milk == 0
    assert mock_lactating_cow.events.events == {}


def test_daily_milking_update_without_history_non_cow_does_nothing(
    mock_calf: Animal,
    mocker: MockerFixture,
) -> None:
    """Non-cow animals should return early and not call the milk_production update."""
    calf = mock_calf

    if hasattr(calf, "_milk_production_output_days_in_milk"):
        delattr(calf, "_milk_production_output_days_in_milk")

    mock_update = mocker.patch.object(
        calf.milk_production,
        "perform_daily_milking_update_without_history",
    )

    calf.daily_milking_update_without_history()

    mock_update.assert_not_called()
    assert not hasattr(calf, "_milk_production_output_days_in_milk")


def test_daily_milking_update_without_history_cow_updates_output(
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
) -> None:
    """For cows, daily_milking_update_without_history should call the milk_production
    update and store the output DIM."""
    cow = mock_lactating_cow
    cow.days_in_milk = 12
    cow.days_born = 34
    cow.days_in_pregnancy = 56

    fake_outputs = MilkProductionOutputs(
        events=MagicMock(spec=AnimalEvents),
        days_in_milk=99,
    )

    mock_update = mocker.patch.object(
        cow.milk_production,
        "perform_daily_milking_update_without_history",
        return_value=fake_outputs,
    )

    cow.daily_milking_update_without_history()

    mock_update.assert_called_once()
    (inputs_arg,) = mock_update.call_args[0]

    assert inputs_arg.days_in_milk == 12
    assert inputs_arg.days_born == 34
    assert inputs_arg.days_in_pregnancy == 56
    assert cow._milk_production_output_days_in_milk == 99


def test_daily_growth_update(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.days_in_pregnancy = 30
    animal.animal_type = AnimalType.LAC_COW
    animal.body_weight = 500
    animal.mature_body_weight = 600
    animal.birth_weight = 50
    animal.days_born = 100
    animal.days_in_milk = 60
    animal.conceptus_weight = 20
    animal.gestation_length = 280
    animal.calf_birth_weight = 45
    animal.calves = 2
    animal.calving_interval = 365
    dummy_time = MagicMock(RufasTime)
    dummy_events = AnimalEvents()
    dummy_outputs = GrowthOutputs(body_weight=510, conceptus_weight=22, events=dummy_events)
    spy = mocker.patch.object(animal.growth, "evaluate_body_weight_change", return_value=dummy_outputs)
    animal.daily_growth_update(dummy_time)
    spy.assert_called_once()
    args, _ = spy.call_args
    inputs_arg = args[0]
    assert inputs_arg.days_in_pregnancy == 30
    assert inputs_arg.animal_type == animal.animal_type
    assert inputs_arg.body_weight == 500
    assert inputs_arg.mature_body_weight == 600
    assert inputs_arg.birth_weight == 50
    assert inputs_arg.days_born == 100
    assert inputs_arg.days_in_milk == 60
    assert inputs_arg.conceptus_weight == 20
    assert inputs_arg.gestation_length == 280
    assert inputs_arg.calf_birth_weight == 45
    assert inputs_arg.calves == 2
    assert inputs_arg.calving_interval == 365
    assert animal.body_weight == dummy_outputs.body_weight
    assert animal.conceptus_weight == dummy_outputs.conceptus_weight


@pytest.mark.parametrize(
    "current_days_in_milk, milk_production_output, reproduction_output, expected",
    [
        (0, 5, 3, 3),
        (10, 8, 1, 8),
        (10, 0, 1, 1),
    ],
)
def test_determine_days_in_milk_valid(
    current_days_in_milk: int,
    milk_production_output: int,
    reproduction_output: int,
    expected: int,
    mock_lactating_cow: Animal,
) -> None:
    animal = mock_lactating_cow
    animal.days_in_milk = current_days_in_milk
    animal._milk_production_output_days_in_milk = milk_production_output
    result = animal._determine_days_in_milk(reproduction_output)
    assert result == expected


@pytest.mark.parametrize(
    "current_days_in_milk, reproduction_output",
    [
        (-1, 1),
        (-5, 0),
    ],
)
def test_determine_days_in_milk_invalid(
    current_days_in_milk: int, reproduction_output: int, mock_lactating_cow: Animal
) -> None:
    animal = mock_lactating_cow
    animal.days_in_milk = current_days_in_milk
    with pytest.raises(ValueError):
        animal._determine_days_in_milk(reproduction_output)


def test_daily_reproduction_update_not_eligible(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_lactating_cow.animal_type = AnimalType.CALF
    result, _ = mock_lactating_cow.daily_reproduction_update(MagicMock(spec=RufasTime))
    assert result is None


def test_daily_reproduction_update_not_cow(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.animal_type = AnimalType.HEIFER_II
    mock_reproduction_update = mocker.patch.object(
        Reproduction,
        "reproduction_update",
        return_value=ReproductionOutputs(
            body_weight=10,
            days_in_milk=11,
            days_in_pregnancy=12,
            events=AnimalEvents(),
            phosphorus_for_gestation_required_for_calf=13,
            herd_reproduction_statistics=HerdReproductionStatistics(),
        ),
    )
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=False)
    result, _ = animal.daily_reproduction_update(MagicMock(RufasTime))

    mock_reproduction_update.assert_called_once()
    assert animal.body_weight == 10
    assert animal.days_in_pregnancy == 12
    assert animal.nutrients.phosphorus_for_gestation_required_for_calf == 13
    assert result is None


def test_daily_reproduction_update(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.animal_type = AnimalType.HEIFER_II
    mock_determine_days_in_milk = mocker.patch.object(animal, "_determine_days_in_milk", return_value=3)
    mock_set_wood_parameters = mocker.patch.object(MilkProduction, "set_wood_parameters")
    mock_determine_future_death_date = mocker.patch.object(animal, "determine_future_death_date", return_value=3)
    mock_determine_future_cull_date = mocker.patch.object(
        animal, "determine_future_cull_date", return_value=(3, "test")
    )
    mock_get_wood_parameters = mocker.patch.object(
        LactationCurve, "get_wood_parameters", return_value={"l": 10.2, "m": 41.2, "n": 41.8}
    )
    mock_reproduction_update = mocker.patch.object(
        Reproduction,
        "reproduction_update",
        return_value=ReproductionOutputs(
            body_weight=10,
            days_in_milk=11,
            days_in_pregnancy=12,
            events=AnimalEvents(),
            phosphorus_for_gestation_required_for_calf=13,
            herd_reproduction_statistics=HerdReproductionStatistics(),
            newborn_calf_config=NewBornCalfValuesTypedDict(
                breed="test_breed",
                animal_type="test_type",
                birth_date="test_bd",
                days_born=5,
                birth_weight=15.3,
                initial_phosphorus=18.4,
                net_merit=75.1,
            ),
        ),
    )
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=True)
    mocker.patch.object(Animal, "calves", new_callable=PropertyMock, return_value=100)
    mocker.patch.object(Animal, "calving_interval_history", new_callable=PropertyMock, return_value=[100])
    mocker.patch.object(AnimalEvents, "get_most_recent_date", return_value=2)
    result, _ = animal.daily_reproduction_update(MagicMock(RufasTime))

    mock_reproduction_update.assert_called_once()
    mock_get_wood_parameters.assert_called_once()
    mock_set_wood_parameters.assert_called_once()
    mock_determine_days_in_milk.assert_called_once()
    mock_determine_future_cull_date.assert_called_once()
    mock_determine_future_death_date.assert_called_once()

    assert animal.future_cull_date == 3
    assert animal.cull_reason == "test"
    assert animal.days_in_milk == 3
    assert animal.body_weight == 10
    assert animal.days_in_pregnancy == 12
    assert animal.nutrients.phosphorus_for_gestation_required_for_calf == 13
    assert result == NewBornCalfValuesTypedDict(
        breed="test_breed",
        animal_type="test_type",
        birth_date="test_bd",
        days_born=5,
        birth_weight=15.3,
        initial_phosphorus=18.4,
        net_merit=75.1,
    )


def test_daily_routines(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.animal_type = AnimalType.HEIFER_III
    mocker.patch.object(Animal, "is_pregnant", new_callable=PropertyMock, return_value=True)
    mock_daily_nutrients_update = mocker.patch.object(animal, "_daily_nutrients_update")
    mock_daily_digestive_system_update = mocker.patch.object(
        animal, "_daily_digestive_system_update", return_value={AnimalType.CALF: {"Pattanaik": 0}}
    )
    mock_daily_milking_update = mocker.patch.object(animal, "daily_milking_update")
    mock_daily_growth_update = mocker.patch.object(animal, "daily_growth_update")
    mock_daily_reproduction_update = mocker.patch.object(
        animal,
        "daily_reproduction_update",
        return_value=(
            NewBornCalfValuesTypedDict(
                breed="test_breed",
                animal_type="test_type",
                birth_date="test_bd",
                days_born=5,
                birth_weight=15.3,
                initial_phosphorus=18.4,
                net_merit=75.1,
            ),
            HerdReproductionStatistics(),
        ),
    )
    mock_animal_life_stage_update = mocker.patch.object(
        animal,
        "animal_life_stage_update",
        return_value=(
            AnimalStatus.LIFE_STAGE_CHANGED,
            NewBornCalfValuesTypedDict(
                breed="test_breed",
                animal_type="test_type",
                birth_date="test_bd",
                days_born=5,
                birth_weight=15.3,
                initial_phosphorus=18.4,
                net_merit=75.1,
            ),
        ),
    )
    result = animal.daily_routines(MagicMock(RufasTime))

    assert animal.days_born == 11
    assert animal.days_in_pregnancy == 1
    mock_daily_growth_update.assert_called_once()
    mock_daily_milking_update.assert_called_once()
    mock_daily_reproduction_update.assert_called_once()
    mock_animal_life_stage_update.assert_called_once()
    mock_daily_nutrients_update.assert_called_once()
    mock_daily_digestive_system_update.assert_called_once()
    assert result == DailyRoutinesOutput(
        animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
        newborn_calf_config=NewBornCalfValuesTypedDict(
            breed="test_breed",
            animal_type="test_type",
            birth_date="test_bd",
            days_born=5,
            birth_weight=15.3,
            initial_phosphorus=18.4,
            net_merit=75.1,
        ),
        herd_reproduction_statistics=HerdReproductionStatistics(),
    )


def test_daily_routines_cow_give_birth(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.animal_type = AnimalType.DRY_COW
    mock_daily_nutrients_update = mocker.patch.object(animal, "_daily_nutrients_update")
    mock_daily_digestive_system_update = mocker.patch.object(
        animal, "_daily_digestive_system_update", return_value={AnimalType.CALF: {"Pattanaik": 0}}
    )
    mock_daily_milking_update = mocker.patch.object(animal, "daily_milking_update")
    mock_daily_growth_update = mocker.patch.object(animal, "daily_growth_update")
    mock_daily_reproduction_update = mocker.patch.object(
        animal,
        "daily_reproduction_update",
        return_value=(
            mock_new_born_calf_config := NewBornCalfValuesTypedDict(
                breed="test_breed",
                animal_type="test_type",
                birth_date="test_bd",
                days_born=5,
                birth_weight=15.3,
                initial_phosphorus=18.4,
                net_merit=75.1,
            ),
            HerdReproductionStatistics(),
        ),
    )
    mock_animal_life_stage_update = mocker.patch.object(
        animal, "animal_life_stage_update", return_value=(AnimalStatus.LIFE_STAGE_CHANGED, None)
    )
    result = animal.daily_routines(MagicMock(RufasTime))

    assert animal.days_born == 11
    mock_daily_growth_update.assert_called_once()
    mock_daily_milking_update.assert_called_once()
    mock_daily_reproduction_update.assert_called_once()
    mock_animal_life_stage_update.assert_called_once()
    mock_daily_nutrients_update.assert_called_once()
    mock_daily_digestive_system_update.assert_called_once()
    assert result == DailyRoutinesOutput(
        animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
        newborn_calf_config=mock_new_born_calf_config,
        herd_reproduction_statistics=HerdReproductionStatistics(),
    )


@pytest.mark.parametrize(
    "expected_status, heifer_evaluation", [(AnimalStatus.LIFE_STAGE_CHANGED, True), (AnimalStatus.REMAIN, False)]
)
def test_calf_life_stage_update(
    mock_lactating_cow: Animal, mocker: MockerFixture, expected_status: AnimalStatus, heifer_evaluation: bool
) -> None:
    animal = mock_lactating_cow
    mock_transition = mocker.patch.object(animal, "_transition_calf_to_heiferI")
    mocker.patch.object(animal, "_evaluate_calf_for_heiferI", return_value=heifer_evaluation)

    result = animal._calf_life_stage_update(MagicMock(RufasTime))

    status, output = result
    assert status == expected_status
    assert output is None
    if heifer_evaluation:
        mock_transition.assert_called_once()
    else:
        mock_transition.assert_not_called()


@pytest.mark.parametrize(
    "expected_status, heifer_evaluation", [(AnimalStatus.LIFE_STAGE_CHANGED, True), (AnimalStatus.REMAIN, False)]
)
def test_heiferI_life_stage_update(
    mock_lactating_cow: Animal, mocker: MockerFixture, expected_status: AnimalStatus, heifer_evaluation: bool
) -> None:
    animal = mock_lactating_cow
    mock_transition = mocker.patch.object(animal, "_transition_heiferI_to_heiferII")
    mocker.patch.object(animal, "_evaluate_heiferI_for_heiferII", return_value=heifer_evaluation)

    status, output = animal._heiferI_life_stage_update(MagicMock(RufasTime))

    assert status == expected_status
    assert output is None
    if heifer_evaluation:
        mock_transition.assert_called_once()
    else:
        mock_transition.assert_not_called()


def test_heiferII_life_stage_update_culling(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    mocker.patch.object(animal, "_evaluate_heiferII_for_culling", return_value=True)

    status, output = animal._heiferII_life_stage_update(MagicMock(RufasTime))

    assert status == AnimalStatus.SOLD
    assert output is None


def test_heiferII_life_stage_update_transition(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    mocker.patch.object(animal, "_evaluate_heiferII_for_culling", return_value=False)
    mocker.patch.object(animal, "_evaluate_heiferII_for_heiferIII", return_value=True)
    mock_transition = mocker.patch.object(animal, "_transition_heiferII_to_heiferIII")

    status, output = animal._heiferII_life_stage_update(MagicMock(RufasTime))

    mock_transition.assert_called_once()
    assert status == AnimalStatus.LIFE_STAGE_CHANGED
    assert output is None


def test_heiferII_life_stage_update_non_culling_or_transition(
    mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    animal = mock_lactating_cow
    mocker.patch.object(animal, "_evaluate_heiferII_for_culling", return_value=False)
    mocker.patch.object(animal, "_evaluate_heiferII_for_heiferIII", return_value=False)
    mock_transition = mocker.patch.object(animal, "_transition_heiferII_to_heiferIII")

    status, output = animal._heiferII_life_stage_update(MagicMock(RufasTime))

    mock_transition.assert_not_called()
    assert status == AnimalStatus.REMAIN
    assert output is None


@pytest.mark.parametrize(
    "expected_status, heifer_evaluation", [(AnimalStatus.LIFE_STAGE_CHANGED, True), (AnimalStatus.REMAIN, False)]
)
def test_heiferIII_life_stage_update(
    mock_lactating_cow: Animal, mocker: MockerFixture, expected_status: AnimalStatus, heifer_evaluation: bool
) -> None:
    animal = mock_lactating_cow
    mocker.patch.object(animal, "evaluate_heiferIII_for_cow", return_value=heifer_evaluation)

    mock_transition = mocker.patch.object(
        animal,
        "transition_heiferIII_to_cow",
        return_value=NewBornCalfValuesTypedDict(
            breed="test_breed",
            animal_type="test_type",
            birth_date="test_bd",
            days_born=5,
            birth_weight=15.3,
            initial_phosphorus=18.4,
            net_merit=75.1,
        ),
    )

    result = animal._heiferIII_life_stage_update(MagicMock(RufasTime))

    status, output = result
    assert status == expected_status
    if heifer_evaluation:
        mock_transition.assert_called_once()
        assert output == NewBornCalfValuesTypedDict(
            breed="test_breed",
            animal_type="test_type",
            birth_date="test_bd",
            days_born=5,
            birth_weight=15.3,
            initial_phosphorus=18.4,
            net_merit=75.1,
        )
    else:
        mock_transition.assert_not_called()
        assert output is None


@pytest.mark.parametrize(
    "animal_type,is_milking,expected_status,expected_type",
    [
        (AnimalType.LAC_COW, False, AnimalStatus.LIFE_STAGE_CHANGED, AnimalType.DRY_COW),
        (AnimalType.DRY_COW, True, AnimalStatus.LIFE_STAGE_CHANGED, AnimalType.LAC_COW),
        (AnimalType.CALF, False, AnimalStatus.REMAIN, AnimalType.CALF),
    ],
)
def test_cow_life_stage_update(
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
    animal_type: AnimalType,
    is_milking: bool,
    expected_status: AnimalStatus,
    expected_type: AnimalType,
) -> None:
    animal = mock_lactating_cow
    animal.animal_type = animal_type
    mocker.patch.object(Animal, "is_milking", new_callable=PropertyMock, return_value=is_milking)

    status, output = animal._cow_life_stage_update(MagicMock(RufasTime))

    assert animal.animal_type == expected_type
    assert status == expected_status
    assert output is None


@pytest.mark.parametrize(
    "future_cull_date,future_death_date,expected_status", [(10, 15, AnimalStatus.SOLD), (15, 10, AnimalStatus.SOLD)]
)
def test_animal_life_stage_update_not_cow(
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
    future_cull_date: int,
    future_death_date: int,
    expected_status: AnimalStatus,
) -> None:
    mock_lactating_cow.animal_type = AnimalType.LAC_COW
    mock_lactating_cow.future_cull_date = future_cull_date
    mock_lactating_cow.future_death_date = future_death_date
    mock_lactating_cow.reproduction.do_not_breed = False
    mocker.patch.object(RufasTime, "simulation_day", new_callable=PropertyMock, return_value=5)
    time = RufasTime(datetime(year=1999, month=1, day=2), datetime(year=2000, month=1, day=1))
    mock_update = mocker.patch.object(
        mock_lactating_cow,
        "_cow_life_stage_update",
        return_value=(
            AnimalStatus.LIFE_STAGE_CHANGED,
            NewBornCalfValuesTypedDict(
                breed="test_breed",
                animal_type="test_type",
                birth_date="test_bd",
                days_born=5,
                birth_weight=15.3,
                initial_phosphorus=18.4,
                net_merit=75.1,
            ),
        ),
    )

    status, output = mock_lactating_cow.animal_life_stage_update(time)

    mock_update.assert_called_once()
    if future_cull_date == 10:
        assert mock_lactating_cow.sold_at_day == 5
        assert status == AnimalStatus.SOLD
    if future_death_date == 10:
        assert mock_lactating_cow.dead_at_day == 5
        assert mock_lactating_cow.cull_reason == animal_constants.DEATH_CULL
        assert status == AnimalStatus.DEAD
    assert output == NewBornCalfValuesTypedDict(
        breed="test_breed",
        animal_type="test_type",
        birth_date="test_bd",
        days_born=5,
        birth_weight=15.3,
        initial_phosphorus=18.4,
        net_merit=75.1,
    )


@pytest.mark.parametrize("future_cull_date,future_death_date,expected_status", [(15, 15, AnimalStatus.SOLD)])
def test_animal_life_stage_update_low_production(
    mock_lactating_cow: Animal,
    mocker: MockerFixture,
    future_cull_date: int,
    future_death_date: int,
    expected_status: AnimalStatus,
) -> None:
    mock_lactating_cow.animal_type = AnimalType.LAC_COW
    mock_lactating_cow.future_cull_date = future_cull_date
    mock_lactating_cow.future_death_date = future_death_date
    mock_lactating_cow.reproduction.do_not_breed = True
    mock_lactating_cow.milk_production.daily_milk_produced = 5
    mocker.patch.object(RufasTime, "simulation_day", new_callable=PropertyMock, return_value=5)
    time = RufasTime(datetime(year=1999, month=1, day=2), datetime(year=2000, month=1, day=1))
    mock_update = mocker.patch.object(
        mock_lactating_cow,
        "_cow_life_stage_update",
        return_value=(
            AnimalStatus.LIFE_STAGE_CHANGED,
            NewBornCalfValuesTypedDict(
                breed="test_breed",
                animal_type="test_type",
                birth_date="test_bd",
                days_born=5,
                birth_weight=15.3,
                initial_phosphorus=18.4,
                net_merit=75.1,
            ),
        ),
    )

    status, output = mock_lactating_cow.animal_life_stage_update(time)

    mock_update.assert_called_once()

    assert mock_lactating_cow.cull_reason == animal_constants.LOW_PROD_CULL
    assert mock_lactating_cow.sold_at_day == 5
    assert status == AnimalStatus.SOLD
    assert output == NewBornCalfValuesTypedDict(
        breed="test_breed",
        animal_type="test_type",
        birth_date="test_bd",
        days_born=5,
        birth_weight=15.3,
        initial_phosphorus=18.4,
        net_merit=75.1,
    )


@pytest.mark.parametrize("born_days, expected", [(10, False), (60, True)])
def test_evaluate_calf_for_heiferI(mock_lactating_cow: Animal, born_days: int, expected: bool) -> None:
    mock_lactating_cow.days_born = born_days

    assert mock_lactating_cow._evaluate_calf_for_heiferI() == expected


@pytest.mark.parametrize("born_days, expected", [(10, False), (380, True)])
def test_evaluate_heiferI_for_heiferII(mock_lactating_cow: Animal, born_days: int, expected: bool) -> None:
    mock_lactating_cow.days_born = born_days

    assert mock_lactating_cow._evaluate_heiferI_for_heiferII() == expected


@pytest.mark.parametrize("born_days, expected", [(10, False), (381, True)])
def test_evaluate_heiferII_for_heiferIII(
    mock_lactating_cow: Animal, born_days: int, expected: bool, mocker: MockerFixture
) -> None:
    mock_lactating_cow.days_born = born_days
    mocker.patch.object(Animal, "is_pregnant", new_callable=PropertyMock, return_value=True)
    mocker.patch.object(Animal, "days_in_pregnancy", new_callable=PropertyMock, return_value=10000)
    mocker.patch.object(Animal, "gestation_length", new_callable=PropertyMock, return_value=22)

    assert mock_lactating_cow._evaluate_heiferII_for_heiferIII() == expected


@pytest.mark.parametrize("born_days, expected", [(10, False), (501, True)])
def test_evaluate_heiferII_for_culling(
    mock_lactating_cow: Animal, born_days: int, expected: bool, mocker: MockerFixture
) -> None:
    mock_lactating_cow.days_born = born_days
    mocker.patch.object(Animal, "is_pregnant", new_callable=PropertyMock, return_value=False)
    mocker.patch.object(Animal, "days_in_pregnancy", new_callable=PropertyMock, return_value=10000)
    mocker.patch.object(Animal, "gestation_length", new_callable=PropertyMock, return_value=22)

    assert mock_lactating_cow._evaluate_heiferII_for_culling() == expected


@pytest.mark.parametrize("days_in_pregnancy, expected", [(10, False), (5, True)])
def test_evaluate_heiferIII_for_cow(
    mock_lactating_cow: Animal, days_in_pregnancy: int, expected: bool, mocker: MockerFixture
) -> None:
    mocker.patch.object(Animal, "gestation_length", new_callable=PropertyMock, return_value=5)
    mocker.patch.object(Animal, "days_in_pregnancy", new_callable=PropertyMock, return_value=days_in_pregnancy)

    assert mock_lactating_cow.evaluate_heiferIII_for_cow() == expected


def test_transition_calf_to_heiferI(mock_lactating_cow: Animal) -> None:
    mock_lactating_cow._transition_calf_to_heiferI()
    assert mock_lactating_cow.animal_type == AnimalType.HEIFER_I


def test_transition_heiferI_to_heiferII(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_update = mocker.patch.object(Animal, "daily_reproduction_update")
    mock_time = MagicMock(spec=RufasTime)
    mock_lactating_cow._transition_heiferI_to_heiferII(mock_time)

    assert mock_lactating_cow.animal_type == AnimalType.HEIFER_II
    assert mock_lactating_cow.heifer_reproduction_program == AnimalConfig.heifer_reproduction_program
    assert mock_lactating_cow.heifer_reproduction_sub_program == AnimalConfig.heifer_reproduction_sub_program
    mock_update.assert_called_once_with(mock_time)


def test_transition_heiferII_to_heiferIII(mock_lactating_cow: Animal) -> None:
    mock_lactating_cow._transition_heiferII_to_heiferIII()
    assert mock_lactating_cow.animal_type == AnimalType.HEIFER_III


def test_transition_heiferIII_to_cow(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mocker.patch.object(Animal, "calves", new_callable=PropertyMock, return_value=2)
    mock_time = MagicMock(spec=RufasTime)
    mock_set = mocker.patch.object(MilkProduction, "set_wood_parameters")
    mock_wood_param = mocker.patch.object(
        LactationCurve,
        "get_wood_parameters",
        return_value={
            "l": 1.0,
            "m": 2.0,
            "n": 3.0,
        },
    )
    mock_update = mocker.patch.object(
        Animal,
        "daily_reproduction_update",
        return_value=(
            NewBornCalfValuesTypedDict(
                breed="test_breed",
                animal_type="test_type",
                birth_date="test_bd",
                days_born=5,
                birth_weight=15.3,
                initial_phosphorus=18.4,
                net_merit=75.1,
            ),
            HerdReproductionStatistics(),
        ),
    )

    result = mock_lactating_cow.transition_heiferIII_to_cow(mock_time)
    assert mock_lactating_cow.animal_type == AnimalType.LAC_COW
    assert mock_lactating_cow.cow_reproduction_program == AnimalConfig.cow_reproduction_program
    assert mock_lactating_cow.reproduction.cow_presynch_program == AnimalConfig.cow_presynch_method
    assert mock_lactating_cow.reproduction.cow_ovsynch_program == AnimalConfig.cow_tai_method
    assert mock_lactating_cow.reproduction.cow_resynch_program == AnimalConfig.cow_resynch_method
    assert mock_lactating_cow.calving_interval == AnimalConfig.calving_interval
    mock_wood_param.assert_called_once_with(2)
    mock_update.assert_called_once_with(mock_time)
    mock_set.assert_called_once()
    assert result == NewBornCalfValuesTypedDict(
        breed="test_breed",
        animal_type="test_type",
        birth_date="test_bd",
        days_born=5,
        birth_weight=15.3,
        initial_phosphorus=18.4,
        net_merit=75.1,
    )


def test_transition_heiferIII_to_cow_error(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mocker.patch.object(Animal, "calves", new_callable=PropertyMock, return_value=2)
    mock_time = MagicMock(spec=RufasTime)
    mock_set = mocker.patch.object(MilkProduction, "set_wood_parameters")
    mock_wood_param = mocker.patch.object(
        LactationCurve,
        "get_wood_parameters",
        return_value={
            "l": 1.0,
            "m": 2.0,
            "n": 3.0,
        },
    )
    mock_update = mocker.patch.object(
        Animal, "daily_reproduction_update", return_value=(None, HerdReproductionStatistics())
    )

    try:
        mock_lactating_cow.transition_heiferIII_to_cow(mock_time)
        assert False
    except ValueError:
        assert mock_lactating_cow.animal_type == AnimalType.LAC_COW
        assert mock_lactating_cow.cow_reproduction_program == AnimalConfig.cow_reproduction_program
        assert mock_lactating_cow.reproduction.cow_presynch_program == AnimalConfig.cow_presynch_method
        assert mock_lactating_cow.reproduction.cow_ovsynch_program == AnimalConfig.cow_tai_method
        assert mock_lactating_cow.reproduction.cow_resynch_program == AnimalConfig.cow_resynch_method
        assert mock_lactating_cow.calving_interval == AnimalConfig.calving_interval
        mock_update.assert_called_once_with(mock_time)
        mock_wood_param.assert_not_called()
        mock_set.assert_not_called()


@pytest.mark.parametrize(
    "animal_type, method_name, expected",
    [
        (AnimalType.CALF, "_get_calf_values", {"key": "calf"}),
        (AnimalType.HEIFER_I, "_get_heiferI_values", {"key": "heiferI"}),
        (AnimalType.HEIFER_II, "_get_heiferII_values", {"key": "heiferII"}),
        (AnimalType.HEIFER_III, "_get_heiferIII_values", {"key": "heiferIII"}),
        (AnimalType.DRY_COW, "_get_cow_values", {"key": "cow"}),
        (AnimalType.LAC_COW, "_get_cow_values", {"key": "cow"}),
    ],
)
def test_get_animal_values(
    animal_type: AnimalType, method_name: str, expected: Any, mock_lactating_cow: Animal, mocker: MockerFixture
) -> None:
    setattr(mock_lactating_cow, method_name, lambda: expected)
    mock_lactating_cow.animal_type = animal_type
    result = mock_lactating_cow.get_animal_values()
    assert result == expected


def test_get_calf_values(mock_calf: Animal) -> None:
    expected = CalfValuesTypedDict(
        id=1,
        breed="HO",
        animal_type="Calf",
        days_born=10,
        birth_weight=10.0,
        net_merit=10.0,
        mature_body_weight=10.0,
        body_weight=12.3,
        wean_weight=10.0,
        events="",
    )
    assert mock_calf._get_calf_values() == expected


def test_get_heiferI_values(mock_heiferI: Animal) -> None:
    expected = HeiferIValuesTypedDict(
        id=1,
        breed="HO",
        animal_type="HeiferI",
        days_born=10,
        birth_weight=10.0,
        net_merit=10.0,
        mature_body_weight=10.0,
        body_weight=12.3,
        wean_weight=10.0,
        events="",
    )
    assert mock_heiferI._get_heiferI_values() == expected


def test_get_heiferII_values(mock_heiferII: Animal) -> None:
    mock_heiferII.reproduction.heifer_reproduction_program = HeiferReproductionProtocol.TAI
    mock_heiferII.reproduction.heifer_reproduction_sub_program = HeiferTAISubProtocol.TAI_5dCG2P
    mock_heiferII.reproduction.estrus_day = 1
    mock_heiferII.reproduction.conception_rate = 1
    mock_heiferII.reproduction.ai_day = 1
    mock_heiferII.reproduction.abortion_day = 1
    mock_heiferII.reproduction.gestation_length = 1
    mock_heiferII.reproduction.calf_birth_weight = 1
    mock_heiferII.reproduction.reproduction_statistics = AnimalReproductionStatistics()
    mock_heiferII.reproduction.reproduction_statistics.estrus_count = 0
    mock_heiferII.nutrients.phosphorus_for_gestation_required_for_calf = 1
    expected = HeiferIIValuesTypedDict(
        abortion_day=1,
        ai_day=1,
        animal_type="HeiferII",
        birth_weight=10.0,
        body_weight=12.3,
        breed="HO",
        calf_birth_weight=1,
        conception_rate=1,
        days_born=10,
        days_in_pregnancy=10,
        estrus_count=0,
        estrus_day=1,
        events="",
        gestation_length=1,
        heifer_reproduction_program="TAI",
        heifer_reproduction_sub_protocol="5dCG2P",
        id=1,
        mature_body_weight=10.0,
        net_merit=10.0,
        phosphorus_for_gestation_required_for_calf=1,
        wean_weight=10.0,
    )
    assert mock_heiferII._get_heiferII_values() == expected


def test_get_heiferIII_values(mock_heiferIII: Animal) -> None:
    mock_heiferIII.reproduction.heifer_reproduction_program = HeiferReproductionProtocol.TAI
    mock_heiferIII.reproduction.heifer_reproduction_sub_program = HeiferTAISubProtocol.TAI_5dCG2P
    mock_heiferIII.reproduction.estrus_day = 1
    mock_heiferIII.reproduction.conception_rate = 1
    mock_heiferIII.reproduction.ai_day = 1
    mock_heiferIII.reproduction.abortion_day = 1
    mock_heiferIII.reproduction.gestation_length = 1
    mock_heiferIII.reproduction.calf_birth_weight = 1
    mock_heiferIII.reproduction.reproduction_statistics = AnimalReproductionStatistics()
    mock_heiferIII.reproduction.reproduction_statistics.estrus_count = 0
    mock_heiferIII.nutrients.phosphorus_for_gestation_required_for_calf = 1
    expected = HeiferIIIValuesTypedDict(
        abortion_day=1,
        ai_day=1,
        animal_type="HeiferIII",
        birth_weight=10.0,
        body_weight=12.3,
        breed="HO",
        calf_birth_weight=1,
        conception_rate=1,
        days_born=10,
        days_in_pregnancy=10,
        estrus_count=0,
        estrus_day=1,
        events="",
        gestation_length=1,
        heifer_reproduction_program="TAI",
        heifer_reproduction_sub_protocol="5dCG2P",
        id=1,
        mature_body_weight=10.0,
        net_merit=10.0,
        phosphorus_for_gestation_required_for_calf=1,
        wean_weight=10.0,
    )
    assert mock_heiferIII._get_heiferIII_values() == expected


def test_get_cow_values(mock_lactating_cow: Animal) -> None:
    mock_lactating_cow.reproduction.heifer_reproduction_program = HeiferReproductionProtocol.TAI
    mock_lactating_cow.reproduction.heifer_reproduction_sub_program = HeiferTAISubProtocol.TAI_5dCG2P
    mock_lactating_cow.reproduction.estrus_day = 1
    mock_lactating_cow.reproduction.conception_rate = 1
    mock_lactating_cow.reproduction.ai_day = 1
    mock_lactating_cow.reproduction.abortion_day = 1
    mock_lactating_cow.reproduction.gestation_length = 1
    mock_lactating_cow.reproduction.calf_birth_weight = 1
    mock_lactating_cow.reproduction.reproduction_statistics = AnimalReproductionStatistics()
    mock_lactating_cow.reproduction.reproduction_statistics.estrus_count = 0
    mock_lactating_cow.nutrients.phosphorus_for_gestation_required_for_calf = 1
    expected = CowValuesTypedDict(
        abortion_day=1,
        ai_day=1,
        animal_type="LacCow",
        birth_weight=10.0,
        body_weight=12.3,
        breed="HO",
        calf_birth_weight=1,
        conception_rate=1,
        days_born=10,
        days_in_pregnancy=0,
        estrus_count=0,
        estrus_day=1,
        events="",
        gestation_length=1,
        heifer_reproduction_program="TAI",
        heifer_reproduction_sub_protocol="5dCG2P",
        id=1,
        mature_body_weight=10.0,
        net_merit=10.0,
        phosphorus_for_gestation_required_for_calf=1,
        wean_weight=10.0,
        calving_interval=400,
        cow_ovsynch_program="OvSynch 56",
        cow_presynch_program="PreSynch",
        cow_reproduction_program="TAI",
        cow_resynch_program="TAIbeforePD",
        days_in_milk=10,
        parity=0,
    )
    assert mock_lactating_cow._get_cow_values() == expected


def test_determine_future_death_date_no_death(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.calves = 1
    animal.days_born = 150
    mocker.patch("RUFAS.biophysical.animal.animal.random", return_value=0.95)
    result = animal.determine_future_death_date()
    assert result == sys.maxsize


def test_determine_future_death_date_with_death(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.calves = 5
    animal.days_born = 12
    mocker.patch("RUFAS.biophysical.animal.animal.random", return_value=0.0005)
    result = animal.determine_future_death_date()
    assert result == 12


def patch_random_first_call(mocker: MockerFixture, first_value: float, second_value: float) -> None:
    called = False

    def side_effect() -> float:
        nonlocal called
        if not called:
            called = True
            return first_value
        return second_value

    mocker.patch("RUFAS.biophysical.animal.animal.random", side_effect=side_effect)


def test_determine_future_cull_date_feet_leg(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_lactating_cow.calves = 1
    mock_lactating_cow.days_born = 150
    patch_random_first_call(mocker, 0.05, 0.05)
    result = mock_lactating_cow.determine_future_cull_date()
    assert result == (159, animal_constants.LAMENESS_CULL)


def test_determine_future_cull_date_injury(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_lactating_cow.calves = 6
    mock_lactating_cow.days_born = 150
    patch_random_first_call(mocker, 0.05, 0.25)
    result = mock_lactating_cow.determine_future_cull_date()
    assert result == (186, animal_constants.INJURY_CULL)


def test_determine_future_cull_date_mastitis(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_lactating_cow.calves = 1
    mock_lactating_cow.days_born = 150
    patch_random_first_call(mocker, 0.05, 0.46)
    result = mock_lactating_cow.determine_future_cull_date()
    assert result == (295, animal_constants.MASTITIS_CULL)


def test_determine_future_cull_date_disease(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_lactating_cow.calves = 1
    mock_lactating_cow.days_born = 150
    patch_random_first_call(mocker, 0.05, 0.7)
    result = mock_lactating_cow.determine_future_cull_date()
    assert result == (465, animal_constants.DISEASE_CULL)


def test_determine_future_cull_date_udder(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_lactating_cow.calves = 1
    mock_lactating_cow.days_born = 150
    patch_random_first_call(mocker, 0.05, 0.85)
    result = mock_lactating_cow.determine_future_cull_date()
    assert result == (551, animal_constants.UDDER_CULL)


def test_determine_future_cull_date_unknown(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_lactating_cow.calves = 1
    mock_lactating_cow.days_born = 150
    patch_random_first_call(mocker, 0.05, 0.9)
    result = mock_lactating_cow.determine_future_cull_date()
    assert result == (618, animal_constants.UNKNOWN_CULL)


def test_determine_future_cull_date_no_cull(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    mock_lactating_cow.calves = 1
    mock_lactating_cow.days_born = 150
    mocker.patch("RUFAS.biophysical.animal.animal.random", return_value=0.95)
    result = mock_lactating_cow.determine_future_cull_date()
    assert result == (sys.maxsize, "")


def test_set_nutrient_standard() -> None:
    test_standard = NutrientStandard.NASEM
    Animal.set_nutrient_standard(test_standard)
    assert Animal.nutrient_standard == NutrientStandard.NASEM


def test_set_nutrition_requirements(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    expected_requirements = MagicMock(spec=NutritionRequirements)
    mock_calc = mocker.patch.object(animal, "calculate_nutrition_requirements", return_value=expected_requirements)
    housing = "barn"
    walking_distance = 10.0
    previous_temperature = 20.0
    available_feeds: list[Any] = []
    animal.set_nutrition_requirements(housing, walking_distance, previous_temperature, available_feeds)
    assert animal.nutrition_requirements == expected_requirements
    mock_calc.assert_called_once_with(housing, walking_distance, previous_temperature, available_feeds)


def test_calculate_nutrition_requirements_calf(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.animal_type = AnimalType.CALF
    animal.birth_weight = 30.0
    animal.body_weight = 35.0
    animal.days_born = 10
    animal.mature_body_weight = 100.0
    animal.nutrient_standard = NutrientStandard.NASEM  # standard is irrelevant in the calf branch
    dummy_intake = {"me_intake": 5.0, "dry_matter_intake": 2.0}
    dummy_requirements = {"ne_maint": 1.0, "ne_gain": 0.5}
    expected = NutritionRequirements(
        maintenance_energy=dummy_requirements["ne_maint"],
        growth_energy=dummy_requirements["ne_gain"],
        pregnancy_energy=0.0,
        lactation_energy=0.0,
        metabolizable_protein=dummy_intake["me_intake"],
        calcium=0.0,
        phosphorus=0.0,
        process_based_phosphorus=0.0,
        dry_matter=dummy_intake["dry_matter_intake"],
        activity_energy=0.0,
        essential_amino_acids=EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        ),
    )
    AnimalConfig.wean_length = 5
    mocker.patch.object(CalfRationManager, "calc_intake", return_value=dummy_intake)
    mocker.patch.object(CalfRationManager, "calc_requirements", return_value=dummy_requirements)
    result = animal.calculate_nutrition_requirements("barn", 10.0, 20.0, [])
    assert result == expected


def test_calculate_nutrition_requirements_nasem(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.animal_type = AnimalType.LAC_COW
    animal.body_weight = 500.0
    animal.mature_body_weight = 600.0
    animal.days_in_pregnancy = 30
    animal.days_in_milk = 60
    animal.birth_weight = 50.0
    animal.days_born = 100
    animal.conceptus_weight = 20.0
    animal.calves = 2
    animal.calving_interval = 365
    animal.body_condition_score_5 = 3.0
    animal.growth = type("DummyGrowth", (), {"daily_growth": 1.0})()
    MilkProduction.set_milk_quality(fat_percent=3.5, true_protein_percent=3.0, lactose_percent=4.5)
    milk_prod = MilkProduction()
    milk_prod._daily_milk_produced = 30.0
    milk_prod._milk_production_variance = 0.0
    milk_prod.milk_production_reduction = 0.0

    assert milk_prod.daily_milk_produced == 30.0

    animal.milk_production = milk_prod
    animal.nutrient_standard = NutrientStandard.NASEM
    animal.previous_nutrition_supply = None
    mocker.patch.object(Animal, "is_pregnant", new_callable=PropertyMock, return_value=True)
    mocker.patch.object(Animal, "is_milking", new_callable=PropertyMock, return_value=True)
    AnimalConfig.wean_length = 5
    animal.nutrients.phosphorus_requirement = 100.0
    dummy_requirements = NutritionRequirements(
        maintenance_energy=1,
        growth_energy=2,
        pregnancy_energy=3,
        lactation_energy=4,
        metabolizable_protein=5,
        calcium=6,
        phosphorus=7,
        process_based_phosphorus=8,
        dry_matter=9,
        activity_energy=10,
        essential_amino_acids=EssentialAminoAcidRequirements(
            histidine=0,
            isoleucine=0,
            leucine=0,
            lysine=0,
            methionine=0,
            phenylalanine=0,
            threonine=0,
            thryptophan=0,
            valine=0,
        ),
    )
    mocker.patch.object(NASEMRequirementsCalculator, "calculate_requirements", return_value=dummy_requirements)
    result = animal.calculate_nutrition_requirements("barn", 10.0, 20.0, [])
    assert result == dummy_requirements


def test_calculate_nutrition_requirements_nrc(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    animal.animal_type = AnimalType.LAC_COW
    animal.body_weight = 500.0
    animal.mature_body_weight = 600.0
    animal.days_in_pregnancy = 30
    animal.days_in_milk = 60
    animal.birth_weight = 50.0
    animal.days_born = 100
    animal.conceptus_weight = 20.0
    animal.calves = 2
    animal.calving_interval = 365
    animal.body_condition_score_5 = 3.0
    animal.growth = type("DummyGrowth", (), {"daily_growth": 1.0})()
    MilkProduction.set_milk_quality(fat_percent=3.5, true_protein_percent=3.0, lactose_percent=4.5)
    milk_prod = MilkProduction()
    milk_prod._daily_milk_produced = 30.0
    milk_prod._milk_production_variance = 0.0
    milk_prod.milk_production_reduction = 0.0

    assert milk_prod.daily_milk_produced == 30.0

    animal.milk_production = milk_prod
    animal.nutrient_standard = NutrientStandard.NRC
    supply = MagicMock(spec=NutritionSupply)
    supply.configure_mock(dry_matter=10.0, ndf_supply=5.0, tdn_supply=4.0, metabolizable_energy=20.0)
    animal.previous_nutrition_supply = supply
    mocker.patch.object(Animal, "is_pregnant", new_callable=PropertyMock, return_value=True)
    mocker.patch.object(Animal, "is_milking", new_callable=PropertyMock, return_value=True)
    AnimalConfig.wean_length = 5
    animal.nutrients.phosphorus_requirement = 100.0
    dummy_requirements = NutritionRequirements(
        maintenance_energy=11,
        growth_energy=12,
        pregnancy_energy=13,
        lactation_energy=14,
        metabolizable_protein=15,
        calcium=16,
        phosphorus=17,
        process_based_phosphorus=18,
        dry_matter=19,
        activity_energy=20,
        essential_amino_acids=EssentialAminoAcidRequirements(
            histidine=0,
            isoleucine=0,
            leucine=0,
            lysine=0,
            methionine=0,
            phenylalanine=0,
            threonine=0,
            thryptophan=0,
            valine=0,
        ),
    )
    mocker.patch.object(NRCRequirementsCalculator, "calculate_requirements", return_value=dummy_requirements)
    result = animal.calculate_nutrition_requirements("grazing", 20.0, 25.0, [])
    assert result == dummy_requirements


def test_determine_heifer_reproduction_programs_NA(mock_lactating_cow: Animal) -> None:
    program, sub_program = mock_lactating_cow._determine_heifer_reproduction_programs(
        HeiferIIValuesTypedDict(
            abortion_day=1,
            ai_day=1,
            animal_type="HeiferII",
            birth_weight=10.0,
            body_weight=12.3,
            breed="HO",
            calf_birth_weight=1,
            conception_rate=1,
            days_born=10,
            days_in_pregnancy=10,
            estrus_count=0,
            estrus_day=1,
            events="",
            gestation_length=1,
            heifer_reproduction_program="N/A",
            heifer_reproduction_sub_protocol="5dCG2P",
            id=1,
            mature_body_weight=10.0,
            net_merit=10.0,
            phosphorus_for_gestation_required_for_calf=1,
            wean_weight=10.0,
        )
    )
    assert program is None
    assert sub_program is None


def test_determine_heifer_reproduction_programs_TAI(mock_lactating_cow: Animal) -> None:
    program, sub_program = mock_lactating_cow._determine_heifer_reproduction_programs(
        HeiferIIValuesTypedDict(
            abortion_day=1,
            ai_day=1,
            animal_type="HeiferII",
            birth_weight=10.0,
            body_weight=12.3,
            breed="HO",
            calf_birth_weight=1,
            conception_rate=1,
            days_born=10,
            days_in_pregnancy=10,
            estrus_count=0,
            estrus_day=1,
            events="",
            gestation_length=1,
            heifer_reproduction_program="TAI",
            heifer_reproduction_sub_protocol="5dCG2P",
            id=1,
            mature_body_weight=10.0,
            net_merit=10.0,
            phosphorus_for_gestation_required_for_calf=1,
            wean_weight=10.0,
        )
    )
    assert isinstance(sub_program, HeiferTAISubProtocol)


def test_determine_heifer_reproduction_programs_SynchED(mock_lactating_cow: Animal) -> None:
    program, sub_program = mock_lactating_cow._determine_heifer_reproduction_programs(
        HeiferIIValuesTypedDict(
            abortion_day=1,
            ai_day=1,
            animal_type="HeiferII",
            birth_weight=10.0,
            body_weight=12.3,
            breed="HO",
            calf_birth_weight=1,
            conception_rate=1,
            days_born=10,
            days_in_pregnancy=10,
            estrus_count=0,
            estrus_day=1,
            events="",
            gestation_length=1,
            heifer_reproduction_program="SynchED",
            heifer_reproduction_sub_protocol="CP",
            id=1,
            mature_body_weight=10.0,
            net_merit=10.0,
            phosphorus_for_gestation_required_for_calf=1,
            wean_weight=10.0,
        )
    )
    assert program == HeiferReproductionProtocol.SynchED
    assert isinstance(sub_program, HeiferSynchEDSubProtocol)


def test_reduce_milk_production_success(mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    animal.milk_production.milk_production_reduction = 3.0
    AnimalModuleConstants.MILK_REDUCTION_KG = 1.0
    AnimalConfig.milk_reduction_maximum = 5.0
    result = animal.reduce_milk_production()
    assert result is True
    assert animal.milk_production.milk_production_reduction == 4.0


def test_reduce_milk_production_failure(mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    animal.milk_production.milk_production_reduction = 5.0
    AnimalModuleConstants.MILK_REDUCTION_KG = 1.0
    AnimalConfig.milk_reduction_maximum = 5.0
    result = animal.reduce_milk_production()
    assert result is False
    assert animal.milk_production.milk_production_reduction == 5.0


def test_update_pen_history_new_pen(mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    animal.pen_history = []
    current_pen = 1
    current_day = 100
    types_in_pen = {AnimalType.CALF, AnimalType.LAC_COW}
    animal.update_pen_history(current_pen, current_day, types_in_pen)
    assert len(animal.pen_history) == 1
    record = animal.pen_history[0]
    assert record["start_date"] == current_day
    assert record["end_date"] == current_day
    assert record["pen"] == current_pen
    assert set(record["animal_types_in_pen"]) == types_in_pen


def test_update_pen_history_same_pen(mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    current_pen = 1
    animal.pen_history = [
        {"start_date": 50, "end_date": 50, "pen": current_pen, "animal_types_in_pen": [AnimalType.CALF]}
    ]
    current_day = 100
    new_types = {AnimalType.LAC_COW, AnimalType.CALF}
    animal.update_pen_history(current_pen, current_day, new_types)
    assert len(animal.pen_history) == 1
    record = animal.pen_history[0]
    assert record["end_date"] == current_day
    assert set(record["animal_types_in_pen"]) == new_types


def test_set_daily_walking_distance_success(mock_lactating_cow: Animal) -> None:
    animal = mock_lactating_cow
    AnimalConfig.cow_times_milked_per_day = 3
    animal.set_daily_walking_distance(1.0, 2.0)
    assert animal.daily_vertical_distance == 6.0
    assert animal.daily_horizontal_distance == 12.0
    assert animal.daily_distance == pytest.approx(13.416407865)


def test_set_daily_walking_distance_non_cow(mock_lactating_cow: Animal, mocker: MockerFixture) -> None:
    animal = mock_lactating_cow
    mocker.patch.object(AnimalType, "is_cow", new_callable=PropertyMock, return_value=False)
    with pytest.raises(ValueError):
        animal.set_daily_walking_distance(1.0, 2.0)
