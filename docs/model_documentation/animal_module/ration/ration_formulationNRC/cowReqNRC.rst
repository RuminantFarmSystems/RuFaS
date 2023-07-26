.. _dairy-cattle-requirements :

Dairy Cattle Ration (Lactation and Dry Cows)
===========================================

**# of Subroutine and Name:** Description of equations used to calculate
nutrient requirements of cows.

**Flow of Information:**

A. Nutrient requirements including energy, protein, mineral (Ca and P)
   and several other requirements (NDF, forage NDF, fat) are
   considered.

B. Energy supply, protein supply and mineral supply from feeds are
   calculated.

C. Supply >= requirements when formulating diet.

D. All the equations are calculated on a daily basis

Arguments

-  Animal inputs

   i.    BW: Body weight (kg)

   ii.   MW: Mature body weight(kg)

   iii.  Housing: Housing type (Barn or Grazing)

   iv.   Topography (Flat or Hilly)

   v.    Distance: Daily walking distance (km)

   vi.   DOP: Days of pregnancy (d)

   vii.  Parity: Number of parity

   viii. TP_Milk: Milk true protein content, % of milk

   ix.   Fat_Milk: Milk fat content, % of milk

   x.    Lactose_Milk: Milk lactose content, % of milk

   xi.   Milk: Milk production, kg

   xii.  DIM: Days in milk

   xiii. CI: Calving interval, d

\*Note: Milk relative inputs are set to 0 for dry cows

-  Feed inputs (from the feed table, variables with \* are not used in
   any equations yet)

   i.      TDN: Total digestible nutrient (% of DM)

   ii.     Type: Feed type (Forage, Concentrate, or Mineral)

   iii.    \*PAF: Processing adjustment factor (not used)

   iv.     DE: Digestible energy (standard value, Mcal/kg)

   v.      ME: Metabolizable energy (standard value, Mcal/kg)

   vi.     NEL: Net energy for lactation (standard value, Mcal/kg)

   vii.    NEM: Net energy for maintenance (standard value, Mcal/kg)

   viii.   NEG: Net energy for growth (standard value, Mcal/kg)

   ix.     \*DM: Dry matter (% of as-fed basis, not used)

   x.      CP: Crude protein (% of DM)

   xi.     \*NDICP: Neutral detergent insoluble crude protein (% of DM,
           not used)

   xii.    \*ADICP: Acid detergent insoluble crude protein (% of DM, not
           used)

   xiii.   EE: Ether extract, i.e., crude fat (% of DM)

   xiv.    NDF: Neutral detergent fiber (% of DM)

   xv.     \*ADF: Acid detergent fiber (% of DM, not used)

   xvi.    \*Lignin (% of DM, not used)

   xvii.   \*Ash (% of DM, not used)

   xviii.  N_A: Fraction A of protein, soluble protein, degraded
           immediately in rumen (% of CP)

   xix.    N_B: Fraction B of protein, potentially degradable protein,
           require time to generally degrade in rumen (% of CP)

   xx.     N_C: Fraction C of protein, not degradable in rumen (% of CP)

   xxi.    Kd: Rumen protein degradation rate (%/h)

   xxii.   \*eRUP: Example rumen undegradable protein (% of CP, not
           used)

   xxiii.  dRUP: RUP degradability (% of RUP)

   xxiv.   Ca: Calcium content (% of DM)

   xxv.    P: Phosphorous content (% of DM)

   xxvi.   \*Other minerals (Mg, K, Na, etc. are not considered yet)

   xxvii.  Is_fat: If the feed is fat supplement or not (yes = 1; no = 0)

   xxviii. Is_wetforage: If the feed is wet forage or not (yes = 1; no = 0)

   xxix.   \*peNDF: Physically effective NDF (proportion of NDF)

   xxx.    Cost: Feed cost ($/kg of DM)

-  Outputs

i. 

Dry matter intake (kgDM/day)

A. **Energy Requirements**

..

   Energy requirement is divided into 5 components: maintenance,
   activity, growth, pregnancy and lactation (all in net energy, Mcal).

   **1.** **Maintenance requirement**

   Maintenance requirement is calculated based on metabolic body weight
   (body weight\ :sup:`0.75`).

+-------------------------------+-------------+
| :math:`CBW = MW*0.06275`      | [A.Cow.A.1] |
+-------------------------------+-------------+

..

   CBW = Calf birth weight (kg)

   MW = Mature body weight (kg), default = 682 kg for Holstein
+-------------+---------------------------------------------------------------+------------+
| :math:`CW =`| :math:`(18 +(DOP- 190)*0.665)*(\frac{CBW}{45}),if\ DOP > 190;`| [A.Cow.A.2]|
+-------------+---------------------------------------------------------------+------------+
|             | :math:`0,\ otherwise`                                         |            |
+-------------+---------------------------------------------------------------+------------+

   CW = Conceptus weight (kg)

   DOP = Days of pregnancy

+--------------------------------------------------+------------------+
|    :math:`NEmaint = ((0.08*(BW - CW))^{0.75}`    | [A.Cow.A.3]      |
+--------------------------------------------------+------------------+

..

   NEmaint = Net energy for maintenance requirement, Mcal

   **2. Activity requirement**

   Activity requirement is proportional to body weight and daily walking
   distance. Grazing system and hilly topography will cost additional
   energy.

+------------------------+----------------------------------+------------+
|    :math:`NEa1\  =`    | :math:`0.0012*                   | [A.Cow.A.4]|
|                        | BW,\ if\ Housing = Grazing;\ \ ` |            |
|                        | :math:`0,\ otherwise\ `          |            |
+------------------------+----------------------------------+------------+

..

   NEa1 = Net energy for activity requirement caused by grazing system,
   Mcal

**The value shown below calculates the net energy for activity required
when the**

   **topography of farmland is hilly. Currently, the model does not
   support hilly topography as an input, thus, it should be noted that
   this value is unused and is not found within the model’s code.**

+------------------------+-----------------------------------+------------+
|    :math:`NEa2\  =`    | :math:`0.006*BW                   | [A.Cow.A.5]|
|                        | ,\ if\ Topography = Hilly;\ \ \ ` |            |
+------------------------+-----------------------------------+------------+
|                        | :math:`0,\ otherwise`             |            |
+------------------------+-----------------------------------+------------+

..

   NEa2 = Net energy for activity requirement caused by hilly
   topography, Mcal

+------------------------+------------------------------------+-------------+
|    :math:`NEa\  =`     | :math:`Di                          | [A.Cow.A.6] |
|                        | stance*0.00045*BW + NEa1 + NEa2\ ` |             |
+------------------------+------------------------------------+-------------+

..

   NEa = Total net energy for activity requirement, Mcal

   Distance = Daily walking distance, km

   **3. Growth requirement**

+------------------------+-----------------------------------+-------------+
|    :math:`MSBW = \  =` | :math:`0.96*MW\ `                 | [A.Cow.A.7] |
+------------------------+-----------------------------------+-------------+

..

   MSBW = Mature shrunk body weight, kg

+-----------------------+------------------------------------+-------------+
|    :math:`SBW\  =`    | :math:`0.96*BW\ `                  | [A.Cow.A.8] |
+-----------------------+------------------------------------+-------------+

..

   SBW = Shrunk body weight, kg

   **The value shown below was calculated, but was never utilized in any
   further calculations in the model’s current version. Thus, it has
   been omitted within the model and remains solely as a reference to
   past versions of the model.**

+----------------------------------------------------------+-------------+
|    :math:`EBW = 0.891*SBW`                               | [A.Cow.A.9] |
+----------------------------------------------------------+-------------+

..

   EBW = Empty body weight, kg

+----------------------------------------------------------+--------------+
|    :math:`EQSBW = (SBW - CW)*\frac{478}{MSBW}`           |  [A.Cow.A.10]|
+----------------------------------------------------------+--------------+

..

   EQSBW = Equivalent shrunk body weight, kg

+----------------------------------------------------------+-----------------+
| :math:`ADG =`                                            |    [A.Cow.A.11] |
| :math:`\frac{(0.92 - 0.82)*MSBW}{CI},\ if\ Parity\  = 1;`|                 |
+----------------------------------------------------------+-----------------+
| :math:`\frac{(1 - 0.92)*MSBW}{CI},\ if\ Parity\  = 2.0;` |                 |
+----------------------------------------------------------+-----------------+
| :math:`0,\ if\ Parity > 2`                               |                 |
+----------------------------------------------------------+-----------------+

   ADG = Average daily gain, kg

   CI = Calving interval, d

+------------------------------------+--------------+
|    :math:`EQEBG = 0.956*ADG`       | [A.Cow.A.12] |
+------------------------------------+--------------+

..

   EQEBG = Equivalent empty weight gain, kg

+----------------------------------------------------------+-------------+
|    :math:`EQEBW = 0.891*EQSBW`                           | [A.Cow.A.13]|
+----------------------------------------------------------+-------------+

..

   EQEBW = Equivalent shrunk body weight, kg
+---------+----------------------------------------------+-------------+
| NEg =   | :math:`{0.0635*EQSBW}^{0.75}*{EQEBG}^{1.097}`| [A.Cow.A.14]|
+---------+----------------------------------------------+-------------+


   NEg = Net energy for growth requirement, Mcal

**4. Pregnancy requirement**

+---------------------------------------------------------+--------------+
|    :math:`MEPreg\ \  =`                                 | [A.Cow.A.15] |
|    :math:`2*0.00159*DOP - 0.0352)*CBW/(45*0.14),\ `     |              |
|    :math:`if\ DOP > 190:0,\ otherwise`                  |              |  
+---------------------------------------------------------+--------------+

..

   MEPreg = Metabolizable energy requirement for pregnancy, Mcal

+----------------------+----------------------------------+-------------+
|    :math:`NEPreg\ =` | :math:`MEPreg*0.64`              |[A.Cow.A.16] |
+----------------------+----------------------------------+-------------+

..

   NEPreg = Net energy requirement for pregnancy, Mcal

**5. Lactation requirement**

+-----------------+-----------------------------------------+--------------+
| :math:`MilkEn =`| :math:`(0.0929 * Fat\_ Milk + 0.0547/0.9| [A.Cow.A.17] |
|                 | 3 * TP\_ Milk + 0.0395 * Lact\_ Milk)`  |              |
+-----------------+-----------------------------------------+--------------+

+---------------------+-----------------------------------+-------------+
|   :math:`NElact =`\ | :math:`MilkEn*Milk`               |[A.Cow.A.18] |
+---------------------+-----------------------------------+-------------+


   NElact = Net energy requirement for lactation, Mcal

B. **Protein requirements**

..

   Protein requirement is divided into 4 components: maintenance,
   growth, pregnancy and lactation (all in metabolizable protein, g.

1. **Maintenance requirement**

+----------------------------------------------------+
| :math:`0.3*(BW - CW)^{0.6} + 4.1*(BW - CW)^{0.5}   |
| + (DMI*1000*0.03 - 0.5*(\frac{MPbact}{0.68}        |
| - MPbact)) + 0.4*11.8*\frac{DMI}{0.67}`            |
+----------------------------------------------------+

   MPm = Metabolizable protein requirement for maintenance, g

   MPbact = Bacteria metabolizable protein production, g

2. **Growth requirement**

+------------------------+------------------------------------+-------------+
|    :math:`NPg\  =`     | :math:`0,\ if\ ADG = 0;\ \ `       | [A.Cow.B.2] |
|                        | :math:`A                           |             |
|                        | DG*(268 - 29.4*\frac{NEg}{ADG})\ ` |             |
+------------------------+------------------------------------+-------------+

..

   NPg = Net protein requirement for growth, g

+---------------------------+---------------------------------+-------------+
|                           | :math:`\frac{(8                 | [A.Cow.B.3] |
|   :math:`EffMP\_ NPg\  =` | 3.4 - 0.114*EQSBW)}{1           |             |
|                           | 00}\ if\ EQSBW\  \leq \ 478;\ ` |             |
|                           | :math:`0.28908,otherwise`       |             |
+---------------------------+---------------------------------+-------------+

..

   EffMP_NPg = Efficiency of converting metabolizable protein to net
   protein

+------------------------+-----------------------------------+-------------+
|    :math:`MPg\  =`     | :math:`\frac{NPg}{EffMP\_ NPg}\ ` | [A.Cow.B.4] |
+------------------------+-----------------------------------+-------------+

..

   MPg = Metabolizable protein requirement for growth, g

3. **Pregnancy requirement**

+----------------------+-----------------------------------+-------------+
|    :math:`MPpreg =`  | :math:`(0.69*DOP - 69.2)*\frac{CBW| [A.Cow.B.5] |
|                      | }{45*0.33}\ if\ DOP > 190;\ \ `   |             |
|                      | :math:`\ 0,\ othe`\ rwise         |             |
+----------------------+-----------------------------------+-------------+

..

   MPpreg = Metabolizable protein requirement for pregnancy, g

4. **Lactation requirement**

+------------------------+------------------------------------+------------+
|    :math:`MPlact\  =`  | :math:`Milk*\frac{                 | [A.Cow.B.6]|
|                        | TP_{Milk}}{100}*\frac{1000}{0.67}` |            |
+------------------------+------------------------------------+------------+

..

   MPlact = Metabolizable protein requirement for lactation, g

5. **Total requirement**

+------------------------+------------------------------------+-------------+
|    :math:`MPreq\  =`   |:math:`MPm + MPg + MPpreg + MPlact` | [A.Cow.B.7] |
+------------------------+------------------------------------+-------------+

..

   MPreq = Metabolizable protein requirement, g

C. **Mineral requirements**

..

   Only calcium and phosphorus requirements are considered currently.

1. **Calcium requirement**

+----------------------+----------------------------------+-------------+
| :math:`Ca_{main}\  =`| :math:`0.031*BW + 0.08           | [A.Cow.C.1] |
|                      | *BW/100,\ for\ lactating\ cows`; |             |
+----------------------+----------------------------------+-------------+
|                      | :math:`0.0154*BW                 |             |
|                      | + 0.08*BW/100,\ for\ dry\ cows`  |             |
|                      |                                  |             |
+----------------------+----------------------------------+-------------+

..

   Ca\ :sub:`main` = Calcium maintenance requirement, g/day

+--------------------------+-------------------------------------------+------------+
|    :math:`Ca_{growth} =` | :math:`9                                  |[A.Cow.C.2] |
|                          | .83*MW - 0.22*BW - 0.22*\frac{ADG}{0.96}` |            |
+--------------------------+-------------------------------------------+------------+

..

   Ca\ :sub:`growth` = Calcium growth requirement, g/day

+---------------------+---------------------------------------------------+------------+
|:math:`Ca_{preg}\  =`| :math:`0.02456*exp((0.05581-0.00007*DOP)*DOP)     | [A.Cow.C3] |
|                     | -0.02456*exp(0.05581-0.00007*(DOP-1)* (DOP - 1)), |            |
|                     | if DOP>190;`                                      |            |
+---------------------+---------------------------------------------------+------------+
|                     | :math:`\ if\ DOP > 190;\ `                        |            |
+---------------------+---------------------------------------------------+------------+
|                     | :math:`0,\ otherwise`                             |            |
+---------------------+---------------------------------------------------+------------+

..

   Ca\ :sub:`preg` = Calcium pregnancy requirement, g/day

+-----------------------+----------------------------+--------------+
|   :math:`Ca_{lact} =` | :math:`1.22*Milk`          | [A.Cow.C.4]  |
+-----------------------+----------------------------+--------------+

..

   Ca\ :sub:`lact` = Calcium lactation requirement, g/day

+-----------------------+------------------------------------+--------------+
|    :math:`Ca_{req} =` | :math:`Ca_{main} + Ca              | [A.Cow.C.5]  |
|                       | _{growth} + Ca_{preg} + Ca_{lact}` |              |
+-----------------------+------------------------------------+--------------+

..

   Ca\ :sub:`req` = Total calcium requirement, g/day

2. **Phosphorus requirement**

+------------------+--------------------------------------------------+--------------+
| :math:`Pmain =`\ | :math:`1*DMI + 0.002*BW,\ for\ lactating\ cows;` | [A.Cow.C.6]  |
+------------------+--------------------------------------------------+--------------+
|                  | :math:`0.8*DMI + 0.002*BW,\ for\ dry\ cows`      |              |
+------------------+--------------------------------------------------+--------------+

   P\ :sub:`main` = Phosphorus maintenance requirement, g/day

+----------------------+-------------------------------------------------------------+-------------+
| :math:`P_{growth} =` |:math:`( 1.2 + 4.635*MW^{0.22}*BW^{- 0.22})*\frac{ADG}{0.96}`| [A.Cow.C.7] |
+----------------------+-------------------------------------------------------------+-------------+

   P\ :sub:`growth` = Phosphorus growth requirement, g

+---------------------+-----------------------------------+------------+
|    :math:`Ppreg =`  | :math:`(0.02743*exp(( 0.0 5527 -  | [A.Cow.C.8]|   
|                     | 0.00007)*DOP)*DOP)- 0.02743*exp(( |            |
|                     | 0.05527 - 0.000075*(DGest-1))*(BW |            |
|                     | /715) * (*DOP - 1))`              |            |
|                     | :math:`if\ DOP > 190;`            |            |
+---------------------+-----------------------------------+------------+
|                     | :math:`0,\ otherwise\ `           |            |
+---------------------+-----------------------------------+------------+

..

   P\ :sub:`preg` = Phosphorus pregnancy requirement, g

+-----------------------+-------------------------------+-------------+
|    :math:`P_{lact} =` | :math:`0.90*Milk\ `           | [A.Cow.C.9] |
+-----------------------+-------------------------------+-------------+

..

   Plact= Phosphorus lactation requirement, g

   P\ :sub:`lact` = Phosphorus lactation requirement, g/d

+--------------------------+-----------------------------------------------------+---------------+
|:math:`P_{absorb\_ req} =`| :math:`P_{main} + P_{growth} + P_{preg} + P_{lact}` | [A.Cow.C.10]  |
+--------------------------+-----------------------------------------------------+---------------+

..

   P\ :sub:`absorb_req` = Total requirement for absorbed phosphorus,
   g/day

+----------+-----------------------------------+--------------+
|P_{req} = | :math:`P_{absorb\_ req}/0.90\ `   |  [A.Cow.C.11]|        
|          | if class = calf                   |              |
+----------+-----------------------------------+--------------+
|          | :math:`P_{absorb\_ req}/0.664\ `  |              |
|          | if class = heifer, dry            |              |
+----------+-----------------------------------+--------------+
|          | :math:`P_{absorb\_ req\ }/        |              |  
|          | (1.86696 - 5.01238*P_{ration\_ co |              |
|          | nc}+5.12286*P_{ration\_ conc}^{2})|              |
|          | if class = lactating cow          |              |
+----------+-----------------------------------+--------------+

..

   P\ :sub:`req` = Total requirement for phosphorus, g/day

   P\ :sub:`ration_conc` = ration concentration of phosphorus g P/g DM

D. **Dry matter intake estimation**

Dry matter intake estimation is different for lactating cow and dry cow.

The sum of dry matter intake of each feed is assumed to be less than dry
matter intake estimation

(:math:`\sum_{i} Feed_{i} < DMIest`).

+--------------------------------------------------------+-------------+
| :math:`FCM = (0.4*Milk) + ((15*\ Fat\ Milk*Milk))/100` | [A.Cow.D.1] |
+--------------------------------------------------------+-------------+

FCM = Fat corrected milk

+-----------------+---------------------------------------------------+------------+
| :math:`DMIEst =`| :math:`(0.372*FCM + 0.0968*BW\hat{}0.75)*(1 - exp(| [A.Cow.D.2]|
|                 | - 0.192*(WOL + 3.67))),\ for\ lactating\ cows;`   |            |
+-----------------+---------------------------------------------------+------------+
|                 | :math:`((1.97 - 0.75*exp(0.16*DOP - 280)))/100*B  |            |
|                 | W,\ for\ dry\ cows`                               |            |
+-----------------+---------------------------------------------------+------------+
DMIest = Dry matter intake estimation, kg

   WOL = Week of lactation, which is the integer part of days in milk
   (DIM) divided by 7

   DOP = Days of pregnancy

E. **Other requirements**

..

   1. Minimum dietary NDF content: 25%

   2. Maximum dietary NDF content: 40%

   3. Minimum dietary forage NDF content: 19%

   4. Maximum dietary fat content: 7%

F. **Feed nutrient supply**

1. **Energy supply**

Energy supply from the feed include NEm, NEl and NEg. NEm provides
energy for maintenance and activity requirement, NEl provides energy for
lactation and pregnancy, and NEg provides energy for growth. Feed actual
energy contents are corrected from standard values provided by NRC
(2001). Minerals do not provide any energy.

+-------------------------+----------------------------------+------------+
|    :math:`TDNconc =`    | :math:`\frac{TotalTDN}{DMI}*100` | [A.Cow.F.1]|
+-------------------------+----------------------------------+------------+

..

   TDNconc = TDN concentration, %

   TotalTDN = Dietary TDN content (calculate using standard value in NRC
   (2001))

+--------------------------+-------------------------------+------------+
|                          | :math:`1,\ if\ TotalTDN\      | [A.Cow.F.2]|
|:math:`DMI\_ to\_ maint =`| < 0.035*BW^{0.75}`            |            |
+--------------------------+-------------------------------+------------+
|                          | :math:`\frac{TotalTDN}{0.035*S|            |
|                          | BW^{0.75}}` , otherwise       |            |
+--------------------------+-------------------------------+------------+

..

   DMI_to_maint = The amount of intake needed to meet the maintenance
   requirement, dimensionless

+------------------------+------------------------------------+-------------+
|    :math:`Discount =`  | :math:`1, if TDNconc < 60;`        | [A.Cow.F.3] |
+------------------------+------------------------------------+-------------+
|                        | :math:`\frac{ TDNconc - (0.18 * TD |             |
|                        | Nconc - 10.3) * (DMI\_{to_{maint}} |             |
|                        | - 1) }{ TDNconc }, otherwise\ `    |             |
+------------------------+------------------------------------+-------------+

..

   Discount = TDN discount, TDN digestibility decrease caused by DMI and
   TDNconc

+------------------------+------------------------------------+-------------+
| :math:`{TDNact}_{i} =` | :math:`TDN_{i}*Discount`           | [A.Cow.F.4] |
+------------------------+------------------------------------+-------------+

..

   TDNact\ :sub:`i` = Actual TDN content of feed i, %

   TDN\ :sub:`i` = Standard TDN content of feed i, %

+------------------------+------------------------------------+--------------+
| :math:`{DEact}_{i} =`  | :math:`DE_{i}*Discount`            | [A.Co w.F.4] |
+------------------------+------------------------------------+--------------+

..

   DEact\ :sub:`i` = Actual digestible energy of feed i, Mcal/kg

   DE\ :sub:`i` = Standard DE feed i, Mcal/kg

+-----------------------+-------------------------------------+------------+
| :math:`{MEact}_{i} =` | :math:`1.01*DEact_{i} - 0.45 + 0.0  | [A.Cow.F.5]|
|                       | 046*\left( EE_{i} - 3 \right),\ `   |            |
|                       | :math:`if\ feed\ type\ is\ not\     |            |
|                       | fat\ and\ fat\ content\ \leq \ 3\%;`|            |
+-----------------------+-------------------------------------+------------+
|                       | :math:`1.01*DEact_{i} - 0.45,`      |            |
|                       | :math:`\ if\ feed\ type\ is\ not\   |            |
|                       | fat\ and\ fat\ content\ :math:`\leq |            |
|                       | \ 3\%`                              |            |
+-----------------------+-------------------------------------+------------+
|                       | :math:`DE_{i},` if feed type is fat |            |
+-----------------------+-------------------------------------+------------+

..

   MEact\ :sub:`i` = Actual metabolizable energy of feed i, Mcal/kg

   EE\ :sub:`i` = Feed fat (ether extract) content, %

   MEact calculation is different for different feed dependent on feed
   type (fat or not) and fat content.

+----------------------+-----------------------------------+-----------+
|                      | :math:`0.703*MEact_{i} - 0.19 +   |[A.Cow.F.6]| 
|:math:`{NElact}_{i} =`| \frac{0.097*MEact_{i} + 0.19}{9   |           |
|                      | 7}*\left( EE_{i} - 3 \right),\ `  |           |
|                      | :math:`if\ feed\ type\ is \not\   |           |
|                      | fat\ and\ fat\ content\ \geq 3\%;`|           |
+----------------------+-----------------------------------+-----------+
|                      | :math:`0.703*`                    |           |
|                      | :math:`MEact_{i} - 0.19,`         |           |
|                      | :math:`if\                        |           |
|                      | feed\ type\ is\ not\ fat\ and`\   |           |
|                      | :math:`\ fat\ content \leq 3\%;`  |           |
+----------------------+-----------------------------------+-----------+
|                      | :math:`D{Eact}_{i                 |           |
|                      | }*0.8,\ if\ feed\ type\ is\ fat`  |           |
+----------------------+-----------------------------------+-----------+

..

   NElact\ :sub:`i` = Actual net energy for lactation of feed i, Mcal/kg

+----------------------+----------------------------------------+-----------+
|:math:`{NEmact}_{i} =`| :math:`1.37*MEact_{i} - 0.138*MEact_{  |[A.Cow.F.7]|  
|                      | i}^{2} + 0.0105*MEact_{i}^{3}- 1.12,`  |           |
|                      | :math:`if\ feed\ \ type\ is\ not\ fat;`|           |
+----------------------+----------------------------------------+-----------+
|                      | :math:`M{Eact}_                        |           |
|                      | {i}*0.8,\ if\ feed\ type\ is\ fat`     |           |
+----------------------+----------------------------------------+-----------+

..

   NEmact\ :sub:`i` = Actual net energy for maintenance of feed i,
   Mcal/kg

+----------------------+-----------------------------------+------------+
|                      | :math:`1.                         |[ A.Cow.F.8]|
|:math:`{NEgact}_{i} =`| 42*MEact_{i} - 0.174*MEact_{i}^{2 |            |
|                      | } + 0.0122*MEact_{i}^{3} - 1.65,` |            |
|                      | :math:`i                          |            |
|                      | f\ feed\ \ type\ is\ not\ fat;\ ` |            |
+----------------------+-----------------------------------+------------+
|                      | :math:`M{Eact}_{i}`               |            |
|                      | :math:`*0.55,\ if\ feed\ type`    |            |
|                      | :math:`is\ fat`                   |            |
+----------------------+-----------------------------------+------------+

..

   NEgact\ :sub:`i` = Actual net energy for growth of feed i, Mcal/kg

2. **Protein supply**

Protein supply from the feed includes 2 parts: digestible rumen
undegradable protein (RUP) and digestible microbial crude protein (MCP),
which is produced through rumen degradable protein (RDP). MCP production
requires nitrogen source and energy source, so MCP is either nitrogen
limited (when energy is sufficient) or energy limited (when nitrogen is
sufficient). Minerals do not provide any protein.

+------------------------+------------------------------------+-------------+
|    :math:`{Kp}_{i} =`  | :math:`2.904 + \ 1.375*\frac{D     | [A.Cow.F.9] |
|                        | MI}{BW}*100 - 0.02*PercentConc,\ ` |             |
|                        |                                    |             |
|                        | :math:`\                           |             |
|                        | if\ feed_{i}\ is\ concentrate;\ `  |             |
+------------------------+------------------------------------+-------------+
|                        | :math:`3.362 + 0                   |             |
|                        | .479*\frac{DMI}{BW}*100 - 0.017\ ` |             |
|                        | :math:`*NDF_{i}                    |             |
|                        | - 0.007`\ :math:`*PercentConc,\ `\ |             |
|                        | :math:`if\ feed_{i}\ is\ forage;`  |             |
+------------------------+------------------------------------+-------------+
|                        |:math:`3.054 + 0.614*\frac{DMI}{BW}`|             |
|                        | *if feed wet forage*               |             |
+------------------------+------------------------------------+-------------+

..

   Kp\ :sub:`i` = Protein passage rate of feed i, %/h

   PercentConc = Dietary concentrate percentage, % of DM

   NDF\ :sub:`i` = Neutral detergent fiber (ether extract) content of
   feed i, %

+---------------------+---------------------------------------+--------------+
|                     | :math:`\frac{Kd_{                     | [A.Cow.F.10] |
| :math:`{RDP}_{i} =` | i}}{Kd_{i} + Kp_{i}}*\frac{N_{B_{i}}} |              |
|                     | {100}*CP_{i} + \frac{N_{A_{i}}}{100}* |              |
|                     | CP_{i},\ if\ Kp_{i} + Kd_{i} > 0\ \ ` |              |
+---------------------+---------------------------------------+--------------+
|                     | :math:`0,\ if\ Kp_{i} + Kd_{i} \leq 0`|              |
+---------------------+---------------------------------------+--------------+

..

   RDP\ :sub:`i` = Rumen degradable protein of feed i, % of DM

   Kd\ :sub:`i` = Protein degradation rate of feed i, %/h

   N\ :sub:`Ai` = Fraction A of protein of feed i, % of CP

   N\ :sub:`Bi` = Fraction B of protein of feed i, % of CP

+---------------------+--------------------------------------+--------------+
|                     | :math:`CP_{i} - RDP_{i}`             | [A.Cow.F.11] |
| :math:`{RUP}_{i} =` |                                      |              |
+---------------------+--------------------------------------+--------------+

..

   RUP\ :sub:`i` = Rumen undegradable protein of feed i, % of DM

+---------------------+-------------------------------------------+--------------+
|    :math:`MPbact =` | :math:`0.64*min(1000*0.                   | [A.Cow.F.12] |
|                     | 13*TDNact_{diet},\ 1000*0.85*RDP_{diet})` |              |
+---------------------+-------------------------------------------+--------------+

..

   MPbact = Metabolizable bacterial protein production, g

   TDNact\ :sub:`diet` = Dietary actual TDN, kg

   RDP\ :sub:`diet` = Dietary RDP, kg

+----------------------+-------------------------------------------+--------------+
| :math:`RUP_{diet} =` | :math:`\sum_{i} feed_{i}*RUP_{i}*dRUP_{i}`| [A.Cow.F.13] |
+----------------------+-------------------------------------------+--------------+

..

   RUP\ :sub:`diet` = Dietary digestible RUP, kg

   feed\ :sub:`i` = Dry matter intake of feed i, kg

   dRUP\ :sub:`i` = RUP digestibility of feed i, % of RUP

+------------------------+-------------------------------------------+--------------+
|:math:`{MP}_{supply} =` | :math:`MPbact + RUP_{diet} + 0.4*11.8*DMI`| [A.Cow.F.14] |
+------------------------+-------------------------------------------+--------------+

..

   MP\ :sub:`supply` = Total metabolizable protein supply

   Note: 0.4 \* 11.8 \* DMI is the endogenous protein.

3. **Mineral supply**

..

   Use calcium supply as an example (phosphorus is similar):

+-----------------------+------------------------------------+--------------+
|                       | :math:`\sum_{i} fe                 | [A.Cow.F.15] |
|:math:`{Ca}_{supply} =`| ed_{i}*Ca_{i}*\frac{dCa_{i}}{100}` |              |
+-----------------------+------------------------------------+--------------+

..

   dCa\ :sub:`i` = Ca digestibility of feed i, % of Ca

   dCa = 30% for forage, 60% for concentrate, 95% for mineral

   dP (P digestibility) = 64% for forage, 70% for concentrate, 80% for
   mineral
