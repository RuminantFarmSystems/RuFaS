from .storage import Storage


class Grain(Storage):
    """
    Represents grain storage and manages its specific attributes and behaviors.

    Inherits from Storage.
    """

    def __init__(self, config: dict[str, str | float], capacity: float = float("inf")):
        super().__init__(config, capacity)
        self.dm_loss_coefficient = config.get("dm_loss_coefficient")


class Dry(Grain):
    """
    Represents dry grain storage and manages its specific attributes and behaviors.

    Inherits from Grain.
    """

    def __init__(self, config: dict[str, str | float]) -> None:
        super().__init__(config)


class HighMoisture(Grain):
    """
    Represents high-moisture grain storage and manages its specific attributes and behaviors.

    Inherits from Grain.
    """

    def __init__(self, config: dict[str, str | float]) -> None:
        super().__init__(config)
