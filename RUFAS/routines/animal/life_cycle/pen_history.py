from RUFAS.routines.animal.pen import Pen


class PenHistory:
    """
    A class to represent the history of a pen on a farm.

    This class tracks the usage of a pen including the start and end dates, the specific pen, and the classes
    of animals that have been in the pen.

    Attributes
    ----------
    start_date : int
        The start date of the pen's usage.
    end_date : int
        The end date of the pen's usage.
    pen : object
        The specific pen object
    classes_in_pen : list[str]
        The classes of animals that have been in the pen.

    Methods
    -------
    None.

    """

    # TODO: Annotate pen later when circular dependency is resolved - may be solved by GitHub Issue # 793
    def __init__(self, start: int, end: int, pen: Pen, classes_in_pen: list[str]):
        """
        Construct the necessary attributes for the PenHistory object.

        Parameters
        ----------
        start : int
            The start date of the pen's usage.
        end : int
            The end date of the pen's usage.
        pen : object
            The specific pen object
        classes_in_pen : list[str]
            The classes of animals that have been in the pen.
        """

        self.start_date = start
        self.end_date = end
        self.pen = pen
        self.classes_in_pen = classes_in_pen
