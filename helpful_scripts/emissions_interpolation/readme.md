## Words of warning
The python script in this folder `emissions_interpolation.py` was written by Joe Waddell, and was only used/tested locally.
This means it can't be guaranteed to work on another computer (especially if not on a windows machine) due to some hardcoding.
He lightly rewrote it to make it a little more user friendly, but please contact him via GitHub if you run into any troubles.

### Overview
The files in this folder relate to: https://github.com/RuminantFarmSystems/MASM/pull/2067

`COUNTY_ZIP_032010.csv` came from: https://www.huduser.gov/portal/datasets/usps_crosswalk.html
This file was necessary for FIPS to zip mapping.
Note that the FIPS codes used here were from the 2010 census, not the 2020 census. Some codes have changed.

`geonames_US.csv` came from: https://www.geonames.org/
This file contains the lat long coordinates for each zip code.
This was opened in Excel and converted to a CSV.

`fips_to_region.csv` is simply mapping regions to FIPS codes

`Feed Emissions Source RuFaS_Feed_Library_Combined_Final.csv` notes the source of emissions factors for each feed item.

Two files with the suffix `_wheat_regional_averages.csv` refer to regional averages collected for a specific pair of wheat feeds (with identical emissions factors), necessary to fill in statewide gaps.

### How to use this
In the first section of the file, there are some user defined values that can be modified, if future use cases here need to modify the methodology we used in PR #2067.
Simply run this script directly, and the files will be created in the `emissions_interpolation` directory (to be evaluated prior to adding to the `input/data/EEE` directory).

Note that there is a special case at the end of the file: for feeds 193 and 197, these were not found across entire states. Therefore, we elected to use regional averages. Hence yet another supplementary pair of files added to the `emissions_interpolation` folder.