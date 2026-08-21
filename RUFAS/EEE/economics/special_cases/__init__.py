"""Special-case handlers for economics preprocessing.

Each handler owns the bespoke preprocessing for one ``ECONOMIC_MAP`` line item
that the generic pipeline cannot express. The main
:class:`~RUFAS.EEE.economics.preprocessing.EconomicPreprocessor` builds a
``(section, name) -> handler`` map from :data:`SPECIAL_CASE_HANDLERS` and
delegates matching line items to them.

To register a new special case, implement a
:class:`~RUFAS.EEE.economics.special_cases.base.SpecialCaseHandler` subclass and
append it to :data:`SPECIAL_CASE_HANDLERS`.
"""

from RUFAS.EEE.economics.special_cases.base import SpecialCaseHandler
from RUFAS.EEE.economics.special_cases.bedding_requirements import BeddingRequirementsHandler


__all__ = ["SpecialCaseHandler", "BeddingRequirementsHandler"]
