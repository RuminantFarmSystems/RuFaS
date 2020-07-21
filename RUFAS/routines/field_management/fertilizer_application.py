"""
RuFaS
File name: fertilizer_application.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


def update_all(soil, fert_app):
    """
    Description:
        Calls the methods necessary to simulate a fertilizer application

    Args:
        soil: an instance of the Soil class defined in soil.py
        fert_app: an instance of the BaseApplication class defined in
            field_management.py representing a requested fertilizer application
    """
    fertilizer_application = formulate_fert_app(fert_app)
    fertilizer_P(soil, fertilizer_application)
    fertilizer_N()
    fertilizer_K()


def formulate_fert_app(fert_app):
    """
    Description:
        Takes information about a requested fertilizer application and formulates
        an actual application to meet the parameters of that request

    Args:
        fert_app

    Returns:
        fertilizer_application: dictionary mirroring fert_app with updated
            information regarding the fertilizer application
    """
    fertilizer_application = dict(fert_app)

    return fertilizer_application


def fertilizer_P(soil, fert_app):
    """
    Description:
        calculates P added in fertilizer, adds fertilizer P to surface pool,
        and updates cumulative fertilizer P added during model run
        "pseudocode_field_management" FM.3
    Args:
        soil
        fert_app: the formulated fertilizer application
    """

    P_mass = fert_app['P_mass']
    surf_perc = fert_app['surface_percent']
    depth = fert_app['depth']

    soil.fert_P_applied = P_mass
    soil.no_rains = 0
    soil.fert_CNT = 1.0

    # At the time of application, 75% of applied fertilizer P is
    # available to be released by rain. Until the first rain event,
    # that P is gradually adsorbed by the soil.
    # FM.3.B.1/2
    soil.fert_P_available += P_mass * 0.75 * surf_perc
    soil.fert_P_released += P_mass * 0.25 * surf_perc

    sum_fac = 0.0
    last_layer = 0
    for layer in soil.soil_layers:
        layer.labile_P *= soil.area

        # for each layer above the application depth
        # FM.3.B.3
        if layer.bottom_depth_cm < depth:
            # FM.3.B.4
            soil.depth_fact = layer.bottom_depth_cm / depth
            layer.labile_P += P_mass * soil.depth_fact * (1.0 - surf_perc)

            sum_fac += soil.depth_fact
            last_layer += 1

    # for the layer at the application depth
    # FM.3.B.5
    soil.depth_fact = 1.0 - sum_fac

    # FM.3.B.3 with FM.3.B.5
    soil.soil_layers[last_layer].labile_P += P_mass * soil.depth_fact * (1.0 - surf_perc)

    # S.5.A.8
    for layer in soil.soil_layers:
        layer.labile_P /= soil.area


def fertilizer_N():
    pass


def fertilizer_K():
    pass
