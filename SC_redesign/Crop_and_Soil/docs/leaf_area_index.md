### __Leaf area index__

The `LeafAreaIndex`class handles the seasonal changes in canopy height and
leaf area for each crop during the growing season. The **leaf area index**
(*LAI*) is defined as the area of green leaf per unit area of land, having a 
maximum value that, once reached, remains constant until leaf senescence 
becomes the dominant growth process.

The main function, `grow_canopy()`, returns on a daily basis the updated 
**optimal leaf area fraction**, **shape coefficients**, **canopy height**,
**maximum leaf area change** and **senescent leaf area index** to finally 
determine the **leaf area added** every day.

The **optimal leaf area fraction** controls the canopy height and leaf area
until the maximum *LAI* is reached and represents the fraction of the 
plant’s maximum *LAI* corresponding to a given fraction of potential heat 
units. To calculate this fraction on a given day, RuFaS needs to first 
calculate two **shape coefficients** and the **fraction of potential heat 
units** accumulated. Then, the **optimal leaf area fraction** is calculated 
as follows:

```math
  $$ fr_{\text{LAI, opt}} = \frac{h}{h+exp(l_{\text{1}}-l_{\text{2}}\times h)} 
       
$$
```
where $fr_{\text{LAI, opt}}$ is the `optimal_leaf_area_fraction`, $l_{\text{1}}$ 
is `first_shape`, $l_{\text{2}}$ is `second_shape` and $h$ is `heat_fraction`, 
the fraction of potential heat units accumulated for the plant on a given day.

**Canopy height** represents the canopy height on a given day, in meters, 
and is calculated using the following equation:

```math
  $$ h_{\text{c}} = 
  h_{\text{c,max}}\times \sqrt{fr_{\text{LAI,opt}}}     
$$
```

where $h_{\text{c}}$ is `canopy_height`, $h_{\text{c,max}}$ is `max_canopy_height`, 
and $fr_{\text{LAI,opt}}$ is `optimal_leaf_area_fraction`. Once $h_{\text{c,max}}$ 
is reached, $h_{\text{c}}$ remains constant. 

The **maximum leaf area change** calculates the maximum or potential leaf 
area added during the day using the following equation:

```math
  $$ LAI_{\text{pot}} = (fr_{\text{LAI, opt}}-fr_{\text{LAI, opt i-1}}) \times LAI_{\text{max}} \times (1-exp(5\times (LAI_{\text{i-1}}-LAI_{\text{max}})))
       
$$
```

where $LAI_{\text{pot}}$ is the `maximum_leaf_area_change` on a given day, $fr_{\text{LA, opt}}$  
is the `optimal_leaf_area_fraction` on a given day, $fr_{\text{LA, opt i-1}}$ 
is `previous_optimal_leaf_area_fraction`, the optimal leaf area fraction of the previous day, $LAI_{\text{max}}$ 
is `max_leaf_area_index`, the maximum leaf area index achievable by the plant, 
and $LAI_{\text{i-1}}$ is `previous_leaf_area`, the leaf area index on the previous day.

When **senescence** starts, *LAI* is calculated as follows: 

```math
  $$ LAI_{\text{i}} = LAI_{\text{max}} \times \frac {(1-h)}{(1-h_{\text{sen}})}
$$
```
where $LAI_{\text{i}}$ is the `leaf_area_index` on a given day, $LAI_{\text{max}}$ is `max_leaf_area_index`,
the maximum leaf area index achievable by the plant, $h$ is `heat_fraction`,
the fraction of potential heat units accumulated for the plant on a given 
day and $h_{\text{sen}}$ is `senescent_heat_fraction`, the fraction of 
potential heat units at which senescence begins.

The **actual leaf area added** on a given day is based upon the potential 
leaf area added on a given day and an adjustment for plant stress, according
to:

```math
  $$ LAI_{\text{act, i}} = 
  LAI_{\text{pot}} \times \sqrt{\gamma_\text{reg}}     
$$
```
where $LAI_{\text{act, i}}$ is the `actual_leaf_area_added` on a given day, 
$LAI_{\text{pot}}$ is `maximum_leaf_area_change`, the maximum or potential leaf area added on a given 
the day, and $\gamma_\text{reg}$ is the plant `growth_factor` [0.0-1.0].

Finally, the **leaf area index** on a given day is calculated as:

```math
  $$ LAI_{\text{i}} = LAI_{\text{act, i}} + LAI_{\text{i-1}}
$$
```
where $LAI_{\text{i}}$ is the `leaf_area_index` on a given day, $LAI_{\text{act, i}}$ 
is the `actual_leaf_area_added` on day i and $LAI_{\text{i-1}}$ is 
`previous_leaf_area`, the leaf area index of the previous day. 

---
**References**: this module is based upon the "Canopy Cover and Crop" and 
"Actual Growth" sections of the [SWAT][1] model (5:2.1.2, 5:3.2).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf


