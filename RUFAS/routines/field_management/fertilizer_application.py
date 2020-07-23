"""
RuFaS
File name: fertilizer_application.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


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
    fertilizer_application = formulate_fert_app(soil, field_management, fert_app)
    fertilizer_P(soil, field_management, fertilizer_application)
    fertilizer_N(soil, field_management, fertilizer_application)
    fertilizer_K(soil, field_management, fertilizer_application)


def formulate_fert_app(soil, field_management, fert_app):
    """
    Description:
        Takes information about a requested fertilizer application and formulates
        an actual application to meet the parameters of that request
        "pseudocode_field_management" FM.3.A

    Args:
        soil
        fert_app
        field_management

    Returns:
        fertilizer_application: dictionary mirroring fert_app with updated
            information regarding the fertilizer application
    """
    fertilizer_application = dict(fert_app)

    # FM.3.A.1
    N_frac = field_management.managed_applications['fertilizer'].composition['N']
    P_frac = field_management.managed_applications['fertilizer'].composition['P']
    K_frac = field_management.managed_applications['fertilizer'].composition['K']
    N_requested_mass = (0 if N_frac == 0 else (fert_app['N_mass'] / N_frac)) * soil.area
    P_requested_mass = (0 if P_frac == 0 else (fert_app['P_mass'] / P_frac)) * soil.area
    K_requested_mass = (0 if K_frac == 0 else (fert_app['K_mass'] / K_frac)) * soil.area

    # FM.3.A.2
    field_management.fert_applied = max(N_requested_mass, P_requested_mass, K_requested_mass)

    # FM.3.A.3
    fertilizer_application['N_mass'] = field_management.fert_applied * N_frac
    fertilizer_application['P_mass'] = field_management.fert_applied * P_frac
    fertilizer_application['K_mass'] = field_management.fert_applied * K_frac

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


def fertilizer_N(soil, field_management, fert_app):
    """
    Description:
        Applies fertilizer Nitrogen to soil ammonia pools
        "pseudocode_field_management" FM.3.C
    Args:
        soil
        field_management
        fert_app: formulated fertilizer application
    """
    field_management.fert_N_applied = fert_app['N_mass']

    # FM.3.C.1
    soil.soil_layers[0].NH4 += field_management.fert_N_applied


def fertilizer_K(soil, field_management, fert_app):
    """
    Description:
        Applies fertilizer Potassium to the soil
    Args:
        soil
        field_management
        fert_app: formulated fertilizer application
    """
    field_management.fert_K_applied = fert_app['K_mass']

    # FM.3.D.1
    soil.soil_layers[0].K += field_management.fert_K_applied
