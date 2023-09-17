.. _Manure_excretion :

Manure Excretion
================

   | Last Updated: March 30, 2023 (by Haowen Hu)

Manure subroutine of the animal module

Implemented in general_manure.py, calf_manure_excretion.py,
growing_heifer_manure_excretion.py, lactating_manure_excretion.py,
dry_cow_manure_excretion.py

**Flow of Information**

   The amount of manure excreted by the animal is calculated from animal
   and ration characteristics. Equations for specific animal classes are
   included in the animal class manure file whereas equations that
   represent calculations for multiple animal classes are in
   general_manure.py. Methane emissions are calculated in the manure
   routine of the animal module.

**Arguments**

-  bw: body weight (kg, animal life cycle)

-  dry_matter_intake: dry matter intake (kg, pen ration)

-  CP_concentration: diet CP concentration (%, from ration_driver.py)

-  potassium_concentration: diet K concentration (%, from ration_driver.py)

-  ADF_concentration : diet ADF concentration (%, from ration_driver.py)

-  NDF_concentration : diet NDF concentration (%, from ration_driver.py)

-  ASH_concentration: diet ash intake (kg, from ration_driver.py)

-  milk_protein: milk protein (%, from cow.py)

-  milk_fat: milk fat (%, from cow.py)

-  days_in_milk: days in milk (days, from cow.py)


**Outputs**

-  manure: manure (kg as excreted)

-  total_solids: total solids (kg)

-  total_volatile_solids: volatile solids (kg)

-  degradable_volatile_solids: degradable volatile solids (kg)

-  manure_nitrogen : manure nitrogen (kg)

-  potassium : manure potassium (g)

-  fecal_water: fecal water (kg)

-  urine: urine (kg)

-  methane_emission : methane emissions (g/d)

-  urine_urea_nitrogen_concentration : urinary urea N concentration (g N/L)

-  total_ammonical_nitrogen_concentration: total ammoniacal N concentration in slurry (g N/L)

(1) **Calf Manure Excretion:** Equations for manure production specific to calves.

   a. **Manure Excretion: Calculates the amount of manure produced by calves.**

      **Manure excretion (kg/d):** Amount of feces and urine excreted daily by a calf (kg/d)

         :math:`manure\  = \ 3.45\  \times \ dry\_ matter\_ intake\ (Nennich\ et\ al.,\ 2005)`

            [A.3A.A.1]

            manure = amount of manure excreted (kg)

            dry_matter_intake = dry matter intake (kg)

      **Urine excretion (kg/d):** Amount of urine excreted in kg. This is an assumption.

         :math:`urine = 2.0`

            [A.3A.A.2]

            urine = amount of urine excreted (kg)

      **Total solids excretion (kg/d):** Amount of dry material excreted by the calf (kg/d).

         :math:`total\_ solids\  = \ 0.393\  \times dry\_ matter\_ intake` (Nennich et al., 2005)

            [A.3A.A.3]

            manure = amount of manure excreted (kg)

            dry_matter_intake = dry matter intake (kg)

      **Total volatile solids excretion (kg/d):**

         :math:`total\_ volatile\_ solids = 0.0023 \times bw` (ASAE, 2003)

            [A.3A.A.4]

            bw = animal weight (kg)

      **Degradable volatile solids excretion (kg/d)**

         :math:`degradable\_ volatile\_ solids = 0.9 \times volatile\_ solids` (Communication with Varma)

            [A.3A.A.5]

      **Non-degradable volatile solids excretion (kg/d)**

         :math:`non\_ degradable\_ volatile\_ solids = total\_ volatile\_ solids\  - degradable\_ volatile\_ solids`

            [A.3A.A.6]

   b. **Nutrient Excretion**

      **Manure N excretion (kg/d):** Amount of nitrogen excreted by a calf (kg/d).

         :math:`manure\_ nitrogen\ = (112.55 \times dry\_ matter\_ intake \times \ \frac{cp\_ conc}{100})\ /\ 1000` (Nennich et al., 2005)

            [A.3A.B.1]

            manure_nitrogen = amount of nitrogen excreted in manure (kg)

            dry_matter_intake = dry matter intake (kg)

            cp conc = concentration of crude protein in ration (%)

      **Urine N excretion (kg/d):** Amount of urine nitrogen excreted by a calf (kg/d).

         :math:`N\_ urine =` 0.45 \* N_manure (Communication with Varma)

            [A.3A.B.2]

            N urine = amount of nitrogen excreted in urine (kg)

            manure_nitrogen = amount of nitrogen excreted in manure (kg)

   c. **Methane Emissions**

      The user has an input option to select which methane model they want
      to use for methane emissions calculations.

      Literature Average: Pattanaik et al. (2003) reported no difference in calf methane
      production in crossbred calves. Methane emissions by calves are
      estimated from mean values observed in that study.

      :math:`methane\_ emission\  = \ \frac{0.013\  \times {{{\ bw}^{0.75}\  \times \ 4.184\ MJ/Mcal}^{}}^{}}{0.05565}`

         [A.3A.C.1]

         methane_emission = methane production (g/d)

         bw = animal weight (kg)

(2) **Growing Heifer Manure Excretion:** Equations for manure production
      specific to heifers.

   a. **Manure Excretion:** Calculates the amount of manure produced by heifers.

      **Urine excretion (kg/d):** Amount of urine excreted in kg with assumption
      that 1.038 kg urine is approximately 1 L. Due to lack of information, 
      average excretion rate from heifers is assumed.

         :math:`urine = 9.0` [(Nennich et al., 2005), Table 5]

            [A.3B.A.1]

            urine = amount of urine excreted (kg)

      **Manure excretion (kg/d):** Amount of feces and urine excreted daily by heifers (kg/d).

         :math:`manure = 4.158\  \times dry\_ matter\_ intake - 0.0246\  \times bw` (Nennich et al., 2005; NASEM, 2021)

            [A.3B.A.2]

            manure = amount of manure excreted (kg)

            dry_matter_intake = dry matter intake (kg)
            
            bw = animal weight (kg)

      **Total solids excretion (kg/d):** Amount of dry material excreted by heifers (kg/d). This is the same equation used for dry cows.

         :math:`total\_ solids = 0.178 \times dry\_ matter\_ intake + 2.733` (ASABE, 2005)

            [A.3F.A.3]

            total solids = amount of total solids excreted (kg)

            dry_matter_intake = dry matter intake (kg)

      **Total volatile solids excretion (kg/d):** Amount of volatile solids excreted by heifers (kg/d).

         :math:`total\_ volatile\_ solids = 0.0073 \times bw` [(ASABE,  2005) Table 1.b]

            [A.3B.A.3]

            total volatile solids = amount of volatile solids excreted (kg)

            bw = animal weight (kg)

      **Degradable volatile solids excretion (kg/d):** Amount of degradable volatile solids excreted by heifers (kg/d).

         :math:`degradable\_ volatile\_ solids = 0.9 \times volatile\_ solids` (Communication with Varma)

            [A.3A.A.5]

            degradable volatile solids = amount of degradable volatile solids excreted (kg)

            volatile solids = amount of volatile solids excreted (kg)

      **Non-degradable volatile solids excretion (kg/d)**

         :math:`non\_ degradable\_ volatile\_ solids = total\_ volatile\_ solids\  - degradable\_ volatile\_ solids`

            [A.3A.A.6]

   b. **Nutrient Excretion** (placeholder equations until mass balance
      completed)

      **Manure N excretion (kg/d):** Amount of nitrogen excreted by a heifer (kg/d).

         :math:`manure\_ nitrogen\ = (15.1 + 0.83\  \times \ \ (dry\_ mattter\_ intake\  \times \ 1000)`
         
            :math:`\times \frac{CP\_ concentration/6.25}{100})\ /\ 1000`
         
         (Reed et al., 2015; Johnson et al., 2016; NASEM, 2021)

            [A.3B.B.1]

            manure_nitrogen = amount of nitrogen excreted in manure (kg)

   `        dry_matter_intake = dry matter intake (kg)

            CP_concentration = concentration of crude protein in ration (%)

      **Urine N excretion (kg/d):** Amount of urine nitrogen excreted by a heifer (kg/d).

         :math:`N\_ urine = (14.3 + 0.510 \times \ (dry\_ matter\_ intake\  \times \ 1000) \times \ \frac{CP\_ concentration/6.25}{100})\ /\ 1000`
         (Reed et al., 2015)

            [A.3B.B.2]

            N urine = amount of nitrogen excreted in urine (kg)

            dry_matter_intake = dry matter intake (kg)

            CP_concentration = concentration of crude protein in ration (%)

      **Fecal N excretion (kg/d):** Amount of fecal nitrogen excreted by a heifer (kg/d)

         :math:`N\_ fecal = manure\_ nitogen\ - \ N\_ urine`

            [A.3B.B.3]

      **Manure K excretion (g/d):** Amount of potassium excreted by a heifer (g/d) .

         :math:`potassium = 1000\  \times \ dry\_ matter\_ intake \times \ \frac{potassium\_ concentration}{100}`
         (ASABE, 2005)

            [A.3B.B.4]

            potassium = amount of potassium excreted in manure (g)

            dry_matter_intake = dry matter intake (kg)

            potassium_concentration = concentration of potassium in ration (%)

   c. **Methane Emissions**

      The user has an input option to select which methane model they want
      to use for methane emissions calculations.

      An empirical equation relates methane emissions to dry matter intake
      (Boadi and Wittenberg, 2002).

         :math:`methane\_ emission\  = \ (38.62\  + \ 26.44\  \times \ dry\_ matter\ intake\ )\  \times 0.554`

            [A.3B.C.1]

            methane_emission = methane production (g/d)

            dry_matter_intake = dry matter intake (kg)

      IPCC Tier 2 (2006)

      The Tier 2 system of the IPCC relates methane emissions to gross
      energy intake by a conversion factor, Ym (= 0.065).

      Gross energy in the diet is calculated from diet nutrient composition
      (Moraes et al. 2014).

         :math:`gross\ energy\ conc\  = \ 0.263\  \times CP\_ concentration\  + \ 0.522\  \times EE\ conc`
                  
            | :math:`+ \ 0.198\  \times NDF\_ concentration\  + \ 0.160\  \times soluble\ residue`

            [A.3B.C.2]

            gross energy conc = dietary gross energy concentration (MJ/kg DM)

            CP_concentration = crude protein concentration (% DM)

            ee con = ether extract concentration (or crude fat, % DM)

            NDF_concentration = neutral detergent fiber concentration (% DM)

            soluble residue = dietary percentage of soluble residues [% DM, = (100 - ASH_concentration) - NDF_concentration - CP_concentration - ee conc]

         :math:`methane\_ emission\  = \ (0.065\  \times gross\ energy\ conc\  \times dry\_ matter\_ intake)/0.05565`

            [A.3B.C.3]

            methane_emission = methane production (g/cow per day)

            gross energy conc = dietary gross energy concentration (MJ/kg DM)

            dry_matter_intake = dry matter intake (kg)

(3)  **Lactating Cow Manure Excretion:** Equations for manure production specific 
     to cows (adapted from Li’s pseudocode).

   a. **Manure excretion (kg/d):** Amount of feces and urine excreted daily by lactating cows (kg/d).

      **Fecal water (kg/d):** Calculate the amount of fecal water excreted (kg/d)

         :math:`fecal\_ water = 1.987 \times dry\_ matter\_ intake + 0.348 \times ADF\_ concentration - 0.412` 
               
               | :math:`\times CP\_ concentration - 0.074 \times dm\_ conc - 0.0057 \times days\_ milk` (Appuhamy et al., 2014)

            [A.3E.A.1]

            fecal water = amount of water excreted in feces (kg)

            dry_matter_intake = dry matter intake of the ration (kg)

            ADF_concentration = acid detergent fiber concentration of the diet (%)

            CP_concentration = crude protein concentration of the diet (%)

            dm conc = dry matter concentration of the diet (%)

            days milk = days in milk (days)

      **Total solids/Fecal dry matter (kg/d):** Calculate the amount of fecal 
      dry matter excreted (kg/d). Fecal dry matter is assumed to be equivalent 
      to total solids.

         :math:`fecal\ solids = - 0.576 + 0.370 \times dry\_ matter\_ intake + 0.059 \times ADF\_ concentration`

            :math:`- 0.075 \times CP\_ concentration` (Appuhamy et al., 2014)

            [A.3E.A.2]

            fecal solids = amount of dry matter excreted in feces (kg)

            dry_matter_intake = dry matter intake of the ration (kg)

            ADF_concentration = acid detergent fiber concentration of the diet (%)

            CP_concentration = crude protein concentration of the diet (%)

      **Urine (kg/d):** Calculate the amount of urine excreted (kg/d)

         :math:`urine = - 7.742 + 0.388 \times dry\_ matter\_ intake + 0.726 \times CP\_ concentration` 
            :math:`+ 2.066 \times milk\_ protein` 
         
         (Appuhamy et al., 2014)

            [A.3E.A.3]

            urine = amount of urine excreted (kg)

            dry_matter_intake = dry matter intake of the ration (kg)

            CP_concentration = crude protein concentration of the diet (%)

            milk protein = true milk protein concentration (%)

      **Manure excretion (kg/d):** Amount of feces and urine excreted daily by lactating cows (kg/d).

         :math:`manure = fecal\_ water + total\_ solids + urine` (Appuhamy et al., 2014)

            [A.3E.A.4]

            manure = amount of manure excreted (kg)

            fecal water = amount of water excreted in feces (kg)

            total solids = amount of dry matter excreted in feces (kg)

            urine = amount of urine excreted (kg)

      **Total and degradable volatile solids (kg/d):** Total and degradable volatile solids excreted by a lactating cow (kg/d).
      **Organic matter intake (kg/d):** Estimate Organic matter intake (kg/d) as a required input:

         :math:`om\ intake\  = \ dry\_ matter\_ intake\  - \ ash\ amount`

            [A.2.A.3]

            om intake = organic matter intake (kg)

            dry_matter_intake = dry matter intake (kg)

            ash amount = ash intake (kg)

      **Degradable volatile solids (kg/d)**

         :math:`degradable\_ volatile\_ solids = - 1.017 + 0.364 \times om\ intake + 0.029`
         
            | :math:`\times NDF\_ concentration - 0.023 \times CP\_ concentration` (Appuhamy et al., 2018)

            [A.3E.A.5]

            degradable volatile solids = degradable volatile solids (kg)

            om intake = organic matter matter intake (kg)

            NDF concentration = neutral detergent fiber concentration (%)

            CP_concentration = crude protein concentration (%)

      **Total volatile solids excreted by a lactating cow (kg/d)**

         :math:`total\_ volatile\_ solids = \  - 1.201 + 0.402 \times om\_ intake + 0.036 \times NDF\_ concentration`
         
            | :math:`- 0.024 \times CP\_ concentration` (Appuhamy et al., 2018)

            [A.3E.A.6]

            total volatile solids = total volatile solids (kg)

            om intake = organic matter intake (kg)

            NDF_concentration = neutral detergent fiber concentration (%)

            CP_concentration = crude protein concentration (%)

      **Non-degradable volatile solids excretion (kg/d)**

         :math:`non\_ degradable\_ volatile\_ solids = total\_ volatile\_ solids\  - degradable\_ volatile\_ solids\ `

            [A.3A.A.6]

   b. **Nutrient Excretion**

      **Manure N excretion (kg/d):** Amount of nitrogen excreted by a lactating cow (kg/d). Calculated as the sum of fecal nitrogen and urine nitrogen.

      **Total manure nitrogen (kg/d)**

         :math:`manure\_ nitrogen\  = \ (20.3\  + \ 0.654\  \times \ (dry\_ matter\_ intake\  \times \ 1000)`
         
            | :math:`\times \ \frac{CP\_ concentration/6.25}{100}) / 1000` (Reed et al., 2015)

            [A.3E.B.1]

            manure_nitrogen = amount of nitrogen excreted in manure (kg)

            dry_matter_intake = dry matter intake (kg)

            CP_concentration = concentration of crude protein in ration (%)

            Urinary nitrogen (kg/d)

         :math:`N\_ urine = (12.0\  + \ 0.333\  \times \ (dry\_ matter\_ intake\  \times \ 1000)`
         
            | :math:`\times \ \frac{CP\_ concentration/6.25}{100}) / 1000` (Reed et al., 2015)

            [A.3E.B.2]

            N urine = amount of nitrogen excreted in urine (kg)

            dry_matter_intake = dry matter intake (kg)

            CP_concentration = concentration of crude protein in ration (%)

            bw = animal weight (kg)

      **Fecal nitrogen (kg/d)**

         :math:`N\_ feces = manure\_ nitrogen\ - N\_ urine`

            [A.3B.B.3]

            manure_nitrogen = amount of nitrogen excreted in manure (kg)

            N feces = amount of nitrogen excreted in feces (kg)

            N urine = amount of nitrogen excreted in urine (kg)

      **Manure K excretion (g/d)**

         :math:`potassium\  = \ 7.21\  \times \ dry\_ matter\_ intake + 15944`
         
            | :math:`\times \ potassium\_ concentration\ /\ 100 - 164.5` (Nennich et al., 2005)

            [A.3E.B.3]

            potassium = amount of potassium excreted in manure (g)

            dry_matter_intake = dry matter intake (kg)

            potassium_concentration = Dietary potassium concentration (%)

   c. **Enteric Methane Emissions**
      Methane emissions are calculated for all animals except calves. The
      user has an input option to select which methane model they want to
      use for methane emissions calculations. Mutian (Dairy cows, US Animal Model)

      :math:`methane\_ emission\  = \  - 126\  + \ 11.3\  \times \ dry\_ matter\_ intake\  + 2.30`
      
         | :math:`\times \ NDF\_ concentration\ + 28.8\times \ milk\_ fat\  + \ 0.148\  \times \ bw`

      [A.3E.C.1]

      methane_emission = methane production (g/day)

      dry_matter_intake = dry matter intake (kg)

      NDF_concentration = dietary neutral detergent fiber concentration (% of DM)

      milk fat = milk fat concentration (%)

      BW = body weight (kg)

      Mills (used by the CNCPS and IFSM)

      Mills et al. (2003) parameterized Mitscherlich equations for a
      nonlinear model of methane emissions. The CNCPS and IFSM models use
      the Mitscherlich 3 equation.

      :math:`methane\_ emission\  = (45.98\  - \ 45.98\  \times exp( - \lbrack( - 0.0011 \times \frac{starch\_ conc}{ADF\_ concentration})\  + \ 0.0045\rbrack`
      
         | :math:`\times \ me\_ intake\  \times 4.184)) / 0.05565`

         [A.3E.C.2]

         methane_emission = methane production (g/d)

         starch conc = starch concentration (% DM)

         ADF_concentration = acid detergent fiber concentration (% DM)

         ME intake = metabolizable energy intake (Mcal/kg DM)

         IPCC Tier 2 (2006)

      The Tier 2 system of the IPCC relates methane emissions to gross
      energy intake by a conversion factor, Ym (= 0.065). Gross energy in
      the diet is calculated from diet nutrient composition (Moraes et al.
      2014).

      :math:`gross\ energy\ conc\  = \ 0.263\  \times CP\_ concentration\  + \ 0.522\  \times ee\ conc\  + \ 0.198`
      
         | :math:`\times NDF\_ concentration\  + \ 0.160\  \times soluble\ residue`

         [A.3B.C.2]

         gross energy conc = dietary gross energy concentration (MJ/kg DM)

         CP_concentration = crude protein concentration (% DM)

         ee con = ether extract concentration (or crude fat, % DM)

         NDF_concentration = neutral detergent fiber concentration (% DM)

         soluble residue = dietary percentage of soluble residues [% DM, = (100 - ASH_concentration) - NDF_concentration - cp conc - ee conc]

      :math:`methane\_ emission\  = \ (0.065\  \times gross\ energy\ conc\  \times dry\_ matter\_ intake)/0.05565`

         [A.3B.C.3]

         methane_emission = methane production (g/cow per day)

         gross energy conc = dietary gross energy concentration (MJ/kg DM)

         dry_matter_intake = dry matter intake (kg)

(4) **Dry Cow Manure Excretion:** Equations for manure production specific to dry cows.
   
   a. **Manure excretion (kg/d)**

      **Urine excretion (kg/d):** Amount of urine excreted in kg with assumption that 1.038 kg urine is
      approximately 1 L. Due to lack of information, average excretion rate
      from dry cows is assumed.

         :math:`urine = 15.4` [(Nennich et al., 2005), Table 5]

            [A.3F.A.1]

            urine = amount of urine excreted (kg)

      **Manure excretion (kg/d):** Amount of feces and urine excreted daily by dry cows (kg/d).

         :math:`total_manure_excreted = 0.00711\  \times \ body\_ weight + 0.324\  \times \ CP\_ concentration`  
         
               | :math:`+ \ 0.259\  \times \ NDF\_ concentration\  + \ 8.05` 
         
         (Wilkerson et al., 1997; Nennich et al., 2005; NASEM, 2021) 
          
           [A.3F.A.2]

            total_manure_excreted = amount of manure excreted (kg)

            body_weight = animal weight (kg)

            CP_concentration = crude protein (% DM)

            NDF_concentration = neutral detergent fiber (% DM)

      **Total solids excretion (kg/d):** Amount of dry material excreted by dry cows (kg/d). The same equation is applied for heifers.

         :math:`total\_ solids = 0.178 \times dry\_ matter\_ intake + 2.733` (ASABE, 2005)

            [A.3F.A.3]

            total solids = amount of total solids excreted (kg)

            dry_matter_intake = dry matter intake (kg)

      **Total and degradable volatile solids (kg/d)**

         - Amount of total and degradable volatile solids excreted by dry cows (kg/d).
         - Equations for lactating cows (Appuhamy et al., 2018) are used for dry
           cows because the range of intake covers that is typically seen in dry cows.

      **Organic matter intake (kg/d):** Estimate Organic matter intake (kg/d) as a required input:

         :math:`om\ intake\  = \ dry\_ matter\_ intake\  - \ ash\ amount`

            [A.2.A.3]

            om intake = organic matter intake (kg)

            dry_matter_intake = dry matter intake (kg)

            ash amount = ash intake (kg)

      **Degradable volatile solids (kg/d)**

         :math:`degradable\_ volatile\_ solids = - 1.017 + 0.364 \times om\ intake + 0.029`
         
            | :math:`\times NDF\_ concentration - 0.023 \times CP\_ concentration` (Appuhamy et al., 2018)

            [A.3E.A.5]

            degradable volatile solids = degradable volatile solids (kg)

            om intake = organic matter matter intake (kg)

            NDF_concentration = neutral detergent fiber concentration (%)

            CP_concentration = crude protein concentration (%)

      **Total volatile solids (kg/d)**

         :math:`total\_ volatile\_ solids = \  - 1.201 + 0.402 \times om\_ intake + 0.036`
         
            | :math:`\times NDF\_ concentration - 0.024 \times CP\_ concentration` (Appuhamy et al., 2018)

            [A.3E.A.6]

            total volatile solids = total volatile solids (kg)

            om intake = organic matter intake (kg)

            NDF_concentration = neutral detergent fiber concentration (%)

            CP_concentration = crude protein concentration (%)

      **Non-degradable volatile solids excretion (kg/d)**

         :math:`non\_ degradable\_ volatile\_ solids = total\_ volatile\_ solids\  - degradable\_ volatile\_ solids\ `

            [A.3A.A.6]

   b. **Nutrient Excretion**

      **Manure N excretion (kg/d):** Amount of nitrogen excreted by a dry cow (kg/d). This is the same
      equation used for heifers.

         :math:`manure\_ nitrogen\ = (15.1 + 0.83\  \times \ \ (dry\_ matter\_ intake\  \times \ 1000)`
            :math:`\times \ \frac{CP\_ concentration/6.25}{100})\ /\ 1000` 
         
         (Reed et al., 2015; Johnson et al., 2016; NASEM, 2021)

            [A.3B.B.1]

            manure_nitrogen = amount of nitrogen excreted in manure (kg)

            dry_matter_intake = dry matter intake (kg)

            CP_concentration = concentration of crude protein in ration (%)

      **Urine N excretion (kg/d):** Amount of urine nitrogen excreted by a dry cow (kg/d).

         :math:`N\_ urine = (14.3 + 0.510 \times \ (dry\_ matter\_ intake\  \times \ 1000)`
            :math:`\times \ \frac{CP\_ concentration/6.25}{100})\ /\ 1000` 
         
         (Reed et al., 2015)

            [A.3B.B.2]

            N urine = amount of nitrogen excreted in manure (kg)

            dry_matter_intake = dry matter intake (kg)

            CP_concentration = concentration of crude protein in ration (%)

      **Fecal N excretion (kg/d):** Amount of fecal nitrogen excreted by a dry cow (kg/d)

         :math:`N\_ feces\  = \ manure\_ nitrogen\  - \ N\_ urine`

            [A.3B.B.3]

            N feces = amount of nitrogen excreted in feces (kg/d)

      **Manure K excretion (g/d)**

      **Amount of potassium excreted by a dry cow (g/d).**

         :math:`potassium = 1000\  \times \ dry\_ matter\_ intake \times \ \frac{potassium\_ concentration}{100}` (ASABE, 2005)

            [A.3B.B.4]

            potassium = amount of potassium excreted in manure (g)

            dry_matter_intake = dry matter intake (kg)

            potassium_concentration = concentration of potassium in ration (%)

   c. **Enteric Methane Emissions**

      Methane emissions are calculated for all animals. The user has an
      input option to select which methane model they want to use for
      methane emissions calculations.

      Mills (used by the CNCPS and IFSM).

      Mills et al. (2003) parameterized Mitscherlich equations for a
      nonlinear model of methane emissions. The CNCPS and IFSM models use
      the Mitscherlich 3 equation.


      :math:`methane\_ emission\  = (45.98\  - \ 45.98\  \times exp( - \lbrack( - 0.0011 \times \frac{starch\_ conc}{ADF\_ concentration})\  + \ 0.0045\rbrack`

         | :math:`\times \ me\_ intake\  \times 4.184))/0.05565`


      [A.3E.C.2]

         methane_emission = methane production (g/d)

         starch_conc = starch concentration (% DM)

         ADF_concentration = acid detergent fiber concentration (% DM)

         ME intake = metabolizable energy intake (Mcal/kg DM)

         IPCC Tier 2 (2006)

      The Tier 2 system of the IPCC relates methane emissions to gross
      energy intake by a conversion factor, Ym (= 0.065).

      Gross energy in the diet is calculated from diet nutrient composition (Moraes et al. 2014).

      :math:`gross\ energy\ conc\  = \ 0.263\  \times CP\_ concentration\  + \ 0.522 \times EE\ conc\  + \ 0.198` 
         
         | :math:`\times NDF\_ concentration + \ 0.160 \times soluble\ residue`   

      [A.3B.C.2]

         gross energy conc = dietary gross energy concentration (MJ/kg DM)

         CP_concentration = crude protein concentration (% DM)

         ee con = ether extract concentration (or crude fat, % DM)

         NDF_concentration = neutral detergent fiber concentration (% DM)

         soluble residue = dietary percentage of soluble residues [% DM, = (100 - ASH_concentration) - NDF_concentration - CP_concentration - ee conc]

      :math:`methane\_ emission\  = \ (0.065\  \times gross\ energy\ conc\  \times dry\_ matter\_ intake)/0.05565`

         [A.3B.C.3]

         methane_emission = methane production (g/cow per day)

         gross energy conc = dietary gross energy concentration (MJ/kg DM)

         dry_matter_intake = dry matter intake (kg)

(5) **General Manure Excretion**

   a. **Manure Dry Matter Concentration**

      **Dry matter concentration of manure (%)**

         :math:`dm\_ conc\_ manure = \frac{total\_ solids}{manure} \times 100`
            [A.3G.A.1]

            dm conc manure = manure dry matter concentration (%)

            manure = amount of manure excreted (kg)

            total solids = amount of total solids excreted (kg)

   b. **Urinary Urea N and total ammoniacal N**

      The concentration of urinary urea N and total ammoniacal N are
      derived from a pair of JDS papers by de Boer (2002) and Monteny
      (2002). The estimates are based on a regression relationship between
      urinary urea N concentration (g/L) and total urinary N concentration
      (g N/kg). This relationship between total ammoniacal N and urinary
      urea N concentration is valid when urinary urea N concentration is
      between 2 and 12 g/L based on Monteny (2002). Thus, in this version
      of RuFaS, when urinary urea N concentration is lower than 2 g/L,
      urinary urea N concentration is assumed to be 2 g/L for this
      relationship to be effective. Likewise, when urinary urea N
      concentration goes above 12 g/L, urinary urea N concentration is
      assumed to be 12 g/L. For calves specifically, total ammoniacal
      nitrogen concentration is assumed to be a constant of 0.14 in this
      version of RuFaS. Note that a key assumption is that 1.038 kg of
      urine = 1 L of urine.

      **Urinary N concentration (g N/kg), N_urine in kg , urine in kg**

         :math:`urinary\_ N\_ conc\  = \ (N\_ urine\ *1000\ )/urine`

            [A.3G.B.1]

      **Urinary urea concentration (g N/L)**

         :math:`urine\_ urea\_ nitrogen\_ concentration\  = \  - 1.16\  + \ 0.86*urinary\_ N\_ conc`

            [A.3G.B.2]
      **Total ammoniacal N (:math:`{NH}_{3}`-N) in the slurry top layer as a
      percentage of UUC (%)**

         :math:`tan\_ percent\_ of\_ urea\  = \ 48.2\  - \ 2.9\ *\ urine\_ urea\_ N\_ conc`

            [A.3G.B.3]

      **Total ammoniacal N (:math:`{NH}_{3}`-N) concentration (g N/L) in the
      manure:**

         :math:`total\_ ammonical\_ n\_ conc\  = (\ tan\_ percent\_ of\_ urea/100)*urine\_ urea\_ N\_ conc`

            [A.3G.B.4]

**References**

Appuhamy, J. A. D. R. N., L. E. Moraes, C. Wagner-Riddle, D. P. Casper,
   J.France, and E. Kebreab. 2014. Development of mathematical models to
   predict volume and nutrient composition of fresh manure from lactating
   Holstein cows. Animal Production Science 54(12).

Appuhamy, J. A. D. R. N., Moraes, L. E., Wagner-Riddle, C., Casper, D.
   P., & Kebreab, E. (2018). Predicting manure volatile solid output of
   lactating dairy cows. Journal of dairy science, 101(1), 820-829.

ASABE. 2005. Manure Production and Characteristics. Pages 1-32. ASABE,
   ed. ASABE, St. Joseph, MN.

A.Bannink, H. Valk, A.M. Van Vuuren. Intake and excretion of sodium,
   potassium, and nitrogen and the effects on urine production by lactating
   dairy cows. Journal of Dairy Science, 82 (1999), pp. 1008-1018

D.Boadi, C. Benchaar, J. Chiquette, and D. Massé. Mitigation strategies
   to reduce enteric methane emissions from dairy cows: Update review.
   *Canadian Journal of Animal Science*. **84**\ (3): 319-335.
   https://doi.org/10.4141/A03-109

de Boer IJ, Smits MC, Mollenhorst H, van Duinkerken G, Monteny GJ.
   Prediction of ammonia emission from dairy barns using feed
   characteristics part 1: Relation between feed characteristics and
   urinary urea concentration. J Dairy Sci. 2002 Dec;85(12):3382-8. doi:
   10.3168/jds.s0022-0302(02)74425-1. PMID: 12512610.

Johnson ACB, Reed KF, Kebreab E. Short communication: Evaluation of
   nitrogen excretion equations from cattle. J Dairy Sci. 2016
   Sep;99(9):7669-7678. doi: 10.3168/jds.2015-10730. Epub 2016 Jun 16.
   PMID: 27320670.

J.A. N. Mills, E. Kebreab, C. M. Yates, L. A. Crompton, S. B. Cammell,
   M.S. Dhanoa, R. E. Agnew, J. France, Alternative approaches to
   predicting methane emissions from dairy cows, *Journal of Animal
   Science*, Volume 81, Issue 12, December 2003, Pages 3141–3150,
   https://doi.org/10.2527/2003.81123141x

Moraes, L.E., Strathe, A.B., Fadel, J.G., Casper, D.P. and Kebreab, E.
   (2014), Prediction of enteric methane emissions from cattle. Glob Change
   Biol, 20: 2140-2148. https://doi.org/10.1111/gcb.12471

Monteny GJ, Smits MC, van Duinkerken G, Mollenhorst H, de Boer IJ.
   Prediction of ammonia emission from dairy barns using feed
   characteristics part II: Relation between urinary urea concentration and
   ammonia emission. J Dairy Sci. 2002 Dec;85(12):3389-94. doi:
   10.3168/jds.S0022-0302(02)74426-3. PMID: 12512611.

Nennich TD, Harrison JH, VanWieringen LM, Meyer D, Heinrichs AJ, Weiss
   WP, St-Pierre NR, Kincaid RL, Davidson DL, Block E. Prediction of manure
   and nutrient excretion from dairy cattle. J Dairy Sci. 2005
   Oct;88(10):3721-33. doi: 10.3168/jds.S0022-0302(05)73058-7. PMID:16162547.

Niu, M, Kebreab, E, Hristov, AN, et al. Prediction of enteric methane
   production, yield, and intensity in dairy cattle using an
   intercontinental database. *Glob Change Biol*. 2018; 24: 3368– 3389.
   https://doi.org/10.1111/gcb.14094

Reed, K. F., Moraes, L. E., Casper, D. P., & Kebreab, E. (2015).
   Predicting nitrogen excretion from cattle. Journal of dairy science,
   98(5), 3025-3035.
