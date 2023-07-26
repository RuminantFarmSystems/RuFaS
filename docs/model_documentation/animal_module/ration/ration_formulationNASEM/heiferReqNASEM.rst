.. _Heifers-requirements-pseudocode-NASEM :

Dairy Cattle Ration NASEM 2021 (Heifers)
========================================

**# of Subroutine and Name:** Description of equations used to calculate
nutrient requirements of heifers according to equations provided within
NASEM (2021)

Flow of Information:
--------------------

A. Nutrient requirements include energy, protein, minerals (Ca and P).

B. Energy supply, protein supply and mineral supply from feeds are calculated.

C. Supply >= this refers to the nutrients supplied by the diet to meet
   nutritional requirements. All the equations are calculated on a daily basis

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

   xiv.  DMIest: Estimated dry matter intake according to empirical
         prediction equation (kg/d)

-  Feed inputs (from the feed table, variables with \* are not used in
   any equations yet)

   i.    DM: Dry matter (% of as-fed basis)

   ii.   Type: Feed type (Forage, Concentrate, or Mineral. In
         addition, NASEM (2021) include the following categories:
         Dry Forage, Wet Forage, Pasture)

   iii.  Ash (% of DM)

   iv.   OM: Organic matter (% of DM)

   v.    ROM: Residual OM (% of DM)

   vi.   N: Nitrogen (% of DM)

   vii.  CP: Crude protein (% of DM)

   viii. TP: True protein (% of DM)

   ix.   MP: Metabolizable protein

   x.    NPN: Non protein N

   xi.   CP equivalent to NPN

   xii.  DM of NPN source

   xiii. CPN_A: Fraction A of protein, soluble protein, degraded
         immediately in rumen (% of CP)

   xiv.  CPN_B: Fraction B of protein, potentially degradable protein,
         require time to generally degrade in rumen (% of CP)

   xv.    CPN_C: Fraction C of protein, not degradable in rumen (% of
          CP)

   xvi.    RDP: Ruminally degraded CP

   xvii.   RUP: Ruminally undegraded CP

   xviii.  MICP: Microbial CP

   xix.    MN: Microbial N

   xx.     MTP: Microbial TP

   xxi.    EndCP: Endogenous CP

   xxii.   EndN: Endogenous N

   xxiii.  Starch (% of DM)

   xxiv.   NDF: Neutral detergent fiber (% of DM)

   xxv.    Forage NDF

   xxvi.   ADF: Acid detergent fiber (% of DM)

   xxvii.  Lignin (% of DM,)

   xxviii. FA: Fatty acids

   xxix.   GE: Gross energy (standard value, Mcal/kg)

   xxx.    DE: Digestible energy (standard value, Mcal/kg)

   xxxi.   ME: Metabolizable energy (standard value, Mcal/kg)

   xxxii.  NEM: Net energy for maintenance (standard value, Mcal/kg)

   xxxiii. NEG: Net energy for growth (standard value, Mcal/kg)

   xxxiv.  Ca: Calcium content (% of DM)

   xxxv.   P: Phosphorus content (% of DM)

   xxxvi.  Other minerals (Mg, K, Na, etc. are not considered yet)

   xxxvii. Cost: Feed cost ($/kg of DM)

-  Outputs

   i. To be determined

Energy Requirements
-------------------

   Energy requirement is divided into four components: maintenance,
   activity, growth, and pregnancy (energy units are net energy for
   lactation, Mcal per day).

Maintenance requirement
-----------------------

   Maintenance requirement is calculated based on metabolic body weight
   (BW\ :sup:`0.75`).
   
   :math:`\mathbf{CBW =}` **input variable, otherwise CBW = MW** \* **0.06275**  [B.Heifer.A.1]

      CBW = Calf birth weight (kg) can be estimated using the equation above, 
      otherwise there is an input variable depending on breed. Holstein = 42 kg; Jersey = 31 kg

      MW = Mature body weight (kg). Default values according to NASEM (2021) = 700 kg for Holstein; 520 kg for Jersey

   **GrUterW =** (**CBW \* 1.825**) :math:`\mathbf{\exp^{- 0.0243\  - \ (0.0000245*DOP)*(280 - DOP)}}` [B.Heifer.A.2] 

      GrUterW = gain in reproductive tissues associated with pregnancy

      DOP= Days of pregnancy (this must be between 12 and 280 DOP)

   :math:`\mathbf{NEmaint =}` :math:`\mathbf{{0.10*(BW - GrUterW)}^{0.75}}`  [B.Heifer.A.4]

      for normal activity in confinement conditions, otherwise include
      adjustments for activity requirements under grazing conditions.

      NEmaint = Net energy for maintenance requirement, Mca

Activity requirement
--------------------

   Activity requirement (NEa) is proportional to body weight and daily
   walking distance. Grazing systems and hilly topography will cost
   additional energy. This is part of the energy requirements for
   maintenance, and it must be added to NEmaint when applied.

   :math:`\mathbf{NEa1\  =}` **(Dt_PastIn)/DtDMIn < 0.005; 0,** 
      otherwise if it is ≥  0.005,then **0.0075** \* :math:`\mathbf{{BW}^{0.75}}` \* **((600-12 x DtPastSupplIn))/600**    [B.Heifer.A.5]  

      DtPastIn = consumption of pasture DM, kg/d

      DtPastSupplIn = consumption of non pasture DM, kg/d

      NEa1 = Cost of locomotion for grazing activity on a flat surface, Mcal/d

   Additional energy requirements are also estimated

   :math:`\mathbf{NEa2\  =}` :math:`\mathbf{0.00035(DistParlor)/1000}` \* :math:`\mathbf{TripParlor*BW}` [B.Heifer.A.6] 

      DistParlor = round trip distance from the barn or paddock to the parlor, m

      TripsParlor = number of trips to the parlor, n

      NEa2 = additional locomotion cost for walking to the parlor for a flat surface, Mcal/d

   :math:`\mathbf{NEa3\  =}` :math:`\mathbf{0.0067*EnvTopoParlor\ /\ 1000*BW\ }` [B.Heifer.A.7]

      EnVTopoParlor = daily total climb while grazing and during transit
      between the milking parlor and the barn or paddock, m

      NEa3 = Energy cost associated with elevation change while grazing and
      in transit to and from milking, Mcal/d

   :math:`\mathbf{NEa\  =}` :math:`\mathbf{NEa1  + NEa2  + NEa3}`    [B.Heifer.A.8]

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

   **EBW =** :math:`\mathbf{0.85 * BW\ }`            [B.Heifer.A.9]

      EBW = Empty body weight (without digesta), kg
      
   **EBG =** :math:`\mathbf{0.85 * ADG\ }`             [B.Heifer.A.10]

      EBG = Empty body weight gain (without digesta), kg

      ADG = Average daily gain, kg/d

   :math:`\mathbf{FatADG = (0.067 + 0.375*(BW/MW)) * EBG/ADG}` [B.Heifer.A.11]

      FatADG = Fat constituent of average daily gain, g/g

   :math:`\mathbf{ProtADG = (0.201 + 0.081 * (BW/MW)) * EBG/ADG}` [B.Heifer.A.12]

      FatADG = Protein constituent of average daily gain, g/g

   :math:`\mathbf{REFADG = 9.4*FatADG + 5.55*ProtADG}` [B.Heifer.A.13]

      REFADG = Retained energy of frame ADG, Mcal/kg

   :math:`\mathbf{MEFrameADG = REFADG/0.4}`  [B.Heifer.A.14]

      MEFrameADG = Metabolizable energy for frame ADG, Mcal/kg. The value 0.4 is
      assumed to be the efficiency of converting feed ME to NE for gain (NEg).

   :math:`\mathbf{NElFrameADG = REFADG/0.61}` [B.Heifer.A.15]

      NElFrameADG = Net energy for frame ADG, Mcal/kg. The efficiency of
      converting NEl to NEg is based on the conversions of 0.40 for ME to
      NEg and 0.66 for ME to NEl and is thus 0.40/0.66 = 0.61.

Pregnancy requirement
---------------------

   Daily rates of wet tissue deposition (kg/d) are derived from
   equations A.2 and A.3 as defined above.

   During gestation

   :math:`\mathbf{GrUterWGain = (0.0243 – (0.0000245 * DayGest)) * GrUterW}`  [B.Heifer.A.16]

   :math:`\mathbf{NElPreg = GrUterWGain * (0.882 / 0.14) * 0.66}`    [B.Heifer.A.17]

      NElPreg = Net energy (lactation) requirement for pregnancy, Mcal/d.
      Assumptions: tissue contains 0.882 Mcal of energy / kg; an ME to
      gestation energy efficiency of 0.14; and ME to NEl efficiency of 0.66.

      MEpreg = Metabolizable energy requirement for pregnancy, Mcal/day

Protein requirements
--------------------

   Protein requirement is divided into three components: maintenance,
   growth, and pregnancy and lactation (all in metabolizable protein
   (MP, g). The last is defined as the sum of rumen undegraded protein
   (RUP + microbial protein (MICP). Requirements for essential amino
   acids (EAA) are also included in NASEM (2021) but not yet implemented
   in the current version of RuFaS.

   Each physiological function is quantified in terms of TP (true
   protein), instead of CP (crude protein).

   To convert both net protein and net amino acids values to a
   metabolizable basis, net values have to be divided into the
   calculated efficiencies for each physiological function.

Maintenance requirement
-----------------------

   The protein requirements for non-productive functions (the
   quantification of protein secretion and accretion), includes: scurf +
   endogenous urinary loss + metabolic fecal protein.

   - Scurf

   :math:`\mathbf{NPscurf = 0.20 * {BW}^{0.60} * 0.85}`  [B.Heifer.B.1]                                                 |
      
      NPscurf= Net protein requirement
   
   :math:`\mathbf{NetAAscurf = NPscurf * [AACorrScurf]/100}` [B.Heifer.B.2]                                                 |

      NPscurf= Net protein requirement for scurf in grams per day

      BW = body weight in kg

      NetAAscurf = Net AA demand for scurf excretion in grams per day

      AACorrScurf = For each individual amino acid, a fixed value for each
      AA excreted as scurf is assumed according to column four in Table 6-2
      (page 79) in the NASEM (2021) book.

   - Endogenous urinary excretion
      
   :math:`\mathbf{NPEndUrin = 53 * 6.25 * BW * 0.001}`  [B.Heifer.B.3]                                    |
   
   :math:`\mathbf{NetAAEndUrin = 0.010 * 6.25 * BW * [AACorrWhEmpBody] / 100}` [B.Heifer.B.4] 

      PEndUrin = Net protein requirement for endogenous urinary excretion

      NetAAEndUrin = Net amino acids requirement for endogenous urinary excretion

      AACorrWholeEmptyBody = For each individual amino acid, a fixed value
      for each AA excreted as a whole empty body is assumed according to
      column five in Table 6-2 (page 79) in the NASEM (2021) book.

   - Metabolic fecal protein

   The daily loss of CP as metabolic fecal protein (MFP) is estimated
   using the following equation.

   :math:`\mathbf{CPMFP = (11.62 + 0.134 * NDF) * DMI}` [B.Heifer.B.5]  

      CPMFP = Crude protein (CP) in metabolic fecal protein MFP in grams per day

      NDF = Neutral detergent fiber in the diet, as a % on dry matter basis

      DMI = Dry matter intake, kg/d

   :math:`\mathbf{NPMFP = CPMFP * 0.73}` [B.Heifer.B.6]

      NPMFP = Net protein requirement for metabolic fecal protein in grams
      per day. There is an assumption: 73 percent of true protein (TP) in MFP.

   :math:`\mathbf{NPAAMFP = NPMFP *[AACorrMFP] / 100}`      [B.Heifer.B.7]                              |

      NetAAMFP= Net amino acids requirement for metabolic fecal protein in grams per day

      AACorrMFP = aminoacids corrected for MFP. There is a fixed value for
      each individual amino acid in column six provided in the Table 6-2
      (page 79) of the NASEM (2021) book.

Growth requirement (frame growth)
---------------------------------

   There are two important concepts: frame growth and BW changes related
   to mobilization of body reserves. Following equations refer to the
   first item.

   :math:`\mathbf{NPGrowth =  FrameWG * 0.11 * 0.86}`  [B.Heifer.B.8]                              |   

      NPGrowth= Net protein requirement for body frame weight gain in grams per day.

      If the change in BW is not frame growth but rather a change in body
      reserves, the protein content is assumed to be 8.0 percent protein.
      In that case, the 0.11 coefficient should be replaced by 0.08 in the
      above equation.

   :math:`\mathbf{NetAAGrowth = NPGrowth * [AACorrWEBW] / 100}`   [B.Heifer.B.9]

      NetAAGrowth = Net amino acids requirement for body frame weight gain
      in grams per day.

      AACorrWEBW = For each individual amino acid, a fixed value for each
      AA excreted as a whole empty body is assumed according to column five
      in Table 6-2 (page 79) in the NASEM (2021) book.

Pregnancy requirement 
----------------------

   :math:`\mathbf{NPGest = GainGrUter * 125}` [B.Heifer.B.10]

      NPGest= Net protein requirement for pregnancy in grams per day.

      GainGrUter = daily gain in mass of the gravid uterus in kilograms per day.

      125 (coefficient) = Daily gain in mass of the gravid uterus is
      assumed to contain 125 g of protein per kilogram of wet weight.

   :math:`\mathbf{NetAAGest = NPGest * [ACorrWEBW] / 100}` [B.Heifer.B.11] 

      NetAAGest = is the amino acids composition of protein accretion
      associated with pregnancy.

      AACorrWEBW = For each individual amino acid, a fixed value for each
      AA excreted as whole empty body composition is assumed to be the one
      provided in column five in Table 6-2 (page 79) in the NASEM (2021) book.


Total requirement - Recommendations of metabolizable protein amino acids according to NASEM (2021)
--------------------------------------------------------------------------------------------------

   :math:`\mathbf{RecomMPSupply = [(NPScurf + NPMFP) / TargetEffMP]}`
    :math:`\mathbf{ + (NPGest / 0.33) + (NPGrowth / 0.40) + NPEndUrin}` 
   
   [B.Heifer.B.12]

   :math:`\mathbf{RecomMPSupply = [(NetAAScurf + NetAAMFP) / TargetEffAA]}`
    :math:`\mathbf{ + (NetAAGest / 0.33) + (NetAAGrowth / 0.40) + NPEndUrin}`
    
   [B.Heifer.B.13]                

      TargetEffMP and TargetEffAA= Proposed target efficiencies of
      converting metabolizable protein (MP) and essential amino acids (EAA)
      to export proteins and body gain. See Table 6-4 on page 88 in the
      NASEM (2021) book.

Mineral requirements
--------------------

   Only calcium and phosphorus requirements are included in the code at
   present.

Calcium requirement
-------------------

Maintenance
~~~~~~~~~~~

   :math:`\mathbf{Ca_{main}\  = 0.90*DMI}`  [B.Heifer.C.1]

      Ca_main = Calcium requirement for maintenance, g/day

      DMI = dry matter intake in kg/day

Growth
~~~~~~

   :math:`\mathbf{Ca_{growth} =  983*MW^{- 0.22}*BW^{- 0.22}*ADG}` [B.Heifer.C.2]

      Ca_growth = Calcium requirement for growth, g/day

      MW = mature body weight in kg

      ADG = average daily gain in grams per day.

Pregnancy
~~~~~~~~~

   :math:`\mathbf{Ca_{preg} = 0.02456 * exp((0.05581 - 0.00007 * DOP) * DOP)}`
      :math:`\mathbf{- 0.02456 * exp((0.05581 - 0.00007 * (DOP - 1)) * (DOP -  1))}`
      :math:`\mathbf{* (BW / 715), if DOP > 190; 0, otherwise}` [B.Heifer.C.3] 

      Ca_preg = Calcium pregnancy requirement, g/day

      DOP = days of pregnancy

      BW = Body weight in kg

      715 is the average cow weight in the study by House and Bell (1993);
      therefore, pregnancy (gestation) requirement is scaled to that BW.
      For details see Page 107 in the Minerals chapter of NASEM (2021)
      book. IF DOP < 190; then it is assumed that Ca_Preg is equal to zero.

Total Calcium requirement

   :math:`\mathbf{Ca_{req} = Ca_{main} + Ca_{growth} + Ca_{preg}}` [B.Heifer.C.4]
      
      Ca_Req = Total calcium requirement, g/day

Phosphorus requirement
----------------------

Maintenance
~~~~~~~~~~~

   :math:`\mathbf{P_{main}  =  1.0 * DMI + 0.0006 * BW}`, **for lactating cows**  [B.Heifer.C.5]

      P_main = Phosphorus requirement for maintenance, g/day

      DMI = dry matter intake, kg/day

      BW = Body weight, kg

Growth
~~~~~~


   :math:`\mathbf{P_{growth} = (1.2 + 4.635 * MW^{0.22} * BW^{- 0.22}) * ADG}` [B.Heifer.C.6]

      P_growth = Phosphorus requirement for growth, g/day

      MW = mature body weight, kg

      BW = Body weight, kg

      ADG = average daily BW gain in grams per day.

Pregnancy 
~~~~~~~~~~

   :math:`\mathbf{P_{preg} = 0.02743 * exp(( 0.05527 - 0.00007) * DOP) - 0.02743}`
      :math:`\mathbf{* exp((0.05527 - 0.000075 * (DOP - 1) * (BW / 715))}` 
      :math:`\mathbf{* (*DOP - 1)), if DOP > 190; 0, otherwise}` [B.Heifer.C.7]

      P_preg = Phosphorus requirement for pregnancy, g

      DOP = days of pregnancy

      BW = Body weight

      715 is the average cow weight in the study by House and Bell (1993);
      therefore, pregnancy (gestation) requirement is scaled to that BW.
      For details see Page 112 in the Minerals chapter of NASEM (2021)
      book. IF DOP < 190; then it is assumed that P_Preg is equal to zero.

Total Phosphorus requirement
   
   :math:`\mathbf{P_{req} = P _{main} + P_{growth} + P_{preg}}` [B.Heifer.C.8]

      P_Req = Total phosphorus requirement, g/day

Dry matter intake estimation
----------------------------

   :math:`\mathbf{DMIest = (1.97  -  0.75 * exp( 0.16 * (DOP - 280))) 100 * BW}`
      *this is for pregnant heifers; otherwise*
   :math:`\mathbf{0.022 * MatBW * (1 - exp(- 1.54 * (BW / MatBW))}`  [B.Heifer.D.1]

      DMIest = dry matter intake estimation, kg/d

      DOP = days of pregnancy

      BW = body weight, kg

      MatBW = is the expected mature body weight of the heifer, kg

Other requirements
------------------

   1. Minimum dietary NDF content: 25%

   2. Maximum dietary NDF content: 40%

   3. Minimum dietary forage NDF content: 19%

   4. Maximum dietary fat content: 7%

Feed nutrient supply
--------------------

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

   :math:`\mathbf{ROM = 100 - Ash - NDF - Starch - (FA/FatFactor) - (CP - 0.64 * sNPNCPE)}`  [B.Heifer.F.1]

      ROM = Diet residual organic matter concentration, % DM

      Ash = Diet ash content, % DM

      NDF = Diet Neutral detergent fiber content, % DM

      Starch = Diet starch content, % DM

      FA = Diet fatty acids, % DM

      Fat_Factor = Adjustment factor, it is equal to 1 if Feed type = fatty
      acid or FA soap and 1.06 for all other feeds, % DM

      sNPNCPE = The CP equivalent from supplemental non protein nitrogen
      (0.89 Mcal/kg)

   **Gross energy of a diet or feed**
   
   :math:`\mathbf{{GE}_{DMFeed} = 0.042 * {NDF}_{DM} + 0.0423 * {Starch}_{DM} + 0.040 * {ROM}_{DM}}`
      :math:`\mathbf{+ 0.094* {FA}_{DM} + 0.0565 * ({CP}_{DM} + {sNPNCPE}_{DM} + 0.0089 * {NPNCPE}_{DM}}` [B.Heifer.F.2]

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

   **True digestibility coefficients of feed fractions for base
   conditions**

   For the NASEM (2021) system, the base condition is for an animal with
   a 3.5 percent of BW and fed a diet with 26 percent starch. All diets
   are assumed to have adequate RDP to meet microbial requirements and
   adequate proper forage NDF to promote proper rumen conditions.

   Neutral detergent fiber
 
   :math:`\mathbf{dNDF_{NDFBase} = (0.75 * (NDF_{DM} - Lignin_{DM}) * (1 - {(Lignin_{DM}/NDF)}^{0.667})) / NDF_{DM}` [B.Heifer.F.3]

      *Lignin based equation taken from NRC (2001)*   

   :math:`\mathbf{0.12 + 0.61*IVNDFD}`

      *In vitro NDF digestibility based equation taken from Lopes et al., (2015)*

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


   :math:`\mathbf{dCP_{CP} = (RDP_{DM} + dRUP_{DM})/CP_{DM}}` [B.Heifer.F.4]
      
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

   :math:`\mathbf{dNDF_{NDF} = dNDF_{NDFBase} - 0.0059 * ({Starch}_{DM} - 26) - 1.1 * (DMI_{BW} - 0.035)}` [A.Heifer.F.5]

      dNDF_NDF = digested proportion of NDF

      dNDF_NDFBase = digested proportion of NDF at base conditions

      Starch_DM = starch concentration, % DM

      DMI_BW = DMI/BW, kg/kg

      0.035 = 3.5% of BW

   Starch

   :math:`\mathbf{dStarch_{Starch} = dStarch_{StarchBase} - 1.0 * (DMI_{BW} - 0.0035)}` [B.Heifer.F.6]
   
      dStarch_Starch = digested proportion of starch

      dStarch_StarchBase = digested proportion of starch at base conditions

      Starch_DM = starch concentration, % DM

      DMI_BW = DMI/BW, kg/kg

      0.035 = 3.5% of BW

   **Estimating Endogenous Fecal Material and Apparent Digestibilities**

   Metabolic fecal crude protein

   :math:`\mathbf{MFCP = 11.62 + 0.134 * NDF_{DMI}}` [B.Heifer.F.7]

      MFCP = metabolic fecal CP, g/kg DMI

      NDF is a percentage of DM

   :math:`\mathbf{fMCP = (MicCP*0.2)/DMI}` [B.Heifer.F.8] 

      fMCP = fecal microbial CP, g/kg DMI

      MicCP = Microbial CP, g/d


   :math:`\mathbf{adROM_{ROM} = ((ROM * 0.96) - 3.43) / ROM}` [B.Heifer.F.9]

      adROM_ROM = apparently digested proportion of ROM

      ROM = Residual organic matter in kg/d


   :math:`\mathbf{adCP_{CP} = ((RDP + dRUP) - (fMCP + MFCP)) / CP}` [B.Heifer.F.10]

      adCP_CP = apparently digested proportion of CP

      RDP = Rumen degradable crude protein, kg/d

      dRUP = digested rumen undegradable protein, kg/d

      fMCP = fecal microbial CP, kg/d

      MFCP = metabolic fecal CP, kg/d

      CP = crude protein, kg/d


   :math:`\mathbf{adOM_{OM} = (NDF + dNDF_{NDF} + Starch * dStarch_{Starch} + FA * dFA_{FA} +}`
      :math:`\mathbf{RDP + dRUP + 0.96 * ROM - MFCP - fMCP - efROM) / OM}` [B.Heifer.F.11]

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


   :math:`\mathbf{DE_{DM} = 0.042*NDF_{DM}*dNDF_{NDF} + 0.0423*Starch_{DM}*dStarch_{Starch}}`
      :math:`\mathbf{+ 0.0940 * FA_{DM} * dFA_{FA} + 0.0565*(RDP_{DM} - sNPNCPE_{DM}}`
      :math:`\mathbf{+ dRUP_{DM} + 0.00899*sNPNCPE_{DM} + 0.040*ROM_{DM\ }*0.96}`
      :math:`\mathbf{- 0.00565*MFCP - 0.00565*fMCP - 0.0040*efROM_{DM}}` [B.Heifer.F.12]

      DE_DM = digestible energy, Mcal/kg DM

      Feed fractions are given as a percentage of DM; endogenous fractions
      are g/kg; and digestibilities are expressed as proportions.

   **Estimating the Metabolizable Energy of Diets**

   To calculate ME supply, energy losses from both fermentation gasses
   and urine have to be discounted from the DE value of the diet.

   Gas energy loss

   :math:`\mathbf{GasE_{DM} = (0.294 * DMI - 0.347 * FA_{DM} + 0.0409 * dNDF_{DM}) / DMI}` [B.Heifer.F.13]

      GasE_DM = gas energy loss, Mcal/kg DM

      DMI = dry matter intake, kg/d

      FA_DM = Fatty acids, % diet DM

      dNDF_DM = digested neutral detergent fiber, % diet DM

   Urinary energy loss is calculated from estimated urinary N excretion.


   :math:`\mathbf{UN = (DMI * CP_{DM} * adCP_{CP} - 0.00014 * MBW - BodyGain_{CP}) * 1,000 / 6.25}` [B.Heifer.F.14] 

      UN = Urinary N excretion per day, g/d

      DMI = dry matter intake, kg/d

      CP_DM = proportions xx

      adCP_CP = proportions xx

      MBW = mature body weight

      BodyGain_CP = body gain CP, kg/d. For lactating cows this can be ignored.

   
   :math:`\mathbf{{UE}_{DM} = (0.0146*UN) / DMI}` [B.Heifer.F.15] 

      UE_DM = Urinary energy, Mcal/kg DM

      DMI = dry matter intake, kg/d

      Energy coefficient = 0.0146 Mcal/g of urinary N.

   Metabolizable energy

   :math:`\mathbf{{ME}_{DM} = DE_{DM} - GasE_{DM} - UE_{DM}}` [B.Heifer.F.16] 

      ME_DM = metabolizable energy, Mcal/kg DM.

      GasE_DM = gas energy loss, Mcal/kg DM

      UE_DM = urinary energy, Mcal/kg DM

      Equation B.Heifer.F.16 uses whole-diet estimates of gas losses and
      urinary energy in contrast with NRC (2001) where conversion of DE to
      ME was considered on an individual feed basis.

   Net energy lactation of diets (NEL_DM; Mca/kg DM). The efficiency of
   conversion of ME to NEL is assumed to be equal to 0.66.

   :math:`\mathbf{{NEL}_{DM} = 0.66*ME_{DM}}` [B.Heifer.F.17] 

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

   :math:`\mathbf{{Dt}_{RUP} = \sum_{c=1}^{Nc} ((1 - DCa_{c})*(Dt_{CPAIn_{C}} - Dt_{CPAIn_{NPN,c}}) + kp_{c}/kp_{c} + kd_{c} *}` 
      :math:`\mathbf{Dt_{CPBIn_{c}} + Dt_{CPCIn_{c}}})` [B.Heifer.F.18]

      Dt = total diet concentration of the specified nutrient

      c = This subscript represents the class of feed the ingredient belongs to

      DCa_c = ruminal degradability of fraction A in feed class c

      CPAIn_c = CP intake of fraction A within feed class c

      CPAIn_NPN,c = intake of ruminally degraded nonprotein N x 6.25 (CP
      equiv.) within feed class c

      CPBIn_c = intake of CP of fraction B within feed class, c

      CPCIn_c = CP intake of fraction C within feed class c

      kp_c = static *kp* for feed class c (e.g., forage or concentrate),
      and kd_c is the weighted average of the in situ determined kd for
      each feed in class c

   **Metabolizable protein supply (MP)**

   Endogenous protein flow to the duodenum
   
   :math:`\mathbf{{DU}_{EndN} = 15.4 + 1.21 * DMI}`  [B.Heifer.F.19]

      DU_EndN = duodenal endogenous N, g/d

      DMI = dry matter intake, kg/d

   Microbial protein supply (predicted values should be multiplied by 6.25
   to convert to CP.

   :math:`\mathbf{MicN = ({\beta}_{0} + \beta_{1} * RDP) / ((1 + \beta_{2}/RDNDF) * (1 + \beta_{3}/RDS))}`  [B.Heifer.F.20]

   Where,

   :math:`\mathbf{RDNDF = (( - 31.9 + 0.721*NDF) - (0.247*St) + (6.63*CP) -}`
      :math:`\mathbf{(0.211*{CP}^{2}) - (38.7*ADF/NDF) - (0.121*ForWet) +}`
      :math:`\mathbf{(1.51*DMI)*((NDF/100)*DMI))) / 100}` [B.Heifer.F.21]


   :math:`\mathbf{RStDig = (71.2 - (1.45*DMI) + (0.424*fNDF) + (1.39*St) -}`
      :math:`\mathbf{(0.0219*{St}^{2}) - (0.154*ForWet))*(St/100)*DMI)) / 100}` [B.Heifer.F.22]

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

   :math:`mathbf{\beta_{0} = 101 ± 11}` **(intercept);** :math:`mathbf{\beta_{1} = 82.6 ± 4.2}` **(coefficient for RDP intake);** 
   :math:`mathbf{\beta_{2} = 0.094 ± 0.028}` **(coefficient for rumen-degraded NDF intake);** :math:`mathbf{\beta_{3} = 0.027 ± 0.010}` **(coefficient for rumen-degraded starch)**

   **Metabolizable amino acid supply**

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


   :math:`\mathbf{{Ca}_{supply} = \sum_{i}^{} feed_{i} * Ca_{i} * \frac{dCa_{i}}{100}}` [B.Heifer.F.23]

      :math:`dCa_{i}` = Ca digestibility of feed i, % of Ca

      dCa = 40% for forage, 40% for concentrate, 60% for mineral

      dP (P digestibility) = For feeds that did not have P fraction data,
      AC was set as default of 0.72. AC is 0.84 for inorganic P and 0.68
      for organic P fraction.