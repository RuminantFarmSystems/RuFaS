"""
This file gives some examples of how crops might be specified.
"""

config_1 = {"crop 1": {"crop": "corn"},  # default corn
            "crop 2": {"crop": "alfalfa",   # modified alfalfa
                       "potential_heat_units": 500},
            "crop 3": {"crop": "custom_crop"},  # use custom crop
            "custom crops": {

            }
}