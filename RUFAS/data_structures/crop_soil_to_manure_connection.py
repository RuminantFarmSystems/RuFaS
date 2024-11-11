from typing import NamedTuple, Optional

from RUFAS.data_structures.events import ManureEvent
from RUFAS.data_structures.nutrient_request import NutrientRequest
from RUFAS.data_structures.nutrient_request_results import NutrientRequestResults


class ManureEventNutrientRequest(NamedTuple):
    """Used to couple a manure event with a nutrient request."""

    event: ManureEvent
    nutrient_request: Optional[NutrientRequest]


class ManureEventNutrientRequestResults(NamedTuple):
    """Used to couple a manure event with the results of a nutrient request."""

    event: ManureEvent
    nutrient_request_results: Optional[NutrientRequestResults]
