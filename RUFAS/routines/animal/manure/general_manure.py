def phosphorus_excreted(BW, milk_prod, p_intake, total_manure):
    """
    Calculates the phosphorus excreted by the animal.

    Args:
        BW: animal body weight (kg)
        milk_prod: daily milk production (kg) (if this function is called for
            a non-cow animal, this value is 0
        p_intake: amount of P in formulated ration (g)
        total_manure: amount of manure excreted by animal (kg)

    Returns:
        P excreted by animal
        WIP (water extractable inorganic P) fraction
        WOP (water extractable organic P) fraction
    """
    # P in milk produced (g) (A.#.C.1)
    p_milk = 0.0009 * milk_prod * 1000

    # P in urine (g) (A.#.C.2)
    p_urine = 0.000002 * BW * 1000

    # P in feces (g) (A.#.C.3)
    p_feces = -2.3 + 0.63 * p_intake

    # P in manure (g) (A.#.C.4)
    p_manure = p_urine + p_feces

    # Water extractable Inorganic P (WIP) fraction - fraction of manure
    # compromised of inorganic water extractable P (A.#.C.5)
    WIP_frac = 0.50 * ((p_feces + p_urine) / (total_manure * 1000))

    # Water extractable Organic P (WOP) fraction - fraction of maure
    # compromised of organic water extractable P (A.#.C.6)
    WOP_frac = 0.05 * ((p_feces + p_urine) / (total_manure * 1000))

    # P excreted (g)
    p_excrt = p_milk + p_manure

    return p_excrt, WIP_frac, WOP_frac
