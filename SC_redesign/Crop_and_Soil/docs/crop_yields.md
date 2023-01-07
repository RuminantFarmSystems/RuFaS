## Summary

The `Yields` class contains the methods that determine the amount and composition of harvestable crop production. 
Its main method function `obtain_yields()` executes all routines to determine production at the time of harvest. As 
such, this function is only called once throughout a crop's growing season. This is typically done at cut/harvest time.

## Reference

The `Yields` class is primarily an implementation of the methods described in 
[SWAT](https://swat.tamu.edu/media/99192/swat2009-theory.pdf) section 5:2.4, with some minor modifications.

## Details

This class utilizes and updates a number of attribute variables in the course of its routines. Details about these 
attributes and the methods of the class are given in more detail in the following subsections.

#### Input variables

The `Yields` class uses the following attributes, which are input variables.

* `optimal_harvest_index`: potential harvest index for the plant at maturity under ideal growing conditions (unitless)
* `min_harvest_index`: harvest index for the plant in drought conditions; represents minimum harvest index allowed for 
the plant (unitless)
* `harvest_efficiency`: efficiency of the harvest operation: the proportion of the yield that will be extracted from the 
field [0, 1]
* `yield_nitrogen_fraction`: crop-specific expected fraction of nitrogen in yield
* `yield_phosphorus_fraction`: crop-specific expected fraction of phosphorus in yield
* `heat_fraction`: fraction of a plant's potential heat units accumulated to date (unitless)
* `water_deficiency`: water deficiency factor for the plant (unitless)
* `above_ground_biomass`: plant biomass excluding roots; shoot biomass (kg/ha). This variable is updated by 
`obtain_yields()`
* `biomass`: plant biomass (kg/ha)
* `dry_down_fraction`: proportion of plant biomass that is lost to dry-down [0, 1]
* `nitrogen`: nitrogen stored in plant biomass (kg/ha)
* `phosphorus`: phosphorus stored in plant biomass (kg/ha)
* `optimal_nitrogen_fraction`: optimal fraction of nitrogen in the plant biomass for current growth stage (unitless)
* `optimal_phosphorus_fraction`: optimal fraction of phosphorus in the plant biomass for current growth stage (unitless)
* `user_harvest_index`: (**Optional**) a user-specified harvest index (unitless); if given, 'harvest-index-override' is 
triggered

#### Calculated variables

The `Yields` class calculates the following attributes with its methods. Unless otherwise specified, these attributes
are updated by `obtain_yields()`.

* `potential_harvest_index`: potential harvest index for a given day. 
* `harvest_index`: harvest index for a given day; fraction of above-ground plant biomass that is harvestable 
economic yield (unitless)
* `crop_yield`: total amount (kg/ha) of the desired crop product
* `yield_collected`: amount (kg/ha) of the desired crop product to be removed from the field
* `yield_residue`: amount of residue created; unharvested yield (kg/ha)
* `collected_nitrogen`: nitrogen contained in the harvested yield (kg/ha)
* `collected_phosphorus`: phosphorus contained in the harvested yield (kg/ha)

#### Properties

`Yields` has the following property attributes:

* `is_mature`: has the crop reached maturity (true/false)?
* `has_given_harvest_index`: has the user provided the `user_harvest_index` attribute (true/false)? If `True`, the 'harvest
index override' is triggered. 

#### Routine/algorithm

The `obtain_yields()` method follows the following procedure

1. determine the `harvest_index`. 
   * First, `potential_harvest_index` is calculated from `heat_fraction` and `optimal_harvest_index`, via the 
   `determine_potential_harvest_index()` static function.
   * Then, `harvest_index` is calculated from `potential_harvest_index`, `min_harvest_index`, and `water_deficiency` 
   via the `adjust_harvest_index` static function.
   * Alternatively, if `user_harvest_index` is given, `harvest_index` is directly set to this value 
   (harvest index override)
2. check if the crop has reached maturity (`is_mature`) and, if it has, trigger the dry-down process. The new 
`above_ground_biomass` value is calculated with `adjust_biomass_for_dry_down()` using the pre-dry-down 
`above_ground_biomass` and the `dry_down_fraction`.
3. calculate the biomass of the yield product (`crop_yield`).
   * if the `harvest_index` is less than 1, yield biomass is calculated from the `above_ground_biomass` and the 
   `harvest_index` value via the `determine_yield_from_shoot_biomass()` static method.
   * if `harvest_index` is greater than 1, it means that both above- and below-ground biomass are part of the product.
   yield is calculated with `determine_yield_from_total_biomass()` from `biomass` and `harvest_index`.
4. calculate the amount of yield that will be removed from the field during harvest. This is done with the 
`determine_extracted_yield()` static function from `crop_yield`, and `harvest_efficiency`. 
5. calculate the amount of nitrogen and phosphorus contained in the yield product (`collected_nitrogen`, 
`collected_phosphorus`, respectively)
   * this is done by multiplying the `yield_collected` by `optimal_nitrogen_fraction` or `optimal_phosphorus_fraction`.
   * Alternatively, when the 'harvest index override' has triggered, these values are calculated by multiplying 
   `yield_collected` by the species-specific expected nutrient fraction (`yield_nitrogen_fraction`, 
   `yield_phosphorus_fraction`)
6. calculate the un-harvest yield that will be recycled into the soil as plant residue. This is done with 
the `determine_unextracted_yield()` from `crop_yield` and `harvest_efficiency`. 

<!-- # TODO: 7. calculate above- and below-ground lignin?? -->

<!-- # TODO: 8. calculate crop quality metrics to be used by feed module?? -->
