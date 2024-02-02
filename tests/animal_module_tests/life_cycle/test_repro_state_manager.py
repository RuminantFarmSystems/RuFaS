from typing import Type

import pytest

from RUFAS.routines.animal.life_cycle.repro_protocol_enums import ReproStateEnum
from RUFAS.routines.animal.life_cycle.repro_state_manager import ReproStateManager


@pytest.mark.parametrize("initial_states, expected_states", [
    # Test the default initialization.
    (None, {ReproStateEnum.NONE}),

    # Test initialization with a single state.
    ({ReproStateEnum.FRESH}, {ReproStateEnum.FRESH}),

    # Test initialization with multiple states.
    ({ReproStateEnum.FRESH, ReproStateEnum.WAITING_FULL_ED_CYCLE},
     {ReproStateEnum.FRESH, ReproStateEnum.WAITING_FULL_ED_CYCLE}),
])
def test_repro_state_manager_init(
        initial_states: set[ReproStateEnum] | None,
        expected_states: set[ReproStateEnum]
) -> None:
    """
    Test the method __init__() of the ReproStateManager class in repro_state_manager.py.
    """

    # Act
    manager = ReproStateManager(initial_states=initial_states)

    # Assert
    assert manager._states == expected_states


@pytest.mark.parametrize("initial_states, state_to_enter, keep_existing, expected_states, expected_exception", [
    # Test entering a single state with no existing states.
    (None, ReproStateEnum.WAITING_FULL_ED_CYCLE, False, {ReproStateEnum.WAITING_FULL_ED_CYCLE}, None),

    # Test entering a single state with an existing state.
    ({ReproStateEnum.PREGNANT}, ReproStateEnum.WAITING_FULL_ED_CYCLE, False, {ReproStateEnum.WAITING_FULL_ED_CYCLE},
     None),

    # Test entering a single state with an existing state and keep_existing=True.
    ({ReproStateEnum.PREGNANT}, ReproStateEnum.WAITING_FULL_ED_CYCLE, True,
     {ReproStateEnum.PREGNANT, ReproStateEnum.WAITING_FULL_ED_CYCLE}, None),

    # Test entering the NONE state with an existing state.
    ({ReproStateEnum.PREGNANT}, ReproStateEnum.NONE, False, {ReproStateEnum.NONE}, None),

    # Test entering the NONE state again
    ({ReproStateEnum.NONE}, ReproStateEnum.NONE, False, {ReproStateEnum.NONE}, None),

    # Test entering the same state with keep_existing=True.
    ({ReproStateEnum.WAITING_FULL_ED_CYCLE}, ReproStateEnum.WAITING_FULL_ED_CYCLE, True, None, ValueError),

    # Test entering the same state with keep_existing=False.
    ({ReproStateEnum.WAITING_FULL_ED_CYCLE}, ReproStateEnum.WAITING_FULL_ED_CYCLE, False,
     {ReproStateEnum.WAITING_FULL_ED_CYCLE}, None),
])
def test_enter_state(
        initial_states: set[ReproStateEnum] | None,
        state_to_enter: ReproStateEnum,
        keep_existing: bool,
        expected_states: set[ReproStateEnum] | None,
        expected_exception: Type[Exception] | None
) -> None:
    """
    Test the enter() method of the ReproStateManager class in repro_state_manager.py.
    """

    # Arrange
    manager = ReproStateManager(initial_states=initial_states)

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception, match="Attempting to re-enter the same state"):
            manager.enter(state_to_enter, keep_existing)
    else:
        manager.enter(state_to_enter, keep_existing)
        assert manager._states == expected_states


@pytest.mark.parametrize("initial_states, state_to_exit, expected_states, expected_exception", [
    # Test exiting a single active state
    ({ReproStateEnum.WAITING_FULL_ED_CYCLE}, ReproStateEnum.WAITING_FULL_ED_CYCLE, {ReproStateEnum.NONE}, None),

    # Test exiting a state with multiple active states
    ({ReproStateEnum.WAITING_FULL_ED_CYCLE, ReproStateEnum.PREGNANT},
     ReproStateEnum.WAITING_FULL_ED_CYCLE, {ReproStateEnum.PREGNANT}, None),

    # Test attempting to exit a state that is not currently active
    ({ReproStateEnum.WAITING_FULL_ED_CYCLE}, ReproStateEnum.PREGNANT, None, ValueError),

    # Test exiting NONE state does nothing
    ({ReproStateEnum.NONE}, ReproStateEnum.NONE, {ReproStateEnum.NONE}, None),
])
def test_exit_state(
        initial_states: set[ReproStateEnum] | None,
        state_to_exit: ReproStateEnum,
        expected_states: set[ReproStateEnum] | None,
        expected_exception: Type[Exception] | None
):
    """
    Test the exit() method of the ReproStateManager class in repro_state_manager.py.
    """

    # Arrange
    manager = ReproStateManager(initial_states=initial_states)

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception, match="Attempting to exit a state that is not entered"):
            manager.exit(state_to_exit)
    else:
        manager.exit(state_to_exit)
        assert manager._states == expected_states


@pytest.mark.parametrize("initial_states, state_to_check, expected_result", [
    # Checking for a state that is active
    ({ReproStateEnum.WAITING_FULL_ED_CYCLE}, ReproStateEnum.WAITING_FULL_ED_CYCLE, True),

    # Checking for a state that is not active
    ({ReproStateEnum.WAITING_FULL_ED_CYCLE}, ReproStateEnum.PREGNANT, False),

    # Checking for NONE state when it is the only active state
    ({ReproStateEnum.NONE}, ReproStateEnum.NONE, True),
])
def test_is_in_state(
        initial_states: set[ReproStateEnum] | None,
        state_to_check: ReproStateEnum,
        expected_result: bool
):
    """
    Test the is_in() method of the ReproStateManager class in repro_state_manager.py.
    """

    # Arrange
    manager = ReproStateManager(initial_states=initial_states)

    # Act
    result = manager.is_in(state_to_check)

    # Assert
    assert result == expected_result


def test_reset_state_manager() -> None:
    """
    Test the reset() method of the ReproStateManager class in repro_state_manager.py.
    """

    # Arrange
    initial_states = {ReproStateEnum.WAITING_FULL_ED_CYCLE, ReproStateEnum.PREGNANT}
    manager = ReproStateManager(initial_states=initial_states)

    # Act
    manager.reset()

    # Assert
    assert manager._states == {ReproStateEnum.NONE}


@pytest.mark.parametrize("initial_states, expected_result", [
    # Test case where the current state is NONE
    ({ReproStateEnum.NONE}, True),

    # Test case where the current state is not NONE
    ({ReproStateEnum.WAITING_FULL_ED_CYCLE}, False),

    # Test case with no initial states
    (None, True)
])
def test_is_in_empty_state(
        initial_states: set[ReproStateEnum] | None,
        expected_result: bool
) -> None:
    """
    Test the is_in_empty_state() method of the ReproStateManager class in repro_state_manager.py.
    """

    # Arrange
    manager = ReproStateManager(initial_states=initial_states)

    # Act and assert
    assert manager.is_in_empty_state() is expected_result


@pytest.mark.parametrize("initial_states, states_to_check, expected_result", [
    # Test with no active states and checking an empty set
    (None, set(), False),

    # Test with no active states and checking a non-empty set
    (None, {ReproStateEnum.PREGNANT}, False),

    # Test with an active state, checking for that state
    ({ReproStateEnum.PREGNANT}, {ReproStateEnum.PREGNANT}, True),

    # Test with an active state, checking for a different state
    ({ReproStateEnum.PREGNANT}, {ReproStateEnum.WAITING_FULL_ED_CYCLE}, False),

    # Test with multiple active states, checking for one of them
    ({ReproStateEnum.PREGNANT, ReproStateEnum.WAITING_FULL_ED_CYCLE}, {ReproStateEnum.PREGNANT}, True),

    # Test with multiple active states, checking for a non-active state
    ({ReproStateEnum.PREGNANT, ReproStateEnum.WAITING_FULL_ED_CYCLE}, {ReproStateEnum.FRESH}, False),

    # Test with multiple active states, checking for multiple states including an active one
    ({ReproStateEnum.PREGNANT, ReproStateEnum.WAITING_FULL_ED_CYCLE}, {ReproStateEnum.PREGNANT, ReproStateEnum.FRESH},
     True),

    # Test with multiple active states, checking for multiple states none of which are active
    ({ReproStateEnum.PREGNANT, ReproStateEnum.WAITING_FULL_ED_CYCLE}, {ReproStateEnum.FRESH, ReproStateEnum.IN_OVSYNCH},
     False),
])
def test_is_in_any(
        initial_states: set[ReproStateEnum] | None,
        states_to_check: set[ReproStateEnum],
        expected_result: bool
) -> None:
    """
    Test the is_in_any() method of the ReproStateManager class in repro_state_manager.py.
    """

    # Arrange
    manager = ReproStateManager(initial_states=initial_states)

    # Act
    result = manager.is_in_any(states_to_check)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("initial_states", [
    # Test with no states
    None,

    # Test with a single state
    {ReproStateEnum.WAITING_FULL_ED_CYCLE},

    # Test with multiple states
    {ReproStateEnum.WAITING_FULL_ED_CYCLE, ReproStateEnum.PREGNANT},
])
def test_repro_state_manager_str(
        initial_states: set[ReproStateEnum] | None
) -> None:
    """
    Test the __str__ method of the ReproStateManager class in repro_state_manager.py.
    """

    # Arrange
    manager = ReproStateManager(initial_states=initial_states)

    # Act and assert
    if initial_states is None:
        assert ReproStateEnum.NONE.value in str(manager)
    else:
        for state in initial_states:
            assert state.value in str(manager)
