.. _Cow-requirements-pseudocode-NASEM :

===========================================================
**Dairy Cattle Ration NASEM 2021 (Lactation and Dry Cows)**
===========================================================

**# of Subroutine and Name:** Description of equations used to calculate
nutrient requirements of cows according to equations provided within
NASEM (2021)

Flow of Information:
====================

A. Nutrient requirements include energy, protein, minerals (Ca and P).

B. Energy supply, protein supply and mineral supply from feeds are calculated.

C. Supply >= this refers to the nutrients supplied by the diet to meet
   nutritional requirementsAll the equations are calculated on a
   daily basis

Arguments
---------

-  Animal inputs

   i.    BW: Body weight (kg)

   ii.   MW: Mature body weight (kg)

   iii.  CBW: Calf birth weight (kg)

   iv.   EQSBW: Equivalent shrunk body weight (kg)

   v.    GrUterW: Gravid uterine weight (kg)

   vi.   UterW: Uterine weight (kg)

   vii.  ADG: Average daily weight gain (g/d)

   viii. Frame_Weight_Gain_g: Frame weight gain refers to the accretion
         of both fat and protein in carcass (grams/d) per day)

   ix.   animal_type: Animal type according to set categories within
         RuFaS model: 'Calf', 'Heifer I II III, 'Cow'

   x.    Housing: Housing type (Barn or Grazing)

   xi.   Topography (Flat or Hilly)

   xii.  Distance: Estimated distance traveled by the animal daily (km/d)

   xiii. DOP: Days of pregnancy (d)

   xiv.  Parity: Number of parity (number)

   xv.   TP_Milk: Milk true protein content ( % of milk)

   xvi.  Fat_Milk: Milk fat content (% of milk)

   xvii. Lactose_Milk: Milk lactose content (% of milk)

   xviii. Milk: Milk production(kg/d)

   xix.  DIM: Days in milk (d)

   xx.   CI: Calving interval (d)

   xxi.  DMIest: Estimated dry matter intake according to empirical
         prediction equation (kg/d)

\*Note: Milk relative inputs are set to 0 for dry cows

-  Feed inputs (from the feed table, variables with \* are not used in any equations yet)

   i.       DM: Dry matter (% of as-fed basis)

   ii.      Water

   iii.     Type: Feed type (Forage, Concentrate, or Mineral. In
            addition, NASEM (2021) include the following categories:
            Dry Forage, Wet Forage, Pasture)

   iv.      Ash (% of DM)

   v.       OM: Organic matter (% of DM)

   vi.      ROM: Residual OM (% of DM)

   vii.     N: Nitrogen (% of DM)

   viii.    CP: Crude protein (% of DM)

   ix.      TP: True protein (% of DM)

   x.       MP: Metabolizable protein

   xi.      NPN: Non protein N

   xii.     CP equivalent to NPN

   xiii.    DM of NPN source

   xiv.     CPN_A: Fraction A of protein, soluble protein, degraded immediately in rumen (% of CP)

   xv.      CPN_B: Fraction B of protein, potentially degradable
            protein, require time to generally degrade in rumen (% of CP)

   xvi.     CPN_C: Fraction C of protein, not degradable in rumen (% of CP)

   xvii.    RDP: Ruminally degraded CP

   xviii.   RUP: Ruminally undegraded CP

   xix.     MICP: Microbial CP

   xx.      MN: Microbial N

   xxi.     MTP: Microbial TP

   xxii.    EndCP: Endogenous CP

   xxiii.   EndN: Endogenous N

   xxiv.    Starch (% of DM)

   xxv.     NDF: Neutral detergent fiber (% of DM)

   xxvi.    Forage NDF

   xxvii.   ADF: Acid detergent fiber (% of DM)

   xxviii.  Lignin (% of DM,)

   xxix.    FA: Fatty acids

   xxx.     GE: Gross energy (standard value, Mcal/kg)

   xxxi.    DE: Digestible energy (standard value, Mcal/kg)

   xxxii.   ME: Metabolizable energy (standard value, Mcal/kg)

   xxxiii.  NEL: Net energy for lactation (standard value, Mcal/kg)

   xxxiv.   NEM: Net energy for maintenance (standard value, Mcal/kg)

   xxxv.    NEG: Net energy for growth (standard value, Mcal/kg)

   xxxvi.   Ca: Calcium content (% of DM)

   xxxvii.  P: Phosphorus content (% of DM)

   xxxviii. Other minerals (Mg, K, Na, etc. are not considered yet)

   xxxix.   Cost: Feed cost ($/kg of DM)

-  Outputs

i. DMI: To be determined

Energy Requirements
===================

   Energy requirement is divided into 5 components: maintenance,
   activity, growth, pregnancy and lactation (all in net energy, Mcal
   per day).

Maintenance requirement
-----------------------

   Maintenance requirement is calculated based on metabolic body weight
   (body weight\ :sup:`0.75`).

+----------------------+-------------------------------------+-------------+
|    :math:`CBW =`     | input variable, otherwise CBW = MW  | [B.Cow.A.1] |
|                      | \* 0.06275                          |             |
+----------------------+-------------------------------------+-------------+

   CBW = Calf birth weight (kg) can be estimated using the equation
   above, otherwise there is an input variable depending on breed.
   Holstein = 42 kg; Jersey = 31 kg

   MW = Mature body weight (kg). Default values according to NASEM
   (2021) = 700 kg for Holstein; 520 kg for Jersey

+-------------------+----------------------------------------------------+-------------+
| :math:`GrUterW =` | (CBW \* 1.825) \*                                  | [B.Cow.A.2] |
|                   | :math:`exp^{- 0.0243 - (0.0000245*DOP)*(280-DOP)}` |             |
+-------------------+----------------------------------------------------+-------------+

+-----------+--------------------------------------------------------+--------------+
|  UterW =  | (CBW \* 0.2288) \* :math:`exp^{- 0.2*DayLact} + 0.204` | [B.Cow.A.3]  |
+-----------+--------------------------------------------------------+--------------+

..

   DOP= Days of pregnancy (this must be between 12 and 280 DOP)

   DayLact = Day of lactation

+-------------------+------------------------------------------+-------------+
| :math:`NEmaint =` | :math:`{0.10*(BW-GrUterW-UterW)}^{0.75}` | [B.Cow.A.4] | 
+-------------------+------------------------------------------+-------------+

..

   for normal activity in confinement conditions, otherwise include
   adjustments for activity requirements under grazing conditions.

   NEmaint = Net energy for maintenance requirement, Mcal

Activity requirement
--------------------

   Activity requirement (NEa) is proportional to body weight and daily
   walking distance. Grazing systems and hilly topography will cost
   additional energy. This is part of the energy requirements for
   maintenance, and it must be added to NEmaint when applied.

+--------+-------------------------------------------------------------+-------------+
| NEa1 = | (Dt_PastIn)/DtDMIn < 0.005; 0, otherwise if it is ≥ 0.005,  | [B.Cow.A.5] |
|        | then 0.0075 * :math:`{BW}^{0.75} * (600-12 * DtPastSupplIn)`|             |
|        | / 600                                                       |             |
+--------+-------------------------------------------------------------+-------------+

..

   DtPastIn = consumption of pasture DM, kg/d

   DtPastSupplIn = consumption of non pasture DM, kg/d

   NEa1 = Cost of locomotion for grazing activity on a flat surface,
   Mcal/d

   Additional energy requirements are also estimated

+-----------+-----------------------------------------------+-------------+
| NEa2  =   | :math:`0.00035(DistParlor)/1000*TripParlor*BW`| [B.Cow.A.6] |
+-----------+-----------------------------------------------+-------------+

..

   DistParlor = round trip distance from the barn or paddock to the
   parlor, m

   TripsParlor = number of trips to the parlor, n

   NEa2 = additional locomotion cost for walking to the parlor for a
   flat surface, Mcal/d

+--------+-------------------------------------+-------------+
| NEa3 = | :math:`0.0067*EnvTopoParlor/1000*BW`| [B.Cow.A.7] |
+--------+-------------------------------------+-------------+

..

   EnVTopoParlor = daily total climb while grazing and during transit
   between the milking parlor and the barn or paddock, m

   NEa3 = Energy cost associated with elevation change while grazing and
   in transit to and from milking, Mcal/d

+-------+------------------------------+-------------+
| NEa = | :math:`NEa1 + NEa2 + NEa3`   | [B.Cow.A.8] |
+-------+------------------------------+-------------+

..

   NEa = Total net energy for activity requirement, Mcal/d

   Activity requirements are proportional to body weight and daily
   walking distance. Grazing systems and hilly topography will cost
   additional energy.

Growth requirement (body frame gain)
------------------------------------

   In NASEM (2021), body frame gain (fat + protein) corresponds to the
   true growth and it is part of the calculation which is further
   partitioned to body reserves or condition gain (or loss), and
   pregnancy-associated gain (considered a pregnancy requirement).

   The value shown below was calculated, but was never utilized in any
   further calculations in the model’s current version. Thus, it has
   been omitted within the model and remains solely as a reference to
   past versions of the model.

+-----------------------+---------------------------------+-------------+
|    EBW =              | :math:`0.85*BW\ `               | [B.Cow.A.9] |
+-----------------------+---------------------------------+-------------+

..

   EBW = Empty body weight (without digesta), kg

+-----------------------+---------------------------------+--------------+
|    :math:`EBG\  =`    | :math:`0.85*ADG\ `              | [B.Cow.A.10] |
+-----------------------+---------------------------------+--------------+

..

   EBG = Empty body weight gain (without digesta), kg

   ADG = Average daily gain, kg/d

+----------+-------------------------------------------+--------------+
| FatADG = | (0.067 + 0.375 * (BW / MW)) * EBG / ADG   | [B.Cow.A.11] |
+----------+-------------------------------------------+--------------+

..

   FatADG = Fat constituent of average daily gain, g/g

+------------+-----------------------------------------+--------------+
|  ProtADG = | (0.201 + 0.081 * (BW / MW)) * EBG / ADG | [B.Cow.A.12] |
+------------+-----------------------------------------+--------------+

..

   FatADG = Protein constituent of average daily gain, g/g

+-------------------+----------------------------------+--------------+
|  :math:`REFADG =` | 9.4 * FatADG + 5.55 * ProtADG    | [B.Cow.A.13] |
+-------------------+----------------------------------+--------------+

..

   REFADG = Retained energy of frame ADG, Mcal/kg

+----------------------------------------------------+----------------+
|    :math:`MEFrameADG = REFADG/0.4`                 | [B.Cow.A.14]   |
+----------------------------------------------------+----------------+

..

   MEFrameADG = Metabolizable energy for frame ADG, Mcal/kg. The value
   0.4 is assumed to be the efficiency of converting feed ME to NE for
   gain (NEg).

+--------------------------------------------------------+--------------+
|    :math:`NElFrameADG = REFADG/0.61`                   | [B.Cow.A.15] |
+--------------------------------------------------------+--------------+

..

   NElFrameADG = Net energy for frame ADG, Mcal/kg. The efficiency of
   converting NEl to NEg is based on the conversions of 0.40 for ME to
   NEg and 0.66 for ME to NEl and is thus 0.40/0.66 = 0.61.

Pregnancy requirement
---------------------

   Daily rates of wet tissue deposition (kg/d) are derived from
   equations A.2 and A.3 as defined above.

   During gestation

    GrUterWGain = (0.0243 - (0.0000245 * DayGest)) * GrUterW  [B.Cow.A.16] 

   During involution

+----------------+-----------------------------------+--------------+
|  GrUterWGain = | –0.2 * DayLact * (UterW – 0.204)  | [B.Cow.A.17] | 
+----------------+-----------------------------------+--------------+

+-----------+---------------------------------------+--------------+
| NElPreg = | GrUterWGain * (0.882 / 0.14) * 0.66   | [B.Cow.A.18] |
+-----------+---------------------------------------+--------------+

..

   NElPreg = Net energy (lactation) requirement for pregnancy, Mcal/d.
   Assumptions: tissue contains 0.882 Mcal of energy / kg; an ME to
   gestation energy efficiency of 0.14; and ME to NEl efficiency of
   0.66.

   MEpreg = Metabolizable energy requirement for pregnancy, Mcal/day

Lactation requirement
---------------------

   :math:`MilkEn =` (0.0929 \* Fat_Milk + 0.0547 \* Prot_Milk + 0.0395
   \* Lact_Milk) [B.Cow.A.19]

   If true protein (TP_Milk) is measured, its energy content is adjusted
   up to account for the energy of Non-Protein-Nitrogen (NPN), then use
   the following equation.

   :math:`MilkEn =` (0.0929 \* Fat_Milk + 0.0585 \* TP_Milk + 0.0395 \*
   Lact_Milk) [B.Cow.A20]

   MilkEn = Milk energy, Mcal/kg of milk production

   Fat_Milk = Fat content in milk, %

   Prot_Milk = Crude protein content in milk, %

   TP_Milk = True protein content in milk, %

   Lact_Milk = Lactose content in milk, %

Protein requirements
====================

   Protein requirement is divided into 4 components: maintenance,
   growth, pregnancy and lactation (all in metabolizable protein (MP,
   g). The last is defined as the sum of rumen undegraded protein (RUP +
   microbial protein (MICP). Requirements for essential amino acids
   (EAA) are also included in NASEM (2021) but not yet implemented in
   the current version of RuFaS.

   Each physiological function is quantified in terms of TP (true
   protein), instead of CP (crude protein).

   To convert both net protein and net amino acids values to a
   metabolizable basis, net values have to be divided into the
   calculated efficiencies for each physiological function. Efficiencies
   can be either fixed or combined for lactating cows. For simplicity, I
   have included requirements only on a fixed basis.

Maintenance requirement
-----------------------

   The protein requirements for non-productive functions (the
   quantification of protein secretion and accretion), includes: scurf +
   endogenous urinary loss + metabolic fecal protein.

   Scurf

+----------------------+-------------------------------------+-------------+
| :math:`NP scurf =`   | :math:`0.20 * {BW}^{0.60} * 0.85`   | [B.Cow.B.1] |
+----------------------+-------------------------------------+-------------+
| :math:`NetAAscurf =` | :math:`NPscurf * [AACorrScurf]/100` | [B.Cow.B.2] |
+----------------------+-------------------------------------+-------------+

..

      NPscurf= Net protein requirement for scurf in grams per day

      BW = body weight in kg

      NetAAscurf = Net AA demand for scurf excretion in grams per day

      AACorrScurf = For each individual amino acid, a fixed value for each
      AA excreted as scurf is assumed according to column four in Table 6-2
      (page 79) in the NASEM (2021) book.

   Endogenous urinary excretion

+------------------------+---------------------------------------------------+-------------+
| :math:`NPEndUrin =`    |   :math:`53 * 6.25 * BW * 0.001`                  | [B.Cow.B.3] |
+------------------------+---------------------------------------------------+-------------+
| :math:`NetAAEndUrin =` | :math:`0.010 * 6.25 * BW * [AACorrWhEmpBody]/100` | [B.Cow.B.4] |
+------------------------+---------------------------------------------------+-------------+

..

   PEndUrin = Net protein requirement for endogenous urinary excretion

   NetAAEndUrin= Net amino acids requirement for endogenous urinary
   excretion

   AACorrWholeEmptyBody = For each individual amino acid, a fixed value
   for each AA excreted as a whole empty body is assumed according to
   column five in Table 6-2 (page 79) in the NASEM (2021) book.

   Metabolic fecal protein

   The daily loss of CP as metabolic fecal protein (MFP) is estimated
   using the following equation.

+---------------------+----------------------------------------+-------------+
|    :math:`CPMFP =`  |    :math:`(11.62 + 0.134\ *NDF)*\ DMI` | [B.Cow.B.5] |
+---------------------+----------------------------------------+-------------+

..

   CPMFP = Crude protein (CP) in metabolic fecal protein MFP in grams
   per day

   NDF = Neutral detergent fiber in the diet, as a % on dry matter basis

   DMI = Dry matter intake, kg/d

+---------------------+------------------------+--------------+
|    :math:`NPMFP =`  |    :math:`CPMFP * 073` | [B.Cow.B.6]  |
+---------------------+------------------------+--------------+

..

   NPMFP = Net protein requirement for metabolic fecal protein in grams
   per day. There is an assumption: 73 percent of true protein (TP) in
   MFP.

+---------------------+-------------------------------+-------------+
| :math:`NPAAMFP =`   | :math:`NPMFP*[AACorrMFP]/100` | [B.Cow.B.7] |
+---------------------+-------------------------------+-------------+

..

   NetAAMFP= Net amino acids requirement for metabolic fecal protein in
   grams per day

   AACorrMFP = aminoacids corrected for MFP. There is a fixed value for
   each individual amino acid in column six provided in the Table 6-2
   (page 79) of the NASEM (2021) book.

Growth requirement (frame growth)
---------------------------------

   There are two important concepts: frame growth and BW changes related
   to mobilization of body reserves. Following equations refer to the
   first item.

+---------------------+---------------------------------+--------------+
|  :math:`NPGrowth =` |    :math:`FrameWG*\ 0.11*0.86`  |  [B.Cow.B.8] |
+---------------------+---------------------------------+--------------+

NPGrowth= Net protein requirement for body frame weight gain in grams
per day.

   If the change in BW is not frame growth but rather a change in body
   reserves, the protein content is assumed to be 8.0 percent protein.
   In that case, the 0.11 coefficient should be replaced by 0.08 in the
   above equation.

+-----------------------+------------------------------------------------+-------------+
| :math:`NetAAGrowth =` | :math:`NPGrowth*\lbrack AACorrWEBW\rbrack/100` | [B.Cow.B.9] |
+-----------------------+------------------------------------------------+-------------+

..

   NetAAGrowth = Net amino acids requirement for body frame weight gain
   in grams per day.

   AACorrWEBW = For each individual amino acid, a fixed value for each
   AA excreted as a whole empty body is assumed according to column five
   in Table 6-2 (page 79) in the NASEM (2021) book.

Pregnancy requirement 
----------------------

+---------------------+------------------------------+-----------------+
|    :math:`NPGest =` |    :math:`GainGrUter*\ 125`  | [B.Cow.B.10]    |
+---------------------+------------------------------+-----------------+

..

   NPGest= Net protein requirement for pregnancy in grams per day.

   GainGrUter = daily gain in mass of the gravid uterus in kilograms per
   day.

   125 (coefficient) = Daily gain in mass of the gravid uterus is
   assumed to contain 125 g of protein per kilogram of wet weight.

+---------------------+------------------------------------------------+--------------+
| :math:`NetAAGest =` |   :math:`NPGest*\lbrack AACorrWEBW\rbrack/100` | [B.Cow.B.11] |
+---------------------+------------------------------------------------+--------------+

..

   NetAAGest = is the amino acids composition of protein accretion
   associated with pregnancy.

   AACorrWEBW = For each individual amino acid, a fixed value for each
   AA excreted as whole empty body composition is assumed to be the one
   provided in column five in Table 6-2 (page 79) in the NASEM (2021)
   book.

Lactation requirement
---------------------

NPMilk = net protein in milk. This refers to milk true protein (TP)
yield in grams per day.

+---------------------+------------------------------------------------+--------------+
| :math:`NetAAMilk =` |   :math:`NPMilk*\lbrack AAcalcMilk\rbrack/100` | [B.Cow.B.12] |
+---------------------+------------------------------------------------+--------------+

..

   NetAA-Milk = Net amino acids yield in milk in grams per day

   AAcalcMilk = Estimated AA composition of the true protein (TP)
   fraction involved in the estimation of AA Supply and recommendations.
   In this case, for milk production. Units are in grams of AA per 100
   grams of TP.

   Fixed values for each individual amino acid in milk are according to
   column seven in Table 6-2 (page 79) in the NASEM (2021) book.

Total requirement - Recommendations of metabolizable protein amino acids according to NASEM (2021)
--------------------------------------------------------------------------------------------------

For lactating cows

+--------------------------+------------------------------------------------+--------------+
| :math:`RecomMPSupply1 =` | :math:`(NPScurf + NPMFP + NPMilk + NPGrowth)   | [B.Cow.B.13] |
|                          | /TargetEffMP + (NPGest / 0.33) + NPEndUrin`    |              |
+--------------------------+------------------------------------------------+--------------+

+----------------------------+-----------------------------------------+--------------+
| :math:`RecomMPAASupply1 =` | :math:`[(NetAAScurf + NetAAMFP +        | [B.Cow.B.14] |
|                            | NetAAMilk + NetAAGrowth) / TargetEffAA] |              |
|                            | + (NetAAGest/0.33) + NetAAEndUrin`      |              |
+----------------------------+-----------------------------------------+--------------+

..

   For both late gestation cows and heifers

+--------------------------+-------------------------------------------+---------------+
| :math:`RecomMPSupply2 =` | :math:`[(NPScurf+NPMFP)/TargetEffMP]      |               | 
|                          | +(NPGest/0.33)+(NPGrowth/0.40)+NPEndUrin` | [B.Cow.B.15]  |
+--------------------------+-------------------------------------------+---------------+

+--------------------------+-------------------------------------------------+--------------+
| :math:`RecomMPSupply2 =` | :math:`[(NetAAScurf+NetAAMFP)/TargetEffAA]      |              |
|                          | +(NetAAGest/0.33)+(NetAAGrowth/0.40)+NPEndUrin` | [B.Cow.B.16] |
+--------------------------+-------------------------------------------------+--------------+

..

   TargetEffMP and TargetEffAA= Proposed target efficiencies of
   converting metabolizable protein (MP) and essential amino acids (EAA)
   to export proteins and body gain. See Table 6-4 on page 88 in the
   NASEM (2021) book.

Mineral requirements
====================

   Only calcium and phosphorus requirements are included in the code at
   present.

Calcium requirement
-------------------

Maintenance
~~~~~~~~~~~

+-----------------------+------------------+-------------+
| :math:`Ca_{main}\  =` | :math:`0.90*DMI` | [B.Cow.C.1] |
+-----------------------+------------------+-------------+
 
   *this equation applies to all metabolic stages*
..

   Ca_main = Calcium requirement for maintenance, g/day

   DMI = dry matter intake in kg/day

Growth
~~~~~~

+-----------------------+------------------------------------------+-------------+
| :math:`Ca_{growth} =` | :math:`9.83*MW^{- 0.22}*BW^{- 0.22}*ADG` | [B.Cow.C.2] |
+-----------------------+------------------------------------------+-------------+

..

   Ca_growth = Calcium requirement for growth, g/day

   MW = mature body weight in kg

   ADG = average daily gain in grams per day.

Pregnancy
~~~~~~~~~

+--------------------------+-----------------------------------------+-------------+
|    :math:`Ca_{preg}\  =` | :math:`0.02456*exp 0.05581-0.00007*DOP  | [B.Cow.C.3] |
|                          | * DOP -0.02456*exp (0.05581-0.00007*DOP |             |
|                          | - 1 * (DOP - 1))*(BW/715), if DOP>190;  |             |
|                          | 0, otherwise`                           |             |
+--------------------------+-----------------------------------------+-------------+

..

   Ca_preg = Calcium pregnancy requirement, g/day

   DOP = days of pregnancy

   BW = Body weight in kg

   715 is the average cow weight in the study by House and Bell (1993);
   therefore, pregnancy (gestation) requirement is scaled to that BW.
   For details see Page 107 in the Minerals chapter of NASEM (2021)
   book. IF DOP < 190; then it is assumed that Ca_Preg is equal to zero.

Lactation
~~~~~~~~~

+-----------------------+-------------------------------------+-------------+
| :math:`Ca_{lact} =`   | :math:`(0.295 + 0.239*MilkTP)*Milk` | [B.Cow.C.4] |
+-----------------------+-------------------------------------+-------------+

..

   Ca_lact = Calcium requirement for lactation, g/day

   MilkTP = Milk true protein, percent

   Milk = Milk yield, kg/day

   Total Calcium requirement

+-----------------------+------------------------------------+------------+
|    :math:`Ca_{req} =` | :math:`Ca_{main} + Ca_{growth}     | [B.Cow.C.5]|
|                       | + Ca_{preg} + Ca_{lact}`           |            |
+-----------------------+------------------------------------+------------+

..

   Ca_Req = Total calcium requirement, g/day

Phosphorus requirement
----------------------

Maintenance
~~~~~~~~~~~

+-----------------------+-----------------------------------+-------------+
|                       | :math:`1.0*DMI + 0.0              | [B.Cow.C.6] | 
|  :math:`P_{main}\  =` | 006*BW,\ for\ lactating\ cows;\ ` |             | 
+-----------------------+-----------------------------------+-------------+

..

   P_main = Phosphorus requirement for maintenance, g/day

   DMI = dry matter intake, kg/day

   BW = Body weight, kg

Growth
~~~~~~

+-----------------------+-------------------------------------+-------------+
|                       | :math:`\left( 1.2 + 4.635           | [B.Cow.C.7] |
|  :math:`P_{growth} =` | *MW^{0.22}*BW^{- 0.22} \right)*ADG` |             |
+-----------------------+-------------------------------------+-------------+

..

   P_growth = Phosphorus requirement for growth, g/day

   MW = mature body weight, kg

   BW = Body weight, kg

   ADG = average daily BW gain in grams per day.

Pregnancy 
~~~~~~~~~~

+---------------------+---------------------------------------+-------------+
|  :math:`P_{preg} =` | :math:`0.02743*exp((0.05527-0.00007)  | [B.Cow.C.8] |
|                     | * DOP)-0.02743*exp((0.05527-0.000075) |             |
|                     | *(DOP-1)) * (BW/715)*  (DOP - 1), if  |             |
|                     | DOP>190; 0, otherwise`                |             |
+---------------------+---------------------------------------+-------------+

..

   P_preg = Phosphorus requirement for pregnancy, g

   DOP = days of pregnancy

   BW = Body weight

   715 is the average cow weight in the study by House and Bell (1993);
   therefore, pregnancy (gestation) requirement is scaled to that BW.
   For details see Page 112 in the Minerals chapter of NASEM (2021)
   book. IF DOP < 190; then it is assumed that P_Preg is equal to zero.

Lactation 
~~~~~~~~~~

+-----------------------+-----------------------------------------------+-------------+
|    :math:`P_{lact} =` | :math:`Milk*(0.49 + 0.13*TPMilk); Milk*0.90`  | [B.Cow.C.9] |            
|                       | Otherwise when milk protein is unknown        |             |
+-----------------------+-----------------------------------------------+-------------+

..

   P_lact = Phosphorus requirement for lactation, g/d

   Milk = Milk yield, kg/day

   MilkTP = Milk true protein, percent

   Total Calcium requirement

+-----------------------+------------------------------------+--------------+
|    :math:`P_{req} =`  | :math:`P_{main} +                  | [B.Cow.C.10] |
|                       | P_{growth} + P_{preg} + P_{lact}`  |              |
+-----------------------+------------------------------------+--------------+

..

   P_Req = Total phosphorus requirement, g/day

Dry matter intake estimation
============================

   Dry matter intake estimation is different for lactating cows and dry
   cows. The sum of dry matter intake of each feed is assumed to be less
   than dry matter intake estimation

   (:math:`\sum_{i} Feed_{i} < DMIest`).

+------------------+--------------------------------------------------+-------------+
| :math:`DMIest =` | :math:`((3.7 +Parity*5.7)+0.305*MilkE+0.022*BW+  | [B.Cow.D.1] |
|                  | (-0.689 -1.87*Parity)*BCS) * (1-(0.212+          |             |
|                  | Parity*0.136*exp(-0.053*DIM) for lactating cows; |             |
|                  | \frac{(1.97-0.75*exp(0.16*(DOP - 280)))}{100}    |             |
|                  | * BW, for dry cows`                              |             |
+------------------+--------------------------------------------------+-------------+

..

   DMIest = Dry matter intake estimation, kg

   DIM = Days in milk

   MilkE = Milk energy, Mcal/d

   Parity = is an adjustment factor ranging from 0 (all primiparous) to
   1 (all multiparous)

   BCS = Body condition score scaled from 1 (thin) to 5 (obese)

   DOP = Days of pregnancy

Other requirements
==================

   1. Minimum dietary NDF content: 25%

   2. Maximum dietary NDF content: 40%

   3. Minimum dietary forage NDF content: 19%

   4. Maximum dietary fat content: 7%

Feed nutrient supply
====================

Energy supply
-------------

   Energy values are expressed in NEl units to fulfill the requirements
   for physiological functions.. Feed actual energy contents are
   corrected from standard values provided by NASEM (2021). Minerals do
   not provide any energy. There are substantial changes on how energy
   supply is estimated from feeds. For instance, the total digestible
   nutrients (TDN) is not used any longer.

   The Feed library has been expanded and updated within the NASEM
   (2021) system. This is still a pending task within RuFaS (to include
   the new feed library).

+---------------+----------------------------------------+-------------+
| :math:`ROM =` | :math:`100 - Ash - NDF - Starch -      | [B.Cow.F.1] |
|               | (FA/FatFactor) - (CP - 0.64*sNPNCPE)`  |             |               
+---------------+----------------------------------------+-------------+

..

   ROM = Diet residual organic matter concentration, % DM

   Ash = Diet ash content, % DM

   NDF = Diet Neutral detergent fiber content, % DM

   Starch = Diet starch content, % DM

   FA = Diet fatty acids, % DM

   Fat_Factor = Adjustment factor, it is equal to 1 if Feed type = fatty
   acid or FA soap and 1.06 for all other feeds, % DM

   sNPNCPE = The CP equivalent from supplemental non protein nitrogen
   (0.89 Mcal/kg)

   *Gross energy of a diet or feed*

+-----------------------+-------------------------------------------------+-------------+
| :math:`GE_{DMFeed} =` | :math:`0.042*NDF_{DM}+0.0423*Starch_{DM}+0.040  | [B.Cow.F.1] |
|                       | *ROM_{DM} 0.094*FA_{DM}+0.0565*(CP_{DM}+        |             |
|                       | sNPNCPE_{DM}+0.0089*NPNCPE_{DM})`               |             |               
+-----------------------+-------------------------------------------------+-------------+

..

   GE_DMFeed = Gross energy of a diet or feed, Mcal/kg

   NDF_DM = Diet neutral detergent fiber content, % DM

   Starch_DM = Diet starch content, % DM

   ROM_DM = Diet residual organic matter, % DM

   FA_DM = Diet fatty acids, % DM

   CP_DM = Diet crude protein, % DM (excluding supplemental NPN;
   non-protein N)

   sNPNCPE = The CP equivalent from supplemental non protein nitrogen
   (0.89 Mcal/kg)

   Equation coefficients for each chemical fraction (e.g.,value of
   0.0565 for CP_DM) refers to energy contents in Mcal per kilogram
   (CP_DM = 5.65 Mcal/kg).

   **Estimating the digestible energy value for feeds and diets**

   *True digestibility coefficients of feed fractions for base
   conditions*

   For the NASEM (2021) system, the base condition is for an animal with
   a 3.5 percent of BW and fed a diet with 26 percent starch. All diets
   are assumed to have adequate RDP to meet microbial requirements and
   adequate proper forage NDF to promote proper rumen conditions.

   Neutral detergent fiber

+-------------------------+-------------------------------------------------+-------------+
| :math:`dNDF_{NDFBase} =`| :math:`{0.75 *(NDF_{DM}-Lignin_{DM})*           | [B.Cow.F.3] |
|                         | [1-(Lignin_{DM}/NDF)^{0.667}]}/NDF_{DM}`        |             |
+-------------------------+-------------------------------------------------+-------------+
|                         | *Lignin based equation taken from NRC (2001)*   |             |
+-------------------------+-------------------------------------------------+-------------+
|                         | :math:`0.12+0.61*IVNDFD`                        |             |
+-------------------------+-------------------------------------------------+-------------+
|                         | *In vitro NDF digestibility based equation taken|             |
|                         | from Lopes et al., (2015)*                      |             |        
+-------------------------+-------------------------------------------------+-------------+

..

   dNDF_NDFBase = digested proportion of NDF at base conditions

   Lignin_DM = Lignin concentration, % DM

   NDF = Neutral detergent fiber, % DM

   IVNDFD = In vitro NDF digestibility

   Starch at base conditions (dStarch_StarchBase)

   Default value: 0.91; otherwise take tabulated values for selected
   feed from Table 3-1 (Page 25) in the NASEM (2021) book.

   Crude protein

   According to White et al. (2017), total tract digestibility of
   protein is less affected by intake than that for other nutrients.

+--------------------+----------------------------------------+--------------+
| :math:`dCP_{CP} =` | :math:`(RDP_{DM} + dRUP_{DM})/CP_{DM}` | [ B.Cow.F.4] |
+--------------------+----------------------------------------+--------------+

..

   dCP_CP = Proportion of digested CP

   RDP_DM = Rumen degradable protein, % DM

   dRUP = digested rumen undegradable protein, % DM

   Crude protein_DM = Crude protein, % DM

   Residual organic matter

   The true digestibility of ROM calculated with NDF was 0.96 and was
   set as the base digestibility (dROM_ROM_Base) in the model.

   Fatty acids

   The base digestibility of FAs is set at 0.73 for most feeds.
   Digestibility of FAs from different fat sources and supplements is
   discussed in Chapter 4 of the NASEM (2021) book.

   **Adjustments to the base digestibilities for intake and diet
   composition**

   Neutral detergent fiber - According to the modified equation of de
   Souza et al. (2018).

+---------------------+-----------------------------------------------+-------------+
| :math:`dNDF_{NDF} =`| :math:`dNDF_{NDFBase} - 0.0059*{(Starch}_{DM} | [B.Cow.F.5] |
|                     | - 26) - 1.1*(DMI_{BW} - 0.035)`               |             |   
+---------------------+-----------------------------------------------+-------------+

..

   dNDF_NDF = digested proportion of NDF

   dNDF_NDFBase = digested proportion of NDF at base conditions

   Starch_DM = starch concentration, % DM

   DMI_BW = DMI/BW, kg/kg

   0.035 = 3.5% of BW

   Starch

+----------------------------+-------------------------------------------------------+-------------+
| :math:`dStarch_{Starch} =` | :math:`dStarch_{StarchBase} - 1.0*(DMI_{BW} - 0.0035)`| [B.Cow.F.6] |
+----------------------------+-------------------------------------------------------+-------------+

..

   dStarch_Starch = digested proportion of starch

   dStarch_StarchBase = digested proportion of starch at base conditions

   Starch_DM = starch concentration, % DM

   DMI_BW = DMI/BW, kg/kg

   0.035 = 3.5% of BW

   **Estimating Endogenous Fecal Material and Apparent Digestibilities**

   Metabolic fecal crude protein

+--------------------+------------------------------------+-------------+
|  :math:`MFCP =`    |  :math:`11.62 + 0.134*NDF_{DMI}`   | [B.Cow.F.7] |
+--------------------+------------------------------------+-------------+

..

   MFCP = metabolic fecal CP, g/kg DMI

   NDF is a percentage of DM

+-----------------------+----------------------------------+-------------+
|    :math:`fMCP =`     | :math:`(MicCP*0.2)/DMI`          | [B.Cow.F.8] |
+-----------------------+----------------------------------+-------------+

..

   fMCP = fecal microbial CP, g/kg DMI

   MicCP = Microbial CP, g/d

+-----------------------+----------------------------------+-------------+
| :math:`adROM_{ROM} =` | :math:`[(ROM*0.96) - 3.43]/ROM`  | [B.Cow.F.9] |
+-----------------------+----------------------------------+-------------+

..

   adROM_ROM = apparently digested proportion of ROM

   ROM = Residual organic matter in kg/d

+-----------------------+-------------------------------------------+-------------+
| :math:`adCP_{CP} =`   | :math:`[(RDP + dRUP) - (fMCP + MFCP)]/CP` | [B.Cow.F.10]|
+-----------------------+-------------------------------------------+-------------+

..

   adCP_CP = apparently digested proportion of CP

   RDP = Rumen degradable crude protein, kg/d

   dRUP = digested rumen undegradable protein, kg/d

   fMCP = fecal microbial CP, kg/d

   MFCP = metabolic fecal CP, kg/d

   CP = crude protein, kg/d

+---------------------+--------------------------------------+-------------+
| :math:`adOM_{OM} =` | :math:`(NDF + dNDF_{NDF} + Star      | [B.Cow.F.11]|
|                     | ch*dStarch_{Starch} + FA*dFA_{FA}+RD |             |
|                     | P+dRUP+0.96*ROM-MFCP-fMCP-efROM)/OM` |             |
+---------------------+--------------------------------------+-------------+

  
..

   adOM_OM = apparently digested proportion of OM

   NDF = neutral detergent fiber, kg/d

   Starch = starch, kg/d

   dStarch_Starch = digested starch. kg/d

   FA = Fatty acids, kg/d

   dFA_FA = digested fatty acids, kg/d

   RDP = Rumen degradable crude protein, kg/d

   dRUP = digested rumen undegradable protein, kg/d

   ROM = Residual organic matter, kg/d

   fMCP = fecal microbial CP, kg/d

   MFCP = metabolic fecal CP, kg/d

   efROM = Revise!

   OM = organic matter, kg/d

   **Estimating the Digestible Energy of Feeds and Diets**

+-------------------+----------------------------------------------------+--------------+
| :math:`DE_{DM} =` | :math:`0.042*NDF_{DM}*dNDF_{NDF}+0.0423*Sta        | [B.Cow.F.12] |
|                   | rch_{DM}*dStarch_{Starch}+0.0940*FA_{DM}*dFA{FA}   |              |
|                   | +0.0565*(RDP_{DM}-sNPNCPE_{DM}+dRUP_{DM})+0.00899*s|              |
|                   | NPNCPE_{DM}+0.040*ROM{DM}*0.96-0.00565*MFCP-0.0056 |              |
|                   | 5*fMCP-0.0040*efROM_{DM}`                          |              |
+-------------------+----------------------------------------------------+--------------+

..

   DE_DM = digestible energy, Mcal/kg DM

   Feed fractions are given as a percentage of DM; endogenous fractions
   are g/kg; and digestibilities are expressed as proportions.

   **Estimating the Metabolizable Energy of Diets**

   To calculate ME supply, energy losses from both fermentation gasses
   and urine have to be discounted from the DE value of the diet.

   Gas energy loss

+---------------------+-----------------------------------+--------------+
| :math:`GasE_{DM} =` | :math:`(0.294*DMI - 0.347*FA_{DM} | [B.Cow.F.13] |
|                     | + 0.0409*dNDF_{DM})/DMI`          |              |
+---------------------+-----------------------------------+--------------+

..

   GasE_DM = gas energy loss, Mcal/kg DM

   DMI = dry matter intake, kg/d

   FA_DM = Fatty acids, % diet DM

   dNDF_DM = digested neutral detergent fiber, % diet DM

   Urinary energy loss is calculated from estimated urinary N excretion.

+------------+-------------------------------------------+--------------+
|:math:`UN =`| :math:`(DMI*CP_{DM}*adCP_{CP} - Milk_{CP} | [B.Cow.F.14] |
|            | - BodyGain_{CP})*1,000/6.25`              |              |
+------------+-------------------------------------------+--------------+

..

   UN = Urinary N excretion per day, g/d

   DMI = dry matter intake, kg/d

   CP_DM = proportions xx

   adCP_CP = proportions xx

   Milk_CP = milk crude protein, kg/d. If the animal is not lactating
   and within 60 DIM (parturition) this term “Milk_CP” in equation
   A.Cow.F.15 is replaced with “0.00014 \* MBW”. MBW = mature body
   weight (see Chapter 6 of NASEM book for details).

   BodyGain_CP = body gain CP, kg/d. For lactating cows this can be
   ignored.

+-----------------------+-------------------------------+--------------+
| :math:`{UE}_{DM} =`   |    :math:`(0.0146*UN)/DMI`    | [B.Cow.F.15] |
+-----------------------+-------------------------------+--------------+

..

   UE_DM = Urinary energy, Mcal/kg DM

   DMI = dry matter intake, kg/d

   Energy coefficient = 0.0146 Mcal/g of urinary N.

   Metabolizable energy

+------------------------------+---------------------------------------+--------------+
| :math:`{ME}_{DM}`\ :math:`=` |  :math:`DE_{DM} - GasE_{DM} - UE_{DM}`| [B.Cow.F.16] |
+------------------------------+---------------------------------------+--------------+

..

   ME_DM = metabolizable energy, Mcal/kg DM.

   GasE_DM = gas energy loss, Mcal/kg DM

   UE_DM = urinary energy, Mcal/kg DM

   Equation B.Cow.F.16 uses whole-diet estimates of gas losses and
   urinary energy in contrast with NRC (2001) where conversion of DE to
   ME was considered on an individual feed basis.

   Net energy lactation of diets (NEL_DM; Mca/kg DM). The efficiency of
   conversion of ME to NEL is assumed to be equal to 0.66.

+-----------------------+---------------------------------+--------------+
| :math:`{NEL}_{DM} =`  |    :math:`0.66*ME_{DM}`         | [B.Cow.F.17] |
+-----------------------+---------------------------------+--------------+

Protein supply
--------------

Protein supply from the feed is estimated in terms of metabolizable
protein (MP) and includes 2 parts: digestible rumen undegradable protein
(RUP) and digestible microbial crude protein (MCP), which is produced
through rumen degradable protein (RDP). MCP production requires nitrogen
source and energy source, so MCP is either nitrogen limited (when energy
is sufficient) or energy limited (when nitrogen is sufficient).

The NASEM (2021) protein system expanded feed library and retain
elements of the NRC (2001) but (A, B, C fractions, and *kd*) but to
re-derive statics *kp* values for forages and concentrates to remove the
bias compared to NANMN flows (non-ammonia, non microbial N flows).
Microbial protein is predicted as a function of both RDP and rumen
degraded carbohydrates (starch and NDF).

In NASEM (2021), the contents (% of CP) of individual essential amino
acids of common feedstuffs are also included in tabulated values.

Revised estimates of Static *kp*

+---------+-----------+------------------------------------------------------+--------------+
| :math:`{Dt}_{RUP} =`| :math:`\sum_{c=1}^{Nc}[(1 - DCa_{c})*(Dt_{CPAIn_{C}} | [B.Cow.F.18] |
|                     | - Dt_{CPAIn_{NPN,c}}) + kp_{c}/kp_{c}                |              |
|                     | + kd_{c}* Dt_{CPBIn_{c}} + Dt_{CPCIn_{c}}]`          |              |
+---------------------+------------------------------------------------------+--------------+

..

   Dt\_ = total diet concentration of the specified nutrient

   c = This subscript represents the class of feed the ingredient
   belongs to

   DCa_c = ruminal degradability of fraction A in feed class c

   CPAIn_c = CP intake of fraction A within feed class c

   CPAIn_NPN,c = intake of ruminally degraded nonprotein N x 6.25 (CP
   equiv.) within feed class c

   CPBIn_c = intake of CP of fraction B within feed class, c

   CPCIn_c = CP intake of fraction C within feed class c

   kp_c = static *kp* for feed class c (e.g., forage or concentrate),
   and kd_c is the weighted average of the in situ determined kd for
   each feed in class c

*Metabolizable protein supply (MP)*

Endogenous protein flow to the duodenum

+-----------------+----------------------------------------+--------------+
|                 |    :math:`15.4 + 1.21*DMI`             | [B.Cow.F.19] |
| :math:`{DU}_{En |                                        |              |
| dN} =`          |                                        |              |
+-----------------+----------------------------------------+--------------+

..

   DU_EndN = duodenal endogenous N, g/d

   DMI = dry matter intake, kg/d

Microbial protein supply (predicted values should be multiplied by 6.25
to convert to CP.

+--------------+------------------------------------------+--------------+
|              | :math:`[{\beta}_{0} + {\beta}_{1}        | [B.Cow.F.20] |
| :math:`MicN=`| *RDP)]/[(1 + {\beta}_{2}/RDNDF)          |              |
|              | *(1 + {\beta}_{3}/RDS)]`                 |              |
+--------------+------------------------------------------+--------------+

Where,

+-----------------+---------------------------------------+--------------+
| :math:`RDNDF =` | :math:`[(-31.9+0.721*NDF)-(0.247*St)- | [B.Cow.F.21] |
|                 | +(6.63*CP)-(0.211*{CP}^{2})-(38.7*AD  |              |
|                 | F/NDF)-(0.121*ForWet)+(1.51*DMI)*((N  |              |
|                 | DF/100)*DMI)]/100`                    |              |
+-----------------+---------------------------------------+--------------+

+-----------------+---------------------------------------------+------------+
| :math:`RStDig =`| :math:`[(71.2-(1.45*DMI)+(0.424*fNDF)       |[B.Cow.F.22]|
|                 | +(1.39*St)-(0.0219*{St}^{2})-(0.154*ForWet))|            |
|                 | *(St/100)*DMI]/100`                         |            |                    
+-----------------+---------------------------------------------+------------+


   MicN = microbial N, g/d

   RDP = rumen degradable protein intake, kg/d

   RDNDF = rumen-degraded NDF intake, kg/d

   RDS = rumen-degraded starch intake, kg/d

   NDF = neutral detergent fiber, % diet DM

   St = starch, % diet DM

   CP = crude protein, % diet DM

   ADF = acid detergent fiber, % diet DM

   ForWet = concentration of wet forage (greater than 20 percent DM) in
   the diet

   DMI = dry matter intake, kg/d

   fNDF = forage NDF, % diet DM

   Regression coefficients in the MicN equation

   :math:`\beta_{0} =` 101 ± 11 (intercept); :math:`\beta_{1} =` 82.6 ±
   4.2 (coefficient for RDP intake); :math:`\beta_{2} =` 0.094 ± 0.028
   (coefficient for rumen-degraded NDF intake); :math:`\beta_{3} =`
   0.027 ± 0.010 (coefficient for rumen-degraded starch)

*Metabolizable amino acid supply*

Metabolizable Amino Acids from Microbial Crude Protein (MCP; pages 77
and 78 in NASEM book)

Assessing metabolizable AA supply from MCP in ruminal outflow requires
knowing: 1) the TP/CP ratio of MCP, 2) the AA composition of microbial
TP (true protein), and 3) the digestibility of microbial TP.

Metabolizable Amino Acids from Rumen Undegradable Protein (RUP; pages 77
and 78 in NASEM book)

The AA profile of the RUP fraction of the feedstuffs is assumed to be
the same as in the original feedstuff. This is in line with the previous
version of the model.

Mineral supply
--------------

It follows the same approach as in the NRC (2001), however absorption
coefficients (AC; digestibilities) were adjusted (e.g., Table 7-1, page
109 in NASEM book)

   Use calcium supply as an example (phosphorus is similar):

+-------------------------+-----------------------------------------------------+--------------+
| :math:`{Ca}_{supply} =` | :math:`\sum_{i}feed_{i}*Ca_{i}*\frac{dCa_{i}}{100}` | [B.Cow.F.23] |
+-------------------------+-----------------------------------------------------+--------------+

..

   dCa\ :sub:`i` = Ca digestibility of feed i, % of Ca

   dCa = 40% for forage, 40% for concentrate, 60% for mineral

   dP (P digestibility) = For feeds that did not have P fraction data,
   AC was set as default of 0.72. AC is 0.84 for inorganic P and 0.68
   for organic P fraction.
   