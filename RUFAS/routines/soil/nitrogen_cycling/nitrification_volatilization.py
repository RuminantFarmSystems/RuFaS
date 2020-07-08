"""
RUFAS: Ruminant Farm Systems Model

File name: nitrification_volatilization.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: Implements the nitrogen cycling processes of nitrification and
             volatilization.
"""

from math import exp


#
# nitrification is the transfer of NH4 to NO3, this method determines when that
# transfer occurs and calculates the magnitude of that transfer.
# "pseudocode_soil" S.4.B
#
def nitrification_volatilization(soil):
    for x in range(0, len(soil.soil_layers)):
        layer = soil.soil_layers[x]

        temp_fac = layer.temp_fac

        water_fac = layer.water_fac

        # "pseudocode_soil" S.4.B.3
        if x == 0:
            z_mid = 5
        else:
            z_mid = (layer.bottom_depth + soil.soil_layers[x - 1].bottom_depth) / 2

        exp_part = exp(4.706 - 0.0305 * z_mid)
        DepthFac = 1 - (z_mid / (z_mid + exp_part))

        # "pseudocode_soil" S.4.B.5
        CECFac = 0.15
        VolatilReg = temp_fac * DepthFac * CECFac

        #
        # nitrification only occurs when the soil temperature of a given layer
        # exceeds 5ºC
        #
        NitrReg = 0
        if layer.temperature >= 5:
            # "pseudocode_soil" S.4.B.4
            NitrReg = temp_fac * water_fac

        # "pseudocode_soil" S.4.B.6
        exp_part = exp(-NitrReg - VolatilReg)
        nitri_volatil = layer.NH4 * (1 - exp_part)

        nitri_volatil = min(layer.NH4, nitri_volatil)
        layer.NH4 -= nitri_volatil

        # "pseudocode_soil" S.4.B.7
        FracNitr = 1 - exp(-NitrReg)

        # "pseudocode_soil" S.4.B.8
        FracVolatil = 1 - exp(-VolatilReg)

        # "pseudocode_soil" S.4.B.9/10
        if FracNitr + FracVolatil == 0:
            nitrification = 0
            volatilization = 0

        else:
            nitrification = (FracNitr / (FracNitr + FracVolatil)) * \
                            nitri_volatil
            volatilization = (FracVolatil / (FracNitr + FracVolatil)) * \
                             nitri_volatil

        layer.nitrification = nitrification
        layer.volatilization = volatilization
        layer.nitri_volatil = nitri_volatil

        layer.NO3 += nitrification

