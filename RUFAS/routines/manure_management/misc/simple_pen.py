from RUFAS.routines.animal.pen import Pen


class SimplePen:
    """
    A simplified Pen class that extracts only relevant information from the
    original Pen class in the animal module.

    """

    def __init__(self, pen: Pen):
        """
        Initializes a SimplePen object.

        Args:
            pen: A Pen object from the animal module.

        """

        self._id = pen.id
        # TODO: Will add more attributes in the next pull request

    @property
    def id(self) -> int:
        """
        Returns the id of this SimplePen object.

        Returns:
            The id of this SimplePen object.

        """

        return self._id
