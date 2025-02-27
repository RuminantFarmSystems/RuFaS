from datetime import datetime

import pytest
from mock.mock import MagicMock, call
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import Breed, Sex
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
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
)
from RUFAS.biophysical.animal.digestive_system.digestive_system import DigestiveSystem
from RUFAS.biophysical.animal.growth.growth import Growth
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.nutrients.nutrients import Nutrients
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.time import Time


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
    assert animal.sold == False
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
            heifer_reproduction_sub_protocol="5dCG2P"
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
            heifer_reproduction_sub_protocol="5dCG2P"
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
            heifer_reproduction_sub_protocol="5dCG2P"
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
            heifer_reproduction_sub_protocol="5dCG2P"
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


@pytest.mark.parametrize("is_pregnant", [True, False])
def test_is_pregnant(is_pregnant: bool, mock_heiferII: Animal) -> None:
    days_in_pregnancy = 10 if is_pregnant else 0
    animal = mock_heiferII
    animal.days_in_pregnancy = days_in_pregnancy

    assert animal.is_pregnant == is_pregnant


@pytest.mark.parametrize("is_milking", [True, False])
def test_is_milking(is_milking: bool, mock_lactating_cow: Animal) -> None:
    days_in_milk = 10 if is_milking else 0
    animal = mock_lactating_cow
    animal.days_in_milk = days_in_milk

    assert animal.is_milking == is_milking


def test_setup_lactation_curve_parameters(mocker: MockerFixture) -> None:
    mock_set_lactation_parameters = mocker.patch(
        "RUFAS.biophysical.animal.milk.lactation_curve.LactationCurve.set_lactation_parameters"
    )
    mock_time = mocker.MagicMock(auto_spec=Time)

    Animal.setup_lactation_curve_parameters(time=mock_time)

    mock_set_lactation_parameters.assert_called_once_with(mock_time)
