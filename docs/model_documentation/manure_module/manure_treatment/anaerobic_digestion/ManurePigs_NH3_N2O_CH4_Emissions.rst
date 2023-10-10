Manure Pigs NH3 N2O CH4 Emissions
================================

**Manure Module: Calculate Ammonia (NH3), Nitrous Oxide (N2O) and Methane (CH4) Emissions by Animal Housing**

  **Calculate Ammonia (NH3), Nitrous Oxide (N2O) and Methane (CH4) Emissions by pigs.**

   -  Inputs (All inputs come from the weather file, the Animal Module).

      #. TAN = Ammoniacal N concentration (mg/kg)
      #. SurfaceArea = m\ :sup:`2`
      #. StorageTime = days
      #. N_Initial = kg/kg
      #. VF_BeddingMaterialType = kg/pig
      #. VF_LitterSurface = m\ :sup:`2`/pig
      #. VF_Maintenance =
      #. VF_BeddingmaterialAmount = kg/pig
      #. VF_Mixing =
      #. B0 = Maximum methane producing capacity (m\ :sup:`3`/kg )
      #. VS = Total volatile solids (kg)
      #. MCF = methane conversion factor
      #. EmissionFactor = (kg)
      #. EmissionFactor = (kg)
      #. VF_ManureType = (kg)
      #. VF_TurningNumber = (kg)
      #. VF_OutsideTemperature = (\ :sup:`o`\C )
      #. VF_CompostingDuration = (months)
      #. T\ :sub:`R` = Read Temperature (K-Kelvin)
      

   -  Outputs

      #. NH\ :sub:`3` _Outdoor = Ammonia from the outdoor slurry tank, g NH\ :sub:`3` /m\ :sup:`2` per day
      #. N_LossesBuilding = total N losses
      #. NH\ :sub:`3`\_EmittedBuilding = Ammonia from the building
      #. N\ :sub:`2`\O_EmittedBuilding = Nitrous Oxide from building
      #. CH\ :sub:`4`\_Emitted = Methane CH4 Emissions
      #. X_EmittedComposting = Emitted Composting


  **Calculate Ammonia from the outdoor slurry tank 1.VF_Temperature**

    - VF_Temperature

      -  Temp_Effluent=0.9614*TR+1.6889           *[M.5.1.1.1]*
      
      -  VF_Temperature= 𝑒\ :sup:`(0.08∗Temp_Effluent)` / 2.612        *[M.5.1.1.2]*


    - VF_NDilution A Correction factor

      -  VF_NDilution=TAN/1.03 *[M.5.1.2]*

    - Ammonia from the outdoor slurry tank

      -  NH\ :sub:`3`\_Outdoor=1.57*VF_Temperature*VF_NDilution*VF_Cover*SurfaceArea*StorageTime
         *[M.5.1.3]*
         
  **Calculate total N losses**

    - N_LossesBuilding=0.64*N_Initial*VF_BeddingMaterialType*VF_LitterSurface*VF_Maintenance*VF_BeddingmaterialAmount*VF_Mixing *[M.5.2.1]*

  **Calculate NH3**

    -  NH\ :sub:`3`\_EmittedBuilding=17/14*0.20*N_Initial*VF_LitterSurface*VF_Maintenance*VF\_
       BeddingmaterialAmount *[M.5.3.1]*
       
  **Calculate N2O**

    - N\ :sub:`2`\O_EmittedBuilding=44/28*0.06*N_Initial*VF_BeddingMaterialType*VF_LitterSurf
      ace*VF_Maintenance*VF_BeddingmaterialAmount*VF_Mixing *[M.5.4.1]*
  
  **Calculate CH4 emissions**

    - CH\ :sub:`4`\_Emitted=VS*B0*MCF *[M.5.5.1]* 
    
  **Solid manure composting**
    - X_EmittedComposting=EmissionFactor*VF_ManureType*VF_TurningNumber*VF_OutsideTemperature*VF_CompostingDuration *[M.5.6.1]*

**References**

  Rigolot, C., Espagnol, S., Robin, P., Hassouna, M., Béline, F.,
  Paillat, J. M., & Dourmad, J. Y. (2010). Modelling of manure
  production by pigs and NH3, N2O and CH4 emissions. Part II: effect
  of animal housing, manure storage and treatment practices. Animal,
  4(8), 1413-1424.