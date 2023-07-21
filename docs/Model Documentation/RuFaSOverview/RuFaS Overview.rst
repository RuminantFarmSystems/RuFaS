   **Ruminant Farm Systems Model: Development Progress and
   Applications**

   | K. F. Reed
   | Department of Animal Science
   | Cornell University

**Model Background**

Simulation models are a tool that can guide policy, support farm
decisions, and evaluate novel technologies. Models can estimate multiple
outcomes that result from of management changes or adoption of new
technologies and provide a more robust, systematic evaluation than
isolated research experiments. Examples of whole-farm models for dairy
production include the Integrated Farm Systems Model (Rotz et al.,
2013), DairyMod (Johnson et al., 2008), DyNoFlo (Cabrera et al., 2006),
and SIMS(DAIRY) (Del Prado et al., 2011). However, wide-scale industry
adoption of these models has not occurred due to limitations in model
applications for current and future scenario analysis. Existing model
structure and code bases prevent model adaptation or development of
features like data integration and novel management scenarios that would
encourage widespread. Thus, we are developing a new farm simulation
model that can adapt to changing technologies and support sustainable
dairy production (Kebreab et al., 2019).

The Ruminant Farm Systems Model (RuFaS, Figure 1) applies modern
computer coding practices centered around clarity and adaptability to
respond to evolving technologies in the dairy industry. RuFaS embraces
the key characteristics for next-generation agricultural systems models
described by Jones et al. (2017) so that it can be adaptable as new
technology arises, be interoperable with other software and models, and
meets user needs by continuous interaction with stakeholders during the
development process.

Our development team includes scientists from 5 universities and several
USDA-ARS stations who represent a range of disciplines. Rather than
relying on research scientists to fill the role of translating their
model equations and algorithms into computer code, we work closely with
computer scientists to develop the modular codebase. We emphasize
thorough documentation at all steps of model development. The scientists
develop detailed pseudocode that provide heuristic descriptions of the
model processes, literature references, and the mathematical equations.
Similarly, the computer scientists provide in-code comments that
describe the flow of information and references to equation numbers from
the pseudocode to link the computer code directly to the scientific
documentation.

The Ruminant Farm System (RuFaS) model is based on a foundation of four
biophysical modules (animal, manure handling, crop + soil, and feed
storage) that represent the main components of a dairy farm as shown in
Figure 1. The simulation inputs include the desired length of the
simulation, herd characteristics, manure management strategy, crop
characteristics, and other elements of farm management. We

use a tiered file structure for inputs that separates inputs that
designate whole farm and simulation structure from inputs specific to
each of the modules with increasing level of detail associated with
inputs at lower tiers. Model outputs are exported to CSV files, graphic
images, and an SQL database. The model uses a daily time-step and is
programmed in Python, an adaptable and easy to read computer programming
language.

   .. image:: RuFaSOverviewGraphs/media/image1.png
      :width: 6.44167in
      :height: 3.77083in

Figure 1. Conceptual diagram of the Ruminant Farm Systems model

**Progress Updates**

Model Inputs and Management Options

Through the model inputs, the user defines the farm management and
environment for each simulation scenario. At the farm level, the user
specifies the target lactating cow number, the replacement rate and
growing herd size, the housing type and size, purchased and growing
feeds, field number and size, and provides the weather (temperature,
solar radiation, precipitation) during the simulation period. At the
herd level, the user can specify the breed and reproduction protocols.
The model primarily uses the Wood’s lactation curve to estimate the
baseline milk production for each cow on each day of lactation and this
baseline production can be adjusted to fit desired farm or total
lactation production by modifying the lactation curve parameters. Other
animal characteristics that can be modified by the user include
parameters that define the bodyweight distribution, reproductive
efficiency, and probability of disease.

The model user defines a manure management strategy for each animal pen
to provide the flexibility to represent different manure compositions
and handling methods based on the animal group. The method and frequency
of manure collection, treatment

and processing methods, and storage length and type are all set by the
user for each pen or group of pens.

The Crop and Soil Module has similar flexibility to represent a range of
crop production practices. The user can specify any number of fields,
each with its own size, soil properties, crop rotation, and tillage,
fertilization, planting, and harvest practices. Crop growth in RuFaS is
based on the methods used in the Soil and Water Assessment Tool (Neitsch
et al., 2011) and currently has the ability to simulate corn, alfalfa,
soybeans, rye, winter wheat, meadow fescue, and beets.

The feed storage module is much simpler than the rest of the model in
its current state and provides only empirical estimates of forage
composition change, emissions, and leachate for silage and hay storage.
This module estimates changes in forage composition during storage once
per season which is the only part of the model that does not function on
a daily timestep.

Nutrient Cycling and Outputs

RuFaS simulates transformation, export, and loss of biomass,
agriculturally significant elements (N, P, and K) and H2O as they cycle
through the 4 modules that represent a dairy farm. The Feed Storage
module tracks the composition and inventory of farm grown feeds. This
information is passed to the Animal Module and used, in combination with
purchased feeds, by the automated, least-cost diet formulation
algorithms to simulate feed delivery each day. The diet formulation
algorithms are currently based on the NRC (2001) Nutrient Requirements
for Dairy Cattle though we hope to update them soon. The Animal Module
uses a Monte Carlo stochastic framework to simulate each individual
animal as they move through their lifecycle on the farm which is
represented by 5 distinct animal classes. Detailed descriptions of the
ration formulation methods and the life events simulated by the Animal
Module are provided in our recent publication (Hansen et al., 2021). The
simulated intake, diet composition and characteristics of each
individual animal drive the estimates for partitioning of the diet N, P,
and K into milk, body mass, and manure to maintain a mass balance of
these important elements at the animal level. Manure organic matter and
enteric methane emissions are also estimated. Daily production of manure
from each animal is summed per pen and the total manure mass and
composition (DM content, volatile solids, degradable volatile solids, N,
K, P, soluble P, and ammonia concentration) are passed to the Manure
Module.

The Manure Module first simulates ammonia emissions from the barn floor
after excretion and before cleaning and then combines the bedding, flush
water, and parlor cleaning water into a simulated reception pit.
Currently the model can represent both flushing and scraping cleaning
systems from tie stall and free stall pens. Compost bedded-pack barns
and dry-lot housing systems are still in development. After the
reception pit, the model simulates movement of the combined manure and
wastewater to either long term storage or for processing. Current
options for manure processing include mechanical solid-liquid separation
and anaerobic digestion. Manure emissions and composition change are
estimated at each daily step during manure handling, processing, and
storage.

On the days when the Crop and Soil Module simulates manure application
to fields, the Manure Module passes information about the amount and
composition of the manure in storage and subtracts the mass of the
simulated manure application from the stored quantities. The Crop and
Soil Module then simulates daily biogeochemical nutrient and water
transformation, crop uptake, and loss from the soil profile based on a
combination of the SWAT (Neitsch et al., 2011), SurPhos (Vadas, 2009)
and DayCent (Del Grosso et al., 2011) models. Crop growth rate and
composition is based on solar radiation, temperature, and water and N
availability. At harvest, above ground crop biomass is partitioned into
crop residue that remains on the field and that which is transferred to
the Feed Storage Module to inventory management, completing the dairy
farm nutrient cycle.

Model Applications

One of the features that sets RuFaS apart from other farm simulation
models is the objective for the model to be used for both research and
as a decision support tool for the dairy industry. The detailed
documentation and use of Python language will facilitate research use by
empowering future scientists to understand, modify, and update the model
as part of their research program. For industry applications, the
flexibility built into the model structure and multiple options for each
management decision will support the industry need to estimate current
environmental footprints and to inform sustainable decision making.

For example, one type of management decision that RuFaS could support is
determination of the reproduction protocols. A recent case study
compared two different synchronization protocols (5dCoSynch and
OvSynch56) under two different voluntary waiting periods. By including
these options in a farm system model, RuFaS is able to provide estimates
of the impact of these decisions on the expected feed consumption,
enteric methane production, and manure production. For example, in a
preliminary comparison, we found that a shorter voluntary waiting period
reduced the enteric methane intensity of milk production but that the
improved conception rate of the OvSynch56 protocol, did not appear to
reduce the methane intensity in comparison to the 5dCoSynch protocol.

Farm system impacts of diet changes or improvements in feed efficiency
are another example of an application of RuFaS to inform management
decisions. In the case study we presented in Hansen et al. (2021) we
demonstrate that RuFaS is able to compare changes in feed efficiency by
assigning a stochastic residual feed intake (RFI, kg/d) value to
individual animals. As expected, improved efficiency and reduced RFI
decreased enteric methane and manure production. However, the percent
decrease in both enteric methane and manure emissions were not
equivalent to the percent increase in feed efficiency due to
non-linearities in the system. Thus, RuFaS can provide estimates of
expected environmental benefits from nutrition and breeding programs to
improve feed efficiency that account for interactions between the diet,
animals, herd dynamics, and downstream farm management choices.

**References**

Cabrera, V. E., P. E. Hildebrand, J. W. Jones, D. Letson and A. De
Vries. 2006. "An integrated north florida dairy farm model to reduce
environmental impacts under seasonal climate variability." Ag., Ecosys.,
and Environ. 113: 82-97.

Del Grosso, S. J., Parton, W. J., Mosier, A. R., Hartman, M. D.,
Brenner, J., Ojima, D.

   S., & Schimel, D. S. 2001. Simulated interation of carbon dynamics
   and nitrogen trace gas fluxes using the DAYCENT model. In M.
   Schaffer, L. Ma, & S. Hansen (Eds.), *Modeling Carbon and Nitrogen
   Dynamics for Soil Management.* (pp. 303-332). CRC Press.

Del Prado, A., T. Misselbrook, D. Chadwick, A. Hopkins, R. Dewhurst, P.
Davison, A.

Butler, J. Schröder and D. Scholefield. 2011. Simsdairy: A modelling
framework to identify sustainable dairy farms in the uk. Framework
description and test for organic systems and n fertiliser optimisation.
Sci. Tot. Environ. 409: 3993-4009. Hansen, T.L., M. Li, J. Li, C.J.
Vankerhove, M.A. Sortirova, J.M. Tricarico, V.E. Cabrera, E. Kebreab,
K.F. Reed. 2021. The Ruminant Farm Systems Animal Module: A nagement.
Animals. 11:1373.

   .

Johnsoard, A. Parsons, M. Lambert and B. Cullen.

   2008. "Dairymod and ecomod: Biophysical pasture-simulation models for
   australia and new zealand." Aust. J. Exp. Ag. 48: 621-31.

Jones, J. W., J. M. Antle, B. Basso, K. J. Boote, R. T. Conant, I.
Foster, H. C. J.

   Godfray, M. Herrero, R. E. Howitt, S. Janssen\ *, et al.* 2017. Brief
   history of agricultural systems modeling

   10.1016/j.agsy.2016.05.014.

| Kebreab, E., K.F.Reed, V.E. Cabrerew modeling environment for
  integrated dairy system management. Animal
| Frontiers.9: doi: 10.1093/af/vfz004
| Neitsch, S.L., J.G. Arnold, J.R. Kiniry, and J.R. Williams. 2011. Soil
  and Water
| Assessment Tool Theoretical Documentation: Version 2009. Texas Water
  Resources Institute Technical Report No. 406.

NRC. Nutrient requirements of dairy cattle seventh revised edition.
2001. Washington, D.C.: The National Academies Press.

Rotz, C., B. Isenberg, K. Stackhouse-Lawson and E. Pollak. 2013. "A
simulation-based approach for evaluating and comparing the environmental
footprints of beef production systems." J Anim. Sci. 91 : 5427-37.

Vadas, P. A. 2009. Surface Phosphorus and Runoff Model: Theorhetical
Documentation. Madison, WI: US Dairy Forage Research Center.
