from RUFAS.EEE.economics.handler.base import Handler
from RUFAS.EEE.economics.handler.bedding_requirements import BeddingRequirementsHandler


SPECIAL_CASE_HANDLERS: list[type[Handler]] = [
    BeddingRequirementsHandler,
]

__all__ = ["SPECIAL_CASE_HANDLERS", "Handler", "BeddingRequirementsHandler", ]
