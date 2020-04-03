def phosphorus_excreted(milk_prod, total_manure, p_feces_excrt, p_urine):
    """
    Calculates the phosphorus excreted by the animal.

    Args:
        milk_prod: daily milk production (kg) (if this function is called for
            a non-cow animal, this value is 0
        total_manure: amount of manure excreted by animal (kg)
        p_feces_excrt: amount of P excreted by an animal (g)
        p_urine: amount of P required for urine production (g)

    Returns:
        P excreted by animal
        WIP (water extractable inorganic P) fraction
        WOP (water extractable organic P) fraction
    """
    # P fraction of manure (A.3.A.4)
    p_frac = (p_feces_excrt + p_urine) / (total_manure * 1000)

    # Water extractable Inorganic P (WIP) fraction - fraction of manure
    # compromised of inorganic water extractable P (A.3.A.5)
    WIP_frac = 0.50 * p_frac

    # Water extractable Organic P (WOP) fraction - fraction of maure
    # compromised of organic water extractable P (A.3.A.6)
    WOP_frac = 0.05 * p_frac

    # amount of P in milk per animal (g) (A.1E.A.5)
    p_milk = 0.0009 * milk_prod * 1000

    # amount of P excreted by an animal (g) (A.3.A.7)
    p_excrt = p_milk + p_feces_excrt + p_urine

    return p_excrt, WIP_frac, WOP_frac
