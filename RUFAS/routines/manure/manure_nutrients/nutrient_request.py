from dataclasses import dataclass, fields

from RUFAS.routines.manure.manure_treatments.manure_types import ManureType


@dataclass(kw_only=True, frozen=True)
class NutrientRequest:
    """A class that represents a request for nutrients from the crop and soil module."""

    nitrogen: float = 0.0
    """Amount of manure nitrogen requested, kg."""

    phosphorus: float = 0.0
    """Amount of manure phosphorus requested, kg."""

    manure_type: ManureType

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
            value = getattr(self, field.name)
            if field.name != "manure_type":
                if value < 0:
                    raise ValueError(f"Field {field.name} must be non-negative.")
            else:
                if not isinstance(value, ManureType):
                    raise ValueError(f"Field {field.name} must be an instance of ManureType.")

        if any(isinstance(getattr(self, field.name), (int, float)) and getattr(self, field.name) > 0.0 for field in fields(self)):
            return
        else:
            for field in fields(self):
                value = getattr(self, field.name)
                print(value)
                print(field.name)
            raise ValueError("At least one nutrient must be requested and positive.")
