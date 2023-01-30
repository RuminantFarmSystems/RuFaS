## Feed Management and Inventory Model

The **Feed Management and Inventory Model** is currently managed by the `Feed` class 
and its subclass, `Storage`.

The **Feed** class takes in data from the input JSON file and stores information 
for the feeds managed by the farm and the methods for storage. It contains the 
**Storage** subclass which specifies a single feed storage receptacle.

Upon harvest, farm grown feed is grouped by crop type, harvest date, and quality, 
then assigned to an available storage receptacle sequentially.

Quality assessment for farm grown feeds is currently based on the fr_PHU 
(fraction of potential heat units) accumulated by the crop at harvest and 
occurs in the **Yields** class. Forage quality of “purchased” feeds is a database 
entry queried in the **Feed** class.

Nutrients are lost at various stages from harvest to feedout at various rates for 
different feed-storage combinations. Feed storage loss is currently an empirical 
model of those various reductions based on the work of Kevin Panke-Buisse, a 
research microbiologist at the USDA DFRC in Madison, WI. After pairing a crop 
to a storage receptacle, the model is calibrated and nutrient losses at each 
stage are calculated and applied sequentially.

## Future enhancements

Develop a **FeedManagement** class that directs the management of the **Feed** class
similar to the **AnimalManagement** and **ManureManagement** classes.

The **FeedManagement** class will have 4 primary jobs:
1. Keep track of the different **Storage** objects and how much of each type of feed is in all of them
2. Direct newly-harvested feed from the **Crop and Soil** module to a storage object
3. Tell the **Animal Module** how much feed there is
4. Remove feed from the **Storage** objects daily as the **Animal Module** uses it to feed to cows

