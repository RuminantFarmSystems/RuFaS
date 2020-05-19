"""
RUFAS
SurPhos

File name: manure.py

Author(s):  DR. Peter A. Vadas
            USDA-ARS Dairy Forage Research Center
            E-mail: peter.vadas@ars.usda.gov

Coder(s):   Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""


def update_all(soil, m_app):
    """
    Description:
        calculates TP, WIP, and WOP added in the manure, adds P to surface
        manure pools. All units are KG or HA

    Args:
        soil: an instance of the Soil class specified in soil.py
        m_app: an instance of the Manure class specified in
            application_management.py
    """

    soil.manure_type = m_app.type

    # Update manure characteristics
    # S.5.C.I.1-6
    cover_app = m_app.percent_cover * soil.area
    P_app = m_app.mass * m_app.P_frac
    soil.manure_annual += m_app.mass
    soil.manure_P_annual += P_app

    soil.manure_moisture = (soil.manure_moisture * soil.manure_mass + (1.0 - m_app.DM) * m_app.mass) \
                           / (soil.manure_mass + m_app.mass)
    wet_rate = m_app.mass / m_app.DM / cover_app
    infiltration = min(0.9, 0.000002 * wet_rate + 0.267)

    # S.5.B.3
    for layer in soil.soil_layers:
        layer.active_P *= soil.area
        layer.labile_P *= soil.area

    # application factors
    # S.5.C.II.1
    I_fac = 1.0 - infiltration
    S_fac = 1.0 - m_app.surface_percent
    W_fac = 1.0 - (m_app.WIP_frac + m_app.WOP_frac)

    # concentration factors
    # S.5.C.II.2
    C_WIP = P_app * m_app.WIP_frac * I_fac
    C_WOP = P_app * m_app.WOP_frac * 0.95 * I_fac

    # slurry factors
    # S.5.C.II.3
    S_fac_cover = 1.0
    S_fac_mass = 1.0
    if m_app.DM <= 0.15:
        S_fac_cover = 0.5
        S_fac_mass = 0.8
        S_fac = infiltration

    # depth factors
    # S.5.C.II.4
    D_fac_1 = 1.0
    D_fac_2 = 1.0
    if m_app.depth > 0.0:
        D_fac_1 = S_fac * C_WIP * C_WOP
        D_fac_2 = S_fac

    # update manure features and composition
    # S.5.C.II.5
    soil.manure_cov = min(soil.area, soil.manure_cov + cover_app * S_fac_cover)
    soil.manure_mass += m_app.mass * S_fac_mass
    soil.WIP += P_app * m_app.WIP_frac * S_fac
    soil.WOP += P_app * m_app.WOP_frac * S_fac
    soil.SOP += P_app * W_fac * 0.75 * m_app.surface_percent * S_fac
    soil.SIP += P_app * W_fac * 0.25 * m_app.surface_percent * S_fac

    # update active and labile soil pools for each layer affected by the application
    # S.5.C.II.6
    last_layer = 0
    D_fac_sum = 0
    for layer in soil.soil_layers:
        if layer.bottom_depth_cm < m_app.depth:
            D_fac = layer.bottom_depth_cm / m_app.depth
            layer.active_P += P_app * W_fac * 0.25 * I_fac * D_fac_1 * D_fac
            layer.labile_P += C_WIP + C_WOP + (P_app * W_fac * 0.75 * 0.95 * I_fac * D_fac_2) * D_fac

            D_fac_sum += D_fac
            last_layer += 1

    D_fac = 1 - D_fac_sum
    soil.soil_layers[last_layer].active_P += P_app * W_fac * 0.25 * I_fac * D_fac_1 * D_fac
    soil.soil_layers[last_layer].labile_P += C_WIP + C_WOP + \
                                             (P_app * W_fac * 0.75 * 0.95 * I_fac * D_fac_2) * D_fac

    # S.5.B.4
    for layer in soil.soil_layers:
        layer.active_P /= soil.area
        layer.labile_P /= soil.area

    soil.manure_mass_app = soil.manure_mass
