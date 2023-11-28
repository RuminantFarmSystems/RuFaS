from dataclasses import dataclass, fields


@dataclass(kw_only=True, frozen=True)
class NutrientRequest:
    """A class that represents a request for nutrients from the crop and soil module."""

    nitrogen: float = 0.0
    """Amount of manure nitrogen requested, kg."""

    phosphorus: float = 0.0
    """Amount of manure phosphorus requested, kg."""

    def __post_init__(self) -> None:
        """
        Validate the dataclass fields.

        Raises:
            ValueError
                If any field is negative.
            ValueError
                If no fields are positive.

        """
        for field in fields(self):
            if getattr(self, field.name) < 0:
                raise ValueError(f"Field {field.name} must be non-negative.")

        if any(getattr(self, field.name) > 0.0 for field in fields(self)):
            return
        else:
            raise ValueError("At least one nutrient must be requested and positive.")
