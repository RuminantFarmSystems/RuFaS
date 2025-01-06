# flake8: noqa
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

#################
# User settings #
#################
# Dataset to modify: # NOTE # this has to be run twice, reordering the below, if algorithm should be used on both.
EEEname = "full_feeds_land_use_change_emissions_July2024"
EEEname = "full_feeds_emissions_July2024"

# start distance for beighbor search.
km_radius_start = 50
# User should select if they want to run this algorithm on specific subsets of feed data.
# This value should map to one of the options in the feed_source file
feed_source_choice = "Foods3"

# set this to true if you want to use regional averages for wheat middlings, for known cases where data are missing for some states.
# NOTE that the resulting files will have a different suffix.
use_wheat_regional_average = True

##########################################
# Load files necessary for interpolation #
##########################################
zip_to_latlong_sheet = pd.read_csv(r"helpful_scripts\emissions_interpolation\geonames_US.csv")

fips_to_county_sheet = pd.read_csv(r"helpful_scripts\emissions_interpolation\COUNTY_ZIP_032010.csv")

feed_source = pd.read_csv(
    "helpful_scripts\emissions_interpolation\Feed Emissions Source RuFaS_Feed_Library_Combined_Final.csv"
)

fips_to_region = pd.read_csv(r"helpful_scripts\emissions_interpolation\fips_to_region.csv")

regional_sheet = pd.read_csv(f"input\data\EEE\{EEEname}_wheat_regional_averages.csv")


def get_statecode(county_code):
    return str(county_code).zfill(5)[0:2]


def get_zips_from_fips(fips_to_county_sheet, fips_code):
    all_matches = fips_to_county_sheet.loc[fips_to_county_sheet["COUNTY"] == fips_code]
    ziplist = list(all_matches["ZIP"].values)
    return ziplist


def get_latlong_from_zip(
    zip_to_latlong_sheet, zipcodes: list[int]
) -> tuple[tuple[float, float], list[tuple[float, float]]]:
    latlonglist = []
    latlist = []
    longlist = []
    for zip_code in zipcodes:
        try:
            lat = float(zip_to_latlong_sheet.loc[zip_to_latlong_sheet["zip_code"] == zip_code]["lat"].values[0])
            long = float(zip_to_latlong_sheet.loc[zip_to_latlong_sheet["zip_code"] == zip_code]["long"].values[0])
            latlonglist.append((lat, long))
            latlist.append(lat)
            longlist.append(long)
        except:
            print(f"missing zip code {zip_code}")
    if not latlist:
        print("latlist nonexistent")
        return (0.0, 0.0), [(0.0, 0.0)]
    averagelatlong = (float(np.mean(latlist)), float(np.mean(longlist)))
    return averagelatlong, latlonglist


def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def points_within_radius(reference_point, points, radius=100):
    """
    Finds all points within a certain radius (in km) of a reference GPS point.

    Parameters
    ----------
    reference_point : tuple
        A tuple containing latitude and longitude of the reference point.

    points : list
        A list of tuples, each containing latitude and longitude of the points to check.

    radius : float
        The radius in kilometers within which to find points. Default is 100 km.

    Returns
    -------
        list: A list of points that are within the given radius of the reference point.
    """
    lat1, lon1 = reference_point
    close_points = []
    close_distances = []
    for point in points:
        lat2, lon2 = point
        distance = haversine(lat1, lon1, lat2, lon2)
        if distance <= radius and distance != 0.0:
            close_points.append(point)
            close_distances.append(distance)
    return close_points, close_distances


def get_neighbors(fips_code: int, fips_code_list: list[int]) -> list[int]:
    # do the stuff with the fips code
    # get the GPS coordinate
    return [fips_code]


#######################
# Load the datasets ###
#######################

# loading in the dataset of interest
# NOTE # User will need to do this for both the LUC and base file
emissions_doc_location = f"input\\data\\EEE\\{EEEname}.csv"
emissions_doc = pd.read_csv(emissions_doc_location)

emissions_doc["county_code"]
# checking mid maturity corn silage
emissions_doc["51"][emissions_doc["51"] == 0]

# prep column name lists
feed_columns = list(emissions_doc.columns)
feed_columns.remove("county_code")

county_codes = list(emissions_doc["county_code"])


#####################
# GPS for each FIPS #
#####################

fips_gps_map = []
for fips_code in county_codes:
    zipcodes = []
    statecode = get_statecode(fips_code)
    while not zipcodes and get_statecode(fips_code) == statecode:
        if fips_code == 9001:
            print("9001")
        if fips_code == 9007:
            print("9007")
        zipcodes = get_zips_from_fips(fips_to_county_sheet, fips_code)
        if not zipcodes:
            print(fips_code)
            fips_code += 1
            print("beep")
    averagelatlong, latlongs = get_latlong_from_zip(zip_to_latlong_sheet, zipcodes)
    fips_gps_map.append(averagelatlong)

# print(fips_gps_map)
assert len(fips_gps_map) == len(county_codes)

###########################
# Neighbors for each FIPS #
###########################
feed_ids_to_check = feed_source[feed_source["EF_Source"] == feed_source_choice]["RuFaS ID"].tolist()

emissions_copy = emissions_doc.copy()
emissions_neighbors_detailed = []

for idx_county_code, county_code in enumerate(county_codes):  # noqa: C901
    statecode = get_statecode(county_code)
    gps_county = fips_gps_map[idx_county_code]

    county_codes_without_self = county_codes.copy()
    county_codes_without_self.remove(county_code)
    tempmap = fips_gps_map.copy()
    tempmap.remove(gps_county)
    if len(tempmap) != len(county_codes_without_self):
        raise ValueError("temp map and county codes don't match")
    gps_points_in_state = [x for x, y in zip(tempmap, county_codes_without_self) if get_statecode(y) == statecode]
    for idx_feed, feed_id in enumerate(feed_columns):
        if feed_id == "1" and statecode == "09":
            print("catchit")
        if emissions_doc[feed_id][idx_county_code] == 0.0 and float(feed_id) in feed_ids_to_check:
            neighbor_values: list[float] = []
            neighbor_distances = []
            km_radius = km_radius_start

            neighbors_gps_list, neighbors_distance_list = points_within_radius(
                gps_county, gps_points_in_state, km_radius
            )

            while not neighbors_distance_list or not neighbor_values:
                kmmax = 5000
                if km_radius > kmmax:
                    break
                for idx, gps in enumerate(neighbors_gps_list):
                    if neighbors_distance_list[idx] == 0.0:
                        pass
                    else:
                        neighbor_idx = fips_gps_map.index(gps)
                        neighbor_value = emissions_doc[feed_id][neighbor_idx]
                        if neighbor_value > 0.0:
                            neighbor_values.append(neighbor_value)
                            neighbor_distances.append(neighbors_distance_list[idx])
                            neighbor_county_code = county_codes[neighbor_idx]
                km_radius += 50
                neighbors_gps_list, neighbors_distance_list = points_within_radius(
                    gps_county, gps_points_in_state, km_radius
                )

            if not neighbor_values:
                emissions_neighbors_detailed.append(
                    [county_code, gps_county, feed_id, "could not find neighbor within state", km_radius]
                )
            else:
                neighborly_average_value = np.mean(neighbor_values)
                emissions_copy.loc[idx_county_code, feed_id] = neighborly_average_value
                emissions_neighbors_detailed.append(
                    [county_code, gps_county, feed_id, neighbor_values, neighbor_distances]
                )


#################################################################
# Final step to fill in missing state vals for some wheat items #
#################################################################

if use_wheat_regional_average:
    for idx_county_code, county_code in enumerate(county_codes):
        for feed_id in ["193", "197"]:
            if emissions_copy[feed_id][idx_county_code] == 0.0:
                region_found = str(fips_to_region[fips_to_region["FIPS"] == county_code]["Region"].values[0])
                if region_found in ["New.England", "Great.Lakes"]:
                    region_found = "Northeast"
                if region_found in ["Upper.Midwest"]:
                    region_found = "Northern.Plains"
                regional_average = float(regional_sheet[regional_sheet["region"] == region_found]["wheat"].values[0])
                emissions_copy.loc[idx_county_code, feed_id] = regional_average

    emissions_copy.to_csv(
        f"helpful_scripts/emissions_interpolation/{EEEname}_interpolated_regional_average.csv", index=False
    )

    emissions_neighbors_detailed_pd = pd.DataFrame(emissions_neighbors_detailed)
    # emissions_neighbors_detailed_pd.to_csv("emissions_nozeroes_detailed.csv", index=False)

    emissions_neighbors_detailed_pd.columns = [
        "county_code",
        "gps_county",
        "feed_id",
        "neighbor_values",
        "neighbor_distances",
    ]
    emissions_neighbors_detailed_pd.to_csv(
        f"helpful_scripts/emissions_interpolation/{EEEname}_interpolated_regionalavg_detailed.csv", index=False
    )
else:
    emissions_copy.to_csv(f"helpful_scripts/emissions_interpolation/{EEEname}_interpolated.csv", index=False)

    emissions_neighbors_detailed_pd = pd.DataFrame(emissions_neighbors_detailed)
    # emissions_neighbors_detailed_pd.to_csv("emissions_nozeroes_detailed.csv", index=False)

    emissions_neighbors_detailed_pd.columns = [
        "county_code",
        "gps_county",
        "feed_id",
        "neighbor_values",
        "neighbor_distances",
    ]
    emissions_neighbors_detailed_pd.to_csv(
        f"helpful_scripts/emissions_interpolation/{EEEname}_interpolated_detailed.csv", index=False
    )
