from dataclasses import field


class FloatWithUnit(float):
    def __new__(cls, value: float, unit: str = "unitless"):
        return float.__new__(cls, value)

    def __init__(self, value: float, unit: str = "unitless"):
        float.__init__(value)
        self.unit = unit


class IntWithUnit(int):
    def __new__(cls, value: int, unit: str = "unitless"):
        return int.__new__(cls, value)

    def __init__(self, value: int, unit: str = "unitless"):
        int.__init__(value)
        self.unit = unit


class FieldWithUnit(field):
    def __new__(cls, init: bool, unit: str = "unitless"):
        return field(init=init)

    def __init__(self, init: bool, unit: str = "unitless"):
        field(init=init)
        self.unit = unit
