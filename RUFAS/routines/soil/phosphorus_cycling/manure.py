################################################################################
"""
SurPhos
File name: manure.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################


# calculates # of plops added per day and amount of TP, WIP, and WOP added
# in manure, adds P to surface manure pools, and updates cumulative manure
# and TP added during model run
# "pseudocode_soil" S.6.C
def update_all(soil, m_app):

    m_type = m_app['type']
    mass = m_app['mass']
    percent_cover = m_app['percent_cover']
    P_frac = m_app['P_frac']
    DM = m_app['dry_matter']
    surf_perc = m_app['surf_perc']
    WIP_frac = m_app['WOP_frac']
    WOP_frac = m_app['WIP_frac']
    depth = m_app['depth']

    soil.manure_type = m_type

    # Update manure characteristics
    # S.6.C.I.1-6
    cover_app = percent_cover * soil.area
    P_app = mass * P_frac
    soil.manure_annual += mass
    soil.manure_P_annual += P_app

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
    C_WIP = P_app * WIP_frac * I_fac
    C_WOP = P_app * WOP_frac * 0.95 * I_fac

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
    soil.WIP += P_app * WIP_frac * S_fac
    soil.WOP += P_app * WOP_frac * S_fac
    soil.SOP += P_app * W_fac * 0.75 * surf_perc * S_fac
    soil.SIP += P_app * W_fac * 0.25 * surf_perc * S_fac

    # update active and labile soil pools for each layer affected by the application
    # S.6.C.II.6
    last_layer = 0
    D_fac_sum = 0
    for layer in soil.soil_layers:
        if layer.bottom_depth_cm < depth:
            D_fac = layer.bottom_depth_cm / depth
            layer.active_P += P_app * W_fac * 0.25 * I_fac * D_fac_1 * D_fac
            layer.labile_P += C_WIP + C_WOP + (P_app * W_fac * 0.75 * 0.95 * I_fac * D_fac_2) * D_fac

            D_fac_sum += D_fac
            last_layer += 1

    D_fac = 1 - D_fac_sum
    soil.soil_layers[last_layer].active_P += P_app * W_fac * 0.25 * I_fac * D_fac_1 * D_fac
    soil.soil_layers[last_layer].labile_P += C_WIP + C_WOP + \
                                             (P_app * W_fac * 0.75 * 0.95 * I_fac * D_fac_2) * D_fac

    # S.6.B.4
    for layer in soil.soil_layers:
        layer.active_P /= soil.area
        layer.labile_P /= soil.area

    soil.manure_mass_app = soil.manure_mass
