import sys
from dataclasses import asdict
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import HeiferReproductionProtocol, HeiferTAISubProtocol, \
    CowReproductionProtocol
from RUFAS.biophysical.animal.data_types.reproduction_inputs import ReproductionInputs
from RUFAS.biophysical.animal.data_types.reproduction_outputs import ReproductionOutputs, AnimalReproductionStatistics, \
    HerdReproductionStatistics
from RUFAS.biophysical.animal.reproduction.reproduction import Reproduction
from RUFAS.time import Time


@pytest.fixture
def mock_reproduction(mocker: MockerFixture) -> Reproduction:
    # mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.AnimalConfig",
    #              return_value=MagicMock(auto_spec=AnimalConfig))
    return Reproduction()


def mock_reproduction_inputs(
        animal_type: AnimalType,
        body_weight: int = 0.0,
        breed: Breed = Breed.HO,
        cull_reason: str = "",
        days_born: int = 0,
        days_in_pregnancy: int = 0,
        days_in_milking: int = 0,
        events: AnimalEvents = AnimalEvents(),
        future_cull_date: int = sys.maxsize,
        future_death_date: int = sys.maxsize
) -> ReproductionInputs:
    return ReproductionInputs(
        animal_type=animal_type,
        body_weight=body_weight,
        breed=breed,
        cull_reason=cull_reason,
        days_born=days_born,
        days_in_pregnancy=days_in_pregnancy,
        days_in_milking=days_in_milking,
        events=events,
        future_cull_date=future_cull_date,
        future_death_date=future_death_date
    )


def mock_reproduction_outputs(
        animal_type: AnimalType,
        body_weight: int = 0.0,
        breed: Breed = Breed.HO,
        cull_reason: str = "",
        days_born: int = 0,
        days_in_pregnancy: int = 0,
        days_in_milking: int = 0,
        events: AnimalEvents = AnimalEvents(),
        future_cull_date: int = sys.maxsize,
        future_death_date: int = sys.maxsize
) -> ReproductionOutputs:
    return ReproductionOutputs(
        animal_type=animal_type,
        body_weight=body_weight,
        breed=breed,
        cull_reason=cull_reason,
        days_born=days_born,
        days_in_pregnancy=days_in_pregnancy,
        days_in_milking=days_in_milking,
        events=events,
        future_cull_date=future_cull_date,
        future_death_date=future_death_date,
        animal_level_statistics=AnimalReproductionStatistics(),
        herd_level_statistics=HerdReproductionStatistics()
    )


@pytest.mark.parametrize(
    'animal_type',
    [
        AnimalType.HEIFER_II,
        AnimalType.DRY_COW,
        AnimalType.LAC_COW
    ]
)
def test_reproduction_update(
        animal_type: AnimalType,
        mock_reproduction: Reproduction,
        mocker: MockerFixture
) -> None:

    mock_time = MagicMock(auto_spec=Time)
    mock_time.simulation_day = 100

    mock_inputs = mock_reproduction_inputs(animal_type=animal_type)

    mock_outputs = mock_reproduction_outputs(**asdict(mock_inputs))

    mocker.patch("RUFAS.biophysical.animal.reproduction.reproduction.ReproductionOutputs",
                 return_value=mock_outputs)
    mock_reproduction.heiferII_reproduction_update = MagicMock(return_value=mock_outputs)
    mock_reproduction.cow_reproduction_update = MagicMock(return_value=mock_outputs)

    result = mock_reproduction.reproduction_update(mock_inputs, mock_time)

    assert result == mock_outputs

    if animal_type == AnimalType.HEIFER_II:
        mock_reproduction.heiferII_reproduction_update.assert_called_once_with(mock_outputs, mock_time)
        mock_reproduction.cow_reproduction_update.assert_not_called()

    if animal_type == AnimalType.LAC_COW or animal_type == AnimalType.DRY_COW:
        mock_reproduction.heiferII_reproduction_update.assert_not_called()
        mock_reproduction.cow_reproduction_update.assert_called_once_with(mock_outputs, mock_time)


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
        (AnimalConfig.heifer_breed_start_day + 1, 0, HeiferReproductionProtocol.ED,
         AnimalConfig.heifer_breed_start_day + 1, True, True, False),

        # After breeding start day, is pregnant; expect pregnancy update
        (AnimalConfig.heifer_breed_start_day + 1, 10, HeiferReproductionProtocol.ED, 0, False, True, True),
    ]
)
def test_heiferII_reproduction_update_same_method_as_config(
    days_born: int,
    days_in_pregnancy: int,
    protocol: HeiferReproductionProtocol,
    ai_day: int,
    expect_ai: bool,
    expect_protocol_call: bool,
    expect_pregnancy_update: bool,
    mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = protocol
    reproduction.ai_day = ai_day

    default_heifer_reproduction_program = AnimalConfig.heifer_reproduction_program
    AnimalConfig.heifer_reproduction_program = protocol.value

    mock_time = MagicMock(spec=Time)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_outputs(
        animal_type=AnimalType.HEIFER_II,
        days_born=days_born,
        days_in_pregnancy=days_in_pregnancy
    )

    mock_execute_heifer_ed_protocol = mocker.patch.object(
        reproduction,
        'execute_heifer_ed_protocol',
        return_value=mock_outputs
    )
    mock_execute_heifer_tai_protocol = mocker.patch.object(
        reproduction,
        'execute_heifer_tai_protocol',
        return_value=mock_outputs
    )
    mock_execute_heifer_synch_ed_protocol = mocker.patch.object(
        reproduction,
        'execute_heifer_synch_ed_protocol',
        return_value=mock_outputs
    )
    mock_perform_ai = mocker.patch.object(
        reproduction,
        '_perform_ai',
        return_value=mock_outputs
    )
    mock_pregnancy_update = mocker.patch.object(reproduction, 'heifer_pregnancy_update', return_value=mock_outputs)

    result = reproduction.heiferII_reproduction_update(mock_outputs, mock_time)

    if expect_protocol_call:
        if protocol == HeiferReproductionProtocol.ED:
            mock_execute_heifer_ed_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)
            mock_execute_heifer_tai_protocol.assert_not_called()
            mock_execute_heifer_synch_ed_protocol.assert_not_called()
        elif protocol == HeiferReproductionProtocol.TAI:
            mock_execute_heifer_tai_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)
            mock_execute_heifer_ed_protocol.assert_not_called()
            mock_execute_heifer_synch_ed_protocol.assert_not_called()
        elif protocol == HeiferReproductionProtocol.SynchED:
            mock_execute_heifer_synch_ed_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)
            mock_execute_heifer_ed_protocol.assert_not_called()
            mock_execute_heifer_tai_protocol.assert_not_called()

        if expect_ai:
            mock_perform_ai.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        else:
            mock_perform_ai.assert_not_called()

        if expect_pregnancy_update:
            mock_pregnancy_update.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        else:
            mock_pregnancy_update.assert_not_called()

    else:
        mock_execute_heifer_ed_protocol.assert_not_called()
        mock_execute_heifer_tai_protocol.assert_not_called()
        mock_execute_heifer_synch_ed_protocol.assert_not_called()

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
    ]
)
def test_heiferII_reproduction_update_different_method_as_config(
    days_born: int,
    protocol: HeiferReproductionProtocol,
    mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = protocol
    reproduction.ai_day = AnimalConfig.heifer_breed_start_day + 10

    mock_time = MagicMock(spec=Time)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_outputs(
        animal_type=AnimalType.HEIFER_II,
        days_born=days_born,
        days_in_pregnancy=0
    )

    mock_execute_heifer_ed_protocol = mocker.patch.object(
        reproduction,
        'execute_heifer_ed_protocol',
        return_value=mock_outputs
    )
    mock_execute_heifer_tai_protocol = mocker.patch.object(
        reproduction,
        'execute_heifer_tai_protocol',
        return_value=mock_outputs
    )
    mock_execute_heifer_synch_ed_protocol = mocker.patch.object(
        reproduction,
        'execute_heifer_synch_ed_protocol',
        return_value=mock_outputs
    )
    mock_perform_ai = mocker.patch.object(reproduction, '_perform_ai')
    mock_pregnancy_update = mocker.patch.object(reproduction, 'heifer_pregnancy_update')

    result = reproduction.heiferII_reproduction_update(mock_outputs, mock_time)

    if days_born <= AnimalConfig.heifer_breed_start_day:
        assert reproduction.heifer_reproduction_program == HeiferReproductionProtocol(
            AnimalConfig.heifer_reproduction_program
        )
        mock_execute_heifer_ed_protocol.assert_not_called() if days_born < AnimalConfig.heifer_breed_start_day \
            else mock_execute_heifer_ed_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        mock_execute_heifer_tai_protocol.assert_not_called()
        mock_execute_heifer_synch_ed_protocol.assert_not_called()
        mock_perform_ai.assert_not_called()
        mock_pregnancy_update.assert_not_called()

    else:
        assert reproduction.heifer_reproduction_program == protocol
    assert result == mock_outputs


@pytest.mark.parametrize(
    "days_born, protocol",
    [
        (AnimalConfig.heifer_breed_start_day+1, HeiferTAISubProtocol.TAI_5dCG2P),
    ]
)
def test_heiferII_reproduction_update_invalid_protocol(
    days_born: int,
    protocol: HeiferReproductionProtocol,
    mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    reproduction.heifer_reproduction_program = protocol

    mock_time = MagicMock(spec=Time)
    mock_time.simulation_day = 100

    mock_outputs = mock_reproduction_outputs(
        animal_type=AnimalType.HEIFER_II,
        days_born=days_born,
    )

    mock_execute_heifer_ed_protocol = mocker.patch.object(reproduction, 'execute_heifer_ed_protocol')
    mock_execute_heifer_tai_protocol = mocker.patch.object(reproduction, 'execute_heifer_tai_protocol')
    mock_execute_heifer_synch_ed_protocol = mocker.patch.object(reproduction, 'execute_heifer_synch_ed_protocol')
    mock_perform_ai = mocker.patch.object(reproduction, '_perform_ai')
    mock_pregnancy_update = mocker.patch.object(reproduction, 'heifer_pregnancy_update')

    with pytest.raises(ValueError):
        reproduction.heiferII_reproduction_update(mock_outputs, mock_time)

    mock_execute_heifer_ed_protocol.assert_not_called()
    mock_execute_heifer_tai_protocol.assert_not_called()
    mock_execute_heifer_synch_ed_protocol.assert_not_called()
    mock_perform_ai.assert_not_called()
    mock_pregnancy_update.assert_not_called()


@pytest.mark.parametrize(
    "days_in_pregnancy, repro_program, do_not_breed, expect_birth, expect_protocol_call",
    [
        (280, CowReproductionProtocol.ED, False, True, True),
        (280, CowReproductionProtocol.ED, True, True, False),
        (0, CowReproductionProtocol.ED, False, False, True),
        (0, CowReproductionProtocol.TAI, False, False, True),
        (0, CowReproductionProtocol.ED_TAI, False, False, True),
        (0, CowReproductionProtocol.ED, True, False, False),
        (150, CowReproductionProtocol.ED, False, False, True)
    ]
)
def test_cow_reproduction_update(
    days_in_pregnancy: int,
    repro_program: CowReproductionProtocol,
    do_not_breed: bool,
    expect_birth: bool,
    expect_protocol_call: bool,
    mocker: MockerFixture
) -> None:
    reproduction = Reproduction()
    reproduction.cow_reproduction_program = repro_program
    reproduction.do_not_breed = do_not_breed
    reproduction.gestation_length = 280

    default_cow_reproduction_program = AnimalConfig.cow_reproduction_program
    AnimalConfig.cow_reproduction_program = repro_program.value

    mock_time = MagicMock(spec=Time)
    mock_time.simulation_day = 100

    mock_outputs = ReproductionOutputs(
        animal_type=AnimalType.LAC_COW,
        days_in_pregnancy=days_in_pregnancy,
        days_in_milking=150,
        body_weight=0.0,
        breed=Breed.HO,
        days_born=500,
        cull_reason="",
        future_cull_date=sys.maxsize,
        future_death_date=sys.maxsize,
        animal_level_statistics=MagicMock(),
        herd_level_statistics=MagicMock(),
        events=MagicMock()
    )

    mock_cow_give_birth = mocker.patch.object(reproduction, 'cow_give_birth', return_value=mock_outputs)
    mock_execute_cow_ed_protocol = mocker.patch.object(reproduction, 'execute_cow_ed_protocol', return_value=mock_outputs)
    mock_execute_cow_tai_protocol = mocker.patch.object(reproduction, 'execute_cow_tai_protocol', return_value=mock_outputs)
    mock_execute_cow_ed_tai_protocol = mocker.patch.object(reproduction, 'execute_cow_ed_tai_protocol', return_value=mock_outputs)
    mock_pregnancy_update = mocker.patch.object(reproduction, 'cow_pregnancy_update', return_value=mock_outputs)

    result = reproduction.cow_reproduction_update(mock_outputs, mock_time)

    if expect_birth:
        mock_cow_give_birth.assert_called_once_with(mock_outputs, mock_time)
    else:
        mock_cow_give_birth.assert_not_called()

    if expect_protocol_call:
        if repro_program == CowReproductionProtocol.ED:
            mock_execute_cow_ed_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        elif repro_program == CowReproductionProtocol.TAI:
            mock_execute_cow_tai_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)
        elif repro_program == CowReproductionProtocol.ED_TAI:
            mock_execute_cow_ed_tai_protocol.assert_called_once_with(mock_outputs, mock_time.simulation_day)
    else:
        mock_execute_cow_ed_protocol.assert_not_called()
        mock_execute_cow_tai_protocol.assert_not_called()
        mock_execute_cow_ed_tai_protocol.assert_not_called()

    if not do_not_breed:
        mock_pregnancy_update.assert_called_once_with(mock_outputs, mock_time.simulation_day)

    assert result == mock_outputs

    AnimalConfig.cow_reproduction_program = default_cow_reproduction_program
