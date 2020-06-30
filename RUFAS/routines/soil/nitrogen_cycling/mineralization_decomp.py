"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: Implements the nitrogen cycling processes of mineralization and
             decomposition.
"""

from math import exp


#
# Calculates mineralization and decomposition processes for the nitrogen cycle.
# "pseudocode_soil" S.4.E
#
def mineralization_decomp(soil):

    minrate = 0.0003
    for layer in soil.soil_layers:
        active_N = layer.active_N
        temp_fac = layer.temp_fac
        water_fac = layer.water_fac

        # "pseudocode_soil" S.4.E.1
        N_min_act = 0
        if layer.temperature > 0:
            N_min_act = minrate * ((temp_fac * water_fac) ** 0.5) * active_N

        N_min_act = min(layer.active_N, N_min_act)
        layer.active_N -= N_min_act
        layer.NH4 += N_min_act

        #
        # Decomposition and mineralization of Fresh N only occur in the first
        # soil layer.
        #
        if layer.name == "Layer1":
            fresh_N = soil.fresh_N
            NO3 = layer.NO3
            res = soil.residue
            BD = layer.bulk_density
            depth = layer.bottom_depth

            # "pseudocode_soil" S.4.E.2
            CN = 0
            if fresh_N + NO3 > 0:
                CN = (0.58 * res) / (fresh_N + NO3)

            freshOrgP = (res * 0.0003) * BD * depth / 100
            labileP = layer.labile_P

            # "pseudocode_soil" S.4.E.3
            CP = 0
            if freshOrgP + labileP > 0:
                CP = (0.58 * res) / (freshOrgP + labileP)

            minCoeff = 0.05

            # "pseudocode_soil" S.4.E.5
            term1 = exp(-0.693 * (CN - 25) / 25)
            term2 = exp(-0.693 * (CP - 200) / 200)
            term3 = 1.0

            resComp = min(term1, term2, term3)

            # "pseudocode_soil" S.4.E.4
            soil.decay_rate = minCoeff * resComp * ((temp_fac * water_fac) ** 0.5)

            # "pseudocode_soil" S.4.E.6
            FreshMin = soil.decay_rate * fresh_N

            FreshMin = min(soil.fresh_N, FreshMin)
            soil.fresh_N -= FreshMin

            layer.active_N += (0.2 * FreshMin)
            layer.NH4 += (0.8 * FreshMin)

    # "pseudocode_soil" S.4.E.7/8
    soil.fresh_N += 0.0015 * soil.residue
    soil.residue = soil.residue * (1 - soil.decay_rate)

