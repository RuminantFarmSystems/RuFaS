.. _Monensin_design :

Enteric Methane Mitigation: Monensin
====================================

Date created: May 4, 2023

Last updated: Jun 15, 2023

**People**
----------

-  Subject experts: Edward, Joseph, Haowen, Kristan

-  Software developer: Loi

**Overview**
------------

This design doc aims to implement an empirical equation recently
developed from literature data by our team for predicting the mitigation
potential of monensin on methane yield (CH\ :sub:`4`/DMI) emissions
within the programming context of RuFaS. The advantage of using this
ratio is that emissions are scaled on dry matter intake (DMI) basis,
with this allowing a fairer comparison among animal groups. The
presented solution is still under development and the shape of the
prediction equation may change as additional scientific feedback is
received and more data becomes available to build more robust models.

**Context**
-----------

Monensin is a well-known feed additive (FA) used in cattle diets for
improving feed efficiency. However, its effect as a mitigation strategy
is not always clear with this being mainly explained by the sparsity of
literature that included *in vivo* enteric CH\ :sub:`4` measurements
under monensin supplementation. The potential of decreasing enteric
CH\ :sub:`4` production is mainly related to its effect as a propionate
enhancer in rumen conditions as it has been confirmed in *in vitro*
studies (e.g., Capelari and Powers, 2017). In *in vitro* conditions, it
is possible to evaluate rumen fermentation profile as a result of the
available substrate (diet), however the effect of DMI, which is the main
driver factor of *in vivo* CH\ :sub:`4` emissions (Ramin and Huhtanen,
2013; Niu et al. 2018) cannot be accounted for.

To overcome limited *in vivo* data on CH\ :sub:`4` emissions under
monensin supplementation, we took advantage of the relative availability
of literature data on both intake and rumen fermentation to estimate
total CH\ :sub:`4` production (g/d) and thus estimate the mitigation
effect (% of reduction related to basal diet) at a given dietary dose
(mg/kg DMI) instead. This preliminary analysis was performed on
treatment means data from 20 studies conducted with dairy cows and
published in peer-reviewed journals between 1997 and 2021. We propose a
four-step approach: 1. Collate data of the molar proportions of the main
VFA’s and estimate CH\ :sub:`4` production at rumen conditions from
stoichiometry principles (Wolin 1960), 2. Combine this with estimates of
the apparently fermented substrate, obtained from existing equations
(Huhtanen et al. 2010) to estimate *in vivo* CH\ :sub:`4` production, 3.
Calculate the mean difference (MD) of predicted CH\ :sub:`4` emissions
derived as monensin treatment mean minus control treatment mean (dose =
0 g/kg DMI). The MD values were divided by control means with this
resulting in the percentage of reduction of CH\ :sub:`4` emissions at a
given dose of monensin, and 4. The potential mitigation impact was
calculated as CH\ :sub:`4` yield (mg/kg DMI).

Once the mitigation effect was estimated for each treatment (diet)
within individual study (control vs monensin), diet composition
variables were also retrieved and incorporated into the dataset (Table
1). Linear regression models for predicting CH\ :sub:`4` yield
(CH\ :sub:`4`/DMI; g/kg) were built using a stepwise selection method
(forward and backwards) combining variables such as the monensin dose,
factors such as DMI, concentrate supply, and chemical composition of the
diet. The best model was chosen on the basis of the lowest root mean
square error (RMSE) of the regression. The empirical equation obtained
includes monensin dose and dietary crude protein (CP) concentration (%)
as prediction factors.

**The successful implementation of monensin as an enteric CH\ 4 mitigation within RuFaS may allow:** 

a. Evaluating diets that may favor decreased CH\ :sub:`4` production in
   combination with improved feed efficiency.

b. Considering the negative relationship found between CP contents in
   the diet and CH\ :sub:`4` yield emissions (Eq. 1), it is expected
   that should be possible to estimate impact of monensin
   supplementation on N balance at animal-group basis.

c. In the future, calculate the monetary cost of the addition of
   monensin to the diet in a long-term perspective (animal cycles).

**Definitions**
---------------

**Methane metrics.** For accounting the mitigation potential of enteric
CH\ :sub:`4` emissions at an individual animal level (per cow), the
following metrics are considered:

a. Methane yield: It is the arithmetic ratio between daily CH\ :sub:`4`
   production (g/day; output) related to the DMI (kg/day; input):
   CH\ :sub:`4`/DMI, g/kg).

Additional metrics such as total CH\ :sub:`4` emissions (g/d) or
CH\ :sub:`4` intensity (g per kg of energy corrected milk), might be
considered as optional.

**Definition of variables.** For accounting the mitigation potential of
enteric CH\ :sub:`4` emissions at an individual animal level (per cow),
the following metrics are considered:

b. Estimation of total CH\ :sub:`4` emissions: From empirical equations
   built from animal and diet-related factors which are set within the
   RuFaS platform. Selected models were thought to be representative of
   US dairy feeding conditions. At present, there are three equations
   for this: IPCC-Tier 2 (2007), Mills et al. (2003), and Niu et al.
   (2018).

c. Arithmetic ratios for accounting emissions as described in the
   previous section.

d. Dry matter intake: estimated using either equations by NRC (2001) or
   NASEM (2021) feeding systems as specified by the user.


**Requirements**
----------------

   a. Predicted CH\ :sub:`4` emissions are linked to estimation of dry
      matter intake (DMI). Therefore, estimations may differ depending
      on the feeding system chosen by the user (NRC vs NASEM).

   b. Total CH\ :sub:`4` emissions (g/d) are calculated according to
      empirical equations mentioned in definition 4b and described in
      the Pseudocode documentation. The RuFaS user defines which of the
      available equations wants to set for calculations.

   c. Set the dietary dose of monensin (mg per kg of DMI) to be added to
      the diet. This should be within the range specified in Table 1.

   d. Retrieve nutrient composition of the diet for calculating
      CH\ :sub:`4` yield mitigation potential according to equation 1.
      Specifically: crude protein (as a % on a DM basis) Diet
      composition may change within each pen upon feeding interval set
      (i.e., every 30 days).

   e. Calculate total CH\ :sub:`4` emissions (g/d) **without monensin
      supplementation** and then divide it by DMI for obtaining
      CH\ :sub:`4` yield values.

   f. Calculate mitigation potential of monensin for decreasing
      CH\ :sub:`4` yield (% of reduction in CH\ :sub:`4` yield related
      to the basal diet) using Eq. 1 listed in this design document.

   g. Subtract the obtained value (% of reduction) from the initial
      estimated CH\ :sub:`4` yield emission for accounting the reduction
      at an individual animal level in terms of g of methane per kg of
      DMI and then replicate this calculation for all animals within
      each pen on a daily basis.

   h. Calculate total CH\ :sub:`4` emissions (g/d) **with monensin
      supplementation** by multiplying the adjusted yield by DMI.

**Milestones**
--------------

   a. We are able to calculate mitigation potential for CH\ :sub:`4`
      yield of monensin at a given dose in the diet at an individual
      animal level.

   b. By summing the calculated mitigation potential (% of reduction)
      from the estimated emissions obtained from the basal diet (no
      supplementation) for each individual, we are able to estimate both
      CH\ :sub:`4` emissions and reduction of carbon footprint at an
      animal group level (pen, herd, etc.).

   c. We are able to calculate the effectiveness of monensin as an
      enteric CH\ :sub:`4` yield mitigation strategy for each animal
      group (e.g., calves, heifers, lactating cows) with this allowing
      adjusting diet composition if required.

   d. With the proposed empirical equation for CH\ :sub:`4` yield, we
      are able to account for the effects of changes in both DMI and
      diet composition (specifically: CP) thus obtaining realistic
      predictions at a given dose of monensin in the diet.

**Existing solution**
---------------------

There is no solution already implemented for this issue in the current
version of RuFaS.

**Proposed solution**
---------------------

Based on recent work conducted by our team, we developed an empirical
equation for accounting the mitigation potential (% of reduction) of
monensin for reducing CH\ :sub:`4` yield emissions CH\ :sub:`4`/DMI;
mg/kg.

:math:`Change\ in\ {CH}_{4}\ yield\ (\%) = \ 0.30054\  - \ 0.00377\  \times \ Monensin\  - \ 1.57832\  \times \ CP`

   Eq. 1

Where, Monensin = monensin daily dose (mg/kg of DMI), and CP refer to
dietary crude protein content (as a % of DM). Still caution should be
exercised when aiming to estimate the CH\ :sub:`4` mitigation potential
of monensin for growing animals (calves and heifers) or dry cows when
using this empirical equation as these animal groups are not well
represented in the current dataset. A preliminary flow chart is
presented for implementing the FA monensin as mitigation strategy for
reducing CH\ :sub:`4` yield in Figure 1.

**Table 1.** Limits to applying the proposed solution. Descriptive
statistics of current dataset (n = 20 studies)

+--------------------+----------+-------+-------+---------+-----------+
| Variable           | units    | Mean  | SD    | Minimum | Maximum   |
+====================+==========+=======+=======+=========+===========+
| DMI                | kg/d     | 21.0  | 3.02  | 10.0    | 27.6      |
+--------------------+----------+-------+-------+---------+-----------+
| CP                 | % of DM  | 17.4  | 1.27  | 15.0    | 19.1      |
+--------------------+----------+-------+-------+---------+-----------+
| Monensin daily     | mg/kg    | 19.5  | 7.61  | 10.2    | 48.0      |
| dose               | DMI      |       |       |         |           |
+--------------------+----------+-------+-------+---------+-----------+

DMI= dry matter intake; CP= crude protein.

**Suggested levels of monensin in diets when using the proposed equation for CH4 yield**: 
A range between **20 to 36 mg/kg DMI** is recommended to be used for
typical dairy cattle rations.

Two hypothetical test cases (examples) are presented as test cases for
calculating CH\ :sub:`4` yield mitigation potential when monensin is
added to the diet at an individual animal level:

Example 1.
----------

-  Animal group = dry cows

-  Average daily DMI per cow consuming a diet (70:30 ratio on a DM basis) = 12 kg

-  Diet composition of the diet containing corn silage and legume hay as the forage components of the diet yields: *16 % CP*.

-  Total CH\ :sub:`4` WITHOUT Monensin addition as estimated by Niu et al. (2018) = 250 g/d

-  CH\ :sub:`4` yield WITHOUT Monensin addition, g/kg DMI = 20.8

-  Monensin dose = 24 mg/kg DMI

-  By applying Eq. 1, we get: **-4.25 % reduction in CH\ 4 yield emissions.**

..

   :math:`CH4\ yield\ reduction\ (\%) = \ 0.30054\  - \ 0.00377\  \times \ 24\  - \ 1.57832\  \times \ 16.0\%\ CP\  = -4.25%\ `

-  Then, 20.8 – (20.8 × 4.25%) = 0.88 → 19.1 g/kg (CH\ :sub:`4` yield emission WITH monensin added to the diet).

-  And to obtain the mitigation potential for total CH\ :sub:`4` emissions = > 
19.1 g/kg × 12 kg = **229 g/d** - Total CH\ :sub:`4` emissions WITH monensin added to the diet.

Example 2.
----------

-  Animal group = lactating cows

-  Average daily DMI per cow consuming a diet (50:50 ratio on a DM basis) = 24 kg

-  Diet composition of the diet containing corn silage, alfalfa and grass as the forage components of the diet yields: *18 % CP*.

-  Total CH\ :sub:`4` WITHOUT Monensin addition as estimated by Niu et al. (2018) = 400 g/d

-  CH\ :sub:`4` yield WITHOUT Monensin addition , g/kg DMI = 16.7

-  Monensin dose = 24 mg/kg DMI

-  By applying Eq. 1, we get: **-7.40% reduction in CH\ 4 yield emissions.**

..

   :math:`CH4\ yield\ reduction\ (\%) = \ 0.30054\  - \ 0.00377\  \times \ 24\  - \ 1.57832\  \times \ 18.0\%\ CP\  = \ `-7.40%

-  Then, 16.7 - (16.7 × 7.40%) = 1.24 → 15.5 g/kg (CH\ :sub:`4` yield emission WITH monensin added to the diet).

-  And to obtain the mitigation potential for total CH\ :sub:`4` emissions = > 15.5 g/kg × 24 kg = **372 g/d** - Total CH\ :sub:`4` 
   emissions WITH monensin added to the diet.

**Alternative solutions**
-------------------------

   a.  **Use other metrics for accounting the CH\ :sub:`4` mitigation potential of 3-NOP**
       Two additional empirical equations are available for calculating
       mitigation potential (% of reduction) in terms of total CH\ :sub:`4`
       emissions (g/d) and CH\ :sub:`4` intensity (g per kg of energy corrected
       milk produced). The metric for CH\ :sub:`4` intensity for carbon
       footprint estimations is only applicable for lactating cows.

:math:`Change\ in\ Total\ {CH}_{4}\ production\ (\%) = \  - 0.15827\  - \ 0.00591` 

   | :math:`\times \ \ Monensin\  + \ 0.00918\  \times \ DMI`

   Eq. 2

:math:`Change\ in\ {CH}_{4}\ intensity\ (\%) = \ 0.04881\  - \ 0.00589\  \times \ Monensin`

   Eq. 3

       Where, Monensin = monensin daily dose (mg/kg of DM), and CP refer to
       dietary crude protein content (as a % of DM).

   b.  **Assume fixed values for accounting enteric CH\ 4 mitigation potential of 3-NOP**
       The user might consider using fixed values instead. No study was found
       in the literature accounting for reductions in CH\ :sub:`4` yield
       emissions when adding monensin to the diet. Expected reductions on total
       CH\ :sub:`4` emissions (g/d) as obtained in the meta-analysis study
       conducted by Appuhamy et al. (2013) are recommended to be used as a
       reference (Tables 2 and 3). Note the differences between beef and dairy
       cattle diets in the reductions in CH\ :sub:`4` emissions are encompassed
       with decreases in DMI. Also increased monensin addition is more commonly
       used for beef cattle data.
      
       Instead of Appuhamy et al. (2013) numbers, the recent meta-analysis by
       Marumo et al. (2013) in dairy cattle (n = 19 in vivo studies), have
       indicated that monensin addition to the diet at an average dose of 24
       mg/kg DMI, decreases daily CH\ :sub:`4` production and CH\ :sub:`4`
       yield by 5.4% and 4.0%, respectively.

   **Table 2.** Descriptive statistics of DMI and monensin dose used when
   added to cattle diets. Source: Appuhamy et al. (2013)

+----------------------+-----------+--------+-----------+------------+
| Variable             | units     | Mean   | Minimum   | Maximum    |
+======================+===========+========+===========+============+
| Dairy cattle         |           |        |           |            |
+----------------------+-----------+--------+-----------+------------+
| DMI                  | kg/d      | 18.6   | 9.70      | 28.5       |
+----------------------+-----------+--------+-----------+------------+
| Monensin daily dose  | mg/kg DMI | 21.0   | 11.0      | 35.0       |
+----------------------+-----------+--------+-----------+------------+
| Beef cattle          |           |        |           |            |
+----------------------+-----------+--------+-----------+------------+
| DMI                  | kg/d      | 7.2    | 5.4       | 10.5       |
+----------------------+-----------+--------+-----------+------------+
| Monensin daily dose  | mg/kg DMI | 32     | 28        | 40         |
+----------------------+-----------+--------+-----------+------------+

   **Table 3.** Estimated enteric CH\ :sub:`4` mitigation effect of
   monensin when added to cattle diets (n = 22 controlled studies). Source:
   Appuhamy et al. (2013).

+--------------------------+------+------+---------+--------+-------+
|                          |      |      |         |        |       |
+==========================+======+======+=========+========+=======+
| Item                     | N    | Ave  | MD\*    | *P*    | MD    |
|                          |      | rage |         | -value | (     |
|                          |      |      |         |        | %)*\* |
+--------------------------+------+------+---------+--------+-------+
| CH\ :sub:`4` production  |      |      |         |        |       |
| (g/d)                    |      |      |         |        |       |
+--------------------------+------+------+---------+--------+-------+
| Dairy cows               | 11   | 338  | -7 ± 5  | 0.184  | 2.07% |
+--------------------------+------+------+---------+--------+-------+
| Beef steers              | 11   | 131  | -19 ± 4 | <0.001 | 1     |
|                          |      |      |         |        | 4.50% |
+--------------------------+------+------+---------+--------+-------+
| Both dairy cows and beef | 22   | 240  | -13 ± 4 | <0.001 | 5.42% |
| steers                   |      |      |         |        |       |
+--------------------------+------+------+---------+--------+-------+
| Daily DMI (kg/d)         |      |      |         |        |       |
+--------------------------+------+------+---------+--------+-------+
| Dairy cows               | 10   | 18.6 | -0.41 ± | <0.001 | 2.20% |
|                          |      |      | 0.09    |        |       |
+--------------------------+------+------+---------+--------+-------+
| Both dairy cows and beef | 10   | 7.24 | -0.48 ± | 0.001  | 5.66% |
| steers                   |      |      | 0.13    |        |       |
+--------------------------+------+------+---------+--------+-------+

\* Reduction in total CH\ :sub:`4` emissions (g/d); 
\*\* Average mitigation effect (% of reduction).

| |image1|
**Figure 1.** Proposed flowchart for implementing monensin as
CH\ :sub:`4` mitigation strategy within the RuFaS model.

**Monitoring, and Alerting**
----------------------------

    a. Methane mitigation equations listed above should work for
       lactating cow data within the limits set in Table 1.

    b. Upper limit: According to literature review, it is recommended in
       any case not to exceed a maximum dose of 36 mg/kg DMI as it may
       have a significant effect on DMI and consequently on animal
       performance.

    c. Lower limit: Addition of monensin to the diet around ≤ 16 mg/kg
       DMI may seriously compromise abatement effect and even increase
       CH\ :sub:`4` yield emissions.

**Cross-Team Impact**
---------------------

    a. As presented in this design doc, it is expected that the proposed
       solution should not impact on the other modules within RuFaS.
       This proposal is considered as a further development within both
       animal and feed formulation modules.

**Open Questions**
------------------

**Detailed Scoping and Timeline**
---------------------------------

    a. 4-6 weeks of developing

    b. 1-2 weeks of testing

**Rerferences**
---------------

Appuhamy, J. A. D., A. B. Strathe, S. Jayasundara, C. Wagner-Riddle, J.
   Dijkstra, J. France, and E. Kebreab. 2013. Anti-methanogenic effects of
   monensin in dairy and beef cattle: A meta-analysis. J. Dairy Sci.
   96:5161–5173. https://doi.org/10 .3168/jds.2012-5923

Capelari, M., Powers, W. 2017. The effect of nitrate and monensin on in
   vitro ruminal fermentation. J. Anim. Sci. 95: 5112-5123.
   https://doi.org/10.2527/jas2017.1657

Marumo, J. L., LaPierre, P. A., Van Amburgh, M. E. 2023. Enteric Methane
   Emissions Prediction in Dairy Cattle and Effects of Monensin on Methane
   Emissions: A Meta-Analysis. Animals 13: 1392.
   https://doi.org/10.3390/ani13081392

NASEM (National Academies of Sciences, Engineering, and Medicine). 2021.
   Nutrient Requirements of Dairy Cattle. 8th rev. ed. The National
   Academies Press. https://doi.org/10.17226/25806.

Niu, M., E. Kebreab, A. N. Hristov, J. Oh, C. Arndt, A. Bannink, A. R.
   Bayat, A. F. Brito, T. Boland, D. Casper, L. A. Crompton, J. Dijkstra,
   M. A. Eugène, P. C. Garnsworthy, M. N. Haque, A. L. F. Hellwing, P.
   Huhtanen, M. Kreuzer, B. Kuhla, P. Lund, J. Madsen, C. Martin, S. C.
   McClelland, M. McGee, P. J. Moate, S. Muetzel, C. Muñoz, P. O’Kiely, N.
   Peiren, C. K. Reynolds, A. Schwarm, K. J. Shingfield, T. M. Storlien, M.
   R. Weisbjerg, D. R. Yáñez-Ruiz, and Z. Yu. 2018. Prediction of enteric
   methane produc[1]tion, yield, and intensity in dairy cattle using an
   intercontinental database. Glob. Chang. Biol. 24: 3368–3389.
   https://doi.org/10.1111/gcb.14094

NRC (National Research Council). 2001. Nutrient Requirements of Dairy
   Cattle. 7th rev. ed. Natl. Acad. Sci., Washington, DC.

Ramin, M., and P. Huhtanen. 2013. Development of equations for
   predicting methane emissions from ruminants. J. Dairy Sci. 96:2476–
   2493. https://doi.org/10.3168/jds.2012-6095

.. |image1| image:: ../media/monensin.png
   :width: 6in
   :height: 6in