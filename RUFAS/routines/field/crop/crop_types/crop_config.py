"""
File name: crop_config.py

Author(s): Clay Morrow, morrowcj@outlook.com

Description:
    This module contains configuration variables, with data used to generate the various crop subclasses.
    Each of these variables is a dictionary whose keys and values correspond to class attributes and their values,
    respectively.

    Keeping the attribute data separate from the actual class definitions allows for the values to changed
    dynamically (e.g., at runtime). This makes the code more robust to changes in parameters (e.g., from new varieties
    or genotypes)

    These variables should have the same name as the specific crop type that they are meant to house data for, but in
    capital case. For example, the ``Alfalfa`` class (alfalfa.py) used the config variable ``ALFALFA``

    These configuration variables should NOT include any attributes that are calculated internally,
    iterators or accumulators, attributes whose values do not differ from those in the inherited ``BaseCrop`` class,
    or any variables that do not correspond to crop-specific parameters. They should also NOT include data that is
    normally input by the user (data derived from .json files).
"""
# ToDo: It may be best to document all contained attributes in this file.

# alfalfa.py
ALFALFA = {
        # alfalfa ID variables
        "harvest_type": 'optimal',  # ToDo: is this always the type for alfalfa? Corn reads this from data
        "crop_type": 'perennial',
        "raw_id": 1,
        "feed_id": '1g',
        "fix_nitrogen": True,
        # heat unit variables
        "T_base_min": 4,
        "T_base_max": 43.33,
        "PHU": 800,  # TODO: Potential heat units unknown - GitHub Issue #154
        # LAI parameters
        "fr_PHU_1": 0.15,
        "fr_PHU_2": 0.50,
        "fr_LAI_1": 0.01,
        "fr_LAI_2": 0.95,
        "fr_PHU_sen": 0.90,
        "fr_PHU_harvest": 1.2,
        "fr_PHU_harvest_min": 0.9,
        "LAI_max": 4,
        "LAI_min": 0.75,
        # root depth variables
        "z_root_max": 3000,
        # biomass variables
        "kl": 0.65,
        "RUE": 20,
        "T_opt": 25,
        # water use
        "beta_w": 10,  # ToDo taken from corn GitHub Issue #154
        "epco": 1,
        # nitrogen uptake
        "beta_n": 10,
        "fr_n1": 0.0417,
        "fr_n2": 0.0290,
        "fr_n3": 0.0200,
        "fr_n3ish": 0.02001,
        # phosphorus uptake
        "beta_p": 10,
        "fr_PHU_50": 0.5,
        "fr_PHU_100": 1.0,
        "fr_p1": 0.0035,
        "fr_p2": 0.0028,
        "fr_p3": 0.0020,
        "fr_p3ish": 0.00201,
        # yields
        "HI_max": 0,
        "HI_min": 0.9,
        "HI_actual": 0,
        "HI_opt": 0.9,
        "harvest_eff": 0.9,
        "gamma_wu": 0,
        "biomass_dry_down_percent": 0.0,
        "DM_harvest_percent": 0.15,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #155
        "NDF_harvest_percent": 0.416
}

# corn.py
CORN = {
        # corn ID variables
        "crop_type": 'annual',
        "raw_id": 34,
        "feed_id": '34g',
        "fix_nitrogen": False,
        "kill_year": True,
        # heat unit variables
        "T_base_min": 10,
        "T_base_max": 30,
        "PHU": 1200,
        # LAI parameters
        "fr_PHU_1": 0.15,
        "fr_PHU_2": 0.50,
        "fr_LAI_1": 0.05,
        "fr_LAI_2": 0.95,
        "fr_PHU_sen": 0.90,
        "fr_PHU_harvest": 1.2,
        "fr_PHU_harvest_min": 0.7,
        "LAI_max": 3,
        "LAI_min": 0,
        # root depth
        "z_root_max": 2000,
        # biomass
        "kl": 0.65,
        "RUE": 39,
        "T_opt": 25,
        # water uptake
        "beta_w": 10,
        "epco": 0.5,
        # nitrogen uptake
        "beta_n": 10,
        "fr_n1": 0.047,
        "fr_n2": 0.0177,
        "fr_n3": 0.0138,
        "fr_n3ish": 0.01381,
        # phosphorus
        "beta_p": 10,
        "fr_PHU_50": 0.5,
        "fr_PHU_100": 1.0,
        "fr_p1": 0.0048,
        "fr_p2": 0.0018,
        "fr_p3": 0.0014,
        "fr_p3ish": 0.00141,
        # yield
        "HI_max": 0,
        "HI_min": 0.3,
        "HI_actual": 0,
        "HI_opt": 0.6,
        "harvest_eff": 0.9,
        "biomass_dry_down_percent": 0.0,
        "DM_harvest_percent": 0.35  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #155
}

