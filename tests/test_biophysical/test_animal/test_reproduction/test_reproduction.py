import math
from datetime import datetime
from typing import Optional, Any
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.preg_check_config import PregnancyCheckConfig
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    HeiferTAISubProtocol,
    CowReproductionProtocol,
    ReproStateEnum,
    CowTAISubProtocol,
    HeiferSynchEDSubProtocol,
    CowPreSynchSubProtocol,
    CowReSynchSubProtocol,
)
from RUFAS.biophysical.animal.data_types.reproduction import (
    ReproductionInputs,
    ReproductionOutputs,
    HerdReproductionStatistics,
    ReproductionDataStream,
)
from RUFAS.biophysical.animal.reproduction.repro_protocol_misc import InternalReproSettings
from RUFAS.biophysical.animal.reproduction.repro_state_manager import ReproStateManager
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction, HEIFER_REPRODUCTION_SUB_PROTOCOLS
from RUFAS.rufas_time import RufasTime


@pytest.fixture
def mock_reproduction() -> Reproduction:
    return Reproduction()


def mock_reproduction_inputs(
    animal_type: AnimalType,
    body_weight: float = 0.0,
    breed: Breed = Breed.HO,
    days_born: int = 0,
    days_in_pregnancy: int = 0,
    days_in_milk: int = 0,
    net_merit: float = 0.0,
    phosphorus_for_gestation_required_for_calf: float = 0.0,
) -> ReproductionInputs:
    return ReproductionInputs(
        animal_type=animal_type,
        body_weight=body_weight,
        breed=breed,
        days_born=days_born,
        days_in_pregnancy=days_in_pregnancy,
        days_in_milk=days_in_milk,
        net_merit=net_merit,
        phosphorus_for_gestation_required_for_calf=phosphorus_for_gestation_required_for_calf,
    )


def mock_reproduction_outputs(
    body_weight: float = 0.0,
    days_in_pregnancy: int = 0,
    days_in_milk: int = 0,
    events: AnimalEvents = AnimalEvents(),
    phosphorus_for_gestation_required_for_calf: float = 0.0,
    newborn_calf_config: NewBornCalfValuesTypedDict | None = None,
) -> ReproductionOutputs:
    return ReproductionOutputs(
        body_weight=body_weight,
        days_in_pregnancy=days_in_pregnancy,
        days_in_milk=days_in_milk,
        events=events,
        phosphorus_for_gestation_required_for_calf=phosphorus_for_gestation_required_for_calf,
        herd_reproduction_statistics=HerdReproductionStatistics(),
        newborn_calf_config=newborn_calf_config,
    )


def mock_reproduction_data_stream(
    animal_type: AnimalType,
    body_weight: float = 0.0,
    breed: Breed = Breed.HO,
    days_born: int = 0,
    days_in_pregnancy: int = 0,
    days_in_milk: int = 0,
    net_merit: float = 0.0,
    phosphorus_for_gestation_required_for_calf: float = 0.0,
    events: AnimalEvents = AnimalEvents(),
    newborn_calf_config: NewBornCalfValuesTypedDict | None = None,
) -> ReproductionDataStream:
    return ReproductionDataStream(
        animal_type=animal_type,
        body_weight=body_weight,
        breed=breed,
        days_born=days_born,
        days_in_pregnancy=days_in_pregnancy,
        days_in_milk=days_in_milk,
        events=events,
        net_merit=net_merit,
        phosphorus_for_gestation_required_for_calf=phosphorus_for_gestation_required_for_calf,
        herd_reproduction_statistics=HerdReproductionStatistics(),
        newborn_calf_config=newborn_calf_config,
    )


@pytest.mark.parametrize(
    "input_config, expected_properties",
    [
        (
            {
                "heifer_reproduction_program": HeiferReproductionProtocol.TAI,
                "heifer_reproduction_sub_program": HeiferTAISubProtocol.TAI_5dCG2P,
                "cow_reproduction_program": CowReproductionProtocol.TAI,
                "cow_presynch_program": CowPreSynchSubProtocol.Presynch_DoubleOvSynch,
                "cow_ovsynch_program": CowTAISubProtocol.TAI_OvSynch_48,
                "cow_resynch_program": CowReSynchSubProtocol.Resynch_TAIbeforePD,
                "ai_day": 0,
                "estrus_day": 0,
                "abortion_day": 0,
                "breeding_to_preg_time": 0,
                "conception_rate": 0.0,
                "cow_TAI_conception_rate": 0.0,
                "num_conception_rate_decreases": 0,
                "gestation_length": 0,
                "conceptus_weight": 0.0,
                "calf_birth_weight": 0.0,
                "calves": 0,
                "calving_interval": 0,
                "body_weight_at_calving": 0.0,
                "estrus_count": 0,
            },
            {
                "heifer_reproduction_program": HeiferReproductionProtocol.TAI,
                "heifer_reproduction_sub_program": HeiferTAISubProtocol.TAI_5dCG2P,
                "cow_reproduction_program": CowReproductionProtocol.TAI,
                "cow_presynch_program": CowPreSynchSubProtocol.Presynch_DoubleOvSynch,
                "cow_ovsynch_program": CowTAISubProtocol.TAI_OvSynch_48,
                "cow_resynch_program": CowReSynchSubProtocol.Resynch_TAIbeforePD,
                "ai_day": 0,
                "estrus_day": 0,
                "abortion_day": 0,
                "breeding_to_preg_time": 0,
                "conception_rate": 0.0,
                "TAI_conception_rate": 0.0,
                "num_conception_rate_decreases": 0,
                "hormone_schedule": {},
                "gestation_length": 0,
                "conceptus_weight": 0.0,
                "calf_birth_weight": 0.0,
                "calves": 0,
                "calving_interval": AnimalConfig.calving_interval,
                "calving_interval_history": [],
                "body_weight_at_calving": 0.0,
                "do_not_breed": False,
                "estrus_count": 0,
            },
        ),
        # 1. All None
        (
            {},
            {
                "heifer_reproduction_program": HeiferReproductionProtocol(AnimalConfig.heifer_reproduction_program),
                "heifer_reproduction_sub_program": AnimalConfig.heifer_reproduction_sub_program,
                "cow_reproduction_program": CowReproductionProtocol(AnimalConfig.cow_reproduction_program),
                "cow_presynch_program": CowPreSynchSubProtocol(AnimalConfig.cow_presynch_method),
                "cow_ovsynch_program": CowTAISubProtocol(AnimalConfig.cow_tai_method),
                "cow_resynch_program": CowReSynchSubProtocol(AnimalConfig.cow_resynch_method),
                "ai_day": 0,
                "estrus_day": 0,
                "abortion_day": 0,
                "breeding_to_preg_time": 0,
                "conception_rate": 0.0,
                "TAI_conception_rate": 0.0,
                "num_conception_rate_decreases": 0,
                "hormone_schedule": {},
                "gestation_length": 0,
                "conceptus_weight": 0.0,
                "calf_birth_weight": 0.0,
                "calves": 0,
                "calving_interval": AnimalConfig.calving_interval,
                "calving_interval_history": [],
                "body_weight_at_calving": 0.0,
                "do_not_breed": False,
                "estrus_count": 0,
            },
        ),
        # 2. Fully custom
        (
            {
                "heifer_reproduction_program": HeiferReproductionProtocol.TAI,
                "heifer_reproduction_sub_program": HeiferSynchEDSubProtocol.SynchED_CP,
                "cow_reproduction_program": CowReproductionProtocol.TAI,
                "cow_presynch_program": CowPreSynchSubProtocol.Presynch_G6G,
                "cow_ovsynch_program": CowTAISubProtocol.TAI_5d_CoSynch,
                "cow_resynch_program": CowReSynchSubProtocol.Resynch_PGFatPD,
                "ai_day": 10,
                "estrus_day": 15,
                "abortion_day": 20,
                "breeding_to_preg_time": 42,
                "conception_rate": 0.35,
                "cow_TAI_conception_rate": 0.22,
                "num_conception_rate_decreases": 2,
                "hormone_schedule": {1: {"GnRH": True}, 2: {"PGF2a": True}},
                "gestation_length": 279,
                "conceptus_weight": 25.0,
                "calf_birth_weight": 40.5,
                "calves": 2,
                "calving_interval": 400,
                "calving_interval_history": [380, 390],
                "body_weight_at_calving": 600.0,
                "do_not_breed": True,
                "estrus_count": 5,
            },
            {
                "heifer_reproduction_program": HeiferReproductionProtocol.TAI,
                "heifer_reproduction_sub_program": HeiferSynchEDSubProtocol.SynchED_CP,
                "cow_reproduction_program": CowReproductionProtocol.TAI,
                "cow_presynch_program": CowPreSynchSubProtocol.Presynch_G6G,
                "cow_ovsynch_program": CowTAISubProtocol.TAI_5d_CoSynch,
                "cow_resynch_program": CowReSynchSubProtocol.Resynch_PGFatPD,
                "ai_day": 10,
                "estrus_day": 15,
                "abortion_day": 20,
                "breeding_to_preg_time": 42,
                "conception_rate": 0.35,
                "TAI_conception_rate": 0.22,
                "num_conception_rate_decreases": 2,
                "hormone_schedule": {1: {"GnRH": True}, 2: {"PGF2a": True}},
                "gestation_length": 279,
                "conceptus_weight": 25.0,
                "calf_birth_weight": 40.5,
                "calves": 2,
                "calving_interval": 400,
                "calving_interval_history": [380, 390],
                "body_weight_at_calving": 600.0,
                "do_not_breed": True,
                "estrus_count": 5,
            },
        ),
        # 3. Partial None/Custom
        (
            {
                "cow_reproduction_program": CowReproductionProtocol.TAI,
                "cow_ovsynch_program": CowTAISubProtocol.TAI_OvSynch_48,
                "ai_day": 5,
                "estrus_day": 0,
                "abortion_day": 0,
                "conception_rate": 0.5,
                "num_conception_rate_decreases": 1,
                "gestation_length": 280,
                "calf_birth_weight": 45.0,
                "calves": 1,
                "calving_interval": 0,
                "calving_interval_history": [365],
                "body_weight_at_calving": 650.0,
                "estrus_count": 2,
            },
            {
                "heifer_reproduction_program": HeiferReproductionProtocol(AnimalConfig.heifer_reproduction_program),
                "heifer_reproduction_sub_program": AnimalConfig.heifer_reproduction_sub_program,
                "cow_reproduction_program": CowReproductionProtocol.TAI,
                "cow_presynch_program": CowPreSynchSubProtocol(AnimalConfig.cow_presynch_method),
                "cow_ovsynch_program": CowTAISubProtocol.TAI_OvSynch_48,
                "cow_resynch_program": CowReSynchSubProtocol(AnimalConfig.cow_resynch_method),
                "ai_day": 5,
                "estrus_day": 0,
                "abortion_day": 0,
                "breeding_to_preg_time": 0,
                "conception_rate": 0.5,
                "TAI_conception_rate": 0.0,
                "num_conception_rate_decreases": 1,
                "hormone_schedule": {},
                "gestation_length": 280,
                "conceptus_weight": 0.0,
                "calf_birth_weight": 45.0,
                "calves": 1,
                "calving_interval": AnimalConfig.calving_interval,
                "calving_interval_history": [365],
                "body_weight_at_calving": 650.0,
                "do_not_breed": False,
                "estrus_count": 2,
            },
        ),
        # 4. Non-empty hormone_schedule and calving_interval_history
        (
            {
                "hormone_schedule": {
                    1: {"GnRH": True, "Notes": "Day 1 injection"},
                    3: {"PGF2a": True, "Notes": "Day 3 injection"},
                },
                "calving_interval_history": [340, 365, 370],
                # fill the rest as you want, or keep them None to test defaults
            },
            {
                "hormone_schedule": {
                    1: {"GnRH": True, "Notes": "Day 1 injection"},
                    3: {"PGF2a": True, "Notes": "Day 3 injection"},
                },
                "calving_interval_history": [340, 365, 370],
                # fill the rest with the expected final states
                "heifer_reproduction_program": HeiferReproductionProtocol(AnimalConfig.heifer_reproduction_program),
                "heifer_reproduction_sub_program": AnimalConfig.heifer_reproduction_sub_program,
                "cow_reproduction_program": CowReproductionProtocol(AnimalConfig.cow_reproduction_program),
                "cow_presynch_program": CowPreSynchSubProtocol(AnimalConfig.cow_presynch_method),
                "cow_ovsynch_program": CowTAISubProtocol(AnimalConfig.cow_tai_method),
                "cow_resynch_program": CowReSynchSubProtocol(AnimalConfig.cow_resynch_method),
                "ai_day": 0,
                "estrus_day": 0,
                "abortion_day": 0,
                "breeding_to_preg_time": 0,
                "conception_rate": 0.0,
                "TAI_conception_rate": 0.0,
                "num_conception_rate_decreases": 0,
                "gestation_length": 0,
                "conceptus_weight": 0.0,
                "calf_birth_weight": 0.0,
                "calves": 0,
                "calving_interval": AnimalConfig.calving_interval,
                "body_weight_at_calving": 0.0,
                "do_not_breed": False,
                "estrus_count": 0,
            },
        ),
    ],
)
def test_reproduction_initialization(input_config: dict[str, Any], expected_properties: dict[str, Any]) -> None:
    reproduction = Reproduction(**input_config)

    assert reproduction.heifer_reproduction_program == expected_properties["heifer_reproduction_program"]
    assert reproduction.heifer_reproduction_sub_program == expected_properties["heifer_reproduction_sub_program"]
    assert reproduction.cow_reproduction_program == expected_properties["cow_reproduction_program"]
    assert reproduction.cow_presynch_program == expected_properties["cow_presynch_program"]
    assert reproduction.cow_ovsynch_program == expected_properties["cow_ovsynch_program"]
    assert reproduction.cow_resynch_program == expected_properties["cow_resynch_program"]
    assert reproduction.ai_day == expected_properties["ai_day"]
    assert reproduction.estrus_day == expected_properties["estrus_day"]
    assert reproduction.abortion_day == expected_properties["abortion_day"]
    assert reproduction.breeding_to_preg_time == expected_properties["breeding_to_preg_time"]
    assert reproduction.gestation_length == expected_properties["gestation_length"]

    assert reproduction.conceptus_weight == expected_properties["conceptus_weight"]
    assert reproduction.calf_birth_weight == expected_properties["calf_birth_weight"]
    assert reproduction.body_weight_at_calving == expected_properties["body_weight_at_calving"]

    assert reproduction.conception_rate == expected_properties["conception_rate"]
    assert reproduction.TAI_conception_rate == expected_properties["TAI_conception_rate"]
    assert reproduction.num_conception_rate_decreases == expected_properties["num_conception_rate_decreases"]

    assert reproduction.calves == expected_properties["calves"]
    assert reproduction.calving_interval == expected_properties["calving_interval"]

    assert reproduction.calving_interval_history == expected_properties["calving_interval_history"]

    assert reproduction.hormone_schedule == expected_properties["hormone_schedule"]

    assert reproduction.do_not_breed == expected_properties["do_not_breed"]

    assert reproduction.reproduction_statistics.estrus_count == expected_properties["estrus_count"]


@pytest.mark.parametrize("animal_type", [AnimalType.HEIFER_II, AnimalType.DRY_COW, AnimalType.LAC_COW])
def test_reproduction_update(animal_type: AnimalType, mock_reproduction: Reproduction, mocker: MockerFixture) -> None:
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 100

    mock_inputs = mock_reproduction_inputs(animal_type=animal_type)

    mock_reproduction_data_stream = ReproductionDataStream(
        animal_type=mock_inputs.animal_type,
        body_weight=mock_inputs.body_weight,
        breed=mock_inputs.breed,
        days_born=mock_inputs.days_born,
        days_in_pregnancy=mock_inputs.days_in_pregnancy,
        days_in_milk=mock_inputs.days_in_milk,
        events=AnimalEvents(),
        net_merit=mock_inputs.net_merit,
        phosphorus_for_gestation_required_for_calf=mock_inputs.phosphorus_for_gestation_required_for_calf,
        herd_reproduction_statistics=HerdReproductionStatistics(),
        newborn_calf_config=None,
    )

    expected_outputs = mock_reproduction_outputs(
        body_weight=mock_inputs.body_weight,
        days_in_milk=mock_inputs.days_in_milk,
        days_in_pregnancy=mock_inputs.days_in_pregnancy,
        events=AnimalEvents(),
        phosphorus_for_gestation_required_for_calf=mock_inputs.phosphorus_for_gestation_required_for_calf,
        newborn_calf_config=None,
    )

    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.ReproductionDataStream",
        return_value=mock_reproduction_data_stream,
    )
    mock_heiferII_reproduction_update = mocker.patch.object(
        mock_reproduction, "heiferII_reproduction_update", return_value=expected_outputs
    )
    mock_cow_reproduction_update = mocker.patch.object(
        mock_reproduction, "cow_reproduction_update", return_value=expected_outputs
    )

    result = mock_reproduction.reproduction_update(mock_inputs, mock_time)

    assert result == expected_outputs

    if animal_type == AnimalType.HEIFER_II:
        mock_heiferII_reproduction_update.assert_called_once_with(mock_reproduction_data_stream, mock_time)
        mock_cow_reproduction_update.assert_not_called()

    if animal_type == AnimalType.LAC_COW or animal_type == AnimalType.DRY_COW:
        mock_heiferII_reproduction_update.assert_not_called()
        mock_cow_reproduction_update.assert_called_once_with(mock_reproduction_data_stream, mock_time)


@pytest.mark.parametrize("animal_type", [AnimalType.CALF, AnimalType.HEIFER_I, AnimalType.HEIFER_III])
def test_reproduction_update_type_error(
    animal_type: AnimalType, mock_reproduction: Reproduction, mocker: MockerFixture
) -> None:
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 100

    mock_inputs = mock_reproduction_inputs(animal_type=animal_type)

    mock_reproduction_data_stream = ReproductionDataStream(
        animal_type=mock_inputs.animal_type,
        body_weight=mock_inputs.body_weight,
        breed=mock_inputs.breed,
        days_born=mock_inputs.days_born,
        days_in_pregnancy=mock_inputs.days_in_pregnancy,
        days_in_milk=mock_inputs.days_in_milk,
        events=AnimalEvents(),
        net_merit=mock_inputs.net_merit,
        phosphorus_for_gestation_required_for_calf=mock_inputs.phosphorus_for_gestation_required_for_calf,
        herd_reproduction_statistics=HerdReproductionStatistics(),
        newborn_calf_config=None,
    )

    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.ReproductionDataStream",
        return_value=mock_reproduction_data_stream,
    )
    mock_heiferII_reproduction_update = mocker.patch.object(mock_reproduction, "heiferII_reproduction_update")
    mock_cow_reproduction_update = mocker.patch.object(mock_reproduction, "cow_reproduction_update")

    with pytest.raises(TypeError):
        mock_reproduction.reproduction_update(mock_inputs, mock_time)

    mock_heiferII_reproduction_update.assert_not_called()
    mock_cow_reproduction_update.assert_not_called()


@pytest.mark.parametrize(
    "days_born, days_in_pregnancy, protocol, ai_day, expect_ai, expect_protocol_call, expect_pregnancy_update",
    [
        # Before breeding start day; no protocols should execute
        (AnimalConfig.heifer_breed_start_day - 1, 0, HeiferReproductionProtocol.ED, 0, False, False, False),
        # On breeding start day, with ED protocol, expect ED protocol execution
        (AnimalConfig.heifer_breed_start_day, 0, HeiferReproductionProtocol.ED, 0, False, True, False),
        # On breeding start day, with TAI protocol, expect TAI protocol execution
        (AnimalConfig.heifer_breed_start_day, 0, HeiferReproductionProtocol.TAI, 0, False, True, False),
        # On breeding start day, with SynchED protocol, expect SynchED protocol execution
        (AnimalConfig.heifer_breed_start_day, 0, HeiferReproductionProtocol.SynchED, 0, False, True, False),
        # After breeding start day, AI day matches days_born; expect AI
        (
            AnimalConfig.heifer_breed_start_day + 1,
            0,
            HeiferReproductionProtocol.ED,
            AnimalConfig.heifer_breed_start_day + 1,
            True,
            True,
            False,
        ),
        # After breeding start day, is pregnant; expect pregnancy update
        (AnimalConfig.heifer_breed_start_day + 1, 10, HeiferReproductionProtocol.ED, 0, False, True, True),
    ],
)
def test_heiferII_reproduction_update_same_method_as_config(
    days_born: int,
    days_in_pregnancy: int,
    protocol: HeiferReproductionProtocol,
    ai_day: int,
    expect_ai: bool,
    expect_protocol_call: bool,
    expect_pregnancy_update: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = protocol
    reproduction.ai_day = ai_day

    default_heifer_reproduction_program = AnimalConfig.heifer_reproduction_program
    AnimalConfig.heifer_reproduction_program = protocol

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II, days_born=days_born, days_in_pregnancy=days_in_pregnancy
    )

    mock_execute_heifer_reproduction_protocol = mocker.patch.object(
        reproduction, "_execute_heifer_reproduction_protocol", return_value=mock_outputs
    )
    mock_perform_ai = mocker.patch.object(reproduction, "_perform_ai", return_value=mock_outputs)
    mock_pregnancy_update = mocker.patch.object(reproduction, "heifer_pregnancy_update", return_value=mock_outputs)

    result = reproduction.heiferII_reproduction_update(mock_outputs, mock_time)

    if expect_protocol_call:
        mock_execute_heifer_reproduction_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)

        if expect_ai:
            mock_perform_ai.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        else:
            mock_perform_ai.assert_not_called()

        if expect_pregnancy_update:
            mock_pregnancy_update.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        else:
            mock_pregnancy_update.assert_not_called()

    else:
        mock_execute_heifer_reproduction_protocol.assert_not_called()

    assert result == mock_outputs

    AnimalConfig.heifer_reproduction_program = default_heifer_reproduction_program


@pytest.mark.parametrize(
    "days_born, protocol",
    [
        # Before breeding start day
        (AnimalConfig.heifer_breed_start_day - 1, HeiferReproductionProtocol.SynchED),
        # On breeding start day
        (AnimalConfig.heifer_breed_start_day, HeiferReproductionProtocol.SynchED),
        # After breeding start day, AI day matches days_born; expect AI
        (AnimalConfig.heifer_breed_start_day + 1, HeiferReproductionProtocol.SynchED),
    ],
)
def test_heiferII_reproduction_update_different_method_as_config(
    days_born: int, protocol: HeiferReproductionProtocol, mocker: MockerFixture
) -> None:
    original_protocol = AnimalConfig.heifer_reproduction_program
    AnimalConfig.heifer_reproduction_program = HeiferReproductionProtocol.ED

    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = protocol
    reproduction.ai_day = AnimalConfig.heifer_breed_start_day + 10

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II, days_born=days_born, days_in_pregnancy=0
    )

    mock_execute_heifer_reproduction_protocol = mocker.patch.object(
        reproduction, "_execute_heifer_reproduction_protocol", return_value=mock_outputs
    )
    mock_perform_ai = mocker.patch.object(reproduction, "_perform_ai")
    mock_pregnancy_update = mocker.patch.object(reproduction, "heifer_pregnancy_update")

    result = reproduction.heiferII_reproduction_update(mock_outputs, mock_time)

    assert result == mock_outputs
    if days_born <= AnimalConfig.heifer_breed_start_day:
        assert reproduction.heifer_reproduction_program == AnimalConfig.heifer_reproduction_program

        if days_born == AnimalConfig.heifer_breed_start_day:
            mock_execute_heifer_reproduction_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        else:
            mock_execute_heifer_reproduction_protocol.assert_not_called()
        mock_perform_ai.assert_not_called()
        mock_pregnancy_update.assert_not_called()

    else:
        assert reproduction.heifer_reproduction_program == protocol
    assert result == mock_outputs

    AnimalConfig.heifer_reproduction_program = original_protocol


@pytest.mark.parametrize(
    "days_in_pregnancy, repro_program, do_not_breed, days_born, ai_day, repro_state, expect_birth",
    [
        (280, CowReproductionProtocol.ED, True, 500, 0, None, True),
        (0, CowReproductionProtocol.ED, False, 500, 0, None, False),
        (0, CowReproductionProtocol.TAI, False, 500, 0, None, False),
        (0, CowReproductionProtocol.ED_TAI, False, 500, 0, None, False),
        (0, CowReproductionProtocol.ED, True, 500, 0, None, False),
        (150, CowReproductionProtocol.ED, True, 500, 0, None, False),
        (0, CowReproductionProtocol.TAI, False, 500, 0, None, False),
        (0, CowReproductionProtocol.ED, False, 500, 500, ReproStateEnum.AFTER_AI, False),
    ],
)
def test_cow_reproduction_update(
    days_in_pregnancy: int,
    repro_program: CowReproductionProtocol,
    do_not_breed: bool,
    days_born: int,
    ai_day: int,
    repro_state: ReproStateEnum,
    expect_birth: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = repro_program
    reproduction.do_not_breed = do_not_breed
    reproduction.gestation_length = 280
    reproduction.ai_day = ai_day
    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in_any.return_value = repro_state is not None

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100
    mock_time.current_date = datetime.today().date()

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW,
        days_in_pregnancy=days_in_pregnancy,
        days_in_milk=150,
        body_weight=0.0,
        breed=Breed.HO,
        days_born=days_born,
        events=mock_events,
        newborn_calf_config=NewBornCalfValuesTypedDict(
            breed=Breed.HO.name,
            animal_type=AnimalType.CALF.value,
            birth_date="",
            days_born=0,
            birth_weight=10.8,
            initial_phosphorus=18.8,
            net_merit=8.8,
        ),
    )

    mock_cow_give_birth = mocker.patch.object(reproduction, "cow_give_birth", return_value=mock_outputs)
    mock_validate_cow_reproduction_program = mocker.patch.object(reproduction, "_validate_cow_reproduction_program")
    mock__update_cow_repro_program_and_log_repro_stats_if_needed = mocker.patch.object(
        reproduction, "_update_cow_repro_program_and_log_repro_stats_if_needed", return_value=mock_outputs
    )
    mock_execute_cow_reproduction_protocols = mocker.patch.object(
        reproduction, "_execute_cow_reproduction_protocols", return_value=mock_outputs
    )
    mock_handle_cow_ai_day = mocker.patch.object(reproduction, "_handle_cow_ai_day", return_value=mock_outputs)
    mock_cow_pregnancy_update = mocker.patch.object(reproduction, "cow_pregnancy_update", return_value=mock_outputs)
    mock_check_do_not_breed_flag = mocker.patch.object(
        reproduction, "_check_do_not_breed_flag", return_value=mock_outputs
    )

    result = reproduction.cow_reproduction_update(mock_outputs, mock_time)

    if expect_birth:
        mock_cow_give_birth.assert_called_once_with(mock_outputs, mock_time)
        assert mock_outputs.newborn_calf_config is not None
    else:
        mock_cow_give_birth.assert_not_called()

    if not do_not_breed:
        mock_validate_cow_reproduction_program.assert_called_once_with()
        mock__update_cow_repro_program_and_log_repro_stats_if_needed.assert_called_once_with(
            mock_outputs, mock_time.simulation_day
        )
        mock_execute_cow_reproduction_protocols.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        mock_handle_cow_ai_day.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        mock_cow_pregnancy_update.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_validate_cow_reproduction_program.assert_not_called()
        mock__update_cow_repro_program_and_log_repro_stats_if_needed.assert_not_called()
        mock_execute_cow_reproduction_protocols.assert_not_called()
        mock_handle_cow_ai_day.assert_not_called()
        mock_cow_pregnancy_update.assert_not_called()

    mock_check_do_not_breed_flag.assert_called_once_with(mock_time.simulation_day, mock_outputs)

    assert result == mock_outputs


@pytest.mark.parametrize("calves", [1, 2, 3])
def test_cow_give_birth(calves: int, mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    reproduction.calves = calves - 1
    reproduction.gestation_length = 280
    reproduction.calf_birth_weight = 40.0
    reproduction.body_weight_at_calving = 0.0

    reproduction.cow_reproduction_program = CowReproductionProtocol.ED_TAI

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 500
    mock_time.current_date = datetime.today().date()

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW,
        body_weight=500.0,
        breed=Breed.HO,
        days_born=500,
        days_in_pregnancy=reproduction.gestation_length,
        days_in_milk=150,
        phosphorus_for_gestation_required_for_calf=18.8,
        net_merit=23.3,
    )

    mock_reset_repro_state = mocker.patch.object(reproduction.repro_state_manager, "reset")
    mock_add_cow_give_birth_events = mocker.patch.object(
        reproduction, "_add_cow_give_birth_events", return_value=mock_outputs
    )
    mock_update_cow_repro_program_and_reset_repro_state_if_needed = mocker.patch.object(
        reproduction, "_update_cow_repro_program_and_reset_repro_state_if_needed", return_value=mock_outputs
    )
    mock_simulate_estrus_if_eligible = mocker.patch.object(
        reproduction, "_simulate_estrus_if_eligible", return_value=mock_outputs
    )
    mock_net_merit_assignment = mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.AnimalGenetics.assign_net_merit_value_to_newborn_calf"
    )

    result = reproduction.cow_give_birth(mock_outputs, mock_time)

    assert reproduction.calves == calves  # Verify calf count has incremented
    assert result.days_in_milk == 1  # Reset milking days
    assert result.days_in_pregnancy == 0  # Reset pregnancy days
    assert reproduction.gestation_length == 0  # Reset gestation length
    assert reproduction.body_weight_at_calving == 500

    mock_reset_repro_state.assert_called_once_with()  # Ensure reproduction state reset after calving
    mock_add_cow_give_birth_events.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    mock_update_cow_repro_program_and_reset_repro_state_if_needed.assert_called_once_with(
        mock_outputs, mock_time.simulation_day
    )
    mock_simulate_estrus_if_eligible.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    mock_net_merit_assignment.assert_called_once_with(mock_time, mock_outputs.breed, mock_outputs.net_merit)


@pytest.mark.parametrize(
    "repro_program, value_error_expected",
    [
        (CowReproductionProtocol.ED, False),
        (CowReproductionProtocol.TAI, False),
        (CowReproductionProtocol.ED_TAI, False),
        (HeiferReproductionProtocol.SynchED, True),
    ],
)
def test_validate_cow_reproduction_program(repro_program: CowReproductionProtocol, value_error_expected: bool) -> None:
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = repro_program
    if value_error_expected:
        with pytest.raises(ValueError):
            reproduction._validate_cow_reproduction_program()
    else:
        reproduction._validate_cow_reproduction_program()


@pytest.mark.parametrize(
    "config_cow_repro_program, current_cow_repro_program, days_in_pregnancy",
    [
        (CowReproductionProtocol.ED, CowReproductionProtocol.ED, 500),
        (CowReproductionProtocol.ED, CowReproductionProtocol.TAI, 500),
        (CowReproductionProtocol.ED, CowReproductionProtocol.ED_TAI, 500),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.TAI, 500),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.ED, 500),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.ED_TAI, 500),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED, 500),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.TAI, 500),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED_TAI, 500),
        (CowReproductionProtocol.ED, CowReproductionProtocol.ED, 0),
        (CowReproductionProtocol.ED, CowReproductionProtocol.TAI, 0),
        (CowReproductionProtocol.ED, CowReproductionProtocol.ED_TAI, 0),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.TAI, 0),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.ED, 0),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.ED_TAI, 0),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED, 0),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.TAI, 0),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED_TAI, 0),
    ],
)
def test_update_cow_repro_program_and_log_repro_stats_if_needed(
    config_cow_repro_program: CowReproductionProtocol,
    current_cow_repro_program: CowReproductionProtocol,
    days_in_pregnancy: int,
    mocker: MockerFixture,
) -> None:
    original_cow_reproduction_program = AnimalConfig.cow_reproduction_program

    AnimalConfig.cow_reproduction_program = config_cow_repro_program
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = current_cow_repro_program

    reproduction_data_stream = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_in_pregnancy=days_in_pregnancy, events=AnimalEvents()
    )
    mock_add_event = mocker.patch.object(reproduction_data_stream.events, "add_event")
    mock_enter_repro_state = mocker.patch.object(reproduction.repro_state_manager, "enter")

    reproduction._update_cow_repro_program_and_log_repro_stats_if_needed(reproduction_data_stream, 0)

    if current_cow_repro_program == config_cow_repro_program:
        mock_add_event.assert_not_called()
        mock_enter_repro_state.assert_not_called()
    else:
        if days_in_pregnancy > 0:
            assert mock_add_event.call_count == 5
            mock_enter_repro_state.assert_not_called()
        else:
            assert mock_add_event.call_count == 6
            mock_enter_repro_state.assert_called_once_with(ReproStateEnum.ENTER_HERD_FROM_INIT)

    AnimalConfig.cow_reproduction_program = original_cow_reproduction_program


@pytest.mark.parametrize(
    "cow_reproduction_program, current_repro_state",
    [
        (CowReproductionProtocol.ED_TAI, set()),
        (CowReproductionProtocol.ED, set()),
        (CowReproductionProtocol.TAI, set()),
        (CowReproductionProtocol.ED, {ReproStateEnum.WAITING_FULL_ED_CYCLE}),
        (CowReproductionProtocol.TAI, {ReproStateEnum.IN_PRESYNCH}),
        (CowReproductionProtocol.ED, {ReproStateEnum.IN_PRESYNCH}),
        (CowReproductionProtocol.ED_TAI, {ReproStateEnum.WAITING_FULL_ED_CYCLE}),
        (CowReproductionProtocol.ED, {ReproStateEnum.WAITING_SHORT_ED_CYCLE, ReproStateEnum.IN_PRESYNCH}),
        (CowReproductionProtocol.ED_TAI, {ReproStateEnum.PREGNANT}),
        (CowReproductionProtocol.ED, {ReproStateEnum.PREGNANT}),
        (CowReproductionProtocol.TAI, {ReproStateEnum.PREGNANT}),
        (CowReproductionProtocol.ED, {ReproStateEnum.NONE}),
        (CowReproductionProtocol.TAI, {ReproStateEnum.NONE}),
        (CowReproductionProtocol.ED_TAI, {ReproStateEnum.NONE}),
    ],
)
def test_execute_cow_reproduction_protocols(
    cow_reproduction_program: CowReproductionProtocol, current_repro_state: set[ReproStateEnum], mocker: MockerFixture
) -> None:
    reproduction_data_stream = mock_reproduction_data_stream(AnimalType.LAC_COW)
    simulation_day = 100

    reproduction = Reproduction()
    reproduction.cow_reproduction_program = cow_reproduction_program
    reproduction.repro_state_manager._states = current_repro_state

    mock_execute_cow_ed_protocol = mocker.patch.object(
        reproduction, "execute_cow_ed_protocol", return_value=reproduction_data_stream
    )
    mock_execute_cow_tai_protocol = mocker.patch.object(
        reproduction, "execute_cow_tai_protocol", return_value=reproduction_data_stream
    )
    mock_execute_cow_ed_tai_protocol = mocker.patch.object(
        reproduction, "execute_cow_ed_tai_protocol", return_value=reproduction_data_stream
    )

    should_call_ed, should_call_tai, should_call_ed_tai = (
        cow_reproduction_program == CowReproductionProtocol.ED,
        cow_reproduction_program == CowReproductionProtocol.TAI,
        cow_reproduction_program == CowReproductionProtocol.ED_TAI,
    )
    ed_repro_states: set[ReproStateEnum] = {
        ReproStateEnum.WAITING_FULL_ED_CYCLE,
        ReproStateEnum.WAITING_SHORT_ED_CYCLE,
        ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH,
    }
    tai_repro_states: set[ReproStateEnum] = {
        ReproStateEnum.IN_PRESYNCH,
        ReproStateEnum.HAS_DONE_PRESYNCH,
        ReproStateEnum.IN_OVSYNCH,
    }

    for repro_state in current_repro_state:
        should_call_ed = True if repro_state in ed_repro_states else should_call_ed
        should_call_tai = True if repro_state in tai_repro_states else should_call_tai

    reproduction._execute_cow_reproduction_protocols(reproduction_data_stream, simulation_day)

    if should_call_ed:
        mock_execute_cow_ed_protocol.assert_called_once_with(reproduction_data_stream, simulation_day)
    else:
        mock_execute_cow_ed_protocol.assert_not_called()

    if should_call_tai:
        mock_execute_cow_tai_protocol.assert_called_once_with(reproduction_data_stream, simulation_day)
    else:
        mock_execute_cow_tai_protocol.assert_not_called()

    if should_call_ed_tai:
        mock_execute_cow_ed_tai_protocol.assert_called_once_with(reproduction_data_stream, simulation_day)
    else:
        mock_execute_cow_ed_tai_protocol.assert_not_called()


@pytest.mark.parametrize("days_born, ai_day", [(500, 500), (0, 180), (181, 180)])
def test_handle_cow_ai_day(days_born: int, ai_day: int, mocker: MockerFixture) -> None:
    reproduction_data_stream = mock_reproduction_data_stream(AnimalType.LAC_COW)
    reproduction_data_stream.days_born = days_born

    reproduction = Reproduction()
    reproduction.ai_day = ai_day

    mock_calculate_conception_rate_on_ai_day = mocker.patch.object(reproduction, "_calculate_conception_rate_on_ai_day")
    mock_enter_repro_state = mocker.patch.object(reproduction.repro_state_manager, "enter")
    mock_add_event = mocker.patch.object(reproduction_data_stream.events, "add_event")
    mock_perform_ai = mocker.patch.object(reproduction, "_perform_ai", return_value=reproduction_data_stream)

    simulation_day = 100

    result = reproduction._handle_cow_ai_day(reproduction_data_stream, simulation_day)

    assert result == reproduction_data_stream
    if days_born == ai_day:
        mock_calculate_conception_rate_on_ai_day.assert_called_once_with()
        mock_enter_repro_state.assert_called_once_with(ReproStateEnum.AFTER_AI)
        mock_add_event.assert_called_once_with(
            days_born, simulation_day, f"Current repro state(s): {reproduction.repro_state_manager}"
        )
        mock_perform_ai.assert_called_once_with(reproduction_data_stream, simulation_day)
    else:
        mock_calculate_conception_rate_on_ai_day.assert_not_called()
        mock_enter_repro_state.assert_not_called()
        mock_add_event.assert_not_called()
        mock_perform_ai.assert_not_called()


@pytest.mark.parametrize(
    "heifer_reproduction_program",
    [
        HeiferReproductionProtocol.ED,
        HeiferReproductionProtocol.TAI,
        HeiferReproductionProtocol.SynchED,
        CowReproductionProtocol.ED,
    ],
)
def test_execute_heifer_reproduction_protocol(
    heifer_reproduction_program: HeiferReproductionProtocol, mocker: MockerFixture
) -> None:
    reproduction_data_stream = mock_reproduction_data_stream(AnimalType.HEIFER_II)
    simulation_day = 100

    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = heifer_reproduction_program

    mock_execute_heifer_ed_protocol = mocker.patch.object(
        reproduction, "execute_heifer_ed_protocol", return_value=reproduction_data_stream
    )
    mock_execute_heifer_tai_protocol = mocker.patch.object(
        reproduction, "execute_heifer_tai_protocol", return_value=reproduction_data_stream
    )
    mock_execute_heifer_synch_ed_protocol = mocker.patch.object(
        reproduction, "execute_heifer_synch_ed_protocol", return_value=reproduction_data_stream
    )

    if heifer_reproduction_program not in [
        HeiferReproductionProtocol.ED,
        HeiferReproductionProtocol.TAI,
        HeiferReproductionProtocol.SynchED,
    ]:
        with pytest.raises(ValueError):
            reproduction._execute_heifer_reproduction_protocol(reproduction_data_stream, simulation_day)
    else:
        result = reproduction._execute_heifer_reproduction_protocol(reproduction_data_stream, simulation_day)
        assert result == reproduction_data_stream

        if heifer_reproduction_program == HeiferReproductionProtocol.ED:
            mock_execute_heifer_ed_protocol.assert_called_once_with(reproduction_data_stream, simulation_day)
            mock_execute_heifer_tai_protocol.assert_not_called()
            mock_execute_heifer_synch_ed_protocol.assert_not_called()
        elif heifer_reproduction_program == HeiferReproductionProtocol.TAI:
            mock_execute_heifer_tai_protocol.assert_called_once_with(reproduction_data_stream, simulation_day)
            mock_execute_heifer_synch_ed_protocol.assert_not_called()
            mock_execute_heifer_ed_protocol.assert_not_called()
        else:
            mock_execute_heifer_synch_ed_protocol.assert_called_once_with(reproduction_data_stream, simulation_day)
            mock_execute_heifer_ed_protocol.assert_not_called()
            mock_execute_heifer_tai_protocol.assert_not_called()


def test_add_cow_give_birth_events(mocker: MockerFixture) -> None:
    reproduction_data_stream = mock_reproduction_data_stream(AnimalType.LAC_COW)
    reproduction_data_stream.days_born = 500

    mock_add_event = mocker.patch.object(reproduction_data_stream.events, "add_event")

    reproduction = Reproduction()
    reproduction.calves = 2

    simulation_day = 100
    result = reproduction._add_cow_give_birth_events(reproduction_data_stream, simulation_day)

    assert result == reproduction_data_stream
    assert mock_add_event.call_args_list == [
        call(reproduction_data_stream.days_born, simulation_day, animal_constants.NEW_BIRTH),
        call(
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.NUM_CALVES_BORN_NOTE}: {reproduction.calves}",
        ),
    ]


@pytest.mark.parametrize(
    "config_cow_repro_program, current_cow_repro_program",
    [
        (CowReproductionProtocol.ED, CowReproductionProtocol.ED),
        (CowReproductionProtocol.ED, CowReproductionProtocol.TAI),
        (CowReproductionProtocol.ED, CowReproductionProtocol.ED_TAI),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.TAI),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.ED),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.ED_TAI),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.TAI),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED_TAI),
        (CowReproductionProtocol.ED, CowReproductionProtocol.ED),
        (CowReproductionProtocol.ED, CowReproductionProtocol.TAI),
        (CowReproductionProtocol.ED, CowReproductionProtocol.ED_TAI),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.TAI),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.ED),
        (CowReproductionProtocol.TAI, CowReproductionProtocol.ED_TAI),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.TAI),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED_TAI),
    ],
)
def test_update_cow_repro_program_and_reset_repro_state_if_needed(
    config_cow_repro_program: CowReproductionProtocol,
    current_cow_repro_program: CowReproductionProtocol,
    mocker: MockerFixture,
) -> None:
    original_cow_reproduction_program = AnimalConfig.cow_reproduction_program
    AnimalConfig.cow_reproduction_program = config_cow_repro_program

    reproduction_data_stream = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW)

    reproduction = Reproduction()
    reproduction.cow_reproduction_program = current_cow_repro_program
    mock_set_cow_reproduction_program = mocker.patch.object(
        reproduction, "_set_cow_reproduction_program", return_value=reproduction_data_stream
    )
    mock_reset_repro_state = mocker.patch.object(reproduction.repro_state_manager, "reset")

    simulation_day = 100
    result = reproduction._update_cow_repro_program_and_reset_repro_state_if_needed(
        reproduction_data_stream, simulation_day
    )

    assert result == reproduction_data_stream
    if current_cow_repro_program == config_cow_repro_program:
        mock_set_cow_reproduction_program.assert_not_called()
        mock_reset_repro_state.assert_not_called()
    else:
        mock_set_cow_reproduction_program.assert_called_once_with(
            reproduction_data_stream, simulation_day, config_cow_repro_program
        )
        mock_reset_repro_state.assert_called_once_with()

    AnimalConfig.cow_reproduction_program = original_cow_reproduction_program


@pytest.mark.parametrize(
    "cow_reproduction_program",
    [
        CowReproductionProtocol.ED,
        CowReproductionProtocol.TAI,
        CowReproductionProtocol.ED_TAI,
    ],
)
def test_simulate_estrus_if_eligible(cow_reproduction_program: CowReproductionProtocol, mocker: MockerFixture) -> None:
    reproduction_data_stream = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW)

    reproduction = Reproduction()
    reproduction.cow_reproduction_program = cow_reproduction_program

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=reproduction_data_stream)

    simulation_day = 100
    result = reproduction._simulate_estrus_if_eligible(reproduction_data_stream, simulation_day)

    assert result == reproduction_data_stream
    if cow_reproduction_program in [CowReproductionProtocol.ED, CowReproductionProtocol.ED_TAI]:
        mock_simulate_estrus.assert_called_once_with(
            reproduction_data_stream,
            reproduction_data_stream.days_born,
            simulation_day,
            f"{animal_constants.ESTRUS_AFTER_CALVING_NOTE}: {animal_constants.ESTRUS_DAY_SCHEDULED_NOTE}",
            AnimalConfig.average_estrus_cycle_return,
            AnimalConfig.std_estrus_cycle_return,
        )
    else:
        mock_simulate_estrus.assert_not_called()


@pytest.mark.parametrize(
    "heifer_reproduction_program, new_repro_program",
    [
        (HeiferReproductionProtocol.SynchED, HeiferReproductionProtocol.SynchED),
        (HeiferReproductionProtocol.TAI, HeiferReproductionProtocol.ED),
        (HeiferReproductionProtocol.ED, CowReproductionProtocol.TAI),
    ],
)
def test_set_heifer_reproduction_program(
    heifer_reproduction_program: HeiferReproductionProtocol, new_repro_program: HeiferReproductionProtocol
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = heifer_reproduction_program

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = MagicMock(spec=ReproductionOutputs)
    mock_outputs.days_born = 500
    mock_outputs.events = MagicMock()
    mock_outputs.events.add_event = MagicMock()

    if not isinstance(new_repro_program, HeiferReproductionProtocol):
        with pytest.raises(ValueError):
            reproduction._set_heifer_reproduction_program(mock_outputs, mock_time.simulation_day, new_repro_program)
    else:
        result = reproduction._set_heifer_reproduction_program(
            mock_outputs, mock_time.simulation_day, new_repro_program
        )

        if heifer_reproduction_program != new_repro_program:
            mock_outputs.events.add_event.assert_called_once_with(
                mock_outputs.days_born,
                mock_time.simulation_day,
                f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from {heifer_reproduction_program} "
                f"to {new_repro_program}",
            )

        assert result == mock_outputs


@pytest.mark.parametrize(
    "cow_reproduction_program, new_repro_program",
    [
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED_TAI),
        (CowReproductionProtocol.ED_TAI, CowReproductionProtocol.ED),
        (CowReproductionProtocol.ED_TAI, HeiferReproductionProtocol.TAI),
    ],
)
def test_set_cow_reproduction_program(
    cow_reproduction_program: CowReproductionProtocol, new_repro_program: CowReproductionProtocol
) -> None:
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = cow_reproduction_program

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = MagicMock(spec=ReproductionOutputs)
    mock_outputs.days_born = 500
    mock_outputs.events = MagicMock()
    mock_outputs.events.add_event = MagicMock()

    if not isinstance(new_repro_program, CowReproductionProtocol):
        with pytest.raises(ValueError):
            reproduction._set_cow_reproduction_program(mock_outputs, mock_time.simulation_day, new_repro_program)
    else:
        result = reproduction._set_cow_reproduction_program(mock_outputs, mock_time.simulation_day, new_repro_program)

        if cow_reproduction_program != new_repro_program:
            mock_outputs.events.add_event.assert_called_once_with(
                mock_outputs.days_born,
                mock_time.simulation_day,
                f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from {cow_reproduction_program} "
                f"to {new_repro_program}",
            )

        assert result == mock_outputs


@pytest.mark.parametrize(
    "avg_estrus_cycle, max_cycle_length, estrus_cycle_value, expected_estrus_day",
    [
        (21, math.inf, 1, 501),
        (21, 25, 24, 524),
        (21, 23, 24, 522),
    ],
)
def test_simulate_first_estrus(
    avg_estrus_cycle: int,
    max_cycle_length: float,
    estrus_cycle_value: int,
    expected_estrus_day: int,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.estrus_day = 0

    mock_outputs = MagicMock(spec=ReproductionOutputs)
    mock_outputs.days_born = 500
    mock_outputs.events = MagicMock()
    mock_outputs.events.add_event = MagicMock()

    mocker.patch("random.randint", return_value=estrus_cycle_value)
    result = reproduction._simulate_first_estrus(
        mock_outputs,
        start_day=500,
        simulation_day=1000,
        estrus_note="Estrus simulated",
        avg_estrus_cycle=avg_estrus_cycle,
        max_cycle_length=max_cycle_length,
    )

    assert reproduction.estrus_day == expected_estrus_day

    mock_outputs.events.add_event.assert_called_once_with(
        mock_outputs.days_born, 1000, f"Estrus simulated on day {expected_estrus_day}"
    )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "avg_estrus_cycle, std_estrus_cycle, max_cycle_length, estrus_cycle_value, expected_estrus_day",
    [
        (21, 3, math.inf, 20, 520),
        (21, 3, 25, 24, 524),
        (21, 3, 23, 24, 522),
    ],
)
def test_simulate_estrus(
    avg_estrus_cycle: int,
    std_estrus_cycle: int,
    max_cycle_length: float,
    estrus_cycle_value: int,
    expected_estrus_day: int,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.estrus_day = 0

    mock_outputs = MagicMock(spec=ReproductionOutputs)
    mock_outputs.days_born = 500
    mock_outputs.events = MagicMock()
    mock_outputs.events.add_event = MagicMock()

    mocker.patch("scipy.stats.truncnorm.rvs", return_value=estrus_cycle_value)
    result = reproduction._simulate_estrus(
        mock_outputs,
        start_day=500,
        simulation_day=1000,
        estrus_note="Estrus simulated",
        avg_estrus_cycle=avg_estrus_cycle,
        std_estrus_cycle=std_estrus_cycle,
        max_cycle_length=max_cycle_length,
    )

    assert reproduction.estrus_day == expected_estrus_day

    mock_outputs.events.add_event.assert_called_once_with(
        mock_outputs.days_born, 1000, f"Estrus simulated on day {expected_estrus_day}"
    )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "detection_rate, random_value, expected_result",
    [
        (0.6, 0.4, True),
        (0.6, 0.7, False),
        (0.8, 0.2, True),
        (0.3, 0.5, False),
    ],
)
def test_detect_estrus(
    detection_rate: float, random_value: float, expected_result: bool, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    mock_method = mocker.patch("RUFAS.util.Utility.compare_randomized_rate_less_than", return_value=expected_result)
    result = reproduction._detect_estrus(detection_rate)
    mock_method.assert_called_once_with(detection_rate)
    assert result == expected_result


@pytest.mark.parametrize(
    "days_in_pregnancy, days_born, estrus_day, expected_estrus_simulated, expected_handle_generic_called",
    [
        (10, AnimalConfig.heifer_breed_start_day, 0, True, False),
        (10, 400, 400, False, True),
        (0, 400, 0, False, False),
    ],
)
def test_execute_heifer_ed_protocol(
    days_in_pregnancy: int,
    days_born: int,
    estrus_day: int,
    expected_estrus_simulated: bool,
    expected_handle_generic_called: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.estrus_day = estrus_day
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II, days_in_pregnancy=days_in_pregnancy, days_born=days_born
    )

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_first_estrus", return_value=mock_outputs)
    mock_handle_generic_estrus = mocker.patch.object(
        reproduction, "_handle_generic_estrus_detection", return_value=mock_outputs
    )

    result = reproduction.execute_heifer_ed_protocol(mock_outputs, mock_time.simulation_day)

    if expected_estrus_simulated:
        mock_simulate_estrus.assert_called_once()
    else:
        mock_simulate_estrus.assert_not_called()

    if expected_handle_generic_called:
        mock_handle_generic_estrus.assert_called_once()
    else:
        mock_handle_generic_estrus.assert_not_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_in_milk, repro_state, days_born, estrus_day, "
    "expected_simulate_estrus, expected_repro_state_entered, expected_handle_called,"
    "expected_repeat_estrus_simulation",
    [
        (1, ReproStateEnum.ENTER_HERD_FROM_INIT, 350, 400, False, False, False, True),
        (10, ReproStateEnum.FRESH, 350, 500, False, False, False, True),
        (100, ReproStateEnum.ENTER_HERD_FROM_INIT, 450, 400, True, True, False, False),
        (100, ReproStateEnum.ENTER_HERD_FROM_INIT, 350, 400, False, True, False, False),
        (100, ReproStateEnum.FRESH, 450, 400, False, False, False, False),
        (100, ReproStateEnum.ENTER_HERD_FROM_INIT, 400, 400, False, False, False, False),
        (100, ReproStateEnum.FRESH, 400, 400, False, False, False, False),
        (100, ReproStateEnum.WAITING_SHORT_ED_CYCLE, 400, 400, False, False, True, False),
        (100, ReproStateEnum.WAITING_FULL_ED_CYCLE, 400, 400, False, False, True, False),
        (100, ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH, 400, 400, False, False, True, False),
    ],
)
def test_execute_cow_ed_protocol(
    days_in_milk: int,
    repro_state: ReproStateEnum,
    days_born: int,
    estrus_day: int,
    expected_simulate_estrus: bool,
    expected_repro_state_entered: bool,
    expected_handle_called: bool,
    expected_repeat_estrus_simulation: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.estrus_day = estrus_day
    reproduction.repro_state_manager = ReproStateManager()
    reproduction.repro_state_manager.enter(repro_state)
    if repro_state == ReproStateEnum.WAITING_SHORT_ED_CYCLE:
        reproduction.repro_state_manager.enter(ReproStateEnum.IN_OVSYNCH, keep_existing=True)
    mock_enter_repro_state = mocker.patch.object(reproduction.repro_state_manager, "enter")
    mock_exit_repro_state = mocker.patch.object(reproduction.repro_state_manager, "exit")

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_events = MagicMock(spec=AnimalEvents)

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_in_milk=days_in_milk, days_born=days_born, events=mock_events
    )

    mock_repeat_estrus_simulation = mocker.patch.object(
        reproduction, "_repeat_estrus_simulation_before_vwp", return_value=mock_outputs
    )
    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)
    mock_handle_estrus_detection = mocker.patch.object(
        reproduction, "_handle_estrus_detection", return_value=mock_outputs
    )

    result = reproduction.execute_cow_ed_protocol(mock_outputs, mock_time.simulation_day)

    if expected_repeat_estrus_simulation:
        mock_repeat_estrus_simulation.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_repeat_estrus_simulation.assert_not_called()

    if expected_simulate_estrus:
        mock_simulate_estrus.assert_called_once_with(
            mock_outputs,
            days_born,
            mock_time.simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
    else:
        mock_simulate_estrus.assert_not_called()

    if expected_repro_state_entered:
        mock_enter_repro_state.assert_called_once_with(ReproStateEnum.WAITING_FULL_ED_CYCLE)

    if expected_handle_called:
        mock_handle_estrus_detection.assert_called_once()
    else:
        mock_handle_estrus_detection.assert_not_called()

    if (
        repro_state == ReproStateEnum.WAITING_SHORT_ED_CYCLE
        or repro_state == ReproStateEnum.WAITING_FULL_ED_CYCLE
        or repro_state == ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH
    ):
        mock_exit_repro_state.assert_called_once()

    assert result == mock_outputs


def test_execute_cow_ed_protocol_resets_ed_days_when_pregnant(mocker: MockerFixture) -> None:
    """If the cow is pregnant, ED_days should be reset to 0."""
    reproduction = Reproduction()
    reproduction.reproduction_statistics.ED_days = 5
    mock_events = MagicMock(spec=AnimalEvents)
    data_stream = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW,
        days_in_milk=0,
        events=mock_events,
    )
    data_stream.days_in_pregnancy = 100

    simulation_day = 100

    mock_repeat_estrus = mocker.patch.object(
        reproduction,
        "_repeat_estrus_simulation_before_vwp",
        return_value=data_stream,
    )
    mock_simulate_estrus = mocker.patch.object(
        reproduction,
        "_simulate_estrus",
        return_value=data_stream,
    )
    mock_handle_estrus_detection = mocker.patch.object(
        reproduction,
        "_handle_estrus_detection",
        return_value=data_stream,
    )

    result = reproduction.execute_cow_ed_protocol(data_stream, simulation_day)

    assert reproduction.reproduction_statistics.ED_days == 0

    mock_repeat_estrus.assert_not_called()
    mock_simulate_estrus.assert_not_called()
    mock_handle_estrus_detection.assert_not_called()

    assert result is data_stream


@pytest.mark.parametrize(
    "is_estrus_detected, expected_on_detected_called, expected_on_not_detected_called",
    [
        (True, True, False),
        (False, False, True),
    ],
)
def test_handle_generic_estrus_detection(
    is_estrus_detected: bool,
    expected_on_detected_called: bool,
    expected_on_not_detected_called: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II,
    )

    mock_handle_estrus_detection = mocker.patch.object(
        reproduction, "_handle_estrus_detection", return_value=mock_outputs
    )

    result = reproduction._handle_generic_estrus_detection(mock_outputs, mock_time.simulation_day)

    mock_handle_estrus_detection.assert_called_once_with(
        mock_outputs,
        mock_time.simulation_day,
        on_estrus_detected=reproduction._handle_estrus_detected,
        on_estrus_not_detected=reproduction._handle_estrus_not_detected,
    )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "animal_type, estrus_detection_rate, is_estrus_detected, expected_on_detected_called, "
    "expected_on_not_detected_called",
    [
        (AnimalType.HEIFER_II, AnimalConfig.heifer_estrus_detection_rate, True, True, False),
        (AnimalType.HEIFER_II, AnimalConfig.heifer_estrus_detection_rate, False, False, True),
        (AnimalType.LAC_COW, AnimalConfig.cow_estrus_detection_rate, True, True, False),
        (AnimalType.LAC_COW, AnimalConfig.cow_estrus_detection_rate, False, False, True),
    ],
)
def test_handle_estrus_detection(
    animal_type: AnimalType,
    estrus_detection_rate: float,
    is_estrus_detected: bool,
    expected_on_detected_called: bool,
    expected_on_not_detected_called: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=animal_type,
    )

    mock_on_estrus_detected = mocker.patch.object(reproduction, "_handle_estrus_detected", return_value=mock_outputs)
    mock_on_estrus_not_detected = mocker.patch.object(
        reproduction, "_handle_estrus_not_detected", return_value=mock_outputs
    )
    mock_detect_estrus = mocker.patch.object(reproduction, "_detect_estrus", return_value=is_estrus_detected)
    mock_add_event = mocker.patch.object(mock_outputs.events, "add_event")

    result = reproduction._handle_estrus_detection(
        mock_outputs,
        mock_time.simulation_day,
        on_estrus_detected=mock_on_estrus_detected,
        on_estrus_not_detected=mock_on_estrus_not_detected,
    )

    mock_detect_estrus.assert_called_once_with(estrus_detection_rate)
    mock_add_event.assert_any_call(
        mock_outputs.days_born, mock_time.simulation_day, animal_constants.ESTRUS_OCCURRED_NOTE
    )

    if is_estrus_detected:
        mock_on_estrus_detected.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        mock_add_event.assert_any_call(
            mock_outputs.days_born,
            mock_time.simulation_day,
            f"{animal_constants.ESTRUS_DETECTED_NOTE}, with estrus detection rate at {estrus_detection_rate}",
        )
        mock_on_estrus_not_detected.assert_not_called()
    else:
        mock_on_estrus_not_detected.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        mock_add_event.assert_any_call(
            mock_outputs.days_born,
            mock_time.simulation_day,
            f"{animal_constants.ESTRUS_NOT_DETECTED_NOTE}, with estrus detection rate at {estrus_detection_rate}",
        )
        mock_on_estrus_detected.assert_not_called()

    assert result == mock_outputs


def test_handle_estrus_detected(mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II, days_born=500)

    mock_add_event = mocker.patch.object(mock_outputs.events, "add_event")

    result = reproduction._handle_estrus_detected(mock_outputs, mock_time.simulation_day)

    assert reproduction.conception_rate == AnimalConfig.heifer_estrus_conception_rate
    assert reproduction.ai_day == mock_outputs.days_born + 1
    mock_add_event.assert_called_once_with(
        mock_outputs.days_born,
        mock_time.simulation_day,
        f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {reproduction.ai_day}",
    )
    assert result == mock_outputs


def test_handle_estrus_not_detected(mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II, days_born=500)

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)

    result = reproduction._handle_estrus_not_detected(mock_outputs, mock_time.simulation_day)

    mock_simulate_estrus.assert_called_once_with(
        mock_outputs,
        mock_outputs.days_born,
        mock_time.simulation_day,
        animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
        AnimalConfig.average_estrus_cycle_heifer,
        AnimalConfig.std_estrus_cycle_heifer,
    )
    assert result == mock_outputs


@pytest.mark.parametrize(
    "hormones, expected_GnRH, expected_PGF, expected_CIDR, expected_event_calls",
    [
        (["GnRH"], 1, 0, 0, [animal_constants.INJECT_GNRH]),
        (["PGF"], 0, 1, 0, [animal_constants.INJECT_PGF]),
        (["CIDR"], 0, 0, 1, [animal_constants.INJECT_CIDR]),
        (["GnRH", "PGF"], 1, 1, 0, [animal_constants.INJECT_GNRH, animal_constants.INJECT_PGF]),
        (["invalid"], 0, 0, 1, [animal_constants.INJECT_CIDR]),
    ],
)
def test_deliver_hormones(
    hormones: list[str],
    expected_GnRH: int,
    expected_PGF: int,
    expected_CIDR: int,
    expected_event_calls: list[str],
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II, days_born=500)

    mock_add_event = mocker.patch.object(mock_outputs.events, "add_event")

    if hormones == ["invalid"]:
        with pytest.raises(ValueError):
            reproduction._deliver_hormones(mock_outputs, hormones, mock_outputs.days_born, mock_time.simulation_day)
        return

    result = reproduction._deliver_hormones(mock_outputs, hormones, mock_outputs.days_born, mock_time.simulation_day)

    assert reproduction.reproduction_statistics.GnRH_injections == expected_GnRH
    assert reproduction.reproduction_statistics.PGF_injections == expected_PGF
    assert reproduction.reproduction_statistics.CIDR_injections == expected_CIDR

    for event, call_arg in zip(expected_event_calls, mock_add_event.call_args_list):
        assert call_arg[0][2] == event

    assert result == mock_outputs


def test_execute_hormone_delivery_schedule(mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=500)

    schedule = {500: {"deliver_hormones": ["GnRH", "PGF"], "set_ai_day": True, "set_conception_rate": True}}

    mock_deliver_hormones = mocker.patch.object(reproduction, "_deliver_hormones", return_value=mock_outputs)
    mock_add_event = mocker.patch.object(mock_outputs.events, "add_event")

    result = reproduction._execute_hormone_delivery_schedule(mock_outputs, mock_time.simulation_day, schedule)

    mock_deliver_hormones.assert_called_once_with(
        mock_outputs, ["GnRH", "PGF"], mock_outputs.days_born, mock_time.simulation_day
    )

    assert reproduction.ai_day == mock_outputs.days_born
    assert reproduction.conception_rate == reproduction.TAI_conception_rate

    mock_add_event.assert_any_call(
        mock_outputs.days_born,
        mock_time.simulation_day,
        f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {reproduction.ai_day}",
    )

    assert 500 not in schedule  # Ensuring the day is removed from the schedule after execution

    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_born, heifer_reproduction_program, heifer_sub_reproduction_program, expected_hormone_schedule_setup,"
    "expected_hormone_schedule_execute",
    [
        (
            AnimalConfig.heifer_breed_start_day,
            HeiferReproductionProtocol.TAI,
            HeiferTAISubProtocol.TAI_5dCG2P,
            True,
            True,
        ),
        (300, HeiferReproductionProtocol.TAI, HeiferTAISubProtocol.TAI_5dCGP, False, True),
        (
            AnimalConfig.heifer_breed_start_day,
            HeiferReproductionProtocol.SynchED,
            HeiferSynchEDSubProtocol.SynchED_2P,
            True,
            True,
        ),
        (300, HeiferReproductionProtocol.SynchED, HeiferSynchEDSubProtocol.SynchED_2P, False, False),
    ],
)
def test_execute_heifer_tai_protocol(
    days_born: int,
    heifer_reproduction_program: HeiferReproductionProtocol,
    heifer_sub_reproduction_program: HEIFER_REPRODUCTION_SUB_PROTOCOLS,
    expected_hormone_schedule_setup: bool,
    expected_hormone_schedule_execute: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = heifer_reproduction_program
    reproduction.heifer_reproduction_sub_program = heifer_sub_reproduction_program
    reproduction.hormone_schedule = {
        0: {"deliver_hormones": ["CIDR"]},
        5: {"deliver_hormones": ["PGF"]},
        6: {"deliver_hormones": ["PGF"]},
        8: {"deliver_hormones": ["GnRH"]},
        9: {"set_ai_day": True, "set_conception_rate": True},
    }
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II, days_born=days_born, events=MagicMock(spec=AnimalEvents)
    )

    mock_set_hormone_schedule = mocker.patch.object(reproduction, "_set_up_hormone_schedule", return_value=mock_outputs)
    mock_execute_hormone_schedule = mocker.patch.object(
        reproduction, "_execute_hormone_delivery_schedule", return_value=mock_outputs
    )

    result = reproduction.execute_heifer_tai_protocol(mock_outputs, mock_time.simulation_day)

    if expected_hormone_schedule_setup:
        mock_set_hormone_schedule.assert_called_once_with(
            mock_outputs, days_born, heifer_sub_reproduction_program.value
        )
    else:
        mock_set_hormone_schedule.assert_not_called()

    mock_execute_hormone_schedule.assert_called_once_with(
        mock_outputs, mock_time.simulation_day, reproduction.hormone_schedule
    )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_in_milk, cow_presynch_method, ovsynch_program_start_day, presynch_program_start_day, "
    "expected_fresh_entry, expected_presynch_setup, expected_ovsynch_setup, expected_hormone_execute",
    [
        (10, "None", 20, 15, True, False, False, True),
        (25, "None", 20, 15, False, False, True, True),
        (10, "Double OvSynch", 20, 15, True, False, False, True),
        (20, "Double OvSynch", 20, 15, False, True, True, True),
    ],
)
def test_execute_cow_tai_protocol(
    days_in_milk: int,
    cow_presynch_method: str,
    ovsynch_program_start_day: int,
    presynch_program_start_day: int,
    expected_fresh_entry: bool,
    expected_presynch_setup: bool,
    expected_ovsynch_setup: bool,
    expected_hormone_execute: bool,
    mocker: MockerFixture,
) -> None:
    default_cow_presynch_method = AnimalConfig.cow_presynch_method
    default_ovsynch_program_start_day = AnimalConfig.ovsynch_program_start_day
    default_presynch_program_start_day = AnimalConfig.presynch_program_start_day

    AnimalConfig.cow_presynch_method = CowPreSynchSubProtocol(cow_presynch_method)
    AnimalConfig.ovsynch_program_start_day = ovsynch_program_start_day
    AnimalConfig.presynch_program_start_day = presynch_program_start_day

    reproduction = Reproduction()
    reproduction.hormone_schedule = {
        0: {"deliver_hormones": ["GnRH"]},
        7: {"deliver_hormones": ["PGF"]},
        9: {"deliver_hormones": ["GnRH"]},
        10: {
            "set_ai_day": True,
            "set_conception_rate": True,
            "set_ovsynch_end": True,
        },
    }
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_in_milk=days_in_milk, events=MagicMock(spec=AnimalEvents)
    )

    mock_enter_fresh_state = mocker.patch.object(
        reproduction, "_enter_fresh_state_if_in_empty_state", return_value=mock_outputs
    )
    mock_setup_presynch = mocker.patch.object(
        reproduction, "_setup_presynch_on_presynch_start_day_if_valid", return_value=mock_outputs
    )
    mock_setup_ovsynch = mocker.patch.object(
        reproduction, "_setup_ovsynch_on_ovsynch_start_day_if_valid", return_value=mock_outputs
    )
    mock_execute_hormone_schedule = mocker.patch.object(
        reproduction, "_execute_cow_hormone_delivery_schedule", return_value=mock_outputs
    )

    result = reproduction.execute_cow_tai_protocol(mock_outputs, mock_time.simulation_day)

    if expected_fresh_entry:
        mock_enter_fresh_state.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_enter_fresh_state.assert_not_called()

    if expected_presynch_setup:
        mock_setup_presynch.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_setup_presynch.assert_not_called()

    if expected_ovsynch_setup:
        mock_setup_ovsynch.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_setup_ovsynch.assert_not_called()

    if expected_hormone_execute:
        mock_execute_hormone_schedule.assert_called_with(
            mock_outputs, mock_time.simulation_day, reproduction.hormone_schedule
        )

    assert result == mock_outputs

    AnimalConfig.cow_presynch_method = default_cow_presynch_method
    AnimalConfig.ovsynch_program_start_day = default_ovsynch_program_start_day
    AnimalConfig.presynch_program_start_day = default_presynch_program_start_day


@pytest.mark.parametrize(
    "days_born, estrus_day, heifer_reproduction_program, expected_hormone_schedule_setup, "
    "expected_handle_hormone_delivery_called, expected_handle_estrus_detection_called",
    [
        (AnimalConfig.heifer_breed_start_day, 0, HeiferReproductionProtocol.SynchED, True, True, False),
        (300, 0, HeiferReproductionProtocol.SynchED, False, True, False),
        (300, 300, HeiferReproductionProtocol.SynchED, False, True, True),
        (
            AnimalConfig.heifer_breed_start_day,
            AnimalConfig.heifer_breed_start_day,
            HeiferReproductionProtocol.SynchED,
            True,
            True,
            True,
        ),
    ],
)
def test_execute_heifer_synch_ed_protocol(
    days_born: int,
    estrus_day: int,
    heifer_reproduction_program: HeiferReproductionProtocol,
    expected_hormone_schedule_setup: bool,
    expected_handle_hormone_delivery_called: bool,
    expected_handle_estrus_detection_called: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = heifer_reproduction_program
    heifer_reproduction_sub_program = (
        AnimalConfig.heifer_reproduction_sub_program
        if heifer_reproduction_program == AnimalConfig.heifer_reproduction_program
        else InternalReproSettings.HEIFER_REPRO_PROTOCOLS[heifer_reproduction_program.value]["default_sub_protocol"]
    )
    reproduction.hormone_schedule = {
        0: {"deliver_hormones": ["CIDR"]},
        5: {"deliver_hormones": ["PGF"]},
        6: {"deliver_hormones": ["PGF"]},
        8: {"deliver_hormones": ["GnRH"]},
        9: {"set_ai_day": True, "set_conception_rate": True},
    }
    reproduction.estrus_day = estrus_day
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II, days_born=days_born, events=MagicMock(spec=AnimalEvents)
    )

    mock_set_hormone_schedule = mocker.patch.object(reproduction, "_set_up_hormone_schedule", return_value=mock_outputs)
    mock_handle_hormone_delivery = mocker.patch.object(
        reproduction, "_handle_synch_ed_hormone_delivery_and_set_estrus_day", return_value=mock_outputs
    )
    mock_handle_estrus_detection = mocker.patch.object(
        reproduction, "_handle_synch_ed_estrus_detection", return_value=mock_outputs
    )

    result = reproduction.execute_heifer_synch_ed_protocol(mock_outputs, mock_time.simulation_day)

    if expected_hormone_schedule_setup:
        mock_set_hormone_schedule.assert_called_once_with(
            mock_outputs, days_born, heifer_reproduction_sub_program.value
        )
    else:
        mock_set_hormone_schedule.assert_not_called()

    if expected_handle_hormone_delivery_called:
        mock_handle_hormone_delivery.assert_called_once_with(mock_outputs, mock_time.simulation_day)

    if expected_handle_estrus_detection_called:
        mock_handle_estrus_detection.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_handle_estrus_detection.assert_not_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "animal_type, sub_program, start_from, expected_schedule_key, raises_exception",
    [
        (AnimalType.HEIFER_II, HeiferTAISubProtocol.TAI_5dCG2P, 100, "heifers", False),
        (AnimalType.HEIFER_II, HeiferSynchEDSubProtocol.SynchED_CP, 100, "heifers", False),
        (AnimalType.LAC_COW, CowTAISubProtocol.TAI_OvSynch_48, 100, "cows", False),
        (AnimalType.LAC_COW, CowPreSynchSubProtocol.Presynch_DoubleOvSynch, 100, "cows", False),
        (AnimalType.HEIFER_II, HeiferTAISubProtocol.TAI_5dCG2P, 100, "heifers", True),  # No schedule available
        (AnimalType.LAC_COW, CowPreSynchSubProtocol.Presynch_DoubleOvSynch, 100, "cows", True),  # No schedule available
    ],
)
def test_set_up_hormone_schedule(
    animal_type: AnimalType,
    sub_program: HeiferTAISubProtocol | HeiferSynchEDSubProtocol | CowTAISubProtocol | CowPreSynchSubProtocol,
    start_from: int,
    expected_schedule_key: str,
    raises_exception: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    if isinstance(sub_program, HeiferTAISubProtocol) or isinstance(sub_program, HeiferSynchEDSubProtocol):
        reproduction.heifer_reproduction_sub_program = sub_program

    mock_outputs = mock_reproduction_data_stream(animal_type=animal_type)

    mock_get_adjusted_schedule = mocker.patch(
        "RUFAS.biophysical.animal.reproduction.hormone_delivery_schedule.HormoneDeliverySchedule.get_adjusted_schedule",
        return_value=None if raises_exception else {0: {"deliver_hormones": ["GnRH"]}},
    )

    if raises_exception:
        with pytest.raises(Exception, match=f"No hormone delivery schedule for {animal_type} - .*"):
            reproduction._set_up_hormone_schedule(mock_outputs, start_from, sub_program.value)
    else:
        result = reproduction._set_up_hormone_schedule(mock_outputs, start_from, sub_program.value)
        mock_get_adjusted_schedule.assert_called_once_with(expected_schedule_key, sub_program.value, start_from)
        assert result == mock_outputs
        assert reproduction.hormone_schedule == {0: {"deliver_hormones": ["GnRH"]}}


@pytest.mark.parametrize(
    "hormone_schedule_empty, clear_schedule_during_execution, expected_hormone_execution, expected_simulate_estrus",
    [
        # 1) Schedule present, not cleared → hormone delivery only, no estrus
        (False, False, True, False),
        # 2) Schedule empty from start → nothing happens
        (True, False, False, False),
        # 3) Schedule present, cleared by hormone execution → hormone + estrus
        (False, True, True, True),
    ],
    ids=[
        "schedule_present_no_clear",
        "schedule_empty_no_action",
        "schedule_present_then_cleared_trigger_estrus",
    ],
)
def test_handle_synch_ed_hormone_delivery_and_set_estrus_day(
    hormone_schedule_empty: bool,
    clear_schedule_during_execution: bool,
    expected_hormone_execution: bool,
    expected_simulate_estrus: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.hormone_schedule = {} if hormone_schedule_empty else {0: {"deliver_hormones": ["GnRH"]}}

    simulation_day = 100

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II,
        events=MagicMock(spec=AnimalEvents),
    )

    if clear_schedule_during_execution:

        def _side_effect(
            repro_stream: ReproductionDataStream, simulation_day: int, schedule: dict[int, dict[str, list[str]]]
        ) -> ReproductionDataStream:
            assert reproduction.hormone_schedule
            reproduction.hormone_schedule = {}
            return repro_stream

        mock_execute_hormone_schedule = mocker.patch.object(
            reproduction,
            "_execute_hormone_delivery_schedule",
            side_effect=_side_effect,
        )
    else:
        mock_execute_hormone_schedule = mocker.patch.object(
            reproduction,
            "_execute_hormone_delivery_schedule",
            return_value=mock_outputs,
        )

    mock_simulate_estrus = mocker.patch.object(
        reproduction,
        "_simulate_estrus",
        return_value=mock_outputs,
    )

    result = reproduction._handle_synch_ed_hormone_delivery_and_set_estrus_day(
        mock_outputs,
        simulation_day,
    )

    if expected_hormone_execution:
        mock_execute_hormone_schedule.assert_called_once()
    else:
        mock_execute_hormone_schedule.assert_not_called()

    if expected_simulate_estrus:
        mock_simulate_estrus.assert_called_once_with(
            mock_outputs,
            mock_outputs.days_born,
            simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_after_pgf,
            AnimalConfig.std_estrus_cycle_after_pgf,
            max_cycle_length=14,
        )
    else:
        mock_simulate_estrus.assert_not_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "estrus_detected, expected_estrus_event, expected_ai_scheduled",
    [
        (True, True, True),  # Estrus detected, AI day scheduled.
        (False, False, False),  # Estrus not detected, handle non-detection.
    ],
)
def test_handle_synch_ed_estrus_detection(
    estrus_detected: bool, expected_estrus_event: bool, expected_ai_scheduled: bool, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II)
    mock_outputs.events = mock_events

    mock_detect_estrus = mocker.patch.object(reproduction, "_detect_estrus", return_value=estrus_detected)
    mock_handle_estrus_not_detected = mocker.patch.object(
        reproduction, "_handle_estrus_not_detected_in_synch_ed", return_value=mock_outputs
    )

    result = reproduction._handle_synch_ed_estrus_detection(mock_outputs, mock_time.simulation_day)

    mock_detect_estrus.assert_called_once()
    mock_outputs.events.add_event.assert_any_call(
        mock_outputs.days_born, mock_time.simulation_day, animal_constants.ESTRUS_OCCURRED_NOTE
    )

    assert result == mock_outputs

    if expected_estrus_event:
        mock_outputs.events.add_event.assert_any_call(
            mock_outputs.days_born, mock_time.simulation_day, animal_constants.ESTRUS_DETECTED_NOTE
        )
        assert reproduction.conception_rate == AnimalConfig.heifer_reproduction_sub_program_conception_rate
    if expected_ai_scheduled:
        assert reproduction.ai_day == mock_outputs.days_born + 1
        mock_outputs.events.add_event.assert_any_call(
            mock_outputs.days_born,
            mock_time.simulation_day,
            f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {reproduction.ai_day}",
        )
    else:
        mock_handle_estrus_not_detected.assert_called_once_with(mock_outputs, mock_time.simulation_day)


@pytest.mark.parametrize(
    "heifer_reproduction_sub_program, heifer_reproduction_program, expected_fallback_protocol, "
    "expected_program_change, expected_hormone_schedule_setup, expected_conception_rate",
    [
        (
            HeiferSynchEDSubProtocol.SynchED_CP,
            HeiferReproductionProtocol.SynchED,
            HeiferReproductionProtocol.TAI,
            True,
            True,
            0.5,
        )
    ],
)
def test_handle_estrus_not_detected_in_synch_ed(
    heifer_reproduction_sub_program: HeiferSynchEDSubProtocol,
    heifer_reproduction_program: HeiferReproductionProtocol,
    expected_fallback_protocol: HeiferReproductionProtocol,
    expected_program_change: bool,
    expected_hormone_schedule_setup: bool,
    expected_conception_rate: float,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_sub_program = heifer_reproduction_sub_program
    reproduction.heifer_reproduction_program = heifer_reproduction_program
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II)
    mock_outputs.events = mock_events

    mock_set_up_hormone_schedule = mocker.patch.object(
        reproduction, "_set_up_hormone_schedule", return_value=mock_outputs
    )
    mock_execute_hormone_schedule = mocker.patch.object(
        reproduction, "_execute_hormone_delivery_schedule", return_value=mock_outputs
    )

    result = reproduction._handle_estrus_not_detected_in_synch_ed(mock_outputs, mock_time.simulation_day)

    mock_outputs.events.add_event.assert_any_call(
        mock_outputs.days_born, mock_time.simulation_day, animal_constants.ESTRUS_NOT_DETECTED_NOTE
    )
    mock_outputs.events.add_event.assert_any_call(
        mock_outputs.days_born,
        mock_time.simulation_day,
        animal_constants.TAI_AFTER_ESTRUS_NOT_DETECTED_IN_SYNCH_ED_NOTE,
    )

    if expected_program_change:
        mock_outputs.events.add_event.assert_any_call(
            mock_outputs.days_born,
            mock_time.simulation_day,
            f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from {heifer_reproduction_program} to "
            f"{expected_fallback_protocol}",
        )
        assert reproduction.heifer_reproduction_program == expected_fallback_protocol

    if expected_hormone_schedule_setup:
        mock_set_up_hormone_schedule.assert_called_once_with(
            mock_outputs, mock_outputs.days_born, HeiferTAISubProtocol.SynchED_2P.value
        )

    mock_execute_hormone_schedule.assert_called_once_with(
        mock_outputs, mock_time.simulation_day, reproduction.hormone_schedule
    )

    assert reproduction.TAI_conception_rate == expected_conception_rate
    assert result == mock_outputs


@pytest.mark.parametrize(
    "heifer_reproduction_program, abortion_day, expected_repro_program_change, expected_event_calls",
    [
        (HeiferReproductionProtocol.ED, 50, False, 1),  # ED program, no program change
        (HeiferReproductionProtocol.SynchED, 50, True, 2),  # Non-ED program, expect program change to ED
    ],
)
def test_open_heifer(
    heifer_reproduction_program: HeiferReproductionProtocol,
    abortion_day: int,
    expected_repro_program_change: bool,
    expected_event_calls: int,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = heifer_reproduction_program
    reproduction.abortion_day = abortion_day
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II)
    mock_outputs.events = mock_events

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)

    result = reproduction.open_heifer(mock_outputs, mock_time.simulation_day)

    assert mock_outputs.events.add_event.call_count == expected_event_calls
    mock_outputs.events.add_event.assert_any_call(
        mock_outputs.days_born, mock_time.simulation_day, animal_constants.REBREEDING_NOTE
    )

    if expected_repro_program_change:
        mock_outputs.events.add_event.assert_any_call(
            mock_outputs.days_born,
            mock_time.simulation_day,
            f"{animal_constants.SETTING_REPRO_PROGRAM_NOTE} from "
            f"{heifer_reproduction_program} to {HeiferReproductionProtocol.ED}",
        )
        assert reproduction.heifer_reproduction_program == HeiferReproductionProtocol.ED
    else:
        assert reproduction.heifer_reproduction_program == heifer_reproduction_program

    mock_simulate_estrus.assert_called_once_with(
        mock_outputs,
        abortion_day,
        mock_time.simulation_day,
        animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
        AnimalConfig.average_estrus_cycle_heifer,
        AnimalConfig.std_estrus_cycle_heifer,
    )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "cow_reproduction_program, resynch_method, days_born, estrus_day, expected_repro_state, expected_simulate_estrus, "
    "expected_handle_open_tai, expected_handle_open_pgf, conception_rate_decrease",
    [
        (CowReproductionProtocol.ED, CowReSynchSubProtocol.Resynch_TAIafterPD, 150, 100, True, True, False, False, 1),
        (CowReproductionProtocol.TAI, CowReSynchSubProtocol.Resynch_TAIafterPD, 150, 100, True, False, False, False, 1),
        (
            CowReproductionProtocol.TAI,
            CowReSynchSubProtocol.Resynch_TAIbeforePD,
            150,
            100,
            False,
            False,
            True,
            False,
            1,
        ),
        (CowReproductionProtocol.TAI, CowReSynchSubProtocol.Resynch_PGFatPD, 150, 100, False, False, False, True, 1),
    ],
)
def test_open_cow(
    cow_reproduction_program: CowReproductionProtocol,
    resynch_method: CowReSynchSubProtocol,
    days_born: int,
    estrus_day: int,
    expected_repro_state: bool,
    expected_simulate_estrus: bool,
    expected_handle_open_tai: bool,
    expected_handle_open_pgf: bool,
    conception_rate_decrease: int,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = cow_reproduction_program
    reproduction.estrus_day = estrus_day
    reproduction.num_conception_rate_decreases = 0

    default_resynch_method = AnimalConfig.cow_resynch_method
    AnimalConfig.cow_resynch_method = resynch_method

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=days_born, days_in_milk=60)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)
    mock_enter_state = mocker.patch.object(reproduction.repro_state_manager, "enter")
    mock_handle_open_tai = mocker.patch.object(
        reproduction, "_handle_open_cow_in_tai_before_pd_resynch", return_value=mock_outputs
    )
    mock_handle_open_pgf = mocker.patch.object(
        reproduction, "_handle_open_cow_in_pgf_at_pd_resynch", return_value=mock_outputs
    )

    result = reproduction.open_cow(mock_outputs, mock_time.simulation_day)

    assert reproduction.num_conception_rate_decreases == conception_rate_decrease

    if cow_reproduction_program == CowReproductionProtocol.ED and days_born > estrus_day:
        mock_enter_state.assert_called_once_with(ReproStateEnum.WAITING_FULL_ED_CYCLE)
        assert mock_outputs.events.add_event.call_count == 2
        mock_outputs.events.add_event.assert_any_call(
            mock_outputs.days_born,
            mock_time.simulation_day,
            f"Current repro state(s): {reproduction.repro_state_manager}",
        )
        mock_simulate_estrus.assert_called_once_with(
            mock_outputs,
            days_born,
            mock_time.simulation_day,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
    else:
        if resynch_method == CowReSynchSubProtocol.Resynch_TAIafterPD:
            mock_enter_state.assert_called_once_with(ReproStateEnum.IN_OVSYNCH)
        else:
            mock_enter_state.assert_not_called()
        mock_simulate_estrus.assert_not_called()

    if expected_handle_open_tai:
        mock_handle_open_tai.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_handle_open_tai.assert_not_called()

    if expected_handle_open_pgf:
        mock_handle_open_pgf.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_handle_open_pgf.assert_not_called()

    assert result == mock_outputs
    AnimalConfig.cow_resynch_method = default_resynch_method


def test_open_cow_sets_do_not_breed_and_returns_when_dryoff_before_third_check(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    """If dry-off happens before/at the third pregnancy check and cow is not milking, mark do_not_breed and return."""
    reproduction = Reproduction()
    reproduction.num_conception_rate_decreases = 0
    reproduction.do_not_breed = False

    monkeypatch.setattr(AnimalConfig, "dry_off_day_of_pregnancy", 150)
    monkeypatch.setattr(AnimalConfig, "third_pregnancy_check_day", 200)

    data_stream = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW,
        days_born=100,
        days_in_milk=0,
    )

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus")
    mock_enter_state = mocker.patch.object(reproduction.repro_state_manager, "enter")
    mock_handle_open_tai = mocker.patch.object(
        reproduction,
        "_handle_open_cow_in_tai_before_pd_resynch",
    )
    mock_handle_open_pgf = mocker.patch.object(
        reproduction,
        "_handle_open_cow_in_pgf_at_pd_resynch",
    )

    result = reproduction.open_cow(data_stream, simulation_day=100)

    assert reproduction.do_not_breed is True
    assert reproduction.num_conception_rate_decreases == 1
    assert result is data_stream

    mock_simulate_estrus.assert_not_called()
    mock_enter_state.assert_not_called()
    mock_handle_open_tai.assert_not_called()
    mock_handle_open_pgf.assert_not_called()


@pytest.mark.parametrize(
    "animal_type, conception_rate, random_value, expected_conception_success, semen_type",
    [
        (AnimalType.HEIFER_II, 0.7, 0.5, True, "conventional"),
        (AnimalType.HEIFER_II, 0.3, 0.5, False, "sexed"),
        (AnimalType.LAC_COW, 0.8, 0.7, True, "conventional"),
        (AnimalType.LAC_COW, 0.2, 0.5, False, "sexed"),
    ],
)
def test_perform_ai(
    animal_type: AnimalType,
    conception_rate: float,
    random_value: float,
    expected_conception_success: bool,
    semen_type: str,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.conception_rate = conception_rate
    AnimalConfig.semen_type = semen_type

    mock_outputs = mock_reproduction_data_stream(animal_type=animal_type)

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 100

    mock_add_event = mocker.patch.object(mock_outputs.events, "add_event")
    mock_compare_randomized_rate = mocker.patch(
        "RUFAS.util.Utility.compare_randomized_rate_less_than", return_value=expected_conception_success
    )
    mock_increment_heifer_ai_counts = mocker.patch.object(
        reproduction, "_increment_heifer_ai_counts", return_value=mock_outputs
    )
    mock_increment_cow_ai_counts = mocker.patch.object(
        reproduction, "_increment_cow_ai_counts", return_value=mock_outputs
    )
    mock_handle_successful_heifer_conception = mocker.patch.object(
        reproduction, "_handle_successful_heifer_conception", return_value=mock_outputs
    )
    mock_handle_successful_cow_conception = mocker.patch.object(
        reproduction, "_handle_successful_cow_conception", return_value=mock_outputs
    )
    mock_increment_successful_heifer_conceptions = mocker.patch.object(
        reproduction, "_increment_successful_heifer_conceptions", return_value=mock_outputs
    )
    mock_increment_successful_cow_conceptions = mocker.patch.object(
        reproduction, "_increment_successful_cow_conceptions", return_value=mock_outputs
    )
    mock_handle_failed_heifer_conception = mocker.patch.object(
        reproduction, "_handle_failed_heifer_conception", return_value=mock_outputs
    )
    mock_handle_failed_cow_conception = mocker.patch.object(
        reproduction, "_handle_failed_cow_conception", return_value=mock_outputs
    )

    result = reproduction._perform_ai(mock_outputs, mock_time.simulation_day)

    mock_add_event.assert_any_call(mock_outputs.days_born, mock_time.simulation_day, animal_constants.AI_PERFORMED_NOTE)
    mock_add_event.assert_any_call(
        mock_outputs.days_born, mock_time.simulation_day, f"{animal_constants.INSEMINATED_W_BASE}{semen_type}"
    )

    assert reproduction.reproduction_statistics.semen_number == 1
    assert reproduction.reproduction_statistics.AI_times == 1

    if animal_type == AnimalType.HEIFER_II:
        mock_increment_heifer_ai_counts.assert_called_once_with(mock_outputs)
        mock_increment_cow_ai_counts.assert_not_called()
        if expected_conception_success:
            mock_handle_successful_heifer_conception.assert_called_once_with(mock_outputs, mock_time.simulation_day)
            mock_increment_successful_heifer_conceptions.assert_called_once_with(mock_outputs)
            mock_handle_failed_heifer_conception.assert_not_called()
        else:
            mock_handle_successful_heifer_conception.assert_not_called()
            mock_increment_successful_heifer_conceptions.assert_not_called()
            mock_handle_failed_heifer_conception.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_increment_cow_ai_counts.assert_called_once_with(mock_outputs)
        mock_increment_heifer_ai_counts.assert_not_called()
        if expected_conception_success:
            mock_handle_successful_cow_conception.assert_called_once_with(mock_outputs, mock_time.simulation_day)
            mock_increment_successful_cow_conceptions.assert_called_once_with(mock_outputs)
            mock_handle_failed_cow_conception.assert_not_called()
        else:
            mock_handle_successful_cow_conception.assert_not_called()
            mock_increment_successful_cow_conceptions.assert_not_called()
            mock_handle_failed_cow_conception.assert_called_once_with(mock_outputs, mock_time.simulation_day)

    assert result == mock_outputs
    mock_compare_randomized_rate.assert_called_once_with(conception_rate)


@pytest.mark.parametrize(
    "repro_program, expected_ai_ed, expected_ai_tai, expected_ai_synched",
    [
        (HeiferReproductionProtocol.ED, 1, 0, 0),
        (HeiferReproductionProtocol.TAI, 0, 1, 0),
        (HeiferReproductionProtocol.SynchED, 0, 0, 1),
    ],
)
def test_increment_heifer_ai_counts(
    repro_program: HeiferReproductionProtocol,
    expected_ai_ed: int,
    expected_ai_tai: int,
    expected_ai_synched: int,
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = repro_program
    reproduction_data_stream = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II)

    result = reproduction._increment_heifer_ai_counts(reproduction_data_stream)

    assert result.herd_reproduction_statistics.heifer_num_ai_performed == 1
    assert result.herd_reproduction_statistics.heifer_num_ai_performed_in_ED == expected_ai_ed
    assert result.herd_reproduction_statistics.heifer_num_ai_performed_in_TAI == expected_ai_tai
    assert result.herd_reproduction_statistics.heifer_num_ai_performed_in_SynchED == expected_ai_synched


@pytest.mark.parametrize(
    "repro_program, expected_successful_ed, expected_successful_tai, expected_successful_synched",
    [
        (HeiferReproductionProtocol.ED, 1, 0, 0),
        (HeiferReproductionProtocol.TAI, 0, 1, 0),
        (HeiferReproductionProtocol.SynchED, 0, 0, 1),
    ],
)
def test_increment_successful_heifer_conceptions(
    repro_program: HeiferReproductionProtocol,
    expected_successful_ed: int,
    expected_successful_tai: int,
    expected_successful_synched: int,
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = repro_program
    reproduction_data_stream = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II)

    result = reproduction._increment_successful_heifer_conceptions(reproduction_data_stream)

    assert result.herd_reproduction_statistics.heifer_num_successful_conceptions == 1
    assert result.herd_reproduction_statistics.heifer_num_successful_conceptions_in_ED == expected_successful_ed
    assert result.herd_reproduction_statistics.heifer_num_successful_conceptions_in_TAI == expected_successful_tai
    assert (
        result.herd_reproduction_statistics.heifer_num_successful_conceptions_in_SynchED == expected_successful_synched
    )


@pytest.mark.parametrize(
    "days_born, simulation_day",
    [
        (100, 200),
        (150, 250),
    ],
)
def test_handle_successful_heifer_conception(days_born: int, simulation_day: int, mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II, days_born=days_born)
    mock_event_add = mocker.patch.object(mock_outputs.events, "add_event")

    mock_initialize_pregnancy = mocker.patch.object(
        reproduction, "_initialize_pregnancy_parameters", return_value=mock_outputs
    )

    result = reproduction._handle_successful_heifer_conception(mock_outputs, simulation_day)

    mock_event_add.assert_called_once_with(days_born, simulation_day, animal_constants.HEIFER_PREG)
    mock_initialize_pregnancy.assert_called_once_with(mock_outputs)
    assert result == mock_outputs


@pytest.mark.parametrize(
    "animal_type, days_born, simulation_day, expected_estrus_protocol, average_estrus_cycle, std_estrus_cycle",
    [
        (
            AnimalType.HEIFER_II,
            100,
            200,
            HeiferReproductionProtocol.ED,
            AnimalConfig.average_estrus_cycle_heifer,
            AnimalConfig.std_estrus_cycle_heifer,
        ),
        (
            AnimalType.LAC_COW,
            150,
            250,
            CowReproductionProtocol.ED,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        ),
    ],
)
def test_handle_failed_heifer_conception(
    animal_type: AnimalType,
    days_born: int,
    simulation_day: int,
    expected_estrus_protocol: HeiferReproductionProtocol | CowReproductionProtocol,
    average_estrus_cycle: float,
    std_estrus_cycle: float,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = HeiferReproductionProtocol.SynchED  # Set initial protocol

    mock_outputs = mock_reproduction_data_stream(animal_type=animal_type, days_born=days_born)
    mock_event_add = mocker.patch.object(mock_outputs.events, "add_event")

    mock_set_heifer_repro = mocker.patch.object(
        reproduction, "_set_heifer_reproduction_program", return_value=mock_outputs
    )
    mock_set_cow_repro = mocker.patch.object(reproduction, "_set_cow_reproduction_program", return_value=mock_outputs)
    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)

    result = reproduction._handle_failed_heifer_conception(mock_outputs, simulation_day)

    mock_event_add.assert_any_call(days_born, simulation_day, animal_constants.HEIFER_NOT_PREG)

    if animal_type == AnimalType.HEIFER_II:
        mock_set_heifer_repro.assert_called_once_with(mock_outputs, simulation_day, HeiferReproductionProtocol.ED)
        mock_set_cow_repro.assert_not_called()
    else:
        mock_set_cow_repro.assert_called_once_with(mock_outputs, simulation_day, CowReproductionProtocol.ED)
        mock_set_heifer_repro.assert_not_called()

    mock_simulate_estrus.assert_called_once_with(
        mock_outputs,
        days_born - 1,
        simulation_day,
        animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
        average_estrus_cycle,
        std_estrus_cycle,
    )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "average_gestation_length, std_gestation_length, random_value",
    [
        (280, 5, 282),
        (290, 6, 288),
    ],
)
def test_calculate_gestation_length(
    average_gestation_length: int, std_gestation_length: float, random_value: int, mocker: MockerFixture
) -> None:
    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.average_gestation_length",
        average_gestation_length,
    )
    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.std_gestation_length", std_gestation_length
    )
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.truncnorm.rvs", return_value=random_value)

    reproduction = Reproduction()
    result = reproduction._calculate_gestation_length()
    assert result == random_value


@pytest.mark.parametrize(
    "breed, avg_weight, std_weight, random_value",
    [
        (Breed.HO, AnimalConfig.birth_weight_avg_ho, AnimalConfig.birth_weight_std_ho, 43.9),
        (Breed.JE, AnimalConfig.birth_weight_avg_je, AnimalConfig.birth_weight_std_je, 27.2),
    ],
)
def test_calculate_calf_birth_weight(
    breed: Breed, avg_weight: float, std_weight: float, random_value: float, mocker: MockerFixture
) -> None:
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.birth_weight_avg_ho", avg_weight)
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.birth_weight_std_ho", std_weight)
    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.truncnorm.rvs", return_value=random_value)

    reproduction = Reproduction()
    result = reproduction._calculate_calf_birth_weight(breed)
    assert result == random_value


@pytest.mark.parametrize(
    "days_born, breed, expected_gestation_length, expected_birth_weight",
    [
        (100, Breed.HO, 280, 43.9),
        (150, Breed.JE, 290, 27.2),
    ],
)
def test_initialize_pregnancy_parameters(
    days_born: int, breed: Breed, expected_gestation_length: int, expected_birth_weight: float, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.HEIFER_II, days_born=days_born, breed=breed)

    mock_calculate_gestation_length = mocker.patch.object(
        reproduction, "_calculate_gestation_length", return_value=expected_gestation_length
    )
    mock_calculate_calf_birth_weight = mocker.patch.object(
        reproduction, "_calculate_calf_birth_weight", return_value=expected_birth_weight
    )

    result = reproduction._initialize_pregnancy_parameters(mock_outputs)

    mock_calculate_gestation_length.assert_called_once()
    mock_calculate_calf_birth_weight.assert_called_once_with(breed)

    assert result.days_in_pregnancy == 1
    assert reproduction.abortion_day == 0
    assert reproduction.breeding_to_preg_time == days_born - AnimalConfig.heifer_breed_start_day
    assert reproduction.gestation_length == expected_gestation_length
    assert reproduction.calf_birth_weight == expected_birth_weight
    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_born, ai_day, simulation_day",
    [
        (100, 68, 200),
    ],
)
def test_heifer_pregnancy_update(days_born: int, ai_day: int, simulation_day: int, mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    reproduction.ai_day = ai_day

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II, days_born=days_born, events=MagicMock(spec=AnimalEvents)
    )

    mock_handle_pregnancy_check = mocker.patch.object(
        reproduction, "_handle_heifer_pregnancy_check", side_effect=lambda outputs, config, day: outputs
    )

    result = reproduction.heifer_pregnancy_update(mock_outputs, simulation_day)

    mock_handle_pregnancy_check.assert_called_once_with(
        mock_outputs,
        {
            "day": AnimalConfig.first_pregnancy_check_day,
            "loss_rate": AnimalConfig.first_pregnancy_check_loss_rate,
            "on_preg_loss": animal_constants.PREG_LOSS_BEFORE_1,
            "on_preg": animal_constants.PREG_CHECK_1_PREG,
            "on_not_preg": animal_constants.PREG_CHECK_1_NOT_PREG,
        },
        simulation_day,
    )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_in_pregnancy, random_value, pregnancy_check_config, expected_event," "expected_open_called",
    [
        (
            10,
            0.05,
            PregnancyCheckConfig(
                day=AnimalConfig.first_pregnancy_check_day,
                loss_rate=AnimalConfig.first_pregnancy_check_loss_rate,
                on_preg_loss=animal_constants.PREG_LOSS_BEFORE_1,
                on_preg=animal_constants.PREG_CHECK_1_PREG,
                on_not_preg=animal_constants.PREG_CHECK_1_NOT_PREG,
            ),
            animal_constants.PREG_CHECK_1_PREG,
            False,
        ),
        (
            0,
            0.05,
            PregnancyCheckConfig(
                day=AnimalConfig.first_pregnancy_check_day,
                loss_rate=AnimalConfig.first_pregnancy_check_loss_rate,
                on_preg_loss=animal_constants.PREG_LOSS_BEFORE_1,
                on_preg=animal_constants.PREG_CHECK_1_PREG,
                on_not_preg=animal_constants.PREG_CHECK_1_NOT_PREG,
            ),
            animal_constants.PREG_CHECK_1_NOT_PREG,
            True,
        ),
        (
            10,
            0.015,
            PregnancyCheckConfig(
                day=AnimalConfig.second_pregnancy_check_day,
                loss_rate=AnimalConfig.second_pregnancy_check_loss_rate,
                on_preg_loss=animal_constants.PREG_LOSS_BTWN_1_AND_2,
                on_preg=animal_constants.PREG_CHECK_2_PREG,
            ),
            animal_constants.PREG_CHECK_2_PREG,
            False,
        ),
        (
            0,
            0.05,
            PregnancyCheckConfig(
                day=AnimalConfig.third_pregnancy_check_day,
                loss_rate=AnimalConfig.third_pregnancy_check_loss_rate,
                on_preg_loss=animal_constants.PREG_LOSS_BTWN_2_AND_3,
                on_preg=animal_constants.PREG_CHECK_3_PREG,
            ),
            "Not Pregnant",
            True,
        ),
    ],
)
def test_handle_heifer_pregnancy_check(
    days_in_pregnancy: int,
    random_value: float,
    pregnancy_check_config: PregnancyCheckConfig,
    expected_event: str,
    expected_open_called: bool,
    mocker: MockerFixture,
) -> None:
    loss_rate: float = pregnancy_check_config["loss_rate"]
    reproduction = Reproduction()

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II,
        days_in_pregnancy=days_in_pregnancy,
    )
    mock_add_events = mocker.patch.object(mock_outputs.events, "add_event")

    mocker.patch("RUFAS.util.Utility.compare_randomized_rate_less_than", return_value=random_value < loss_rate)
    mock_terminate_pregnancy = mocker.patch.object(reproduction, "_terminate_pregnancy", return_value=mock_outputs)
    mock_open_heifer = mocker.patch.object(reproduction, "open_heifer", return_value=mock_outputs)

    result = reproduction._handle_heifer_pregnancy_check(mock_outputs, pregnancy_check_config, 100)

    if days_in_pregnancy:
        if random_value < loss_rate:
            mock_terminate_pregnancy.assert_called_once_with(mock_outputs, pregnancy_check_config["on_preg_loss"], 100)
        else:
            mock_add_events.assert_called_with(mock_outputs.days_born, 100, expected_event)
            mock_terminate_pregnancy.assert_not_called()
    elif "on_not_preg" in pregnancy_check_config:
        mock_open_heifer.assert_called_once_with(mock_outputs, 100)
        mock_add_events.assert_called_with(mock_outputs.days_born, 100, expected_event)

    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_in_pregnancy, random_value, repro_state, pregnancy_check_config, expected_event, expected_open_called",
    [
        (
            10,
            0.01,
            ReproStateEnum.PREGNANT,
            PregnancyCheckConfig(
                day=AnimalConfig.first_pregnancy_check_day,
                loss_rate=AnimalConfig.first_pregnancy_check_loss_rate,
                on_preg_loss=animal_constants.PREG_LOSS_BEFORE_1,
                on_preg=animal_constants.PREG_CHECK_1_PREG,
                on_not_preg=animal_constants.PREG_CHECK_1_NOT_PREG,
            ),
            animal_constants.PREG_LOSS_BEFORE_1,
            False,
        ),
        (
            10,
            0.15,
            ReproStateEnum.IN_OVSYNCH,
            PregnancyCheckConfig(
                day=AnimalConfig.second_pregnancy_check_day,
                loss_rate=AnimalConfig.second_pregnancy_check_loss_rate,
                on_preg_loss=animal_constants.PREG_LOSS_BTWN_1_AND_2,
                on_preg=animal_constants.PREG_CHECK_2_PREG,
            ),
            animal_constants.PREG_CHECK_2_PREG,
            False,
        ),
        (
            0,
            0.05,
            None,
            PregnancyCheckConfig(
                day=AnimalConfig.third_pregnancy_check_day,
                loss_rate=AnimalConfig.third_pregnancy_check_loss_rate,
                on_preg_loss=animal_constants.PREG_LOSS_BTWN_2_AND_3,
                on_preg=animal_constants.PREG_CHECK_3_PREG,
            ),
            "Not Pregnant",
            True,
        ),
        (
            0,
            0.015,
            ReproStateEnum.IN_OVSYNCH,
            {
                "day": AnimalConfig.first_pregnancy_check_day,
                "loss_rate": AnimalConfig.first_pregnancy_check_loss_rate,
                "on_preg_loss": animal_constants.PREG_LOSS_BEFORE_1,
                "on_preg": animal_constants.PREG_CHECK_1_PREG,
                "on_not_preg": animal_constants.PREG_CHECK_1_NOT_PREG,
            },
            animal_constants.PREG_CHECK_1_NOT_PREG,
            True,
        ),
    ],
)
def test_handle_cow_pregnancy_check(
    days_in_pregnancy: bool,
    random_value: float,
    repro_state: Optional[ReproStateEnum],
    pregnancy_check_config: PregnancyCheckConfig,
    expected_event: str,
    expected_open_called: bool,
    mocker: MockerFixture,
) -> None:
    loss_rate: float = pregnancy_check_config["loss_rate"]
    reproduction = Reproduction()
    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in.return_value = repro_state == ReproStateEnum.IN_OVSYNCH

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW,
        days_in_pregnancy=days_in_pregnancy,
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_add_events = mocker.patch.object(mock_events, "add_event")
    mock_outputs.events = mock_events

    mocker.patch("RUFAS.util.Utility.compare_randomized_rate_less_than", return_value=random_value < loss_rate)
    mock_terminate_pregnancy = mocker.patch.object(reproduction, "_terminate_pregnancy", return_value=mock_outputs)
    mock_open_cow = mocker.patch.object(reproduction, "open_cow", return_value=mock_outputs)
    mock_exit_ovsynch = mocker.patch.object(
        reproduction,
        "_exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected",
        return_value=mock_outputs,
    )

    result = reproduction._handle_cow_pregnancy_check(mock_outputs, pregnancy_check_config, 100)

    if days_in_pregnancy:
        if random_value < loss_rate:
            reproduction.repro_state_manager.exit.assert_called_once_with(ReproStateEnum.PREGNANT)
            mock_terminate_pregnancy.assert_called_once_with(mock_outputs, pregnancy_check_config["on_preg_loss"], 100)
        else:
            mock_add_events.assert_called_with(mock_outputs.days_born, 100, expected_event)
            if repro_state == ReproStateEnum.IN_OVSYNCH:
                mock_exit_ovsynch.assert_called_once_with(mock_outputs, 100)
            mock_terminate_pregnancy.assert_not_called()
    elif "on_not_preg" in pregnancy_check_config:
        mock_open_cow.assert_called_once_with(mock_outputs, 100)
        mock_add_events.assert_called_with(mock_outputs.days_born, 100, expected_event)

    assert result == mock_outputs


@pytest.mark.parametrize(
    "animal_type, preg_loss_const, body_weight, conceptus_weight, expected_event, expected_open_called",
    [
        (AnimalType.HEIFER_II, "Pregnancy Lost", 500.0, 10.0, "Pregnancy Lost", "open_heifer"),
        (AnimalType.LAC_COW, "Pregnancy Terminated", 600.0, 15.0, "Pregnancy Terminated", "open_cow"),
    ],
)
def test_terminate_pregnancy(
    animal_type: AnimalType,
    preg_loss_const: str,
    body_weight: float,
    conceptus_weight: float,
    expected_event: str,
    expected_open_called: str,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.conceptus_weight = conceptus_weight
    reproduction.calf_birth_weight = 8.0

    mock_outputs = mock_reproduction_data_stream(
        animal_type=animal_type, body_weight=body_weight, phosphorus_for_gestation_required_for_calf=2.0
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_open_heifer = mocker.patch.object(reproduction, "open_heifer", return_value=mock_outputs)
    mock_open_cow = mocker.patch.object(reproduction, "open_cow", return_value=mock_outputs)

    result = reproduction._terminate_pregnancy(mock_outputs, preg_loss_const, 100)

    mock_outputs.events.add_event.assert_any_call(mock_outputs.days_born, 100, expected_event)
    if expected_open_called == "open_heifer":
        mock_open_heifer.assert_called_once_with(mock_outputs, 100)
        mock_open_cow.assert_not_called()
    else:
        mock_open_cow.assert_called_once_with(mock_outputs, 100)
        mock_open_heifer.assert_not_called()

    assert result == mock_outputs
    assert result.body_weight == body_weight - conceptus_weight
    assert reproduction.conceptus_weight == 0
    assert reproduction.calf_birth_weight == 0
    assert result.phosphorus_for_gestation_required_for_calf == 0
    assert result.days_in_pregnancy == 0
    assert reproduction.abortion_day == result.days_born


@pytest.mark.parametrize(
    "should_decrease_in_rebreeding, num_decreases, decrease_rate, should_decrease_by_parity, initial_conception_rate, "
    "expected_conception_rate",
    [
        (True, 2, 0.02, False, 0.5, 0.46),  # Conception rate decreases by rebreeding count only
        (True, 3, 0.01, False, 0.6, 0.57),  # Conception rate decreases by rebreeding count only
        (False, 1, 0.03, True, 0.5, 0.48),  # Conception rate decreases by parity only
        (False, 0, 0.02, True, 0.7, 0.68),  # Conception rate decreases by parity only
        (True, 2, 0.02, True, 0.6, 0.54),  # Conception rate decreases by both factors
        (False, 0, 0.02, False, 0.7, 0.7),  # No decrease in conception rate
    ],
)
def test_calculate_conception_rate_on_ai_day(
    should_decrease_in_rebreeding: bool,
    num_decreases: int,
    decrease_rate: float,
    should_decrease_by_parity: bool,
    initial_conception_rate: float,
    expected_conception_rate: float,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.should_decrease_conception_rate_in_rebreeding",
        should_decrease_in_rebreeding,
    )
    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.conception_rate_decrease", decrease_rate
    )
    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.should_decrease_conception_rate_by_parity",
        should_decrease_by_parity,
    )
    reproduction = Reproduction()
    reproduction.num_conception_rate_decreases = num_decreases
    reproduction.conception_rate = initial_conception_rate

    mock_decrease_by_parity = mocker.patch.object(
        reproduction, "_decrease_conception_rate_by_parity", return_value=expected_conception_rate
    )

    reproduction._calculate_conception_rate_on_ai_day()

    if should_decrease_in_rebreeding:
        expected_after_rebreeding = initial_conception_rate - (num_decreases * decrease_rate)
    else:
        expected_after_rebreeding = initial_conception_rate

    if should_decrease_by_parity:
        mock_decrease_by_parity.assert_called_once_with(reproduction.calves, expected_after_rebreeding)
    else:
        mock_decrease_by_parity.assert_not_called()

    assert reproduction.conception_rate == expected_conception_rate


def test_enter_ovsynch_repro_state(mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    reproduction_data_stream = mock_reproduction_data_stream(AnimalType.LAC_COW)
    mock_enter_repro_state = mocker.patch.object(reproduction.repro_state_manager, "enter")

    simulation_day = 100
    result = reproduction._enter_ovsynch_repro_state(reproduction_data_stream, simulation_day)

    assert result == reproduction_data_stream
    mock_enter_repro_state.assert_called_once_with(ReproStateEnum.IN_OVSYNCH)


@pytest.mark.parametrize(
    "is_in_empty_state, is_in_enter_herd, days_born, estrus_day, expected_repro_state, expect_estrus_event",
    [
        (True, False, 100, 100, ReproStateEnum.FRESH, True),  # In empty state, estrus day matches
        (False, True, 120, 100, ReproStateEnum.FRESH, True),  # In 'ENTER_HERD_FROM_INIT' state, estrus day past
        (False, False, 110, 100, None, False),  # Not in relevant states, estrus day ahead
    ],
)
def test_repeat_estrus_simulation_before_vwp(
    is_in_empty_state: bool,
    is_in_enter_herd: bool,
    days_born: int,
    estrus_day: int,
    expected_repro_state: ReproStateEnum | None,
    expect_estrus_event: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.estrus_day = estrus_day
    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in_empty_state.return_value = is_in_empty_state
    reproduction.repro_state_manager.is_in.return_value = is_in_enter_herd

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=days_born)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_enter_repro_state = mocker.patch.object(reproduction.repro_state_manager, "enter")
    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)

    result = reproduction._repeat_estrus_simulation_before_vwp(mock_outputs, 100)

    if expected_repro_state:
        mock_enter_repro_state.assert_called_once_with(expected_repro_state)
        mock_outputs.events.add_event.assert_called()
    else:
        mock_enter_repro_state.assert_not_called()

    if expect_estrus_event:
        mock_outputs.events.add_event.assert_called()
        mock_simulate_estrus.assert_called_once_with(
            mock_outputs,
            days_born,
            100,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
    else:
        mock_simulate_estrus.assert_called_once_with(
            mock_outputs,
            days_born,
            100,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "is_in_ovsynch, expected_enter_state, days_born, expected_conception_rate, expected_ai_day",
    [
        (True, ReproStateEnum.ESTRUS_DETECTED, 100, AnimalConfig.cow_estrus_conception_rate, 101),
        # In Ovsynch, estrus detected
        (False, ReproStateEnum.ESTRUS_DETECTED, 120, AnimalConfig.cow_estrus_conception_rate, 121),
        # Not in Ovsynch, estrus detected
    ],
)
def test_setup_ai_day_after_estrus_detected(
    is_in_ovsynch: bool,
    expected_enter_state: ReproStateEnum,
    days_born: int,
    expected_conception_rate: float,
    expected_ai_day: int,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in.return_value = is_in_ovsynch
    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW,
        days_born=days_born,
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_exit_ovsynch_program = mocker.patch.object(
        reproduction,
        "_exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected",
        return_value=mock_outputs,
    )
    mock_enter_state = mocker.patch.object(reproduction.repro_state_manager, "enter")

    result = reproduction._setup_ai_day_after_estrus_detected(mock_outputs, 100)

    if is_in_ovsynch:
        mock_exit_ovsynch_program.assert_called_once_with(mock_outputs, 100)
    else:
        mock_exit_ovsynch_program.assert_not_called()

    mock_enter_state.assert_called_once_with(expected_enter_state)

    mock_outputs.events.add_event.assert_any_call(
        days_born, 100, f"Current repro state(s): {reproduction.repro_state_manager}"
    )
    mock_outputs.events.add_event.assert_any_call(
        days_born, 100, f"{animal_constants.AI_DAY_SCHEDULED_NOTE} on day {expected_ai_day}"
    )

    assert reproduction.conception_rate == expected_conception_rate
    assert reproduction.ai_day == expected_ai_day
    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_born, avg_estrus_cycle, std_estrus_cycle",
    [
        (100, AnimalConfig.average_estrus_cycle_cow, AnimalConfig.std_estrus_cycle_cow),
    ],
)
def test_simulate_full_estrus_cycle(
    days_born: int, avg_estrus_cycle: float, std_estrus_cycle: float, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    reproduction.repro_state_manager = MagicMock()
    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=days_born)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)
    mock_enter_state = mocker.patch.object(reproduction.repro_state_manager, "enter")

    result = reproduction._simulate_full_estrus_cycle(mock_outputs, 100)

    mock_enter_state.assert_called_once_with(ReproStateEnum.WAITING_FULL_ED_CYCLE, keep_existing=True)
    mock_outputs.events.add_event.assert_any_call(
        days_born, 100, f"Current repro state(s): {reproduction.repro_state_manager}"
    )

    mock_simulate_estrus.assert_called_once_with(
        mock_outputs, days_born, 100, animal_constants.ESTRUS_DAY_SCHEDULED_NOTE, avg_estrus_cycle, std_estrus_cycle
    )
    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_born, avg_estrus_cycle, std_estrus_cycle",
    [
        (150, AnimalConfig.average_estrus_cycle_cow, AnimalConfig.std_estrus_cycle_cow),
    ],
)
def test_simulate_full_estrus_cycle_before_ovsynch(
    days_born: int, avg_estrus_cycle: float, std_estrus_cycle: float, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    reproduction.repro_state_manager = MagicMock()
    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=days_born)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)
    mock_enter_state = mocker.patch.object(reproduction.repro_state_manager, "enter")

    result = reproduction._simulate_full_estrus_cycle_before_ovsynch(mock_outputs, 100)

    mock_enter_state.assert_called_once_with(ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH)
    mock_outputs.events.add_event.assert_any_call(
        days_born, 100, f"Current repro state(s): {reproduction.repro_state_manager}"
    )

    mock_simulate_estrus.assert_called_once_with(
        mock_outputs, days_born, 100, animal_constants.ESTRUS_DAY_SCHEDULED_NOTE, avg_estrus_cycle, std_estrus_cycle
    )
    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_born, schedule, actions, expected_presynch_end, expected_ovsynch_end",
    [
        (100, {100: {"set_presynch_end": True}}, {"set_presynch_end": True}, True, False),
        (150, {150: {"set_ovsynch_end": True}}, {"set_ovsynch_end": True}, False, True),
        (200, {}, {}, False, False),  # No actions in schedule
    ],
)
def test_execute_cow_hormone_delivery_schedule(
    days_born: int,
    schedule: dict[int, dict[str, bool]],
    actions: dict[str, bool],
    expected_presynch_end: bool,
    expected_ovsynch_end: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.repro_state_manager = MagicMock()
    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=days_born)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_execute_hormone_delivery = mocker.patch.object(
        reproduction, "_execute_hormone_delivery_schedule", return_value=mock_outputs
    )

    result = reproduction._execute_cow_hormone_delivery_schedule(mock_outputs, 100, schedule)

    mock_execute_hormone_delivery.assert_called_once_with(mock_outputs, 100, schedule)

    if expected_presynch_end:
        mock_outputs.events.add_event.assert_any_call(
            days_born,
            100,
            f"{animal_constants.PRESYNCH_PERIOD_END}: {AnimalConfig.cow_presynch_method}",
        )
        reproduction.repro_state_manager.exit.assert_called_once_with(ReproStateEnum.IN_PRESYNCH)
        reproduction.repro_state_manager.enter.assert_called_once_with(ReproStateEnum.HAS_DONE_PRESYNCH)

    if expected_ovsynch_end:
        mock_outputs.events.add_event.assert_any_call(
            days_born,
            100,
            f"{animal_constants.OVSYNCH_PERIOD_END_NOTE}: {AnimalConfig.cow_ovsynch_method}",
        )
        reproduction.repro_state_manager.exit.assert_called_once_with(ReproStateEnum.IN_OVSYNCH)

    assert result == mock_outputs


@pytest.mark.parametrize(
    "previous_ai_day, program_to_enter",
    [
        (0, "PreSynch"),
        (105, "PreSynch"),
        (0, "OvSynch"),
        (105, "OvSynch"),
    ],
)
def test_reset_ai_day_if_needed(previous_ai_day: int, program_to_enter: str, mocker: MockerFixture) -> None:
    """Unit test for _reset_ai_day_if_needed in Reproduction class"""
    reproduction = Reproduction()
    reproduction.ai_day = previous_ai_day

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=100)
    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_add_events = mocker.patch.object(mock_events, "add_event")
    mock_outputs.events = mock_events

    reproduction._reset_ai_day_if_needed(program_to_enter, mock_outputs, 100)

    assert reproduction.ai_day == 0
    if previous_ai_day > 0:
        mock_add_events.assert_called_once_with(
            100,
            100,
            f"Resetting the pre-existing AI day to enter {program_to_enter} period.",
        )


@pytest.mark.parametrize(
    "should_setup_presynch, expected_event_called",
    [
        (True, True),  # Should set up presynch and log an event
        (False, False),  # Should not set up presynch
    ],
)
def test_setup_presynch_on_presynch_start_day_if_valid(
    should_setup_presynch: bool, expected_event_called: bool, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=100)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_should_setup_presynch = mocker.patch.object(
        reproduction, "_should_set_up_hormone_delivery_for_presynch", return_value=(should_setup_presynch, mock_outputs)
    )
    mock_set_up_hormone_schedule = mocker.patch.object(
        reproduction, "_set_up_hormone_schedule", return_value=mock_outputs
    )

    result = reproduction._setup_presynch_on_presynch_start_day_if_valid(mock_outputs, 100)

    mock_should_setup_presynch.assert_called_once_with(mock_outputs, 100)

    if should_setup_presynch:
        mock_set_up_hormone_schedule.assert_called_once_with(mock_outputs, 100, AnimalConfig.cow_presynch_method.value)
        mock_outputs.events.add_event.assert_called_once_with(
            100,
            100,
            f"{animal_constants.PRESYNCH_PERIOD_START}: {AnimalConfig.cow_presynch_method}",
        )
    else:
        mock_set_up_hormone_schedule.assert_not_called()
        mock_outputs.events.add_event.assert_not_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "is_empty_state, is_enter_herd_from_init, expected_enter_fresh",
    [
        (True, False, True),  # Empty state, should enter fresh
        (False, True, True),  # In 'ENTER_HERD_FROM_INIT' state, should enter fresh
        (False, False, False),  # Neither empty nor 'ENTER_HERD_FROM_INIT', should not enter fresh
    ],
)
def test_enter_fresh_state_if_in_empty_state(
    is_empty_state: bool, is_enter_herd_from_init: bool, expected_enter_fresh: bool
) -> None:
    reproduction = Reproduction()
    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in_empty_state.return_value = is_empty_state
    reproduction.repro_state_manager.is_in.return_value = is_enter_herd_from_init

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_born=100, events=MagicMock(spec=AnimalEvents)
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    result = reproduction._enter_fresh_state_if_in_empty_state(mock_outputs, 100)

    if expected_enter_fresh:
        reproduction.repro_state_manager.enter.assert_called_once_with(ReproStateEnum.FRESH)
        mock_outputs.events.add_event.assert_called_once_with(
            100,
            100,
            f"Current repro state(s): {reproduction.repro_state_manager}",
        )
    else:
        reproduction.repro_state_manager.enter.assert_not_called()
        mock_outputs.events.add_event.assert_not_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "should_setup_ovsynch, expected_event_called, ovsynch_conception_rate",
    [
        (True, True, 0.5),  # Should set up ovsynch and log an event
        (False, False, 0.0),  # Should not set up ovsynch
    ],
)
def test_setup_ovsynch_on_ovsynch_start_day_if_valid(
    should_setup_ovsynch: bool, expected_event_called: bool, ovsynch_conception_rate: float, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_born=100, events=MagicMock(spec=AnimalEvents)
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.ovsynch_program_conception_rate",
        ovsynch_conception_rate,
    )

    mock_should_setup_ovsynch = mocker.patch.object(
        reproduction, "_should_set_up_hormone_delivery_for_ovsynch", return_value=(should_setup_ovsynch, mock_outputs)
    )
    mock_set_up_hormone_schedule = mocker.patch.object(
        reproduction, "_set_up_hormone_schedule", return_value=mock_outputs
    )

    result = reproduction._setup_ovsynch_on_ovsynch_start_day_if_valid(mock_outputs, 100)

    mock_should_setup_ovsynch.assert_called_once_with(mock_outputs, 100)

    if should_setup_ovsynch:
        mock_set_up_hormone_schedule.assert_called_once_with(mock_outputs, 100, AnimalConfig.cow_ovsynch_method.value)
        assert reproduction.TAI_conception_rate == ovsynch_conception_rate
        mock_outputs.events.add_event.assert_called_once_with(
            100,
            100,
            f"{animal_constants.OVSYNCH_PERIOD_START_NOTE}: {AnimalConfig.cow_ovsynch_method}",
        )
    else:
        mock_set_up_hormone_schedule.assert_not_called()
        mock_outputs.events.add_event.assert_not_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "reproduction_program, presynch_method, days_in_milk, hormone_schedule, in_fresh_state, in_presynch,"
    "expected_setup",
    [
        (
            CowReproductionProtocol.TAI,
            CowPreSynchSubProtocol.Presynch_DoubleOvSynch,
            AnimalConfig.presynch_program_start_day,
            {},
            True,
            False,
            True,
        ),
        (
            CowReproductionProtocol.ED,
            CowPreSynchSubProtocol.Presynch_DoubleOvSynch,
            AnimalConfig.presynch_program_start_day,
            {},
            True,
            False,
            False,
        ),
        (
            CowReproductionProtocol.TAI,
            CowPreSynchSubProtocol.Presynch_PreSynch,
            AnimalConfig.presynch_program_start_day,
            {},
            False,
            True,
            True,
        ),
        (
            CowReproductionProtocol.TAI,
            CowPreSynchSubProtocol.Presynch_G6G,
            AnimalConfig.presynch_program_start_day + 1,
            {},
            True,
            False,
            True,
        ),
        (CowReproductionProtocol.TAI, "None", AnimalConfig.presynch_program_start_day, {}, True, False, False),
        (
            CowReproductionProtocol.TAI,
            CowPreSynchSubProtocol.Presynch_DoubleOvSynch,
            AnimalConfig.presynch_program_start_day,
            {0: {"dummy": "schedule"}},
            True,
            False,
            False,
        ),
        (
            CowReproductionProtocol.TAI,
            CowPreSynchSubProtocol.Presynch_PreSynch,
            AnimalConfig.presynch_program_start_day,
            {},
            False,
            False,
            False,
        ),
    ],
)
def test_should_set_up_hormone_delivery_for_presynch(
    reproduction_program: CowReproductionProtocol,
    presynch_method: CowPreSynchSubProtocol,
    days_in_milk: int,
    hormone_schedule: dict[int, dict[str, Any]],
    in_fresh_state: bool,
    in_presynch: bool,
    expected_setup: bool,
    mocker: MockerFixture,
) -> None:
    default_cow_presynch_method = AnimalConfig.cow_presynch_method
    AnimalConfig.cow_presynch_method = presynch_method

    reproduction = Reproduction()
    reproduction.cow_reproduction_program = reproduction_program
    reproduction.hormone_schedule = hormone_schedule

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_in_milk=days_in_milk, events=MagicMock(spec=AnimalEvents)
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.cow_presynch_method", presynch_method)
    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.presynch_program_start_day",
        AnimalConfig.presynch_program_start_day,
    )
    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in_empty_state.return_value = in_fresh_state
    reproduction.repro_state_manager.is_in_any.return_value = in_fresh_state or in_presynch
    reproduction.repro_state_manager.is_in.return_value = in_presynch

    result, outputs = reproduction._should_set_up_hormone_delivery_for_presynch(mock_outputs, 100)

    assert result == expected_setup

    if expected_setup and (in_fresh_state or in_presynch):
        reproduction.repro_state_manager.enter.assert_called_once_with(ReproStateEnum.IN_PRESYNCH)
        mock_outputs.events.add_event.assert_called_once_with(
            mock_outputs.days_born,
            100,
            f"Current repro state(s): {reproduction.repro_state_manager}",
        )
    else:
        reproduction.repro_state_manager.enter.assert_not_called()
        mock_outputs.events.add_event.assert_not_called()

    assert outputs == mock_outputs

    AnimalConfig.cow_presynch_method = default_cow_presynch_method


@pytest.mark.parametrize(
    "reproduction_program, ovsynch_method, days_in_milk, hormone_schedule, in_presynch, in_ovsynch, expected_setup",
    [
        (
            CowReproductionProtocol.TAI,
            CowTAISubProtocol.TAI_OvSynch_48,
            AnimalConfig.ovsynch_program_start_day,
            {},
            True,
            False,
            False,
        ),  # Valid setup conditions
        (
            CowReproductionProtocol.ED,
            CowPreSynchSubProtocol.Presynch_DoubleOvSynch,
            AnimalConfig.ovsynch_program_start_day,
            {},
            True,
            False,
            False,
        ),  # Non-TAI program, no setup
        (
            CowReproductionProtocol.TAI,
            CowTAISubProtocol.TAI_OvSynch_56,
            AnimalConfig.ovsynch_program_start_day,
            {},
            False,
            True,
            True,
        ),  # Already in Ovsynch
        (
            CowReproductionProtocol.TAI,
            CowTAISubProtocol.TAI_OvSynch_56,
            AnimalConfig.ovsynch_program_start_day + 1,
            {},
            False,
            True,
            True,
        ),  # After start day
        (CowReproductionProtocol.TAI, "None", AnimalConfig.ovsynch_program_start_day, {}, True, False, False),
        # Invalid Ovsynch method
        (
            CowReproductionProtocol.TAI,
            CowPreSynchSubProtocol.Presynch_DoubleOvSynch,
            AnimalConfig.ovsynch_program_start_day,
            {0: {"dummy": "schedule"}},
            True,
            False,
            False,
        ),  # Hormone schedule exists
        (
            CowReproductionProtocol.TAI,
            CowTAISubProtocol.TAI_5d_CoSynch,
            AnimalConfig.ovsynch_program_start_day,
            {},
            False,
            False,
            False,
        ),  # Not in Presynch or Ovsynch
    ],
)
def test_should_set_up_hormone_delivery_for_ovsynch(
    reproduction_program: CowReproductionProtocol,
    ovsynch_method: CowTAISubProtocol,
    days_in_milk: int,
    hormone_schedule: dict[int, dict[str, Any]],
    in_presynch: bool,
    in_ovsynch: bool,
    expected_setup: bool,
    mocker: MockerFixture,
) -> None:
    default_cow_ovsynch_method = AnimalConfig.cow_ovsynch_method
    AnimalConfig.cow_ovsynch_method = ovsynch_method

    reproduction = Reproduction()
    reproduction.cow_reproduction_program = reproduction_program
    reproduction.hormone_schedule = hormone_schedule

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_in_milk=days_in_milk, events=MagicMock(spec=AnimalEvents)
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.cow_ovsynch_method", ovsynch_method)
    mocker.patch(
        "RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig.ovsynch_program_start_day",
        AnimalConfig.ovsynch_program_start_day,
    )

    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in_any.return_value = in_ovsynch
    reproduction.repro_state_manager.is_in.return_value = in_presynch
    reproduction.repro_state_manager.is_in_empty_state.return_value = in_ovsynch

    result, outputs = reproduction._should_set_up_hormone_delivery_for_ovsynch(mock_outputs, 100)

    assert result == expected_setup

    if expected_setup and (in_presynch or in_ovsynch):
        reproduction.repro_state_manager.enter.assert_called_once_with(ReproStateEnum.IN_OVSYNCH)
        mock_outputs.events.add_event.assert_called_once_with(
            mock_outputs.days_born,
            100,
            f"Current repro state(s): {reproduction.repro_state_manager}",
        )
    else:
        reproduction.repro_state_manager.enter.assert_not_called()
        mock_outputs.events.add_event.assert_not_called()

    assert outputs == mock_outputs

    AnimalConfig.cow_ovsynch_method = default_cow_ovsynch_method


def test_increment_cow_ai_counts() -> None:
    reproduction = Reproduction()
    reproduction_data_stream = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW)

    initial_ai_count = reproduction_data_stream.herd_reproduction_statistics.cow_num_ai_performed
    result = reproduction._increment_cow_ai_counts(reproduction_data_stream)

    assert result.herd_reproduction_statistics.cow_num_ai_performed == initial_ai_count + 1


@pytest.mark.parametrize(
    "protocol, expected_field",
    [
        (CowReproductionProtocol.ED, "cow_num_ai_performed_in_ED"),
        (CowReproductionProtocol.TAI, "cow_num_ai_performed_in_TAI"),
    ],
    ids=["ed_program", "tai_program"],
)
def test_increment_cow_ai_counts_increments_program_specific_counters(
    protocol: CowReproductionProtocol,
    expected_field: str,
) -> None:
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = protocol

    reproduction_data_stream = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW)
    stats = reproduction_data_stream.herd_reproduction_statistics

    initial_total = stats.total_num_ai_performed
    initial_cow = stats.cow_num_ai_performed
    initial_ed = stats.cow_num_ai_performed_in_ED
    initial_tai = stats.cow_num_ai_performed_in_TAI
    initial_ed_tai = stats.cow_num_ai_performed_in_ED_TAI

    result = reproduction._increment_cow_ai_counts(reproduction_data_stream)
    new_stats = result.herd_reproduction_statistics

    assert new_stats.total_num_ai_performed == initial_total + 1
    assert new_stats.cow_num_ai_performed == initial_cow + 1

    if expected_field == "cow_num_ai_performed_in_ED":
        assert new_stats.cow_num_ai_performed_in_ED == initial_ed + 1
        assert new_stats.cow_num_ai_performed_in_TAI == initial_tai
        assert new_stats.cow_num_ai_performed_in_ED_TAI == initial_ed_tai
    elif expected_field == "cow_num_ai_performed_in_TAI":
        assert new_stats.cow_num_ai_performed_in_TAI == initial_tai + 1
        assert new_stats.cow_num_ai_performed_in_ED == initial_ed
        assert new_stats.cow_num_ai_performed_in_ED_TAI == initial_ed_tai


def test_increment_successful_cow_conceptions() -> None:
    reproduction = Reproduction()
    reproduction.herd_reproduction_statistics = HerdReproductionStatistics()
    reproduction_data_stream = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW)

    initial_conception_count = reproduction.herd_reproduction_statistics.cow_num_successful_conceptions
    result = reproduction._increment_successful_cow_conceptions(reproduction_data_stream)

    assert result.herd_reproduction_statistics.cow_num_successful_conceptions == initial_conception_count + 1


@pytest.mark.parametrize(
    "protocol, expected_field",
    [
        (CowReproductionProtocol.ED, "cow_num_successful_conceptions_in_ED"),
        (CowReproductionProtocol.TAI, "cow_num_successful_conceptions_in_TAI"),
    ],
    ids=["ed_program", "tai_program"],
)
def test_increment_successful_cow_conceptions_increments_program_specific_counters(
    protocol: CowReproductionProtocol,
    expected_field: str,
) -> None:
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = protocol

    reproduction_data_stream = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW)
    stats = reproduction_data_stream.herd_reproduction_statistics

    initial_total = stats.total_num_successful_conceptions
    initial_cow = stats.cow_num_successful_conceptions
    initial_ed = stats.cow_num_successful_conceptions_in_ED
    initial_tai = stats.cow_num_successful_conceptions_in_TAI
    initial_ed_tai = stats.cow_num_successful_conceptions_in_ED_TAI

    result = reproduction._increment_successful_cow_conceptions(reproduction_data_stream)
    new_stats = result.herd_reproduction_statistics

    assert new_stats.total_num_successful_conceptions == initial_total + 1
    assert new_stats.cow_num_successful_conceptions == initial_cow + 1

    if expected_field == "cow_num_successful_conceptions_in_ED":
        assert new_stats.cow_num_successful_conceptions_in_ED == initial_ed + 1
        assert new_stats.cow_num_successful_conceptions_in_TAI == initial_tai
        assert new_stats.cow_num_successful_conceptions_in_ED_TAI == initial_ed_tai
    elif expected_field == "cow_num_successful_conceptions_in_TAI":
        assert new_stats.cow_num_successful_conceptions_in_TAI == initial_tai + 1
        assert new_stats.cow_num_successful_conceptions_in_ED == initial_ed
        assert new_stats.cow_num_successful_conceptions_in_ED_TAI == initial_ed_tai


@pytest.mark.parametrize(
    "days_in_milk, estrus_day, repro_state, "
    "expected_repeat_estrus_simulation, expected_simulate_estrus, expected_handle_estrus_not_detected",
    [
        (5, 0, ReproStateEnum.ENTER_HERD_FROM_INIT, True, False, False),
        (50, 100, ReproStateEnum.ENTER_HERD_FROM_INIT, True, False, False),
        (55, 95, ReproStateEnum.ENTER_HERD_FROM_INIT, False, True, False),
        (75, 0, ReproStateEnum.FRESH, False, False, True),
    ],
)
def test_execute_cow_ed_tai_protocol(
    days_in_milk: int,
    estrus_day: int,
    repro_state: ReproStateEnum,
    expected_repeat_estrus_simulation: bool,
    expected_simulate_estrus: bool,
    expected_handle_estrus_not_detected: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.estrus_day = estrus_day
    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in.return_value = repro_state == ReproStateEnum.ENTER_HERD_FROM_INIT
    reproduction.repro_state_manager.is_in_any.return_value = repro_state in {
        ReproStateEnum.FRESH,
        ReproStateEnum.ENTER_HERD_FROM_INIT,
    }

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_in_milk=days_in_milk, days_born=100, events=MagicMock(spec=AnimalEvents)
    )

    mock_repeat_estrus_simulation = mocker.patch.object(
        reproduction, "_repeat_estrus_simulation_before_vwp", return_value=mock_outputs
    )
    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)
    mock_handle_estrus_not_detected = mocker.patch.object(
        reproduction, "_handle_estrus_not_detected_before_ovsynch_start_day", return_value=mock_outputs
    )

    result = reproduction.execute_cow_ed_tai_protocol(mock_outputs, 100)

    if expected_repeat_estrus_simulation:
        mock_repeat_estrus_simulation.assert_called_once_with(mock_outputs, 100)
    else:
        mock_repeat_estrus_simulation.assert_not_called()

    if expected_simulate_estrus:
        mock_simulate_estrus.assert_called_once_with(
            mock_outputs,
            mock_outputs.days_born,
            100,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
    else:
        mock_simulate_estrus.assert_not_called()

    if expected_handle_estrus_not_detected:
        mock_handle_estrus_not_detected.assert_called_once_with(mock_outputs, 100)
    else:
        mock_handle_estrus_not_detected.assert_not_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "initial_state, expected_states, expected_events",
    [
        (ReproStateEnum.ENTER_HERD_FROM_INIT, [ReproStateEnum.IN_OVSYNCH], ["Current repro state(s):"]),
        (
            ReproStateEnum.WAITING_FULL_ED_CYCLE_BEFORE_OVSYNCH,
            [ReproStateEnum.IN_OVSYNCH],
            [
                animal_constants.ESTRUS_NOT_DETECTED_BETWEEN_VWP_AND_OVSYNCH_START_DAY_NOTE,
                animal_constants.CANCEL_ESTRUS_DETECTION_NOTE,
                "Current repro state(s):",
            ],
        ),
        (
            ReproStateEnum.FRESH,
            [ReproStateEnum.IN_OVSYNCH],
            [animal_constants.NO_ED_INSTITUTED_BEFORE_OVSYNCH_IN_ED_TAI_NOTE, "Current repro state(s):"],
        ),
    ],
)
def test_handle_estrus_not_detected_before_ovsynch_start_day(
    initial_state: ReproStateEnum,
    expected_states: list[ReproStateEnum],
    expected_events: list[str],
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.is_in.side_effect = lambda state: state == initial_state
    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_born=100, events=MagicMock(spec=AnimalEvents)
    )

    mock_add_events = mocker.patch.object(mock_outputs.events, "add_event")

    result = reproduction._handle_estrus_not_detected_before_ovsynch_start_day(mock_outputs, 100)

    for state in expected_states:
        reproduction.repro_state_manager.enter.assert_any_call(state)

    for _ in expected_events:
        mock_add_events.assert_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "calves, initial_conception_rate, expected_conception_rate",
    [
        (1, 0.5, 0.5),  # Parity 1: no adjustment
        (2, 0.5, 0.45),  # Parity 2: decrease by 0.05
        (3, 0.5, 0.4),  # Parity 3 or more: decrease by 0.1
        (5, 0.6, 0.5),  # Parity 5 or more: decrease by 0.1
    ],
)
def test_decrease_conception_rate_by_parity(
    calves: int, initial_conception_rate: float, expected_conception_rate: float
) -> None:
    reproduction = Reproduction()

    result = reproduction._decrease_conception_rate_by_parity(calves, initial_conception_rate)

    assert result == expected_conception_rate


@pytest.mark.parametrize(
    "calves, cow_reproduction_program, resynch_method, expected_ovsynch_scheduled",
    [
        (0, CowReproductionProtocol.TAI, CowReSynchSubProtocol.Resynch_TAIbeforePD, True),
        (1, CowReproductionProtocol.ED_TAI, CowReSynchSubProtocol.Resynch_TAIbeforePD, True),
        (2, CowReproductionProtocol.TAI, CowReSynchSubProtocol.Resynch_TAIafterPD, False),
        (0, CowReproductionProtocol.ED, CowReSynchSubProtocol.Resynch_TAIbeforePD, False),
    ],
)
def test_handle_successful_cow_conception(
    calves: int,
    cow_reproduction_program: CowReproductionProtocol,
    resynch_method: CowReSynchSubProtocol,
    expected_ovsynch_scheduled: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.calves = calves
    reproduction.cow_reproduction_program = cow_reproduction_program

    default_resynch_method = AnimalConfig.cow_resynch_method
    AnimalConfig.cow_resynch_method = resynch_method

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW,
        breed=Breed.HO,
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_events.get_most_recent_date = MagicMock(return_value=mock_outputs.days_born - 100)
    mock_outputs.events = mock_events

    mock_calculate_gestation_length = mocker.patch.object(reproduction, "_calculate_gestation_length", return_value=280)
    mock_calculate_calf_birth_weight = mocker.patch.object(
        reproduction, "_calculate_calf_birth_weight", return_value=43.9
    )
    mock_schedule_ovsynch = mocker.patch.object(
        reproduction, "_schedule_ovsynch_program_in_advance", return_value=mock_outputs
    )

    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.enter = MagicMock()

    result = reproduction._handle_successful_cow_conception(mock_outputs, 100)

    # Validate the conception-related events and updates
    mock_outputs.events.add_event.assert_any_call(
        mock_outputs.days_born,
        100,
        f"{animal_constants.SUCCESSFUL_CONCEPTION}, with conception rate at {reproduction.conception_rate}",
    )
    mock_outputs.events.add_event.assert_any_call(mock_outputs.days_born, 100, animal_constants.COW_PREG)
    assert result.days_in_pregnancy == 1
    assert call(ReproStateEnum.PREGNANT) in reproduction.repro_state_manager.enter.call_args_list
    # reproduction.repro_state_manager.enter.assert_has_calls(call(ReproStateEnum.PREGNANT))

    # Check if gestation length and birth weight calculations were called
    mock_calculate_gestation_length.assert_called_once()
    mock_calculate_calf_birth_weight.assert_called_once_with(mock_outputs.breed)

    # Check if calving-to-pregnancy time is calculated when calves > 0
    if calves > 0:
        assert reproduction.reproduction_statistics.calving_to_pregnancy_time == 100

    # Verify OvSynch scheduling based on protocol
    if expected_ovsynch_scheduled:
        mock_schedule_ovsynch.assert_called_once_with(mock_outputs, 100)
        reproduction.repro_state_manager.enter.assert_any_call(ReproStateEnum.IN_OVSYNCH, keep_existing=True)
    else:
        mock_schedule_ovsynch.assert_not_called()

    assert result == mock_outputs

    AnimalConfig.cow_resynch_method = default_resynch_method


@pytest.mark.parametrize(
    "cow_reproduction_program, resynch_method, expected_estrus_simulated, expected_ovsynch_scheduled, keep_existing",
    [
        (CowReproductionProtocol.ED, CowReSynchSubProtocol.Resynch_TAIbeforePD, True, False, False),
        (CowReproductionProtocol.ED_TAI, CowReSynchSubProtocol.Resynch_TAIbeforePD, True, True, True),
        (CowReproductionProtocol.TAI, CowReSynchSubProtocol.Resynch_TAIbeforePD, False, True, False),
        (CowReproductionProtocol.ED_TAI, CowReSynchSubProtocol.Resynch_TAIafterPD, True, False, False),
    ],
)
def test_handle_failed_cow_conception(
    cow_reproduction_program: CowReproductionProtocol,
    resynch_method: CowReSynchSubProtocol,
    expected_estrus_simulated: bool,
    expected_ovsynch_scheduled: bool,
    keep_existing: bool,
    mocker: MockerFixture,
) -> None:
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = cow_reproduction_program

    default_resynch_method = AnimalConfig.cow_resynch_method
    AnimalConfig.cow_resynch_method = resynch_method

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, events=MagicMock(spec=AnimalEvents))

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)
    mock_schedule_ovsynch = mocker.patch.object(
        reproduction, "_schedule_ovsynch_program_in_advance", return_value=mock_outputs
    )

    reproduction.repro_state_manager = MagicMock()
    reproduction.repro_state_manager.enter = MagicMock()

    result = reproduction._handle_failed_cow_conception(mock_outputs, 100)

    mock_outputs.events.add_event.assert_any_call(
        mock_outputs.days_born,
        100,
        f"{animal_constants.FAILED_CONCEPTION}, with conception rate at {reproduction.conception_rate}",
    )
    mock_outputs.events.add_event.assert_any_call(mock_outputs.days_born, 100, animal_constants.COW_NOT_PREG)

    if expected_estrus_simulated:
        reproduction.repro_state_manager.enter.assert_any_call(ReproStateEnum.WAITING_FULL_ED_CYCLE)
        mock_simulate_estrus.assert_called_once_with(
            mock_outputs,
            mock_outputs.days_born,
            100,
            animal_constants.ESTRUS_DAY_SCHEDULED_NOTE,
            AnimalConfig.average_estrus_cycle_cow,
            AnimalConfig.std_estrus_cycle_cow,
        )
    else:
        mock_simulate_estrus.assert_not_called()

    if expected_ovsynch_scheduled:
        mock_schedule_ovsynch.assert_called_once_with(mock_outputs, 100)
    else:
        mock_schedule_ovsynch.assert_not_called()

    assert result == mock_outputs
    AnimalConfig.cow_resynch_method = default_resynch_method


@pytest.mark.parametrize(
    "days_in_pregnancy, days_born, ai_day, simulation_day",
    [
        (10, 100, 68, 200),
    ],
)
def test_cow_pregnancy_update(
    days_in_pregnancy: int, days_born: int, ai_day: int, simulation_day: int, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    reproduction.ai_day = ai_day

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.HEIFER_II, days_born=days_born, days_in_pregnancy=days_in_pregnancy
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_handle_cow_check = mocker.patch.object(
        reproduction, "_handle_cow_pregnancy_check", side_effect=lambda outputs, config, day: outputs
    )

    result = reproduction.cow_pregnancy_update(mock_outputs, simulation_day)

    mock_handle_cow_check.assert_called_once_with(
        mock_outputs,
        {
            "day": AnimalConfig.first_pregnancy_check_day,
            "loss_rate": AnimalConfig.first_pregnancy_check_loss_rate,
            "on_preg_loss": animal_constants.PREG_LOSS_BEFORE_1,
            "on_preg": animal_constants.PREG_CHECK_1_PREG,
            "on_not_preg": animal_constants.PREG_CHECK_1_NOT_PREG,
        },
        simulation_day,
    )

    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_in_pregnancy, days_in_milk, do_not_breed, expected_do_not_breed, expect_event",
    [
        (0, AnimalConfig.do_not_breed_time + 1, False, True, True),  # Not pregnant and beyond do-not-breed time
        (10, AnimalConfig.do_not_breed_time + 1, False, False, False),  # Pregnant and beyond do-not-breed time
        (0, AnimalConfig.do_not_breed_time - 1, False, False, False),  # Not pregnant but within breeding window
        (0, AnimalConfig.do_not_breed_time + 1, True, True, False),  # Already marked as do-not-breed
    ],
)
def test_check_do_not_breed_flag(
    days_in_pregnancy: int, days_in_milk: int, do_not_breed: bool, expected_do_not_breed: bool, expect_event: bool
) -> None:
    reproduction = Reproduction()
    reproduction.do_not_breed = do_not_breed

    mock_outputs = mock_reproduction_data_stream(
        animal_type=AnimalType.LAC_COW, days_in_pregnancy=days_in_pregnancy, days_in_milk=days_in_milk
    )

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    mock_add_event = mock_outputs.events.add_event

    simulation_day = 100
    result = reproduction._check_do_not_breed_flag(simulation_day, mock_outputs)

    assert reproduction.do_not_breed == expected_do_not_breed

    if expect_event:
        mock_add_event.assert_called_once_with(
            mock_outputs.days_born,
            simulation_day,
            f"{animal_constants.DO_NOT_BREED}, days in milk: {days_in_milk}, not pregnant",
        )
    else:
        mock_add_event.assert_not_called()

    assert result == mock_outputs


@pytest.mark.parametrize(
    "repro_state, expected_state_entered, expected_event",
    [
        (
            ReproStateEnum.WAITING_SHORT_ED_CYCLE,
            ReproStateEnum.WAITING_SHORT_ED_CYCLE,
            animal_constants.SIMULATE_ESTRUS_AFTER_PGF_NOTE,
        ),
    ],
)
def test_handle_open_cow_in_pgf_at_pd_resynch(
    repro_state: ReproStateEnum, expected_state_entered: ReproStateEnum, expected_event: str, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=100)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    simulation_day = 100
    single_pgf_injection_schedule = {mock_outputs.days_born: {"deliver_hormones": ["PGF"]}}
    mock_execute_hormone_schedule = mocker.patch.object(
        reproduction, "_execute_cow_hormone_delivery_schedule", return_value=mock_outputs
    )

    mock_simulate_estrus = mocker.patch.object(reproduction, "_simulate_estrus", return_value=mock_outputs)

    reproduction.repro_state_manager.enter(repro_state)
    mock_enter_repro_state = mocker.patch.object(reproduction.repro_state_manager, "enter")

    result = reproduction._handle_open_cow_in_pgf_at_pd_resynch(mock_outputs, simulation_day)

    mock_execute_hormone_schedule.assert_called_once_with(mock_outputs, simulation_day, single_pgf_injection_schedule)
    mock_enter_repro_state.assert_called_once_with(expected_state_entered)
    mock_simulate_estrus.assert_called_once_with(
        mock_outputs,
        mock_outputs.days_born,
        simulation_day,
        expected_event,
        AnimalConfig.average_estrus_cycle_after_pgf,
        AnimalConfig.std_estrus_cycle_after_pgf,
        max_cycle_length=animal_constants.MAX_ESTRUS_CYCLE_LENGTH_PGF_AT_PREG_CHECK,
    )
    assert result == mock_outputs


@pytest.mark.parametrize(
    "initial_state, final_state, expected_event_called",
    [
        (ReproStateEnum.WAITING_FULL_ED_CYCLE, ReproStateEnum.IN_OVSYNCH, True),
        (ReproStateEnum.IN_OVSYNCH, ReproStateEnum.IN_OVSYNCH, False),
        (ReproStateEnum.NONE, ReproStateEnum.IN_OVSYNCH, True),
    ],
)
def test_handle_open_cow_in_tai_before_pd_resynch(
    initial_state: ReproStateEnum, final_state: ReproStateEnum, expected_event_called: bool, mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    reproduction.repro_state_manager.enter(initial_state)

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=100)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    simulation_day = 100
    mock_exit_waiting_cycle = mocker.patch.object(reproduction.repro_state_manager, "exit")

    result = reproduction._handle_open_cow_in_tai_before_pd_resynch(mock_outputs, simulation_day)

    if initial_state == ReproStateEnum.WAITING_FULL_ED_CYCLE:
        mock_exit_waiting_cycle.assert_called_once_with(ReproStateEnum.WAITING_FULL_ED_CYCLE)
        mock_outputs.events.add_event.assert_any_call(
            mock_outputs.days_born, simulation_day, animal_constants.CANCEL_ESTRUS_DETECTION_NOTE
        )
    else:
        mock_exit_waiting_cycle.assert_not_called()

    assert result == mock_outputs


def test_schedule_ovsynch_program_in_advance(mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    simulation_day = 100
    days_before_first_preg_check = animal_constants.DAYS_BEFORE_FIRST_PREG_CHECK_TO_START_TAI

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=100)

    mock_events = MagicMock(auto_spec=AnimalEvents)
    mock_events.add_event = MagicMock()
    mock_outputs.events = mock_events

    expected_start_day = mock_outputs.days_born + AnimalConfig.first_pregnancy_check_day - days_before_first_preg_check

    mock_set_hormone_schedule = mocker.patch.object(reproduction, "_set_up_hormone_schedule", return_value=mock_outputs)

    result = reproduction._schedule_ovsynch_program_in_advance(
        mock_outputs, simulation_day, days_before_first_preg_check
    )

    mock_set_hormone_schedule.assert_called_once_with(
        mock_outputs, expected_start_day, AnimalConfig.cow_ovsynch_method.value
    )
    assert reproduction.TAI_conception_rate == AnimalConfig.ovsynch_program_conception_rate

    mock_outputs.events.add_event.assert_called_once_with(
        mock_outputs.days_born,
        simulation_day,
        f"{animal_constants.SETTING_UP_OVSYNCH_PROGRAM_IN_ADVANCE_NOTE}: {AnimalConfig.cow_ovsynch_method}",
    )

    assert result == mock_outputs


def test_exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(mocker: MockerFixture) -> None:
    reproduction = Reproduction()
    simulation_day = 150

    mock_outputs = mock_reproduction_data_stream(animal_type=AnimalType.LAC_COW, days_born=100)

    mock_add_event = mocker.patch.object(mock_outputs.events, "add_event")
    mock_exit_repro_state = mocker.patch.object(reproduction.repro_state_manager, "exit")

    reproduction.hormone_schedule = {0: {"some_schedule": "test"}}

    result = reproduction._exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(
        mock_outputs, simulation_day
    )

    mock_exit_repro_state.assert_called_once_with(ReproStateEnum.IN_OVSYNCH)

    assert reproduction.hormone_schedule == {}

    mock_add_event.assert_called_once_with(
        mock_outputs.days_born,
        simulation_day,
        f"{animal_constants.DISCONTINUE_OVSYNCH_PROGRAM_IN_TAI_BEFORE_PD_NOTE}: {AnimalConfig.cow_ovsynch_method}",
    )

    assert result == mock_outputs
