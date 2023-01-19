### __Leaf area index__

The `LeafAreaIndex`class handles the seasonal changes in canopy height and leaf area for each crop during the growing season. The **leaf area index** (*LAI*) is 
defined as the area of green leaf per unit area of land, having a maximum value that, once reached, remains constant until leaf senescence becomes the dominant 
growth process.

The main function, `grow_canopy()`, returns on a daily basis the updated **optimal leaf area fraction**, **shape coefficients**, **canopy height**, **maximum leaf 
area change** and **senescent leaf area index** to finally determine the **leaf area added** every day.

The **optimal leaf area fraction** controls the canopy height and leaf area until the maximum *LAI* is reached and represents the fraction of the plant’s maximum 
*LAI* corresponding to a given fraction of potential heat units. To calculate this fraction on a given day, RuFaS needs to first calculate two **shape 
coefficients** and the **fraction of potential heat units** accumulated. Then, the **optimal leaf area fraction** is calculated as follows:

```math
  $$ A_{\text{leaf, opt}} = \frac{h}{h+exp(l_{\text{1}}-l_{\text{2}}\times h)}
$$
```
where $A_{\text{leaf, opt}}$ is the `optimal_leaf_area_fraction`, $l_{\text{1}}$ is the first of two shape parameters (`_lai_shapes`), $l_{\text{2}}$ is the second 
shape parameter, and $h$ is `heat_fraction`, the fraction of potential heat units accumulated for the plant on a given day.

**Canopy height** represents the canopy height on a given day, in meters, and is calculated using the following equation:

```math
  $$ h_{\text{c}} = 
  h_{\text{c,max}}\times \sqrt{A_{\text{leaf,opt}}}     
$$
```

where $h_{\text{c}}$ is `canopy_height`, $h_{\text{c,max}}$ is `max_canopy_height`, and $A_{\text{leaf,opt}}$ is `optimal_leaf_area_fraction`. Once 
$h_{\text{c,max}}$ is reached, $h_{\text{c}}$ remains constant. 

The **maximum leaf area change** calculates the maximum or potential leaf area added during the day using the following equation:

```math
  $$ A_{\text{leaf,pot}} = (A_{\text{leaf, opt}}-A_{\text{leaf, opt i-1}}) \times A_{\text{leaf, max}} \times (1-exp(5\times (A_{\text{leaf, i-1}}-A_{\text{leaf, max}})))
$$
```

where $A_{\text{leaf, pot}}$ is the `maximum_leaf_area_change` on a given day, $A_{\text{leaf, opt}}$ is the `optimal_leaf_area_fraction` on a given day, 
$A_{\text{leaf, opt i-1}}$ is `previous_optimal_leaf_area_fraction`, the optimal leaf area fraction of the previous day, $A_{\text{leaf, max}}$ is 
`max_leaf_area_index`, the maximum leaf area index achievable by the plant, and $A_{\text{leaf, i-1}}$ is `previous_leaf_area`, the leaf area index of the previous 
day.

When **senescence** starts, *LAI* is calculated as follows: 

```math
  $$ A_{\text{leaf, i}} = A_{\text{leaf, max}} \times \frac {(1-h)}{(1-h_{\text{sen}})}
$$
```
where $A_{\text{leaf, i}}$ is the `leaf_area_index` on a given day, $A_{\text{leaf, max}}$ is `max_leaf_area_index`, the maximum leaf area index achievable by the 
plant, $h$ is `heat_fraction`, the fraction of potential heat units accumulated for the plant on a given day and $h_{\text{sen}}$ is `senescent_heat_fraction`, the 
fraction of potential heat units at which senescence begins.

The **actual leaf area added** on a given day is based upon the potential leaf area added on a given day and an adjustment for plant stress, according to:

```math
  $$ A_{\text{leaf, act, i}} = 
  A_{\text{leaf, pot}} \times \sqrt{\gamma_\text{reg}}      
$$
```
where $A_{\text{leaf, act, i}}$ is the `actual_leaf_area_added` on a given day, $A_{\text{leaf, pot}}$ is `maximum_leaf_area_change`, the maximum or potential leaf 
area added on a given the day, and $\gamma_\text{reg}$ is the plant `growth_factor` [0.0-1.0].

Finally, the **leaf area index** on a given day is calculated as:

```math
  $$ A_{\text{leaf, i}} = A_{\text{leaf, act, i}} + A_{\text{leaf, i-1}}
$$
```
where $A_{\text{leaf, i}}$ is the `leaf_area_index` on a given day, $A_{\text{leaf, act, i}}$ is the `actual_leaf_area_added` on day i and $A_{\text{leaf, i-1}}$ is 
`previous_leaf_area`, the leaf area index of the previous day. 

---
**References**: this module is based upon the "Canopy Cover and Crop" and "Actual Growth" sections of the [SWAT][1] model (5:2.1.2, 5:3.2).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf


