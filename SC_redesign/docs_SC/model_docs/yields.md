### __Crop yields__

Crop yields in RuFaS are calculated by the `Yields` class. `Yields` contains the methods that determine the amount and composition of harvestable crop production. 

Its main method `obtain_yields()` executes all routines to determine crop production at the time of harvest. As such, this method is only called once throughout a 
crop's growing season. This is typically done at cut/harvest time.

Crop yield is a function of the **harvest index** parameter. The **harvest index** is the fraction of the above-ground plant dry biomass that is harvestable economic 
yield. For the majority of crops, the harvest index will be between 0.0 and 1.0. However, plants whose roots are harvested may have a harvest index greater than 1.0. 

The **harvest index** can be determined internally, where first, the **potential harvest index** method calculates the potential harvest index for a crop on a given 
day: 

$$HI_{\text{pot}} = \frac {HI_{\text{opt}}\times h_{\text{perc}}}{h_{\text{perc}} + exp(11.1 - 10\times h)}
$$

$$ h_{\text{perc}} = 100\times h $$

where $HI_{\text{pot}}$ is the potential harvest index for a given day (`potential_harvest_index`), $HI_{\text{opt}}$ is the species-specific potential harvest index 
for the plant at maturity under ideal growing conditions (`optimal_harvest_index`), $h$ is the fraction of potential heat units accumulated by the plant on a given 
day (`heat_fraction`), and $h_{\text{perc}}$ is $h$ expressed as a percentage (`heat_percent`).

Then, **adjust harvest index** determines the crop **harvest index** by adjusting the **potential harvest index** for water deficiency:

$$HI_{\text{act}} = (HI_{\text{pot}} - HI_{\text{min}})\times \frac {W_{\text{def}}}{W_{\text{def}} + exp(6.13 - 0.883\times W_{\text{def}})} + HI_{\text{min}}
$$

where $HI_{\text{act}}$ is the actual harvest index for a given day (`harvest_index`), $HI_{\text{pot}}$ is the potential harvest index for a given day  
(`potential_harvest_index`), $HI_{\text{min}}$ is the minimum harvest index allowed for the plant under drought conditions (`min_harvest_index`), and 
$W_{\text{def}}$ is the water deficiency factor (`water_deficiency`).

Alternatively, the user can provide a **target harvest index** for the crop (`user_harvest_index`). When that occurs, the provided value is used in place of the **harvest index** (`harvest_index`) calculated with the previous method.  

Once crops reach maturity (`heat_fraction` $\geq 1.0$), the **above-ground biomass** is adjusted by the water losses due to the start of the dry-down process. The new above-ground biomass value is calculated using the pre-dry-down above-ground biomass and the dry-down fraction:


$$ Biom_{\text{ag, dry}} = Biom_{\text{ag}}-(Biom_{\text{ag}}\times d)
$$

where $Biom_{\text{ag, dry}}$ is the above ground biomass after dry-down (`above_ground_biomass`), $Biom_{\text{ag}}$ is the above ground biomass 
(`above_ground_biomass`), and $d$ is the proportion of plant biomass that is lost to dry-down [0, 1] (`dry_down_fraction`)

**Crop yield** represents the biomass of the yield product and its calculation varies according to: 
   * if the **harvest index** is less than or equal to 1, yield biomass is calculated as a proportion of the above-ground biomass using the **harvest index** value.
   * if the **harvest index** is greater than 1, it means that both above- and below-ground biomass are part of the product, and yield is calculated as a proportion 
     of the total biomass using the **harvest index** value.

$$ Y_{\text{tot}} = 
\begin{cases}
    Biom_{\text{ag}}\times HI_{\text{act}}         & \text{if } HI_{\text{act}} \le 1 \\ 
    Biom_{\text{tot}}\times HI_{\text{act}}        & \text{if } HI_{\text{act}} > 1 \\
\end{cases} 
$$

where $Y_{\text{tot}}$ is the total amount of the desired crop product (`crop_yield`), $Biom_{\text{ag}}$ is the above ground biomass (`above_ground_biomass`), 
$Biom_{\text{tot}}$ is the total plant biomass on a given day (`biomass`), and $HI_{\text{act}}$ is the actual harvest index on the day of harvest 
(`harvest_index`).

After the **crop yield** is calculated, it is partitioned into the portion that will be extracted from the field, **yield collected**, and the portion that will 
remain in the field, **yield residue**. This partitioning is determined by the **harvest efficiency**: the proportion of the yield that will be extracted from the 
field [0, 1].

The **extracted yield** method calculates the amount of **crop yield** that will be removed from the field during harvest:

$$Y_{\text{crop}} = 
    Y_{\text{tot}}\times H_{\text{eff}} 
$$

where $Y_{\text{crop}}$ is the amount of the desired crop product removed from the field (`yield_collected`), $Y_{\text{tot}}$ is the total amount of the 
desired crop product (`crop_yield`), and $H_{\text{eff}}$ is the harvest efficiency [0, 1] (`harvest_efficiency`).

The unharvested yield that remains in the field is calculated through the **unextracted yield** method with the following equation:

$$ Y_{\text{res}} = 
    Y_{\text{tot}}\times (1-H_{\text{eff}}) 
$$

where $Y_{\text{res}}$ is the unharvested yield (`yield_residue`), $Y_{\text{tot}}$ is the total amount of the desired crop product (`crop_yield`), and $H_{\text{eff}}$ is the harvest efficiency [0, 1] (`harvest_efficiency`).

Finally, the amount of nitrogen and phosphorus removed in the yield product is calculated through the **collected nitrogen** and **collected phosphorus** methods, 
respectively. This is done by multiplying the **yield collected** by the optimal nutrient fraction from the crop database. Alternatively, when the **harvest index** 
is provided by the user, instead of using the nitrogen and phosphorus optimal fractions, these values are calculated by multiplying the **yield collected** by the 
crop-specific expected nutrient fraction in yield:

For nitrogen: 

$$ Y_{\text{N}} = 
\begin{cases}
    Y_{\text{crop}} \times N_{\text{opt}}         & \text{if } HI_{\text{pot}}\text { is calculated} \\ 
    Y_{\text{crop}} \times N_{\text{exp}}         & \text{if } HI_{\text{pot}}\text { is provided}  
\end{cases} 
$$

where $Y_{\text{N}}$ is the amount of nitrogen removed in the yield (`collected_nitrogen`), $Y_{\text{crop, col}}$ is the amount of the desired crop product removed 
from the field (`yield_collected`), $Y_{\text{crop}}$ is the total amount of the desired crop product (`crop_yield`), $N_{\text{opt}}$ is the fraction of
nitrogen in the yield (`optimal_nitrogen_fraction`), and $N_{\text{exp}}$ is the crop-specific expected fraction of nitrogen in yield (`yield_nitrogen_fraction`)

And for phosphorus:

$$ 
Y_{\text{P}} = 
\begin{cases}
   Y_{\text{crop}} \times P_{\text{opt}}         & \text{if } HI_{\text{pot}}\text { is calculated} \\ 
   Y_{\text{crop}} \times P_{\text{exp}}         & \text{if } HI_{\text{pot}}\text { is provided}  
\end{cases} 
$$

where $Y_{\text{P}}$ is the amount of phosphorus removed in the yield (`collected_phosphorus`), $Y_{\text{crop}}$ is the amount of the desired crop product removed 
from the field (`yield_collected`), $Y_{\text{crop}}$ is the total amount of the desired crop product (`crop_yield`), $P_{\text{opt}}$ is the fraction of phosphorus 
in the yield (`optimal_phosphorus_fraction`), and $P_{\text{exp}}$ is the crop-specific expected fraction of phosphorus in yield (`yield_phosphorus_fraction`)

---
**References**: this module is based upon the "Crop Yield" section of the [SWAT][1] model (5:2.4).

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf
