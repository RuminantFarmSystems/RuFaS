I. **Overview**

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
of 120 days' worth of storage capacity. Outdoor slurry storage design
calculations also take into account the additional volume from
precipitations.

II.  **Existing Solution**

III. **Proposed Solution**

**Section 1. Methane Emissions**

The model developed by Sommer et al. (2004) and Chianese et al. (2009)
aims to simulate the production and emission of methane (CH\ :sub:`4`)
from barn floor and manure storage facilities. The equations focus on
the degradation of volatile solids (VS) present in the manure,
considering factors like temperature and storage time to estimate
methane emissions from these storage systems.

In the following 2 sub-sections, we model methane emissions from the
Barn floor and from the outdoor storage respectively.

A. **Methane Emissions Calculations – Barn floor**

Manure on housing facility floors (free stall and tie stall) is a small
source of CH\ :sub:`4` emissions. Those methane emissions have been
measured from barn floors. Chianese et al., 2009 used such data to infer
a simple relationship between CH\ :sub:`4` emissions and ambient
temperature in the barn. This relationship predicts reasonable emission
rates for ambient temperatures greater than 0°C and is the best
currently available method to calculate CH\ :sub:`4` emissions from free
stall and tie stall barn floors. When temperature are below 0°C, there
are no methane emissions.

Before calculating methane emissions let us determine the surface area
of the barn that is covered with manure. Methane emissions are an
increasing function of the area of the spread.

Here, we assume that exposed manure surface areas are constant across
animal types. The soiled areas assigned to tie stall and free stall
facilities are 1.2 m\ :sup:`2` per cow in tie stall, 3.5 m\ :sup:`2` per
cow in free stall, 1.0 m\ :sup:`2` per growing cow in tie stall, and 2.5
m\ :sup:`2` per growing cow in free stall. These areas are fixed for the
duration of a simulation.

Let :math:`A_{manure}^{barn}`\ be the total barn area soiled with manure
in m\ :sup:`2` such that:

:math:`A_{manure}^{barn} = \ 1.2 \times N_{cow,tie} + 3.5 \times N_{cow,free} + 1 \times N_{growing,tie} + 2.5 \times N_{growing,free}`
[**M.1.A.1**]

where,

:math:`N_{cow,tie}`\ is the number of cows in tie stall,

:math:`N_{cow,free}`\ is the number of cows in free stall,

:math:`N_{growing,tie\ }`\ is the number of growing animals in tie
stall,

:math:`N_{growing,free\ \ }`\ is the number of growing animals in free
stall.

Let :math:`{Emis}_{CH_{4}}^{Barn\ Floor}` be the methane emissions in
kg/day from the barn floor such that:

   :math:`{Emis}_{CH_{4}}^{Barn\ Floor} = \frac{Max\ (0,0.13T) \times A_{manure}^{barn}}{1000}`
   [**M.1.A.2**]

where,

T is the temperature in :sup:`o`\ C,

:math:`A_{manure}^{barn}` is barn surface area covered with manure in
m\ :sup:`2` calculated in [M.1.A.1].

B. **Methane Emissions Calculations – Outdoor Storage**

We use an adaptation of Sommer et al. (2004) and Chianese et al. (2009)
to calculate daily emissions of methane, given the ambient barn
temperature, and a methane conversion factor for the manure management.
Below, all the parameters and values for the manure storage emissions
come from Sommer et al. (2004).

Let :math:`{Emis}_{CH_{4}}^{Outdoor\ Storage}` be the methane emissions
in kg per day from the outdoor storage such that:

:math:`{Emis}_{CH_{4}}^{Outdoor\ Storage} = exp\left( \ln A - \frac{E}{R \times T} \right) \times \left\lbrack \left( \frac{24 \times {VS}_{d} \times b_{1}}{1000} \right) + \left( \frac{24 \times {VS}_{nd} \times b_{2}}{1000} \right) \right\rbrack\ `
[**M.1.B.1**]

where,

A is the Arrhenius parameter, indicating the methane production rate (g
CH\ :sub:`4` kg\ :sup:`-1` VS h\ :sup:`-1`), with ln(A) = 43.33 g
CH\ :sub:`4` kg\ :sup:`‐1` VS h\ :sup:`‐1`,

E is the Apparent activation energy, in joules per mol (J
mol\ :sup:`-1`), set at E = 112,700 J mol\ :sup:`‐1`,

R is a gas constant in of joules per kelvin per mol (J K\ :sup:`-1`
mol\ :sup:`-1`), set at 8.314 J K\ :sup:`‐1` mol\ :sup:`‐1`,

T is the temperature in kelvin K,

:math:`{VS}_{d}`\ and :math:`{VS}_{nd}` are the degradable and
non-degradable volatile solids in the manure, in g,

:math:`b_{1}`\ and :math:`b_{2}`\ are unitless correcting factors set at
:math:`b_{1} = 1` and :math:`b_{2} = 0.0`\ 1.

C. **The Daily Dry Matter Available, Daily Dry Matter Loss, and Manure
   mass update**

The daily dry matter loss is simply what is lost from the volatile
solids in the dry matter from methane emissions. Using the estimated
emissions of methane in kg per day from the barn floor manure and the
outdoor manure storage in [M.1.A.2] and [M.1.B.1] respectively, we can
then derive the dry matter loss in kg per day. Let
:math:`{DM}_{loss}^{Slurry\ Outdoor}`\ be the dry matter loss in kg per
day such that:

:math:`{DM}_{loss}^{Slurry\ Outdoor} = {Emis}_{CH_{4}}^{Barn\ Floor}\  + \ {Emis}_{CH_{4}}^{Outdoor\ Storage}`
**[M.1.C.1]**

**Numerical Example of Accounting for Dry Matter loss via Methane
Emissions within a time step.**

Here, using arbitrary numerical values, we estimate the dry matter loss
in kg from the barn floor and outdoor manure storage through methane
emissions.

**Step 1: Calculate the methane loss from barn floor and outdoor storage
using [M.1.A.2] and [M.1.B.1]**

Let’s consider a free stall barn with one cow on a day where ambient
temperature T = 15 °C.

:math:`N_{cow,tie} = N_{growing,tie\ } = N_{growing,free\ }0`, and
:math:`N_{cow,free} = 1`

Using [M.1.A.1], we know :math:`A_{manure}^{barn} =` 3.5 m\ :sup:`2`
**,** plugging this into [M.1.A.2] yields:

:math:`{Emis}_{CH_{4}}^{Barn\ Floor} = \frac{(0.13 \times 15) \times 3.5}{1000} = 6.8 \times 10^{- 3}\ kg.{day}^{- 1}`

Let the initial volatile solids be :math:`{VS}_{d}\  = 950\ g` and total
solids mass be :math:`{VS}_{nd}\  = 70\ g`:

.. math:: {{VS}_{total} = VS}_{d} + {VS}_{nd}\  = 1020\ g

If Total Solids is such that TS = 12 kg

(Note: :math:`{VS}_{d},\ {VS}_{nd}\ `\ from the animal module are in kg,
so we convert them to grams for the follow equation)

:math:`{Emis}_{CH_{4}}^{Outdoor\ Storage} = exp\left( \ln(43.33) - \frac{112,700}{8.314 \times 15} \right) \times \left\lbrack \left( \frac{24 \times 950 \times 1}{1000} \right) + \left( \frac{24 \times 70 \times 0.01}{1000} \right) \right\rbrack = 0.56\ kg.{day}^{- 1}\ `

**Step 2: Calculate the updated Volatile Solids**

The new VS remaining = Initial VS – Methane loss:

.. math:: {VS}_{t + 1}^{Slurry\ Outdoor} = {VS}_{t}^{Slurry\ Outdoor} - \left( {Emis}_{CH_{4}}^{Barn\ floor} \right)_{t} - \ \left( {Emis}_{CH_{4}}^{Outdoor\ Storage} \right)_{t} = \frac{(950 + 70)}{1000} - 7 \times 10^{- 3}\  - \ 0.56 = 9.63\ kg

**Step 3: Calculate the updated Total Solids**

The updated Total solids = Initial Total Solids – Methane loss. With a
mass 12 kg of initial total solids, let
:math:`{TS}_{t + 1}^{slurry\ Outdoor}` be the updated TS in kg in the
next period such that:

.. math:: {TS}_{t + 1}^{Slurry\ Outdoor} = {TS}_{t}^{Slurry\ Outdoor} - \left( {Emis}_{CH_{4}}^{Barn\ floor} \right)_{t} - \left( {Emis}_{CH_{4}}^{Outdoor\ Storage} \right)_{t}

.. math:: = 12\ –\ 7 \times 10^{- 3}\  - \ 0.56

.. math:: = 11.43\ kg

**Manure mass:**

Every day, the outdoor manure in storage loses dry matter. This loss is
estimated and subtracted from the initial total manure mass to generate
a new total for the next period.

Assume the initial total slurry manure in outdoor storage is 100 kg, 12
kg of which is in total solids. Additionally, suppose the daily dry
matter loss is 0.57 kg. We can update the total manure mass using the
following equation:

 :math:`{TS}_{t + 1}^{Slurry\ Outdoor} = {TS}_{t}^{Slurry\ Outdoor} - \left( {DM}_{loss}^{Slurry\ Outdoor} \right)_{t}`

Plugging in the numerical value in this example yield

 :math:`{TS}_{t + 1}^{Slurry\ Outdoor} = 12 - 0.57 =` 11.43 kg

Since the proportion of total solids in the manure is 12 %, let the
updated manure mass :math:`M_{t + 1}^{Slurry\ Outdoor}`\ be such that:

.. math:: M_{t + 1}^{Slurry\ Outdoor} = \frac{{TS}_{t + 1}^{Slurry\ Outdoor}}{0.12}\  = 95.25\ kg

Therefore, the updated outdoor manure mass after losing 0.567 kg of
total solids is 95.25 kg.

**Section 2. Accounting for Phosphorus (P) and Potassium (K) contents in
the Outdoor Storage**

Cows continuously produce manure containing phosphorus (P) and potassium
(K). Hence, P and K get added daily to the outdoor slurry manure
storage. In subsection A and B below, we account for those changes in P
and K mass.

A. **Phosphorous Content in the Outdoor Manure Storage**

P gets added daily to the manure storage. P is further divided into 4
pools, each corresponding to 4 distinct forms of P: 1) water extractable
inorganic (WIP), 2) water extractable organic (WOP), 3) non-water
extractable inorganic (NWIP), 4) non-water extractable organic (NWOP).
We will then calculate daily changes in total P and in each of its
sub-pools.

Let :math:`P_{t + 1}^{Slurry\ Outdoor}`\ be the total mass of P in the
outdoor manure storage at time :math:`t + 1` , in kg. The general
equation, for all forms of P is such that:

.. math:: P_{t + 1}^{Slurry\ Outdoor} = P_{t}^{Slurry\ Outdoor} + P_{t}^{bedding} + P_{t}^{animal} - P_{t}^{loss}

where,

:math:`P_{t}^{Slurry\ Outdoor}` is the total accumulated P in the
previous period :math:`t`, in kg.

:math:`P_{t}^{bedding}` is the mass of P present in the bedding material
added in the previous period :math:`t`, in kg.

:math:`P_{t}^{animal}` is the mass of P present in the manure execrated
by the animal in the previous period :math:`t`, in kg.

:math:`P_{t}^{loss}`\ is the mass of P loss in the previous period
:math:`t`, in kg.

In words, the updated mass of P in the outdoor manure storage at time
:math:`t + 1` sums what was already accumulated at time :math:`t` with
what was added in the previous period :math:`t` (through P present in
the added bedding material and from the manure execrated by the animal).
It then subtracts the losses in P in the previous period :math:`t`.

For this version, we make 3 simplifying assumptions:

i.   The mass of P in the bedding material is negligeable and set at 0,
     :math:`P_{t}^{bedding} = 0\ \forall t.`

ii.  The masses of different forms of P will be received from the animal
     module.

iii. There are no losses in P within the manure storage
     :math:`P_{t + 1}^{loss} = 0\ \forall t`.

Under such assumptions, the equations for updating the mass all 4 forms
of phosphorus (P) contained in outdoor manure storage can be expressed
as follows:

   :math:`P_{t + 1}^{Slurry\ Outdoor,\ pool} = P_{t}^{Slurry\ Outdoor,\ pool} + P_{t}^{animal,\ pool}`
   **[M.2.A.1]**

where,

:math:`pool \in \left\{ P,WIP,WOP,\ NWIP,NWOP \right\}`

and the corresponding relative proportion
:math:`\% P_{t + 1}^{Slurry\ Outdoor,\ pool}` for each
:math:`pool \in \left\{ P,WIP,WOP,\ NWIP,NWOP \right\}` becomes:

   :math:`\% P_{t + 1}^{Slurry\ Outdoor,\ pool} = \frac{P_{t + 1}^{Slurry\ Outdoor,\ pool}}{\sum_{pool}^{}P_{t + 1}^{Slurry\ Outdoor,\ pool}}`
   **[M.2.A.2]**

B. **Potassium Content in the Outdoor Manure Storage**

Potassium K gets added continuously to the outdoor manure storage
through cows ‘manure production.

Let :math:`K_{t + 1}^{Slurry\ Outdoor}`\ be the total mass of K in the
outdoor manure storage at time :math:`t + 1` such that:

.. math:: K_{t + 1}^{Slurry\ Outdoor} = K_{t}^{Slurry\ Outdoor} + K_{t}^{bedding} + K_{t}^{animal} - K_{t}^{loss}

Here, we make 2 simplifying assumptions:

i.  The mass of K in the bedding material is negligeable and set at 0,
    :math:`K_{t}^{bedding} = 0\ \forall t.`

ii. There are no losses in K within the outdoor manure storage
    :math:`K_{t}^{loss} = 0\ \forall t`

:math:`K_{t + 1}^{Slurry\ Outdoor} = K_{t}^{Slurry\ Outdoor} + K_{t}^{bedding} + K_{t}^{animal} - K_{t}^{loss}`
**[M.2.B.1]**

**Section 3. Ammonia Emissions**

Ammonia loss from manure can be predicted using a relationship for
NH\ :sub:`3` volatilized from the surface of an aqueous solution
containing ammonium where the NH\ :sub:`3` is transported to the free
atmosphere through a pathway with a finite resistance. Assuming a very
low (zero) concentration of NH\ :sub:`3` in the free atmosphere,
volatile loss can be determined using (Rotz and Oenema, 2006).

Note that the same equation is applicable for barn and storage
emissions, the only difference is that the mass of the manure solution
on the floor (M) includes the mass of urine for barn emissions and
manure mass only for outdoor storage emissions.

A. **Ammonia Emissions Calculations – Barn floor and Outdoor Storage**

The daily NH\ :sub:`3`\ −N emissions are determined assuming the exposed
urine and manure characteristics are relatively constant throughout each
day. Although manure is typically removed at intervals within a day,
scraping also tends to mix urine and feces and spread a thin surface
layer that remains on the floor surface.

**Barn emissions** –

Here, the exposed urine surface areas in free stall is assumed to be 3.5
m\ :sup:`2` per cow. For growing animals, surface areas were 2.0
m\ :sup:`2` for dairy heifers under one year of age and 2.5 m\ :sup:`2`
for heifers over one year of age.

The exposed urine surface area in tie stall barn is assumed to be 1.5
m\ :sup:`2` per cow, which is twice the open gutter surface area behind
each animal.

Hence the area of exposed urine in the barn is such that:

:math:`A_{urine}^{Outdoor\ Slurry} = \ 1.5 \times N_{cow,tie} + 3.5 \times N_{cow,free} + 2 \times N_{heifer < 1year,free} + 2.5 \times N_{heifer \geq 1year,free}`
[**M.3.A.1**]

where,

:math:`N_{cow,tie}`\ is the number of cows in tie stall,

:math:`N_{cow,free}`\ is the number of cows in free stall,

:math:`N_{heifer < 1year,free\ }`\ is the number of Heifer less than one
year old in free stall,

:math:`N_{heifer \geq 1year,free\ \ }`\ is the number of Heifer one year
old and older in free stall.

Using the area of exposed urine in the barn area calculated above, let
:math:`M_{urine}` be the mass per square meter of the urine on the floor
in kg.m\ :sup:`-2` such that:

   :math:`M_{urine} = \frac{Urine}{A_{urine}^{barn}}` [**M.3.A.2**]

where,

Urine is the daily urine excreted by the housed animals in kg,

:math:`A_{urine}^{Outdoor\ Slurry}\ `\ is the exposed urine surface area
m\ :sup:`2`.

Lastly, let :math:`M_{urine\ TAN}` be the urine TAN exposed surface area
in kg.m\ :sup:`-2` such that:

   :math:`M_{urine\ TAN} = \frac{Urine\ TAN}{A_{urine}^{barn}}`
   [**M.3.A.3**]

where,

Urine TAN is the daily urine TAN excreted by the housed animals in kg,

:math:`A_{urine}^{Outdoor\ Slurry}\ `\ is the exposed urine surface area
m\ :sup:`2`.

**Storage emissions** – Here, the exposed manure surface areas in
outdoor manure storage :math:`A_{manure}^{Outdoor\ Slurry}`\ in
m\ :sup:`2` is obtained from user input. Using the area of exposed
manure in the outdoor manure storage, let :math:`M_{manure}` be the mass
per square meter of the manure in kg.m\ :sup:`2` such that:

   :math:`M_{manure} = \frac{Manure}{A_{manure}^{Outdoor\ Slurry}}`
   [**M.3.A.4**]

where,

Manure is the daily manure excreted by the animals in kg,

:math:`A_{manure}^{Outdoor\ Slurry}`\ is the exposed manure surface area
m\ :sup:`2`.

Lastly, let :math:`M_{manure\ TAN}` be the manure TAN exposed surface
area in kg.m\ :sup:`-2` such that:

   :math:`M_{manure\ TAN} = \frac{Manure\ TAN}{A_{manure}^{Outdoor\ Slurry}}`
   [**M.3.A.5**]

where,

Manure TAN is the daily manure TAN excreted by the housed animals in kg,

:math:`A_{manure}^{Outdoor\ Slurry}\ `\ is the outdoor exposed manure
surface area m\ :sup:`2`.

Before proceeding with NH\ :sub:`3` loss calculations, we need to derive
the equilibrium coefficient :math:`Q` for the NH\ :sub:`3` gas in the
air for a given concentration of TAN in the solution using Henry’s law
of distribution. Since :math:`Q` is a function of Henry’s law
coefficient :math:`K_{h}\ `\ and a dissociation of ammonium coefficient
:math:`K_{a}^{Solution}`, we will compute those first. These two
coefficients are a function of temperature and pH such that:

   :math:`K_{h} = 10 \times \left( \frac{1478}{T + 273} - 1.69 \right)`
   **[M.3.A.6]**

   :math:`K_{a}^{Solution} = 1 + 10 \times \left( \frac{0.09018 + 2729.9}{T + 273} - pH \right)`
   **[M.3.A.7]**

where,

Solution :math:`\in \left\{ urine,manure \right\}`,

T is the ambient temperature in °C as a proxy for manure solution
temperature [1]_,

pH is the pH of the solution set by default at 7.7 for urine/Barn and at
7.8 for manure /Outdoor Storage.

Using the coefficient derived above in [M.3.A.6] - [M.3.A.7], we can now
compute the unitless equilibrium coefficient :math:`Q(Solution)` as:

   :math:`Q(Solution) = K_{h} \times K_{a}^{Solution}` **[M.3.A.8]**

where,

Solution :math:`\in \left\{ urine,manure \right\}`,

:math:`K_{h}` is the Henry’s law coefficient,

:math:`K_{a}^{Solution}` is the dissociation of ammonium coefficient for
a given solution.

Next, we derive :math:`r` the resistance of NH\ :sub:`3` transport from
the urine surface in the barn to the free atmosphere in s.m\ :sup:`-1`
such that:

   :math:`r_{urine} = HSC \times \left( 1 - 0.027 \times (20 - T) \right)`
   **[M.3.A.9]**

where,

HSC is a housing-specific constant s.m\ :sup:`-1` set at 260.

For the manure in the outdoor storage, the resistance r of NH\ :sub:`3`
transport from the manure surface to the free atmosphere in
s.m\ :sup:`-1` is such that:

:math:`r_{manure} = 75` if the manure surface is covered with crust,

:math:`r_{manure} = 19` if the manure surface is not covered with crust,

:math:`r_{manure} = 10` if the manure is in a solid state.

Lastly, let :math:`{NH_{3}}_{volatilization}^{Slurry\ Outdoor}` be the
NH\ :sub:`3` loss during enclosed animal housing in kg
N.m\ :sup:`-2`.d\ :sup:`-1`, such that:

   :math:`{NH_{3}}_{volatilization}^{Slurry\ Outdoor}(solution) = \frac{M_{\ solution\ TAN} \times c \times y}{r_{solution}\  \times M_{solution} \times Q(Solution)}`
   **[M.3.A.10]**

where,

Solution :math:`\in \left\{ urine,manure \right\}`,

TAN is total ammoniacal N in the manure solution in kg N m\ :sup:`-2`,

c is the time conversion constant = 86400 s d\ :sup:`-1`,

y is manure and urine specific density, set to be 1000 kg.m\ :sup:`-3`,

:math:`r_{solution}` is the resistance of NH\ :sub:`3` transport in
s.m\ :sup:`-1` derived above,

:math:`M_{solution}` is the solution mass per unit area of exposed
surface in kg.m\ :sup:`-2`,

   :math:`Q(Solution)` is the dimensionless equilibrium coefficient for
   the NH\ :sub:`3` gas in the air for a given concentration of TAN in
   the solution computed in [M.3.A.8],

   To get the total NH\ :sub:`3` emissions, let us multiply
   :math:`{NH_{3}}_{volatilization}^{Slurry\ Outdoor}`\ in kg
   N.m\ :sup:`-2`.d\ :sup:`-1` by
   :math:`A_{solution}^{Outdoor\ Slurry}`, the exposed surface area of
   the solution :math:`\in \left\{ urine,manure \right\}`, in
   m\ :sup:`2`:

.. math:: TOTAL\ {NH_{3}}_{volatilization}^{Slurry\ Outdoor}(solution) = \frac{M_{\ solution\ TAN} \times c \times y}{r_{solution}\  \times M_{solution} \times Q(Solution)} \times A_{solution}^{Outdoor\ Slurry}

   **[M.3.A.11]**

Using calculations of the daily loss of ammonia in
:math:`kg\ N.m^{- 2}`\ above, the updated manure and urine TAN in
kg.m\ :sup:`-2`.d\ :sup:`-1` are such that:

:math:`\left( {TAN}_{solution}^{Slurry\ Outdoor} \right)_{t + 1} = \left( {TAN}_{solution}^{Slurry\ Outdoor}\  \right)_{t} + \left( M_{solution\ TAN} \right)_{t} - \left( {NH}_{3\ Volatisation}^{Slurry\ Outdoor} \right)_{t}`
**[M.3.A.12]**

:math:`\left( TOTAL\ {TAN}_{solution}^{Slurry\ Outdoor} \right)_{t + 1} = \left( \left( {TAN}_{solution}^{Slurry\ Outdoor}\  \right)_{t} + \left( M_{solution\ TAN} \right)_{t} - \left( {NH}_{3\ Volatisation}^{Slurry\ Outdoor} \right)_{t} \right) \times A_{solution}^{Outdoor\ Slurry}`
**[M.3.A.13]**

where,

Solution :math:`\in \left\{ urine,manure \right\}`.

**Numerical Example of Accounting for ammonia emissions within a time
step.**

Estimate the N loss in kg from the barn floor and manure storage through
ammonia.

**Step 1: Calculate the ammonia lost from barn floor using [M.3.A.1] -
[M.3.A.13]**

**Barn emissions** - The urine solution mass on the floor (M) was
determined as the daily urine excreted by the housed animals divided by
the exposed surface area (kg/m\ :sup:`2`).

   :math:`{NH_{3}}_{volatilization}^{Slurry\ Outdoor}(urine) = \frac{M_{urine\ TAN} \times c \times y}{r_{urine}\  \times M_{urine} \times Q(urine)}`

If we have one cow in a free stall with Urine = 21 kg:

the area :math:`A_{urine}^{Outdoor\ Slurry} = 3.5\ m2`,

:math:`M_{urine} = \frac{Urine}{A_{urine}^{Outdoor\ Slurry}} = \frac{21}{3.5} = 6\ kg.m^{- 2}`.

If we set the urine TAN mass from the animal module at 0.21 kg,

:math:`M_{urine\ TAN} = \frac{Urine\ TAN}{A_{urine}^{Outdoor\ Slurry}} = \frac{0.21}{3.5} = 0.06\ kg.m^{- 2}`.

With T = 15 °C **,** T = 288.2 K, and pH = 7.7, HSC =260 s.m\ :sup:`-1`
, c = 86400 s.d\ :sup:`-1` , and y = 1000 kg.m\ :sup:`-3`

.. math:: K_{h} = 10 \times \left( \frac{1478}{15 + 273} - 1.69 \right) = 2749.6\ 

.. math:: K_{a}^{Urine} = 1 + 10 \times \left( \frac{0.09018 + 2729.9}{15 + 273} - 7.7 \right) = 75

.. math:: Q(urine) = K_{h} \times K_{a}^{urine} = 2749.6 \times 75 = \ 203815

.. math:: r_{urine} = HSC \times \left( 1 - 0.027 \times (20 - T) \right) = 260 \times \left( 1 - 0.027 \times (20 - 15) \right) = 224.9

Finally, plugging in those values in:

.. math:: {NH_{3}}_{volatilization}^{Slurry\ Outdoor}(urine) = \frac{M_{urine\ TAN} \times c \times y}{r_{urine}\  \times M_{urine} \times Q(urine)}

.. math:: = \frac{0.06 \times 86400 \times 1000}{224.9 \times 6 \times 203815} = 0.019\ kg\ N.m^{- 2}{.d}^{- 1}

.. math:: TOTAL\ {NH_{3}}_{volatilization}^{Slurry\ Outdoor}(urine) = \frac{M_{urine\ TAN} \times c \times y}{r_{urine}\  \times M_{urine} \times Q(urine)} \times A_{urine}^{Outdoor\ Slurry}\ \  = \frac{0.06 \times 86400 \times 1000}{224.9 \times 6 \times 203815} \times 3.5 = 0.066\ kg\ N.d^{- 1}

**Step 2: Cumulative loss and Remaining TAN**
:math:`kg\ N.m^{- 2}d^{- 1}`

Cumulative loss = Summation of ammonia lost each day
:math:`kg\ N.m^{- 2}d^{- 1}`

   = 0.019 :math:`kg\ N.m^{- 2}d^{- 1}`

Remaining Urine TAN daily = Initial TAN daily - Daily loss of ammonia
:math:`kg\ N.m^{- 2}`

.. math:: \left( {TAN}_{urine}^{Slurry\ Outdoor} \right)_{t + 1} = \left( {TAN}_{urine}^{Slurry\ Outdoor}\  \right)_{t} + \left( M_{urine\ TAN} \right)_{t} - \left( {NH}_{3\ Volatisation}^{Slurry\ Outdoor} \right)_{t}

   = 0 + 0.060 – 0.019

   = 0.041 :math:`kg\ N.m^{- 2}{.d}^{- 1}`

Total remaining TAN **=** Remaining TAN \* Area of barn (kg N/cow)

.. math:: \left( TOTAL\ {TAN}_{solution}^{Slurry\ Outdoor} \right)_{t + 1} = \left( \left( {TAN}_{urine}^{Slurry\ Outdoor}\  \right)_{t} + \left( M_{urine\ TAN} \right)_{t} - \left( {NH}_{3\ Volatisation}^{Slurry\ Outdoor} \right)_{t} \right) \times A_{urine}^{Outdoor\ Slurry} = 0.041 \times 3.5 = 0.143\ kg\ N.{cow}^{- 1}

**Step 3: Calculate the ammonia lost from storage using [M.3.A.1] -
[M.3.A.13]**

**Storage emissions** - The manure mass (M) in the outdoor storage was
determined as the daily manure mass divided by the exposed surface area
(kg/m\ :sup:`2`).

   :math:`{NH_{3}}_{volatilization}^{Slurry\ Outdoor}(manure) = \frac{M_{manure\ TAN} \times c \times y}{r_{manure}\  \times M_{manure} \times Q(manure)}`

.. math:: {TOTAL\ NH_{3}}_{volatilization}^{Slurry\ Outdoor}(manure) = \frac{M_{manure\ TAN} \times c \times y}{r_{manure}\  \times M_{manure} \times Q(manure)} \times A_{manure}^{Outdoor\ Slurry}

The TAN in storage on a given day was the accumulated TAN removed from
the housing facility plus a portion of the organic N entering storage.
The TAN entering storage each day was the urinary N excreted minus the
TAN lost in the housing facility.

Since Urine TAN Is also mixed with manure before entering storage, so we
consider the following.

If we set the manure TAN mass from the animal module at 0.23 kg,

Urine Total remaining
:math:`\left( TOTAL\ {TAN}_{solution}^{Slurry\ Outdoor} \right)_{t + 1}`
= 0.143 kg N (from Step 2 above)

:math:`M_{manure\ TAN} = \frac{manure\ TAN}{A_{urine}^{Outdoor\ Slurry}} = \frac{0.23\  + \ 0.143}{200} = 0.0019\ kg.m^{- 2}`.

If we have one cow in a free stall with Manure = 75 kg: the area
:math:`A_{urine}^{Outdoor\ Slurry} = 200\ m2`, (Set Model User )

:math:`M_{manure\ } = \frac{Manure}{A_{urine}^{Outdoor\ Slurry}} = \frac{75}{200} = 0.375\ kg.m^{- 2}`.

For the manure mass, the daily dry matter loss should be subtracted from
the total manure. (Methane emissions from storage, Step 3 – Daily TS
loss kg)

M = 75 / 200

M = 0.375 kg/m\ :sup:`2`

T = 15 °C

T = 288.2 K

pH = 7.5

HSC =260 s/m

c = 86400 s/d

ρ = 1000 kg/m3

By solving above, we get

K\ :sub:`h` = 2766.6

K\ :sub:`manure` = 75

Q = 207384.6

HSC = housing specific constant (260 s/m)

r storage = 75 (manure with crust)

r storage = 19 (manure without crust)

r storage = 10 (solid manure)

Use, r = 75 for this calculation (manure with crust)

**Step 3: Cumulative losses**

Cumulative loss = Summation of ammonia storage each day

.. math:: {NH_{3}}_{volatilization}^{Slurry\ Outdoor}(manure) = \frac{M_{manure\ TAN} \times c \times y}{r_{manure}\  \times M_{manure} \times Q(manure)}

   :math:`= \ \frac{0.0019\  \times 864000 \times \ 1000}{75\  \times \ 0.375\ \  \times \ 207384.6}`
   = 0.00029 :math:`kg\ N.m^{- 2}d^{- 1}`

.. math:: {TOTAL\ NH_{3}}_{volatilization}^{Slurry\ Outdoor}(manure) = \frac{M_{manure\ TAN} \times c \times y}{r_{manure}\  \times M_{manure} \times Q(manure)} \times A_{manure}^{Outdoor\ Slurry}

   :math:`= \frac{0.0019\  \times 864000 \times \ 1000}{75\  \times \ 0.375\ \  \times \ 207384.6} \times 200\  = \ 0.058`
   :math:`kg\ N.d^{- 1}`

**
References**

Chianese, D. S., C. A. Rotz, and T. L. Richard. "Simulation of methane
emissions from dairy farms to assess greenhouse gas reduction
strategies." *Transactions of the ASABE* 52.4 (2009): 1313-1323.

https://elibrary.asabe.org/abstract.asp?aid=27781

Rotz, C. A., & Oenema, J. (2006). Predicting management effects on
ammonia emissions from dairy and beef farms. Transactions of the ASABE,
49(4), 1139-1149.

https://elibrary.asabe.org/abstract.asp?aid=21731&t=2&redir=&redirType=

.. [1]
   Note that manure/barn temperature won’t be the same as ambient
   temperature, this needs to be reviewed
