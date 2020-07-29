"""
RUFAS: Ruminant Farm Systems Model

File name: nitrification_volatilization.py

Description: Implements the nitrogen cycling processes of nitrification and
             volatilization.

Author(s): William Donovan, wmdonovan@wisc.edu
"""

from math import exp


def nitrification_volatilization(soil):
    """
    Description:
       nitrification is the transfer of NH4 to NO3, this method determines when that
       transfer occurs and calculates the magnitude of that transfer.
       "pseudocode_soil" S.4.B
    Args:
        soil: an instance of the Soil class specified in soil.py
    """

    for x in range(len(soil.soil_layers)):
        layer = soil.soil_layers[x]

        temp_fac = layer.temp_fac

        water_fac = layer.water_fac

        # "pseudocode_soil" S.4.B.3
        if x == 0:
            z_mid = layer.bottom_depth / 2
        else:
            z_mid = (layer.bottom_depth + soil.soil_layers[x - 1].bottom_depth) / 2

        exp_part = exp(4.706 - 0.0305 * z_mid)
        depth_fac = 1 - (z_mid / (z_mid + exp_part))

        # "pseudocode_soil" S.4.B.5
        CEC_fac = 0.15
        volatil_reg = temp_fac * depth_fac * CEC_fac

        # nitrification only occurs when the soil temperature of a given layer
        # exceeds 5ºC
        nitr_reg = 0
        if layer.temperature >= 5:
            # "pseudocode_soil" S.4.B.4
            nitr_reg = temp_fac * water_fac

        # "pseudocode_soil" S.4.B.6
        exp_part = exp(-nitr_reg - volatil_reg)
        tot_nitri_volatil = layer.NH4 * (1 - exp_part)

        tot_nitri_volatil = min(layer.NH4, tot_nitri_volatil)
        layer.NH4 -= tot_nitri_volatil

        # "pseudocode_soil" S.4.B.7
        frac_nitr = 1 - exp(-nitr_reg)

        # "pseudocode_soil" S.4.B.8
        frac_volatil = 1 - exp(-volatil_reg)

        # "pseudocode_soil" S.4.B.9/10
        if frac_nitr + frac_volatil == 0:
            nitrification = 0
            volatilization = 0

        else:
            nitrification = (frac_nitr / (frac_nitr + frac_volatil)) * \
                            tot_nitri_volatil
            volatilization = (frac_volatil / (frac_nitr + frac_volatil)) * \
                             tot_nitri_volatil

        layer.nitrification = nitrification
        layer.volatilization = volatilization
        layer.tot_nitri_volatil = tot_nitri_volatil

        layer.NO3 += nitrification
