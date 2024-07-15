from enum import Enum


class ElementState(Enum):
    """
    An enumeration of the states an input data element can be in during validation. An element cannot
    be in more than one state at a time.

    Attributes
    ----------
    VALID : int
        The element is valid.
    INVALID : int
        The element is invalid and cannot be fixed.
    FIXED : int
        The element is invalid initially but has been fixed.
    """

    VALID = "valid"
    INVALID = "invalid"
    FIXED = "fixed"


class ElementsCounter:
    """
    A class to keep track of the number of elements in each state during validation.

    Attributes
    ----------
    valid_elements : int
        The number of valid elements.
    invalid_elements : int
        The number of invalid elements.
    fixed_elements : int
        The number of fixed elements.
    """

    def __init__(self) -> None:
        self.valid_elements = 0
        self.invalid_elements = 0
        self.fixed_elements = 0

    def update(self, state: ElementState, value: int) -> None:
        """
        Updates the count of elements in a given state.

        Parameters
        ----------
        state : ElementState
            The state of the element.
        value : int
            The value by which the count should be updated.

        Raises
        ------
        ValueError
            If the state is not one of the valid states.
        """
        if state == ElementState.VALID:
            self.valid_elements += value
        elif state == ElementState.INVALID:
            self.invalid_elements += value
        elif state == ElementState.FIXED:
            self.fixed_elements += value
        else:
            raise ValueError(f"Invalid state: {state}")

    def increment(self, state: ElementState) -> None:
        """
        Increments the count of elements in a given state by one.

        Parameters
        ----------
        state : ElementState
            The state of the element.
        """

        self.update(state, 1)

    def reset(self) -> None:
        """
        Resets the counts of all element states to zero.
        """

        self.valid_elements = 0
        self.invalid_elements = 0
        self.fixed_elements = 0

    def total_elements(self) -> int:
        """
        Returns the total number of elements by adding the counts of valid, invalid, and fixed elements.
        """
        return self.valid_elements + self.invalid_elements + self.fixed_elements

    def __str__(self) -> str:
        """
        Returns a string representation of the ElementsCounter object.
        """

        return str(
            {
                "valid_elements": self.valid_elements,
                "invalid_elements": self.invalid_elements,
                "fixed_elements": self.fixed_elements,
                "total_elements": self.total_elements(),
            }
        )

    def __add__(self, other: "ElementsCounter") -> "ElementsCounter":
        """
        Adds the counts of two ElementsCounter objects together.

        Parameters
        ----------
        other : ElementsCounter
            The other ElementsCounter object to be added.

        Returns
        -------
        ElementsCounter
            A new ElementsCounter object with the counts of the two objects added together.
        """

        new_counter = ElementsCounter()
        new_counter.valid_elements = self.valid_elements + other.valid_elements
        new_counter.invalid_elements = self.invalid_elements + other.invalid_elements
        new_counter.fixed_elements = self.fixed_elements + other.fixed_elements
        return new_counter
