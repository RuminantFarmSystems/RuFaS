### __Heat units__ 

The `HeatUnits`class manages the accumulation of heat units for a crop on a daily basis. Crops have their own temperature range for growth (*i.e.*, minimum, optimum, and maximum) and `HeatUnits` holds, for each particular crop, all the methods that determine the absorption and accumulation of heat units. 


Its central method, `absorb_heat_units()`, executes all the methods that allow updating the **new heat units** absorbed on a given day and its accumulation through the growing season. 

The **accumulate heat units** method provides two alternatives for calculating **new heat units** on a given day:

1. **Main method**: the mean air temperature (`mean_air_temperature`) is used as an input, and every degree above crop's minimum temperature for growth is accumulated as heat units. With  this method, where minimum temperature is dependant on the selected crop, heat units accumulated are always equal to the average air temperature (when above the minimum threshold). 

2. **Alternative method**: new heat units are defined using the **heat unit temperature** (`heat_unit_temperature`) instead of the mean air temperature (`mean_air_temperature`). The selection of this method involves the daily calculation of **minimum heat unit temperature** and **maximum heat unit temperature** to determine the **heat unit temperature** on a given day:

**Minimum heat unit temperature** results from the comparison between the minimum air temperature and the crop's minimum temperature for growth:

$$ T_{\text{hu, min}} = 
  max(T_{\text{air, min}}, T_{\text{crop, min}})     
$$

where $T_{\text{hu, min}}$ is the minimum heat unit temperature on a given day (`minimum_heat_unit_temperature`), $T_{\text{air, min}}$ is the minimum air temperature on a given day (`min_air_temperature`), and $T_{\text{crop, min}}$ is the base or minimum temperature for the crop to grow (`minimum_temperature`).

**Maximum heat unit temperature** results from the comparison between the maximum air temperature and the crop's maximum temperature for growth:

$$ T_{\text{hu, max}} = 
  min(T_{\text{air, max}}, T_{\text{crop, max}})     
$$

where $T_{\text{hu, max}}$ is the maximum heat unit temperature on a given day (`maximum_heat_unit_temperature`), $T_{\text{air, max}}$ is the maximum air temperature on a given day (`max_air_temperature`), and $T_{\text{crop, max}}$ is the maximum temperature for the crop to grow (`maximum_temperature`).

Finally, **heat unit temperature**, which represents the temperature at which heat units are accumulated on a given day when considering both crop and air 
thresholds, is calculated as follows:

$$ T_{\text{hu}} = 
     \frac{T_{\text{hu, min}}+T_{\text{hu, max}}}{2}  
$$

where $T_{\text{hu}}$ is the heat unit temperature (`heat_unit_temperature`), $T_{\text{hu, min}}$ is the minimum heat unit temperature on a given day  
(`minimum_heat_unit_temperature`), and $T_{\text{hu, max}}$ is the maximum heat unit temperature on a given day (`maximum_heat_unit_temperature`).

Once the accumulation method for heat units is defined, the **assign new heat unis** method calculates the new heat units on a given day:

$$ hu = 
\begin{cases}
    max(T_{\text{air}} - T_{\text{crop, min}}, 0)                                        & \text{Main method } \\ 
    max(T_{\text{hu}} - T_{\text{crop, min}}, 0)                                                   & \text{Alternative method}
\end{cases} 
$$

where $hu$ are the new heat units accumulated on a given day (`heat_units`), $T_{\text{air}}$ is the mean air temperature on a given day (`mean_air_temperature`), $T_{\text{hu}}$ is the heat unit temperature (`heat_unit_temperature`), and $T_{\text{crop, min}}$ is the base or minimum temperature for the crop to grow 
(`minimum_temperature`).

Then, the newly acquired heat units are added to the accumulated heat units to date through the the **add heat units** method:

$$ hu_{\text{ac, i}} = 
     hu + hu_{\text{ac, i-1}}
$$

where $hu_{\text{ac, i}}$ are the total heat units accumulated on a given day (`accumulated_heat_units`), $hu$ are the new heat units accumulated on a given day (`heat_units`), and $hu_{\text{ac, i-1}}$ are the total heat units accumulated on the previous day (`accumulated_heat_units`). 


---
**References**: this module is based upon the "Heat Units" section of the [SWAT][1] model (5:1.1).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf
