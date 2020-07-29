"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

Description: Implements the nitrogen cycling processes of mineralization and
             decomposition.

Author(s): William Donovan, wmdonovan@wisc.edu
"""

from math import exp


def mineralization_decomp(soil):
    """
    Description:
       Calculates mineralization and decomposition processes for the nitrogen cycle.
       "pseudocode_soil" S.4.E

    Args:
        soil: an instance of the Soil class specified in soil.py
    """

    min_rate = 0.0003
    for layer in soil.soil_layers:
        active_N = layer.active_N
        temp_fac = layer.temp_fac
        water_fac = layer.water_fac

        # "pseudocode_soil" S.4.E.1
        N_min_act = 0
        if layer.temperature > 0:
            N_min_act = min_rate * ((temp_fac * water_fac) ** 0.5) * active_N

        N_min_act = min(layer.active_N, N_min_act)
        layer.active_N -= N_min_act
        layer.NH4 += N_min_act

    # Decomposition and mineralization of Fresh N only occur in the first
    # soil layer.
    layer = soil.soil_layers[0]

    fresh_N = soil.fresh_N
    NO3 = layer.NO3
    res = soil.residue
    BD = layer.bulk_density
    depth = layer.bottom_depth

    # "pseudocode_soil" S.4.E.2
    CN = 0
    if fresh_N + NO3 > 0:
        CN = (0.58 * res) / (fresh_N + NO3)

    fresh_org_P = (res * 0.0003) * BD * depth / 100
    labile_P = layer.labile_P

    # "pseudocode_soil" S.4.E.3
    CP = 0
    if fresh_org_P + labile_P > 0:
        CP = (0.58 * res) / (fresh_org_P + labile_P)

    min_coeff = 0.05

    # "pseudocode_soil" S.4.E.5
    term1 = exp(-0.693 * (CN - 25) / 25)
    term2 = exp(-0.693 * (CP - 200) / 200)
    term3 = 1.0

    res_comp = min(term1, term2, term3)

    # "pseudocode_soil" S.4.E.4
    decay = min_coeff * res_comp * ((layer.temp_fac * layer.water_fac) ** 0.5)

    # decay rate used in calculating residue for crop
    soil.decay_rate = decay

    # "pseudocode_soil" S.4.E.6
    fresh_min = decay * fresh_N

    fresh_min = min(soil.fresh_N, fresh_min)
    soil.fresh_N -= fresh_min

    layer.active_N += (0.2 * fresh_min)
    layer.NH4 += (0.8 * fresh_min)

    # "pseudocode_soil" S.4.E.7/8
    soil.fresh_N += 0.0015 * soil.residue

    soil.soil_layers[0] = layer

    soil.residue = soil.residue * (1 - soil.decay_rate)
