from dataclasses import dataclass, field

from RUFAS.biophysical.animal.animal import Animal


@dataclass
class DailyHerdUpdates:
    """Collected herd-level animal updates produced while daily routines run."""

    graduated_animals: list[Animal] = field(default_factory=list)
    newborn_calves: list[Animal] = field(default_factory=list)
    removed_animals: list[Animal] = field(default_factory=list)
    sold_newborn_calves: list[Animal] = field(default_factory=list)
    stillborn_newborn_calves: list[Animal] = field(default_factory=list)
    sold_heiferIIs: list[Animal] = field(default_factory=list)
    sold_and_died_cows: list[Animal] = field(default_factory=list)
