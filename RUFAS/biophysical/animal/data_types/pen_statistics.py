from dataclasses import dataclass, field


@dataclass
class PenStatistics:
    average_phosphorus_intake: float = 0.0
    average_phosphorus_requirement: float = 0.0
    average_phosphorus_animal: float = 0.0

    average_body_weight: float = 0.0
    average_dry_matter_intake_estimation: float = 0.0
    average_DBW: float = 0.0

    average_nutrient_requirements: dict[int, float] = field(default_factory=dict)
    average_milk: float = 0.0
    average_crude_protein_milk: float = 0.0

    average_growth: float = 0.0
    average_milk_production_reduction: float = 0.0
