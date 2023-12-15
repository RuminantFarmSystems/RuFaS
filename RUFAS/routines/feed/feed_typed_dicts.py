from typing import Dict, List, TypedDict


class StorageOption(TypedDict):
    """
    Lists all the expected keys and their value types present in the configuration
    data dictionary for different storage options. Whenever an unexpected key or
    an invalid value type is used, the editor should flag with a warning.
    """

    storage_type: str
    moisture: str
    additive: str
    packing_density: int
    inoculation: str
    bunk_type: str
    ventilation: bool
    removal_rate: int
    initial_dry_matter: int


class PurchasedFeedTypedDict(TypedDict):
    """
    Lists all the expected keys and their value types present in the
    purchased_feed.json or the like. Whenever an unexpected key or
    an invalid value type is used, the editor should flag with a warning.
    """

    feed_database: str
    feeds_table: str
    feed_quality_table: str
    nutrient_table: str

    calf_feeds: List[int]
    growing_feeds: List[int]
    close_up_feeds: List[int]
    lac_cow_feeds: List[int]

    purchased_feeds: List[int]
    purchased_feeds_costs: Dict[str, float]
    farm_grown_feeds: List

    storage_options: Dict[str, StorageOption]

    user_defined_ration_percentages: Dict[str, float]
