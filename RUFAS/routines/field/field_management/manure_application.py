"""
SurPhos
File name: manure_application.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


def update_all(soil, field_management, manure_storage, m_app):
    """
    Description:
        Simulates a manure application. Interface between storage and field
        "pseudocode_field_management" FM.4
    Args:
        soil: an instance of the Soil class defined in soil.py
        field_management: an instance of the FieldManagement class defined in
            field_management.py
        manure_storage: an instance of the ManureStorage class defined in
            manure_storage.py
        m_app: an instance of the BaseApplication class specified in
            field_management.py representing a user specified manure application.
    """
    manure_application = formulate_manure_application(manure_storage, m_app)
    added_manure_P(soil, field_management, manure_application)
    added_manure_N(soil, field_management, manure_application)


def formulate_manure_application(manure_storage, m_app):
    """
    Description:
        Interfaces with manure_storage module to formulate an application meeting
        user requested nutrient levels
        "pseudocode_field_management" FM.4.A

    Args:
        manure_storage
        m_app

    Return:
        manure_application: dictionary. the formulated manure application
    """
    manure_application = dict(m_app)
    manure_application['N_mass'] = 0.0
    manure_application['P_mass'] = 0.0
    manure_application['mass'] = 0.0
    manure_application['DM'] = 0.0
    manure_application['WIP'] = 0.0
    manure_application['WOP'] = 0.0

    desired_N = m_app['N_mass']
    desired_P = m_app['P_mass']

    N_frac = 0.0
    P_frac = 0.0
    solid_ratio = 0.0

    for storage in manure_storage.storage.values():
        available_manure = storage.TS + storage.TS_liquid

        # FM.4.A.1-3
        available_N = storage.N + storage.N_liquid
        available_P = storage.P + storage.P_liquid
        available_K = storage.K + storage.K_liquid

        if available_manure == 0 or available_N ==0 or available_P == 0 or available_K == 0:
            continue

        # FM.4.A.4
        N_frac = available_N / available_manure
        P_frac = available_P / available_manure
        K_frac = available_K / available_manure
        CH4_frac = storage.CH4 / available_manure

        # FM.4.A.5
        N_mass = min(available_N, desired_N)
        P_mass = min(available_P, desired_P)

        # FM.4.A.6
        applied_manure = min(max(N_mass / N_frac, P_mass / P_frac), available_manure)

        # FM.4.A.7
        N_mass = applied_manure * N_frac
        P_mass = applied_manure * P_frac
        K_mass = applied_manure * K_frac
        CH4_mass = applied_manure * CH4_frac

        # FM.4.A.8
        solid_ratio = storage.TS / available_manure
        liquid_ratio = storage.TS_liquid / available_manure

        solid_N_ratio = storage.N / available_N
        solid_P_ratio = storage.P / available_P
        solid_K_ratio = storage.K / available_K

        liquid_N_ratio = storage.N_liquid / available_N
        liquid_P_ratio = storage.P_liquid / available_P
        liquid_K_ratio = storage.K_liquid / available_K

        VS_ratio = storage.VS / available_manure
        VS_liquid_ratio = storage.VS_liquid / available_manure

        VS_applied = VS_ratio * applied_manure
        VS_liquid_applied = VS_liquid_ratio * applied_manure

        storage.VS -= VS_applied
        storage.VS_liquid -= VS_liquid_applied

        storage.N -= N_mass * solid_N_ratio
        storage.P -= P_mass * solid_P_ratio
        storage.K -= K_mass * solid_K_ratio
        storage.CH4 -= CH4_mass

        storage.N_liquid -= N_mass * liquid_N_ratio
        storage.P_liquid -= P_mass * liquid_P_ratio
        storage.K_liquid -= K_mass * liquid_K_ratio

        storage.TS -= applied_manure * solid_ratio
        storage.TS_liquid -= applied_manure * liquid_ratio

        desired_N -= N_mass
        desired_P -= P_mass

        WIP_applied = applied_manure * storage.WIP_frac
        WOP_applied = applied_manure * storage.WOP_frac

        storage.WIP -= WIP_applied
        storage.WOP -= WOP_applied

        manure_application['WIP'] = WIP_applied
        manure_application['WOP'] = WOP_applied

        manure_application['mass'] += applied_manure

        manure_application['N_mass'] += N_mass
        manure_application['P_mass'] += P_mass

        manure_application['DM'] += applied_manure * solid_ratio

        if desired_N == 0 and desired_P == 0:
            break

    # TODO: this is a rudimentary method for satisfying purchased manure. - #GitHub Issue #166
    #  A more robust method would require drawing purchased manure from some variety of input (likely a database).
    # FM.4.A.9
    if desired_N != 0 or desired_P != 0:
        if desired_N != 0:
            manure_application['N_mass'] += desired_N
        if desired_P != 0:
            manure_application['P_mass'] += desired_P

        N_frac = 1 if N_frac == 0 else N_frac #TODO: this is an adjustment feature that is availabe if the manure input where total manure, not the exact values. - GitHub Issue #166
        P_frac = 1 if P_frac == 0 else P_frac #TODO: this is an adjustment feature that is availabe if the manure input where total manure, not the exact values. - GitHub Issue #166
        solid_ratio = 0.65 if solid_ratio == 0 else solid_ratio
        manure_application['mass'] = max(manure_application['N_mass'] / N_frac,
                                         manure_application['P_mass'] / P_frac)

        # manure_application['N_mass'] = manure_application['mass'] * N_frac
        # manure_application['P_mass'] = manure_application['mass'] * P_frac
        manure_application['DM'] = manure_application['mass'] * solid_ratio

    return manure_application


def added_manure_P(soil, field_management, m_app):
    """
    Description:
        Apply manure Phosphorus
    Args:
        soil
        field_management
        m_app: the manure application formulated above
    """
    soil.manure_type = "DAIRY"
    cover_percent = m_app['cover_percent']
    field_management.manure_applied = m_app['mass']
    field_management.manure_P_applied = m_app['P_mass']
    DM = m_app['DM']
    surface_percent = m_app['surface_percent']
    soil.WIP_applied = m_app['WIP']
    soil.WOP_applied = m_app['WOP']
    depth = m_app['depth']

    WIP_frac = soil.WIP_applied / field_management.manure_applied
    WOP_frac = soil.WOP_applied / field_management.manure_applied

    # Update manure characteristics
    # FM.4.B.1-5
    cover_app = cover_percent * soil.area

    soil.manure_moisture = (soil.manure_moisture * soil.manure_mass + (1.0 - DM) *
                            field_management.manure_applied) / \
                           (soil.manure_mass + field_management.manure_applied)

    wet_rate = field_management.manure_applied / DM / cover_app
    infiltration = min(0.9, 0.000002 * wet_rate + 0.267)

    # S.5.A.7
    for layer in soil.soil_layers:
        layer.active_P *= soil.area
        layer.labile_P *= soil.area

    # application factors
    # FM.4.C.1
    I_fac = 1.0 - infiltration
    S_fac = 1.0 - surface_percent
    W_fac = 1.0 - (WIP_frac + WOP_frac)

    # concentration factors
    # FM.4.C.2
    C_WIP = field_management.manure_P_applied * WIP_frac * I_fac
    C_WOP = field_management.manure_P_applied * WOP_frac * 0.95 * I_fac

    # slurry factors
    # FM.4.C.3
    S_fac_cover = 1.0
    S_fac_mass = 1.0
    if DM <= 0.15:
        S_fac_cover = 0.5
        S_fac_mass = 0.8
        S_fac = infiltration

    # depth factors
    # FM.4.C.4
    D_fac_1 = 1.0
    D_fac_2 = 1.0
    if depth > 0.0:
        D_fac_1 = S_fac * C_WIP * C_WOP
        D_fac_2 = S_fac

    # update manure features and composition
    # FM.4.C.5
    soil.manure_cov = min(soil.area, soil.manure_cov + cover_app * S_fac_cover)
    soil.manure_mass += field_management.manure_applied * S_fac_mass
    soil.WIP += field_management.manure_P_applied * WIP_frac * S_fac
    soil.WOP += field_management.manure_P_applied * WOP_frac * S_fac
    soil.SOP += field_management.manure_P_applied * W_fac * 0.75 * surface_percent * S_fac
    soil.SIP += field_management.manure_P_applied * W_fac * 0.25 * surface_percent * S_fac

    # update active and labile soil pools for each layer affected by the application
    # FM.4.C.6
    last_layer = 0
    D_fac_sum = 0
    for layer in soil.soil_layers:
        if layer.bottom_depth_cm < depth:
            D_fac = layer.bottom_depth_cm / depth
            layer.active_P += field_management.manure_P_applied * W_fac * 0.25 * \
                              I_fac * D_fac_1 * D_fac
            layer.labile_P += C_WIP + C_WOP + \
                              (field_management.manure_P_applied * W_fac * 0.75 * 0.95 *
                               I_fac * D_fac_2) * D_fac

            D_fac_sum += D_fac
            last_layer += 1

    D_fac = 1 - D_fac_sum
    soil.soil_layers[last_layer].active_P += field_management.manure_P_applied * W_fac * 0.25 * \
                                             I_fac * D_fac_1 * D_fac
    soil.soil_layers[last_layer].labile_P += C_WIP + C_WOP + \
                                             (field_management.manure_P_applied * W_fac * 0.75 * 0.95
                                              * I_fac * D_fac_2) * D_fac

    # S.5.A.8
    for layer in soil.soil_layers:
        layer.active_P /= soil.area
        layer.labile_P /= soil.area


def added_manure_N(soil, field_management, m_app):
    """
    Description:
        Apply manure Nitrogen
        "pseudocode_field_management" FM.4.D

    Args:
        soil
        field_management
        m_app
    """
    field_management.manure_N_applied = m_app['N_mass']

    # FM.4.D.1
    soil.soil_layers[0].active_N += field_management.manure_N_applied * 0.875
    soil.soil_layers[0].stable_N += field_management.manure_N_applied * 0.125
