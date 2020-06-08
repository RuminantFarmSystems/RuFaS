"""
RUFAS
SurPhos

File name: fertilizer.py

Author(s):  DR. Peter A. Vadas
            USDA-ARS Dairy Forage Research Center
            E-mail: peter.vadas@ars.usda.gov

Coder(s):   Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""


def update_all(soil, fert_app):
    """
    Description:
        calculates P added in fertilizer, adds fertilizer P to surface pool,
        and updates cumulative fertilizer P added during model run

    Args:
        soil: an instance of the Soil class specified in soil.py
        fert_app: an instance of the Fertilizer class specified in
            field_management.py
    """
    mass = fert_app['mass']
    surface_percent = fert_app['surface_percent']
    depth = fert_app['depth']

    soil.fert_applied_sum += mass
    soil.no_rains = 0
    soil.fert_CNT = 1

    # At the time of application, 75% of applied fertilizer P is
    # available to be released by rain. Until the first rain event,
    # that P is gradually adsorbed by the soil.
    # S.5.B.1/2
    soil.fert_P_available += mass * 0.75 * surface_percent
    soil.fert_P_released += mass * 0.25 * surface_percent

    sum_fac = 0.0
    last_layer = 0
    for layer in soil.soil_layers:
        # S.5.B.3
        layer.labile_P *= soil.area

        # for each layer above the application depth
        # S.5.B.5/6
        if layer.bottom_depth_cm < depth:
            soil.depth_fact = layer.bottom_depth_cm / depth
            layer.labile_P += mass * soil.depth_fact * (1.0 - surface_percent)

            sum_fac += soil.depth_fact
            last_layer += 1

    # for the layer at the application depth
    # S.5.B.5/7
    soil.depth_fact = 1.0 - sum_fac
    soil.soil_layers[last_layer].labile_P += mass * soil.depth_fact * (1.0 - surface_percent)

    # S.B.4
    for layer in soil.soil_layers:
        layer.labile_P /= soil.area
