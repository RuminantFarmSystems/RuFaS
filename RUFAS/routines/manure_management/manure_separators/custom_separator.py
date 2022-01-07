from .base_separator import BaseSeparator


class CustomSeparator(BaseSeparator):
    def __init__(self, separator, separator_data, treatment):
        super().__init__(separator, separator_data, treatment)
