"""
This module is based upon the "Root Development" section of the SWAT model (5.2.1.3)
"""


class RootDevelopment:
    def __init__(self):
        self.heat_fraction = 1 / 3
        self.max_root_depth = 20
        self.is_perennial = True
        self.root_depth = None
        self.root_fraction = None

    def develop_roots(self):
        """main root development function

        Details: updates the root_fraction and root_depth attributes. The latter is updated differently
        depending upon whether the plant is perennial.
        """
        # update root fraction
        self.root_fraction = self.determine_root_fraction(self.heat_fraction)
        # update root depth
        if self.is_perennial:
            self.root_depth = self.determine_root_depth(self.max_root_depth, self.heat_fraction)
        else:
            self.root_depth = self.max_root_depth  # TODO: assumption by SWAT - valid perhaps after 1st year?

    @staticmethod
    def determine_root_fraction(heat_fraction: float) -> float:
        """calculates root fraction, as a function of plant maturity

        Args:
            heat_fraction: the proportion of potential heat units accumulated to date: a proxy for maturity

        SWAT Reference: 5:2.1.21

        Returns: the fraction of a plant's biomass comprised of roots [0.4-0.2]
        """
        heat_fraction = max(heat_fraction, 0)  # bound to zero
        if heat_fraction >= 2:  # leads to fraction < 0
            return 0
        else:
            return 0.4 - 0.2 * heat_fraction

    @staticmethod
    def determine_root_depth(max_depth: float, heat_fraction: float) -> float:
        """calculates a plant's root depth on a given day

        Args:
            max_depth: maximum possible root depth (mm)
            heat_fraction: fraction of potential heat units

SWAT Reference: 5:2.1.23, 24

        Returns: root depth (mm)
        """
        if heat_fraction <= 0.4:
            return 2.5 * heat_fraction * max_depth
        else:
            return max_depth
