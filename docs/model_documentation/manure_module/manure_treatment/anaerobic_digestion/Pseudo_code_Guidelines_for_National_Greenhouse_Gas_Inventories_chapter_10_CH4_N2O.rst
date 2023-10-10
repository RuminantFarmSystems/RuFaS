Guidelines for Nation Greenhouse Gases 
========================================

Manure Module: Calculate Methane (CH4) and Nitrous Oxide (N2O) Emissions
from Digester

   3.Calculate Methane (CH4) and Nitrous Oxide (N2O) Emissions.

   •Inputs (All inputs come from the weather file, the Animal Module).

+-----------------------------------+-----------------------------------+
| i.                                |    | N_T = number of head of      |
|                                   |      livestock species/category   |
| ii.                               |    | VS_T = annual average VS     |
|                                   |      excretion per head of        |
| iii.                              |      species/category T AWMS_TS = |
|                                   |      fraction of total annual VS  |
|                                   |      for each livestock           |
|                                   |      species/category             |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   T that is managed in manure system S

+-----------------------------------+-----------------------------------+
| iv.                               |    N_TP = number of head of       |
|                                   |    livestock species/category T   |
|                                   |    in the country,                |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   for productivity system P

+-----------------------------------+-----------------------------------+
| v.                                |    AWMS_TSP = fraction of total   |
|                                   |    annual VS for each livestock   |
|                                   |    species/category               |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   T that is managed in manure management system S in the country, for

   productivity system P

+-----------------------------------+-----------------------------------+
| vi.                               |    V_CH4_prod = specific volume   |
|                                   |    of methane produced in the     |
|                                   |    digester, m^3                  |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   CH4 kg^-1 VS

+-----------------------------------+-----------------------------------+
| vii.                              |    V_CH4_used = specific volume   |
|                                   |    of methane used for energy     |
|                                   |    production, m^3                |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   CH4 kg^-1 VS

+-----------------------------------+-----------------------------------+
|    | viii.                        |    V_CH4_flared = specific volume |
|    | ix.                          |    of methane flared, m^3 CH4     |
|                                   |    kg^-1 VS MCF_residues =        |
|                                   |    methane conversion factor for  |
|                                   |    the storage of digested        |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   manure, %

+-----------------------------------+-----------------------------------+
| x.                                |    B0 = maximum methane producing |
|                                   |    capacity for manure produced   |
|                                   |    by                             |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   livestock category T, m^3 CH4 kg^-1 of VS excreted

+-----------------------------------+-----------------------------------+
| xi.                               |    V_CH4_leak = specific volume   |
|                                   |    of methane due to leakage and  |
|                                   |    maintenance                    |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   works, m^3 CH4 kg^-1 VS

+-----------------------------------+-----------------------------------+
| xii.                              |    Nex_TP = annual average N      |
|                                   |    excretion per head of          |
|                                   |    species/category T in the      |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   country, kg N animal^-1 yr^-1

   1

   | xiii. EF_3S = emission factor for direct N2O emissions from manure
     management system S in the country, kg N2O-N/kg N in manure
     management system S
   | xiv. Frac_GasMs = percent of managed manure nitrogen for livestock
     category T that volatilises as NH3 and NOx in the manure management
     system S, % EF_4 = emission factor for N2O emissions from
     atmospheric deposition xv.

   | of nitrogen on soils and water surfaces, kg N2O-N (kg NH3-N + NOx-N
     volatilised)^-1
   | xvi. Nex_T = annual average N excretion per head of
     species/category T in the country, kg N animal^-1 yr^-1
   | xvii. Frac_leachMS = percent of managed manure nitrogen losses for
     livestock category T due to runoff and leaching during solid and
     liquid storage of manure, derived from country specific data, to be
     developed specifically for regions with high rainfall rates and
     outdoor uncovered manure pens.

   xviii. EF_5 = emission factor for N2O emissions from nitrogen
   leaching and runoff, kg N2O-N/kg N leached and runoff

   •Outputs

+-----------------------------------+-----------------------------------+
| i.                                | 𝐶𝐻4(𝑚𝑚) = CH4 emissions from      |
|                                   | Manure Management in the country, |
|                                   | kg                                |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   CH4 yr-1 .

+-----------------------------------+-----------------------------------+
| ii.                               |    𝑁2𝑂𝐷(𝑚𝑚) = Direct N2O          |
|                                   |    emissions from Manure          |
|                                   |    Management in the              |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   country, kg N2O yr-1 .

+-----------------------------------+-----------------------------------+
| iii.                              |    N2OG(mm) = Indirect N2O        |
|                                   |    emissions due to               |
|                                   |    volatilization of N from       |
|                                   |    Manure                         |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   Management in the country, kg N2O yr-1 .

   iv. N2OL(mm) = Indirect N2O emissions due to leaching and runoff from
   Manure Management in the country, kg N2O yr-1 .

   2

   | 1.Calculate Methane CH4 emissions from manure management
   | 1.Effective methane conversion factor for combination digester and
     storage

+-----------------------+-----------------------+-----------------------+
|                       | 𝑣𝐶𝐻4_𝑝𝑟𝑜𝑑−𝑣𝐶𝐻4_𝑢      | [M.3.1.1]             |
|                       | 𝑠𝑒𝑑−𝑣𝐶𝐻4_𝑓𝑙𝑎𝑟𝑒𝑑+𝑀𝐶𝐹𝑟𝑒 |                       |
|                       | 𝑠𝑖𝑑𝑢𝑒𝑠•(𝐵0−𝑣𝐶𝐻4_𝑝𝑟𝑜𝑑) |                       |
+=======================+=======================+=======================+
|    𝑀𝐶𝐹 =              | 𝐵0                    |                       |
+-----------------------+-----------------------+-----------------------+

..

   | 2.Methane CH4 emissions from manure management
   | EF(T) = VST ∗ BO ∗ 0.67 ∗ MCF ∗ AWMSTS [M.3.2.1] 3.Methane CH4
     emissions from manure management

+-----------------+-----------------+-----------------+-----------------+
|    𝑛𝑜_𝑐𝑎𝑡𝑒𝑔𝑜𝑟𝑦  | 𝑁_𝑇             | ∗ 𝑉𝑆𝑇           |    ∗ 𝐴𝑊𝑀𝑆𝑇𝑆 ) ∗ |
|    𝐶𝐻4(𝑚𝑚) =    |                 |                 |    𝐸𝐹_𝑇𝑆 /1000  |
|    ∑𝑇=0 (       |                 |                 |    [M.3.3.1]    |
+=================+=================+=================+=================+
+-----------------+-----------------+-----------------+-----------------+

..

   2. Calculate Nitrous oxide N2O emissions from manure management

   4. Direct Nitrous oxide N2O emissions from Manure Management

+-----------------------+-----------------------+-----------------------+
|    𝑁2𝑂𝐷(𝑚𝑚) =         |    (𝑁𝑇𝑃 ∗ 𝑁𝑒𝑥𝑇𝑃 ∗     |    | 44               |
|    ∑𝑛𝑜_𝑐𝑎𝑡𝑒𝑔𝑜𝑟𝑦       |    𝐴𝑊𝑀𝑆𝑇𝑆𝑃) ∗ 𝐸𝐹3𝑆 ∗  |    | 28 [M.3.4.1]     |
+=======================+=======================+=======================+
+-----------------------+-----------------------+-----------------------+

..

   5. Amount of manure nitrogen that is lost due to volatilization of
   NH3 and NOx

+-----------------------+-----------------------+-----------------------+
|                       |    𝐹𝑟𝑎𝑐_𝐺𝑎𝑠𝑀𝑆 (𝑁𝑇𝑃 ∗  | )TS [M.3.5.1]         |
|  Nvolatilization_MMs= |    𝑁𝑒𝑥𝑇𝑃 ∗ 𝐴𝑊𝑀𝑆𝑇𝑆𝑃) ∗ |                       |
|    ∑𝑛𝑜_𝑐𝑎𝑡𝑒𝑔𝑜𝑟𝑦 𝑇=0   |    ( 100              |                       |
+=======================+=======================+=======================+
+-----------------------+-----------------------+-----------------------+

..

   6. Indirect N2O emissions due to volatilization of N from Manure
   Management

+-----------------------------------+-----------------------------------+
|    𝑁2𝑂𝐺(𝑚𝑚) =                     |    | 44                           |
|    (𝑁𝑣𝑜𝑙𝑎𝑡𝑖𝑙𝑖𝑧𝑎𝑡𝑖𝑜𝑛−𝑀𝑀𝑆 ∗ 𝐸𝐹4) ∗  |    | 28 [M.3.6.1]                 |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   7. Amount of manure nitrogen that leached from manure management
   systems

+-----------------+-----------------+-----------------+-----------------+
|    N            |    ()           | 𝐹𝑟𝑎𝑐_𝑙𝑒𝑎𝑐ℎ𝑀𝑆    | )[M.3.7.1]      |
|    ∑𝑛𝑜_𝑐𝑎𝑡𝑒𝑔𝑜𝑟𝑦 |                 |                 |                 |
+=================+=================+=================+=================+
|                 |    𝑁𝑇 ∗ 𝑁𝑒𝑥𝑇 ∗  | 100             |    TS           |
|   leaching_MMs= |    𝐴𝑊𝑀𝑆𝑇𝑆∗ (    |                 |                 |
|    𝑇=0          |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

..

   3

   8. Indirect N2O emissions due to leaching and runoff from Manure
   Management

+-----------------------------------+-----------------------------------+
|    𝑁2𝑂𝐿(𝑚𝑚) = (𝑁𝑙𝑒𝑎𝑐ℎ𝑖𝑛𝑔−𝑀𝑀𝑆 ∗    |    | 44                           |
|    𝐸𝐹5) ∗                         |    | 28 [M.3.8.1]                 |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   | **References**
   | Eggleston, S., Buendia, L., Miwa, K., Ngara, T., & Tanabe, K.
     (Eds.). (2006). *2006 IPCC*

   *guidelines for national greenhouse gas inventories* (Vol. 5).
   Hayama, Japan: Institute for Global

   Environmental Strategies.

   4
