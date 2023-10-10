I. Overview
============

The Open Lot dairy system is a traditional housing approach that allows
cows to have outdoor space instead of being confined in barns. The open
lots typically consist of natural or compacted soil with some form of
shelter or shade to protect the cows from harsh weather conditions.

In this management system, cows spend most of their time in the open-lot
corral, which is a mixture of bare ground and manure. When cows deposit
urine and manure on the corral surface, dry climate and low humidity
facilitate rapid drying and ammonia (NH\ :sub:`3`) volatilization.

To manage the manure in Open Lots, farmers commonly harrow the surface.
Harrowing is usually performed daily, which results in light mixing the
soil with manure and urine. Harrowing is different than tilling in that
it is not pushing an implement into the soil but dragging something over
the surface. The difference is somewhat analogous to using a shovel vs a
rake. However, this process also disrupts the urine, which is likely a
significant source of volatilization.

In summary, Open Lots dairy systems provide cows with outdoor spaces and
allows for natural behaviors. However, the manure management in this
system involves harrowing the corral surface regularly, which can lead
to ammonia volatilization due to the dry climate and low humidity.

II. **Existing Solution**

RuFaS does not currently model Open Lot manure management practice.

Open Lots can be modeled using approaches from the IFSM and the Daycent
models. These models use process-based interactions to capture the
dynamics of the system. While the IFSM and Daycent models are valuable
tools for simulating Open lots and assessing their performance and
environmental impacts, they do have certain limitations. These include
limited user flexibility in understanding and changing their structure,
inputs, and parameters. 

III. **Proposed Solution**

..

   In this Open Lot method, we receive manure information from the
   animal module and barn information from users. Given weather data, we
   then keep track of 1) the composition of the open lot manure mix as
   manure and urine are added continuously as well as 2) methane,
   nitrous oxide, and ammonia emissions during the process of the open
   lot manure-mix.

   Section 1 focuses methane (CH\ :sub:`4`) emissions, which constitute
   of a daily dry matter loss of the manure mix thus changing its mass.
   The steps to quantify methane emissions are detailed in subsection A.
   Subsection B will compute the ensuing dry matter loss. Section 2: 2A
   will track the mass of phosphorous (P) accumulated and broken down
   into 4 pools: water organic phosphorous, water inorganic phosphorous,
   non-water organic phosphorous, and non-water inorganic phosphorous.
   Section 2: 2B will track the mass of potassium (K). Section 3 will
   detail the Nitrogen (N) cycle by keeping track of the mass of organic
   and inorganic nitrogen.

**Section 1. Methane Emissions; Dry Matter Loss in Manure Mix**

The dry matter quantity in the open lot manure changes daily because 1)
manure is added daily and 2) methane is emitted from volatile solids and
3) carbon decomposition. Here we simply keep track of what is added and
what is lost.

Before we can calculate the mass of dry matter loss from the manure and
update its daily mass accordingly, we will calculate what is lost in
methane emissions (section A) and what is lost from carbon decomposition
(section B).

A. **Methane Emissions Calculations using IFSM (IPCC)**

We use an adaptation of the tier 2 approach of the IPCC (2006) to
calculate the emissions of methane on a given day, given the ambient
temperature, and a methane conversion factor for the manure management
(Page 179, IFSM manual).

First let’s calculate the Methane Conversion Factor (MCF). The constant
values 0.0625 and 0.25 in equation [M.1.A.1] below are parameter
estimates of a regression using IPCC data (2006), where MCF is a linear
function of ambient temperature. As temperature rises so will methane
emissions, which is determined by the :math:`MCF(T)`:

        **   **\ :math:`MCF(T) = 0.0625\  \times T - 0.25` **[M.1.A.1]**

where, :math:`T` is the ambient temperature in :sup:`o`\ C from the
weather data.

Next, let :math:`{Emis}_{CH_{4}}^{OpenLot}`\ be the emissions of methane
in kg/day from the open lot manure mix such that:

        ** 
 **\ :math:`{Emis}_{CH_{4}}^{OpenLot} = \frac{VS \times B_{0} \times 0.67 \times MCF(T)}{100}\ \ `
**[M.1.A.2]**

where,

:math:`VS` is the volatile solids in manure in kg/day,

T is the ambient temperature in :sup:`o`\ C,

:math:`MCF` is the methane (:math:`{CH}_{4})` conversion factor
calculated in [M.1.A.1] given T in :sup:`o`\ C,

B\ :sub:`0` is the maximum methane (:math:`{CH}_{4})\ `\ producing
capacity for dairy manure, in m\ :sup:`3`/kg. Value is set at 0.24 as a
default value and the constant at 0.67 in the equation is to convert the
methane (CH4) emissions estimates from m\ :sup:`3` to kg of methane.

**B. Carbon Decomposition and Carbon Dioxide Emissions**

In this section, we quantify the carbon decomposition taking place in
the manure due to microbial activity (decomposition, consumption,
respiration). Such decomposition is a function of the manure composition
and properties (Carbon content, moisture content…) as wells as ambient
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

:math:`{Rate}_{decomp}^{Slow} = {Rate}_{decomp}^{Effective} \times \left( {1.066}^{\left( T_{} - 10 \right)} - {1.21}^{\left( T_{} - 50 \right)} \right)`
**[M.1.B.2]**

where,

:math:`{Rate}_{decomp}^{Effective}\ `\ is the effectiveness of microbial
decomposition rate, unitless, set at :math:`2.37 \times 10^{- 3},`

:math:`T_{layer}\ `\ is the decomposition temperature simulated in
:sup:`o`\ C, set at :math:`60℃`.

:math:`T` is the ambient temperature :sup:`o`\ C.

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
harrowing event in :math:`d`,set at 1 as a default,

:math:`lag` is the lag time in in :math:`d`, (lag time before reaching
maximum decomposition) set at 2 as a default value.

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

Finally, using calculations above, let :math:`C_{decomp}^{OpenLot}` be
the total carbon decomposition, in kg per day, such that:

:math:`C_{decomp}^{OpenLot} = ({{TS}^{Manure} \times \ C}_{manure}) \times {Rate}_{decomp}^{C} \times {Effect}_{Moist} \times {Effect}_{Anae}`
**[M.1.B.5]**

where,

:math:`{TS}^{Manure}` is the total solids from the manure in kg,

   :math:`C_{manure}` is the proportion of carbon available in manure,
   unitless, set at 0.5 as a default,

   :math:`{Rate}_{decomp}^{C}` is the effective microbial decomposition
   rate calculated in [M.1.B.3],

   :math:`{Effect}_{Moist}` is the effect of moisture on microbial
   decomposition, with
   :math:`{Effect}_{Moist} \in \lbrack 0,1.0\rbrack\ ,` unitless, it is
   set at 0.65.

   :math:`{Effect}_{Anae}\ i`\ s the effect of anaerobic conditions on
   microbial decomposition, unitless.

   **C. The Daily Dry Matter Available, Daily Dry Matter Loss, and Open
   Lot Manure mix update**

The daily dry matter loss is simply what is lost from the dry matter in
methane emission and carbon decomposition. Since we estimated the
emissions of methane in kg/day from the manure in [M.1.A.2] and the
total carbon decomposition in kg/day in [M.1.B.5], we can derive the dry
matter loss in kg/day by simply adding those 2 quantities in kg/day. To
represent the loss at the scale of the total solids we need to double
the mass of carbon decomposition because we assume the carbon content of
the total solids remains constant at 50% (Font-Palma, 2019). (See
example calculation in section - step 4 below)

   :math:`{DM}_{loss}^{OpenLot} = {2 \times C}_{decomp}^{OpenLot} + {Emis}_{{CH}_{4}}^{OpenLot}`
   **[M.1.C.1]**

The total manure in the Open Lot for the next day is updated with the
following equation:

   :math:`{VS}_{t + 1}^{OpenLot} = {VS}_{t}^{OpenLot} - \left( {Emis}_{{CH}_{4}}^{OpenLot} \right)_{t} + {VS}_{t + 1}^{Manure}\ `
   **[M.1.C.2]**

   :math:`{TS}_{t + 1}^{OpenLot} = {TS}_{t}^{OpenLot} - \left( {DM}_{loss}^{OpenLot} \right)_{t} + {TS}_{t + 1}^{Manure}\ `
   **[M.1.C.3]**

**Numerical Example of Accounting for Dry Matter loss via Methane
Emissions and Carbon Decomposition within a time step (daily).**

To estimate the dry matter loss in kg from the manure through methane
and carbon decomposition we first estimate methane loss from volatile
solids (VS) in kg and carbon decomposition in kg. Let the initial Manure
mass be 100 kg, the initial total solid be TS =12 kg, and the initial
volatile solid mass be VS = 10.2 kg. The ambient temperature T is set at
30 :sup:`o`\ C.

**Step 1: Calculate the carbon lost as**
:math:`\mathbf{Emis}_{\mathbf{C}\mathbf{H}_{\mathbf{4}}}^{\mathbf{OpenLot}}`
**(methane) using [M.1.A.1] and [M.1.A.2]**

The Initial VS = 10.2 kg, then the methane loss is 0.03 kg/day. Plugging
[M.1.A.1] into [M.1.A.2],

.. math:: {Emis}_{CH_{4}}^{OpenLot} = \frac{VS \times B_{0} \times 0.67 \times (0.0625\  \times T - 0.25)\ }{100}

Plugging our numerical values into the equation lead to
:math:`{Emis}_{CH_{4}}^{OpenLot} = 10^{- 2} \times \left( 10.2 \times 0.24 \times 0.67\  \times (0.0625\  \times 30 - 0.25) \right) =`
0.03 kg/day.

**Step 2: Calculate the updated VS:**

The new VS remaining = Initial VS – Methane loss + Manure additions.
Assuming no manure is added the next day the updated VS on day *t+1* is:

.. math:: {VS}_{t + 1}^{OpenLot} = {VS}_{t}^{OpenLot} - \left( {Emis}_{CH_{4}}^{OpenLot} \right)_{t} = 10.2 - 0.030 = 10.17\ kg

**Step 3: Calculate the carbon lost to decomposition:**

To represent the loss at the scale of the total solids we double the
mass of carbon decomposition; hence the total solid loss becomes 0.00182
kg (as detailed below).

*Example calculations to solve [M.1.B.1] to [M.1.B.5]*

Let’s assume, Manure TS = 12 kg/day, C\ :sub:`manure` = 0.5 of manure
TS. Then,

C\ :sub:`man`\ = 6 kg/day

T\ :sub:`\_layer` = 60℃

T = 30 ℃

O\ :sub:`2` = 0.1

O\ :sub:`2,amb` = 0.21

O\ :sub:`2,hsat` = 0.02

τ is set to 2 days

decay = 0.10

:math:`{Rate}_{decomp}^{Effective}`\ = 2.37 x 10-3 (dimensionless).

:math:`{NbDays}^{last\ till}` = 1

:math:`lag` = 2

F\ :sub:`m,decomp` = 0.65

Number of days from the start of composting or last turning event (t) =
1

:math:`{Effect}_{Moist}` = 0.65

**By solving, we get:**

:math:`{Rate}_{decomp}^{Max}`\ = 0.0419 [M.1.B.1]

:math:`{Rate}_{decomp}^{slow}`\ = 0.008 [M.1.B.2]

:math:`{Rate}_{decomp}^{C}\ `\ = 0.00026 [M.1.B.3]

:math:`{Effect}_{C}^{Anae\ }`\ = 0.91270 [M.1.B.4]

Finally, using the values and calculations above, we get:

:math:`C_{decomp}^{OpenLot\ }`\ **= 0.0009 kg C/d** [M.1.B.5]

**Step 4: Calculated the updated TS**

To convert the mass of carbon lost into Dry matter we assume the carbon
content of manure TS is 50%:

(0.0009 kg C)\* 2 = 0.00182 kg TS/d

The updated Total solids = Initial Total Solids– Methane loss – Carbon
decomposition scaled up to the total solids + Manure TS additions. With
a mass 12 kg of initial total solids and assuming no manure additions,
let :math:`{TS}_{t + 1}^{OpenLot}` be the updated TS in kg in the next
period such that:

.. math:: {TS}_{t + 1}^{OpenLot} = {TS}_{t}^{OpenLot} - \left( {Emis}_{CH_{4}}^{OpenLot} \right)_{t} - {2 \times \left( C_{decomp}^{OpenLot} \right)}_{t} = 12\ –\ 0.03\  - 0.00182 = 11.968kg

**Step 5: Calculate the updated Manure mass:**

Since the proportion of total solids in the original open lot manure mix
remains the same at 12 %, we can set up another equation to determine
the updated manure mass :math:`M_{t + 1}^{OpenLot}`:

.. math:: M_{t + 1}^{OpenLot} = \frac{{TS}_{t + 1}^{OpenLot}}{0.12}\  = 99.73\ kg

Therefore, the updated manure-bedding mix mass after losing 0.032 kg of
total solids is approximately 99.73 kg.

**Section 2. Accounting for Phosphorus (P) and Potassium (K) contents in
the Open lots**

Cows continuously produce manure containing phosphorus (P) and potassium
(K). Hence, P and K are added daily to the open lot manure mix. In
subsection A and B, we account for those changes in P and K mass.

A. **Phosphorous Content in the Open lots**

P is added daily to the manure mix. P is further divided into 4 pools,
each corresponding to 4 distinct forms of P: 1) water extractable
inorganic (WIP), 2) water extractable organic (WOP), 3) non-water
extractable inorganic (NWIP), 4) non-water extractable organic (NWOP).
We will then calculate daily changes in total P and in each of its
sub-pools.

Let :math:`P_{t + 1}^{OpenLot}`\ be the total mass of P in the manure
mix at time :math:`t + 1` , in kg. The general equation, for all forms
of P is such that:

.. math:: P_{t + 1}^{OpenLot} = P_{t}^{OpenLot} + P_{t}^{animal} - P_{t}^{loss}

Where,

:math:`P_{t}^{OpenLot}` is the total accumulated P in the previous
period :math:`t`, in kg.

:math:`P_{t}^{animal}` is the mass of P present in the manure execrated
by the animal in the previous period :math:`t`, in kg.

:math:`P_{t}^{loss}`\ is the mass of P loss in the previous period
:math:`t`, in kg.

In words, the updated mass of P in Open lots at time :math:`t + 1` sums
what was already accumulated at time :math:`t` with what was added in
the previous period :math:`t` (through P present in the open lot manure
and from the additional manure execrated by the animal). It then
subtracts the losses in P in the previous period :math:`t`.

For this version of the Open Lot model, we make 2 simplifying
assumptions:

i.  The masses of different forms of P will come from the animal module.

ii. There are no losses in P within the Open Lot practice
    :math:`P_{t + 1}^{loss} = 0\ \forall t`.

Under such assumptions, the equations for updating the mass all 4 forms
of phosphorus (P) contained in the open lot manure mix can be expressed
as follows:

:math:`P_{t + 1}^{OpenLot,\ pool} = P_{t}^{OpenLot,\ pool} + P_{t}^{animal,\ pool}`
**[M.2.A.1]**

:math:`Wh`\ ere,

:math:`pool \in \left\{ P,WIP,WOP,\ NWIP,NWOP \right\}`

and the corresponding relative proportion
:math:`\% P_{t + 1}^{OpenLot,\ pool}` for each
:math:`pool \in \left\{ P,WIP,WOP,\ NWIP,NWOP \right\}` becomes:

   :math:`P_{t + 1}^{OpenLot,\ pool} = \frac{P_{t + 1}^{OpenLot,\ pool}}{\sum_{pool}^{}P_{t + 1}^{OpenLot,\ pool}}`
   **[M.2.A.2]**

B. **Potassium Content in the Manure mix**

Potassium K gets added continuously to the open lot manure mix through
manure production.

Let :math:`K_{t + 1}^{OpenLot}`\ be the total mass of K in the open lot
manure mix at time :math:`t + 1` such that:

.. math:: K_{t + 1}^{OpenLot} = K_{t}^{OpenLot} + K_{t}^{animal} - K_{t}^{loss}

Here, we make one simplifying assumption:

i. There are no losses in K within the open lot practice
   :math:`K_{t}^{loss} = 0\ \forall t`

..

   :math:`K_{t + 1}^{OpenLot} = K_{t}^{OpenLot} + K_{t}^{animal} - K_{t}^{loss}`
   **[M.2.B.1]**

**Section 3. Nitrogen losses: Ammonia Emissions, Leaching, and Nitrous
Oxide Emission**

The total nitrogen in the manure changes daily and lead to ammonia
emissions, nitrous oxide loss and N leaching. Here we simply keep track
of what is added and what is lost (no tillage/turning considered)

For this version of the Open Lot model the mass of N will come solely
from the animal module.

A. **Nitrogen Loss to Ammonia Emissions**

..

   Let :math:`\left( {Emis}_{NH_{3}}^{OpenLot} \right)_{t}`\ be the
   emissions of ammonia in kg at time t (daily):

:math:`\left( {Emis}_{NH_{3}}^{OpenLot} \right)_{t} = 0.36 \times \left( N_{t}^{animal} \right)`
**[M.3.A.1]**

Where\ **,**

:math:`N_{t}^{animal}`\ is the mass of nitrogen present in the manure
excreted by the animals at time t (daily) in kg.

B. **Nitrogen Loss to Leaching**

..

   :math:`\left( {Leach}_{N}^{OpenLot} \right)_{t}`\ be the mass in kg
   of Nitrogen leached out of the manure mix at time t (daily):

   :math:`\left( {Leach}_{N}^{OpenLot} \right)_{t} = 0.035 \times \left( N_{t}^{animal} \right)`
   **[M.3.B.1]**

Where,

:math:`N_{t}^{animal}`\ is the mass of nitrogen present in the manure
excreted by the animals at time t (daily) in kg.

C. **Nitrogen Loss to Nitrous Oxide Emissions**

Let :math:`\left( {Emis}_{NO_{2}}^{OpenLot} \right)_{t}`\ be the
emissions of Nitrous Oxide at time t (daily), in kg, such that:

   :math:`\left( {Emis}_{NO_{2}}^{OpenLot} \right)_{t} = 2.10^{- 2} \times \left( N_{t}^{animal} \right)`
   **[M.3.C.1]**

Where,

:math:`N_{t}^{animal}` is the mass of nitrogen present in the manure
excreted by the animals at time t (daily) in kg.

D. **Total Mass of Nitrogen, Organic Nitrogen, Inorganic Nitrogen, and
   Ammonium**

Let :math:`N_{t}^{OpenLot}` be the total mass in kg of Nitrogen in the
open lot manure mix at :math:`t`, such that:

:math:`N_{t}^{OpenLot} = \left( N_{t - 1}^{OpenLot} \right) + \left( N_{t}^{animal} \right) - \left( E_{NH_{3}}^{OpenLot} \right)_{t} - \left( {Leach}_{N}^{OpenLot} \right)_{t} - \left( E_{NO_{2}}^{OpenLot} \right)_{t}`
**[M.3.D.1]**

Let :math:`\left( N_{organic}^{OpenLot} \right)_{t}`\ be the mass in kg
of organic nitrogen in the open lot manure mix at :math:`t` (daily),
such that:

   :math:`\left( N_{organic}^{OpenLot} \right)_{t} = 0.952 \times N_{t}^{OpenLot}`
   **[M.3.D.2]**

Let :math:`\left( N_{inorganic}^{OpenLot} \right)_{t}`\ be the mass in
kg of inorganic nitrogen in the open lot manure mix at :math:`t`, such
that:

   :math:`\left( N_{inorganic}^{OpenLot} \right)_{t} = (1 - 0.952) \times N_{t}^{OpenLot} = 0.048\  \times N_{t}^{OpenLot}`
   **[M.3.D.3]**

Finally, the mass of ammonium in kg is estimated to be half of the
inorganic Nitrogen. Let :math:`\left( {NH_{4}}^{OpenLot} \right)_{t}` be
the mass of ammonium in kg at time t such that:

   :math:`\left( {NH_{4}}^{OpenLot} \right)_{t} = 0.5 \times \left( N_{inorganic}^{OpenLot} \right)_{t}`
   **[M.3.D.4]**

**Numerical Example of Accounting for Nitrogen and its Composition
within a time step.**

For each time period, to calculate the total nitrogen remaining and its
composition (different forms of N), we need to subtract the nitrogen
lost as 1) ammonia emissions
:math:`\left( {Emis}_{NH_{3}}^{OpenLot} \right)_{t}`, 2) leaching
:math:`\left( {Leach}_{N}^{OpenLot} \right)_{t}`, and 3) Nitrous oxide
emissions :math:`\left( {Emis}_{NO_{2}}^{OpenLot} \right)_{t}` .

Let’s walk through a numerical example where the Open Lot manure N mass
from manure excretion at time t (daily) is 1.5 kg and there is no
remaining nitrogen from the previous day (i.e.,
:math:`\left( N_{t - 1}^{OpenLot} \right) = 0`)

:math:`N_{t}^{animal} = 1.5\ kg`.

**Step 1: Calculate the nitrogen lost as**
:math:`\left( \mathbf{Emis}_{\mathbf{N}\mathbf{H}_{\mathbf{3}}}^{OpenLot} \right)_{\mathbf{t}}`
**(Ammonia) using [M.3.A.1]**

Given that 36% of the excreted nitrogen is lost as NH\ :sub:`3`, the
estimate of Nitrogen lost as NH\ :sub:`3` is
:math:`\left( {Emis}_{NH_{3}}^{OpenLot} \right)_{t} = 0.36 \times 1.5 = 0.54\ kg`

**Step 2: Calculate the nitrogen lost through**
:math:`\left( \mathbf{Leach}_{\mathbf{N}}^{OpenLot} \right)_{\mathbf{t}}`\ **(leaching)
using [M.3.B.1]**

Given that 3.5% of the excreted nitrogen is lost through leaching, the
estimate of Nitrogen lost through leaching is
:math:`\left( {Leach}_{N}^{OpenLot} \right)_{t} = 0.035 \times 1.5 = 0.0525\ kg`

**Step 3: Calculate the Nitrous Oxide Emissions**
:math:`\left( \mathbf{Emis}_{\mathbf{N}\mathbf{O}_{\mathbf{2}}}^{OpenLot} \right)_{\mathbf{t}}`\ **using
[M.3.C.1]**

Given that 7% of the excreted nitrogen is lost through Nitrous Oxide
emissions, the estimate of Nitrogen lost through Nitrous Oxide Emissions
if
:math:`\left( {Emis}_{NO_{2}}^{OpenLot} \right)_{t} = 2 \times 10^{- 2} \times 1.5 = 0.03\ kg.`

**Step 4: Calculate the total nitrogen lost using [M.3.A.1], [M.3.B.1],
and [M.3.C.1]**

Total nitrogen lost = Nitrogen lost as Ammonia Emission + Nitrogen lost
through leaching + Nitrogen lost through N\ :sub:`2`\ O emissions

Total nitrogen lost = 0.54 + 0.0525 + 0.03 = 0.6225 kg

**Step 5: Calculate the total nitrogen remaining after losses using
[M.3.D.1]**

Total nitrogen remaining = Nitrogen daily excreted - Total nitrogen lost

Total nitrogen remaining =
:math:`N_{t}^{OpenLot} = 1.5 - 0.6225 = 0.8775\ kg`

So, after accounting for the losses (ammonia emissions, leaching, and
Nitrous Oxide emissions), the total nitrogen remaining is 0.8775 kg.

**Step 6: Calculate the different pools of nitrogen based on the
remaining total nitrogen - organic nitrogen, inorganic nitrogen, and the
ammonium within the inorganic nitrogen.**

To calculate the different components of nitrogen based on the remaining
total nitrogen (0.5925 kg) and the given fractions:

**Step 6a: Calculate the Mass of organic Nitrogen using [M.3.D.2]**

Given that 95.2% of the total nitrogen is organic, the mass of organic
nitrogen at time *t* is
:math:`\left( N_{organic}^{OpenLot} \right)_{t} = 0.952 \times 0.8755 = 0.8358\ kg`

**Step 6b: Calculate the amount of inorganic nitrogen using [M.3.D.3]**

Given that 4.8% of the total nitrogen is inorganic, the mass of
inorganic nitrogen at time *t* is
:math:`\left( N_{inorganic}^{OpenLot} \right)_{t} = 4.8 \times 10^{- 2} \times 0.8775 = 0.04218\ kg.`

**Step 6c: Calculate the ammonium (inorganic nitrogen) using [M.3.D.4]**

Given that 50% of the inorganic nitrogen is ammonium, the mass of
ammonium at time *t* is
:math:`\left( {NH_{4}}^{OpenLot} \right)_{t} = 0.5 \times 0.04218 = 0.0219kg.`


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

Font-Palma, Carolina. "Methods for the treatment of cattle manure—a
review." *C* 5.2 (2019): 27. https://doi.org/10.3390/c5020027
