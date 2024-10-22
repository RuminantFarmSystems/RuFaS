from RUFAS.biophysical.animal.data_types.repro_protocol_enums import ReproStateEnum


class ReproStateManager:
    """
    A class that manages the reproductive states of an animal.

    Notes
    -----
    This class provides methods to enter and exit reproductive states and check if a specific state is active.
    It is designed to handle cases where typically only one state is active, but it works the same
    if multiple active states coexist.

    Parameters
    ----------
    initial_states : set[ReproStateEnum] | None, optional
        The initial reproductive states of the animal. Default is {ReproStateEnum.NONE}.

    Attributes
    ----------
    _states : set[ReproStateEnum]
        A set of currently active reproductive states.

    Methods
    -------
    enter(state: ReproStateEnum, keep_existing: bool = False)
        Enter a new reproductive state.
    exit(state: ReproStateEnum)
        Exit an active reproductive state.
    is_in(state: ReproStateEnum) -> bool
        Check if a specific reproductive state is currently active.
    is_in_any(states: set[ReproStateEnum]) -> bool
        Check if any of the specified reproductive states are currently active.
    reset() -> None
        Clear all current states and revert the state manager to having only the NONE state.
    is_in_empty_state() -> bool
        Check if the current state is in the empty state (NONE).
    """

    def __init__(self, initial_states: set[ReproStateEnum] | None = None) -> None:
        """
        Initialize the ReproStateManager with the given initial states.

        Parameters
        ----------
        initial_states : set[ReproStateEnum] | None, optional
            A set of initial reproductive states to start with. If None, initializes with {ReproStateEnum.NONE}.
        """

        self._states: set[ReproStateEnum] = initial_states if initial_states is not None else {ReproStateEnum.NONE}

    def enter(self, state: ReproStateEnum, keep_existing: bool = False) -> None:
        """
        Enter a reproductive state.

        Notes
        -----
        If `keep_existing` is False or the only current state is NONE, clears existing states before adding the new one.
        If entering NONE, it clears all other states.

        Parameters
        ----------
        state : ReproStateEnum
            The reproductive state to enter.
        keep_existing : bool, optional
            If False (default), clears existing states before adding the new state.

        Raises
        ------
        ValueError
            If attempting to re-enter the same state that is already active.
        """

        if state is ReproStateEnum.NONE:
            self._states = {ReproStateEnum.NONE}
            return

        if not keep_existing or self._states == {ReproStateEnum.NONE}:
            self._states.clear()
        if state in self._states:
            raise ValueError(f"Attempting to re-enter the same state: {state}")
        self._states.add(state)

    def exit(self, state: ReproStateEnum) -> None:
        """
        Exit a reproductive state.

        Notes
        -----
        If the state to exit is NONE or the only current state is NONE, it performs no action.

        Parameters
        ----------
        state : ReproStateEnum
            The reproductive state to exit.

        Raises
        ------
        ValueError
            If attempting to exit a state that is not currently active.
        """

        if state is ReproStateEnum.NONE or self._states == {ReproStateEnum.NONE}:
            return
        if state not in self._states:
            raise ValueError(f"Attempting to exit a state that is not entered: {state}")
        self._states.remove(state)
        if not self._states:
            self._states = {ReproStateEnum.NONE}

    def is_in(self, state: ReproStateEnum) -> bool:
        """
        Check if a specific reproductive state is currently active.

        Parameters
        ----------
        state : ReproStateEnum
            The reproductive state to check.

        Returns
        -------
        bool
            True if the specified state is active, False otherwise.
        """

        return state in self._states

    def is_in_any(self, states: set[ReproStateEnum]) -> bool:
        """
        Check if any of the specified reproductive states are currently active.

        Parameters
        ----------
        states : set[ReproStateEnum]
            The reproductive states to check.

        Returns
        -------
        bool
            True if any of the specified states are active, False otherwise.
        """

        return bool(self._states & states)

    def reset(self) -> None:
        """
        Clear all current states and revert the state manager to having only the NONE state.
        """

        self._states = {ReproStateEnum.NONE}

    def is_in_empty_state(self) -> bool:
        """
        Check if the current state is in the empty state (NONE).

        Returns
        -------
        bool
            True if the current state is NONE, False otherwise.
        """

        return self._states == {ReproStateEnum.NONE}

    def __str__(self) -> str:
        """
        String representation of the current reproductive states.

        Returns
        -------
        str
            A string representation of the current reproductive states.
        """

        return ", ".join([state.value for state in self._states])
