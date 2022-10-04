"""
File name: crop_config.py

Author(s): Clay Morrow, morrowcj@outlook.com

Description:
    This module contains configuration variables, with data used to generate an instance of the crop.
    Each of these variables is a dictionary whose keys and values correspond to class attributes and their values,
    respectively.

    Keeping the attribute data separate from the actual class definition allows for the values to changed
    dynamically (e.g., at runtime). This makes the code more robust to changes in parameters (e.g., from new varieties
    or genotypes)

    These variables should have the same name as the specific crop species that they are meant to house data for, but in
    capital case. For example, a class instance for the "alfalfa" species uses the config variable ``ALFALFA``. This
    functionality is implemented in ``BaseClass`` in base_class.py.

    These configuration variables should NOT include any attributes that are calculated internally,
    iterators or accumulators, attributes whose values do not differ from defaults of the ``BaseCrop`` class,
    or any variables that do not correspond to crop-specific parameters.
"""

ALFALFA = {
        # alfalfa ID variables
        "harvest_type": 'optimal',  # TODO: is this always the type for alfalfa? Corn reads this from data
        "crop_type": 'perennial',
        "raw_id": 1,
        "feed_id": '1g',
        "fix_nitrogen": True,
        # heat unit variables
        "T_base_min": 4,
        "T_base_max": 43.33,
        "PHU": 800,  # TODO: Potential heat units unknown - GitHub Issue #157
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
        "beta_w": 10,  # TODO taken from corn GitHub Issue #157
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
        "biomass_dry_down_percent": 0.0,  # TODO: GitHub Issue #156
        "DM_harvest_percent": 0.15,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.416  # TODO: GitHub Issue #156
}

CORN = {
        # corn ID variables
        "crop_type": 'annual',
        "raw_id": 34,
        "feed_id": '34g',
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
        "biomass_dry_down_percent": 0.0,  # TODO: GitHub Issue #156
        "DM_harvest_percent": 0.35  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
}

CEREAL_RYE = {
        "crop_type": 'annual',
        "feed_id": '107g',
        "raw_id": 107,
        "kill_year": True,
        "T_base_min": 0,
        "T_base_max": 30,  # TODO: GitHub Issue #157
        "PHU": 996,  # TODO: Potential heat units unknown - GitHub Issue #157
        "fr_PHU_sen": 0.80,
        "fr_PHU_harvest": 1.2,  # TODO: GitHub Issue #157
        "LAI_max": 4,
        "z_root_max": 1800,
        "kl": 0.65,  # TODO: GitHub Issue #157
        "RUE": 35,
        "T_opt": 18,
        "beta_w": 10,  # TODO: water-use distribution parameter - GitHub Issue #157
        "epco": 0.5,  # TODO: GitHub Issue #157
        "fr_n1": 0.0600,
        "fr_n2": 0.0231,
        "fr_n3": 0.0130,
        "fr_n3ish": 0.01301,  # TODO: GitHub Issue #157
        "fr_p1": 0.0084,
        "fr_p2": 0.0032,
        "fr_p3": 0.0019,
        "fr_p3ish": 0.00191,  # TODO: GitHub Issue #157
        "HI_min": 0.2,
        "HI_opt": 0.40,
        "biomass_dry_down_percent": 0.0,  # TODO: Hard coded total dry down until daily method is modeled - GitHub Issue #156
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.416  # TODO: GitHub Issue #156
}

FALL_OATS = {
        "crop_type": 'annual',
        "feed_id": '103g',
        "raw_id": 103,
        "kill_year": True,
        "T_base_min": 0,
        "T_base_max": 30,  # TODO: GitHub Issue #157
        "PHU": 1600,  # 1500-1750  # TODO Potential heat units unknown - GitHub Issue #154
        "fr_LAI_1": 0.02,
        "LAI_max": 4,
        "z_root_max": 2000,
        "kl": 0.65,  # TODO: GitHub Issue #157
        "RUE": 35,
        "T_opt": 15,
        "beta_w": 10,  # TODO: water-use distribution parameter - GitHub Issue #157
        "epco": 0.5,  # TODO: GitHub Issue #157
        "fr_n1": 0.0600,
        "fr_n2": 0.0231,
        "fr_n3": 0.0134,
        "fr_n3ish": 0.01341,  # TODO: GitHub Issue #157
        "fr_p1": 0.0084,
        "fr_p2": 0.0032,
        "fr_p3": 0.0019,
        "fr_p3ish": 0.00191,  # TODO: GitHub Issue #157
        "HI_min": 0.175,
        "HI_opt": 0.42,
        "biomass_dry_down_percent": 0.0,  # TODO: Hard coded total dry down until daily method is modeled - GitHub Issue #156
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.416  # TODO: GitHub Issue #156
}

POTATO = {
        "crop_type": 'annual',
        "feed_id": '105g',
        "raw_id": 105,
        "kill_year": True,
        "T_base_min": 10,  # TODO: GitHub Issue #157
        "T_base_max": 40,
        "PHU": 1000,
        "fr_PHU_harvest": 1.2,
        "LAI_max": 4,
        "z_root_max": 600,
        "T_opt": 22,
        "beta_w": 10,
        "epco": 0.5,
        "fr_n1": 0.055,
        "fr_n2": 0.02,
        "fr_n3": 0.012,
        "fr_n3ish": 0.0121,
        "fr_p1": 0.006,
        "fr_p2": 0.0025,
        "fr_p3": 0.0019,
        "fr_p3ish": 0.00191,
        "HI_min": 0.95,
        "HI_opt": 0.95,
        "harvest_eff": 1.2,
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.416,  # TODO: GitHub Issue #156
}

SOYBEAN = {
        "crop_type": 'annual',
        "raw_id": 121,
        "feed_id": '121g',
        "kill_year": True,
        "is_nitrogen_fixer": True,
        "T_base_max": 43.33,
        "PHU": 1150,
        "fr_LAI_1": 0.05,
        "fr_PHU_harvest": 1.2,
        "z_root_max": 1700,
        "kl": 0.45,
        "RUE": 25,
        "T_opt": 25,
        "beta_w": 10,
        "epco": 1,
        "fr_n1": 0.0524,
        "fr_n2": 0.0265,
        "fr_n3": 0.0258,
        "fr_n3ish": 0.02581,
        "fr_p1": 0.0074,
        "fr_p2": 0.0037,
        "fr_p3": 0.0035,
        "fr_p3ish": 0.00351,
        "HI_min": 0.01,
        "HI_opt": 0.31,
        "DM_harvest_percent": 0.15,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.466  # TODO: GitHub Issue #156
}

SPRING_BARLEY = {
        "crop_type": 'annual',
        "feed_id": '10g',
        "raw_id": 10,
        "kill_year": True,
        "T_base_min": 10,
        "T_base_max": 35,
        "PHU": 952,
        "fr_PHU_2": 0.45,
        "fr_PHU_harvest": 1.2,
        "LAI_max": 4,
        "z_root_max": 1300,
        "RUE": 35,
        "beta_w": 10,
        "epco": 0.5,
        "fr_n1": 0.059,
        "fr_n2": 0.0226,
        "fr_n3": 0.0131,
        "fr_n3ish": 0.01311,
        "fr_p1": 0.0057,
        "fr_p2": 0.0022,
        "fr_p3": 0.0013,
        "fr_p3ish": 0.00131,
        "HI_min": 0.2,
        "harvest_eff": 0.54,
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.416  # TODO: GitHub Issue #156
}

SPRING_WHEAT = {
        "crop_type": 'annual',
        "feed_id": '130g',
        "raw_id": 130,
        "kill_year": True,
        "is_nitrogen_fixer": False,  # TODO: change back - GitHub Issue #160
        "T_base_min": 0,
        "T_base_max": 35,
        "PHU": 996,
        "fr_LAI_1": 0.05,
        "fr_PHU_harvest": 1.2,
        "LAI_max": 4,
        "z_root_max": 2000,
        "RUE": 35,
        "T_opt": 18,
        "beta_w": 10,
        "epco": 0.5,
        "fr_n1": 0.06,
        "fr_n2": 0.0231,
        "fr_n3": 0.0134,
        "fr_n3ish": 0.01341,
        "fr_p1": 0.0084,
        "fr_p2": 0.0032,
        "fr_p3": 0.0019,
        "fr_p3ish": 0.00191,
        "HI_min": 0.2,
        "HI_opt": 0.42,
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.416,  # TODO: GitHub Issue #156
}

SUGAR_BEET = {
        "crop_type": 'annual',
        "feed_id": '11g',
        "raw_id": 11,
        "kill_year": True,
        "T_base_min": 1.1,
        "PHU": 1253,
        "fr_PHU_1": 0.05,
        "fr_LAI_1": 0.05,
        "fr_PHU_sen": 0.90,
        "fr_PHU_harvest": 1.2,
        "LAI_max": 5,
        "z_root_max": 2000,
        "RUE": 30,
        "T_opt": 18,
        "beta_w": 10,
        "epco": 0.5,
        "fr_n1": 0.055,
        "fr_n2": 0.02,
        "fr_n3": 0.012,
        "fr_n3ish": 0.0121,
        "fr_p1": 0.006,
        "fr_p2": 0.0025,
        "fr_p3": 0.0019,
        "fr_p3ish": 0.00191,
        "HI_min": 0.95,
        "HI_opt": 0.95,
        "harvest_eff": 0.549,
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.458,  # TODO: GitHub Issue #156
}

TALL_FESCUE = {
        "crop_type": 'perennial',
        "feed_id": '56g',
        "raw_id": 56,
        "T_base_min": 10,  # TODO parameter unknown - GitHub Issue #157
        "T_base_max": 40,
        "PHU": 648,
        "fr_PHU_sen": 0.8,
        "fr_PHU_harvest": 0.6,
        "fr_PHU_harvest_min": 0.9,
        "LAI_max": 4,
        "LAI_min": 0.75,
        "z_root_max": 2000,
        "RUE": 30,
        "T_opt": 15,
        "beta_w": 10,  # TODO: unknown value - GitHub Issue #157
        "epco": 0.5,
        "fr_n1": 0.0560,
        "fr_n2": 0.0210,
        "fr_n3": 0.0120,
        "fr_n3ish": 0.0121,
        "fr_p1": 0.0099,
        "fr_p2": 0.0022,
        "fr_p3": 0.0019,
        "fr_p3ish": 0.00191,
        "HI_min": 0.9,
        "HI_opt": 0.9,
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        'NDF_harvest_percent': 0.416  # TODO: GitHub Issue #156
}

TRITICALE = {
        "crop_type": 'annual',
        "feed_id": '125g',
        "raw_id": 125,
        "kill_year": True,
        "T_base_min": 0,
        "T_base_max": 30,  # TODO: GitHub Issue #157
        "PHU": 1600,  # 1550-1680  # TODO Potential heat units unknown - GitHub Issue #157
        "fr_PHU_1": 0.05,
        "fr_PHU_2": 0.45,
        "fr_LAI_1": 0.05,
        "LAI_max": 4,
        "z_root_max": 1300,
        "kl": 0.65,  # TODO: GitHub Issue #157
        "RUE": 30,
        "T_opt": 18,
        "beta_w": 10,  # TODO: water-use distribution parameter - GitHub Issue #157
        "epco": 0.5,  # TODO: GitHub Issue #157
        "fr_n1": 0.0663,
        "fr_n2": 0.0255,
        "fr_n3": 0.0148,
        "fr_n3ish": 0.01481,
        "fr_p1": 0.0053,
        "fr_p2": 0.0020,
        "fr_p3": 0.0012,
        "fr_p3ish": 0.00121,
        "HI_min": 0.2,
        "HI_opt": 0.4,
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        "NDF_harvest_percent": 0.416  # TODO: GitHub Issue #156
}

WINTER_WHEAT = {
        "crop_type": 'annual',
        "feed_id": '130g',
        "raw_id": 130,
        "kill_year": True,
        "T_base_min": 0,
        "T_base_max": 30,  # TODO: GitHub Issue #157
        "PHU": 1600,  # 1550-1680  # TODO Potential heat units unknown - GitHub Issue #157
        "fr_PHU_1": 0.05,
        "fr_PHU_2": 0.45,
        "fr_LAI_1": 0.05,
        "LAI_max": 4,
        "LAI_min": 0,
        "z_root_max": 1300,
        "kl": 0.65,  # TODO: GitHub Issue #157
        "RUE": 30,
        "T_opt": 18,  # TODO: GitHub Issue #157
        "beta_w": 10,  # TODO: water-use distribution parameter - GitHub Issue #157
        "epco": 0.5,  # TODO: GitHub Issue #157
        "fr_n1": 0.0663,
        "fr_n2": 0.0255,
        "fr_n3": 0.0148,
        "fr_n3ish": 0.01481,
        "fr_p1": 0.0053,
        "fr_p2": 0.0020,
        "fr_p3": 0.0012,
        "fr_p3ish": 0.00121,
        "HI_min": 0.2,
        "HI_opt": 0.4,
        "DM_harvest_percent": 0.0001,  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #156
        'NDF_harvest_percent': 0.416  # TODO: GitHub Issue #156
}
