"""Hardcoded fallback values for economics preprocessing inputs."""

from __future__ import annotations

from typing import Dict, List

# Fallback values for biophysical simulation patterns.
BIOPHYSICAL_FALLBACKS: Dict[str, List[float]] = {
    "AnimalModuleReporter.report_life_cycle_manager_data.bought_heifer_num": [5.0],
    "Economic_preprocessing.Animal.FPCM": [250.0],
    "AnimalModuleReporter.report_life_cycle_manager_data.sold_heiferII_num": [2.0],
    "AnimalModuleReporter.report_life_cycle_manager_data.sold_heiferIII_oversupply_num": [1.0],
    "FeedManager.purchase_feed.ration_interval_*_cost": [100.0],
    "SEE NOTES": [10.0],
    "ManureManager._record_manure_request_results.off_farm_manure.total_manure_mass": [50.0],
    "see future_expansion": [5.0],
    "fertilizer_schedule SEE NOTES": [12.0],
    "both below are from multiple input files, see preprocessing": [8.0],
    "field.crop_specification": [20.0],
    "field.field_size": [30.0],
    "Waiting on tractor_implement and other parts of EEE outputs": [6.0],
}

# Default quantity used when no biophysical or input values are available.
ECONOMIC_QUANTITY_FALLBACK: float = 1.0

# Default price used when no commodity pricing is available.
ECONOMIC_PRICE_FALLBACK: Dict[str, float] = {"revenue": 2.0, "cost": 1.0}
