from dataclasses import field


class FloatWithUnit(float):
    def __new__(cls, value: float | None, unit: str = "unitless"):
        return float.__new__(cls, value) if value is not None else None

    def __init__(self, value: float, unit: str = "unitless"):
        float.__init__(value)
        self.unit = unit


class IntWithUnit(int):
    def __new__(cls, value: int | None, unit: str = "unitless"):
        return int.__new__(cls, value) if value is not None else None

    def __init__(self, value: int, unit: str = "unitless"):
        int.__init__(value)
        self.unit = unit
