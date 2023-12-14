from .storage import Storage


class Grain(Storage):
    """
    Represents grain storage and manages its specific attributes and behaviors.

    Inherits from Storage.
    """

    pass


class Dry(Grain):
    """
    Represents dry grain storage and manages its specific attributes and behaviors.

    Inherits from Grain.
    """

    pass


class HighMoisture(Grain):
    """
    Represents high-moisture grain storage and manages its specific attributes and behaviors.

    Inherits from Grain.
    """

    pass
