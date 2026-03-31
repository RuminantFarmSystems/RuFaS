from .storage import Storage


class Grain(Storage):
    """
    Represents grain storage and manages its specific attributes and behaviors.

    Inherits from Storage.

    Parameters
    ----------
    config : dict[str, str | float]
        Configuration dictionary for the grain storage.

    Attributes
    ----------
    dm_loss_coefficient : float | None
        Coefficient determining how much dry matter is lost in grain storage (unitless).
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
        self.dm_loss_coefficient = config.get("dm_loss_coefficient")


class Dry(Grain):
    """
    Represents dry grain storage and manages its specific attributes and behaviors.

    Inherits from Grain.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)


class HighMoisture(Grain):
    """
    Represents high-moisture grain storage and manages its specific attributes and behaviors.

    Inherits from Grain.
    """

    def __init__(self, config: dict[str, str | float | list[str]]) -> None:
        super().__init__(config)
