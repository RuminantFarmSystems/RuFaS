RuFaS Design Document: Slurry Manure Storage - Outdoor
======================================================

Module: Manure

Outcomes Tracked by Manure Module

+-----------------------------------+-----------------------------------+
|    | •                            |    | N2O, CH4, NH3 emissions      |
|    | •                            |    | Manure composition post      |
|    | •                            |      processing and storage       |
|                                   |      Energy production and use    |
|                                   |      (via EE module)              |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

List of Manure Management Practices Design Documents

| 1. Bedding
| a. Sand
| b. Organic Material
| 2. Collection
| a. Scraping
| b. Flushing
| 3. Processing
| a.Anaerobic Digestion (treatment)
| b.Solid-liquid separation
| 4. Storage and/or Treatment:
| a.Lagoon (treatment)
| b.Composting
| c.Compost Bedded Pack Barn (CBPB)
| d.Slurry Storage - underfloor
| **e.Slurry Storage – outdoor**
| f.Open lot
| 5. Manure Field Connector
| a. Land Application (i.e. Daily Spread)

   **I.** **Overview**

"Dairy manure slurry storage" refers to the practice of containing and
storing manure from dairy operations in the form of a slurry (7 to 12%
dry matter), which is a mixture of manure, wash water, and sometimes
bedding material. The slurry manure is typically stored underfloor or
outside in earthen basin or tanks. The under-floor pit in which manure
is deposited directly into the pit through slatted floors. Other slurry
manure storage facilities are outdoor earthen pits or tanks. In this
document, we consider the slurry manure stored outside in earthen basin
or tanks.

These storage facilities are typically designed to accommodate a minimum
of 120 days' worth of storage capacity.Outdoor slurry storage design
calculations also take into account the additional volume from
precipitations.

   **II.** **Existing Solution**

   **III.** **Proposed Solution**

1

   **Section 0. Input Requirements, Intermediary Steps, and Output
   variables. 0.1 Input Requirement table**

+-------------+-------------+-------------+-------------+-------------+
|             |    **Abb    |    **Unit** |             |             |
|  **Variable | reviation** |             |  **Origin** |   **Notes** |
|    Name**   |             |             |             |             |
+=============+=============+=============+=============+=============+
|    Pen id   |             |    Unitless |    Pen      |             |
|             |             |             |    Class    |             |
|             |             |             |    (?)      |             |
+-------------+-------------+-------------+-------------+-------------+
|    Pen Size |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Housing  |             |    Unitless |    Animal   |             |
|    type     |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| Number of   |             |    Unitless |    Animal   |             |
| Animal      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Animal   |             |    Unitless |    Animal   |             |
|    types    |             |             |             |             |
|    (calf,   |             |             |             |             |
|    heifers, |             |             |             |             |
|             |             |             |             |             |
|  lactating, |             |             |             |             |
|    and dry  |             |             |             |             |
|    cows)    |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Manure   |    MMt      |    kg       |    Animal   |             |
|    Mass     |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Total    |    | 𝑡      |    kg       |    Animal   |             |
|    Solids   |             |             |             |             |
|    at time  |  | 𝑇𝑆𝑚𝑎𝑛𝑢𝑟𝑒 |             |             |             |
|    t from   |             |             |             |             |
|    manure   |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Volatile |    VS       |    kg       |    Animal   |             |
|    Solids   |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| Urea        |             |    gram/L   |    Animal   |             |
| co          |             |             |             |             |
| ncentration |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Urine    |             |    kg       |    Animal   |             |
+-------------+-------------+-------------+-------------+-------------+
|    Urine    |             |    kg       |    Animal   |             |
|    TAN      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Manure   |             |    kg       |    Animal   |             |
|    TAN      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Urine N  |             |    kg       |    Animal   |             |
+-------------+-------------+-------------+-------------+-------------+
|    Fecal    |             |    kg       |    Animal   |             |
|    Nitrogen |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    |        |             |    unitless |             |             |
|  Proportion |             |             |             |             |
|      of     |             |             |             |             |
|    | Carbon |             |             |             |             |
|      in     |             |             |             |             |
|      manure |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Water    |    WIP(t)   |    kg       |    Animal   |             |
|             |             |             |             |             |
|   Inorganic |             |             |             |             |
|             |             |             |             |             |
|  Phosphorus |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Water    |    WOP(t)   |    kg       |    Animal   |             |
|    Organic  |             |             |             |             |
|             |             |             |             |             |
|  Phosphorus |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    NWIP(t)  |    kg       |    Animal   |             |
| | Non-water |             |             |             |             |
|             |             |             |             |             |
|   Inorganic |             |             |             |             |
|    |        |             |             |             |             |
|  Phosphorus |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    NWOP(t)  |    kg       |    Animal   |             |
|   Non-water |             |             |             |             |
|    Organic  |             |             |             |             |
|             |             |             |             |             |
|  Phosphorus |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    P        |    kg       |    Animal   |             |
|  Phosphorus |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    K        |    kg       |    Animal   |             |
|   Potassium |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Enteric  |             |    kg       |    Animal   |             |
|    Methane  |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |             |             |    User     |             |
|   | Bedding |             |             |             |             |
|      type   |             |             |             |             |
|             |             |             |             |             |
| | (sawdust, |             |             |             |             |
|      manure |             |             |             |             |
|             |             |             |             |             |
|     solids, |             |             |             |             |
|      straw) |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Bedding  |             |             |    User     |             |
|    quantity |             |   kg/animal |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Total    | 𝑄𝑏𝑒𝑑𝑑𝑖𝑛𝑔    |    kg       |             |             |
|    bedding  |             |             |             |             |
|    quantity |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    | Date   |             |             |             |             |
|      of     |             |             |             |             |
|      Last   |             |             |             |             |
|    | man    |             |             |             |             |
| ure-bedding |             |             |             |             |
|      mix    |             |             |             |             |
|             |             |             |             |             |
|    complete |             |             |             |             |
|             |             |             |             |             |
|   | removal |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

2

+-------------+-------------+-------------+-------------+-------------+
|             |             |             |             |             |
|  Proportion |             |             |             |             |
|    of C in  |             |             |             |             |
|    Bedding  |             |             |             |             |
+=============+=============+=============+=============+=============+
|    Bedding  |    Set at 0 |    kg       |             |             |
|    P        |             |             |             |             |
|    content  |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| Bedding N   |             |             |             |             |
| content     |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| Bedding K   |             |             |             |             |
| content     |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Daily    |             |             |    User     |             |
|    Tillage  |             |             |             |             |
|             |             |             |             |             |
|   frequency |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    T        |    oC / K   |    Weather  |             |
| Temperature |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    | Total  |             |             |             |             |
|      Solids |   | 𝑏𝑒𝑑𝑑𝑖𝑛𝑔 |             |             |             |
|      at     |    | 𝑇𝑆𝑡    |             |             |             |
|      time t |             |             |             |             |
|      from   |             |             |             |             |
|             |             |             |             |             |
|     bedding |             |             |             |             |
|             |             |             |             |             |
|  | material |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             | 𝑊𝐼𝑃𝑏𝑝(𝑡 =   |    kg       |             |             |
|   | Initial | 0) = 0      |             |             |             |
|             |             |             |             |             |
|     Bedding |             |             |             |             |
|             |             |             |             |             |
|    Material |             |             |             |             |
|      Water  |             |             |             |             |
|             |             |             |             |             |
| extractable |             |             |             |             |
|             |             |             |             |             |
| | inorganic |             |             |             |             |
|      P      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    𝑊𝑂𝑃𝑏𝑝(𝑡  |    kg       |             |             |
|   | Initial |    = 0) = 0 |             |             |             |
|             |             |             |             |             |
|     Bedding |             |             |             |             |
|             |             |             |             |             |
|  | Material |             |             |             |             |
|      Water  |             |             |             |             |
|    |        |             |             |             |             |
| extractable |             |             |             |             |
|             |             |             |             |             |
|     organic |             |             |             |             |
|      P      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    𝑁𝑊𝐼𝑃𝑏𝑝(𝑡 |    kg       |             |             |
|   | Initial |    = 0) = 0 |             |             |             |
|             |             |             |             |             |
|     Bedding |             |             |             |             |
|             |             |             |             |             |
|  | Material |             |             |             |             |
|             |             |             |             |             |
|    NonWater |             |             |             |             |
|             |             |             |             |             |
| extractable |             |             |             |             |
|             |             |             |             |             |
| | inorganic |             |             |             |             |
|      P      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    𝑁𝑊𝑂𝑃𝑏𝑝(𝑡 |    kg       |             |             |
|   | Initial |    = 0) = 0 |             |             |             |
|             |             |             |             |             |
|     Bedding |             |             |             |             |
|             |             |             |             |             |
|  | Material |             |             |             |             |
|             |             |             |             |             |
|    NonWater |             |             |             |             |
|             |             |             |             |             |
| extractable |             |             |             |             |
|             |             |             |             |             |
|     organic |             |             |             |             |
|      P      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

**0.2. The above information is collected and used to calculate the
manure-bedding mix composition and management each day**

+-----------------+-----------------+-----------------+-----------------+
|    Total manure |                 |    Kg           |                 |
|    mass         |                 |                 |                 |
+=================+=================+=================+=================+
|    Density of   |                 |    kg/m3        |                 |
|    the manure   |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Manure       |                 |    oC           |                 |
|    temperature  |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    𝑂𝑢𝑡𝑑𝑜𝑜𝑟      |                 |    m2           |                 |
|    𝑆𝑙𝑢𝑟𝑟𝑦       |                 |                 |                 |
|    𝐴𝑚𝑎𝑛𝑢𝑟𝑒      |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

**0.3. Based on the manure mass, composition, and temperature, the
routines should calculate: (explained in proposed solution)**

+-----------------+-----------------+-----------------+-----------------+
|    Loss of      |                 |    kg/day       |                 |
|    mass/ dry    |                 |                 |                 |
|    matter       |                 |                 |                 |
|    through CH4  |                 |                 |                 |
|    and CO2      |                 |                 |                 |
|    emissions    |                 |                 |                 |
+=================+=================+=================+=================+
|    Loss of      |                 |    kg/day       |                 |
|    nitrogen     |                 |                 |                 |
|    through      |                 |                 |                 |
|    ammonia      |                 |                 |                 |
|    emissions    |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    | Loss of    |                 |    kg/day       |                 |
|      nitrogen   |                 |                 |                 |
|    | through    |                 |                 |                 |
|      nitrous    |                 |                 |                 |
|      oxide      |                 |                 |                 |
|      emissions  |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

3

+-----------------+-----------------+-----------------+-----------------+
|                 |                 |                 |                 |
|  Transformation |                 |                 |                 |
|    of manure    |                 |                 |                 |
|    phosphorus   |                 |                 |                 |
|    chemical     |                 |                 |                 |
|    forms        |                 |                 |                 |
+=================+=================+=================+=================+
|    | Indicator  |                 |                 |                 |
|      of         |                 |                 |                 |
|    | Tillage/no |                 |                 |                 |
|      tillage of |                 |                 |                 |
|      the        |                 |                 |                 |
|                 |                 |                 |                 |
|  manure-bedding |                 |                 |                 |
|      mix at     |                 |                 |                 |
|      time t     |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

**0.4. The following characteristics of the manure mix need to be
calculated and updated each day with respect to the losses in
emissions.**

+-----------------+-----------------+-----------------+-----------------+
|                 |                 |                 |    Comment      |
+=================+=================+=================+=================+
|    Proportion   |                 |    %            |                 |
|    of Dry       |                 |                 |                 |
|    matter to    |                 |                 |                 |
|    total Mass   |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Proportion   |                 |    %            | 1- Proportion   |
|    of Moisture  |                 |                 | of Dry matter   |
|    to total     |                 |                 | to total Mass   |
|    mass         |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Proportion   |                 |    %            |                 |
|    of Nitrogen  |                 |                 |                 |
|    in dry       |                 |                 |                 |
|    Matter       |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    | Proportion |                 |    %            |    | Organic N  |
|      of Organic |                 |                 |      originates |
|      Nitrogen   |                 |                 |    | from fecal |
|      to Total   |                 |                 |      nitrogen   |
|    | Nitrogen   |                 |                 |      so the     |
|                 |                 |                 |      initial    |
|                 |                 |                 |                 |
|                 |                 |                 |     composition |
|                 |                 |                 |      can be     |
|                 |                 |                 |      found from |
|                 |                 |                 |      fecal      |
|                 |                 |                 |      N/total    |
|                 |                 |                 |      manure N   |
+-----------------+-----------------+-----------------+-----------------+
|    | Proportion |                 |    %            |    | Organic N  |
|      of         |                 |                 |      +          |
|      Inorganic  |                 |                 |      Inorganic  |
|      Nitrogen   |                 |                 |      N = total  |
|      to Total   |                 |                 |      N          |
|    | Nitrogen   |                 |                 |    | Inorganic  |
|                 |                 |                 |      N          |
|                 |                 |                 |      originates |
|                 |                 |                 |      from       |
|                 |                 |                 |      urinary N  |
+-----------------+-----------------+-----------------+-----------------+
|    Total        |    TAN          |    kg           |    this is a    |
|    Ammoniacal   |                 |                 |    subset of    |
|    Nitrogen     |                 |                 |    Inorganic N  |
+-----------------+-----------------+-----------------+-----------------+
|    Proportion   |                 |    %            |                 |
|    of Nitrate   |                 |                 |                 |
|    to Total     |                 |                 |                 |
|    Mass         |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Water        |    WIP(t)       |    kg           |                 |
|    Inorganic    |                 |                 |                 |
|    Phosphorus   |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Water        |    WOT(t)       |    kg           |                 |
|    Organic      |                 |                 |                 |
|    Phosphorus   |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Non-water    |    NWIP(t)      |    kg           |                 |
|    Inorganic    |                 |                 |                 |
|    Phosphorus   |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Non-water    |    NWoP(t)      |    kg           |                 |
|    Organic      |                 |                 |                 |
|    Phosphorus   |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Phosphorus   |    P            |    kg           |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Potassium    |    K            |    kg           |                 |
+-----------------+-----------------+-----------------+-----------------+

**Section 1. Methane Emissions**

The model developed by Sommer et al. (2004) and Chianese et al. (2009)
aims to simulate the production and emission of methane (CH4) from barn
floor and manure storage facilities. The equations focus on the
degradation of volatile solids (VS) present in the manure, considering
factors like temperature and storage time to estimate methane emissions
from these storage systems.

4

In the following 2 sub-sections, we model methane emissions from the
Barn floor and from the outdoor storage respectively.

   **A.Methane Emissions Calculations – Barn floor**

Manure on housing facility floors (free stall and tie stall) is a small
source of CH4 emissions. Those methane emissions have been measured from
barn floors. Chianese et al., 2009 used such data to infer a simple
relationship between CH4 emissions and ambient temperature in the barn.
This relationship predicts reasonable emission rates for ambient
temperatures greater than 0°C and is the best currently available method
to calculate CH4 emissions from free stall and tie stall barn floors.
When temperature are below 0°C, there are no methane emissions.

Before calculating methane emissions let us determine the surface area
of the barn that is covered with manure. Methane emissions are an
increasing function of the area of the spread.

Here, we assume that exposed manure surface areas are constant across
animal types. The soiled areas assigned to tie stall and free stall
facilities are 1.2 m2 per cow in tie stall, 3.5 m2 per cow in free
stall, 1.0 m2 per growing cow in tie stall, and 2.5 m2 per growing cow
in free stall. These areas are fixed for the duration of a simulation.
Let 𝐴𝑚𝑎𝑛𝑢𝑟𝑒 be the total barn area soiled with manure in m2 such that:

𝐴𝑚𝑎𝑛𝑢𝑟𝑒 𝑏𝑎𝑟𝑛 = 1.2 × 𝑁𝑐𝑜𝑤,𝑡𝑖𝑒 + 3.5 × 𝑁𝑐𝑜𝑤,𝑓𝑟𝑒𝑒 + 1 × 𝑁𝑔𝑟𝑜𝑤𝑖𝑛𝑔,𝑡𝑖𝑒 + 2.5
× 𝑁𝑔𝑟𝑜𝑤𝑖𝑛𝑔,𝑓𝑟𝑒𝑒 [**M.1.A.1**]

where,

   | 𝑁𝑐𝑜𝑤,𝑡𝑖𝑒is the number of cows in tie stall,
   | 𝑁𝑐𝑜𝑤,𝑓𝑟𝑒𝑒is the number of cows in free stall,
   | 𝑁𝑔𝑟𝑜𝑤𝑖𝑛𝑔,𝑡𝑖𝑒 is the number of growing animals in tie stall,
     𝑁𝑔𝑟𝑜𝑤𝑖𝑛𝑔,𝑓𝑟𝑒𝑒 is the number of growing animals in free stall.

   Let 𝐸𝑚𝑖𝑠𝐶𝐻4 𝐵𝑎𝑟𝑛 𝐹𝑙𝑜𝑜𝑟 be the methane emissions in kg/day from the
   barn floor such that:

𝐸𝑚𝑖𝑠𝐶𝐻4 𝐵𝑎𝑟𝑛 𝐹𝑙𝑜𝑜𝑟 = 𝑀𝑎𝑥 (0,0.13𝑇)×𝐴\ *𝑚𝑎𝑛𝑢𝑟𝑒*

   1000 𝑏𝑎𝑟𝑛 [**M.1.A.2**]

where,

   T is the temperature in oC,

   𝐴𝑚𝑎𝑛𝑢𝑟𝑒 𝑏𝑎𝑟𝑛 is barn surface area covered with manure in m2
   calculatedin [M.1.A.1].

   **B.Methane Emissions Calculations – Outdoor Storage**

We use an adaptation of Sommer et al. (2004) and Chianese et al. (2009)
to calculate daily emissions of methane, given the ambient barn
temperature, and a methane conversion factor for the manure management.
Below, all the parameters and values for the manure storage emissions
come from Sommer et al. (2004).

   Let 𝐸𝑚𝑖𝑠𝐶𝐻4 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑡𝑜𝑟𝑎𝑔𝑒 be the methane emissions in kg per day
   from the outdoor storage such that:

5

+-------------+-------------+-------------+-------------+-------------+
|    𝐸𝑚𝑖𝑠𝐶𝐻4  |    𝐸        |             |    )]       | [*          |
|    𝑂𝑢𝑡𝑑𝑜𝑜𝑟  |    24×𝑉𝑆\ * |   24×𝑉𝑆\ *𝑛 |             | *M.1.B.1**] |
|    𝑆𝑡𝑜𝑟𝑎𝑔𝑒  | 𝑑*\ ×𝑏\ *1* | 𝑑*\ ×𝑏\ *2* |             |             |
|    = 𝑒𝑥𝑝    |             |    ) + (    |             |             |
|    (ln 𝐴 −  |    𝑅×𝑇) ×   |             |             |             |
|             |    [( 1000  | 1000        |             |             |
+=============+=============+=============+=============+=============+
+-------------+-------------+-------------+-------------+-------------+

| where,
| A is the Arrhenius parameter, indicating the methane production rate
  (g CH4 kg-1 VS h-1), with ln(A) = 43.33 g CH4 kg‐1 VS h‐1,
| E is the Apparent activation energy, in joules per mol (J mol-1), set
  at E = 112,700 J mol‐1, R is a gas constant in of joules per kelvin
  per mol (J K-1 mol-1), set at 8.314 J K‐1 mol‐1, T is the temperature
  in kelvin K,
| 𝑉𝑆𝑑and 𝑉𝑆𝑛𝑑 are the degradable and non-degradable volatile solids in
  the manure, in g, 𝑏1and 𝑏2are unitless correcting factors set at 𝑏1 =
  1 and 𝑏2 = 0.01.

   **C.The Daily Dry Matter Available, Daily Dry Matter Loss, and Manure
   mass update**

The daily dry matter loss is simply what is lost from the volatile
solids in the dry matter from methane emissions. Using the estimated
emissions of methane in kg per day from the barn floor manure and the
outdoor manure storage in [M.1.A.2] and [M.1.B.1] respectively, we can
then derive the dry matter loss in kg per day. Let DMloss Slurry
Outdoorbe the dry matter loss in kg per day such that:

   DMloss Slurry Outdoor = 𝐸𝑚𝑖𝑠𝐶𝐻4 𝐵𝑎𝑟𝑛 𝐹𝑙𝑜𝑜𝑟 + 𝐸𝑚𝑖𝑠𝐶𝐻4 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑡𝑜𝑟𝑎𝑔𝑒
   **[M.1.C.1]**

**Numerical Example of Accounting for Dry Matter loss via Methane
Emissions within a time step.** Here, using arbitrary numerical values,
we estimate the dry matter loss in kg from the barn floor and outdoor
manure storage through methane emissions.

**Step 1: Calculate the methane loss from barn floor and outdoor storage
using [M.1.A.2] and [M.1.B.1]**

Let’s consider a free stall barn with one cow on a day where ambient
temperature T = 15 °C.

𝑁𝑐𝑜𝑤,𝑡𝑖𝑒 = 𝑁𝑔𝑟𝑜𝑤𝑖𝑛𝑔,𝑡𝑖𝑒 = 𝑁𝑔𝑟𝑜𝑤𝑖𝑛𝑔,𝑓𝑟𝑒𝑒 0, and 𝑁𝑐𝑜𝑤,𝑓𝑟𝑒𝑒 = 1

+-----------------+-----------------+-----------------+-----------------+
| Using           |                 |    = 3.5        |                 |
| [M.1.A.1], we   |                 |    m2\ **,**    |                 |
| know 𝐴𝑚𝑎𝑛𝑢𝑟𝑒    |                 |    plugging     |                 |
|                 |                 |    this into    |                 |
|                 |                 |    [M.1.A.2]    |                 |
|                 |                 |    yields:      |                 |
+=================+=================+=================+=================+
|    𝐸𝑖 𝐵𝑎𝑟𝑛      | (0.13×15)×3.5   |                 |    = 68         |
|    𝐹𝑙𝑜𝑜𝑟        |                 |                 |    0−3𝑘𝑔𝑑𝑦−1    |
+-----------------+-----------------+-----------------+-----------------+
| 𝐸𝑖 𝐶𝐻4          | 1000            |                 |    = 68 0𝑘𝑔𝑑𝑦   |
+-----------------+-----------------+-----------------+-----------------+

Let the initial volatile solids be 𝑉𝑆𝑑 = 950 g and total solids mass be
𝑉𝑆𝑛𝑑 = 70 g:

𝑉𝑆𝑡𝑜𝑡𝑎𝑙 = 𝑉𝑆𝑑 + 𝑉𝑆𝑛𝑑 = 1020 g

6

| If Total Solids is such that TS = 12 kg
| (Note: 𝑉𝑆𝑑, 𝑉𝑆𝑛𝑑from the animal module are in kg, so we convert them
  to grams for the follow equation)

𝐸𝑚𝑖𝑠𝐶𝐻4 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑡𝑜𝑟𝑎𝑔𝑒 = 𝑒𝑥𝑝 (ln(43.33) −

+-----------------------------------------------------------------------+
|    112,700 24×950×1 24×70×0.01                                        |
|                                                                       |
|    8.314×15) × [( 1000 ) + (                                          |
|                                                                       |
|    | 1000                                                             |
|    | )] = 0.56 𝑘𝑔. 𝑑𝑎𝑦−1                                              |
+=======================================================================+
+-----------------------------------------------------------------------+

| **Step 2: Calculate the updated Volatile Solids**
| The new VS remaining = Initial VS – Methane loss:

𝑉𝑆𝑡+1 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 = 𝑉𝑆𝑡 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 − (𝐸𝑚𝑖𝑠𝐶𝐻4 𝐵𝑎𝑟𝑛 𝑓𝑙𝑜𝑜𝑟) 𝑡−
(𝐸𝑚𝑖𝑠𝐶𝐻4 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑡𝑜𝑟𝑎𝑔𝑒) 𝑡

   | = (950 + 70)
   | 1000

   − 7 × 10−3 − 0.56 = 9.63 𝑘𝑔

**Step 3: Calculate the updated Total Solids**

The updated Total solids = Initial Total Solids – Methane loss. With a
mass 12 kg of initial total solids, let

𝑇𝑆𝑡+1 𝑠𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 be the updated TS in kg in the next period such
that:

   𝑇𝑆𝑡+1 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 = 𝑇𝑆𝑡 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 − (𝐸𝑚𝑖𝑠𝐶𝐻4 𝐵𝑎𝑟𝑛 𝑓𝑙𝑜𝑜𝑟) 𝑡−
   (𝐸𝑚𝑖𝑠𝐶𝐻4 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑡𝑜𝑟𝑎𝑔𝑒)

𝑡

= 12 – 7 × 10−3 − 0.56

= 11.43 𝑘𝑔

**Manure mass:**

Every day, the outdoor manure in storage loses dry matter. This loss is
estimated and subtracted from the

initial total manure mass to generate a new total for the next period.

Assume the initial total slurry manure in outdoor storage is 100 kg, 12
kg of which is in total solids.

Additionally, suppose the daily dry matter loss is 0.57 kg. We can
update the total manure mass using the

following equation:

   𝑇𝑆𝑡+1 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 = 𝑇𝑆𝑡 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 − (𝐷𝑀𝑙𝑜𝑠𝑠 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡

Plugging in the numerical value in this example yields:

   𝑇𝑆𝑡+1 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 = 12 − 0.57 = 11.43 kg

Since the proportion of total solids in the manure is 12 %, let the
updated manure mass 𝑀𝑡+1 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟be

such that:

7

+-----------------------------------+-----------------------------------+
|    𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑀𝑡+1 𝑆𝑙𝑢𝑟𝑟𝑦     |    = 95.25 𝑘𝑔                     |
|    𝑂𝑢𝑡𝑑𝑜𝑜𝑟 = 𝑇𝑆𝑡+1 0.12           |                                   |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

Therefore, the updated outdoor manure mass after losing 0.567 kg of
total solids is 95.25 kg.

**Section 2. Accounting for Phosphorus (P) and Potassium (K) contents in
the Outdoor Storage**

Cows continuously produce manure containing phosphorus (P) and potassium
(K). Hence, P and K get added daily to the outdoor slurry manure
storage. In subsection A and B below, we account for those changes in P
and K mass.

   **A. Phosphorous Content in the Outdoor Manure Storage**

P gets added daily to the manure storage. P is further divided into 4
pools, each corresponding to 4 distinct forms of P: 1) water extractable
inorganic (WIP), 2) water extractable organic (WOP), 3) non-water
extractable inorganic (NWIP), 4) non-water extractable organic (NWOP).
We will then calculate daily changes in total P and in each of its
sub-pools.

Let 𝑃𝑡+1 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟be the total mass of P in the outdoor manure
storage at time 𝑡 + 1 , in kg. The general equation, for all forms of P
is such that:

𝑃𝑡+1 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 = 𝑃𝑡 Slurry Outdoor + 𝑃𝑡 𝑏𝑒𝑑𝑑𝑖𝑛𝑔 + 𝑃𝑡 𝑎𝑛𝑖𝑚𝑎𝑙 − 𝑃𝑡
𝑙𝑜𝑠𝑠

   where,

+-----------------------------------+-----------------------------------+
| in kg.                            |    𝑃𝑡 Slurry Outdoor is the total |
|                                   |    accumulated P in the previous  |
|                                   |    period 𝑡, in kg.               |
|                                   |                                   |
|                                   | 𝑃𝑡 𝑏𝑒𝑑𝑑𝑖𝑛𝑔 is the mass of P       |
|                                   | present in the bedding material   |
|                                   | added in the previous period 𝑡,   |
|                                   | in kg.                            |
|                                   |                                   |
|                                   | 𝑃𝑡 𝑎𝑛𝑖𝑚𝑎𝑙 is the mass of P        |
|                                   | present in the manure execrated   |
|                                   | by the animal in the previous     |
|                                   | period 𝑡,                         |
|                                   |                                   |
|                                   |    𝑃𝑡 𝑙𝑜𝑠𝑠is the mass of P loss   |
|                                   |    in the previous period 𝑡, in   |
|                                   |    kg.                            |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

In words, the updated mass of P in the outdoor manure storage at time 𝑡
+ 1 sums what was already accumulated at time 𝑡 with what was added in
the previous period 𝑡 (through P present in the added bedding material
and from the manure execrated by the animal). It then subtracts the
losses in P in the previous period 𝑡.

   For this version, we make 3 simplifying assumptions:

+-----------------------------------+-----------------------------------+
| i.                                | The mass of P in the bedding      |
|                                   | material is negligeable and set   |
| ii.                               | at 0, 𝑃𝑡 𝑏𝑒𝑑𝑑𝑖𝑛𝑔 = 0 ∀𝑡.          |
|                                   |                                   |
| iii.                              |    The masses of different forms  |
|                                   |    of P will be received from the |
|                                   |    animal module.                 |
|                                   |                                   |
|                                   |    There are no losses in P       |
|                                   |    within the manure storage 𝑃𝑡+1 |
|                                   |    𝑙𝑜𝑠𝑠 = 0 ∀𝑡.                   |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

Under such assumptions, the equations for updating the mass all 4 forms
of phosphorus (P) contained in outdoor manure storage can be expressed
as follows:

8

   𝑃𝑡+1 Slurry Outdoor,𝑝𝑜𝑜𝑙 = 𝑃𝑡 Slurry Outdoor,𝑝𝑜𝑜𝑙 + 𝑃𝑡 𝑎𝑛𝑖𝑚𝑎𝑙,𝑝𝑜𝑜𝑙
   **[M.2.A.1]**

where,

   𝑝𝑜𝑜𝑙 ∈ {𝑃, 𝑊𝐼𝑃, 𝑊𝑂𝑃, 𝑁𝑊𝐼𝑃, 𝑁𝑊𝑂𝑃}

+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
| and | the | c   |     |     |     |     |     |     | for | e   |     |
|     |     | orr |  re |     |     |   p |     | Slu |     | ach |   𝑝 |
|     |     | esp | lat |     |     | rop |     | rry |     |     | 𝑜𝑜𝑙 |
|     |     | ond | ive |     |     | ort |     |     |     |     |     |
|     |     | ing |     |     |     | ion |     | Out |     |     |   ∈ |
|     |     |     |     |     |     |     |     | doo |     |     |     |
|     |     |     |     |     |     |     |     | r,𝑝 |     |     |     |
|     |     |     |     |     |     |     |     | 𝑜𝑜𝑙 |     |     |     |
|     |     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |  %𝑃 |     |     |     |
|     |     |     |     |     |     |     |     | 𝑡+1 |     |     |     |
+=====+=====+=====+=====+=====+=====+=====+=====+=====+=====+=====+=====+
| {𝑃, |     |     |     |     |     |     |     |     |     |     |     |
| 𝑊   |     |     |     |     |     |     |     |     |     |   * |     |
| 𝐼𝑃, |     |     |     |     |     |     |     |     |     | *[M |     |
| 𝑊   |     |     |     |     |     |     |     |     |     | .2. |     |
| 𝑂𝑃, |     |     |     |     |     |     |     |     |     | A.2 |     |
| 𝑁𝑊  |     |     |     |     |     |     |     |     |     | ]** |     |
| 𝐼𝑃, |     |     |     |     |     |     |     |     |     |     |     |
| 𝑁𝑊  |     |     |     |     |     |     |     |     |     |     |     |
| 𝑂𝑃} |     |     |     |     |     |     |     |     |     |     |     |
| be  |     |     |     |     |     |     |     |     |     |     |     |
| com |     |     |     |     |     |     |     |     |     |     |     |
| es: |     |     |     |     |     |     |     |     |     |     |     |
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
| %𝑃  |     |     |     |     |     |     |     |     |     |     |     |
| 𝑡+1 |     |     |     |     |  |  |     |     |     |     |     |     |
| Slu |     |     |     |     | Slu |     |     |     |     |     |     |
| rry |     |     |     |     | rry |     |     |     |     |     |     |
| Out |     |     |     |     |     |     |     |     |     |     |     |
| doo |     |     |     |     |     |     |     |     |     |     |     |
| r,𝑝 |     |     |     |     | Out |     |     |     |     |     |     |
| 𝑜𝑜𝑙 |     |     |     |     | doo |     |     |     |     |     |     |
| =   |     |     |     |     | r,𝑝 |     |     |     |     |     |     |
|     |     |     |     |     | 𝑜𝑜𝑙 |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     | | 𝑃 |     |     |     |     |     |     |
|     |     |     |     |     | 𝑡+1 |     |     |     |     |     |     |
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|     |     |     |     | ∑   | 𝑝   |     |     |     |     |     |     |
|     |     |     |     |     | 𝑜𝑜𝑙 |     |  |  |     |     |     |     |
|     |     |     |     |     |     |     | Slu |     |     |     |     |
|     |     |     |     |     |     |     | rry |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     | Out |     |     |     |     |
|     |     |     |     |     |     |     | doo |     |     |     |     |
|     |     |     |     |     |     |     | r,𝑝 |     |     |     |     |
|     |     |     |     |     |     |     | 𝑜𝑜𝑙 |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     | | 𝑃 |     |     |     |     |
|     |     |     |     |     |     |     | 𝑡+1 |     |     |     |     |
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+

..

   **B.Potassium Content in the Outdoor Manure Storage**

Potassium K gets added continuously to the outdoor manure storage
through cows ‘manure production.

   Let 𝐾𝑡+1 Slurry Outdoorbe the total mass of K in the outdoor manure
   storage at time 𝑡 + 1 such that:

𝐾𝑡+1 Slurry Outdoor = 𝐾𝑡 Slurry Outdoor + 𝐾𝑡 𝑏𝑒𝑑𝑑𝑖𝑛𝑔 + 𝐾𝑡 𝑎𝑛𝑖𝑚𝑎𝑙 − 𝐾𝑡
𝑙𝑜𝑠𝑠

   Here, we make 2 simplifying assumptions:

   i. The mass of K in the bedding material is negligeable and set at 0,
   𝐾𝑡 𝑏𝑒𝑑𝑑𝑖𝑛𝑔 = 0 ∀𝑡.

   ii. There are no losses in K within the outdoor manure storage 𝐾𝑡
   𝑙𝑜𝑠𝑠 = 0 ∀𝑡

   𝐾𝑡+1 Slurry Outdoor = 𝐾𝑡 Slurry Outdoor + 𝐾𝑡 𝑏𝑒𝑑𝑑𝑖𝑛𝑔 + 𝐾𝑡 𝑎𝑛𝑖𝑚𝑎𝑙 − 𝐾𝑡
   𝑙𝑜𝑠𝑠\ **[M.2.B.1]**

**Section 3. Ammonia Emissions**

Ammonia loss from manure can be predicted using a relationship for NH3
volatilized from the surface of an aqueous solution containing ammonium
where the NH3 is transported to the free atmosphere through a pathway
with a finite resistance. Assuming a very low (zero) concentration of
NH3 in the free atmosphere, volatile loss can be determined using (Rotz
and Oenema, 2006).

Note that the same equation is applicable for barn and storage
emissions, the only difference is that the mass of the manure solution
on the floor (M) includes the mass of urine for barn emissions and
manure mass only for outdoor storage emissions.

   **A.Ammonia Emissions Calculations – Barn floor and Outdoor Storage**

9

The daily NH3−N emissions are determined assuming the exposed urine and
manure characteristics are relatively constant throughout each day.
Although manure is typically removed at intervals within a day, scraping
also tends to mix urine and feces and spread a thin surface layer that
remains on the floor surface.

**Barn emissions** –

Here, the exposed urine surface areas in free stall is assumed to be 3.5
m2 per cow. For growing animals, surface areas were 2.0 m2 for dairy
heifers under one year of age and 2.5 m2 for heifers over one year of
age.

The exposed urine surface area in tie stall barn is assumed to be 1.5 m2
per cow, which is twice the open gutter surface area behind each animal.

   Hence the area of exposed urine in the barn is such that:

𝐴𝑢𝑟𝑖𝑛𝑒 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦 = 1.5 × 𝑁𝑐𝑜𝑤,𝑡𝑖𝑒 + 3.5 × 𝑁𝑐𝑜𝑤,𝑓𝑟𝑒𝑒 + 2 ×
𝑁ℎ𝑒𝑖𝑓𝑒𝑟<1𝑦𝑒𝑎𝑟,𝑓𝑟𝑒𝑒 + 2.5 × 𝑁ℎ𝑒𝑖𝑓𝑒𝑟≥1𝑦𝑒𝑎𝑟,𝑓𝑟𝑒𝑒 [**M.3.A.1**]

where,

   | 𝑁𝑐𝑜𝑤,𝑡𝑖𝑒is the number of cows in tie stall,
   | 𝑁𝑐𝑜𝑤,𝑓𝑟𝑒𝑒is the number of cows in free stall,
   | 𝑁ℎ𝑒𝑖𝑓𝑒𝑟<1𝑦𝑒𝑎𝑟,𝑓𝑟𝑒𝑒 is the number of Heifer less than one year old
     in free stall, 𝑁ℎ𝑒𝑖𝑓𝑒𝑟≥1𝑦𝑒𝑎𝑟,𝑓𝑟𝑒𝑒 is the number of Heifer one year
     old and older in free stall.

Using the area of exposed urine in the barn area calculated above, let
𝑀𝑢𝑟𝑖𝑛𝑒 be the mass per square meter of the urine on the floor in kg.m-2
such that:

+-----------------------+-----------------------+-----------------------+
|                       | 𝑈𝑟𝑖𝑛𝑒                 | [**M.3.A.2**]         |
+=======================+=======================+=======================+
| 𝑀𝑢𝑟𝑖𝑛𝑒 =              | 𝑏𝑎𝑟𝑛                  |                       |
|                       | 𝐴𝑢𝑟𝑖𝑛𝑒                |                       |
+-----------------------+-----------------------+-----------------------+

where,

   Urine is the daily urine excreted by the housed animals in kg,

   𝐴𝑢𝑟𝑖𝑛𝑒 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦is the exposed urine surface area m2.

Lastly, let 𝑀𝑢𝑟𝑖𝑛𝑒 𝑇𝐴𝑁 be the urine TAN exposed surface area in kg.m-2
such that:

+-----------------------+-----------------------+-----------------------+
|                       | 𝑈𝑟𝑖𝑛𝑒 𝑇𝐴𝑁             | [**M.3.A.3**]         |
+=======================+=======================+=======================+
| 𝑀𝑢𝑟𝑖𝑛𝑒 𝑇𝐴𝑁 =          |    | 𝑏𝑎𝑟𝑛             |                       |
|                       |    | 𝐴𝑢𝑟𝑖𝑛𝑒           |                       |
+-----------------------+-----------------------+-----------------------+

where,

   Urine TAN is the daily urine TAN excreted by the housed animals in
   kg,

   𝐴𝑢𝑟𝑖𝑛𝑒 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦is the exposed urine surface area m2.

10

   **Storage emissions** – Here, the exposed manure surface areas in
   outdoor manure storage

+-----------------------+-----------------------+-----------------------+
| 𝐴𝑚𝑎𝑛𝑢𝑟𝑒 𝑂𝑢𝑡𝑑𝑜𝑜𝑟       |                       |                       |
| 𝑆𝑙𝑢𝑟𝑟𝑦in m2 is        |                       |                       |
| obtained from user    |                       |                       |
| input. Using the area |                       |                       |
| of exposed manure in  |                       |                       |
| the outdoor           |                       |                       |
|                       |                       |                       |
| manure storage, let   |                       |                       |
| 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 be the mass   |                       |                       |
| per square meter of   |                       |                       |
| the manure in kg.m2   |                       |                       |
| such that:            |                       |                       |
+=======================+=======================+=======================+
| =                     | 𝑀𝑎𝑛𝑢𝑟𝑒                | [**M.3.A.4**]         |
+-----------------------+-----------------------+-----------------------+
| 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 =             | 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦        |                       |
|                       | 𝐴𝑚𝑎𝑛𝑢𝑟𝑒               |                       |
+-----------------------+-----------------------+-----------------------+

| where,
| Manure is the daily manure excreted by the animals in kg,

   𝐴𝑚𝑎𝑛𝑢𝑟𝑒 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦is the exposed manure surface area m2.

Lastly, let 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 𝑇𝐴𝑁 be the manure TAN exposed surface area in kg.m-2
such that:

+-----------------------+-----------------------+-----------------------+
|                       | 𝑀𝑎𝑛𝑢𝑟𝑒 𝑇𝐴𝑁            | [**M.3.A.5**]         |
+=======================+=======================+=======================+
| 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 𝑇𝐴𝑁 =         | 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦        |                       |
|                       | 𝐴𝑚𝑎𝑛𝑢𝑟𝑒               |                       |
+-----------------------+-----------------------+-----------------------+

| where,
| Manure TAN is the daily manure TAN excreted by the housed animals in
  kg,

   𝐴𝑚𝑎𝑛𝑢𝑟𝑒 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦is the outdoor exposed manure surface area m2.

Before proceeding with NH3 loss calculations, we need to derive the
equilibrium coefficient 𝑄 for the NH3 gas in the air for a given
concentration of TAN in the solution using Henry’s law of distribution.

Since 𝑄 is a function of Henry’s law coefficient 𝐾ℎand a dissociation of
ammonium coefficient 𝐾𝑎𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛, we will compute those first. These two
coefficients are a function of temperature and pH such that:

+-----------------------+-----------------------+-----------------------+
|    | 1478             | **[M.3.A.6]**         |    **[M.3.A.7]**      |
|    | 𝐾ℎ = 10 × (      |                       |                       |
|      𝑇+273− 1.69)     |                       |                       |
+=======================+=======================+=======================+
|    0.09018+2729.9     |    − 𝑝𝐻)              |                       |
|    𝐾𝑎𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛= 1 + 10 |                       |                       |
|    × ( 𝑇+273          |                       |                       |
+-----------------------+-----------------------+-----------------------+

| where,
| Solution ∈ {𝑢𝑟𝑖𝑛𝑒, 𝑚𝑎𝑛𝑢𝑟𝑒},
| T is the ambient temperature in °C as a proxy for manure solution
  temperature1,
| pH is the pH of the solution set by default at 7.7 for urine/Barn and
  at 7.8 for manure /Outdoor Storage.

Using the coefficient derived above in [M.3.A.6] - [M.3.A.7], we can now
compute the unitless equilibrium coefficient 𝑄(𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛) as:

+-----------------------------------+-----------------------------------+
| 𝑄(𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛) = 𝐾ℎ × 𝐾𝑎𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛     | **[M.3.A.8]**                     |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

1Note that manure/barn temperature won’t be the same as ambient
temperature, this needs to be reviewed

11

| where,
| Solution ∈ {𝑢𝑟𝑖𝑛𝑒, 𝑚𝑎𝑛𝑢𝑟𝑒},
| 𝐾ℎ is the Henry’s law coefficient,
| 𝐾𝑎𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛 is the dissociation of ammonium coefficient for a given
  solution.

Next, we derive 𝑟 the resistance of NH3 transport from the urine surface
in the barn to the free atmosphere in s.m-1 such that:

| 𝑟𝑢𝑟𝑖𝑛𝑒 = 𝐻𝑆𝐶 × (1 − 0.027 × (20 − 𝑇)) **[M.3.A.9]** where,
| HSC is a housing-specific constant s.m-1 set at 260.

| For the manure in the outdoor storage, the resistance r of NH3
  transport from the manure surface to the free atmosphere in s.m-1 is
  such that:
| 𝑟𝑚𝑎𝑛𝑢𝑟𝑒 = 75 if the manure surface is covered with crust,
| 𝑟𝑚𝑎𝑛𝑢𝑟𝑒 = 19 if the manure surface is not covered with crust,
| 𝑟𝑚𝑎𝑛𝑢𝑟𝑒 = 10 if the manure is in a solid state.

Lastly, let 𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 be the NH3 loss during
enclosed animal housing in kg N.m-2.d-1, such that:

where,

+-----------------------------------+-----------------------------------+
| 𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦          |    | 𝑀 𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑇𝐴𝑁×𝑐×𝑦           |
| 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛) =               |    | 𝑟𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛                    |
|                                   |      ×𝑀𝑠𝑜𝑙                        |
|                                   | 𝑢𝑡𝑖𝑜𝑛×𝑄(𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛)\ **[M.3.A.10]** |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   | Solution ∈ {𝑢𝑟𝑖𝑛𝑒, 𝑚𝑎𝑛𝑢𝑟𝑒},
   | TAN is total ammoniacal N in the manure solution in kg N m-2,
   | c is the time conversion constant = 86400 s d-1,
   | y is manure and urine specific density, set to be 1000 kg.m-3,
   | 𝑟𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 is the resistance of NH3 transport in s.m-1 derived
     above,
   | 𝑀𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 is the solution mass per unit area of exposed surface in
     kg.m-2,
   | 𝑄(𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛) is the dimensionless equilibrium coefficient for the
     NH3 gas in the air for a given concentration of TAN in the solution
     computed in [M.3.A.8],

To get the total NH3 emissions, let us multiply 𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦
𝑂𝑢𝑡𝑑𝑜𝑜𝑟in kg N.m-2.d-1 by 𝐴𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦, the exposed surface
area of the solution ∈ {𝑢𝑟𝑖𝑛𝑒, 𝑚𝑎𝑛𝑢𝑟𝑒}, in m2:

12

   𝑇𝑂𝑇𝐴𝐿 𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛) =

**[M.3.A.11]**

   𝑀 𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑇𝐴𝑁 × 𝑐 × 𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦

   𝑟𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 × 𝑀𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 × 𝑄(𝑆𝑜𝑙𝑢𝑡𝑖𝑜𝑛) × 𝐴𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛

Using calculations of the daily loss of ammonia in 𝑘𝑔 𝑁. 𝑚−2above, the
updated manure and urine TAN

in kg.m-2.d-1 are such that:

   (𝑇𝐴𝑁𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡+1 = (𝑇𝐴𝑁𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 )𝑡 +
   (𝑀𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑇𝐴𝑁)𝑡 − (𝑁𝐻3 𝑉𝑜𝑙𝑎𝑡𝑖𝑠𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡

**[M.3.A.12]**

   (𝑇𝑂𝑇𝐴𝐿 𝑇𝐴𝑁𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡+1 = ((𝑇𝐴𝑁𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟
   )𝑡 + (𝑀𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑇𝐴𝑁)𝑡 −

(𝑁𝐻3 𝑉𝑜𝑙𝑎𝑡𝑖𝑠𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡) × 𝐴𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦
**[M.3.A.13]**

where,

   Solution ∈ {𝑢𝑟𝑖𝑛𝑒, 𝑚𝑎𝑛𝑢𝑟𝑒}.

**Numerical Example of Accounting for ammonia emissions within a time
step.**

Estimate the N loss in kg from the barn floor and manure storage through
ammonia.

**Step 1: Calculate the ammonia lost from barn floor using [M.3.A.1] -
[M.3.A.13]**

**Barn emissions** - The urine solution mass on the floor (M) was
determined as the daily urine excreted by

the housed animals divided by the exposed surface area (kg/m2).

𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑢𝑟𝑖𝑛𝑒) =

| 𝑀𝑢𝑟𝑖𝑛𝑒 𝑇𝐴𝑁×𝑐×𝑦
| 𝑟𝑢𝑟𝑖𝑛𝑒 ×𝑀𝑢𝑟𝑖𝑛𝑒×𝑄(𝑢𝑟𝑖𝑛𝑒)

If we have one cow in a free stall with Urine = 21 kg:

+-----------------------+-----------------------+-----------------------+
| the area 𝐴𝑢𝑟𝑖𝑛𝑒       |                       |                       |
| 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦 = 3.5  |                       |                       |
| m2,                   |                       |                       |
+=======================+=======================+=======================+
| 𝑀𝑢𝑟𝑖𝑛𝑒 =              |    | 𝑈𝑟𝑖𝑛𝑒            |    | 21               |
|                       |    | 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦=  |    | 3.5= 6 𝑘𝑔. 𝑚−2.  |
|                       |      𝐴𝑢𝑟𝑖𝑛𝑒           |                       |
+-----------------------+-----------------------+-----------------------+

If we set the urine TAN mass from the animal module at 0.21 kg,

+-----------------------+-----------------------+-----------------------+
| 𝑀𝑢𝑟𝑖𝑛𝑒 𝑇𝐴𝑁 =          |    | 𝑈𝑟𝑖𝑛𝑒 𝑇𝐴𝑁        |    | 0.21             |
|                       |    | 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦=  |    | 3.5= 0.06 𝑘𝑔.    |
|                       |      𝐴𝑢𝑟𝑖𝑛𝑒           |      𝑚−2.             |
+=======================+=======================+=======================+
+-----------------------+-----------------------+-----------------------+

With T = 15 °C **,** T = 288.2 K, andpH = 7.7, HSC =260 s.m-1, c = 86400
s.d-1 , and y = 1000 kg.m-3

+-----------------------------------+-----------------------------------+
| 𝐾ℎ = 10 × (                       |    | 1478                         |
|                                   |    | 15 + 273 − 1.69) = 2749.6    |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   𝐾𝑎𝑈𝑟𝑖𝑛𝑒= 1 + 10 × (0.09018 + 2729.9 15 + 273

13

   − 7.7) = 75

| 𝑄(𝑢𝑟𝑖𝑛𝑒) = 𝐾ℎ × 𝐾𝑎𝑢𝑟𝑖𝑛𝑒= 2749.6 × 75 = 203815
| 𝑟𝑢𝑟𝑖𝑛𝑒 = 𝐻𝑆𝐶 × (1 − 0.027 × (20 − 𝑇)) = 260 × (1 − 0.027 × (20 − 15))
  = 224.9 Finally, plugging in those values in:

𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑢𝑟𝑖𝑛𝑒) =

| 𝑀𝑢𝑟𝑖𝑛𝑒 𝑇𝐴𝑁 × 𝑐 × 𝑦
| 𝑟𝑢𝑟𝑖𝑛𝑒 × 𝑀𝑢𝑟𝑖𝑛𝑒 × 𝑄(𝑢𝑟𝑖𝑛𝑒)

= 0.06 × 86400 × 1000 [STRIKEOUT:224.9 × 6 × 203815] = 0.019 𝑘𝑔 𝑁. 𝑚−2.
𝑑−1

   𝑇𝑂𝑇𝐴𝐿 𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑢𝑟𝑖𝑛𝑒) = 𝑟𝑢𝑟𝑖𝑛𝑒 × 𝑀𝑢𝑟𝑖𝑛𝑒 ×
   𝑄(𝑢𝑟𝑖𝑛𝑒) × 𝐴𝑢𝑟𝑖𝑛𝑒 𝑀𝑢𝑟𝑖𝑛𝑒 𝑇𝐴𝑁 × 𝑐 × 𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦

   = 0.06 × 86400 × 1000 [STRIKEOUT:224.9 × 6 × 203815] × 3.5 = 0.066 𝑘𝑔
   𝑁. 𝑑−1

**Step 2: Cumulative loss and Remaining TAN** 𝑘𝑔 𝑁. 𝑚−2𝑑−1

Cumulative loss = Summation of ammonia lost each day 𝑘𝑔 𝑁. 𝑚−2𝑑−1

   = 0.019 𝑘𝑔 𝑁. 𝑚−2𝑑−1

Remaining Urine TAN daily = Initial TAN daily - Daily loss of ammonia 𝑘𝑔
𝑁. 𝑚−2

   (𝑇𝐴𝑁𝑢𝑟𝑖𝑛𝑒 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡+1 = (𝑇𝐴𝑁𝑢𝑟𝑖𝑛𝑒 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 )𝑡 + (𝑀𝑢𝑟𝑖𝑛𝑒
   𝑇𝐴𝑁)𝑡 − (𝑁𝐻3 𝑉𝑜𝑙𝑎𝑡𝑖𝑠𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡

   = 0 + 0.060 – 0.019

   = 0.041 𝑘𝑔 𝑁. 𝑚−2. 𝑑−1

Total remaining TAN **=** Remaining TAN \* Area of barn (kg N/cow)

   (𝑇𝑂𝑇𝐴𝐿 𝑇𝐴𝑁𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡+1

   | = ((𝑇𝐴𝑁𝑢𝑟𝑖𝑛𝑒 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 )𝑡 + (𝑀𝑢𝑟𝑖𝑛𝑒 𝑇𝐴𝑁)𝑡 − (𝑁𝐻3 𝑉𝑜𝑙𝑎𝑡𝑖𝑠𝑎𝑡𝑖𝑜𝑛
     𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟)𝑡) × 𝐴𝑢𝑟𝑖𝑛𝑒
   | 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦

   = 0.041 × 3.5 = 0.143 𝑘𝑔 𝑁. 𝑐𝑜𝑤−1

**Step 3: Calculate the ammonia lost from storage using [M.3.A.1] -
[M.3.A.13]**

**Storage emissions** - The manure mass (M) in the outdoor storage was
determined as the daily manure

mass divided by the exposed surface area (kg/m2).

𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑚𝑎𝑛𝑢𝑟𝑒) =

| 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 𝑇𝐴𝑁×𝑐×𝑦
| 𝑟𝑚𝑎𝑛𝑢𝑟𝑒 ×𝑀𝑚𝑎𝑛𝑢𝑟𝑒×𝑄(𝑚𝑎𝑛𝑢𝑟𝑒)

   14

   𝑇𝑂𝑇𝐴𝐿 𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑚𝑎𝑛𝑢𝑟𝑒) =

   𝑀𝑚𝑎𝑛𝑢𝑟𝑒 𝑇𝐴𝑁 × 𝑐 × 𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦

   𝑟𝑚𝑎𝑛𝑢𝑟𝑒 × 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 × 𝑄(𝑚𝑎𝑛𝑢𝑟𝑒) × 𝐴𝑚𝑎𝑛𝑢𝑟𝑒

The TAN in storage on a given day was the accumulated TAN removed from
the housing facility plus a portion of the organic N entering storage.
The TAN entering storage each day was the urinary N excreted minus the
TAN lost in the housing facility.

Since Urine TAN Is also mixed with manure before entering storage, so we
consider the following.

If we set the manure TAN mass from the animal module at 0.23 kg,

+-----------+-----------+-----------+-----------+-----------+-----------+
| Urine     |           |           |           |           |           |
| Total     |           |           |           |           |           |
| remaining |           |           |           |           |           |
| (𝑇𝑂𝑇𝐴𝐿    |           |           |           |           |           |
| 𝑇𝐴        |           |           |           |           |           |
| 𝑁𝑠𝑜𝑙𝑢𝑡𝑖𝑜𝑛 |           |           |           |           |           |
| 𝑆𝑙𝑢𝑟𝑟𝑦    |           |           |           |           |           |
| 𝑂𝑢        |           |           |           |           |           |
| 𝑡𝑑𝑜𝑜𝑟)𝑡+1 |           |           |           |           |           |
| = 0.143   |           |           |           |           |           |
| kg N      |           |           |           |           |           |
| (from     |           |           |           |           |           |
| Step 2    |           |           |           |           |           |
| above)    |           |           |           |           |           |
+===========+===========+===========+===========+===========+===========+
| 𝑀𝑚𝑎𝑛𝑢𝑟𝑒   |           |           |           | 0.23 +    |    =      |
| 𝑇𝐴𝑁 =     |           |  | 𝑚𝑎𝑛𝑢𝑟𝑒 |           | 0.143     |    0.0019 |
|           |           |      𝑇𝐴𝑁  |           |           |    𝑘𝑔.    |
|           |           |           |           |           |    𝑚−2.   |
|           |           | | 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 |           |           |           |
|           |           |           |           |           |           |
|           |           |   𝑆𝑙𝑢𝑟𝑟𝑦= |           |           |           |
|           |           |           |           |           |           |
|           |           |    𝐴𝑢𝑟𝑖𝑛𝑒 |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |           |           |           | 200       |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
| If we     |           |           |           |           |           |
| have one  |           |           |           |           |           |
| cow in a  |           |           |           |           |           |
| free      |           |           |           |           |           |
| stall     |           |           |           |           |           |
| with      |           |           |           |           |           |
| Manure =  |           |           |           |           |           |
| 75 kg:    |           |           |           |           |           |
| the area  |           |           |           |           |           |
| 𝐴𝑢𝑟𝑖𝑛𝑒    |           |           |           |           |           |
| 𝑂𝑢𝑡𝑑𝑜𝑜𝑟   |           |           |           |           |           |
| 𝑆𝑙𝑢𝑟𝑟𝑦 =  |           |           |           |           |           |
| 200 m2,   |           |           |           |           |           |
| (Set      |           |           |           |           |           |
| Model     |           |           |           |           |           |
|           |           |           |           |           |           |
| User )    |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
| 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 = |           |           |    | 75   |           |           |
|           |  | 𝑀𝑎𝑛𝑢𝑟𝑒 |           |    | 200= |           |           |
|           |           |           |           |           |           |
|           | | 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 |           |     0.375 |           |           |
|           |           |           |      𝑘𝑔.  |           |           |
|           |   𝑆𝑙𝑢𝑟𝑟𝑦= |           |      𝑚−2. |           |           |
|           |           |           |           |           |           |
|           |    𝐴𝑢𝑟𝑖𝑛𝑒 |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+

| For the manure mass, the daily dry matter loss should be subtracted
  from the total manure. (Methane emissions from storage, Step 3 – Daily
  TS loss kg)
| M = 75 / 200
| M = 0.375 kg/m2
| T = 15 °C
| T = 288.2 K
| pH = 7.5
| HSC =260 s/m
| c = 86400 s/d
| ρ = 1000 kg/m3

| By solving above, we get
| Kh = 2766.6

15

| Kasolution = 75
| Q = 207384.6
| HSC = housing specific constant (260 s/m)
| r storage = 75 (manure with crust)
| r storage = 19 (manure without crust)
| r storage = 10 (solid manure)
| Use, r = 75 for this calculation (manure with crust)
| **Step 3: Cumulative losses**
| Cumulative loss = Summation of ammonia storage each day

𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑚𝑎𝑛𝑢𝑟𝑒) =

| 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 𝑇𝐴𝑁 × 𝑐 × 𝑦
| 𝑟𝑚𝑎𝑛𝑢𝑟𝑒 × 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 × 𝑄(𝑚𝑎𝑛𝑢𝑟𝑒)

+-----------------------------------+-----------------------------------+
| =                                 |    | 0.0019 ×864000× 1000         |
|                                   |    | 75 × 0.375 × 207384.6 =      |
|                                   |      0.00029 𝑘𝑔 𝑁. 𝑚−2𝑑−1         |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   𝑇𝑂𝑇𝐴𝐿 𝑁𝐻3𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛 𝑆𝑙𝑢𝑟𝑟𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟(𝑚𝑎𝑛𝑢𝑟𝑒) =

   𝑀𝑚𝑎𝑛𝑢𝑟𝑒 𝑇𝐴𝑁 × 𝑐 × 𝑦 𝑂𝑢𝑡𝑑𝑜𝑜𝑟 𝑆𝑙𝑢𝑟𝑟𝑦

   𝑟𝑚𝑎𝑛𝑢𝑟𝑒 × 𝑀𝑚𝑎𝑛𝑢𝑟𝑒 × 𝑄(𝑚𝑎𝑛𝑢𝑟𝑒) × 𝐴𝑚𝑎𝑛𝑢𝑟𝑒

+-----------------------------------+-----------------------------------+
| =                                 |    | 0.0019 ×864000× 1000         |
|                                   |    | 75 × 0.375 × 207384.6× 200 = |
|                                   |      0.058𝑘𝑔 𝑁. 𝑑−1               |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

16

17

| **References**
| Chianese, D. S., C. A. Rotz, and T. L. Richard. "Simulation of methane
  emissions from dairy farms to assess greenhouse gas reduction
  strategies." *Transactions of the ASABE* 52.4 (2009): 1313-1323.

Rotz, C. A., & Oenema, J. (2006). Predicting management effects on
ammonia emissions from dairy and beef farms. Transactions of the ASABE,
49(4), 1139-1149.

18
