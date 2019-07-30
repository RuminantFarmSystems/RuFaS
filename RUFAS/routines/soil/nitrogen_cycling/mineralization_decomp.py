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
    for layer in soil.listOfSoilLayers:
        activeN = layer.activeN
        tempFac = layer.tempFac
        waterFac = layer.waterFac

        # "pseudocode_soil" S.4.E.1
        nMinAct = 0
        if layer.temperature > 0:
            nMinAct = minrate * ((tempFac * waterFac) ** 0.5) * activeN

        nMinAct = min(layer.activeN, nMinAct)
        layer.activeN -= nMinAct
        layer.NH4 += nMinAct

        #
        # Decomposition and mineralization of Fresh N only occur in the first
        # soil layer.
        #
        if layer.name == "Layer1":
            FreshN = layer.topLayerFreshN
            NO3 = layer.NO3
            res = soil.residue
            BD = layer.bulkDensity
            depth = layer.bottomDepth

            # "pseudocode_soil" S.4.E.2
            CN = 0
            if FreshN + NO3 > 0:
                CN = (0.58 * res) / (FreshN + NO3)

            #
            # TODO: these values are taken from phosphorus_cycling.py which is incomplete
            #
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
            Decay = minCoeff * resComp * ((tempFac * waterFac) ** 0.5)

            # decay rate used in calculating residue for crop
            soil.decayRate = Decay

            # "pseudocode_soil" S.4.E.6
            FreshMin = Decay * FreshN

            FreshMin = min(layer.topLayerFreshN, FreshMin)
            layer.topLayerFreshN -= FreshMin

            layer.activeN += (0.2 * FreshMin)
            layer.NH4 += (0.8 * FreshMin)

