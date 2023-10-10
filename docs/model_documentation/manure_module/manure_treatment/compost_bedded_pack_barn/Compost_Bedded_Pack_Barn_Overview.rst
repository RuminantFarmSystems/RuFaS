I. **Overview**

Traditional dairy housing systems involve concrete flooring and limited
bedding, which can lead to cow discomfort, suboptimal health, and
laborious manure management. CBPB (Compost Bedded Pack Barn) aims to
address these issues by providing a soft, comfortable, and dry bedding
surface for cows, enhancing their comfort and overall well-being. In a
nutshell, the CBPB practice starts by spreading a layer of organic
bedding like sawdust or sand on the floor of animal pens in the barn. As
cows produce manure, bedding is regularly added and tilted to keep the
mix dry and clean and to facilitate its composting process. 

See video for an illustration of a compost bedded pack practice on a
farm. https://www.youtube.com/watch?v=NBwXcdF1wxo

The primary objective of CBPB is to create a well-aerated and composting
bedding pack within the barn. The composting process helps in the
decomposition of organic matter, including the manure and bedding
materials, which leads to the production of heat and microbial activity.
This composting activity contributes to the breakdown of organic
components and the reduction of moisture content, resulting in a drier
and more stable bedding pack.

The composted manure from the CBP in the pens is cleaned out
infrequently; when it does get cleaned out it is further managed in two
ways:  the composted manure can be moved to a composting facility for
further storage and composting or it can be land applied. In this module
we assume the final manure pack is either land applied or sent to the
manure compost pile. (In the future once we have the composting
treatment method implemented, we will have both functionality for now
land applied only).

The CBPB practice may also reduce manure storage costs and by saving
space and manure handling labor. CBPB can have significant effects on
nutrient dynamics and gas emissions, and various mitigation strategies
can be implemented to minimize their environmental impacts.

II. **Existing Solution**

RuFaS does not currently model the CBPB manure management practice. CBPB
can be modeled using approaches from the IFSM and the Daycent models.
These models use process-based interactions to capture the dynamics of
the system. While the IFSM and Daycent models are valuable tools for
simulating CBPB and assessing their performance and environmental
impacts, they do have certain limitations. These include limited user
flexibility in understanding and changing their structure, inputs, and
parameters. 

III. **Proposed Solution**

The CBPB receives manure information from the animal module, bedding
material and barn information from users. Given weather data, it then
keeps track of 1) the composition of the bedding-material-manure-mix as
manure and bedding material are added continuously as well as 2)
methane, carbon dioxide, nitrous oxide, and ammonia emissions during the
composting process of the bedding-material-manure-mix.

https://whimsical.com/cbpb-WT7Je8NzWUPu8FbRhdsh3E

Section 1 focuses the methane (CH4) and carbon decomposition, which
constitute a daily dry matter loss of the manure-bedding mix thus
changing its mass. The steps to quantify methane emissions and carbon
decomposition are detailed in subsection A and B respectively.
Subsection C will compute the ensuing dry matter loss. Section 2 will
track the mass of phosphorous (P) accumulated broken down into 4 pools:
water organic phosphorous, water inorganic phosphorous, non-water
organic phosphorous, and non-water inorganic phosphorous. Section 3 will
detail the Nitrogen (N) cycle by keeping track of the mass of organic
and inorganic nitrogen.

**Section 1. Methane and Carbon Dioxide Emissions; Dry Matter Loss in
Manure-Bedding Mix**

The dry matter quantity in the manure-bedding mix changes daily because
1) manure and bedding material are added daily and 2) methane emissions
from volatile solids and 3) carbon decompositions. Here we simply keep
track of what is added and what is lost.

Before we can calculate the mass of dry matter loss from the
manure-bedding mix and update its daily mass accordingly, we will
calculate what is lost in methane emissions (section A) and what is lost
from carbon decomposition (section B).

A. **Methane Emissions Calculations using IFSM (IPCC)**

We use an adaptation of the tier 2 approach of the IPCC (2006) to
calculate the emissions of methane on a given day, given the ambient
barn temperature, and a methane conversion factor for the manure
management (Page 179, IFSM manual).

First let’s calculate the Methane Conversion Factor (MCF). The constant
values 7.11 and 0.0884 in equation [M.1.A.1] below are parameter
estimates of a regression using IPCC data (2006), where MCF is an
exponential function of ambient barn temperature. As temperature rises
so will methane emissions, which is determined by the :math:`MCF(T)`:

        **  **\ :math:`MCF(T) = 7.11 \times e^{0.0884 \times T}`
**[M.1.A.1]**

where, :math:`T` is the ambient barn temperature in :sup:`o`\ C from the
weather data.

Next, let :math:`{Emis}_{({CH}_{4})}`\ be the emissions of methane in
kg/day from the compost-bedding-mix such that:

        ** 
 **\ :math:`{Emis}_{CH_{4}}^{CBPB} = \frac{VS \times B_{0} \times 0.67 \times MCF(T)}{100}\ \ `
**[M.1.A.2]**

where,

:math:`VS` is the volatile solids in manure in kg/day,

T is the temperature in :sup:`o`\ C,

:math:`MCF` is the methane (:math:`{CH}_{4})`\ conversion factor
calculated in [M.1.A.1] given T in :sup:`o`\ C,

B\ :sub:`0` is the maximum methane (:math:`{CH}_{4})\ `\ producing
capacity for dairy manure, in m\ :sup:`3`/kg. Value is set at 0.24 as a
default value and the constant at 0.67 in the equation is the conversion
factor of methane (CH4) in m\ :sup:`3` to kg of methane.

B. **Carbon Decomposition and Carbon Dioxide Emissions**

In this section, we quantify the carbon decomposition taking place in
the composting process of the manure-bedding mix due to microbial
activity (decomposition, consumption, respiration). Such decomposition
is a function of the manure-bedding mix composition and properties
(Carbon content, moisture content…), tillage activity, and ambient
temperature.

Before we proceed with the total carbon decomposition calculations in
[M.1.B.5], we will calculate the maximum microbial decomposition rate,
and the microbial decomposition rate of slowly decomposing components in
[M.1.B.1] and [M.1.B.2] respectively; using those we will determine the
carbon decomposition rate in [M.1.B.3], and the Anaerobic effect in
[M.1.B.4].

Let :math:`{Rate}_{decomp}^{Max}`\ be maximum microbial decomposition
rate in :math:`d^{- 1}`, and :math:`{Rate}_{decomp}^{Slow}`\ be the
microbial decomposition rate of slowly decomposing components in
:math:`d^{- 1}`\ such that:

:math:`{Rate}_{decomp}^{Max} = {Rate}_{decomp}^{Effective} \times \left( {1.066}^{\left( T_{layer} - 10 \right)} - {1.21}^{\left( T_{layer} - 50 \right)} \right)`
**[M.1.B.1]**

:math:`{Rate}_{decomp}^{Slow} = {Rate}_{decomp}^{Effective} \times \left( {1.066}^{\left( T_{BP} - 10 \right)} - {1.21}^{\left( T_{BP} - 50 \right)} \right)`
**[M.1.B.2]**

where,

:math:`{Rate}_{decomp}^{Effective}\ `\ is the effectiveness of microbial
decomposition rate, unitless, set at :math:`2.37 \times 10^{- 3},`

:math:`T_{layer}\ `\ is the decomposition temperature simulated in
:sup:`o`\ C, set at :math:`60℃`,

:math:`T_{BP}`\ is the temperature of the compost-bedded pack in
:sup:`o`\ C, set at :math:`30℃`.

Using results in [M.1.B.1] and [M.1.B.2], let
:math:`{Rate}_{decomp}^{C}`\ be the carbon decomposition rate in
:math:`d^{- 1}`, such that:

:math:`{Rate}_{decomp}^{C} = \left( {Rate}_{decomp}^{Max} - {Rate}_{decomp}^{Slow} \right) \times e^{decay \times ({NbDays}^{last\ till} - lag)} \times {Rate}_{decomp}^{Slow}`
**[M.1.B.3]**

where,

:math:`{Rate}_{decomp}^{Max}`\ is the maximum microbial decomposition
rate in :math:`d^{- 1}`\ calculated above,

:math:`{Rate}_{decomp}^{Slow}`\ is the microbial decomposition rate of
slowly decomposing components in :math:`d^{- 1}`,

:math:`decay` is the first order decaying coefficient set at 0.1 per day
in :math:`d^{- 1}`,

:math:`{NbDays}^{last\ till}`\ is the number of days since the last
tillage event in :math:`d`,set at 1 as a default,

:math:`lag` is the lag time in in :math:`d`, set at 2 as a default
value.

The last sub calculation needed before we can determine total carbon
decomposition is the Anaerobic coefficient. Let be
:math:`{Effect}_{C}^{Anae}`\ be the anaerobic effect, unitless, such
that:

   :math:`{Effect}_{C}^{Anae} = \frac{O_{2}}{O_{2,hsat} + O_{2}} \times \frac{O_{2,hsat} + O_{2,amb}}{O_{2,amb}}`
   **[M.1.B.4]**

where,

:math:`O_{2} \in \lbrack 0,1\rbrack,\ `\ is the mole fraction of oxygen
in the air within the windrow, unitless set at 0.15,

:math:`O_{2,hsat\ }`, is the half-saturation constant, unitless set at
0.02,

:math:`O_{2,amb} \in \lbrack 0,1\rbrack` is the mole fraction of oxygen
in ambient air, unitless set at 0.21.

Finally, using calculations above, let :math:`C_{decomp}^{CBPB}` be the
total carbon decomposition, in kg per day, such that:

:math:`C_{decomp}^{CBPB} = ({TS \times \ C}_{manure} + {Q_{bedding}\  \times C}_{bedding}) \times {Rate}_{decomp}^{C} \times {Effect}_{Moist} \times {Effect}_{Anae}`
**[M.1.B.5]**

where,

:math:`TS` is the total solids from the manure in kg,

   :math:`C_{manure}` is the proportion of carbon available in manure,
   unitless, set at 0.5 as a default,

   :math:`Q_{bedding}`\ is the total mass of bedding material in kg,

   :math:`C_{bedding}` is the carbon available in the bedding, unitless,
   set at 0.35 as a default,

   :math:`{Rate}_{decomp}^{C}` is the effective microbial decomposition
   rate calculated in [M.1.B.3],

   :math:`{Effect}_{Moist}` is the effect of moisture on microbial
   decomposition, with
   :math:`{Effect}_{Moist} \in \lbrack 0,0.1\rbrack\ ,` unitless, it is
   set at 0.65 [1]_.

   :math:`{Effect}_{Anae}\ i`\ s the effect of anaerobic conditions on
   microbial decomposition, unitless.

C. **The Daily Dry Matter Available, Daily Dry Matter Loss, and Manure
   mass update**

The daily dry matter loss is simply what is lost from the dry matter in
methane emission and carbon decomposition. Since we estimated the
emissions of methane in kg/day from the compost-bedding mix in [M.1.A.2]
and the total carbon decomposition in kg/day in [M.1.B.5], we can then
derive the dry matter loss in kg/day is by simply adding those 2
quantities in kg/day. Considering the carbon content of the total solids
is 50%. To represent the loss at the scale of the total solids we need
to double the mass of carbon decomposition.

   :math:`{DM}_{loss}^{CBPB} = {2 \times C}_{decomp}^{CBPB} + {Emis}_{{CH}_{4}}^{CBPB}`
   **[M.1.C.1]**

**Numerical Example of Accounting for Dry Matter loss via Methane
Emissions and Carbon Decomposition within a time step.**

To estimate the dry matter loss in kg from the manure-bedding mix
through methane and carbon decomposition we first estimate methane loss
from volatile solids (VS) in kg and carbon decomposition in kg. Let the
initial volatile solid mass be VS = 10.2 kg and the initial total solid
be TS =12 kg.

**Step 1: Calculate the carbon lost as**
:math:`\mathbf{Emis}_{\mathbf{C}\mathbf{H}_{\mathbf{4}}}^{\mathbf{CBPB}}`
**(methane) using [M.1.A.1] and [M.1.A.2]**

the Initial VS = 10.2 kg, then the methane loss is 0.10 kg/day. Plugging
[M.1.A.1] into [M.1.A.2],

.. math:: {Emis}_{CH_{4}}^{CBPB} = \frac{VS \times B_{0} \times 0.67 \times 7.11 \times e^{0.0884 \times T}}{100}

:math:`= 10^{- 2} \times \left( 10.2 \times 0.24 \times 0.67 \times .11 \times e^{0.0884 \times T} \right) =`
0.1

**Step 2: Calculate the updated VS**

The new VS remaining = Initial VS – Methane loss:

.. math:: {VS}_{t + 1}^{CBPB} = {VS}_{t}^{CBPB} - \left( {Emis}_{CH_{4}}^{CBPB} \right)_{t} = 10.2 - 0.1 = 10.1\ kg

**Step 3: Calculate the updated TS**

Assume :math:`C_{decomp}^{CBPB}`\ = 0.2 kg. Considering the carbon
content of the total solids is 50%. To represent the loss at the scale
of the total solids we need to double the mass of carbon decomposition;
hence the total solid loss becomes 0.4 kg.

The updated Total solids = Initial Total Solids– Methane loss – Carbon
decomposition scaled up to the total solids. With a mass 12 kg of
initial total solids, let :math:`{TS}_{t + 1}^{CBPB}` be the updated TS
in kg in the next period such that:

.. math:: {TS}_{t + 1}^{CBPB} = {TS}_{t}^{CBPB} - \left( {Emis}_{CH_{4}}^{CBPB} \right)_{t} - {2 \times \left( C_{decomp}^{CBPB} \right)}_{t} = 12\ –\ 0.1\  - 0.4 = 11.5\ kg

**Manure mass:**

Everyday dry matter loss is substituted from the total manure-bedding
mix.

Assume the initial total manure-bedding mix is 100 kg with 12 kg total
solids and a daily dry matter loss of 0.5 kg. We can update the total
manure-bedding mix mass using the following equation:

If we lose 0.5 kg of dry matter, which is part of the total solids, we
can subtract this from the total solids mass to find the remaining total
solids mass.

 Updated total solids mass = Total Solids - Dry Matter loss

 :math:`{TS}_{t + 1}^{CBPB} = {TS}_{t}^{CBPB} - \left( {DM}_{loss}^{CBPB} \right)_{t}`

Plugging the corresponding numerical values,
:math:`{TS}_{t + 1}^{CBPB} = 12 - 0.5 = 11.5\ kg.`

Since the proportion of total solids in the original manure-bedding mix
remains the same at 12 %, we can set up another equation to determine
the updated manure mass :math:`M_{t + 1}^{CBPB}`:

.. math:: M_{t + 1}^{CBPB} = \frac{{TS}_{t + 1}^{CBPB}}{0.12}\  = 95.83\ kg

Therefore, the updated manure-bedding mix mass after losing 0.4 kg of
total solids is approximately 95.83 kg.

**Section 2. Accounting for Phosphorus (P) and Potassium (K) contents in
the CBPB**

Cows continuously produce manure containing phosphorus (P) and potassium
(K). Hence, P and K get added daily to the manure-bedding mix. In
subsection D and E, we account for those changes in P and K mass.

A. **Phosphorous Content in the CBPB**

P gets added daily to the manure-bedding mix. P is further divided into
4 pools, each corresponding to 4 distinct forms of P: 1) water
extractable inorganic (WIP), 2) water extractable organic (WOP), 3)
non-water extractable inorganic (NWIP), 4) non-water extractable organic
(NWOP). We will then calculate daily changes in total P and in each of
its sub-pools.

Let :math:`P_{t + 1}^{CBPB}`\ be the total mass of P in the
manure-bedding mix at time :math:`t + 1` , in kg. The general equation,
for all forms of P is such that:

.. math:: P_{t + 1}^{CBPB} = P_{t}^{CBPB} + P_{t}^{bedding} + P_{t}^{animal} - P_{t}^{loss}

where,

:math:`P_{t}^{CBPB}` is the total accumulated P in the previous period
:math:`t`, in kg.

:math:`P_{t}^{bedding}` is the mass of P present in the bedding material
added in the previous period :math:`t`, in kg.

:math:`P_{t}^{animal}` is the mass of P present in the manure execrated
by the animal in the previous period :math:`t`, in kg.

:math:`P_{t}^{loss}`\ is the mass of P loss in the previous period
:math:`t`, in kg.

In words, the updated mass of P in the CBPB at time :math:`t + 1` sums
what was already accumulated at time :math:`t` with what was added in
the previous period :math:`t` (through P present in the added bedding
material and from the manure execrated by the animal). It then subtracts
the losses in P in the previous period :math:`t`.

For this version of the CBPB model, we make 3 simplifying assumptions:

i.   The mass of P in the bedding material is negligeable and set at 0,
     :math:`P_{t}^{bedding} = 0\ \forall t.`

ii.  The masses of different forms of P will be received from the animal
     module.

iii. There are no losses in P within the compost bedded pack practice
     :math:`P_{t + 1}^{loss} = 0\ \forall t`.

Under such assumptions, the equations for updating the mass all 4 forms
of phosphorus (P) contained in the manure-bedding mix can be expressed
as follows:

   :math:`P_{t + 1}^{CBPB,\ pool} = P_{t}^{CBPB,\ pool} + P_{t}^{animal,\ pool}`
   **[M.2.A.1]**

where,

:math:`pool \in \left\{ P,WIP,WOP,\ NWIP,NWOP \right\}`

and the corresponding relative proportion
:math:`\% P_{t + 1}^{CBPB,\ pool}` for each
:math:`pool \in \left\{ P,WIP,WOP,\ NWIP,NWOP \right\}` becomes:

   :math:`\% P_{t + 1}^{CBPB,\ pool} = \frac{P_{t + 1}^{CBPB,\ pool}}{\sum_{pool}^{}P_{t + 1}^{CBPB,\ pool}}`
   **[M.2.A.2]**

B. **Potassium Content in the CBPB**

Potassium K gets added continuously to the manure-bedding mix through
cows ‘manure production.

Let :math:`K_{t + 1}^{CBPB}`\ be the total mass of K in the
manure-bedding mix at time :math:`t + 1` such that:

.. math:: K_{t + 1}^{CBPB} = K_{t}^{CBPB} + K_{t}^{bedding} + K_{t}^{animal} - K_{t}^{loss}

Here, we make 2 simplifying assumptions:

i.  The mass of K in the bedding material is negligeable and set at 0,
    :math:`K_{t}^{bedding} = 0\ \forall t.`

ii. There are no losses in K within the compost bedded pack practice
    :math:`K_{t}^{loss} = 0\ \forall t`

:math:`K_{t + 1}^{CBPB} = K_{t}^{CBPB} + K_{t}^{bedding} + K_{t}^{animal} - K_{t}^{loss}`
**[M.2.B.1]**

**Section 3. Ammonia Emissions, Leaching, and Nitrous Oxide Emission**

The total nitrogen in the manure-bedding mix changes daily via tillage
activity, ammonia emissions, nitrous oxide loss, and N leaching. Here we
simply keep track of what is added and what is lost.

For this version of the CBPB model, we make 2 simplifying assumptions:

i.  The mass of N in the bedding material is negligeable and set at 0,
    :math:`N_{t}^{bedding} = 0\ \forall t.`

ii. The mass of N will be received from the animal module.

A. **Nitrogen Loss to Ammonia Emissions**

..

   Let :math:`\left( {Emis}_{NH_{3}}^{CBPB} \right)_{t}`\ be the
   emissions of ammonia in kg at time t (daily):

:math:`\left( {Emis}_{NH_{3}}^{CBPB} \right)_{t} = 0.5 \times \left( N_{t}^{animal} \right) \times I_{t}^{CBPB}(Till) + 0.25\mathbf{\times}\left( N_{t}^{animal} \right)\mathbf{\  \times}\left( 1 - I_{t}^{CBPB}(Till) \right)`
**[M.3.A.1]**

where\ **,**

:math:`N_{t}^{animal}`\ is the mass of nitrogen present in the manure
excreted by the animals at time t in kg.

:math:`I_{t}^{CBPB}(Till)` is an indicator function equal to 1 if there
is tillage of the manure-bedding mix at time t and equal to 0 otherwise.

B. **Nitrogen Loss to Leaching**

In this section, tillage activity does not influence the leaching level
of N. Let :math:`\left( {Leach}_{N}^{CBPB} \right)_{t}`\ be the mass in
kg of Nitrogen leached out of the manure-bedding mix at time t (daily):

   :math:`\left( {Leach}_{N}^{CBPB} \right)_{t} = 0.035 \times \left( N_{t}^{animal} \right)`
   **[M.3.B.1]**

where,

:math:`N_{t}^{animal}`\ is the mass of nitrogen present in the manure
excreted by the animals at time t in kg.

C. **Nitrogen Loss to Nitrous Oxide Emissions**

Let :math:`\left( {Emis}_{NO_{2}}^{CBPB} \right)_{t}`\ be the emissions
of Nitrous Oxide at time t (daily), in kg, such that:

:math:`\left( {Emis}_{NO_{2}}^{CBPB} \right)_{t} = 7.10^{- 2} \times \left( N_{t}^{animal} \right)\mathbf{\times}I_{t}^{CBPB}(Till) + 10^{- 2}\mathbf{\times}\left( N_{t}^{animal} \right)\mathbf{\times}\left( 1 - I_{t}^{CBPB}(Till) \right)`
**[M.3.C.1]**

where,

:math:`N_{t}^{animal}` is the mass of nitrogen present in the manure
excreted by the animals at time t in kg.

   :math:`I_{t}^{CBPB}(Till)` is an indicator function equal to 1 if
   there is tillage of the manure-bedding mix at time t and equal to 0
   otherwise.

D. **Total Mass of Nitrogen, Organic Nitrogen, Inorganic Nitrogen, and
   Ammonium**

Let :math:`N_{t}^{CBPB}` be the total mass in kg of Nitrogen in the
manure-bedding mix at :math:`t\ (daily)`, such that:

:math:`N_{t}^{CBPB} = \left( N_{t - 1}^{CBPB} \right) + \left( N_{t}^{animal} \right) - \left( E_{NH_{3}}^{CBPB} \right)_{t} - \left( {Leach}_{N}^{CBPB} \right)_{t} - \left( E_{NO_{2}}^{CBPB} \right)_{t}`
**[M.3.D.1]**

Let :math:`\left( N_{organic}^{CBPB} \right)_{t + 1}`\ be the mass in kg
of organic nitrogen in the manure-bedding mix at :math:`t`, such that:

   :math:`\left( N_{organic}^{CBPB} \right)_{t} = 0.952 \times N_{t}^{CBPB}`
   **[M.3.D.2]**

Let :math:`\left( N_{inorganic}^{CBPB} \right)_{t}`\ be the mass in kg
of inorganic nitrogen in the manure-bedding mix at :math:`t`, such that:

   :math:`\left( N_{inorganic}^{CBPB} \right)_{t} = (1 - 0.952) \times N_{t}^{CBPB} = 0.048\  \times N_{t}^{CBPB}`
   **[M.3.D.3]**

Finally, the mass of ammonium in kg is estimated to be half of the
inorganic Nitrogen. Let :math:`\left( {NH_{4}}^{CBPB} \right)_{t}` be
the mass of ammonium in kg at time t such that:

   :math:`\left( {NH_{4}}^{CBPB} \right)_{t} = 0.5 \times \left( N_{inorganic}^{CBPB} \right)_{t}`
   **[M.3.D.4]**

**Numerical Example of Accounting for Nitrogen and its Composition
within a time step.**

For each time period, to calculate the total nitrogen remaining and its
composition (different forms of N), we need to subtract the nitrogen
lost as 1) ammonia emissions
:math:`\left( {Emis}_{NH_{3}}^{CBPB} \right)_{t}`, 2) leaching
:math:`\left( {Leach}_{N}^{CBPB} \right)_{t}`, and 3) Nitrous oxide
emissions :math:`\left( {Emis}_{NO_{2}}^{CBPB} \right)_{t}` .

Let’s walk through a numerical example where the manure-bedding mix is
tilled at time t and the additional N mass from manure excretion at time
t is 1.5 kg and there is no remaining nitrogen from the previous day
(i.e., :math:`\left( N_{t - 1}^{CBPB} \right) = 0`):

:math:`N_{t}^{animal} = 1.5\ kg`.

**Step 1: Calculate the nitrogen lost as**
:math:`\left( \mathbf{Emis}_{\mathbf{N}\mathbf{H}_{\mathbf{3}}}^{\mathbf{CBPB}} \right)_{\mathbf{t}}`
**(Ammonia) using [M.3.A.1]**

Given that 50% of the excreted nitrogen is lost as NH\ :sub:`3`, the
estimate of Nitrogen lost as NH\ :sub:`3` is
:math:`\left( {Emis}_{NH_{3}}^{CBPB} \right)_{t} = 0.5 \times 1.5 = 0.75\ kg`

**Step 2: Calculate the nitrogen lost through**
:math:`\left( \mathbf{Leach}_{\mathbf{N}}^{\mathbf{CBPB}} \right)_{\mathbf{t}}`\ **(leaching)
using [M.3.B.1]**

Given that 3.5% of the excreted nitrogen is lost through leaching, the
estimate of Nitrogen lost through leaching is
:math:`\left( {Leach}_{N}^{CBPB} \right)_{t} = 0.035 \times 1.5 = 0.0525\ kg`

**Step 3: Calculate the Nitrous Oxide Emissions**
:math:`\left( \mathbf{Emis}_{\mathbf{N}\mathbf{O}_{\mathbf{2}}}^{\mathbf{CBPB}} \right)_{\mathbf{t}}`\ **using
[M.3.C.1]**

Given that 7% of the excreted nitrogen is lost through Nitrous Oxide
emissions, the estimate of Nitrogen lost through Nitrous Oxide Emissions
if
:math:`\left( {Emis}_{NO_{2}}^{CBPB} \right)_{t} = 7 \times 10^{- 2} \times 1.5 = 0.105\ kg.`

**Step 4: Calculate the total nitrogen lost using [M.3.A.1], [M.3.B.1],
and [M.3.C.1]**

Total nitrogen lost = Nitrogen lost as Ammonia Emission + Nitrogen lost
through leaching + Nitrogen lost through N\ :sub:`2`\ O emissions

Total nitrogen lost = 0.75 + 0.0525 + 0.105 = 0.9075 kg

**Step 5: Calculate the total nitrogen remaining after losses using
[M.3.D.1]**

Total nitrogen remaining = Initial Nitrogen + N from additional Manure -
Total nitrogen lost

Total nitrogen remaining =
:math:`N_{t}^{CBPB} = 1.5 - 0.9075 = 0.5925\ kg`

So, after accounting for the losses (ammonia emissions, leaching, and
Nitrous Oxide emissions), the total nitrogen remaining is 0.5925 kg.

**Step 6: Calculate the different pools of nitrogen based on the
remaining total nitrogen - organic nitrogen, inorganic nitrogen, and the
ammonium within the inorganic nitrogen.**

To calculate the different components of nitrogen based on the remaining
total nitrogen (0.5925 kg) and the given fractions:

**Step 6a: Calculate the Mass of organic Nitrogen using [M.3.D.2]**

Given that 95.2% of the total nitrogen is organic, the mass of organic
nitrogen at time *t* is
:math:`\left( N_{organic}^{CBPB} \right)_{t} = 0.952 \times 0.5925 = 0.5646\ kg`

**Step 6b: Calculate the amount of inorganic nitrogen using [M.3.D.3]**

Given that 4.8% of the total nitrogen is inorganic, the mass of
inorganic nitrogen at time *t* is
:math:`\left( N_{inorganic}^{CBPB} \right)_{t} = 4.8 \times 10^{- 2} \times 0.5646 = 0.0284\ kg.`

**Step 6c: Calculate the ammonium (inorganic nitrogen) using [M.3.D.4]**

Given that 50% of the inorganic nitrogen is ammonium, the mass of
ammonium at time *t* is

:math:`\left( {NH_{4}}^{CBPB} \right)_{t} = 0.5 \times 0.0284 = 0.0142`
kg.

**References**

Michel, Frederick C. Jr., John A. Pecchia, Jerome Rigot, Harold M.
Keener, “Mass and Nutrient Losses during Composting of Dairy Manure with
Sawdust versus Straw Amendment”, Manuscript Submitted to Compost Science
and Utilization journal, 8/5/2003

https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=f1cad6a0a19f1a51d175b7c603f2f461ed173010

Rotz, C.A., Corson, M.S., Chianese, D.S., Montes, F., Hafner, S.D. and
Coiner, C.U., 2012. The Integrated Farm System Model:. Washington, DC:
USDA ARS.

https://www.ars.usda.gov/ARSUserFiles/80700500/reference%20manual.pdf

Bonifacio, Henry F., C. Alan Rotz, and Tom L. Richard. "A process-based
model for cattle manure compost windrows: Part 1. Model description."
*Transactions of the ASABE* 60, no. 3 (2017): 877-892.

http://elibrary.asabe.org/azdez.asp?JID=3&AID=47792&CID=t2017&v=60&i=3&T=1&refer=7&access=

Bonifacio, Henry F., C. Alan Rotz, and Tom L. Richard. "A process-based
model for cattle manure compost windrows: Part 2. Model performance and
application." *Transactions of the ASABE* 60, no. 3 (2017): 893.

https://elibrary.asabe.org/azdez.asp?JID=3&AID=47793&CID=t2017&v=60&i=3&T=1&refer=7&access=

.. [1]
   According to Michel et al. Adding bedding material like sawdust
   reduces the moisture content to an optimal range of [60%,65%] for
   composting (Rynk et al., 1991; Keener et al., 1999).
