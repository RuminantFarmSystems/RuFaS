## Feed Management and Inventory Model

The **Feed Management and Inventory Model** is currently managed by the `Feed` class 
and its subclass, `Storage`.

The `Feed` class takes in data from the input JSON file and stores information 
for the feeds managed by the farm and the methods for storage. It contains the 
`Storage` subclass which specifies a single feed storage receptacle.

Upon harvest, farm grown feed is grouped by crop type, harvest date, and quality, 
then assigned to an available storage receptacle sequentially. Quality assessment 
for farm-grown feeds addressed in Future Enhancements section.
Forage quality of purchased feeds is provided by the Feed Library database that is queried in the `Feed` class.

Nutrients are lost at various stages from harvest to feedout at various rates for 
different feed-storage combinations. Feed storage loss is currently an empirical 
model of those reductions based on the work of Kevin Panke-Buisse, a 
research microbiologist at the USDA DFRC in Madison, WI. After pairing a crop 
to a storage receptacle, the model is calibrated and nutrient losses at each 
stage are calculated and applied sequentially.

Feed compositions are provided in the Feed Library database along with the qualities of purchased feeds. 
The database structure has three tables: user_feeds, feed_quality, and nutrients. The user_feeds table contains 
the feed_id keys and feed names for selection by the user. The feed_quality table contains the feed_id, quality 
categories, and the nutrient thresholds for the quality categories. The nutrients table contains the feed composition 
data required for ration formulation.

## Future enhancements

Develop a `FeedManagement` class that directs the management of the `Feed` class
similar to the `AnimalManagement` and `ManureManagement` classes.

The `FeedManagement` class will have 5 primary jobs:
1. Keep track of the different `Storage` objects and how much of each type of feed is in all of them
2. Direct newly-harvested feed from the **Crop and Soil** module to a storage object
3. Tell the **Animal Module** how much feed there is
4. Remove feed from the `Storage` objects daily as the **Animal Module** uses it to feed to cows
5. Sort farm-grown feeds based on a quality assessment based on the fr_PHU (fraction of potential heat units) 
accumulated by the crop at harvest. 

