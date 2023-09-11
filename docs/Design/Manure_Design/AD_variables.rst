AD Variables
============

| %Climate default data values
| dsmclimate.latitude % To get the climate data file
| dsmclimate.longitude % To get the climate data file
| dsmclimate.temperature % daily TMY air temperature (C)
| dsmclimate.solarRad % daily TMY solar Radiation (W/m2)
| dsmclimate.windSpeed % daily average windspeed (m/s)
| % Digester Default Values
| dsminfluent.dryCows % Number of dry cows
| dsminfluent.replacementCows % Number of replacement cows
| dsminfluent.calves % Number of calves
| dsminfluent.massManureTotal % Total mass of manure (kg/day)
| dsminfluent.volumeManureTotal % Total volume of manure (m3/day)
| dsminfluent.volumeExtraWaterTotal % Total extra volume of water added
  to digester (m3/day) dsminfluent.totalInfluentVolume % Total influent
  volume (m3/day)
| dsminfluent.massTotalVS % Total mass of Volatile Solids (kg/day)
| dsminfluent.specificMethaneYield % Specific Methane Yield
| dsminfluent.manureBiogasProduction % Biogas production (m3/day)
| dsminfluent.tempEstimated % Estimated temperature of the incoming
  influent (C) dsminfluent.tempOffset % if you use an offset for the
  temperature of the influent (C) dsminfluent.tempMin % Minimum manure
  temperature if used (C)

   % Codigestion Default Values

   % Equipment Default Data

   dsmdigester.generatorCapacity %The output capacity of the engine
   generator (kW) dsmdigester.generatorFeedRate %The biogas feed rate to
   the generator (m3/min)

| dsmdigester.generatorConversionEfficiency % The engine generator
  conversion efficiency % dsmdigester.overallGenThermalEfficiency % The
  overall thermal efficiency of conversion
  dsmdigester.heatExchangeEfficiency % the recovery efficiency of the
  generator heat recovery, (%)
| dsmdigester.generatorTimeOnline % The generator time online (hrs/day)
| dsmdigester.generatorActualOutput % The actual output of the generator
  (kWhr/day) dsmdigester.dailyCapacityFactorGenerator % The capacity
  factor of the generator
| dsmdigester.boilerCapacity % The Generator capacity (kW)
| dsmdigester.boilerFeedRate % Generator feed rate (m3/min)
| dsmdigester.boilerConversionEfficiency % Boiler conversion efficiency
  (%)
| dsmdigester.boilerTimeOnline % Time the boiler is operated (hr/day)
| dsmdigester.boilerActualOutput % Output of the boiler (kWhr/day)
| dsmdigester.dailyCapacityFactorBoiler %The capacity factor of the
  boiler

   dsmdigester.baseParasiticHeat % The base parasitic heat used by
   digester (J/day) dsmdigester.variableParasiticHeat % The variable
   parasitic heat used by the digester (J/day)
   dsmdigester.baseParasiticPowerByMonth %The base (constant) power used
   by the digester dsmdigester.variableParasiticPowerMethod %The
   variable power used by the digester

   %Structure Default Data

   dsmdigester.length % Digester dimension if rectangular (m)
   dsmdigester.width % Digester dimension if rectangular (m)
   dsmdigester.height % Digester dimension if rectangular (m)
   dsmdigester.wall1HeightAboveGround % height of wall above ground (m)
   dsmdigester.wall2HeightAboveGround % height of wall above ground (m)
   dsmdigester.wall3HeightAboveGround % height of wall above ground (m)
   dsmdigester.wall4HeightAboveGround % height of wall above ground (m)
   dsmdigester.recFreeboard % freeboard of digester (m)

   dsmdigester.rectangularFlatTop % Whether digester has a flat top or
   not dsmdigester.rectDomeHeight % height of dome if not flat top (m)

   | dsmdigester.diameter % Digester dimension if circular (m)
     dsmdigester.circHeight % Digester dimension if circular (m)
     dsmdigester.circWallHeightAboveGround % height of wall above ground
     (m) dsmdigester.circFreeboard % freeboard of digester (m)
   | dsmdigester.circularFlatTop % Whether digester has a flat top or
     not dsmdigester.circDomeHeight % height of dome if not flat top (m)

   | dsmdigester.wall1AboveRValue % R value of wall insulation above
     ground level dsmdigester.wall2AboveRValue % R value of wall
     insulation above ground level dsmdigester.wall3AboveRValue % R
     value of wall insulation above ground level
     dsmdigester.wall4AboveRValue % R value of wall insulation above
     ground level dsmdigester.wall1BelowRValue % R value of wall
     insulation below ground level dsmdigester.wall2BelowRValue % R
     value of wall insulation below ground level
     dsmdigester.wall3BelowRValue % R value of wall insulation below
     ground level dsmdigester.wall4BelowRValue % R value of wall
     insulation below ground level dsmdigester.baseRValue % R value of
     base insulation below ground level dsmdigester.coverRValue % R
     value of cover
   | dsmdigester.wallCircAboveRValue % R value of wall insulation above
     ground level dsmdigester.wallCircBelowRValue % R value of wall
     insulation below ground level dsmdigester.baseCircRValue % R value
     of base insulation below ground level dsmdigester.coverCircRValue %
     R value of cover

   | dsmdigester.ksoilType % type of soil (used to estimate other
     parameters) dsmdigester.ksoilSat % water saturation of the soil
     around the digester (%) dsmdigester.ksoilValue % Thermal
     conductivity of the soil
   | dsmdigester.alphaSoilValue % Thermal diffusivity of the soil

   | % Operation Default Data
   | dsmdigester.targetTemperature % Default temperature of digester
     operation (C) dsmdigester.digesterType % Default to plug flow type
     of digester
