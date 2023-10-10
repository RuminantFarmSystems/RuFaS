Chianese et al 2009 Methane
===========================

SIMULATIONOF METHANE EMISSIONSFROM DAIRY FARMSTO

ASSESS GREENHOUSE GAS REDUCTION STRATEGIES

D. S. Chianese, C. A. Rotz, T. L. Richard

   **ABSTRACT.** *As a sector, agriculture is reported to be the second
   greatest contributor to atmospheric methane (CH4) in the U.S.,
   emitting 31% of the total emission. Primary sources of CH4 on dairy
   farms are the animals and manure storage, with smaller contributions
   from field‐applied manure, feces deposited by grazing animals, and
   manure on barn floors. The Integrated Farm System Model (IFSM) was
   expanded to include simulation of CH4 emissions from all farm sources
   along with modules predicting other greenhouse gas (GHG) emissions.
   The new CH4 module incorporated previously published relationships
   and experimental data that were consistent with our modeling
   objectives and the current structure of IFSM. When used to simulate*

*previously reported experiments, the model was found to predict enteric
fermentation and slurry manure storage emissions similar to those
measured. In simulating a representative 100‐cow dairy farm in
Pennsylvania, the model predicted a total*

   *average annual emission of 21 Mg CH4. This included annual emissions
   of 142 kg CH4 per cow from the Holstein herd and 6.4 kg CH4 per m3 of
   slurry manure in storage, which were consistent with previously
   summarized emission data. To illustrate the use of the expanded
   whole‐farm model, potential CH4 reduction strategies were evaluated.
   Farm simulations showed that increasing the production and use of
   forage (corn silage) in animal diets increased CH4 emission by 16%
   with little impact on the global warming potential of the net farm
   emission of all GHGs. Use of grazing along with high forage diets
   reduced*

   *net farm GHG emission by 16%. Using an enclosed manure storage and
   burning the captured biogas reduced farm emission of CH4 by 32% with
   a 24% reduction in the net farm emission of GHG. Incorporation of GHG
   emission modules in IFSM provides a tool for estimating whole‐farm
   emissions of CH4 and evaluating proposed reduction strategies along
   with their impact on net GHG emission and other environmental and
   economic measures.*

   **Keywords.** *Dairy farm, Greenhouse gas, Methane, Simulation
   model.*

   (GHGs) are causing a change in the global climate (IPCC, T
   (representing a 95% confidence level or higher) that anthropogenic
   emissions of greenhouse gases he Intergovernmental Panel on Climate
   Change (IPCC) has reported that it is “extremely likely”

   2007). Although many mitigation plans currently focus on re‐ducing
   carbon dioxide (CO2) emissions, methane (CH4) is a stronger GHG, with
   a global warming potential about 25�times that of CO2 (IPCC, 2007).
   The Food and Agriculture Organization of the United Nations (FAO,
   2006) has claimed that livestock emit 37% of anthrogenic CH4 on a
   global basis. In 2007, agriculture was reported to be the second
   greatest contributor of total CH4 emission in the U.S. with 31%,
   be‐hind only the energy sector (41%) and a little greater than hu‐man
   waste management (28%) in overall impact (EIA, 2007). Therefore,
   quantifying and reducing CH4 emissions

   Submitted for review in July 2008 as manuscript number SE 7621;
   approved for publication by the Structures & Environment Division of
   ASABE in July 2009. Presented at the 2008 ASABE Annual Meeting as
   Paper No. 084098.

   The authors are **Dawn Sedorovich Chianese, ASABE Member Engineer,**
   Associate, ENVIRON International Corporation, Los Angeles,
   California; **C. Alan Rotz, ASABE Fellow,** Agricultural Engineer,
   USDA‐ARS Pasture Systems and Watershed Management Research Unit,
   University Park, Pennsylvania; and **Tom L. Richard, ASABE Member
   Engineer,** Associate Professor, Department of Agricultural and
   Biological Engineering, The Pennsylvania State University, University
   Park, Pennsylvania. **Corresponding author:** C. Alan Rotz, USDA‐ARS,
   Building 3702, Curtin Road, University Park, PA 16802; phone:
   814‐865‐2049; fax: 814‐863‐0935; e‐mail: al.rotz@ars.usda.gov.

   from livestock farms is important for developing more sus‐tainable
   production systems.

   Multiple processes emit CH4 from dairy farms, including enteric
   fermentation in animals and microbial processes in manure. A review
   of agricultural emission data shows that the majority of CH4 from
   dairy farms is created through en‐teric fermentation, followed by
   emissions from manure stor‐ages (Chianese et al., 2009c). In addition
   to these major sources, smaller emissions result from field‐applied
   manure and manure deposited by animals inside barns or on pasture.
   Recent research has shown that plants may also emit CH4, al‐though
   the mechanism is not currently known (Keppler and Röckmann, 2007).
   Most field studies (e.g., Sherlock et al., 2002), as well as our
   review of agricultural emissions (Chia‐nese et al., 2009c), report
   croplands as a negligible source, or small sink, of CH4 over full
   production years. However, field‐applied manure can result in
   significant emissions for a few days after application (Chadwick and
   Pain, 1997; Sher‐lock et al., 2002).

   Computer simulation provides a cost‐effective and effi‐cient method
   of estimating CH4 emissions from dairy farms and analyzing how
   management scenarios affect these emis‐sions. The Integrated Farm
   System Model (IFSM; USDA‐ARS, University Park, Pa.) is a
   process‐based, whole‐farm simulation including major components for
   soil processes, crop growth, tillage, planting and harvest
   operations, feed storage, feeding, herd production, manure storage,
   and eco‐nomics (Rotz et al., 2009). IFSM predicts the effect of
   man‐agement scenarios on farm performance, profitability, and

Transactions of the ASABE

+-----------------------+-----------------------+-----------------------+
|    Vol. 52(4):        |    2009 American      | 1313                  |
|    1313-1323          |    Society of         |                       |
|                       |    Agricultural and   |                       |
|                       |    Biological         |                       |
|                       |    Engineers ISSN     |                       |
|                       |    0001-2351          |                       |
+=======================+=======================+=======================+
+-----------------------+-----------------------+-----------------------+

environmental pollutants such as nitrate leaching, ammonia
volatilization, and phosphorus runoff loss.

Our goal was to develop a tool for estimating GHG emis‐sions from dairy
farms and quantifying management effects on emissions. To accomplish
this, modules were incorpo‐rated in IFSM to simulate processes
controlling CH4 emis‐sions. Specific objectives were to review published
models for simulating CH4 emissions, identify relationships that best
fit our modeling goals, adapt those models for use in IFSM, verify that
the models gave reasonable predictions, and dem‐onstrate the use of this
tool in predicting whole‐farm CH4 emissions and the impact of reduction
strategies. The CH4 module was developed along with modules simulating
CO2 (Chianese et al., 2009a) and nitrous oxide (N2O, Chianese et al.,
2009b) emissions to predict net farm emission of GHG.

| **MODEL DEVELOPMENT**
| The Integrated Farm System Model is a simulation model that integrates
  the major biological and physical processes of a crop, beef, or dairy
  farm (Rotz et al., 2009). Crop produc‐tion, feed use, and the return
  of manure nutrients back to the land are simulated over each of 25
  years of weather. Growth and development of alfalfa, grass, corn,
  soybean, and small grain crops are predicted based on daily soil and
  weather con‐ditions. Tillage, planting, harvest, storage, and feeding
  op‐erations are simulated to predict resource use, timeliness of
  operations, crop losses, and nutritive changes in feeds. Feed
  allocation and animal response are related to the nutritive value of
  available feeds and the nutrient requirements of the animal groups
  making up the herd. The quantity and nutrient content of the manure
  produced is a function of the quantity and nutrient content of the
  feed consumed. Nutrient flows through the farm are modeled to predict
  nutrient accumula‐tion in the soil and loss to the environment.
  Environmental impacts include nitrogen (N) volatilization from manure
  sources, soil denitrification and leaching losses, erosion of
  sediment, and sediment‐bound and soluble phosphorus (P) losses in
  runoff. Whole‐farm mass balances of N, P, and po‐tassium are
  determined as the sum of all nutrient imports in feed, fertilizer,
  deposition, and legume fixation minus the ex‐ports in milk, excess
  feed, animals, manure, and losses leav‐ing the farm. Simulated
  performance is then used to determine production costs, incomes, and
  economic return for the farm production system.

| To include CH4 emissions in IFSM, relationships were needed to predict
  the emission from each important farm source. Enteric fermentation and
  manure (primarily manure storages) are the major sources of CH4 from
  farms, contribut‐ing about 65% and 30% of total agricultural CH4
  emission, respectively (EIA, 2007). Even though manure applied on
  fields, feces deposited on pasture, and manure on barn floors do not
  contribute large amounts of CH4, relationships were included for these
  sources to obtain a comprehensive predic‐tion of farm‐level emissions.
  A number of models have been published that predict emissions from the
  major sources. To create our module, we selected relationships that
  best fit our needs for whole‐farm simulation. Criteria used to
  evaluate potential models were:
| **1. The model had to be capable of simulating important processes
  that affect CH4 emissions with changes in farm management.**
  Strategies to reduce CH4 emissions from en‐

   teric fermentation primarily involve animal diet. Strategies to
   reduce CH4 emissions from manure storages include stor‐age covers and
   capturing and burning the gas. In order to ana‐lyze how these and
   other practices affect CH4 emissions, the model had to account for
   the associated processes (e.g., ani‐mal ration, manure type, and
   storage design).

   **2. The model had to provide process‐level representa‐tion of major
   emission components.** Several published models, as well as sections
   of the IPCC methodology, predict CH4 emissions from farms using
   emission factors (e.g.,�Schils et al., 2005; Lovett et al., 2006).
   While these models are useful as simple tools for estimating CH4
   emis‐sions, they do not have the capability of representing
   pro‐cesses that affect CH4 emissions. For example, Schils et al.
   (2005) simulated CH4 emissions due to enteric fermentation in heifers
   and calves by multiplying a group‐specific emis‐sion factor by the
   number of animals in each group. This model only accounted for the
   effect of animal numbers and would not account for diet
   modifications. Our goal was to se‐lect physically and biologically
   based relationships that also satisfied criterion 1.

   **3. The model had to satisfactorily predict observed data over a
   full range of potential conditions.** The chosen relationships had to
   satisfactorily predict CH4 emissions within the range of observed
   emissions from the given farm component over the full range of
   possible farm characteris‐tics.

   **4. The model had to be consistent with the current scale of other
   components in IFSM.** IFSM is designed to simulate realistic
   scenarios implemented on farms. Characteristics of these scenarios
   are designated at the farm management level (e.g., available feeds,
   sequence of machinery operations, ma‐nure storage duration).
   Subsequently, IFSM simulates pro‐cesses, normally on a daily time
   step, at the field or farm level according to the assumed farm
   characteristics. As a result, se‐lected relationships and their
   associated inputs and parame‐ters had to function well at the field
   or farm level as opposed to other scales (e.g., microbiological or
   regional).

   **5. Model inputs and parameters were limited to readily available
   data.** Some available mechanistic models accu‐rately predict
   emissions; however, these models typically re‐quire many inputs and
   parameters. The required values are often the result of calibration
   against observed data, are diffi‐cult to obtain, or have no physical
   or biological basis. The un‐certainty added by assuming these
   parameter values can outweigh the benefit of using a highly
   mechanistic model. In contrast, the majority of parameters and inputs
   in IFSM are easily obtained through on‐farm observation. Thus, our
   final criterion was that input and parameter values were easily
   ob‐tained within, or consistent with, the current structure of IFSM.

   For the relatively minor emission sources of manure on the barn floor
   and feces of grazing animals, published models were not available. In
   these cases, simpler models or emis‐sion factors were used. This
   simpler approach was justified given their lesser importance in
   contributing to whole‐farm emissions.

   | **ENTERIC FERMENTATION**
   | Ruminant animals subsist primarily on forages. Like most animals,
     ruminants do not have the enzymes necessary to break down
     cellulose. However, bacteria in the rumen break down and obtain
     energy from cellulose in the forage con‐

   1314 TRANSACTIONSOFTHE ASABE

sumed by the animal, producing hydrogen as one by‐product. If the
produced hydrogen is allowed to build up in the rumen, it can lead to
acidosis, a health problem in dairy cows. How‐ever, enteric methanogens,
which exist in a symbiotic rela‐

   changes in animal nutrition and management. A detailed de‐scription
   of the selected model can be found in Mills et al. (2003). A brief
   description is provided here to document the model, parameters used,
   and the integration with IFSM.

+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| t |   |   |   |   |   |   |   |   |   |   |   | * | ⋅ | * | * | ) |   | ( |
| i |   |   |   |   |   |   |   |   |   |   |   | c |   | M | E |   |   | 1 |
| o |   |   |   |   |   |   |   |   |   |   |   | * |   | * | I | ] |   | ) |
| n | E |   |   |   |   |   |   |   |   |   |   |   |   |   | * | ⋅ | * |   |
| s | m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | F |   |
| h | i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i | s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p | s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| w | i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | k |   |
| i | o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | g |   |
| t | n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | C |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | H |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | 4 |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | * |   |
| h | o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e | f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c | C |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r | H |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o | 4 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a | i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n | s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s | p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i | r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n | e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t | d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h | i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e | c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r | t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u | e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m | d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| , |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p | a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r | s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e | : |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| v |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| ‐ |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| y |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| y |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| C |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| O |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| 2 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| C |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| H |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| 4 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| , |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| w |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   | * | * | = | [ | m | − | * | m | ⋅ | e | ( |   |   |   |   |   |   |   |
|   | E | e |   |   | a |   | E | a |   | x | − |   |   |   |   |   |   |   |
|   | C | n |   | * | x |   | * | x |   | p |   |   |   |   |   |   |   |   |
|   | H | t |   | E |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   | 4 | * |   | * |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   | * |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   | , |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| y |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| ‐ |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| . |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| O |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| y |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| ‐ |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

stood (Madigan et al., 2003). The amount of CH4 produced from enteric
fermentation is influenced by various factors in‐cluding animal type and
size, digestibility of the feed, and the intake of dry matter, total
carbohydrates, and digestible car‐bohydrates (Monteny et al., 2001;
Wilkerson et al., 1995).

A number of models have been published to predict the CH4 produced by
ruminant animals. The more mechanistic models (e.g., Baldwin et al.,
1987; Dijkstra et al., 1992; Mills et al., 2001) simulate the chemical
or microbiological pro‐cesses occurring in the rumen that produce CH4.
These mod‐els are often highly detailed and require many state variables
and equations. The more empirical models use equations re‐lating CH4
emissions to various factors such as feed intake (Blaxter and
Clapperton, 1965), feed characteristics (Moe and Tyrrell, 1979), milk
yield and live weight (Kirchgessner et al., 1991), dry matter intake and
feed characteristics (Yates et al., 2000), and metabolizable energy
intake and feed char‐acteristics (Mills et al., 2003). These models
range from equations based solely on statistical correlations to
biologi‐cally based relationships.

Reviews of both mechanistic and empirical models have been published
(Wilkerson et al., 1995; Benchaar et al., 1998; Mills et al., 2003).
Mechanistic models, such as that of Mills et al. (2001), have been shown
to explain more variation as compared to empirical models. Relative to
our model crite‐ria, these models satisfied only criteria 1, 2, and 3.
This mi‐crobiological approach required more detail than needed or
desired for simulating processes at the whole‐farm scale. More
importantly, the inputs and parameters required were not readily
available or easily set.

To best meet the needs of our farm model, a simpler ap‐proach was taken
using the Mitscherlich 3 (Mits3) equation developed by Mills et al.
(2003). Mits3 is a simple process model that satisfies all five
criteria. The model is based on di‐etary composition and is capable of
accounting for manage‐ment practices that alter the animal's intake and
diet. Mits3 is process‐based, relating CH4 emissions to dietary intake
as well as animal type and size. When compared to data from the U.S.,
Mits3 yielded a regression slope of 0.89 with an inter‐cept of 3.50 and
a square root of the mean square prediction error (MSPE) of 34.1% (Mills
et al., 2003). In addition, Mits3 predicts realistic emissions at the
extremes of parameter ranges. Thus, an additional benefit of the
nonlinearity of Mits3 is that the model predicts reasonable emissions
when applied to conditions outside those for which it was originally
developed.

The structure and data requirements of Mits3 were consis‐tent with the
scale needed for whole‐farm simulation. Only three model inputs were
required: starch content of the diet, acid detergent fiber (ADF) content
of the diet, and metaboliz‐able energy intake. These inputs were readily
obtained from the feed and animal components of IFSM. Through these
in‐puts, CH4 production was directly related to diet and indirect‐ly
related to animal number, size, and type. This allowed prediction of
changes in CH4 production as affected by

   where *ECH4,ent* is the emission due to enteric fermentation (kg CH4
   animal-1 day-1), *Emax* is the maximum possible emis‐sion (MJ CH4
   animal-1 day-1), *c* is a shape parameter deter‐mining how emissions
   change with increasing *MEI* (dimen-sionless), *MEI* is the
   metabolizable energy intake (MJ ani‐mal-1 day-1), and *FkgCH4* is the
   conversion of MJ to kg of CH4 (0.018 kg CH4 MJ-1). From Mills et al.
   (2003), the maxi‐mum possible emission is defined as 45.98 MJ CH4
   animal-1 day-1. This maximum possible emission is constant for all
   animals; the effect of animal size and type is indirectly pro‐vided
   through the value of *MEI*. The shape parameter, *c*, is calculated
   as:

+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
| *c* | =   | −   | .0  | 0   | ⋅   | ⎡\  | ⎤⎥⎦ | +   |     | (2) |
|     |     |     |     | 011 |     |  *S |     |     |  .0 |     |
|     |     |     |     |     |     | tar |     |     |     |     |
|     |     |     |     |     |     | ch* |     |     |   0 |     |
|     |     |     |     |     |     |     |     |     | 045 |     |
|     |     |     |     |     |     | ⎪⎣\ |     |     |     |     |
|     |     |     |     |     |     |  *A |     |     |     |     |
|     |     |     |     |     |     | DF* |     |     |     |     |
+=====+=====+=====+=====+=====+=====+=====+=====+=====+=====+=====+
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+

..

   where *Starch* is the starch content, and *ADF* is the acid
   deter‐gent fiber content of the diet. Equation 2 models the observed
   trend of increased CH4 emission with high‐fiber diets and de‐creased
   emission with high‐starch diets.

   To use the above equations, values were needed for the starch and ADF
   contents of diets and the metabolizable ener‐gy intake of each animal
   group making up the herd. IFSM de‐termines the ration that each
   animal group is fed based on a representative animal's nutritional
   requirements and the available feeds (Rotz et al., 1999). This
   information includes the required energy content of the diet (MJ kg
   DM-1), the to‐tal dry matter intake (kg DM day-1 animal-1), and the
   amount of each feed used. The first two parameters are used to
   calcu‐late *MEI*. The ADF contents of feeds used in IFSM are
   deter‐mined assuming a linear relationship with neutral detergent
   fiber (NDF) for each feed type (table 1). These relationships were
   developed using feed composition data from the Na‐tional Research
   Council (NRC, 2001). The starch contents of feeds are determined
   assuming a linear relationship with the amount of nonfiber
   carbohydrate (NFC) in the feed (table 1).

   The fraction of NFC is determined as:

+----+----+----+----+----+----+----+----+----+----+----+----+----+
| *F | =1 | −  | (  | +  | *F | +  | *  | *  | +  | *F |    | (  |
| NF |    |    | *F |    | C  |    | F* | fa |    | as |  ) | 3) |
| C* |    |    | ND |    | P* |    |    | t* |    | h* |    |    |
|    |    |    | F* |    |    |    |    |    |    |    |    |    |
+====+====+====+====+====+====+====+====+====+====+====+====+====+
+----+----+----+----+----+----+----+----+----+----+----+----+----+

..

   where *FNFC* is the fraction of NFC in the diet, *FCP* is the
   frac‐tion of crude protein (CP), *Ffat* is the fraction of fat, and
   *Fash* is the fraction of ash in the diet. The fractions of NDF and
   CP were available in IFSM; typical fractions of fat and ash (table 1)
   were obtained from the National Research Council (NRC, 2001). A given
   animal group is typically fed a mixture of feeds making up the whole
   diet. A weighted average of the individual feed characteristics in
   the ration is used to deter‐mine the starch and ADF contents of the
   full ration fed to each of the six possible animal groups making up
   the herd (Rotz et al., 1999).

   | **MANURE STORAGE**
   | During manure storage, CH4 is generated through a reac‐tion similar
     to that described for enteric fermentation. The

   Vol. 52(4): 1313-1323 1315

   **Table 1. Relationships used to model starch and acid detergent
   fiber (ADF) contents of feeds in IFSM.[a]**

+-----------------------+-----------------------+-----------------------+
|    Feed Type          | Starch                | ADF                   |
+=======================+=======================+=======================+
|                       | (fraction)            | (fraction)            |
+-----------------------+-----------------------+-----------------------+
|    Alfalfa hay        | 0.64*(1‐\ *FN         | 0.78\*\ *FNDF*        |
|                       | DF*\ ‐\ *FCP*\ ‐0.11) |                       |
+-----------------------+-----------------------+-----------------------+
|    Alfalfa silage     | 0.89*(1‐\ *FN         | 0.82\*\ *FNDF*        |
|                       | DF*\ ‐\ *FCP*\ ‐0.12) |                       |
+-----------------------+-----------------------+-----------------------+
|    Grass hay          | 0.45*(1‐\ *FN         | 0.61\*\ *FNDF*        |
|                       | DF*\ ‐\ *FCP*\ ‐0.11) |                       |
+-----------------------+-----------------------+-----------------------+
|    Grass silage       | 0.65*(1‐\ *FN         | 0.64\*\ *FNDF*        |
|                       | DF*\ ‐\ *FCP*\ ‐0.12) |                       |
+-----------------------+-----------------------+-----------------------+
|    Corn grain         | 0.68                  | 0.036                 |
+-----------------------+-----------------------+-----------------------+
|    High‐moisture corn | 0.52                  | 0.004                 |
+-----------------------+-----------------------+-----------------------+
|    Corn silage        | 0.80*(1‐\ *FN         | 0.62\*\ *FNDF*        |
|                       | DF*\ ‐\ *FCP*\ ‐0.07) |                       |
+-----------------------+-----------------------+-----------------------+
|    Perennial          |                       |                       |
|    grass/legume       |                       |                       |
+-----------------------+-----------------------+-----------------------+
|                       | 0.48*(1‐\ *FN         | 0.72\*\ *FNDF*        |
|                       | DF*\ ‐\ *FCP*\ ‐0.14) |                       |
+-----------------------+-----------------------+-----------------------+
|    Alfalfa pasture    | 0.48*(1‐\ *FN         | 0.55\*\ *FNDF*        |
|                       | DF*\ ‐\ *FCP*\ ‐0.14) |                       |
+-----------------------+-----------------------+-----------------------+
|    Protein supplement |                       |                       |
|    1                  |                       |                       |
+-----------------------+-----------------------+-----------------------+
|                       | 0.0                   | 0.0                   |
+-----------------------+-----------------------+-----------------------+
|    Protein supplement | 0.0                   | 0.0                   |
|    2                  |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    Fat additive       | 0.0                   | 0.0                   |
+-----------------------+-----------------------+-----------------------+

..

   [a] *FNDF* (fraction of neutral detergent fiber in feed) and *FCP*
   (fraction of crude protein in feed) are available in IFSM. The last
   value in the equations developed to predict starch content represents
   an average total of fat plus ash contents for the given feed. Typical
   values for fat and ash were obtained from NRC (2001).

   incorporating more recent developments and data. The mod‐el of Chen
   and Hashimoto (1980) was similar in design. Al‐though it could be
   applied to fresh manure, this model was primarily developed to
   simulate anaerobic digesters, and sev‐eral of the parameters were
   empirically determined based on data from digesters. Zeeman (1994)
   used biologically based equations to predict CH4 production but used
   emission fac‐tors, or a similar method, to predict the actual
   emission of CH4 from digested manure. Unlike the other models, the
   model of Sommer et al. (2004) was developed for more gen‐eral
   application to either digested or raw slurry manure.

   The model of Sommer et al. (2004) simulates the produc‐tion and
   emission of CH4 from manure storages based on the degradation of
   volatile solids (VS). Additional factors affect‐ing CH4 production
   are temperature and storage time. A de‐tailed description of the
   development of the model is found in Sommer et al. (2004). The model
   is presented here along with a brief discussion on how the parameters
   were deter‐mined and how the model was integrated with IFSM.

   Emission of CH4 from manure storage is predicted as:

+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   | * |   |   | = | 2 | ⋅ | * | , | ⋅ | * |   | ⋅ | e |   |   |   | ( |   | * |   | ⎤ |   |   |
|   | E |   |   |   | 4 |   | V | * |   | b |   |   | x |   |   |   |   |   | E |   |   |   |   |
|   | * |   |   |   |   |   | s | d |   | * |   |   | p |   |   |   | ) |   | * |   |   |   |   |
| c |   |   |   |   |   |   | * | * |   | 1 |   |   |   |   | | |   | − |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   | ⎡ |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   | | |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   | l |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | n |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | ⎪ |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | ⎣ |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| y |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| , |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| w |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| ‐ |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+
|   | * | , | * |   | 1 |   |   |   |   |   |   |   |   |   |   |   |   |   | * |   | ⎥ |   | ( |
|   | C |   | m |   | 0 |   |   |   |   |   |   |   |   |   |   |   |   |   | R |   | ⎦ |   | 4 |
|   | H |   | a |   | 0 |   |   |   |   |   |   |   |   |   |   |   |   |   | T |   |   |   | ) |
|   | 4 |   | n |   | 0 |   |   |   |   |   |   |   |   |   |   |   |   |   | * |   |   | ⎤ |   |
|   | * |   | * |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| v |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| . |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   | + | 2 | ⋅ | * | , | * | ⋅ | * |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   | 4 |   | V |   | n |   | b |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   | s |   | d |   | * |   |   |   |   |   |   |   |   |   |   |   |   |
| T |   |   |   |   |   |   | * |   | * |   | 2 |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   |   |   |   |   |   | ⋅ | e |   |   |   | ( |   | * |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   | x |   |   |   |   |   | E |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   | p |   |   |   | ) |   | * |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | | |   | − |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | ⎡ |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | | |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | l |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | n |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | ⎪ |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | ⎣ |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| C |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| H |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| 4 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| f |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| ‐ |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   | 1 |   |   |   |   |   |   |   |   |   |   |   |   |   |   | * |   |   |   |
|   |   |   |   |   | 0 |   |   |   |   |   |   |   |   |   |   |   |   |   |   | R |   |   |   |
|   |   |   |   |   | 0 |   |   |   |   |   |   |   |   |   |   |   |   |   |   | T |   |   |   |
| s |   |   |   |   | 0 |   |   |   |   |   |   |   |   |   |   |   |   |   |   | * |   | ⎥ |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | ⎦ |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| b |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| w |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| y |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| d |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| ( |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| M |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| ‐ |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| n |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| y |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| . |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| , |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| 2 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| 0 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| 0 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| 1 |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| ) |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| . |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| A |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| u |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| g |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| p |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| o |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| c |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| s |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| m |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| i |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| l |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| a |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| r |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| , |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| t |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| h |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| e |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

..

   temperature in the storage varies, in contrast to the relatively
   constant temperature in the rumen, and the manure in storage is more
   heterogeneous (e.g., the substrate is less well mixed, and some
   carbohydrates are already partially decomposed) as compared to the
   consistency of the rumen (Monteny et al., 2001).

   where *ECH4,man* is the emission of CH4 from the storage (kg�CH4
   day-1), *Vs,d* and *Vs,nd* are the degradable and nonde‐gradable VS
   in the manure (g), *b*\ 1 and *b*\ 2 are rate correcting factors
   (dimensionless), *A* is the Arrhenius parameter (g CH4 kg-1 VS h-1),
   *E* is the apparent activation energy (J mol-1), *R* is the gas
   constant (J K-1 mol-1), and *T* is the temperature

   Both mechanistic and empirical models have been devel‐ (K) (table 2).

   oped to predict CH4 emissions from manure storages. Unlike some of
   the empirical enteric fermentation models that sim‐

   From Sommer et al. (2004), the degradable volatile solids entering
   storage is:

+------+------+------+------+------+------+------+------+------+------+
|      | *V*  |      | =    | *V*  |      |      | *B   |      |      |
|  ply |      |      |      |      |      |      | o*   |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  use |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  sta |      |      |      |      |      |      |      |      |      |
| tist |      |      |      |      |      |      |      |      |      |
| ical |      |      |      |      |      |      |      |      |      |
|    c |      |      |      |      |      |      |      |      |      |
| orre |      |      |      |      |      |      |      |      |      |
| lati |      |      |      |      |      |      |      |      |      |
| ons, |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  the |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
| majo |      |      |      |      |      |      |      |      |      |
| rity |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|   of |      |      |      |      |      |      |      |      |      |
|    e |      |      |      |      |      |      |      |      |      |
| mpir |      |      |      |      |      |      |      |      |      |
| ical |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  ma‐ |      |      |      |      |      |      |      |      |      |
+======+======+======+======+======+======+======+======+======+======+
|      | *s*  | *d*  |      | *s*  | *    | *E*  | *    | ,    | (5)  |
| nure | ,    |      |      | ,    | tot* |      | CH4* | *    |      |
|      |      |      |      |      |      |      |      | pot* |      |
|  sto |      |      |      |      |      |      |      |      |      |
| rage |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|   mo |      |      |      |      |      |      |      |      |      |
| dels |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  are |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
| biol |      |      |      |      |      |      |      |      |      |
| ogic |      |      |      |      |      |      |      |      |      |
| ally |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|   ba |      |      |      |      |      |      |      |      |      |
| sed. |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  Two |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  mec |      |      |      |      |      |      |      |      |      |
| hani |      |      |      |      |      |      |      |      |      |
| stic |      |      |      |      |      |      |      |      |      |
+------+------+------+------+------+------+------+------+------+------+
|      |      |      |      |      |      |      |      |      |      |
|   mo |      |      |      |      |      |      |      |      |      |
| dels |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|   (H |      |      |      |      |      |      |      |      |      |
| ill, |      |      |      |      |      |      |      |      |      |
|    1 |      |      |      |      |      |      |      |      |      |
| 982; |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
| Garc |      |      |      |      |      |      |      |      |      |
| ía‐O |      |      |      |      |      |      |      |      |      |
| choa |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|   et |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
| al., |      |      |      |      |      |      |      |      |      |
|    1 |      |      |      |      |      |      |      |      |      |
| 999) |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  and |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
| four |      |      |      |      |      |      |      |      |      |
|      |      |      |      |      |      |      |      |      |      |
|  em‐ |      |      |      |      |      |      |      |      |      |
+------+------+------+------+------+------+------+------+------+------+

..

   pirical models (Chen and Hashimoto, 1980; Hill, 1991; Zee‐man, 1994;
   Sommer et al., 2004) were considered for our application. Of all
   models found, these six represented those most appropriate for
   simulating manure storage emissions.

   The more mechanistic models of Hill (1982) and García‐Ochoa et al.
   (1999) satisfied criteria 1, 2, and 3 of our model requirements, but
   were less satisfactory for criteria 4 and 5. These models simulated
   CH4 production based on the chemi‐cal and microbiological reactions
   in the storage. As a result, the model scale was not consistent with
   that of IFSM. Addi‐tionally, there were many model parameters that
   required it‐erative solutions or were difficult to obtain or set over
   the range of possible storage conditions.

   Of the four empirical models considered, three were found

   where *Vs,tot* is the total VS in the manure (g), *Bo* is the
   achiev‐able emission of CH4 during anaerobic digestion (g kg-1 VS),
   and *ECH4,pot* is the potential CH4 yield of the manure (g kg-1

   VS), which can be estimated using Bushwell's equation and

   the carbohydrate, fat, and protein content of the manure. For

   cattle slurry, Sommer et al. (2004) defined *Bo* as 0.2 g CH4 kg-1 VS
   and *ECH4,pot* as 0.48 g CH4 kg-1 VS.

   Total VS in the manure storage at any point in time is the

   difference between that entering the storage and that lost

   from the storage up to that point. The amount entering can be

   **Table 2. Parameters and values for the manure**

   **storage emissions model of Sommer et al. (2004).**

+-----------------+-----------------+-----------------+-----------------+
|    Parameter    | Variable        | Value           | Units           |
+=================+=================+=================+=================+
+-----------------+-----------------+-----------------+-----------------+

+-------------+-------------+-------------+-------------+-------------+
|    to       | Volatile    | *PVS*       | 0.87, 0.86, | g VS g‐1 TS |
|    satisfy  | solids      |             | 0.84        |             |
|    all five | content[a]  |             |             |             |
|    of our   |             |             |             |             |
|    model    |             |             |             |             |
|             |             |             |             |             |
|   criteria. |             |             |             |             |
|    The      |             |             |             |             |
|    model of |             |             |             |             |
|    Hill     |             |             |             |             |
+=============+=============+=============+=============+=============+
|    (1991)   |             | *Bo*        | 0.2         | g CH4 g‐1   |
|    was      |  Achievable |             |             | VS          |
|    dropped  |    CH4[b]   |             |             |             |
|    because  |             |             |             |             |
|    this     |             |             |             |             |
|    model    |             |             |             |             |
|    was      |             |             |             |             |
|             |             |             |             |             |
|   developed |             |             |             |             |
|    for      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

..

   anaerobic digesters, and the empirical parameters were not verified
   to be applicable for manure storages with no treat‐ment. From the
   remaining three models, the model of Som‐mer et al. (2004) was
   selected for our application. Their model employed commonly used
   empirical relationships (e.g., Arrhenius relationship) that were more
   general and thus more applicable to conditions outside of those for
   which they were developed. Additionally, this was a more recent
   model,

+-----------------+-----------------+-----------------+-----------------+
|    Potential    |    *ECH4,pot*   | 0.48            |    g CH4 g‐1 VS |
|    CH4[b]       |                 |                 |                 |
+=================+=================+=================+=================+
|    Correcting   | *b*\ 1, *b*\ 2  | 1.0, 0.01       |                 |
|    factors[b]   |                 |                 |   dimensionless |
+-----------------+-----------------+-----------------+-----------------+
| Arrhenius       | ln(*A*)         | 43.33           |    g CH4 kg‐1   |
| parameter[b]    |                 |                 |    VS h‐1       |
+-----------------+-----------------+-----------------+-----------------+
|    Activation   | *E*             | 112,700         | J mol‐1         |
|    energy[b]    |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    Gas          | *R*             | 8.314           | J K‐1 mol‐1     |
|    constant[b]  |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

..

   [a] Values for heifers, dry cows, and lactating cows from *ASABE
   Standards* (2008).

   [b] From Sommer et al. (2004).

   1316 TRANSACTIONSOFTHE ASABE

determined from the manure mass, the total solids content, and the VS
content:

+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
| *V | *  | =  | *  | *m | ⋅  | *P | ⋅  | *P | −  | *  | *  |    | (  |
| s* | to |    | M* | an |    | T  |    | V  |    | V* | s* |    | 6) |
| ,  | t* |    |    | ur |    | S* |    | S* |    |    | ,  | *l |    |
|    |    |    |    | e* |    |    |    |    |    |    |    | os |    |
|    |    |    |    |    |    |    |    |    |    |    |    | s* |    |
+====+====+====+====+====+====+====+====+====+====+====+====+====+====+
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+

where *Mmanure* is the accumulated mass of manure entering the storage
(kg), *PTS* is the total solids content in the manure (g�TS kg-1
manure), *PVS* is the fraction of VS in the total sol‐ids (g VS g-1 TS),
and *Vs,loss* is the accumulated VS loss. To obtain a similar rate of VS
loss as that reported by Sommer et al. (2004), daily VS loss is
predicted as three times the CH4 loss (*ECH4,man*) from the stored
manure. The mass of nonde‐gradable volatile solids, *Vs,nd*, is then
calculated using a mass balance:

   in the soil. Because the VFAs in the soil were due to the
   ap‐plication of the slurry (Sherlock et al., 2002), their model was
   used to relate CH4 emissions to the VFA concentration in the slurry.
   Therefore, emission of CH4 from field‐applied slurry is predicted as:

+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| * | * | = | ( | 1 | ⋅ | * | + | . | ) | ⋅ | * | ⋅ |   |   |
| E | a |   |   | 7 |   | F |   | 0 |   |   | A |   |   |   |
| C | p |   | . | 0 |   | V |   | 0 |   |   | c |   |   |   |
| H | p |   | 0 |   |   | F |   | 2 |   |   | r |   | . | ( |
| 4 | * |   |   |   |   | A |   | 6 |   |   | o |   | 0 | 1 |
| * |   |   |   |   |   | * |   |   |   |   | p |   |   | 0 |
| , |   |   |   |   |   |   |   |   |   |   | * |   |   | ) |
|   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   | 0 |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   | 3 |   |
|   |   |   |   |   |   |   |   |   |   |   |   |   | 2 |   |
+===+===+===+===+===+===+===+===+===+===+===+===+===+===+===+
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

..

   where *ECH4,app* is the emission of CH4 from field‐applied slurry (kg
   CH4 day-1), *FVFA* is the daily concentration of VFAs in the slurry
   (mmol kg-1 slurry), and *Acrop* is the land area (ha) where the
   manure is applied.

   Sherlock et al. (2002) found that the daily VFA concentra‐tion
   exponentially decreased in the days following the ap‐

+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
| *V  | *   | =   | *V* | *s* | *t  | −   | *V  |     | (7) |     |
| s*  | nd* |     |     | ,   | ot* |     | s*  | *d* |     | pli |
| ,   |     |     |     |     |     |     | ,   |     |     | cat |
|     |     |     |     |     |     |     |     |     |     | ion |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |  of |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     | man |
|     |     |     |     |     |     |     |     |     |     | ure |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     | slu |
|     |     |     |     |     |     |     |     |     |     | rry |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     | and |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |   a |
|     |     |     |     |     |     |     |     |     |     | ppr |
|     |     |     |     |     |     |     |     |     |     | oac |
|     |     |     |     |     |     |     |     |     |     | hed |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |   b |
|     |     |     |     |     |     |     |     |     |     | ack |
|     |     |     |     |     |     |     |     |     |     | gro |
|     |     |     |     |     |     |     |     |     |     | und |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     | lev |
|     |     |     |     |     |     |     |     |     |     | els |
+=====+=====+=====+=====+=====+=====+=====+=====+=====+=====+=====+
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     | wit |
|     |     |     |     |     |     |     |     |     |     | hin |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |   a |
|     |     |     |     |     |     |     |     |     |     | ppr |
|     |     |     |     |     |     |     |     |     |     | oxi |
|     |     |     |     |     |     |     |     |     |     | mat |
|     |     |     |     |     |     |     |     |     |     | ely |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |   f |
|     |     |     |     |     |     |     |     |     |     | our |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |  da |
|     |     |     |     |     |     |     |     |     |     | ys. |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |  Us |
|     |     |     |     |     |     |     |     |     |     | ing |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |   t |
|     |     |     |     |     |     |     |     |     |     | his |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     | inf |
|     |     |     |     |     |     |     |     |     |     | orm |
|     |     |     |     |     |     |     |     |     |     | ati |
|     |     |     |     |     |     |     |     |     |     | on, |
|     |     |     |     |     |     |     |     |     |     |     |
|     |     |     |     |     |     |     |     |     |     |  we |
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+

The inputs required for this model are the mass and tem‐perature of the
manure in storage. The amount of manure in

   derived a relationship predicting the daily concentration of VFA in
   the field‐applied slurry:

+------+------+------+------+------+------+------+------+------+------+
| sto  | *F   | =    | *F   | *i   | ⋅    | e    | −.0  | *t*  | (11) |
| rage | VFA* |      | VFA* | nit* |      |      | 6    |      |      |
| is   |      |      | ,    |      |      |      | 939⋅ |      |      |
| mod  |      |      |      |      |      |      |      |      |      |
| eled |      |      |      |      |      |      |      |      |      |
| as   |      |      |      |      |      |      |      |      |      |
| the  |      |      |      |      |      |      |      |      |      |
| accu |      |      |      |      |      |      |      |      |      |
| mula |      |      |      |      |      |      |      |      |      |
| tion |      |      |      |      |      |      |      |      |      |
| of   |      |      |      |      |      |      |      |      |      |
| that |      |      |      |      |      |      |      |      |      |
| prod |      |      |      |      |      |      |      |      |      |
| uced |      |      |      |      |      |      |      |      |      |
| by   |      |      |      |      |      |      |      |      |      |
+======+======+======+======+======+======+======+======+======+======+
| the  |      |      |      |      |      |      |      |      |      |
| h    |      |      |      |      |      |      |      |      |      |
| erd, |      |      |      |      |      |      |      |      |      |
| with |      |      |      |      |      |      |      |      |      |
| d    |      |      |      |      |      |      |      |      |      |
| aily |      |      |      |      |      |      |      |      |      |
| ma   |      |      |      |      |      |      |      |      |      |
| nure |      |      |      |      |      |      |      |      |      |
| e    |      |      |      |      |      |      |      |      |      |
| xcre |      |      |      |      |      |      |      |      |      |
| tion |      |      |      |      |      |      |      |      |      |
| de   |      |      |      |      |      |      |      |      |      |
| term |      |      |      |      |      |      |      |      |      |
| ined |      |      |      |      |      |      |      |      |      |
| in   |      |      |      |      |      |      |      |      |      |
| the  |      |      |      |      |      |      |      |      |      |
| ani‐ |      |      |      |      |      |      |      |      |      |
+------+------+------+------+------+------+------+------+------+------+

mal component of IFSM (Rotz et al., 1999). The temperature

of the manure in storage on a given simulated day is estimated

as the average ambient air temperature over the previous ten days, where
daily air temperature is also available in IFSM.

   The relationships described above are generally applica‐

ble to uncovered slurry storages. Some dairy farms use con‐trol
technology such as storage covers to reduce emissions.

One such technology includes the capture and combustion of

the CH4 gas. This method drastically decreases the emission of CH4,
although it also increases the emission of CO2 through the combustion of
CH4. To simulate this storage treatment, the emission of CH4 from an
enclosed manure storage is calculated as:

+----+----+----+----+----+----+----+----+----+----+----+----+----+
| *E | ,  | =  | *  | *  | ,  | *  | ⋅  | (  | η  | *  |    | (  |
| CH | c  |    | E* | CH |    | ma |    | 1− |    | ef |  ) | 8) |
| 4* | ov |    |    | 4* |    | n* |    |    |    | f* |    |    |
+====+====+====+====+====+====+====+====+====+====+====+====+====+
+----+----+----+----+----+----+----+----+----+----+----+----+----+

where *ECH4,cov* is the CH4 emitted from the enclosed manure storage (kg
CH4 day-1), *ECH4,man* is the calculated emission of CH4 from an open
manure storage using equation 4 (kg�CH4 day-1), and �\ *eff* is the
efficiency of the collector (fraction). The efficiency of the collector
and flare is assumed to be 0.99 (EPA, 1999). The subsequent flaring of
the cap‐

tured CH4 releases CO2, which adds to the overall farm emis‐sion of this
gas (Chianese et al., 2009a). The additional

emission of CO2 due to the combustion of CH4 is calculated as:

+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| *E    | ,     | =     | *E    | cov   | ⋅     | .2    |    75 | (9)   |
| CO2*  | *f    |       | CH4*  |       |       |       |       |       |
|       | lare* |       | ,     |       |       |       |       |       |
+=======+=======+=======+=======+=======+=======+=======+=======+=======+
+-------+-------+-------+-------+-------+-------+-------+-------+-------+

where *ECO2,flare* is the emission of CO2 due to combustion of the CH4
captured from the manure storage (kg CO2 day-1), and 2.75 is the ratio
of the molecular weights of CO2 and CH4.

**FIELD‐APPLIED MANURE**

Research has shown that field‐applied slurry is a source of CH4
emissions for several days after application, emitting between 40 to 90
g CH4 ha-1 day-1 (Sommer et al., 1996; Chadwick and Pain, 1997; Sherlock
et al., 2002). Emissions

drastically decrease within the first few days, and the soils re‐turn to
being a neutral source of CH4 by 11 days (Sherlock et al., 2002).

Sherlock et al. (2002) related CH4 emissions from field‐applied slurry
to the volatile fatty acids (VFAs) concentration

   where *FVFA* is the daily concentration of VFAs in the slurry (mmol
   kg-1 slurry), *FVFA,init* is the initial concentration of VFAs in the
   slurry at the time of application (mmol kg-1 slurry), and *t* is the
   time since application (days) with *t* = 0 representing the day of
   application.

   Paul and Beauchamp (1989) developed an empirical mod‐el relating the
   pH of manure slurry to VFA and total ammo‐niacal N (TAN)
   concentrations:

+------+------+------+------+------+------+------+------+------+------+
| *pH* | =    | 9    | 43   | −    | .2   | ⋅    | *F   | *i   | (12) |
|      |      |      |      |      | 02   |      | VFA* | nit* |      |
|      |      |      |      |      |      |      | ,    |      |      |
+======+======+======+======+======+======+======+======+======+======+
|      |      | 9    | 43   |      | .2   |      | *F   |      |      |
|      |      |      |      |      | 02   |      | TAN* |      |      |
+------+------+------+------+------+------+------+------+------+------+

..

   where *pH* is the pH of the manure slurry (dimensionless), and *FTAN*
   is the concentration of TAN (NH4+ + NH3) in the slurry (mmol kg-1
   slurry). By rearranging equation 12, an equation was obtained for
   predicting the initial concentration of VFAs based on the pH and TAN
   content of the manure slurry:

+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| *F*   |       | =     | *F    | ( .9  | −     | *pH*  |    )  |       |
|       |       |       | TAN*  | 43    |       |       |       |       |
+=======+=======+=======+=======+=======+=======+=======+=======+=======+
| *VFA* | *     |       | .2 02 |       |       |       |       | (13)  |
|       | init* |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+

..

   To predict emissions from field‐applied manure, equa‐tion�13 was used
   to determine an initial VFA concentration, and equation 11 was used
   to track the VFA concentration through time following application.
   Using this concentra‐tion, an emission rate was determined (eq. 10)
   until the re‐maining VFA concentration approached zero.

   | **GRAZING ANIMALS**
   | On farms that incorporate grazing for at least a portion of the
     year, freshly excreted feces and urine are directly depos‐ited by
     animals on pastures. Studies have shown that feces are a small
     source of CH4 and that emissions from urine are not significantly
     different from background soil emissions (e.g.,�Jarvis et al.,
     1995; Yamulki et al., 1999). Although there is evidence that CH4
     emission rates from freshly depos‐ited feces are influenced by
     environmental conditions and animal rations (Saggar et al., 2004),
     quantitative relation‐ships describing these influences have not
     been developed. Therefore, use of a constant emission factor
     provided the best available approach of representing this emission
     source. This approach was further justified in that this emission
     source was relatively small compared to enteric fermentation and
     manure storage sources (Holter, 1997). To determine an

   Vol. 52(4): 1313-1323 1317

**Table 3. Published emissions of CH4 from feces directly deposited by
dairy animals on pasture lands (all values in g CH4 kg-1 feces DM).**

+-----------------------+-----------------------+-----------------------+
|    Reference          | Reported Range        | Average               |
+=======================+=======================+=======================+
+-----------------------+-----------------------+-----------------------+

..

   model components. Finally, IFSM was used to simulate a
   rep‐resentative farm in Pennsylvania, and the predicted emis‐sions
   were compared to those previously identified as typical

+-----------------+-----------------+-----------------+-----------------+
|    Jarvis et    | 0.31 ‐ 0.95     | 0.65            |    (Chianese et |
|    al. (1995)   |                 |                 |    al., 2009c). |
|                 |                 |                 |    Based on     |
|                 |                 |                 |    this         |
|                 |                 |                 |    evaluation,  |
|                 |                 |                 |    the uncer‐   |
+=================+=================+=================+=================+
|    Flessa et    | ‐‐              | 1.25            |    tainty in    |
|    al.          |                 |                 |    model        |
|    (1996)[a]    |                 |                 |    predictions  |
|                 |                 |                 |    is           |
|                 |                 |                 |    discussed.   |
+-----------------+-----------------+-----------------+-----------------+
|    Holter       | 0.21 ‐ 0.90     | 0.60            |                 |
|    (1997)       |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

+-----------------------+-----------------------+-----------------------+
|    Yamulki et al.     | 0.09 ‐ 0.65           | 0.32                  |
|    (1999)             |                       |                       |
+=======================+=======================+=======================+
|    Saggar et al.      | 0.91 ‐ 1.03           | 0.97                  |
|    (2004)             |                       |                       |
+-----------------------+-----------------------+-----------------------+
|    Average emission   |                       | 0.76                  |
|    factor             |                       |                       |
+-----------------------+-----------------------+-----------------------+

..

   [a] Measured over a whole pasture, whereas other publications report
   emissions from individual fecal deposits.

   emission factor, emission rates from five published studies were
   averaged to obtain a factor of 0.76 g CH4 kg-1 DM of feces deposited
   in the pasture (table 3). For grazing systems, the daily emission of
   CH4 is predicted as the product of this emission rate and the daily
   amount of feces DM deposited by grazing animals.

   | **BARN EMISSIONS**
   | Manure on housing facility floors is also a small source of CH4. No
     published model or data were found for this emis‐sion source.
     Therefore, unpublished CH4 emission data mea‐sured from free‐stall
     barn floors (E. Wheeler, unpublished data, 2008, The Pennsylvania
     State University, University Park, Pa.) were used to develop an
     empirical equation relat‐ing CH4 emission to the air temperature in
     the barn. The re‐sulting model (R2 = 0.49) is:

+----+----+----+----+----+----+----+----+----+----+----+----+----+
| *E | ,  | *  | =  | m  | (  | .0 | *  | (  | /  | 10 |    | (1 |
| CH |    | fl |    | ax | ,0 | 13 | T* | *A |    | 00 |  ) | 4) |
| 4* |    | oo |    |    | .0 |    |    | b  |    |    |    |    |
|    |    | r* |    |    |    |    |    | ar |    |    |    |    |
|    |    |    |    |    |    |    |    | n* |    |    |    |    |
|    |    |    |    |    |    |    |    | )  |    |    |    |    |
+====+====+====+====+====+====+====+====+====+====+====+====+====+
+----+----+----+----+----+----+----+----+----+----+----+----+----+

..

   where *ECH4,floor* is the daily rate of CH4 emission from the barn
   floor (kg CH4 day-1), *T* is the air temperature (°C), and *Abarn* is
   the area of the barn floor covered with manure (m2). At temperatures
   below 0°C, the emission is zero.

   As an empirical equation that correlates CH4 emission with
   temperature, equation 14 satisfies criteria 3, 4, and 5 of our model
   requirements. The temperature dependence of CH4 production is well
   documented (Zeikus and Winfrey, 1976; van Hulzen et al., 1999). This
   simple relationship pre‐dicts reasonable emission rates for
   temperatures of 0°C and greater. Because this emission source is a
   relatively minor contributor to overall farm‐level CH4 emissions,
   develop‐ment of a more detailed process model was not justified.

   | **MODEL EVALUATION**
   | Few data exist on overall emissions of CH4 from dairy farms in the
     U.S. (Chianese et al., 2009c). Studies that have quantified CH4
     emissions from specific farm sources often have not provided the
     specific input data required to simulate scenarios in IFSM. In
     addition, these studies were often small‐scale or laboratory
     studies that could not be adequately simulated in IFSM. Therefore,
     we evaluated IFSM predic‐tions of CH4 emissions in three ways.
     First, for the major emission sources of enteric fermentation and
     manure storage, observed data from previous studies were compared
     to simu‐lated emissions. Studies were selected that represented
     long‐term emissions (Chianese et al, 2009c) and that included the
     major input information required to simulate the observed
     conditions with IFSM but were not a source of data in the
     de‐velopment of the original model. Second, a sensitivity analy‐sis
     was performed on the important parameters of the major

   | **ENTERIC FERMENTATION EMISSIONS**
   | Studies by Kirchgessner et al. (1991) and Kinsman et al. (1995)
     were used to evaluate our model's ability to simulate CH4 emissions
     from dairy animals. Kirchgessner et al. (1991) summarized CH4
     emissions from seven metabolism trials employing 67 lactating cows
     with an average weight of 583�kg and an average daily milk
     production of 17.0 kg cow-1. The animals were fed diets consisting,
     on average, of 57% roughage composed of grass hay and corn silage
     with the remainder from various concentrates. They reported an
     average daily CH4 emission of 300 g CH4 cow-1 (±39 g CH4 cow-1).
     For trials with relatively low feed intake (about 12 kg DM cow-1
     day-1), the reported average emission was 270 g CH4 cow-1 day-1,
     and with a DM intake of 16 kg cow-1 day-1, the average emission was
     334 g CH4 cow-1 day-1 .

   Although specific experiments could not be simulated, IFSM was used
   to represent the average diet characteristics, cow weight, and milk
   production from the reported studies. For the overall average
   conditions, the predicted emission was 299 g CH4 cow-1 day-1, very
   similar to the average of all trials and well within one standard
   deviation of the mean reported by Kirchgessner et al. (1991). When
   animal weights and milk production were adjusted to obtain feed
   intakes of 12 and 16 kg DM cow-1 day-1, predicted daily emissions
   were 263 and 339 g CH4 cow-1, respectively. The close simi‐larity
   between measured and predicted emissions demon‐strates that IFSM is
   capable of predicting CH4 emissions from enteric fermentation in
   dairy cattle.

   In a longer‐term study, Kinsman et al. (1995) measured CH4 emissions
   from 118 lactating cows over a 6‐month peri‐od. Cows weighed an
   average of 602 kg with an average daily milk production of 28.5 kg
   cow-1 (±2.3 kg cow-1). On aver‐age, animals were fed 17.5 kg DM cow-1
   day-1 (±1.4 kg DM cow-1 day-1) of mixed forage and concentrate. The
   diet con‐sisted of corn silage, alfalfa silage, hay, grain, roasted
   soy‐bean, soybean meal, and other supplements (Kinsman et al., 1995).
   They reported daily CH4 emissions from enteric fer‐mentation ranging
   from 431 to 686 L CH4 cow-1 with an av‐erage rate over the 6‐month
   period of 552 L CH4 cow-1. Considering a CH4 density of 0.68 kg m-3
   at atmospheric pressure and temperatures around 15°C, this range in
   daily emissions is 293 to 466 g CH4 cow-1 with an average of 375�g
   CH4 cow-1. Using similar diet characteristics and milk pro‐duction,
   IFSM predicted an average daily emission of 375 g CH4 cow-1. This
   simulated emission was within the range, and equal to the average, of
   CH4 emission rates reported by Kinsman et al. (1995), further
   supporting that IFSM predicts very reasonable CH4 emissions from
   enteric fermentation. IFSM was also able to accurately predict CO2
   emissions for this same study (Chianese et al., 2009a).

   | **MANURE STORAGE EMISSIONS**
   | A study by Husted (1994) was used to test the ability of IFSM in
     predicting CH4 emissions from slurry manure stor‐ages. Husted
     measured CH4 emissions from slurry manure obtained from 160 Jersey
     cows and their calves, which was

   1318 TRANSACTIONSOFTHE ASABE

stored in a 1,200 m3 outdoor tank in Denmark. Over an annual period,
daily CH4 emissions from the uncovered storage ranged from 5 to 35 g m-3
d-1 as slurry temperature varied from 6°C to 18°C. From these emission
measurements, an annual emission of 15.5 kg animal-1 was estimated,
which gave an annual emission from the storage of 2,480 kg CH4. The
confidence limits of the data reflected an uncertainty of

   **Table 4. Sensitivity analysis for the CH4 module.**

+-----------------+-----------------+-----------------+-----------------+
|                 | Variable[a]     |    Change in    | Sensitivity     |
+=================+=================+=================+=================+
|                 |                 | input (%)       | index[b]        |
+-----------------+-----------------+-----------------+-----------------+
|    Enteric      | *MEI*           | 25              | 0.7             |
|    fermentation |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|                 | *Emax*          | 25              | 1.0             |
+-----------------+-----------------+-----------------+-----------------+
|                 |                 | 25              | 0.2             |
+-----------------+-----------------+-----------------+-----------------+
|                 | *Rdiet*         |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|                 | *c*             | 25              | 0.7             |
+-----------------+-----------------+-----------------+-----------------+

+-------------+-------------+-------------+-------------+-------------+
| 30% in this |    Manure   | *Pts*,      | 25          | 1.0         |
| estimate.   |    storage  | *Pvs*       |             |             |
+=============+=============+=============+=============+=============+
|    A        |             | *Bo*        | 25          | 0.98        |
|    rep      |             |             |             |             |
| resentative |             |             |             |             |
|    farm was |             |             |             |             |
|             |             |             |             |             |
|   simulated |             |             |             |             |
|    with     |             |             |             |             |
|    IFSM     |             |             |             |             |
|    using    |             |             |             |             |
|    the      |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
| reported    |             | *ECH4,pot*  | 25          | 1.04[c]     |
| animal,     |             |             |             |             |
| manure, and |             |             |             |             |
| storage     |             |             |             |             |
| chara       |             |             |             |             |
| cteristics. |             |             |             |             |
| The         |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

farm was simulated over 25 years of historical weather data from
Thisted, Denmark (1974 to 1998). Over manure slurry temperatures of 6°C
to 18°C, simulated CH4 emissions were 3.8 to 27 g CH4 m-3 d-1, which was
similar to the range in measured values. Simulated average annual
emissions ranged from 2,150 to 3,500 kg CH4 with a 25‐year average of
2,765 kg CH4. These annual values were within the uncer‐tainty of
Husted's estimated value, and the 25‐year average emission was within
12% of his estimated annual emission. This comparison of simulated and
measured emissions sup‐ports that the model predicts very reasonable
emissions from stored cattle slurry manure.

| **SENSITIVITY ANALYSIS**
| Models are more sensitive to some parameters and inputs than others;
  it is therefore important to quantify this sensitiv‐ity to ensure that
  values of variables with the most impact are accurate. A sensitivity
  analysis was performed on the mod‐ules developed for enteric
  fermentation, manure storage, and field‐applied manure. For this
  analysis, each selected param‐eter was varied by a set percentage, and
  the percent change in the output was determined. To perform this
  analysis, the CH4 relationships were developed into an ad‐hoc program
  using Matlab. Modifications to the CH4 relationships were made as
  necessary to achieve mathematically correct and physically realistic
  output while maintaining the scientific validity of the equations.
  Because a function was created for each emission source, the inputs
  and parameters were easily changed and the relevant outputs obtained.
  This method al‐lowed the sensitivity of important parameters (table 4)
  to be quantified while maintaining the interaction among vari‐ables.
  Data generated by changing the value of each parame‐ter by ±25% were
  used to calculate a sensitivity index:

+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
| *  | =  | ⎛⎢ | *  | +  | %  | −  | *  | −  | %  | ⎛  | *x |    | (1 |
| S* |    |    | y* |    |    |    | y* |    |    | ⋅⎟ | b  |    | 5) |
|    |    |    |    |    |    |    |    |    |    |    | as | ⎞⎟ |    |
|    |    |    |    |    |    |    |    |    |    |    | e* |    |    |
+====+====+====+====+====+====+====+====+====+====+====+====+====+====+
| *  |    | ⎢⎝ | *  | +  | %  | −  | *  | −  | %  | ⎟  | *y |    |    |
| S* |    |    | x* |    |    |    | x* |    |    | ⎠⎝ | b  |    |    |
|    |    |    |    |    |    |    |    |    |    |    | as | ⎟⎠ |    |
|    |    |    |    |    |    |    |    |    |    |    | e* |    |    |
+----+----+----+----+----+----+----+----+----+----+----+----+----+----+

where *SI* is the sensitivity index (dimensionless), and *xbase* is the
model parameter used to obtain the output *ybase*. A value of one
indicates that a 25% change in *y* occurs with a 25% change in *x*; a
lesser ratio indicates lesser sensitivity, whereas a greater ratio
indicates greater sensitivity.

The enteric fermentation output was not highly sensitive to any of the
model parameters. For a given percent change in the input, all of the
parameters caused the same, or less, change in CH4 emissions. The most
important parameter was the maximum possible CH4 emission; the predicted
emission rate was proportional to this assigned value (table 4).

For the manure storage module, the majority of parame‐ters had
sensitivity values of 1.0. In other words, a given change in the input
parameter caused the same change in the output (table 4). However, the
model was very sensitive to the Arrhenius parameter, which had a
sensitivity greater than

+-----------+-----------+-----------+-----------+-----------+-----------+
| *b*\ 1,   |           |           |           | 25        | 0.99      |
| *b*\ 2    |           |           |           |           |           |
+===========+===========+===========+===========+===========+===========+
| ln(*A*)   |           |           | 25        |           | >>100[d]  |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *Mman*    |           |           | 25        |           | 1.0       |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *T*\ 10C  |           |           | 25        |           | 1.7       |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *T*\ 25C  |           |           | 25        |           | 4.3       |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    Field  |           | *FTAN*    | 25        |           | 0.99      |
|    ap     |           |           |           |           |           |
| plication |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *Mman*    |           |           | 25        |           | 0.01      |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *pH*      |           |           | 25        |           | 5.6       |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *t*       |           |           | 25        |           | 0.7[e]    |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *Rapp*    |           |           | 25        |           | 1.1[f]    |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    | [a]  |    | =    |           |           |           |           |
|           |           |           |           |           |           |
|    *Pts*, |     total |           |           |           |           |
|      *Pvs |           |           |           |           |           |
|      Bo*  |    solids |           |           |           |           |
|    | *    |      and  |           |           |           |           |
| ECH4,pot* |           |           |           |           |           |
|           |  volatile |           |           |           |           |
|           |           |           |           |           |           |
|           |    solids |           |           |           |           |
|           |      (VS) |           |           |           |           |
|           |           |           |           |           |           |
|           |     conce |           |           |           |           |
|           | ntrations |           |           |           |           |
|           |      (%)  |           |           |           |           |
|           |      =    |           |           |           |           |
|           |      a    |           |           |           |           |
|           | chievable |           |           |           |           |
|           |      CH4  |           |           |           |           |
|           |           |           |           |           |           |
|           |     yield |           |           |           |           |
|           |      (g   |           |           |           |           |
|           |      CH4  |           |           |           |           |
|           |      kg‐1 |           |           |           |           |
|           |      VS)  |           |           |           |           |
|           |    | =    |           |           |           |           |
|           |           |           |           |           |           |
|           |   maximum |           |           |           |           |
|           |           |           |           |           |           |
|           | potential |           |           |           |           |
|           |      CH4  |           |           |           |           |
|           |           |           |           |           |           |
|           |     yield |           |           |           |           |
|           |      (g   |           |           |           |           |
|           |      CH4  |           |           |           |           |
|           |      kg‐1 |           |           |           |           |
|           |      VS)  |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *b*\ 1,   |    = rate |           |           |           |           |
| *b*\ 2    |    c      |           |           |           |           |
|           | orrection |           |           |           |           |
|           |           |           |           |           |           |
|           |   factors |           |           |           |           |
|           |    for    |           |           |           |           |
|           |    d      |           |           |           |           |
|           | egradable |           |           |           |           |
|           |    and    |           |           |           |           |
|           |    nond   |           |           |           |           |
|           | egradable |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
| VS        |           |           |           |           |           |
| (dimen    |           |           |           |           |           |
| sionless) |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
| ln(*A*)   |    =      |           |           |           |           |
|           |           |           |           |           |           |
|           | Arrhenius |           |           |           |           |
|           |           |           |           |           |           |
|           | parameter |           |           |           |           |
|           |    (g CH4 |           |           |           |           |
|           |    kg‐1   |           |           |           |           |
|           |    VS     |           |           |           |           |
|           |    h‐1)   |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    *Mman* |           |           |           |           |           |
|    = mass |           |           |           |           |           |
|    of     |           |           |           |           |           |
|    manure |           |           |           |           |           |
|    (kg)   |           |           |           |           |           |
|           |           |           |           |           |           |
|           |           |           |           |           |           |
| *T*\ 1OC, |           |           |           |           |           |
|           |           |           |           |           |           |
|  *T*\ 25C |           |           |           |           |           |
|    =      |           |           |           |           |           |
|    te     |           |           |           |           |           |
| mperature |           |           |           |           |           |
|    (°C)   |           |           |           |           |           |
|           |           |           |           |           |           |
|    *FTAN* |           |           |           |           |           |
|    =      |           |           |           |           |           |
|    total  |           |           |           |           |           |
|    a      |           |           |           |           |           |
| mmoniacal |           |           |           |           |           |
|           |           |           |           |           |           |
|  nitrogen |           |           |           |           |           |
|    in     |           |           |           |           |           |
|    manure |           |           |           |           |           |
|    (mmol  |           |           |           |           |           |
|    kg‐1   |           |           |           |           |           |
|           |           |           |           |           |           |
|   slurry) |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *pH*      |    = pH   |           |           |           |           |
|           |    of the |           |           |           |           |
|           |    slurry |           |           |           |           |
|           |    (dimen |           |           |           |           |
|           | sionless) |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
| *t*       |    = time |           |           |           |           |
|           |    until  |           |           |           |           |
|           |    inco   |           |           |           |           |
|           | rporation |           |           |           |           |
|           |    (days) |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |    | =    |           |           |           |           |
|  | *Rapp* |           |           |           |           |           |
|           |    manure |           |           |           |           |
|   | *MEI* |      ap   |           |           |           |           |
|           | plication |           |           |           |           |
|           |      rate |           |           |           |           |
|           |      (kg  |           |           |           |           |
|           |      m‐2) |           |           |           |           |
|           |    | =    |           |           |           |           |
|           |      meta |           |           |           |           |
|           | bolizable |           |           |           |           |
|           |           |           |           |           |           |
|           |    energy |           |           |           |           |
|           |           |           |           |           |           |
|           |    intake |           |           |           |           |
|           |      (MJ  |           |           |           |           |
|           |           |           |           |           |           |
|           | animal‐1) |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |    =      |           |           |           |           |
|  | *Emax* |           |           |           |           |           |
|           |   maximum |           |           |           |           |
| | *Rdiet* |           |           |           |           |           |
|           |  possible |           |           |           |           |
|           |           |           |           |           |           |
|           |  emission |           |           |           |           |
|           |    of CH4 |           |           |           |           |
|           |    (MJ    |           |           |           |           |
|           |           |           |           |           |           |
|           |  animal‐1 |           |           |           |           |
|           |    d‐1) = |           |           |           |           |
|           |    ratio  |           |           |           |           |
|           |    of     |           |           |           |           |
|           |    starch |           |           |           |           |
|           |    to ADF |           |           |           |           |
|           |    in     |           |           |           |           |
|           |    diet   |           |           |           |           |
|           |    (g     |           |           |           |           |
|           |    g‐1)   |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    *c* =  |           |           |           |           |           |
|    shape  |           |           |           |           |           |
|           |           |           |           |           |           |
| parameter |           |           |           |           |           |
|    to     |           |           |           |           |           |
|           |           |           |           |           |           |
| calculate |           |           |           |           |           |
|           |           |           |           |           |           |
|   enteric |           |           |           |           |           |
|    ferm   |           |           |           |           |           |
| entation. |           |           |           |           |           |
|           |           |           |           |           |           |
| [b] The   |           |           |           |           |           |
| se        |           |           |           |           |           |
| nsitivity |           |           |           |           |           |
| index is  |           |           |           |           |           |
| the ratio |           |           |           |           |           |
| of the    |           |           |           |           |           |
| change in |           |           |           |           |           |
| output    |           |           |           |           |           |
| over the  |           |           |           |           |           |
| change    |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+

..

   in input. For example, if change = 1.0, then a 25% change in input
   yielded a 25% change in output.

   [c] Varying *ECH4,pot* by 10% and 50% yielded 1.0 and 1.3,
   respectively. [d] The model was very sensitive to changes in the
   Arrhenius parameter with a change much greater than 100.

   [e] Varying *t* by 10% and 50% yielded 1.7 and 0.5, respectively.

   [f] Varying *Rapp* by 10% and 50% yielded 1.0 and 1.3, respectively.

   100. The Arrhenius parameter accounts for the temperature dependency
   of CH4 emissions from manure storage. This pa‐rameter is an
   established constant within the model that should not be changed. An
   appropriate value for the Arrhe‐nius parameter was determined by the
   original developers of the manure storage model by fitting the
   parameter to ob‐served data. The value selected ensured that annual
   CH4 emissions from slurry storage corresponded to emissions
   cal‐culated using IPCC emission factors (Sommer et al., 2004). As a
   result, the present Arrhenius parameter provides the best available
   model. Additional studies quantifying CH4 emis‐sions from slurry
   storage are required to further evaluate and perhaps improve the
   determination of this parameter (Som‐mer et al., 2004).

   As with the manure storage model, most parameters in the
   field‐applied manure module caused approximately the same percent
   change in output as the change in input. The pH of the manure slurry
   was the only variable that caused a major dif‐ference in the output,
   as evidenced by a five‐fold change in output for a given change in
   input. Currently, the pH of slurry at the time of field application
   is held constant in IFSM at a value of 8.0; future work may improve
   the prediction of CH4

   Vol. 52(4): 1313-1323 1319

   emissions by developing a model to predict changes in slurry pH.
   However, as illustrated in the following section, this emission
   source is very small compared to other farm sources, so a more
   detailed model was not warranted at this time.

   The majority of CH4 emissions from the farm were due to enteric
   fermentation. Even though the manure storage and field application
   modules were very sensitive to certain pa‐rameters, the impact of
   this sensitivity on farm emissions was small relative to that of
   enteric fermentation. A 25% change in the enteric fermentation,
   manure storage, and field ap‐plication emissions of CH4 caused about
   a 15%, 2% and neg‐ligible change in the net GHG emission of the farm,
   respectively. Thus, changes to parameters in the manure stor‐age and
   field application modules had a relatively small im‐pact on net farm
   GHG emissions, even though some parameters were highly sensitive.

   | **REPRESENTATIVE FARM EMISSIONS**
   | As a final evaluation, simulated annual whole‐farm emis‐sions were
     compared to those previously summarized from prior literature for a
     hypothetical dairy farm in central Penn‐sylvania (Chianese et al.,
     2009c). Only a brief description of the farm is provided to
     document those assumptions most relevant to CH4 production and
     emission. This representative farm included 85 lactating Holstein
     cows (average mass of 650 kg), 15 non‐lactating cows (average mass
     of 700 kg), 38�heifers over one year in age (average mass of 470
     kg), and 42 heifers under one year in age (average mass of 200 kg).
     Animals were housed in free‐stall barns where they were fed total
     mixed rations consisting of corn, alfalfa and grass si‐lages,
     high‐moisture corn, and purchased supplemental feeds as required to
     meet animal nutrient needs. Manure was scraped daily, stored in a
     3,000 m3 storage tank for up to six months, and applied to cropland
     in the spring and fall. On av‐erage over the full year, the storage
     contained about 1,100 m3 of manure. The 90 ha farm area consisted
     of 20 ha of grass, 20 ha of alfalfa, and 50 ha of corn. Most of the
     crop nutrient requirements were met through manure nutrients
     generated on the farm, but N fertilizer was applied at rates of 50
     and 70�kg ha-1 on corn and grassland, respectively.

   Based on the above farm characteristics, IFSM was used to simulate
   this representative farm in central Pennsylvania

   using historical State College weather (1982 to 2006). The simulated
   annual emission from animals and housing facili‐ties was 14,202 kg
   CH4, primarily from enteric fermentation with a small emission from
   barn floors (table 5). Other emis‐sions included 6,971 kg CH4 from
   the manure storage and 20�kg CH4 following field application of
   manure (table 5). This gave a total annual emission of 21,193 kg CH4
   from this representative dairy farm. For the overall farm, this
   predicted emission was very similar to the rate of 22,931 kg CH4
   year-1 that was previously estimated as a typical emission for a
   dairy farm of this size, based on a review of published emission data
   (table 5). The major difference between the simulated and previously
   estimated data was the emission of lactating cows. As illustrated in
   the next section, this emission is sensi‐tive to the amount of forage
   in their diet. This simulation used a minimum amount of forage in
   lactating cow diets, and a rel‐atively small increase in the amount
   of forage fed can easily explain this difference in CH4 emission.
   Overall, this com‐parison verifies that IFSM can simulate farm‐level
   CH4 emissions very similar to those summarized from previous studies.

   | **MODEL UNCERTAINTY**
   | Any farm‐level estimation of GHG emissions will have uncertainty
     associated with the prediction. It is not possible to make a
     long‐term measurement of net farm GHG emis‐sion, and even if it
     were done, that too would have uncertain‐ty. To determine the
     uncertainty in a net farm emission, uncertainties of each of the
     components must be defined. Sta‐tistical quantification of the
     uncertainty of components of a biological system requires large
     data sets. Since adequate data are not available, the IPCC (2006a)
     has chosen to use ex‐pert opinion to estimate the uncertainty of
     their emission fac‐tors in predicting GHG emissions. They estimate
     that their Tier 2 methodologies provide emission factors for CH4
     from enteric fermentation and manure handling with uncertainties of
     ±20% (IPCC, 2006b). This is the uncertainty associated with general
     application of their emission factors. Creating and applying their
     Tier 2 emission factors to well defined conditions can reduce this
     uncertainty (IPCC, 2006a).

   The uncertainty estimations of the IPCC provide the best information
   available for quantifying the uncertainty of pre-dicting farm GHG
   emissions. Based on our experience in

   **Table 5. Comparison of previously estimated (Chianese et al, 2009c)
   and model‐predicted annual CH4 emissions from a representative dairy
   farm in Pennsylvania.**

+-----------+-----------+-----------+-----------+-----------+-----------+
|           |           | Repre     |           |           | IFSM      |
|           |           | sentative |           |           | Simulated |
|           |           | Farm      |           |           |           |
|           |           | Analysis  |           |           |           |
+===========+===========+===========+===========+===========+===========+
|           |           | Emission  | Farm      | Emission  | Emission  |
|           |           | Factor[a] | Parameter | (kg CH4)  | (kg CH4)  |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |           | 106 kg    | 111 LU[b] | 11,766    | 7,312[c]  |
|   Animals | Lactating | CH4 LU‐1  |           |           |           |
|    and    |    cows   |           |           |           |           |
|           |           |           |           |           |           |
|   housing |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |    Dry    | 58 kg CH4 | 20 LU     | 1,160     | 1,556     |
|           |    cows   | LU‐1      |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           | Re        | 77 kg CH4 | 52 LU     | 4,000     | 4,950     |
|           | placement | LU‐1      |           |           |           |
|           | heifers   |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |    Barn   | ‐‐        | ‐‐        | ‐‐        | 384       |
|           |    floors |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    Manure |           | 5.6 kg    | 1100 m3   | 6,160     | 6,971     |
|           |           | CH4 m‐3   |           |           |           |
|   storage |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |    Grass  | ‐1.4 kg   | 20 ha     | ‐28       | ‐‐        |
| Croplands |           | CH4 ha‐1  |           |           |           |
|           |           | year‐1    |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |           | ‐2.6 kg   | 20 ha     | ‐52       | ‐‐        |
|           |   Alfalfa | CH4 ha‐1  |           |           |           |
|           |           | year‐1    |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           |    Corn   | ‐1.5 kg   | 50 ha     | ‐75       | ‐‐        |
|           |           | CH4 ha‐1  |           |           |           |
|           |           | year‐1    |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    Field  |           | ‐‐        | ‐‐        | ‐‐        | 20        |
|    ap     |           |           |           |           |           |
| plication |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    Total  |           | 22,931    |           |           | 21,193    |
+-----------+-----------+-----------+-----------+-----------+-----------+

..

   [a] Emission factors were obtained from Chianese et al., 2009c.

   [b] LU = livestock unit of 500 kg body mass.

   [c] This emission was relatively low compared to the representative
   farm because the simulated farm used a minimum forage diet for
   lactating animals, whereas the experimental data supporting the
   representative farm analysis typically reflects greater use of forage
   in these diets.

   1320 TRANSACTIONSOFTHE ASABE

evaluating our model, we believe that the uncertainty in pre‐dicting CH4
emissions during manure storage and handling is well represented by the
±20% suggested by the IPCC (2006b). For predicting emissions from
enteric fermentation for specific animals on well defined diets, the
model is more accurate. For this component, we suggest an uncertainty
of±10%. The uncertainties of all farm components can be com‐bined, in
which the overall uncertainty is the square root of the sum of the
squares of the emission of each component times its uncertainty (IPCC,
2006a). Using this procedure, the uncertainty in estimating the total
CH4 emission from en‐teric fermentation, manure storage, and manure
application in the field is ±9%. Including the uncertainties in
predicting CO2 (Chianese et al., 2009a) and N2O (Chianese et al., 2009b)
emissions, the uncertainty in the estimated net farm GHG emission is
±13%, with about half of this uncertainty due to that in predicting CH4
emissions.

| **MODEL APPLICATION**
| Four whole‐farm simulations were done to illustrate the use of the
  model in evaluating management impacts on CH4 emissions from dairy
  farms. Important factors that effect CH4 production include animal
  diets and management of stored manure. The model was used to simulate
  the 100‐cow repre‐sentative dairy farm described above, and then
  management changes were made to simulate the use of higher‐forage
  diets, the use of grazing along with higher‐forage diets, and the use
  of a covered manure storage with a flare to burn the biogas produced.

For the base farm, lactating cows were fed a relatively high‐grain diet
(table 6, column 1). This has been a common practice in the past, with
relatively inexpensive grain for feed supplementation. With a recent
increase in grain prices, there is incentive to feed more forage
produced on the farm with less grain supplementation. This management
change was simulated by switching the diet formulation for the lactating

   herd from minimum forage to a maximum forage ration (Rotz et al.,
   1999). To obtain the additional forage needed, more of the corn
   produced on the farm was harvested as corn silage with less harvested
   as high‐moisture grain. This pro‐duced 115 Mg DM more forage and 49
   Mg DM less grain for feeding the herd (table 6, column 2 vs. 1).
   Total feed intake was increased about 2%, with an annual average of
   44 Mg DM less supplemental feed purchased and brought onto the farm.
   With the higher‐forage diets, animals produced about 21% more CH4
   through enteric fermentation. This also in‐creased the VS content in
   the stored manure, which increased the emission from the storage by
   6%.

   This change also impacts the other GHG emissions of N2O (Chianese et
   al., 2009b) and CO2 (Chianese et al., 2009a). Al‐though the details
   of these processes are not presented here, the simulation indicates a
   small decrease in N2O emission with greater use of corn silage. This
   occurs because more N is being removed in the corn silage and
   recycled through the animals as compared to grain harvest and
   feeding. Carbon dioxide emission is also reduced with greater use of
   corn si‐lage. With grain harvest, greater amounts of stover are left
   in the field, which creates greater microbial decomposition and
   ultimately more CO2 emission through microbial respiration. By
   removing the whole plant in corn silage harvest, less crop residue is
   left in the soil to enhance microbial respiration. Overall, this
   management change had little effect on the total global warming
   potential of the GHGs emitted from the farm (table 6, column 2 vs.
   1).

   When the use of higher‐forage diets was combined with grazing, some
   net reduction in GHG emission was obtained (table 6, column 3 vs. 2).
   For this strategy, all of the 20 ha of grass was rotationally grazed
   from late April through October by the older heifers and all cows.
   All other farm parameters, including milk production, were set the
   same as the previous scenario. With the use of grazing, harvested
   forage produc‐tion was reduced 22%. A little more grain was produced,
   and purchased feed was reduced 19%. Enteric methane produc‐tion
   increased 2% with the use of pasture forage, but with

   **Table 6. Annual production and greenhouse gas emissions of three
   production strategies on a simulated representative dairy farm in
   central Pennsylvania.[a]**

+-----------------+-----------------+-----------------+-----------------+
| Base Farm,      | High‐Forage     | High‐Forage     | Low‐Forage Diet |
|                 | Diet[c]         | Diet            | with            |
+=================+=================+=================+=================+
| Low‐Forage      |                 | with Grazing    | Enclosed Manure |
| Diet[b]         |                 |                 | Storage[d]      |
+-----------------+-----------------+-----------------+-----------------+

..

   Feed production and use (Mg DM)

+-------------+-------------+-------------+-------------+-------------+
|             | 522         | 637         | 494         | 518         |
|   Harvested |             |             |             |             |
|    forage   |             |             |             |             |
+=============+=============+=============+=============+=============+
|    Grazed   | 0           | 0           | 147         | 0           |
|    forage   |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             | 161         | 112         | 123         | 163         |
|   Harvested |             |             |             |             |
|    grain    |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             | 201         | 157         | 127         | 203         |
|   Purchased |             |             |             |             |
|    feed     |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Total    | 884         | 906         | 891         | 884         |
|    feed     |             |             |             |             |
|    intake   |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

..

   Greenhouse gas emissions (kg)

+-------------+-------------+-------------+-------------+-------------+
|    Methane  | 21,193      | 24,508      | 19,454      | 14,287      |
+=============+=============+=============+=============+=============+
|    Animal   | 14,203      | 17,102      | 17,458      | 14,195      |
|    and barn |             |             |             |             |
|    floor    |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Manure   | 6,971       | 7,387       | 1,986       | 70          |
|    storage  |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Field    | 20          | 19          | 11          | 22          |
|             |             |             |             |             |
| application |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Nitrous  | 642         | 628         | 681         | 454         |
|    oxide    |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Carbon   | 150,478     | 79,249      | 38,780      | 172,611     |
|    dioxide  |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Net farm | 871,619     | 879,093     | 728,068     | 665,078     |
|    emission |             |             |             |             |
|             |             |             |             |             |
|   (CO2e)[e] |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

..

   [a] 100 Holstein cows producing 9,000 kg per cow of milk plus 80
   replacement heifers housed year round in free‐stall barns with feed
   produced from 50 ha of corn, 20 ha of perennial grassland, and 20 ha
   of alfalfa.

   [b] Lactating herd fed a maximum‐forage diet (60% of forage from corn
   silage) while maintaining 9,000 kg cow‐1 milk production.

   [c] Lactating herd fed a minimum‐forage diet (50% of forage from corn
   silage) while maintaining adequate fiber for 9,000 kg cow‐1 milk
   production.

   [d] Farm with low‐forage diet and enclosed manure storage. Methane
   from storage is converted to CO2 through combustion (99% efficiency).

   [e] Total CO2‐equivalent greenhouse gas emission considering the
   global warming potential of CH4 and N2O to be 25 and 298 times that
   of CO2, respectively.

   Vol. 52(4): 1313-1323 1321

much less manure being stored during the summer months, CH4 emissions
from manure storage and field application were greatly reduced. With
these changes, total CH4 emis‐sion from the farm was reduced 21%
compared to the high‐forage feeding strategy without grazing. Nitrous
oxide emission increased 8% due to the higher concentration of N in
urine deposits (Chianese et al., 2009b), and net CO2 emis‐sion decreased
through greater use of farm‐produced feeds (Chianese et al., 2009a).
Overall, net GHG emission was re‐duced 17% with the use of this grazing
strategy.

With an enclosed manure storage, the CH4 produced can be captured and
burned. Combustion of the biogas transforms the CH4 to CO2 (Chianese et
al., 2009a). Since CO2 has 25�times less global warming potential, the
net result is a re‐duction in GHG emissions. Compared to the open
storage tank in the low‐forage diet scenario, simulated CH4 emission
from the storage was reduced by 99% while net farm CO2 emission was
increased 15% (table 6, column 4 vs. 1). Meth‐ane emission following
field application was increased a small and unimportant amount. Covering
the manure storage also eliminated N2O emission from the storage by
preventing crusting on the manure surface (Chianese et al., 2009b). The
overall net effect of using this strategy was a 24% reduction in the
total global warming potential of the whole‐farm emis‐sion of GHGs
(table 6, column 4 vs. 1).

| **CONCLUSIONS**
| A module simulating CH4 emissions from enteric fer‐mentation, slurry
  manure storage, field‐applied manure, feces deposited in pasture, and
  manure on free‐stall barn floors was developed from previously
  published relation‐ships and experimental data and added to a farm
  simulation model (Integrated Farm System Model, or IFSM).
  Relation‐ships selected were consistent with our modeling objectives
  and the current structure of IFSM.

The expanded IFSM was shown to predict CH4 emissions that were
consistent with reported emissions from specific experiments and data
summarized for whole dairy farm sys‐tems. A sensitivity analysis
identified important parameters and illustrated that model predictions
responded appropriate‐ly to changes in model parameters.

Incorporation of the CH4 module with IFSM, along with modules simulating
CO2 and N2O emissions, provides a tool for evaluating the overall impact
of management scenarios used to reduce GHG emissions from dairy farms.
Farm simu‐lations showed that increasing the use of forage (corn silage)
in animal diets increased CH4 emission by 16% with little im‐pact on the
global warming potential of net farm emissions of all GHGs. Use of
grazing along with high‐forage diets re‐duced CH4 and net farm GHG
emissions by 8% and 16%, re‐spectively. Using a manure storage cover and
burning the captured biogas reduced farm emission of CH4 by 32% with a
24% reduction in the net farm emission of GHGs.

   Benchaar, C., J. Rivest, C. Pomar, and J. Chiquette. 1998.

   | Prediction of methane production from dairy cows using
   | existing mechanistic models and regression equations. *J. Animal
     Sci.* 76(2): 617‐627.

   Blaxter, K. L., and J. L. Clapperton. 1965. Prediction of the amount
   of methane produced by ruminants. *British J. Nutr.* 19: 511‐522.

   Chadwick, D. R., and B. F. Pain. 1997. Methane fluxes following
   slurry applications to grassland soils: Laboratory experiments.
   *Agric. Ecosyst. Environ.* 63(1): 51‐60.

   Chen, Y. R., and A. G. Hashimoto. 1980. Substrate utilization kinetic
   model for biological treatment processes. *Biotech.*

   *Bioeng.* 22(10): 2081‐2095.

   | Chianese, D. S., C. A. Rotz, and T. L. Richard. 2009a. Simulation
     of carbon dioxide emissions from dairy farms to assess
   | greenhouse gas reduction strategies. *Trans. ASABE* 52(4):
     1301-1312.

   Chianese, D. S., C. A. Rotz, and T. L. Richard. 2009b. Simulation of
   nitrous oxide emissions from dairy farms to assess greenhouse gas
   reduction strategies. *Trans. ASABE* 52(4): 1325-1335.

   | Chianese, D. S., C. A. Rotz, and T. L. Richard. 2009c. Whole‐farm
     greenhouse gas emissions: A review with application to a
   | Pennsylvania dairy farm. *Applied Eng. in Agric*. 25(3): 431‐442.

   Dijkstra, J., H. D. St. C. Neal, D. E. Beever, and J. France. 1992.

   Simulation of nutrient digestion, absorption, and outflow in the
   rumen: Model description. *J. Nutr.* 122(11): 2239‐2256.

   EIA. 2007. Emissions of greenhouse gases in the United States.

   Washington, D.C.: U.S. Department of Energy, Energy Information
   Administration. Available at: www.eia.doe.gov/
   oiaf/1605/ggrpt/index.html. Accessed 2 January 2008.

   | EPA. 1999. U.S. methane emissions 1990‐2020: Inventories,
   | projections, and opportunities for reductions. EPA
   | 430‐R‐99‐013. Washington, D.C.: U.S. Environmental
   | Protection Agency. Available at: yosemite.epa.gov/OAR/
   | globalwarming.nsf/UniqueKeyLookup/SHSU5BUT5X/$File/m
     ethane_emissions.pdf. Accessed 17 July 2009.

   FAO. 2006. *Livestock's Long Shadow.* H. Steinfeld, P. Gerber, T.

   Wassenaar, V. Castel, M. Rosales, and C. de Haan, eds. Rome, Italy:
   United Nations Food and Agriculture Organization.

   Flessa, H. P. Dörsch, F. Beese, H. Konig, and A. F. Bouwman.

   1996. Influence of cattle wastes on nitrous oxide and methane fluxes
   in pasture land. *J. Environ. Qual.* 25(6): 1366‐1370.

   García‐Ochoa, F., V. E. Santos, L. Naval, E. Guardiola, and B.

   López. 1999. Kinetic model for anaerobic digestion of livestock
   manure. *Enzyme Microb. Tech.* 25(1‐2): 55‐60.

   Hill, D. T. 1982. A comprehensive dynamic model for animal waste
   methanogensis. *Trans. ASAE* 28(3): 850‐855.

   Hill, D. T. 1991. Steady‐state mesophilic design equations for
   methane production from livestock wastes. *Trans. ASAE* 34(5):
   2157‐2163.

   Holter, P. 1997. Methane emissions from Danish cattle dung pats in
   the field. *Soil Biol. Biochem.* 29(1): 31‐37.

   Husted, S. 1994. Seasonal variation in methane emission from stored
   slurry and solid manure. *J. Environ. Qual.* 23(3): 585‐592.

   IPCC. 2006a. Guidelines for national greenhouse gas inventories:
   General guidance and reporting. Intergovernmental Panel on Climate
   Change. Available at: www.ipcc‐nggip.iges.or.jp/
   public/2006gl/vol1.html. Accessed 2 January 2009.

IPCC. 2006b. Guidelines for national greenhouse inventories. Vol.

   4: Agriculture, forestry and other land use. Intergovernmental Panel
   on Climate Change. Available at: www.ipcc‐nggip.

iges.or.jp/public/2006gl/vol4.html. Accessed 26 November

+-----------------------------------+-----------------------------------+
| **REFERENCES**                    | 2008.                             |
|                                   |                                   |
|                                   | IPCC. 2007. Chapter 2: Changes in |
|                                   | atmospheric constituents and in   |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   *ASABE Standards.* 2008. D384.2: Manure production and
   characteristics. St. Joseph, Mich.: ASABE.

Baldwin, R. L., J. H. M. Thornley, and D. E. Beever. 1987. Metabolism of
the lactating cow: II. Digestive elements of a mechanistic model. *J.
Dairy Res.* 54(1): 107‐131.

   radiative forcing. In *Climate Change 2007: The Physical Science
   Basis*. Contribution of Working Group I to the Fourth Assessment
   Report of the Intergovernmental Panel on Climate Change. New York,
   N.Y.: Cambridge University Press. Available

   1322 TRANSACTIONSOFTHE ASABE

   at: www.ipcc.ch/pdf/assessment‐report/ar4/wg1/ar4‐wg1‐chapter2.pdf.
   Accessed 28 November 2008.

Jarvis, S. C., R. D. Lovell, and R. Panayides. 1995. Patterns of methane
emission from excreta of grazing animals. *Soil Biol.*

   *Biochem.* 27(12): 1581‐1588.

Keppler, F., and T. Röckmann. 2007. Methane, plants, and climate change.
*Sci. American* (Feb.): 52‐57.

Kinsman, R., F. D. Sauer, H. A. Jackson, and M. S. Wolynetz. 1995.

   Methane and carbon dioxide emissions from dairy cows in full
   lactation monitored over a six month period. *J. Dairy Sci.*

   Rotz, C. A., M. S. Corson, D. S. Chianese, and C. U. Coiner. 2009.
   *The Integrated Farm System Model: Reference Manual*.

   | University Park, Pa.: USDA‐ARS Pasture Systems and
   | Watershed Management Research Unit. Available at:
   | www.ars.usda.gov/SP2UserFiles/Place/19020000/ifsmreference. pdf.
     Accessed 17 July 2009.

   | Saggar, S., N. S. Bolan, R. Bhandral, C. B. Hedley, and J. Luo.
     2004. A review of emissions of methane, ammonia, and nitrous oxide
     from animal excreta deposition and farm effluent
   | application in grazed pastures. *New Zealand J. Agric.* 47(4):

   78(12): 2760‐2766. 513‐544.

Kirchgessner, M., W. Windisch, H. L. Müller, and M. Kreuzer.

   1991. Release of methane and of carbon dioxide by dairy cattle.
   *Agribiol. Res.* 44(2‐3): 91‐102.

Lovett, D. K., L. Shalloo, P. Dillon, and F. P. O'Mara. 2006. A systems
approach to quantify greenhouse gas fluxes from pastoral dairy
production as affected by management regime. *Agric. Syst.* 88(2‐3):
156‐179.

Madigan, M. T., J. M. Martinko, and J. Parker. 2003. *Brock Biology*

   Schils, R. L. M., A. Verhagen, H. F. M. Aarts, and L. B. J. Sebek.

   2005. A farm‐level approach to define successful mitigation
   strategies for GHG emissions from ruminant livestock systems. *Nutr.
   Cycl. Agroecosyst*. 71(2): 163‐175.

   Sherlock, R. R., S. G. Sommer, R. Z. Khan, C. W. Wood, E. A. Guertal,
   J. R. Freney, C. O. Dawson, and K. C. Cameron. 2002. Ammonia,
   methane, and nitrous oxide emission from pig slurry applied to a
   pasture in New Zealand. *J. Environ. Qual.* 31(5):

   *of Microorganisms*. Englewood Cliffs, N.J.: Prentice Hall.
   1491‐1501.

| Mills, J. A. N., J. Dijkstra, A. Bannink, S. B. Cammell, E. Kebreab,
  and J. France. 2001. A mechanistic model of whole‐tract
| digestion and methanogenesis in the lactating dairy cow: Model
  development, evaluation, and application. *J. Animal Sci.* 79(6):

   Sommer, S. G., R. R. Sherlock, and R. Z. Khan. 1996. Nitrous oxide
   and methane emissions from pig slurry amended soils. *Soil Biol.
   Biochem.* 28(10/11): 1541‐1544.

Sommer, S. G., S. O. Petersen, and H. B. Møller. 2004. Algorithms

   1584‐1597. for calculating methane and nitrous oxide emissions from

Mills, J. A. N., E. Kebreab, C. M. Yates, L. A. Crompton, S. B. Cammell,
M. S. Dhanoa, R. E. Agnew, and J. France. 2003. Alternative approaches
to predicting methane emissions from dairy cows. *J. Animal Sci.*
81(12): 3141‐3150.

   manure management. *Nutr. Cycl. Agroecosyst.* 69(2): 143‐154.

   | van Hulzen, J. B., R. Segers, P. M. van Bodegom, and P. A.
   | Leffelaar. 1999. Temperature effects on soil methane production: An
     explanation for observed variability. *Soil Biol. Biochem.*

Moe, P. W., and H. F. Tyrrell. 1979. Methane production in dairy 31(14):
1919‐1929.

   cows. *J. Dairy Sci.* 62(10): 1583‐1586.

Monteny, G. J., C. M. Groenestein, and M. A. Hilhorst. 2001.
Interactions and coupling between emissions of methane and nitrous oxide
from animal husbandry. *Nutr. Cycl. Agroecosyst.*

   Wilkerson, V. A., D. P. Casper, and D. R. Mertens. 1995. The
   prediction of methane production of Holstein cows by several
   equations. *J. Dairy Sci.* 78(11): 2402‐2414.

   Yamulki, S., S. C. Jarvis, and P. Owen. 1999. Methane emission and

   60: 123‐132. uptake from soils as influenced by excreta deposition
   from

NRC. 2001. *Nutrient Requirements of Dairy Cattle.* 7th ed. Washington,
D.C.: National Research Council.

Paul, J. W., and E. G. Beauchamp. 1989. Relationship between volatile
fatty acids, total ammonia, and pH in manure slurries. *Biol. Waste*
29(4): 313‐318.

Rotz, C. A., D. R. Mertens, D. R. Buckmaster, M. S. Allen, and J.

   H. Harrison. 1999. A dairy herd model for use in whole farm
   simulations. *J. Dairy Sci.* 82(12): 2826‐2840.

   grazing animals. *J. Environ. Qual.* 28(2): 676‐682.

   Yates, C. M., S. B. Cammell, J. France, and D. E. Beever. 2000.
   Prediction of methane emissions from dairy cows using multiple
   regression analysis. In *Proc. 2000 Annual Conf.*, 94. Penicuik,
   U.K.: British Society of Animal Science.

   Zeeman, G. 1994. Methane production/emission in storages for animal
   manure. *Fert. Res.* 37(3): 207‐211.

   Zeikus, J. G., and M. R. Winfrey. 1976. Temperature limitation of
   methanogenesis in aquatic sediments. *Appl. Environ.Microbiol.*
   31(1): 99‐107.

   Vol. 52(4): 1313-1323 1323

+-----------------------------------+-----------------------------------+
|    1324                           | TRANSACTIONSOFTHE ASABE           |
+===================================+===================================+
+-----------------------------------+-----------------------------------+
