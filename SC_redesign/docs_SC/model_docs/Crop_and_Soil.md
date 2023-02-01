
# Crop and Soil

The **Crop and Soil** submodule of the **RuFaS** whole-farm system model simulates agricultural fields, the soils those
fields contain, the crops grown in the fields, utilization of the fields by animals 
(i.e., grazing), <!-- TODO: grazing not yet implemented --> 
and environmental impacts (e.g., emissions). The simulations represent real biogeophysical 
processes that occur on farms and can assist growers in making decisions about their systems and management 
practices.

Users define farms that contain a number of fields. Each field has a geographic location, a specific dimension (area), 
and contains soil whose structure and composition will change throughout the course of the simulation (and across the 
soil profile). Nutrients can be added to the soil through amendments and tillage; 
water and nutrients cycle through the system, affected by weather; soils can erode and compact depending on their
usage. A field can be planted with crops (one or multiple species, annual or perennial), which photosynthesize and 
exchange resources with the soil to grow. 

![Field System Conceptual Design](./SC-temporal-model-diagram.jpg)
*Conceptual model for Crop and Soil module simulations*

The field systems and their driving processes are simulated on a daily basis. This fine-scale temporal
resolution allows for systems that can rapidly respond to external changes (i.e., weather and management). Users can 
define management schedules that determine when crops are planted and harvest, when manure or fertilizers are added
to the soil, when and what kind of tillage occurs, and the timing and duration of grazing. All these processes
contribute to the resulting estimates of interest. Some such output that the model simulates includes biomass and 
nutrient composition of crops throughout their life cycle, harvestable economic yield produced by the crops at the end
of a growing season, soil health and composition, soil nutrient retention and loss, 
environmental impacts, <!-- TODO: emmissions and other environmental factors not yet implemented --> and the 
projected impacts of various or altered management practices <!-- projections not yet implemented -->. 


## Details
<!-- TODO: update once the redesign of crop and soil is finished -->
**Under Construction**: This section is in-development and will be updated as the **Crop and Soil** module progresses.




### Crop Growth

Growth of a crop is governed by the [Crop submodule](./crop.md) <!-- TODO: currently no crop.md file -->

<!-- TODO: list other class submodules as their docs are completed -->

* The development and maintenance of the root system is determined with the 
[Root Development class](./root_development.md) 
* Crop yields at the end of the growing season are calculated from the [Crop Yields class](./crop_yields.md)

### Soil Processes
TBD
### Field Management Practices
TBD
### Farm Management
TBD
