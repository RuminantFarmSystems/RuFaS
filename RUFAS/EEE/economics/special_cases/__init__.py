"""Special-case handlers for economics preprocessing.

Each handler owns the bespoke preprocessing for one or more ``ECONOMIC_MAP``
line items that the generic pipeline cannot express. The main
:class:`~RUFAS.EEE.economics.preprocessing.EconomicPreprocessor` instantiates
the registered handlers and, for each mapping item, delegates to the first
handler whose :meth:`~RUFAS.EEE.economics.special_cases.base.SpecialCaseHandler.matches`
returns ``True``.

To register a new special case, implement a
:class:`~RUFAS.EEE.economics.special_cases.base.SpecialCaseHandler` subclass and
append it to ``SPECIAL_CASE_HANDLERS`` in
:mod:`RUFAS.EEE.economics.preprocessing`.
"""

from RUFAS.EEE.economics.special_cases.base import SpecialCaseHandler
from RUFAS.EEE.economics.special_cases.digester_revenue import DigesterRevenueHandler


__all__ = ["SpecialCaseHandler", "DigesterRevenueHandler"]
