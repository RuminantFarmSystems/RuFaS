### __Water dynamics__

The `WaterDynamics`class handles for each selected field the evapotranspiration process by which water, through evaporation and transpiration, becomes atmospheric
water vapor. The main method, `cycle_water()`, comprises the **cumulative evapotranspiration** and **water deficiency** methods:

**Cumulative evapotranspiration** represents the total millimeters of evapotranspired water at the end of the growing season (or at defined harvest/cut time): 

$$ Et_{\text{cum}} =    E_{\text{cum}}+T_{\text{cum}}     
$$

where $Et_{\text{cum}}$ is the total millimeters of evapotranspired water at the end of the growing season (`cumulative_evapotranspiration`), $E_{\text{cum}}$ is the 
sum of the daily values of water evaporated at the end of the growing season (`cumulative_evaporation`), and $T_{\text{cum}}$ is the sum of the daily values of water 
transpired at the end of the growing season (`cumulative_transpiration`).

**Water deficiency** is a factor that represents the relationship between cumulative and potential evapotranspiration during the growing season. It is used to 
incorporate the effect of water deficit in the **potential harvest index**. The factor is calculated at harvest/cut time using the following equations: 

$$ W_{\text{def}} = 
\begin{cases}
    100\times \frac{Et_{\text{cum}}}{Et_{\text{pot,cum}}}         & \text{if } Et_{\text{pot,cum}} \not= 0 \\
    0                                                             & \text{otherwise}
\end{cases}
$$

where $W_{\text{def}}$ is the water deficiency factor (`water_deficiency`), $Et_{\text{cum}}$ is the total millimeters of evapotranspired water at the end of the 
growing season (`cumulative_evapotranspiration`), and $Et_{\text{pot,cum}}$ is the total millimeters of evapotranspired water in the growing season from a large area 
uniformly covered with growing vegetation with access to unlimited water supply (`max_cumulative_evapotranspiration`).

---
**References**: this module is based upon the "Potential Evapotranspiration", "Actual Evapotranspiration" and "Actual yield" sections of the [SWAT][1] model (2:2.1; 
2:2.2; 5:3.3).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf


