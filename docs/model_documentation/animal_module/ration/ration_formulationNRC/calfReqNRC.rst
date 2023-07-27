.. _calf-requirements :

Calf Ration
===========

   | Last Updated: January 17, 2022

**# of Subroutine and Name:** Description of equations used to calculate
nutrient requirements of calves.

Implemented in calf_ration.py

**Flow of Information:**

A. Dietary intake is calculated for the calf.

   -  Intake (kg) of whole milk or milk replacer and starter are
      calculated based on the animal’s bodyweight and targeted ADG.

B. Nutrient requirements are calculated for the calf to determine
   maintenance and growth energy and protein requirements.

C. The actual gain of the calf is calculated from energy allowable ADG
   and CP allowable ADG.

Arguments

-  Feed library

   i. Nutrient composition of feeds (3 new feeds to add)

+---------+----------------+-------+-------+--------+-------+------+--------+
| Feed    | DM, %          | CP, % | Fat,  | Ash, % | Ca, % | P, % | ME,    |
|         |                | DM    | % DM  | DM     | DM    | DM   | M      |
|         |                |       |       |        |       |      | cal/kg |
+=========+================+=======+=======+========+=======+======+========+
| Whole   | :math:`12.5`   | 25.4  | 30.8  | 6.3    | 1     | 0.75 | 5.37   |
| Milk    |                |       |       |        |       |      |        |
+---------+----------------+-------+-------+--------+-------+------+--------+
| Milk    | :math:`95^{A}` | 20    | 20    | n/a    | 1     | 0.70 | 4.75   |
| Replacer|                |       |       |        |       |      |        |
+---------+----------------+-------+-------+--------+-------+------+--------+
| Starter | :math:`95^{A}` | 18    | 3     | n/a    | 0.7   | 0.45 | 3.28   |
|         |                |       |       |        |       |      |        |
+---------+----------------+-------+-------+--------+-------+------+--------+

..

   Nutrient composition from 2001 Dairy NRC unless otherwise noted

   :sup:`A` From Hill et al. (2010 JDS)

   n/a not available

ii.   Dry matter concentration of feed (%; from feed library)

iii.  Metabolizable energy concentration of feed (Mcal/kg; from feed
      library)

iv.   Crude protein concentration of feed (%; from feed library)

v.    Temperature (input file)

vi.   Wean day (day; user input)

vii.  Wean length (days; user input)

viii. MAYBE: Weaning interval (days; user input)

ix.   Milk type (whole or replacer; user input)

x.    Calf birth weight (kg; animal life cycle)

xi.   Calf body weight (kg; from animal life cycle)

-  Outputs

i.     Whole milk intake (kg)

ii.    Milk replacer intake (kg)

iii.   Starter intake (kg)

iv.    Start of weaning (d)

v.     Milk reduction (integer)

vi.    Milk intake during weaning (kg)

vii.   Total dry matter intake (kg)

viii.  Metabolizable energy intake (Mcal)

ix.    Crude protein intake (kg)

x.     Apparent digestible protein intake (g)

xi.    Milk proportion of diet

xii.   Starter proportion of diet

xiii.  Net energy for maintenance (Mcal)

xiv.   Metabolizable energy for maintenance (Mcal)

xv.    Biological value

xvi.   Endogenous urinary nitrogen losses (g)

xvii.  Metabolic fecal nitrogen losses (g)

xviii. Apparent digestible protein (g)

xix.   Metabolizable energy for gain (Mcal)

xx.    Net energy for gain (Mcal)

xxi.   Energy allowable gain (kg)

xxii.  Apparent digestible protein gain (kg)

xxiii. Live weight change (kg)

A. **Animal Intake**

   Determine the amount of milk or milk replacer consumed by the animal
   prior to and during weaning (per calf).

1. **Milk-based feed intake**


   Calculates the amount of milk or milk replacer consumed by the calf
   (kg). The amount consumed is based on standard industry practices.

+--------------------------------+----------------------------+--------------+
| :math:`whole\_ milk\_ intake =`| :math:`0.10\ *             | [A.Calf.A.1] |
|                                | \ \frac{calf\_ birth\_ wei |              |
|                                | ght\ *\ \ feed\_ dm}{100}` |              |
+--------------------------------+----------------------------+--------------+

..

   whole_milk_intake = amount of whole milk consumed (kg)

   calf_birth_weight = weight of calf at birth (kg)

   feed_dm = dry matter of feed (%)

+--------------------------+--------------------------+-------------+
|                          | :math:`0.10 *            | [A.Calf.A.2]|
| milk_replacer_intake =   | \frac{calf\_             |             |
|                          | birth\_ weight\ *\ 0.1   |             |
|                          | 5\ *\ \ feed\_ dm}{100}` |             |
+--------------------------+--------------------------+-------------+

..

   milk_replacer_intake = amount of milk consumed (kg)

   calf_birth_weight = weight of calf at birth (kg)

   feed_DM = dry matter of feed (%)

2. **Starter intake**

..

   Calculates the daily amount of starter consumed by the calf as a
   piecewise function based on calf body weight (kg) [based on data from
   Khan et al. (2011)]

+-----------------------------+------------------------------+--------+
|                             | :math:`- 0.247               | [A.Cal |
|  :math:`starter\_ intake =` | 83 + 0.0049567\ *\ calf\_ bw | f.A.3] |
|                             | ,\ \ \ \ \ \ \ \ \ \ \ \ \ ` |        |
+=============================+==============================+========+
|                             | :math:`if                    |        |
|                             | \ calf\ bw\  \leq \ 69.365;` |        |
+-----------------------------+------------------------------+--------+
|                             | :math:`- 6.2263 + 0.091      |        |
|                             | 1`\ :math:`45\ *\ calf\_ bw` |        |
+-----------------------------+------------------------------+--------+
|                             | :math:`if\ \ calf\ bw >`     |        |
|                             | :math:`69.365`               |        |
+-----------------------------+------------------------------+--------+

..

   starter_intake = amount of starter consumed on a dm basis (kg)

   calf_bw = current calf body weight (kg)

3. **Reduction in intake during weaning**

..

   The amount of milk-based feed is reduced from the initial milk-based
   feed intake during the weaning period. The day of weaning (no more
   milk-based feed is offered to the animal) is specified by the user.
   TODO: determine if weaning length and reductions in intake should be
   user inputs or generalized to “abrupt” vs. “gradual”.

   Day of calf life when weaning starts (d)

+---------------------------+--------------------------------+--------------+
|    :math:`wean\_ start =` | :math:`\ w                     | [A.Calf.A.4] |
|                           | ean\_ day - wean\_ length - 1` |              |
+---------------------------+--------------------------------+--------------+

..

   wean_start = start day of weaning (d)

   wean_day = day when the animal will be weaned (d)

   wean_length = length of time of the weaning period (d)

   Number of reductions in milk intake that can occur during the weaning
   period (must be integer)

+---------------------------+---------------------------------+--------------+
|                           | :math:`\frac{wean\_ length}{2}` | [A.Calf.A.5] |
|   :math:`milk\_ reduct =` |                                 |              |
+---------------------------+---------------------------------+--------------+

..

   milk_reduct = how many times the amount of milk offered will be
   adjusted for the calf

   wean_length = length of time of the weaning period (d)

   Milk intake during weaning adjustment

+-------------------------------+--------------------------------------+--------------+
|                               | :math:`whole\_ milk\_ intak          | [A.Calf.A.6] |
| :math:`milk\_ intake\_ wean =`| e*\left( 1 - \frac{milk\_ reduct}{we |              |
|                               | an\_ length\  + \ 1} \right),\ \ \ ` |              |
+-------------------------------+--------------------------------------+--------------+
|                               | :math:`if\ who                       |              |
|                               | le\ milk\ inta`\ :math:`ke\  \neq 0` |              |
+-------------------------------+--------------------------------------+--------------+
|                               | :math:`milk\                         |              |
|                               | _ replacer\_ int`\ :math:`ake\ `\ :m |              |
|                               | ath:`*\ \left( 1 - \frac{milk\_ redu |              |
|                               | ct}{wean\_ length\  + \ 1} \right)`, |              |
+-------------------------------+--------------------------------------+--------------+
|                               | :math:`if\ milk\                     |              |
|                               | replacer\ i`\ :math:`ntake\  \neq 0` |              |
+-------------------------------+--------------------------------------+--------------+

..

   milk_reduct = how many times the amount of milk offered will be
   adjusted for the calf

   wean_length = length of time of the weaning period (d)

4. **Total intake**

..

   Convert digestible energy values of calf feeds in the feed library to
   metabolizable energy.

   Milk and milk replacer

+-------------------------+----------------------------------+--------------+
|    :math:`me\_ conc =`  | :math:`0.96 \times de\_ conc`    | [A.Calf.A.7] |
|                         |                                  |              |
+-------------------------+----------------------------------+--------------+

..

   me_conc = metabolizable energy concentration of milk or milk replacer
   (Mcal/kg)

   de_conc = digestible energy concentration of milk or milk replacer
   (Mcal/kg)

   Calf starter

+------------------------+-----------------------------------+--------------+
|    :math:`me\_ conc =` | :math:`(1.0                       | [A.Calf.A.8] |
|                        | 1\ *\ de\_ conc - 0.45) + 0.0046  |              |
|                        | *\ (ee\_ conc - 3)`               |              |
+------------------------+-----------------------------------+--------------+

..

   me_conc = metabolizable energy concentration of starter (Mcal/kg)

   de_conc = digestible energy concentration of starter (Mcal/kg)

   ee_conc = ether extract concentration of starter (% DM)

   Calculation of total intake (kg), ME Intake, and proportion of diet
   that is milk-based or not milk-based feeds.

   Total intake (kg)

+-------------------------+-----------------------------------------+--------------+
|                         | :math:`\sum_{i} dm\_ intake\_ feed_{i}` | [A.Calf.A.9] |
|   :math:`dm\_ intake =` |                                         |              |
+-------------------------+-----------------------------------------+--------------+

..

   dm_intake = dry matter intake (kg)

   dm_intake_feed\ *i* = dry matter intake of the ith feed in the calf
   ration (kg)

   Metabolizable energy intake (Mcal)

   Sum of the ME supplied from ration.

+------------------------+--------------------------------------+---------------+
|                        | :math:`\sum_{i}  me\_ feed_{i}\_ con | [A.Calf.A.10] |
|  :math:`me\_ intake =` | c \times dm\_ intake\_ feed_{i}`     |               |
+------------------------+--------------------------------------+---------------+ 

..

   me_intake = metabolizable energy intake (Mcal)

   me_feed\ *i\_*\ conc = concentration of metabolizable energy in the
   *i*\ th feed of the diet (Mcal/kg)

   dm_intake_feed\ *i* = dry matter intake of the *i*\ th feed in the
   calf ration (kg)

   Proportion of metabolizable energy intake from milk based feeds

+------------------------------+-------------------------------------+--------------+
|    :math:`milk\_             | :math:`\frac{whole\_ milk           | [A.Calf.11]  |
|    me\_ proportion =`        | \_ intake\ *\ me\_ feed_{i}\_ conc\ |              |
|                              | + \ milk\_ replacer\_ intake\ *\    |              |
|                              | me\_ feed_{i}\_ conc}{me\_ intake}` |              |
+------------------------------+-------------------------------------+--------------+

..

   milk_me_proportion = proportion of metabolizable energy intake that
   is milk-based

   whole_milk_intake = amount of whole milk in calf ration (kg)

   me_feed\ *i*\ \_conc = concentration of metabolizable energy in the
   *i*\ th feed of the diet (Mcal/kg)

   me_intake = metabolizable energy intake (Mcal)

   Proportion of metabolizable energy intake from starter

+-----------------------------+-------------------------+---------------+
|    :math:`starter\_         | :math:`\frac{starter\_  | [A.Calf.A.12] |
|    me\_ proportion =`       | intake\ *\ me\_ feed_{i |               |
|                             | }\_ conc}{me\_ intake}` |               |
+-----------------------------+-------------------------+---------------+

..

   starter_me_proportion = proportion of metabolizable energy intake
   that is from starter

   starter_intake = amount of starter consumed (kg)

   me_feed\ *i*\ \_conc = concentration of metabolizable energy in the
   *i*\ th feed of the diet (Mcal/kg)

   me_intake = metabolizable energy intake (Mcal)

   Crude protein intake (kg)

   Sum of the CP supplied from ration.

+-----------------------+-----------------------------+---------------+   
|                       | :math:`\sum_{i} CP\_ feed_{ | [A.Calf.A.13] |   
| :math:`CP\_ intake =` | i}\_ conc \div 100\ *\      |               |   
|                       | dm\_ intake\_ feed_{i}`     |               |   
+-----------------------+-----------------------------+---------------+   



..

   CP_intake = crude protein intake in the total diet (kg)

   CP_feed\ *i*\ \_conc = concentration of crude protein in the *i*\ th
   feed of the diet (%)

   dm_intake_feed\ *i* = dry matter intake of the *i*\ th feed in the
   calf ration (kg)

   Total apparent digested protein (g) 

+------------------------+-----------------------------------------------------+---------------+
| :math:`adp\_ intake =` | :math:`[ 0.93 * \frac{\sum_{i} CP\_ feed_{i}\_ conc | [A.Calf.A.14] |
|                        | \div 100 * dm\_ intake_{feed_{i}}}{CP\_ intake} +   |               |     
|                        | 0.75 * \frac{\sum_{j} CP\_ feed_{j}\_ conc          |               |
|                        | \div 100 * dm\_ intake_{feed_{j}}}{CP\_ intake}]    |               |
|                        | * 1000`                                             |               |
+------------------------+-----------------------------------------------------+---------------+

..

   adp_intake = apparent digested protein consumed (g)

   CP_feed\ *i*\ \_conc = concentration of crude protein in the *i*\ th
   milk-based feed of the diet (%)

   dm_intake_feed\ *i* = dry matter intake of the *i*\ th milk-based
   feed in the calf ration (kg)CP intake = amount of CP in diet (kg)

   starter_CP_intake = amount of CP from starter consumed (kg)

   CP_feed\ *j*\ \_conc = concentration of crude protein in the *j*\ th
   starter feed of the diet (%)

   dm_intake_feed\ *j* = dry matter intake of the *j*\ th starter feed
   in the calf ration (kg)

   Milk-based feed proportion of calf diet

+-----------------------------+-----------------------------+--------------+
|                             | :math:`\frac{whole\_ m      | [A.Calf.A.15]|
| :math:`milk\_ proportion =` | ilk\_ intake + milk\_ repla |              |
|                             | cer\_ intake}{dm\_ intake}` |              |
+-----------------------------+-----------------------------+--------------+

..

   milk_proportion = proportion of calf diet that is milk-based

   whol\_ milk_intake = amount of whole milk in calf ration (kg)

   milk_replacer_intake = amount of milk replacer in calf ration (kg)

   dm_intake = total dry matter intake of the ration (kg)

   Starter proportion of calf diet

+-------------------------------+----------------------------+--------------+
|                               | :math:`\frac{start         | [A.Calf.A16] |
| :math:`starter\_ proportion =`| er\_ intake}{dm\_ intake}` |              |
+-------------------------------+----------------------------+--------------+

..

   starter_proportion = proportion of calf diet that is starter

   starter_intake = amount of starter consumed (kg)

   dm_intake = total dry matter intake of the ration (kg)

B. **Nutrient Requirements**

..

   Calculations to determine the amount of specific nutrients needed by
   the animal at a given age and bodyweight (per calf).

1. **Maintenance requirements**

..

   Calculates the amount of energy and protein needed for the calf at
   maintenance (Mcal and g, respectively).

   Environmental condition can affect the maintenance requirements for
   young calves, thus the NE maint is adjusted based on calf age when
   temperatures are ≤ 5˚C. The temperature factor depends on animal age
   and temperature. The temperature factor was estimated by a linear
   equation of temperature factors in the NRC (2001).

   If the calf is less than or equal to two months of age (60 d) then

+------------------------+---------------------------------------------+--------------+
|                        | :math:`\ 1.34,\                             | [A.Calf.B.1] |
|   :math:`t\_ factor =` | if\ temperature < \  - 30˚C;\ `             |              |
+------------------------+---------------------------------------------+--------------+
|                        | :math:`- 0.0272\ *\ T + 0.4751,\ `          |              |
|                        | if - 30˚C :math:`\leq` temperature          |              |
|                        | :math:`\leq` 15;                            |              |
+------------------------+---------------------------------------------+--------------+
|                        | :math:`0,\ otherwise`                       |              |
+------------------------+---------------------------------------------+--------------+

..

   If the calf is greater than two months of age (60 d) then

+-------------------------+---------------------------------------------------+
|    :math:`t\_ factor =` | :math:`\ 1.07,\                                   |
|                         | if\ temperature < \  - 30˚C;\ `                   |
+=========================+===================================================+
|                         | :math:`- 0.0271\ *\ T + 0.2002,\ `                |
|                         | if - 30˚C :math:`\leq` temperature :math:`\leq` 5;|
+-------------------------+---------------------------------------------------+
|                         | :math:`0,\ otherwise`                             |
+-------------------------+---------------------------------------------------+

..

   t_factor = temperature factor

   T = temperature

   Net energy for maintenance

+------------------------+-----------------------------------+-------------+
|                        | :math:`0.086\ *\ {calf            | [A.Calf.B.2]|
|   :math:`ne\_ maint =` | \_ bw}^{0.75}*\ (1 + t\_ factor)` |             |
+------------------------+-----------------------------------+-------------+

..

   ne_maint = net energy for maintenance (units)

   calf_bw = calf body weight (kg)

   t_factor = temperature factor from Table 1.

   Convert the amount of net energy to metabolizable energy based on the
   proportion of milk or milk replacer and starter in the diet (Mcal).

+--------------------------------+----------------------------+--------------+
|    :math:`me\_ maint =`        | :math:`\frac{n             | [A.Calf.B.3] |
|                                | e\_ maint}{0.86\ *\ m      |              |
|                                | ilk\_ proportion + \ 0.75\ |              |
|                                | *\ starter\_ proportion}`  |              |
+--------------------------------+----------------------------+--------------+

..

   me_maint = metabolizable energy required for maintenance (Mcal)

   ne_maint = net energy required for maintenance (Mcal)

   milk_proportion = proportion of the calf diet that is milk-based

   starter_proportion = proportion of the calf diet that is starter

   Apparent digestible protein requirement for maintenance is calculated
   based on biological value, endogenous urinary N losses, and metabolic
   fecal N.

   Biological value

+-----------------------------------------------------------------------------+--------------+
|                                                                             | [A.Calf.B.4] |
| :math:`bio\_ val =  0.8\ *\ \frac{ \sum_{i} CP\_ feed_{i}\_ conc \div       |              |
| 100\ *\ dm\_ intake\_ feed_{i}}{CP\_ intake} + 0.7\ *\ \frac{ \sum_{j} CP\_ |              |
| feed_{i}\_ conc \div 100\ *\ dm\_ intake\_ feed_{j}}{CP\_ Intake}`          |              |
+-----------------------------------------------------------------------------+--------------+

..

   bio_val = biological value

   CP_feed\ *i*\ \_conc = concentration of crude protein in the *i*\ th
   milk-based feed of the diet (%)

   dm_intake_feed\ *i* = dry matter intake of the *i*\ th milk-based
   feed in the calf ration (kg)CP intake = amount of CP in diet (kg)

   starter_CP_intake = amount of CP from starter consumed (kg)

   CP_feed\ *j*\ \_conc = concentration of crude protein in the *j*\ th
   starter feed of the diet (%)

   dm_intake_feed\ *j* = dry matter intake of the *j*\ th starter feed
   in the calf ration (kg)

   Endogenous urinary nitrogen losses (g)

+----------------------------+--------------------------------+--------------+
|                            | :math:`0.0002\ *\ {            | [A.Calf.B.5] |
| :math:`endo\_ urine\_ N =` | calf\_ bw}^{0.75}\ *\ 1000\ g` |              |
+----------------------------+--------------------------------+--------------+

..

   endo_urine_N = endogenous urinary N loss (g)

   calf_bw = calf BW (kg)

+--------------------------------------------------------------------+---------------+
| :math:`meta\_ Fecal\_ N\  = [0.0019\ *\ (whole\_ milk\_ intake +   | [A.Calf.B.6]  |
| milk\_ replacer\_ intake) + 0.0033\ *\ starter\_ intake]           |               |
| * 1000 \frac{g}{kg}`                                               |               |
+--------------------------------------------------------------------+---------------+

..

   meta_fecal_N = metabolic fecal nitrogen (g)

   whole_milk_intake = amount of whole milk consumed (kg)

   milk_replacer_intake = amount of milk replacer consumed (kg)

   starter_intake = amount starter consumed (kg)

   Apparent digestible protein requirement for maintenance

+--------------------------------------------------------------+--------------+
| :math:`adp\_ maint = 6.25\left( \frac{1}{bio\_ val}*(endo    | [A.Calf.B.7] |
| \_ urine\_ N + meta\_ fecal\_ N) - meta\_ fecal\_ N \right)` |              |
|                                                              |              |
+--------------------------------------------------------------+--------------+

..

   adp_maint = apparent digestible protein for maint (g)

   bio_val = biological value

   endo_urine_N = endogenous urinary nitrogen loss (g)

   meta_fecal_N = metabolic fecal nitrogen (g)

2. **Growth requirements**

..

   Determine the amount of ME available for calf growth (Mcal)

+------------------------+------------------------------------+--------------+
|    :math:`me\_ gain =` | :math:`me\_ intake - me\_ maint`   | [A.Calf.B.8] |
|                        |                                    |              |
+------------------------+------------------------------------+--------------+

..

   me_gain = metabolizable energy available for growth (Mcal)

   me_intake = metabolizable energy intake (Mcal)

   me_maint = metabolizable energy required for maintenance (Mcal)

   Change available ME for growth to NE basis (Mcal)

+-----------------------+----------------------------------------------+--------------+
|                       | :math:`ne\_ gain = me\_ gain\ *\ `           | [A.Calf.B.9] | 
|   :math:`me\_ gain =` |                                              |              |
|                       | :math:`(0.69*\ milk\_ me\_ pro               |              |
|                       | portion + 0.57\ *starter\_ me\_ proportion)` |              |
+-----------------------+----------------------------------------------+--------------+

..

   ne_gain = net energy available for growth (Mcal)

   me_gain = metabolizable energy available for growth (Mcal)

   milk_proportion = proportion of the calf diet that is milk-based

   starter_proportion = proportion of the calf diet that is starter

   Calculate energy available gain based on NE intake (kg/d)

+-------------------------------+--------------------------+---------------+
|    :math:`energy\_            | :math:`e^{0.             | [A.Calf.B.10] |
|    allow\_ gain =`            | 833\frac{1.19\           |               |
|                               | *\ ne\_ gain}{0.69\ *\   |               |
|                               | {calf\_ bw}^{0.355}}\ }` |               |
+-------------------------------+--------------------------+---------------+

..

   energy_allow_gain = energy allowable gain (kg)

   ne_gain = net energy available for growth (Mcal)

   calf_bw = calf body weight (kg)

   Allowable gain based on protein requirements is a function of
   apparent protein intake and maintenance requirement (kg)

+-----------------------------+------------------------------------+---------------+
| :math:`adp\_ allow\_ gain =`| :math:`\frac{(adp\_ intake - adp\_ | [A.Calf.B.11] |
|                             | maint)\ *\ bio\_ val}{0.18         |               |
|                             | 8}\ *\frac{1\ kg}{1000\ g}`        |               |
+-----------------------------+------------------------------------+---------------+

..

   adp_allow_gain = apparent protein allowable daily gain (kg)

   adp_intake = dietary supply of apparent digestible protein (g)

   adp_maint = maintenance requirements for apparent digestible protein
   (g)

   bio_val = biological value

   Calf daily gain is then the minimum of energy allowable gain or ADP
   allowable gain.

+--------------------------------+-----------------------------+---------------+
|:math:`live\_ weight\_ change =`|:math:`min(energy\_ allow\_  | [A.Calf.B.12] |
|                                |gain,\ adp\_ allow\_ gain)`  |               |
+--------------------------------+-----------------------------+---------------+

..

   live_weight_change = daily change in calf weight

   energy_allow_gain = energy allowable gain

   adp_allow_gain = ADP allowable gain

**References**

NRC. 2001. Nutrient Requirements of Dairy Cattle. National Academies,
Washington, D.C.

Khan et al. 2011. Invited review: Effects of milk ration on solid feed
intake, weaning, and performance of dairy heifers. J. Dairy Sci.
94(3):1071-1081.
