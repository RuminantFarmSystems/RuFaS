### __Water dynamics__

The `WaterDynamics`class handles for each selected field the evapotranspiration 
process by which water, through evaporation and transpiration, becomes atmospheric
water vapor. The main function, `cycle_water()`, returns the updated 
**cumulative evapotranspiration** and **water deficiency** factor at harvest/cut time.

**Cumulative evapotranspiration** represents the total millimeters of 
evapotranspired water at the end of the growing season (or at defined 
harvest/cut time): 

```math
  $$ cep = 
   ce+ct     
$$
```
where *cep* is `cumulative_evapotranspiration`, *ce* is `cumulative_evaporation`, the sum of the daily values of water 
evaporated at the end of the growing season, and *ct* is `cumulative_transpiration`, the sum of the daily values of water transpired
at the end of the growing season.

**Water deficiency** is a factor that represents the relationship between 
cumulative and potential evapotranspiration during the growing season. It is 
used to incorporate the effect of water deficit in the 
**potential harvest index**. The factor is calculated at harvest/cut time 
using the following equation: 

```math
  $$ wd = 
  \begin{cases}
     100\times \frac{cep}{pcep}         & \text{if } pcep \not= 0 \\
     
     0                          & \text{otherwise}
  \end{cases}
$$
```
where *wd* is `water_deficiency`, *cep* is `cumulative_evapotranspiration`, 
and *pcep* is `potential_cumulative_evapotranspiration`, the total millimeters 
of evapotranspired water in the growing season from a large area 
uniformly covered with growing vegetation with access to unlimited water supply. 

---
**References**: this module is based upon the "Potential Evapotranspiration", 
"Actual Evapotranspiration" and "Actual yield" sections of the [SWAT][1] model
(2:2.1; 2:2.2; 5:3.3).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf


