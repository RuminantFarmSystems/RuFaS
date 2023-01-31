The `GrowthConstraints` class handles the environmental constraints to potential plant growth that a crop
face during the growing season. This module addresses the stresses caused by insufficient 
water, inadequate nutrients (nitrogen and phosphorus) and extreme temperatures, and determines which, if any, 
is limiting plant growth on a given day.  

The main method, `constrain_growth()` calls on the **water stress**, **temperature stress**, **nitrogen 
stress** and **phosphorus stress** methods to provide daily updates on the **plant growth factor**, 
which quantifies the fraction of potential plant growth achieved on a given day. Each environmental stress 
varies from 0, under optimal conditions, to 1, under extreme stress. 

**Water stress** calculates the stress caused by the water soil conditions on a given day by comparing 
actual and potential plant transpiration according to:

```math
  $$ W_{\text{stress}} = 
  \begin{cases}
    1- \frac{W_{\text{uptake}}}{Tr_{\text{max}}}         & \text{if } Tr_{\text{max}} \not= 0 \\
     
    0                                                    & \text{otherwise}
    
  \end{cases}
$$
```
where $W_{\text{stress}}$ is `water_stress`, $W_{\text{uptake}}$ is `water_uptake`, the total water 
taken up by the plant from the soil on a given day, and $Tr_{\text{max}}$ is `max_transpiration`, 
the maximum plant transpiration on a given day. 

**Temperature stress** represents the stress experienced by a plant when the mean air temperature on a 
given day diverges from the optimal temperature for plant growth. It is calculated using the following 
equations:

```math
  $$ T_{\text{stress}} = 
  \begin{cases}
     1- exp\frac{-0.1054\times (T_{\text{crop, opt}} - T_{\text{air}})^{2}}{(T_{\text{air}} - T_{\text{crop, min}})^{2}}                                               & \text{if } T_{\text{crop, min}} < T_{\text{air}} <= T_{\text{crop, opt}} \\
     1- exp\frac{-0.1054\times (T_{\text{crop, opt}} - T_{\text{air}})^{2}}{((2\times T_{\text{crop, opt}} - T_{\text{crop, min}}) - T_{\text{crop, min}})^{2}}        & \text{if } T_{\text{crop, opt}} < T_{\text{air}} <= 2\times T_{\text{crop, opt}} - T_{\text{crop, min}} \\                                                                                                                                                                                                                                                   
     1                                                                                                                                                                 & \text{otherwise}
    
  \end{cases}
$$
```
where $T_{\text{stress}}$ is `temp_stress`, $T_{\text{air}}$ is `temperature`, the mean air
temperature for a given day, $T_{\text{crop, min}}$ is `minimum_temperature`, the base or minimum temperature for the crop 
to grow, and $T_{\text{opt}}$ is `optimal_temperature`, the optimal temperature for the crop to grow. 

**Nitrogen stress** calculates the plant nitrogen stress on a given day by comparing actual and optimal 
plant nitrogen levels and requires the initial estimation of a **stress factor** for nitrogen stress: 

```math
  $$ S_{\text{N}} = 
     200\times (\frac{N_{\text{plant}}}{N_{\text{opt}}} - 0.5)         
    
$$
```

where $S_{\text{N}}$ is `stress_factor`, the stress factor for nitrogen stress, $N_{\text{plant}}$ is 
`nitrogen`, the actual mass of nitrogen stored in plant material on a given day, and $N_{\text{opt}}$ is
`optimal_nitrogen`, the optimal mass of nitrogen stored in plant material for the current growth stage.

Then, **nitrogen stress** is calculated as follows:

```math
  $$ N_{\text{stress}} = 
     1 - \frac{S_{\text{N}}}{S_{\text{N}} + exp(3.535 - 0.02597 \times S_{\text{N}})}          
    
$$
```
where $N_{\text{stress}}$ is `nitrogen_stress`, and $S_{\text{N}}$ is `stress_factor`, the stress factor for 
nitrogen stress. 

**Phosphorus stress** follows the same calculation as **nitrogen stress**, quantifying the plant phosphorus stress
by comparing actual and optimal plant phosphorus levels. First, the stress_factor for phosphorus stress is calculated:

```math
  $$ S_{\text{P}} = 
     200 \times (\frac{S_{\text{plant}}}{S_{\text{opt}}} - 0.5)         
    
$$
```

where $S_{\text{P}}$ is `stress_factor`, the stress factor for phosphorus stress, $P_{\text{plant}}$ is 
`phosphorus`, the actual mass of phosphorus stored in plant material on a given day, and 
$P_{\text{opt}}$ is `optimal_phosphorus`, the optimal mass of phosphorus stored in plant material for 
the current growth stage.

Then, **phosphorus stress** is calculated using the equation:

```math
  $$ P_{\text{stress}} = 
     1 - \frac{S_{\text{P}}}{S_{\text{P}} + exp(3.535 - 0.02597 \times S_{\text{P}})}          
    
$$
```
where $P_{\text{stress}}$ is `phosphorus_stress`, and $S_{\text{P}}$ is `stress_factor`, the stress factor for 
phosphorus stress. 

Finally, the 4 environmental stresses quantified on a given day are used to calculate the **plant growth factor** as 
follows:

```math
  $$ \gamma_{\text{reg}} = 
     1 - max(W_{\text{stress}}, T_{\text{stress}}, N_{\text{stress}}, P_{\text{stress}})        
    
$$
```
where $\gamma_{\text{reg}}$ is `growth_factor`, $W_{\text{stress}}$ is `water_stress`, $T_{\text{stress}}$
is `temp_stress`, $N_{\text{stress}}$ is `nitrogen_stress`, and $P_{\text{stress}}$ is `phosphorus_stress`. 

---
**References**: this module is based upon the "Growth Constraints" section of the [SWAT][1] model (5:3.1).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf


