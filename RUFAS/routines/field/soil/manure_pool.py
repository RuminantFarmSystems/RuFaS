class ManurePool:
    """
    Class that stores and tracks attributes of machine and grazing applied manure.

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

    def __init__(
        self,
        manure_dry_mass=0.0,
        manure_applied_mass=0.0,
        manure_field_coverage=0.0,
        manure_moisture_factor=0.0,
        water_extractable_inorganic_phosphorus=0.0,
        water_extractable_organic_phosphorus=0.0,
        stable_inorganic_phosphorus=0.0,
        stable_organic_phosphorus=0.0,
        organic_phosphorus_runoff=0.0,
        inorganic_phosphorus_runoff=0.0,
    ):
        self.manure_dry_mass = manure_dry_mass
        self.manure_applied_mass = manure_applied_mass
        self.manure_field_coverage = manure_field_coverage
        self.manure_moisture_factor = manure_moisture_factor
        self.water_extractable_inorganic_phosphorus = water_extractable_inorganic_phosphorus
        self.water_extractable_organic_phosphorus = water_extractable_organic_phosphorus
        self.stable_inorganic_phosphorus = stable_inorganic_phosphorus
        self.stable_organic_phosphorus = stable_organic_phosphorus
        self.organic_phosphorus_runoff = organic_phosphorus_runoff
        self.inorganic_phosphorus_runoff = inorganic_phosphorus_runoff

    def __eq__(self, other):
        if not isinstance(other, ManurePool):
            return False
        return (
            self.manure_dry_mass == other.manure_dry_mass
            and self.manure_applied_mass == other.manure_applied_mass
            and self.manure_field_coverage == other.manure_field_coverage
            and self.manure_moisture_factor == other.manure_moisture_factor
            and self.water_extractable_inorganic_phosphorus == other.water_extractable_inorganic_phosphorus
            and self.water_extractable_organic_phosphorus == other.water_extractable_organic_phosphorus
            and self.stable_inorganic_phosphorus == other.stable_inorganic_phosphorus
            and self.stable_organic_phosphorus == other.stable_organic_phosphorus
            and self.organic_phosphorus_runoff == other.organic_phosphorus_runoff
            and self.inorganic_phosphorus_runoff == other.inorganic_phosphorus_runoff
        )
