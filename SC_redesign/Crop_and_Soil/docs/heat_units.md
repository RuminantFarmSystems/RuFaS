### __Heat units__

**Heat units** are calculated on a daily basis by the `HeatUnits`class.
Each crop has its own temperature range for growth (i.e., minimum, optimum, and maximum) and`
HeatUnits` holds for each particular crop all the methods that determine the **absorption** 
and **accumulation** of heat units. 

The main function, `absorb_heat_units()`, updates the **new heat units** absorbed on a given 
day and its accumulation through the growing season.

RuFaS provides two alternatives for calculating **new heat units**:
1. **Main method**: the average air temperature is used as an input, and every degree above 
crop's minimum temperature for growth is accumulated as heat units. With this method, heat 
units accumulated are always equal to the average air temperature (when above the minimum 
threshold). 

Using this method, **new heat units** represents the number of heat units accumulated on a 
given day, where minimum temperature is dependant on the selected crop, using the equation:

```math
  $$ hu = 
  max(TAir - TminCrop, 0)     
$$
```
where *hu* is `heat_units`, *TAir* is `air_temperature`, the mean air temperature for a given day, and 
*TminCrop* is `minimum_growth_temperature`, base or minimum temperature for the crop to growth.

2. **Alternative method**: `heat_unit_temperature` is used instead of `air_temperature`. 
Heat units accumulated are defined using the `heat_unit_temperature` resulting from the 
comparison between minimum and maximum daily temperatures of crop and air:

**Minimum heat unit temperature** calculates the minimum heat unit temperature on a given
day using:
```math
  $$ Tmin = 
  max(TminAir, TminCrop)     
$$
```
where $T_{\text{min}}$ is `minimum_heat_unit_temperature`, T_{\text{air, min}} is `minimum_air_temperature`, the minimum temperature on 
a given day, and T_{\text{crop, min}} is `minimum_growth_temperature`, base or minimum temperature or the crop to growth.


**Maximum heat unit temperature** calculates the maximum heat unit temperature on a given
day using:

```math
  $$ Tmax = 
  min(TmaxAir, TmaxCrop)     
$$
```
where *Tmax* is `maximum_heat_unit_temperature`, *TmaxAir* is `maximum_air_temperature`, the maximum temperature 
on a given day, and *TmaxCrop* is `maximum_growth_temperature`, base or minimum temperature or the crop to growth.

Finally, **heat unit temperature**, which represents the temperature at which heat units 
are accumulated on a given day when considering both crop and air thresholds, is calculated as follows:

```math
  $$ hut = 
     \frac{Tmin+Tmax}{2}  
$$
```
where *hut* is `heat_unit_temperature`, *Tmax* is `maximum_heat_unit_temperature`and *Tmin* is 
`minimum_heat_unit_temperature`

Using this alternative method, **new heat units** is calculated using the equation:

```math
  $$ hu = 
  max(hut - TminCrop, 0)     
$$
```
where *hu* is `heat_units`, *hut* is `heat_unit_temperature`, and 
*TminCrop* is `minimum_growth_temperature`, base or minimum temperature for the crop to growth.


For both methods of heat unit accumulation, after calculation newly absorbed heat units are 
added to the accumulated heat units every day. 

---
**References**: this module is based upon the "Heat units" section of the [SWAT][1] model
(5:1.1).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf