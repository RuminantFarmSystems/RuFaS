ManurePigs NH3 N2O CH4 Emissions
================================
   Manure Module: Calculate Ammonia (NH3), Nitrous Oxide (N2O) and
   Methane (CH4) Emissions by Animal Housing

   5.Calculate Ammonia (NH3), Nitrous Oxide (N2O) and Methane (CH4)
   Emissions by pigs.

   •Inputs (All inputs come from the weather file, the Animal Module).

+-----------------------------------+-----------------------------------+
| i.                                |    | TAN = Ammoniacal N           |
|                                   |      concentration (mg/kg)        |
| ii.                               |    | SurfaceArea = m^2            |
|                                   |    | StorageTime = days           |
| iii.                              |    | N_Initial = kg/kg            |
|                                   |    | VF_BeddingMaterialType =     |
| iv.                               |      kg/pig                       |
|                                   |    | VF_LitterSurface = m^2/pig   |
| v.                                |    | VF_Maintenance =             |
|                                   |    | VF_BeddingmaterialAmount =   |
| vi.                               |      kg/pig                       |
|                                   |    | VF_Mixing =                  |
| vii.                              |    | B0 = Maximum methane         |
|                                   |      producing capacity (m^3/kg ) |
| viii.                             |      VS = Total volatile solids   |
|                                   |      (kg)                         |
| ix.                               |    | MCF = methane conversion     |
|                                   |      factor                       |
| x.                                |    | EmissionFactor = (kg)        |
|                                   |    | VF_ManureType = (kg)         |
| xi.                               |    | VF_TurningNumber = (kg)      |
|                                   |    | VF_OutsideTemperature = (o C |
| xii.                              |      )                            |
|                                   |    | VF_CompostingDuration =      |
| xiii.                             |      (months)                     |
|                                   |    | TR = Read Temperature        |
| xiv.                              |      (K-Kelvin)                   |
|                                   |                                   |
| xv.                               |                                   |
|                                   |                                   |
| xvi.                              |                                   |
|                                   |                                   |
| xvii.                             |                                   |
|                                   |                                   |
| xviii.                            |                                   |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   •Outputs

+-----------------------------------+-----------------------------------+
| i.                                |    NH3_Outdoor = Ammonia from the |
|                                   |    outdoor slurry tank, g NH3/m2  |
| ii.                               |    per day. N_LossesBuilding =    |
|                                   |    total N losses                 |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   1

+-----------------------------------+-----------------------------------+
|    | iii.                         |    | NH3_EmittedBuilding =        |
|    | iv.                          |      Ammonia from the building    |
|    | v.                           |      N2O_EmittedBuilding =        |
|                                   |      Nitrous Oxide from building  |
| vi.                               |      CH4_Emitted = Methane CH4    |
|                                   |      Emissions                    |
|                                   |    | X_EmittedComposting =        |
|                                   |      Emitted Composting           |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   1.Calculate Ammonia from the outdoor slurry tank 1.VF_Temperature

+-----------------------------------+-----------------------------------+
|    Temp_Effluent=0.9614*TR+1.6889 | [M.5.1.1.1]                       |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   VF_Temperature=𝑒(0.08∗Temp_Effluent) /2.612 [M.5.1.1.2]

   | 2.VF_NDilution A Correction factor
   | VF_NDilution=TAN/1.03 [M.5.1.2]

   3.Ammonia from the outdoor slurry tank

   | NH3_Outdoor=1.57*VF_Temperature*VF_NDilution*VF_Cover*SurfaceArea*StorageTime
     [M.5.1.3] 2. Calculate total N losses
   | N_LossesBuilding=0.64*N_Initial*VF_BeddingMaterialType*VF_LitterSurface*VF_M
     aintenance*VF_BeddingmaterialAmount*VF_Mixing [M.5.2.1]

   | 3. Calculate NH3
   | NH3_EmittedBuilding=17/14*0.20*N_Initial*VF_LitterSurface*VF_Maintenance*VF\_
     BeddingmaterialAmount [M.5.3.1] 4. Calculate N2O
   | N2O_EmittedBuilding=44/28*0.06*N_Initial*VF_BeddingMaterialType*VF_LitterSurf
     ace*VF_Maintenance*VF_BeddingmaterialAmount*VF_Mixing [M.5.4.1]

   2

   | 5. Calculate CH4 emissions
   | CH4_Emitted=VS*B0*MCF [M.5.5.1] 6. Solid manure composting
   | X_EmittedComposting=EmissionFactor*VF_ManureType*VF_TurningNumber*VF_Outsid
     eTemperature*VF_CompostingDuration [M.5.6.1]

   | **References**
   | Rigolot, C., Espagnol, S., Robin, P., Hassouna, M., Béline, F.,
     Paillat, J. M., & Dourmad, J. Y. (2010). Modelling of manure
     production by pigs and NH3, N2O and CH4 emissions. Part II: effect
     of animal housing, manure storage and treatment practices. Animal,
     4(8), 1413-1424.

   3
