"""
RuFaS
File name: fertilizer_application.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


class BaseFertilizer:
    def __init__(self, data):
        # TODO: stand in for fertilizer database
        self.N_frac = data['N_frac']
        self.P_frac = data['P_frac']
        self.K_frac = data['K_frac']


def update_all(soil, field_management, fert_app):
    """
    Description:
        Calls the methods necessary to simulate a fertilizer application

    Args:
        soil: an instance of the Soil class defined in soil.py
        field_management: an instance of the FieldManagement class defined in
            field_management.py
        fert_app: an instance of the BaseApplication class defined in
            field_management.py representing a requested fertilizer application
    """
    fertilizer_application = formulate_fert_app(field_management, fert_app)
    fertilizer_P(soil, field_management, fertilizer_application)
    fertilizer_N(field_management, fertilizer_application)
    fertilizer_K(field_management, fertilizer_application)


def formulate_fert_app(field_management, fert_app):
    """
    Description:
        Takes information about a requested fertilizer application and formulates
        an actual application to meet the parameters of that request
        "pseudocode_field_management" FM.3.A

    Args:
        fert_app
        field_management

    Returns:
        fertilizer_application: dictionary mirroring fert_app with updated
            information regarding the fertilizer application
    """
    fertilizer_application = dict(fert_app)
    fertilizer = BaseFertilizer({'N_frac': 0.6, 'P_frac': 0.2, 'K_frac': 0.2})

    # FM.3.A.1
    N_requested_mass = fert_app['N_mass'] / fertilizer.N_frac
    P_requested_mass = fert_app['P_mass'] / fertilizer.P_frac
    K_requested_mass = fert_app['K_mass'] / fertilizer.K_frac

    # FM.3.A.2
    field_management.fert_applied = max(N_requested_mass, P_requested_mass, K_requested_mass)

    # FM.3.A.3
    fertilizer_application['N_mass'] = field_management.fert_applied * fertilizer.N_frac
    fertilizer_application['P_mass'] = field_management.fert_applied * fertilizer.P_frac
    fertilizer_application['K_mass'] = field_management.fert_applied * fertilizer.K_frac

    return fertilizer_application


def fertilizer_P(soil, field_management, fert_app):
    """
    Description:
        calculates P added in fertilizer, adds fertilizer P to surface pool,
        and updates cumulative fertilizer P added during model run
        "pseudocode_field_management" FM.3.B
    Args:
        soil
        field_management
        fert_app: the formulated fertilizer application
    """

    P_mass = fert_app['P_mass']
    surf_perc = fert_app['surface_percent']
    depth = fert_app['depth']

    field_management.fert_P_applied = P_mass
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


def fertilizer_N(field_management, fert_app):
    """
    Description:
        TODO: no simulation of fertilizer N
    Args:
        field_management
        fert_app: formulated fertilizer application
    """
    field_management.fert_N_applied = fert_app['N_mass']


def fertilizer_K(field_management, fert_app):
    """
    Description:
        TODO: no simulation of fertilizer K
    Args:
        field_management
        fert_app: formulated fertilizer application
    """
    field_management.fert_K_applied = fert_app['K_mass']
