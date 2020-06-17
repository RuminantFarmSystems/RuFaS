from .hardcoded_ration import get_nutrient_rqmts, get_ration


def optimize(feed, rqmts):
    return get_ration()


def calculate_rqmts(BW, BCS, CBW, pasture_concentrate, CP_Milk, DOP, DHD,
                    DVD, DIM, fat_milk, lactose_milk, milk, parity,
                    farming_type, nutrients_list):
    return get_nutrient_rqmts()


def set_globals(DMIest, BW, DBW, milk, CP_milk):
    pass


def calculate_requirements(BW, MW, DOP, housing, distance, parity, CI, TP_Milk, Fat_Milk, Lactose_Milk, Milk):
    '''
    Calculate the dietary requirements of the cows. These values are used
    on the RHS of the linear program. Each calculation has a reference to the
    respective calculation in the pseudocode.

    Args:
        BW: Body weight (kg)
        MW: Mature body weight(kg)
        DOP: Days of pregnancy (d)
        housing: Housing type (Barn or Grazing)
        distance: Daily walking distance (km)
        parity: Number of parity
        CI: Calving interval (d)
        TP_Milk: Milk true protein content  (% of milk)
        Fat_Milk: Milk fat content (% of milk)
        Lactose_Milk: Milk lactose content (% of milk)
        Milk: Milk production (kg)

    '''

    # ENERGY REQUIREMENTS (divided into the following 5 components: maintenance,
    # activity, growth, pregnancy, and lactation requirements):
    # Maintenance requirements
    # ------------------------
    #Calf birth weight (kg)
    CBW = MW * 0.06275  #[A.Cow.A.1]
    #Conceptus weight (kg)
    if DOP > 190:   #[A.Cow.A.2]
        CW = (18 + (DOP - 190) * 0.665) * (CBW/45)
    else:
        CW = 0
    #Net energy for maintenance requirement (Mcal)
    NEmaint = (0.08*(BW - CW))**0.75    #[A.Cow.A.3]
    # Activity requirements
    # ---------------------
    #Net energy for activity requirement caused by grazing system (Mcal)
    if housing == 'Grazing':    #[A.Cow.A.4]
        NEa1 = 0.0012*BW
    else:
        NEa1 = 0
    #Net energy for activity requirement caused by hilly topography (Mcal)
    if housing == 'Hilly':      #[A.Cow.A.5]
        NEa2 = 0.006*BW
    else:
        NEa2 = 0
    #Total net energy for activity requirement (Mcal)
    NEa = distance * 0.00045 * BW + NEa1 + NEa2     #[A.Cow.A.6]
    # Growth requirements
    # ---------------------
    #Mature shrunk body weight (kg)
    MSBW = 0.96 * MW        #[A.Cow.A.7]
    #Shrunk body weight, kg
    SBW = 0.96 * BW         #[A.Cow.A.8]
    #Empty body weight, kg
    EBW = 0.891 * SBW       #[A.Cow.A.9]
    #Equivalent shrunk bodyweight (kg)
    EQSBW = (SBW - CW) * (478/MSBW)       #[A.Cow.A.10]
    #Average Daily Gain (kg)
    if parity == 1:         #[A.Cow.A.11]
        ADG = ((0.92-0.82) * MSBW) / CI
    elif parity == 2:
        ADG = ((1 - 0.92) * MSBW) / CI
    else:
        ADG = 0
    #Equivalent empty weight gain (kg)
    EQEBG = 0.956 * ADG     #[A.Cow.A.12]
    #Equivalent shrunk body weight (kg)
    EQEBW = 0.891 * EQSBW   #[A.Cow.A.13]
    #Net energy for growth requirement (Mcal)
    NEg = 0.0635 * EQEBW**0.75 * EQEBG**1.097   #[A.Cow.A.14]
    # Pregnancy requirement
    # ---------------------
    #Metabolizable energy requirement for pregnancy (Mcal)
    if DOP > 190:           #[A.Cow.A.15]
        MEpreg = (2*0.00159*DOP - 0.0352) * (CBW/(45*0.14))
    else:
        MEpreg = 0
    #Net energy requirement for pregnancy (Mcal)
    NEpreg = MEpreg * 0.64  #[A.Cow.A.16]
    # Lactation requirement
    # ---------------------
    #Milk energy (Mcal/kg of milk production)
    Milken = 0.0929 * Fat_Milk + (0.0547/0.93) * TP_Milk + 0.0395 * Lactose_Milk    #[A.Cow.A.17]
    #Net energy requirement for lactation (Mcal)
    NELact = Milken * Milk      #[A.Cow.A.18]

    #DMI ESTIMATION:
    #Dry matter intake estimation is different for lactating cow and dry cow.
    #The sum of dry matter intake of each feed is assumed to be less than
    #dry matter intake estimation (Sum of Feed < DMIest).

    #Fat corrected milk (kg)
    FCM = (0.4 * Milk) + (15 * Fat_Milk * (Milk/100))   #[A.Cow.D.1]
    #Dry matter intake estimation (kg)
    DMIest = (0.372 * FCM + 0.0968 * BW**0.75) * (1- exp(-0.192 *((DIM/7) + 3.67)))
