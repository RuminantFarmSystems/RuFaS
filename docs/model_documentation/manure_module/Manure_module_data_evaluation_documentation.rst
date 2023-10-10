Manure Module Data Evaluation Documentation
===========================================
   
   **Overview:**

-  In the manure module, we have developed several methods that simulate
   the manure handling system and gas emissions that represent a
   specific manure management scenario (MMS). We have performed unit
   tests (manual testing of the equation to check if the output data is
   within the range as expected) using default/book values to simulate
   the numbers before merging the code to the master branch.

-  Currently, we are performing the data evaluation and comparison
   analysis from the simulation output. During this process, we have
   individual data created from different methods of a certain MMS.

-  We have seven distinct MMS_xi (scenarios could be
   increased/decreased, i=7). Each MMS is defined by a combination of
   (up to) four individual defined operations/activities:
   “bedding_type": "sawdust", "manure_handler": "flush system",
   "manure_separator": "rotary screen", "manure_treatment": “slurry
   storage”. These methods each have sub-components that can be
   selected.

-  During simulation, each defined operation calculates the input and
   output variables assigned to ensure a mass balance at a process
   level. Table 1 provides each method's (or operation/activity)
   simulated variables (influent_xj and effluent_xk) (j=4, k=4).

**Model evaluation methodology:**

-  The manure module simulates output on a process level (that is for
   each individual activity in the MMS) during different stages of the
   manure life cycle (Collection, handling, treatment, and storage). The
   output from each stage includes manure quantity, nutrient data, and
   gas emissions.

-  The farm/experimental data compiled from literature and extension
   specialists is organized in a similar pattern to facilitate
   comparison with RuFaS simulation (based on the limited data
   gathered).

-  The compiled farm/experimental data for each variable (for example
   housing/treatment gas emissions, manure nutrient composition etc.,)
   provides a range of values that can be tested as a reference against
   the manure module simulation output-or to provide a target for
   calibration.

-  The farm/experimental data gathered is specific to each particular
   MMS scenario. For example, MMS_1 could be a combination of organic
   bedding, flush system, no separator, and lagoon treatment. So, this
   specific combination of manure methods (activities) is assigned to
   MMS_x1 within the RuFaS manure module and is available to be
   simulated.

-  Once we have the simulation output, the simulated data is compared
   against the farm/experimental data after ensuring compatible units
   for the comparison.

-  After the evaluation, if the simulated results are within the
   expected data range (that is the reported experimental data), those
   equations will be marked as okay.

-  If the simulated output is not as expected, we would revise and
   update the computational algorithm as needed. Then re-run the
   simulation to ensure that the simulated output falls within the
   allowable tolerance for acceptance (10-30%).

-  Next, we change the combination of MMS scenario with different
   methods and continue to evaluate the data.

**Evaluation process:**

The evaluation process includes data assessment of simulation output
against independent farm data, including datasets obtained during
different stages of the manure life cycle. The farm datasets used for
the quantitative evaluation include: Gaseous emissions and manure
nutrient data from dairy housing and manure management practices
(includes specific stage and entire system).

**Input Simulation:**

-  Model Input information is supplied through three data files: Animal
   module, Manure management input, and Weather parameter files.

-  The animal module JSON file contains data that describes the farm pen
   type, housing, animal types, number of animals at various stages, and
   bedding type.

-  The manure module JSON file contains data that describes the manure
   collection, handling, treatment, and storage practices. The
   combination of manure practices could be modified to represent the
   user farm situation.

-  The weather data file contains daily weather for many years for a
   particular location. The weather data includes the year and the day
   of that year, minimum temperature (°C) , maximum temperature (°C),
   mean temperature (°C), and precipitation (mm).

-  The simulation begins by reading the input information supplied by
   the user and can be modified by editing the values in the input menus
   and dialog boxes that represent the user’s farm situation.

-  After the input parameters are set, a simulation can be performed.

-  The input parameters that are supplied to the simulation include:

   -  sim_day, pen_id, pen_num_animals, pen_animal_types,
      pen_housing_type, pen_bedding_type, pen_hanlder_type,
      pen_separator_type, and pen_treatment_type.

-  sim_day - Number of days the simulation is performed.

-  pen_id - Categorizing the pen allocation within a farm.

-  pen_num_animals - Number of animals within each pen that are
      simulated.

-  pen_animal_types - Type of animal class within each pen that are
      simulated.

-  pen_housing_type - Describes the pen housing type.

-  pen_bedding_type - Describes the bedding type that is used.

-  pen_hanlder_type - Describes the manure collection and handling
      method that is used.

-  pen_separator_type - Describes the solid-liquid separation equipment
      that is used.

-  pen_treatment_type - Describes the manure treatment that is used.

-  In addition to these parameters, the animal module reports the manure
   characteristics data and is passed to the manure module simulation.

-  The manure characteristics include:

   -  Manure mass (kg), TS (kg), VS (kg), N (kg), P (kg), K (kg),
      urine_TAN (kg), manure_TAN (kg), Urine (kg), and TAN (kg) on a
      daily time step.

**Output Simulation:**

Following the simulation, the summary output provides each parameter's
simulated values. The reported parameters include manure quantity,
nutrient data, and gaseous emissions. The parameters reported in the
output file include information on the pen type, manure quantity, manure
nutrient, and gas emissions during different stages of manure handling
methods on a daily time step that the user specifies.

The output data include:

-  No. of animals (animal type) - Includes the animal type and total
   number of animals on the farm contributing to each manure management
   system.

-  Manure volume (m\ :sup:`3`) – Includes the daily total manure volume
   (manure, bedding and wash water). The manure quantity and nutrient
   content is a function of the collection method - bedding, wash water
   and collection method (flushing/scraping).

-  Manure_nutrient_data - The daily manure nutrient content TS, VS, N, P
   and K (kg day\ :sup:`-1`)

-  Housing_Methane (kg) – The daily rate of CH\ :sub:`4` emission from
   the barn floor (kg CH\ :sub:`4` day\ :sup:`-1`)

-  Housing_Ammonia (kg) - The daily rate of ammonia emission from the
   barn floor (kg NH\ :sub:`3`-N day\ :sup:`-1`)

-  Trt_Methane (kg) - The daily rate of CH\ :sub:`4` emission from the
   storage/treatment (kg CH\ :sub:`4` day\ :sup:`-1`)

-  Trt_Ammonia (kg) - The daily rate of ammonia emission from the
   storage/treatment (kg NH\ :sub:`3`-N day\ :sup:`-1`)

-  Trt_Nitrous oxide (kg) - The daily rate of nitrous oxide emission
   from the storage/treatment (kg N₂O day\ :sup:`-1`)

**Quantitative assessment:**

After the simulation, the output data is quantitively compared with the
observed farm and literature data (Chianese et al., 2009; Leytem et al.,
2011; Owen and Boehm, 2015; ASABE, 2019). The output data includes the
accumulation of whole farm manure management and individual manure
methods on a process level. The observed farm and literature data
include information on a specific farm representing the scenario
simulated in the model.

For example, the observed farm and literature data have a scenario with
a certain combination of pen and manure handling methods:

-  sim_day, pen_id, pen_num_animals, pen_animal_types, pen_housing_type,
   pen_bedding_type, pen_hanlder_type, pen_separator_type, and
   pen_treatment_type.

The same scenario information is used as input to the model, and the
simulation is performed. Then the output is compared with the farm data.

The assessment is performed as follows:

-  The output parameters include the list as presented in Table 1
   (influent and effluent) corresponding to each handling method of a
   manure management scenario on a process level.

-  The manure mass or volume (kg or m\ :sup:`3`) and nutrient data (kg)
   produced from each pen on a daily time step from the simulation will
   be plotted against the data from observed farm data.

-  Mostly SI units are used for the comparison against simulation and
   observed data (conversion performed accordingly)

-  Similarly, the gas emissions data (kg day\ :sup:`-1`) from housing
   and treatment stage emitted are compared.

-  The assessment is performed by taking a single output variable on a
   daily basis and also the cumulative (mean and standard deviation)
   over a simulation period (For example: Housing methane emission kg
   CH4 day-1) and plotted against the literature or farm data.

-  The selected variable output “mean and standard deviation” data
   comparison provides us the information to test the model prediction
   accuracy.

**Table 1. List of variables that are simulated in each method**

+---+------------+-------------+-------+--------+-------+-------------+
|   | **Manure   |             | **M   |        | **M   |             |
|   | handling** |             | anure |        | anure |             |
|   |            |             | se    |        | t     |             |
|   |            |             | parat |        | reatm |             |
|   |            |             | ors** |        | ent** |             |
+===+============+=============+=======+========+=======+=============+
|   | **Inf      | **Ef        | **Inf | **E    | **Inf | **Ef        |
|   | luent_xj** | fluent_xk** | luent | ffluen | luent | fluent_xk** |
|   |            |             | _xj** | t_xk** | _xj** |             |
+---+------------+-------------+-------+--------+-------+-------------+
| 1 | Manure     | Manure      | \*\*  | Manure | \*\*  | Manure      |
|   | volume     | volume      |       | volume |       | volume      |
+---+------------+-------------+-------+--------+-------+-------------+
| 2 | TS         | TS          | \*\*  | TS     | \*\*  | TS          |
+---+------------+-------------+-------+--------+-------+-------------+
| 3 | VS         | VS          | \*\*  | VS     | \*\*  | VS          |
+---+------------+-------------+-------+--------+-------+-------------+
| 4 | N          | N           | \*\*  | N      | \*\*  | N           |
+---+------------+-------------+-------+--------+-------+-------------+
| 5 | P          | P           | \*\*  | P      | \*\*  | P           |
+---+------------+-------------+-------+--------+-------+-------------+
| 6 | K          | K           | \*\*  | K      | \*\*  | K           |
+---+------------+-------------+-------+--------+-------+-------------+
| 7 | Urine_TAN  | Hous        | \*\*  | \*\*   | \*\*  | Hous        |
|   |            | ing_Methane |       |        |       | ing_Methane |
+---+------------+-------------+-------+--------+-------+-------------+
| 8 | Urine      | Hous        | \*\*  | \*\*   | \*\*  | Hous        |
|   |            | ing_Ammonia |       |        |       | ing_Ammonia |
+---+------------+-------------+-------+--------+-------+-------------+
| 9 | Manure_TAN | Trt_Methane | \*\*  | \*\*   | \*\*  | Trt_Methane |
+---+------------+-------------+-------+--------+-------+-------------+
| 1 | enter      | Trt_Ammonia | \*\*  | \*\*   | \*\*  | Trt_Ammonia |
| 0 | ic_methane |             |       |        |       |             |
+---+------------+-------------+-------+--------+-------+-------------+
| 1 | \*\*       | Trt_Nitrous | \*\*  | \*\*   | \*\*  | Trt_Nitrous |
| 1 |            | oxide       |       |        |       | oxide       |
+---+------------+-------------+-------+--------+-------+-------------+

**References:**

1. Chianese, D. S., Rotz, C. A., & Richard, T. L. (2009). Simulation of
   methane emissions from dairy farms to assess greenhouse gas reduction
   strategies. Transactions of the ASABE, 52(4), 1313-1323.

2. ASABE. 2019. ASAE D384.2 MAR2005 (R2019). Manure Production and
   Characteristics. ASABE, St. Joseph, Ml. 49085-9659, USA.

3. Jayasundara, S., Ranga Niroshan Appuhamy, J. A. D., Kebreab, E., &
   Wagner-Riddle, C. (2016). Methane and nitrous oxide emissions from
   Canadian dairy farms and mitigation options: An updated review.
   Canadian Journal of Animal Science, 96(3), 306-331.

4. Grant, R. H., & Boehm, M. T. (2015). Inhomogeneity of methane
   emissions from a dairy waste lagoon. Journal of the Air & Waste
   Management Association, 65(11), 1306-1316.

5. Owen, J. J., & Silver, W. L. (2015). Greenhouse gas emissions from
   dairy manure management: a review of field‐based studies. Global
   change biology, 21(2), 550-565.

6. Leytem, A. B., Bjorneberg, D. L., Koehn, A. C., Moraes, L. E.,
   Kebreab, E., & Dungan, R. S. (2017). Methane emissions from dairy
   lagoons in the western United States. *Journal of dairy
   science*, *100*\ (8), 6785-6803.

7. Leytem, A. B., Dungan, R. S., Bjorneberg, D. L., & Koehn, A. C.
   (2011). Emissions of ammonia, methane, carbon dioxide, and nitrous
   oxide from dairy cattle housing and manure management
   systems. *Journal of environmental quality*, *40*\ (5), 1383-1394.

8. Strahm, T. D., Harner, J. P., Key, D. V., & Murphy, J. P. (2000).
   Manure and lagoon nutrients from dairies using flush systems.

9. Bjorneberg, D. L., Leytem, A. B., Westermann, D. T., Griffiths, P.
   R., Shao, L., & Pollard, M. J. (2009). Measurement of atmospheric
   ammonia, methane, and nitrous oxide at a concentrated dairy
   production facility in southern Idaho using open-path FTIR
   spectrometry. *Transactions of the ASABE*, *52*\ (5), 1749-1756.

**Model evaluation and code update (step 1):**

-  We are currently performing the simulation experiment for a single
   MMS or two MMS scenarios assigned to the animal_module_pen_ids. Once
   we have the output, we will compile the data and plot charts to
   compare it with the farm/experimental data.

-  The pseudo is cross-checked depending on the data.

-  Then Loi might help in making the changes.

-  The changes include updating the pseudo-code, performing a unit test,
   and cross-checking the changes providing the expected output.

-  Based on the corrections/changes needed, Loi could support roughly
   four to five hours per week. When Loi is allocated, I (Varma) will
   compile all the changes/updates beforehand required to share with
   Loi.

**Model evaluation and code updates (step 2):**

-  At present, we are running simulations for two MMS scenarios. We plan
   to increase the evaluation process with more combinations of MMS
   scenarios against the animal_module_pen_ids

**Timeline:**

+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
|                  | **M |     |     |     | **A |     |     |     |
|                  | arc |     |     |     | pri |     |     |     |
|                  | h** |     |     |     | l** |     |     |     |
+==================+=====+=====+=====+=====+=====+=====+=====+=====+
|                  | **W | **W | **W | **W | **W | **W | **W | **W |
|                  | eek | eek | eek | eek | eek | eek | eek | eek |
|                  | 1** | 2** | 3** | 4** | 1** | 2** | 3** | 4** |
+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
| Collec           |     |     |     |     |     |     |     |     |
| tion/compilation |     |     |     |     |     |     |     |     |
| -                |     |     |     |     |     |     |     |     |
| f                |     |     |     |     |     |     |     |     |
| arm/experimental |     |     |     |     |     |     |     |     |
| data             |     |     |     |     |     |     |     |     |
+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
| Meeting with Dr. |     |     |     |     |     |     |     |     |
| April and Dr.    |     |     |     |     |     |     |     |     |
| Greg about the   |     |     |     |     |     |     |     |     |
| data             |     |     |     |     |     |     |     |     |
| evalu            |     |     |     |     |     |     |     |     |
| ation/comparison |     |     |     |     |     |     |     |     |
| methodology      |     |     |     |     |     |     |     |     |
+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
| Data evaluation  |     |     |     |     |     |     |     |     |
+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
| Loi’s            |     |     |     |     |     |     |     |     |
| contribution to  |     |     |     |     |     |     |     |     |
| code/pseudo      |     |     |     |     |     |     |     |     |
| revision         |     |     |     |     |     |     |     |     |
| (roughly four to |     |     |     |     |     |     |     |     |
| five hours per   |     |     |     |     |     |     |     |     |
| week)            |     |     |     |     |     |     |     |     |
+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
| Data output      |     |     |     |     |     |     |     |     |
| review with Dr.  |     |     |     |     |     |     |     |     |
| April and Dr.    |     |     |     |     |     |     |     |     |
| Greg             |     |     |     |     |     |     |     |     |
+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
| Sensitivity      |     |     |     |     |     |     |     |     |
| analysis         |     |     |     |     |     |     |     |     |
| frame            |     |     |     |     |     |     |     |     |
| work/methodology |     |     |     |     |     |     |     |     |
+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
|                  |     |     |     |     |     |     |     |     |
+------------------+-----+-----+-----+-----+-----+-----+-----+-----+
