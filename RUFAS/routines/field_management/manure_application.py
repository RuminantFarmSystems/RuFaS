"""
SurPhos
File name: manure_application.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


# calculates # of plops added per day and amount of TP, WIP, and WOP added
# in manure, adds P to surface manure pools, and updates cumulative manure
# and TP added during model run
# "pseudocode_soil" S.6.C
def update_all(soil, manure_storage, m_app):
    manure_application = formulate_manure_application(manure_storage, m_app)
    added_manure_P(soil, manure_application)
    added_manure_N(soil, manure_application)


def formulate_manure_application(manure_storage, m_app):
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

    for storage in manure_storage.storage:
        available_N = sum(storage.N, storage.N_liquid)
        available_P = sum(storage.P, storage.P_liquid)

        available_manure = sum(storage.TS, storage.TS_liquid)

        N_frac = available_N / available_manure
        P_frac = available_P / available_manure

        N_mass = min(available_N, desired_N)
        P_mass = min(available_P, desired_P)

        applied_manure = min(max(N_mass / N_frac, P_mass / P_frac), available_manure)

        N_mass = applied_manure * N_frac
        P_mass = applied_manure * P_frac

        solid_ratio = storage.TS / available_manure
        liquid_ratio = storage.TS_liquid / available_manure

        solid_N_ratio = storage.N / available_N
        solid_P_ratio = storage.P / available_P

        liquid_N_ratio = storage.N_liquid / available_N
        liquid_P_ratio = storage.P_liquid / available_P

        storage.N -= N_mass * solid_N_ratio
        storage.P -= P_mass * solid_P_ratio

        storage.N_liquid -= N_mass * liquid_N_ratio
        storage.P_liquid -= P_mass * liquid_P_ratio

        storage.TS -= applied_manure * solid_ratio
        storage.TS_liquid -= applied_manure * liquid_ratio

        desired_N -= N_mass
        desired_P -= P_mass

        manure_application['WIP'] = applied_manure * storage.WIP_frac
        manure_application['WOP'] = applied_manure * storage.WOP_frac

        manure_application['mass'] += applied_manure

        manure_application['N_mass'] += N_mass
        manure_application['P_mass'] += P_mass

        manure_application['DM'] += applied_manure * solid_ratio

        if desired_N == 0 and desired_P == 0:
            break

    # TODO: this is a rudimentary method for satisfying purchased manure. A
    #  more robust method would require drawing purchased manure from some
    #  variety of input (likely a database)
    if desired_N != 0 or desired_P != 0:
        if desired_N != 0:
            manure_application['N_mass'] += desired_N
        if desired_P != 0:
            manure_application['P_mass'] += desired_P

        N_frac = 0.05 if N_frac == 0 else N_frac
        P_frac = 0.06 if P_frac == 0 else P_frac
        solid_ratio = 0.65 if solid_ratio == 0 else solid_ratio
        manure_application['mass'] = max(manure_application['N_mass'] / N_frac,
                                         manure_application['P_mass'] / P_frac)

        manure_application['N_mass'] = manure_application['mass'] * N_frac
        manure_application['P_mass'] = manure_application['mass'] * P_frac
        manure_application['DM'] = manure_application['mass'] * solid_ratio

    return manure_application


def added_manure_P(soil, m_app):
    m_type = "DAIRY"
    mass = m_app['mass']
    cover_perc = m_app['cover_perc']
    P_mass = m_app['P_mass']
    DM = m_app['DM']
    surf_perc = m_app['surf_perc']
    WIP = m_app['WIP']
    WOP = m_app['WOP']
    depth = m_app['depth']

    WIP_frac = WIP / mass
    WOP_frac = WOP / mass

    soil.manure_type = m_type

    # Update manure characteristics
    # S.6.C.I.1-6
    cover_app = cover_perc * soil.area

    soil.manure_moisture = (soil.manure_moisture * soil.manure_mass + (1.0 - DM) * mass) \
                           / (soil.manure_mass + mass)
    wet_rate = mass / DM / cover_app
    infiltration = min(0.9, 0.000002 * wet_rate + 0.267)

    # S.6.B.3
    for layer in soil.soil_layers:
        layer.active_P *= soil.area
        layer.labile_P *= soil.area

    # application factors
    # S.6.C.II.1
    I_fac = 1.0 - infiltration
    S_fac = 1.0 - surf_perc
    W_fac = 1.0 - (WIP_frac + WOP_frac)

    # concentration factors
    # S.6.C.II.2
    C_WIP = P_mass * WIP_frac * I_fac
    C_WOP = P_mass * WOP_frac * 0.95 * I_fac

    # slurry factors
    # S.6.C.II.3
    S_fac_cover = 1.0
    S_fac_mass = 1.0
    if DM <= 0.15:
        S_fac_cover = 0.5
        S_fac_mass = 0.8
        S_fac = infiltration

    # depth factors
    # S.6.C.II.4
    D_fac_1 = 1.0
    D_fac_2 = 1.0
    if depth > 0.0:
        D_fac_1 = S_fac * C_WIP * C_WOP
        D_fac_2 = S_fac

    # update manure features and composition
    # S.6.C.II.5
    soil.manure_cov = min(soil.area, soil.manure_cov + cover_app * S_fac_cover)
    soil.manure_mass += mass * S_fac_mass
    soil.WIP += P_mass * WIP_frac * S_fac
    soil.WOP += P_mass * WOP_frac * S_fac
    soil.SOP += P_mass * W_fac * 0.75 * surf_perc * S_fac
    soil.SIP += P_mass * W_fac * 0.25 * surf_perc * S_fac

    # update active and labile soil pools for each layer affected by the application
    # S.6.C.II.6
    last_layer = 0
    D_fac_sum = 0
    for layer in soil.soil_layers:
        if layer.bottom_depth_cm < depth:
            D_fac = layer.bottom_depth_cm / depth
            layer.active_P += P_mass * W_fac * 0.25 * I_fac * D_fac_1 * D_fac
            layer.labile_P += C_WIP + C_WOP + (P_mass * W_fac * 0.75 * 0.95 * I_fac * D_fac_2) * D_fac

            D_fac_sum += D_fac
            last_layer += 1

    D_fac = 1 - D_fac_sum
    soil.soil_layers[last_layer].active_P += P_mass * W_fac * 0.25 * I_fac * D_fac_1 * D_fac
    soil.soil_layers[last_layer].labile_P += C_WIP + C_WOP + \
                                             (P_mass * W_fac * 0.75 * 0.95 * I_fac * D_fac_2) * D_fac

    # S.6.B.4
    for layer in soil.soil_layers:
        layer.active_P /= soil.area
        layer.labile_P /= soil.area

    soil.manure_mass_app = soil.manure_mass


def added_manure_N(soil, m_app):
    totalN = m_app['N_mass']

    active_N = totalN * 0.875
    stable_N = totalN * 0.125

    soil.soil_layers[0].active_N += active_N
    soil.soil_layers[0].stable_N += stable_N
