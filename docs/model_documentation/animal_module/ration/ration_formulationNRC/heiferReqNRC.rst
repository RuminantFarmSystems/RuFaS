.. _heifer-requirements :

Heifer Ration
=============

   | Last Updated: January 17, 2022

**# of Subroutine and Name:** Description of equations used to calculate
nutrient requirements of heifers.

**Flow of Information:**

A. Nutrient requirements including energy, protein, mineral (Ca and P)
   and several other requirements (NDF, forage NDF, fat) are considered.

B. Energy supply, protein supply and mineral supply from feeds are
   calculated.

C. Supply >= requirements when formulating diet.

Arguments

-  Animal inputs

   i.    BW: Body weight (kg)

   ii.   MW: Mature body weight(kg)

   iii.  Housing: Housing type (Barn or Grazing)

   iv.   Topography (Flat or Hilly)

   v.    Distance: Daily walking distance (km)

   vi.   DOP: Days of pregnancy (d)

   vii.  BCS5: Body condition score (1 – 5 basis)

   viii. PrevTemp: Average daily temperature of last month (°C)

   ix.   Age: Heifer’s age (month)

   x.    Age1stBred: First breeding age (month)

-  Feed inputs (from the feed table, variables with \* are not used in
   any equations yet)

   - TDN: Total digestible nutrient (% of DM)

   - Type: Feed type (Forage, Concentrate, or Mineral)

   - \*PAF: Processing adjustment factor (not used)

   - DE: Digestible energy (standard value, Mcal/kg)

   - ME: Metabolizable energy (standard value, Mcal/kg)

   - NEL: Net energy for lactation (standard value, Mcal/kg)

   - NEM: Net energy for maintenance (standard value, Mcal/kg)

   - NEG: Net energy for growth (standard value, Mcal/kg)

   - \*DM: Dry matter (% of as-fed basis, not used)

   - CP: Crude protein (% of DM)

   - \*NDICP: Neutral detergent insoluble crude protein (% of DM, not
   used)

   - \*ADICP: Acid detergent insoluble crude protein (% of DM, not used)

   - EE: Ether extract, i.e., crude fat (% of DM)

   - NDF: Neutral detergent fiber (% of DM)

   - \*ADF: Acid detergent fiber (% of DM, not used)

   - \*Lignin (% of DM, not used)

   - \*Ash (% of DM, not used)

   - N_A: Fraction A of protein, soluble protein, degraded immediately in rumen (% of CP)

   - N_B: Fraction B of protein, potentially degradable protein, require
     time to generally degrade in rumen (% of CP)

   - N_C: Fraction C of protein, not degradable in rumen (% of CP)

   - Kd: Protein degradation rate (%/h)

   - \*eRUP: Example rumen undegradable protein (% of CP, not used)

   - dRUP: RUP degradability (% of RUP)

   - Ca: Calcium content (% of DM)

   - P: Phosphorous content (% of DM)

   - \*Other minerals (Mg, K, Na, etc. are not considered yet)

   - Is_fat: If the feed is fat supplement or not (yes = 1; no = 0)

   - Is_wetforage: If the feed is wet forage or not(yes = 1; no = 0)

   - \*peNDF: Physically effective NDF (proportion of NDF)

   - Cost: Feed cost ($/kg of DM)

Outputs

i. To be determined

A. **Energy Requirements**

..

   Energy requirement is divided into 4 components: maintenance,
   activity, growth and pregnancy (all in net energy, Mcal)

1. **Maintenance requirement**

..

   Maintenance requirement is calculated based on metabolic body weight
   (body weight\ :sup:`0.75`), body condition score and previous month
   temperature.

+----------------------+------------------------------------+-----------------+
|    :math:`CBW =`     | :math:`MW*0.06275`                 | [A.Heifer.A.1]  |
+----------------------+------------------------------------+-----------------+

..

   CBW = Calf birth weight (kg)

   MW = Mature body weight (kg), default = 682 kg for Holstein

+----------------------+------------------------------------+----------------+
|    :math:`CW =`      | :math:`(18 + (DOP - 190)*          | [A.Heifer.A.2] |
|                      | 0.665)*( \frac{CBW}{45}),`         |                |
|                      | :math:`if\ DOP > 190;`             |                |
|                      | :math:`\ 0,\ otherwise`            |                |
+----------------------+------------------------------------+----------------+

..

   CW = Conceptus weight (kg)

   DOP = Days of pregnancy

+----------------------+------------------------------------+---------------+
|    :math:`BCS9 =`    | :math:`(BCS5 - 1)*2 + 1`           | [A.Heifer.A.3]|
+----------------------+------------------------------------+---------------+

..

   BCS9 = Body condition score, 1 - 9 basis

   BCS5 = Body condition score, 1 – 5 basis

+----------------------+-----------------------------------+---------------+
|    :math:`NEmaint =` | :math:`(BW - CW)^{0.75}*(0.086*   | [A.Heifer.A.4]|
|                      | (0.8 + (BCS9 - 1)*0.05) + 0.0007* |               |
|                      | (20 - PrevTemp)`                  |               |
+----------------------+-----------------------------------+---------------+

..

   NEmaint = Net energy for maintenance requirement, Mcal

   PrevTemp = Average daily temperature of last month, °C

2. **Activity requirement**

..

   Activity requirement is proportional to body weight and daily walking
   distance. Grazing system and hilly topography will cost additional
   energy.

+----------------------+-----------------------------------------+----------------+
|    :math:`NEa1\  =`  | :math:`0.0009                           | [A.Heifer.A.5] |
|                      | *BW + 0.0016*BW, if Housing = Grazing;` |                |
|                      | :math:`0,\ otherwise`                   |                |
+----------------------+-----------------------------------------+----------------+

..

   NEa1 = Net energy for activity requirement caused by grazing system,
   Mcal

+----------------------+------------------------------------+---------------+
|    :math:`NEa2\  =`  | :math:`0.0                         | [A.Heifer.A.6]|
|                      | 06*BW,\ if\ Topography = Hilly;\ ` |               |
|                      | :math:`0,\ otherwise`              |               |
+----------------------+------------------------------------+---------------+

..

   NEa2 = Net energy for activity requirement caused by hilly
   topography, Mcal

+----------------------+-------------------------------------+---------+
|    :math:`NEa\  =`   | :math:`D                            | [A.Heif |
|                      | istance*0.00045*BW + NEa1 + NEa2\ ` | er.A.7] |
+----------------------+-------------------------------------+---------+

..

   NEa = Total net energy for activity requirement, Mcal

   Distance = Daily walking distance, km

3. **Growth requirement**

+-----------------------+------------------------------------+----------------+
|    :math:`MSBW\  =`   | :math:`\ 0.96*MW`                  | [A.Heifer.A.8] |
+-----------------------+------------------------------------+----------------+

..

   MSBW = Mature shrunk body weight, kg

+----------------------+------------------------------------+----------------+
|    :math:`SBW\  =`   | :math:`0.96*BW\ `                  | [A.Heifer.A.9] |
+----------------------+------------------------------------+----------------+

..

   SBW = Shrunk body weight, kg

+----------------------+-----------------------------------+-----------------+
|    :math:`EBW\  =`   | :math:`0.891*SBW\ `               | [A.Heifer.A.10] |
+----------------------+-----------------------------------+-----------------+

..

   EBW = Empty body weight, kg

+-----------------------+------------------------------------+-----------------+
|    :math:`EQSBW\  =`  | :math:`(SBW - CW)*\frac{478}{MSBW}`| [A.Heifer.A.11] |
+-----------------------+------------------------------------+-----------------+

..

   EQSBW = Equivalent shrunk body weight, kg

+---------------------+---------------------------------+---------------+
|    :math:`ADG\  =`  | :math:`\frac{(0.55*MSBW         |[A.Heifer.A.12]|
|                     | - SBW)}{(Age1stBred - Age)\ *\  |               |
|                     | 30.4},\ before\ breeding;\ \ `  |               |
+---------------------+---------------------------------+---------------+
|                     | :math:`\frac{                   |               |
|                     | (0.82*MSBW - SBW)}{(Age1st - Ag |               |
|                     | e)\ *\ 30.4},\ after\ breeding` |               |
+---------------------+---------------------------------+---------------+

..

   ADG = Average daily gain, kg

   Age1stBred = 1\ :sup:`st` breeding age, month

   Age = Current age, month

   Age1st = First calving age, month

+------------------------+---------------------------------+---------------+
|    :math:`EQEBG\  =`   | :math:`0.956*ADG\ `             |[A.Heifer.A.13]|
+------------------------+---------------------------------+---------------+

..

   EQEBG = Equivalent empty weight gain, kg

+------------------------+---------------------------------+----------------+
|    :math:`EQEBW\  =`   | :math:`0.891*EQSBW\ `           |[A.Heif er.A.14]|
+------------------------+---------------------------------+----------------+

..

   EQEBW = Equivalent empty body weight, kg

+------------------------+---------------------------------+----------------+
|    :math:`NEg\  =`     | :math:`0.063                    | [A.Heifer.A.15]|
|                        | 5*EQEBW^{0.75}*EQEBG^{1.097}\ ` |                |
+------------------------+---------------------------------+----------------+

..

   NEg = Net energy for growth requirement, Mcal

4. **Pregnancy requirement**

+------------------------+--------------------------------+----------------+
|    :math:`MEpreg\  =`  | :math:`(2*0.00159*DOP - \ 0.0  | [A.Heifer.A.16]|
|                        | 352)*\frac{CBW}{45*0.14},\ \ ` |                |
|                        | :math:`\ if\ DOP > 19          |                |
|                        | 0;`\ :math:`\ 0,\ otherwise\ ` |                |
+------------------------+--------------------------------+----------------+

..

   MEpreg = Metabolizable energy requirement for pregnancy, Mcal

+------------------------+---------------------------------+------------------+
|    :math:`NEpreg\  =`  | :math:`MEpreg*0.64\ `           | [A.Heifer.A.17]  |
|                        |                                 |                  |
+------------------------+---------------------------------+------------------+

..

   NEpreg = Net energy requirement for pregnancy, Mcal

B. **Protein requirements**

..

   Protein requirement is divided into 3 components: maintenance, growth
   and pregnancy (all in metabolizable protein, g).

1. **Maintenance requirement**

+---------------------+-------------------------------------+----------------+
|    :math:`MPm =`    | :math:`0.3*(BW -                    | [A.Heifer.B.1] |
|                     | CW)^{0.6} + 4.1*(BW - CW)^{0.5}\ `  |                |
|                     | :math:`+ \left( D                   |                |
|                     | MI*1000*0.03 - 0.5*\left( \frac{MPb |                |
|                     | act}{0.8} - MPbact \right) \right)` |                |
|                     | :math:`+ 0.4*11.8*\frac{DMI}{0.67}` |                |
+---------------------+-------------------------------------+----------------+

..

   MPm = Metabolizable protein requirement for maintenance, g

   MPbact = Bacteria metabolizable protein production, g

2. **Growth requirement**

+---------------------+------------------------------------+----------------+
|    :math:`NPg\  =`  | :math:`0,\ if\ ADG = 0;\ \ `       | [A.Heifer.B.2] |
|                     | :math:`A                           |                |
|                     | DG*(268 - 29.4*\frac{NEg}{ADG})\ ` |                |
+---------------------+------------------------------------+----------------+

..

   NPg = Net protein requirement for growth, g

+------------------------------+----------------------------+----------------+
|    :math:`EffMP\_ NPg` =     | :math:`\ \frac{(83         | [A.Heifer.B.3] |
|                              | .4 - 0.114*EQSBW)}{100},\  |                |
|                              | if\ EQSBW\  \leq \ 478;\ ` |                |
|                              | :math:`0.28908,\ otherwise`|                |
+------------------------------+----------------------------+----------------+

..

   EffMP_NPg = Efficiency of converting metabolizable protein to net
   protein

+----------------------+------------------------------------+----------------+
|    :math:`MPg\  =`   | :math:`\frac{NPg}{EffMP\_ NPg}\ `  | [A.Heifer.B.4] |
+----------------------+------------------------------------+----------------+

..

   MPg = Metabolizable protein requirement for growth, g

3. **Pregnancy requirement**

+------------------------+----------------------------------+---------------+
|    :math:`MPpreg =`    | :math:`(0.69*DOP - 69.2)*\frac{C | [A.Heifer.B.5]|
|                        | BW}{45*0.33},\ if\ DOP > 190;\ ` |               |
|                        | :math:`0,\ otherwise`            |               |
+------------------------+----------------------------------+---------------+

..

   MPpreg = Metabolizable protein requirement for pregnancy, g

4. **Total requirement**

+------------------------+----------------------------------+----------------+
|    :math:`MPreq =`     | :math:`MPm + MPg + MPpreg\ `     | [A.Hei fer.B.6]|
+------------------------+----------------------------------+----------------+

..

   MPreq = Metabolizable protein requirement, g

C. **Mineral requirements**

..

   Only calcium and phosphorus requirements are considered currently.

**1. Calcium requirement**

+------------------------+----------------------------------+----------------+
|                        | :math:`0.                        | [A.Heifer.C.1] |
| :math:`Ca_{main}\ `\ = | 0154*BW + \ 0.08*\frac{BW}{100}` |                |
+------------------------+----------------------------------+----------------+

..

   Ca\ :sub:`main` = Calcium maintenance requirement, g

+------------------------+----------------------------------+---------------+
|                        | :math:`9.83*MW^{0.2              | [A.Heifer.C.2]|
|  :math:`Ca_{growth} =` | 2}*BW^{- 0.22}*\frac{ADG}{0.96}` |               |
+------------------------+----------------------------------+---------------+

..

   Ca\ :sub:`growth` = Calcium growth requirement, g


+---------------------+-------------------------------------------------+----------------+
|:math:`Ca_{preg}\  =`| :math:`0.02456*exp((0.05581 - 0.00007*DOP)*DOP) | [A.Heifer.C.3] |
|                     | - 0.02456*exp((0.05581 - 0.00007*(DOP - 1))*    |                |
|                     | (DOP - 1))`, if DOP > 190;                      |                |
+---------------------+-------------------------------------------------+----------------+
|                     | :math:`0, else`                                 |                |
+---------------------+-------------------------------------------------+----------------+

..

   Ca\ :sub:`preg` = Calcium pregnancy requirement, g

   DOP = Days of pregnancy

+----------------------+-----------------------------------+----------------+
|                      | :math:`Ca_                        | [A.Heifer.C.4] |
|   :math:`Ca_{req} =` | {main} + Ca_{growth} + Ca_{preg}` |                |
+----------------------+-----------------------------------+----------------+

..

   Ca\ :sub:`req` = Total calcium requirement, g

2. **Phosphorus requirement**

+----------------------+------------------------------------+---------------+
|                      | :math:`0.8*DMI + \ 0.002*BW`       | [A.Heifer.C.5]|
| :math:`P_{main}\  =` |                                    |               |
+----------------------+------------------------------------+---------------+

..

   P\ :sub:`main` = Phosphorus maintenance requirement, g

+----------------------+------------------------------------+----------------+
| :math:`P_{growth} =` | :math:`( 1.2 + 4.635*MW^{0.22}*BW^ | [A.Heifer.C.6] |
|                      | {- 0.22})*\frac{ADG}{0.96}`        |                |
+----------------------+------------------------------------+----------------+

..

   P\ :sub:`growth` = Phosphorus growth requirement, g

+--------------------+---------------------------------------------+--------------+
|    :math:`Ppreg =` | :math:`0.02743*exp 0.05527-0.000075*DOP*DOP |[A.Heifer.C.7]|
|                    | - 0.02743 * exp 0.05527-0.000075*DOP-1*(DOP-|              |
|                    | 1),if DOP>190;0, else`                      |              |
+--------------------+---------------------------------------------+--------------+

..

   P\ :sub:`preg` = Phosphorus pregnancy requirement, g

+-----------------+----------------------------------------+---------------+
|:math:`P_{req} =`|:math:`P_{main} + P_{growth} + P_{preg}`| [A.Heifer.C.8]|
+-----------------+----------------------------------------+---------------+

..

   P\ :sub:`req` = Total phosphorus requirement, g

D. **Other requirements**

..

   1. Minimum dietary NDF content: 25%

   2. Maximum dietary NDF content: 40%

   3. Minimum dietary forage NDF content: 19%

   4. Maximum dietary fat content: 7%

E. **Feed nutrient supply**

1. **Energy supply**

Energy supply from the feed include NEm, NEl and Neg. NEm provides
energy for maintenance and activity requirement, NEl provides energy for
pregnancy, and NEg provides energy for growth. Feed actual energy
contents are corrected from standard values provided by NRC (2001).
Minerals do not provide any energy.

+----------------------+----------------------------------+---------------+
|    :math:`TDNconc =` | :math:`\frac{TotalTDN}{DMI}*100` | [A.Heifer.E.1]|
+----------------------+----------------------------------+---------------+

..

   TDNconc = TDN concentration, %

   TotalTDN = Dietary TDN content (calculate using standard value in NRC
   (2001))

+-----------------------------+-----------------------------+----------------+
|                             | :math:`1,\ if\ T            | [A.Heifer.E.2] |
|  :math:`DMI\_ to\_ maint =` | otalTDN < 0.035*BW^{0.75}`; |                |
+-----------------------------+-----------------------------+----------------+
|                             | :math:`\frac{TotalTDN}{0.0  |                |
|                             | 35*SBW^{0.75}},\ otherwise` |                |
+-----------------------------+-----------------------------+----------------+

..

   DMI_to_maint = The amount of intake needed to meet the maintenance
   requirement, dimensionless

+------------------------+----------------------------------+---------------+
|    :math:`Discount =`  | :math:`1,\ if\ TDNconc < 60\ `   | [A.Heifer.E.3]|
+------------------------+----------------------------------+---------------+
|                        | :math:`\frac{(TDNc               |               |
|                        | onc - (0.18*TDNconc - 10.3)*     |               |
|                        | ( DMI_{to_{maint}} - 1)          |               |
|                        | )}{TDNconc}, otherwise`          |               |
+------------------------+----------------------------------+---------------+

..

   Discount = TDN discount

+-----------------------+-----------------------------------+----------------+
| :math:`{TDNact}_{i} =`| :math:`TDN_{i}*Discount`          | [A.Heifer.E.4] |
+-----------------------+-----------------------------------+----------------+

..

   TDNact\ :sub:`i` = Actual TDN content of feed i, %

   TDN\ :sub:`i` = Standard TDN content of feed i, %

+------------------------+--------------------------+-----------------+
|  :math:`{DEact}_{i} =` | :math:`DE_{i}*Discount`  | [A.Heifer.E.4]  |
+------------------------+--------------------------+-----------------+

..

   DEact\ :sub:`i` = Actual digestible energy of feed i, Mcal/kg

   DE\ :sub:`i` = Standard DE feed i, Mcal/kg

+---------------------+---------------------------------------------+----------------+
|:math:`{MEact}_{i} =`| :math:`1.01*DEact_{i} -                     | [A.Heifer.E.5] |
|                     | 0.45 + 0.0046*\left( EE_{i} - 3 \right),\ ` |                |
+---------------------+---------------------------------------------+----------------+
|                     | :math:`if\ feed\ type\ is\ not\ fa          |                |
|                     | t\ and\ \ fat`\ :math:`\ content \geq 3\%`; |                |
+---------------------+---------------------------------------------+----------------+
|                     | :math:`1.01*DEact_{i} - 0.45,`              |                |
+---------------------+---------------------------------------------+----------------+
|                     | if feed type is not fat and fat content     |                |
|                     | :math:`\leq 3\%;`                           |                |
+---------------------+---------------------------------------------+----------------+
|                     | :math:`DE_{i},\ if\ feed\ type\ is\ fat`    |                |
+---------------------+---------------------------------------------+----------------+

..

   MEact\ :sub:`i` = Actual metabolizable energy of feed i, Mcal/kg

   EE\ :sub:`i` = Feed fat (ether extract) content, %

   MEact calculation is different for different feed dependent on feed
   type (fat or not) and fat content.

+----------------------+---------------------------------------+---------------+
|:math:`{NElact}_{i} =`| :math:`0.703*MEact_{i} - 0.           | [A.Heifer.E.6]|
|                      | 19 + \frac{0.097*MEact_{i} + 0.19}    |               |   
|                      | :math:`if\                            |               |
|                      | feed\ \ type\ is\ not\ fat\ `\        |               |
|                      | :math:`\ and\ fat\ content \geq 3\%`; |               |
+----------------------+---------------------------------------+---------------+
|                      | :math:`{NElact                        |               |
|                      | }_{i}\  = 0.703*MEact_{i} - 0.19,`    |               |
+----------------------+---------------------------------------+---------------+
|                      | :math:`if\ feed\ type\ is\ not\ fat`  |               |
|                      | :math:`and\ fat\ content \leq 3\%;`   |               |
+----------------------+---------------------------------------+---------------+
|                      | :math:`{NElact}_{i}` =                |               |
|                      | :math:`M{Eact}_{i}*0.8,\ if\ feed`    |               |
|                      | :math:`type\ is\ fat`                 |               |
+----------------------+---------------------------------------+---------------+

..

   NElact\ :sub:`i` = Actual net energy for lactation of feed i, Mcal/kg

+----------------------+-------------------------------------------+----------------+
|:math:`{NEmact}_{i} =`| :math:`1.37*MEact_{i} - 0.138*MEact_{i    | [A.Heifer.E.7] |
|                      | }^{2} + 0.0105*MEact_{i}^{3} - 1.12,\ \ ` |                |
+----------------------+-------------------------------------------+----------------+
|                      | :math:`i                                  |                |
|                      | f\ feed\ \ type\ is\ `\ :math:`not\ fat;` |                |
+----------------------+-------------------------------------------+----------------+
|                      | :math:`M{Eact}_{i}*0.8,`\ :mat            |                |
|                      | h:`\ if\ feed\ type\ is`\ :math:`\ fat\ ` |                |
+----------------------+-------------------------------------------+----------------+

..

   NEmact\ :sub:`i` = Actual net energy for maintenance of feed i,
   Mcal/kg

+---------------------+------------------------------------------+--------------+
| :math:`{NE          | :math:`1.42*MEact_{i} - 0.174*MEact_{    |[A.Heifer.E.8]|
| gact}_{i} =`        | i}^{2} + 0.0122*MEact_{i}^{3} - 1.65,\ ` |              |
+---------------------+------------------------------------------+--------------+
|                     | :math:`if\ feed\ \ type\ is`             |              |
|                     | :math:`not\ fat;\ `                      |              |
+---------------------+------------------------------------------+--------------+
|                     | :math:`{NEgact}_{i} = M{Eact}_{i}`       |              |
|                     | :math:`*0                                |              |
|                     | .55,\ if\ feed\ `\ :math:`type\ is\ fat` |              |
+---------------------+------------------------------------------+--------------+

..

   NEgact\ :sub:`i` = Actual net energy for growth of feed i, Mcal/kg

2. **Protein supply**

Protein supply from the feed include 2 parts: digestible rumen
undegradable protein (RUP) and digestible microbial crude protein (MCP),
which is produced through rumen degradable protein (RDP). MCP production
requires nitrogen source and energy source, so MCP is either nitrogen
limited (when energy is sufficient) or energy limited (when nitrogen is
sufficient). Minerals do not provide any protein.

+--------------------+---------------------------------------------------+----------------+
|                    | :math:`2.904 + \                                  |  [A.Heifer.E.9]| 
| :math:`{Kp}_{i} =` | 1.375*\frac{DMI}{BW}*100 - 0.02*PercentConc,\ `   |                |
+--------------------+---------------------------------------------------+----------------+
|                    | :math:`\ if\ feed\ is\ concentrate;\ `            |                |
+--------------------+---------------------------------------------------+----------------+
|                    | :math:`3.362`\                                    |                |
|                    | :math:`\  + 0.479*\frac{DMI}{BW}*100 - 0.017*`    |                |
|                    | :math:`- 0.007\ *PercentConc`\ :math:`,`          |                |
|                    | :math:`if\ feed\ is\ forage;\ `                   |                |
+--------------------+---------------------------------------------------+----------------+
|                    | :math:`3.054 + 0.614*`                            |                |
|                    | :math:`\frac{DMI}{BW}*100,\ if\ feed\ wet\ forage`|                |
+--------------------+---------------------------------------------------+----------------+

..

   Kp\ :sub:`i` = Protein passage rate of feed i, %/h

   PercentConc = Dietary concentrate percentage, % of DM

   NDF\ :sub:`i` = Neutral detergent fiber (ether extract) content of
   feed i, %

+---------------------+-------------------------------------+-----------------+
|                     | :math:`\frac{Kd_{i}}{Kd_            | [A.Heifer.E.10] |
| :math:`{RDP}_{i} =` | {i} + Kp_{i}}*\frac{N_{B_{i}}}{100} |                 |
|                     | *CP_{i} + \frac{N_{A_{i}}}{100}*CP_ |                 |
|                     | {i},\ if\ Kp_{i} + Kd_{i} > 0;\ \ ` |                 |
|                     | :math:`0,                           |                 |
|                     | \ if\ Kp_{i} + Kd_{i}\  \leq \ 0\ ` |                 |
+---------------------+-------------------------------------+-----------------+

..

   RDP\ :sub:`i` = Rumen degradable protein of feed i, % of DM

   Kd\ :sub:`i` = Protein degradation rate of feed i, %/h

   N\ :sub:`Ai` = Fraction A of protein of feed i, % of CP

   N\ :sub:`Bi` = Fraction B of protein of feed i, % of CP

+----------------------+-----------------------------------+----------------+
|                      | :math:`CP_{i} - RDP_{i}`          | [A.Heifer.E.11]|
|  :math:`{RUP}_{i} =` |                                   |                |
+----------------------+-----------------------------------+----------------+

..

   RUP\ :sub:`i` = Rumen undegradable protein of feed i, % of DM

+------------------------+----------------------------------+----------------+
|    :math:`MPbact =`    | :math:`0.                        | [A.Heifer.E.12]|
|                        | 64*min(1000*0.13*TDNact_{diet},` |                |
|                        | :math:`1000*` :math:`0.85*`      |                |
|                        | :math:`RDP_{diet}`)              |                |
+------------------------+----------------------------------+----------------+

..

   MPbact = Metabolizable bacterial protein production, g

   TDNact\ :sub:`diet` = Dietary actual TDN, kg

   RDP\ :sub:`diet` = Dietary RDP, kg

+-----------------------+--------------------------------------------+-----------------+
|  :math:`RUP_{diet} =` | :math:`\sum_{i} feed_{i}*RUP_{i}*dRUP_{i}` | [A.Heifer.E.13] |
+-----------------------+--------------------------------------------+-----------------+

..

   RUP\ :sub:`diet` = Dietary digestible RUP, kg

   feed\ :sub:`i` = Dry matter intake of feed i, kg

   dRUP\ :sub:`i` = RUP digestibility of feed i, % of RUP

+-----------------------+---------------------------------+----------------+
|:math:`{MP}_{supply} =`| :math:`MPba                     | [A.Heifer.E.14]|
|                       | ct + RUP_{diet} + 0.4*11.8*DMI` |                |
+-----------------------+---------------------------------+----------------+

..

   MP\ :sub:`supply` = Total metabolizable protein supply

   Note: 0.4 \* 11.8 \* DMI is the endogenous protein.

3. **Mineral supply**

..

   Use calcium supply as an example (phosphorus is similar):

+-----------------------+----------------------------------------+----------------+
|:math:`{Ca}_{supply} =`| :math:`\sum_{i}feed_{i}*Ca_{i}*dCa_{i}`| [A.Heifer.E.15]|
+-----------------------+----------------------------------------+----------------+

..

   dCa\ :sub:`i` = Ca digestibility of feed i, % of Ca

   dCa = 30% for forage, 60% for concentrate, 95% for mineral

   dP (P digestibility) = 64% for forage, 70% for concentrate, 80% for
   mineral
