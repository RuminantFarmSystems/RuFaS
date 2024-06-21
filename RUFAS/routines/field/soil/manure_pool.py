from dataclasses import dataclass


@dataclass(kw_only=True)
class ManurePool:
    """
    Data class that stores and tracks attributes of machine and grazing applied manure.

    manure_dry_mass : float, default 0
        The dry weight equivalent of manure mass on the field that was applied by machine or grazers (kg).
    manure_applied_mass : float, default 0
        The dry weight equivalent of the most recent application of manure applied by machine or grazers (kg).
    manure_field_coverage : float, default 0
        Fraction of the field that is covered by machine- or grazer-applied manure, between [0, 1] (unitless).
    manure_moisture_factor : float, default 0
        Fraction representing the current moisture level of the machine- or grazer-applied manure on the field, between
        [0, 0.9] (unitless).
    water_extractable_inorganic_phosphorus : float, default 0
        Amount of water extractable inorganic phosphorus on the field that was applied by machine or grazers (kg).
    water_extractable_organic_phosphorus : float, default 0
        Amount of water extractable organic phosphorus on the field that was applied by machine or grazers (kg).
    stable_inorganic_phosphorus : float, default 0
        Amount of stable inorganic phosphorus on the field that was applied by machine or grazers (kg).
    stable_organic_phosphorus : float, default 0
        Amount of stable organic phosphorus on the field that was applied by machine or grazers (kg).
    organic_phosphorus_runoff : float, default 0.0
        Amount of organic phosphorus from machine- or grazer-applied manure dissolved in and removed by runoff (kg).
    inorganic_phosphorus_runoff : float, default 0.0
        Amount of inorganic phosphorus from machine- or grazer-applied manure dissolved in and removed by runoff (kg).

    """

    manure_dry_mass: float = 0
    manure_applied_mass: float = 0
    manure_field_coverage: float = 0
    manure_moisture_factor: float = 0
    water_extractable_inorganic_phosphorus: float = 0
    water_extractable_organic_phosphorus: float = 0
    stable_inorganic_phosphorus: float = 0
    stable_organic_phosphorus: float = 0
    organic_phosphorus_runoff: float = 0.0
    inorganic_phosphorus_runoff: float = 0.0
