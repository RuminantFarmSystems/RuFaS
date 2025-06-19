This page is adapted from `Ruminant Farm Systems Model: Development
Progress and
Applications <https://ecommons.cornell.edu/bitstream/handle/1813/110228/Reed%2c%20Kristan.pdf?sequence=2&isAllowed=y>`__.

Last Updated: Jun 13th, 2023

Animal Module
-------------

The **Animal Module** combines the composition and inventory of farm
grown feeds tracked by the **Feed Management and Inventory Module** with
purchased feed to simulate feed delivery each day through the automated,
least-cost diet formulation algorithms. The diet formulation algorithms
are currently based on the NRC (2001) Nutrient Requirements for Dairy
Cattle though we hope to update them soon. The Animal Module uses a
Monte Carlo stochastic framework to simulate each individual animal as
they move through their lifecycle on the farm which is represented by 5
distinct animal classes. Detailed descriptions of the ration formulation
methods and the life events simulated by the Animal Module are provided
in our recent publication (Hansen et al., 2021).

Manure Module
-------------

The **Manure Module** first simulates ammonia emissions from the barn
floor after excretion and before cleaning and then combines the bedding,
flush water, and parlor cleaning water into a simulated reception pit.
Currently the model can represent both flushing and scraping cleaning
systems from tie stall and free stall pens. Compost bedded-pack barns
and dry-lot housing systems are still in development. After the
reception pit, the model simulates movement of the combined manure and
wastewater to either long term storage or for processing. Current
options for manure processing include mechanical solid-liquid separation
and anaerobic digestion. Manure emissions and composition change are
estimated at each daily step during manure handling, processing, and
storage.

Crop and Soil Module
--------------------

On the days when the **Crop and Soil Module** simulates manure
application to fields, the **Manure Module** passes information about
the amount and composition of the manure in storage and subtracts the
mass of the simulated manure application from the stored quantities. The
**Crop and Soil Module** then simulates daily biogeochemical nutrient
and water transformation, crop uptake, and loss from the soil profile
based on a combination of the SWAT (Neitsch et al., 2011), SurPhos
(Vadas, 2009) and DayCent (Del Grosso et al., 2011) models. Crop growth
rate and composition is based on solar radiation, temperature, and water
and N availability. At harvest, above ground crop biomass is partitioned
into crop residue that remains on the field and that which is
transferred to the **Feed Management and Inventory Module** to inventory
management, completing the dairy farm nutrient cycle.

Feed Management and Inventory Module
------------------------------------

The **Feed Management and Inventory Module** is currently managed by the
``Feed`` class and its subclass, ``Storage``.

The ``Feed`` class takes in data from the input JSON file and stores
information for the feeds managed by the farm and the methods for
storage. It contains the ``Storage`` subclass which specifies a single
feed storage receptacle.

Upon harvest, farm grown feed is grouped by crop type, harvest date, and
quality, then assigned to an available storage receptacle sequentially.
Quality assessment for farm-grown feeds addressed in Future Enhancements
section. Forage quality of purchased feeds is provided by the Feed
Library database that is queried in the ``Feed`` class.

Nutrients are lost at various stages from harvest to feedout at various
rates for different feed-storage combinations. Feed storage loss is
currently an empirical model of those reductions based on the work of
Kevin Panke-Buisse, a research microbiologist at the USDA DFRC in
Madison, WI. After pairing a crop to a storage receptacle, the model is
calibrated and nutrient losses at each stage are calculated and applied
sequentially.

Feed compositions are provided in the Feed Library database along with
the qualities of purchased feeds. The database structure has three
tables: user_feeds, feed_quality, and nutrients. The user_feeds table
contains the feed_id keys and feed names for selection by the user. The
feed_quality table contains the feed_id, quality categories, and the
nutrient thresholds for the quality categories. The nutrients table
contains the feed composition data required for ration formulation.

Future enhancements
~~~~~~~~~~~~~~~~~~~

Develop a ``FeedManagement`` class that directs the management of the
``Feed`` class similar to the ``AnimalManagement`` and
``ManureManagement`` classes.

The ``FeedManagement`` class will have 5 primary jobs:

1. Keep track of the different ``Storage`` objects and how much of each
   type of feed is in all of them
2. Direct newly-harvested feed from the **Crop and Soil module** to a
   storage object
3. Tell the **Animal Module** how much feed there is
4. Remove feed from the ``Storage`` objects daily as the **Animal
   Module** uses it to feed to cows
5. Sort farm-grown feeds based on a quality assessment based on the
   fr_PHU (fraction of potential heat units) accumulated by the crop at
   harvest.
