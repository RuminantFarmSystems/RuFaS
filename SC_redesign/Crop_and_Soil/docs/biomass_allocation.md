### __Biomass allocation__

The `BiomassAllocation` class manages the crop biomass accumulation through the photosynthesis process and its partition between above and below ground organs during the growing season.

The central method, `allocate_biomass()`, calls on the **photsynthesize** and **partition biomass** methods to make daily updates on crop biomass allocation.

**Photosynthesize** converts the incoming solar radiation into plant biomass. First, potential plant growth is modeled by simulating **intercept radiation** and 
**maximum biomass growth**. Then, the latter is adjusted by plant stress to calculate the **biomass growth** on a given day and the **biomass** accumulated to date.

**Intercept radiation** represents the amount of daily photosynthetically active radiation intercepted by the leaf area of the crop according to:

```math
  $$ R_{\text{int}} = 0.5\times R_{\text{inc}}\times (1-exp\times (-k_{\text{l}}\times A_{\text{leaf, i}}))
       
$$
```
where $R_{\text{int}}$ is `usable_light`, $R_{\text{inc}}$ is`incoming_solar_radiation`, the total solar radiation available on a given day, $k_{\text{l}}$ is 
`light_extinction`, the light extinction coefficient, and $A_{\text{leaf, i}}$ is `leaf_area_index`, the leaf area index on a given day.

**Maximum biomass growth** calculates the potential or upper-limit to total biomass increase on a given day that results from **intercept radiation** and the crop-specific radiation-use efficiency, which is the amount of dry biomass produced per unit of intercepted solar radiation. It is calculated using the following equation:

```math
  $$ Biom_{\text{max}} = R_{\text{int}}\times Eff_{\text{light}}
       
$$
```
where $Biom_{\text{max}}$ is `biomass_growth_max`, $R_{\text{int}}$ is `usable_light`, and $Eff_{\text{light}}$ is `light_use_efficiency`, the radiation-use efficiency of the crop. 

The **biomass growth** on a given day represents the actual biomass growth once **maximum biomass growth** is adjusted according to the daily crop growth factor:

```math
  $$ Biom_{\text{i}} = Biom_{\text{max}}\times \gamma_{\text{reg}}
       
$$
```
where $Biom_{\text{i}}$ is `biomass_growth` on a given day, $Biom_{\text{max}}$ is `biomass_growth_max`, the maximum biomass growth on a given day, and $\gamma_{\text{reg}}$ is the `growth_factor` of the crop [0.0-1.0].

Then, **biomass**, which represents the total plant biomass on a given day, is calculated based upon the sum of the previously estimated **biomass growth**:

```math
  $$ Biom_{\text{tot}} = \sum_{i=1}^{d} Biom_{\text{i}}
       
$$
```
where $Biom_{\text{tot}}$ is `biomass` and $Biom_{\text{i}}$ is the `biomass_growth` on a given day.

**Partition biomass** divides **biomass** into above ground and below ground portions. The **above ground biomass** is calculated as follows:

```math
  $$ Biom_{\text{ag}} = Biom_{\text{tot}}\times (1-r)
       
$$
```
where $Biom_{\text{ag}}$ is `above_ground_biomass`, $Biom_{\text{tot}}$ is `biomass`, and $r$ is `root_fraction`, the fraction of total biomass 
partitioned to roots on a given day.

Finally, **below ground biomass** represents the biomass partitioned to roots and is calculated according to:

```math
  $$ Biom_{\text{bg}} = Biom_{\text{tot}}\times r
       
$$
```
where $Biom_{\text{bg}}$ is `below_ground_biomass`, $Biom_{\text{tot}}$ is `biomass`, and $r$ is `root_fraction`, the fraction of total biomass 
partitioned to roots on a given day.

---
**References**: this module is based upon the "Biomass Production" and "Crop Yield" sections of the [SWAT][1] model (5:2.1.1, 5:2.4).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf
