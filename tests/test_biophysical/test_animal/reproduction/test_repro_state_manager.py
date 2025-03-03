import pytest
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import ReproStateEnum
from RUFAS.biophysical.animal.reproduction.repro_state_manager import ReproStateManager


def test_repro_state_manager_init() -> None:
    """
    Test initialization of ReproStateManager with and without initial states.
    """
    # Test default initialization
    manager_default = ReproStateManager()
    assert manager_default._states == {ReproStateEnum.NONE}

    # Test initialization with a custom set of states
    custom_states = {ReproStateEnum.PREGNANT, ReproStateEnum.FRESH}
    manager_custom = ReproStateManager(initial_states=custom_states)
    assert manager_custom._states == custom_states


@pytest.mark.parametrize(
    "initial_states, new_state, keep_existing, expected_states",
    [
        (None, ReproStateEnum.PREGNANT, False, {ReproStateEnum.PREGNANT}),
        ({ReproStateEnum.PREGNANT}, ReproStateEnum.FRESH, False, {ReproStateEnum.FRESH}),
        ({ReproStateEnum.FRESH}, ReproStateEnum.PREGNANT, True, {ReproStateEnum.FRESH, ReproStateEnum.PREGNANT}),
        ({ReproStateEnum.PREGNANT, ReproStateEnum.FRESH}, ReproStateEnum.NONE, False, {ReproStateEnum.NONE}),
    ],
)
def test_enter_state(
    initial_states: set[ReproStateEnum] | None,
    new_state: ReproStateEnum,
    keep_existing: bool,
    expected_states: set[ReproStateEnum],
) -> None:
    """
    Test entering reproductive states in ReproStateManager with parametrization.
    """
    manager = ReproStateManager(initial_states)
    manager.enter(new_state, keep_existing)
    assert manager._states == expected_states


@pytest.mark.parametrize("state", [ReproStateEnum.PREGNANT, ReproStateEnum.FRESH])
def test_enter_existing_state_raises_value_error(state: ReproStateEnum) -> None:
    """
    Test that re-entering an already active state raises ValueError.
    """
    manager = ReproStateManager({state})
    with pytest.raises(ValueError, match=f"Attempting to re-enter the same state: {state}"):
        manager.enter(state, keep_existing=True)


@pytest.mark.parametrize(
    "initial_states, exit_state, expected_states",
    [
        ({ReproStateEnum.PREGNANT, ReproStateEnum.FRESH}, ReproStateEnum.PREGNANT, {ReproStateEnum.FRESH}),
        ({ReproStateEnum.FRESH}, ReproStateEnum.FRESH, {ReproStateEnum.NONE}),
        ({ReproStateEnum.NONE}, ReproStateEnum.NONE, {ReproStateEnum.NONE}),
    ],
)
def test_exit_state(
    initial_states: set[ReproStateEnum], exit_state: ReproStateEnum, expected_states: set[ReproStateEnum]
) -> None:
    """
    Test exiting reproductive states in ReproStateManager with parametrization.
    """
    manager = ReproStateManager(initial_states)
    manager.exit(exit_state)
    assert manager._states == expected_states


@pytest.mark.parametrize("state", [ReproStateEnum.WAITING_FULL_ED_CYCLE, ReproStateEnum.IN_OVSYNCH])
def test_exit_nonexistent_state_raises_value_error(state: ReproStateEnum) -> None:
    """
    Test that exiting a non-existent state raises ValueError.
    """
    manager = ReproStateManager(initial_states={ReproStateEnum.PREGNANT, ReproStateEnum.FRESH})

    with pytest.raises(ValueError):
        manager.exit(state)


@pytest.mark.parametrize(
    "state, expected",
    [
        (ReproStateEnum.WAITING_FULL_ED_CYCLE, False),
        (ReproStateEnum.FRESH, True),
    ],
)
def test_repro_state_is_in(state: ReproStateEnum, expected: bool) -> None:
    """
    Test ReproStateManager is_in() method.
    """
    manager = ReproStateManager(initial_states={ReproStateEnum.PREGNANT, ReproStateEnum.FRESH})

    result = manager.is_in(state)
    assert result == expected


@pytest.mark.parametrize(
    "states, expected",
    [
        ({ReproStateEnum.WAITING_FULL_ED_CYCLE, ReproStateEnum.IN_OVSYNCH}, False),
        ({ReproStateEnum.FRESH, ReproStateEnum.PREGNANT}, True),
        ({ReproStateEnum.PREGNANT, ReproStateEnum.IN_PRESYNCH}, True),
        ({ReproStateEnum.HAS_DONE_PRESYNCH, ReproStateEnum.IN_OVSYNCH}, False),
    ],
)
def test_repro_state_is_in_any(states: set[ReproStateEnum], expected: bool) -> None:
    """
    Test ReproStateManager is_in_any() method.
    """
    manager = ReproStateManager(initial_states={ReproStateEnum.PREGNANT, ReproStateEnum.FRESH})
    result = manager.is_in_any(states)
    assert result == expected


def test_repro_state_reset() -> None:
    """
    Test that reset() clears all states and reverts to NONE.
    """
    manager = ReproStateManager(initial_states={ReproStateEnum.PREGNANT, ReproStateEnum.FRESH})
    manager.reset()
    assert manager._states == {ReproStateEnum.NONE}


@pytest.mark.parametrize(
    "initial_states, expected",
    [
        ({ReproStateEnum.NONE}, True),
        ({ReproStateEnum.PREGNANT}, False),
        ({ReproStateEnum.FRESH, ReproStateEnum.PREGNANT}, False),
    ],
)
def test_is_in_empty_state(initial_states: set[ReproStateEnum], expected: bool) -> None:
    """
    Test is_in_empty_state() method to check if the manager is in the empty state (NONE).
    """
    manager = ReproStateManager(initial_states)
    assert manager.is_in_empty_state() == expected


@pytest.mark.parametrize(
    "initial_states, expected",
    [
        ({ReproStateEnum.NONE}, "none"),
        ({ReproStateEnum.PREGNANT}, "pregnant"),
        ({ReproStateEnum.FRESH, ReproStateEnum.PREGNANT}, "fresh, pregnant"),
    ],
)
def test_repro_state_str(initial_states: set[ReproStateEnum], expected: str) -> None:
    """
    Test the __str__() method for correct string representation of reproductive states.
    """
    manager = ReproStateManager(initial_states)
    assert set(expected.split(", ")) == set(str(manager).split(", "))
