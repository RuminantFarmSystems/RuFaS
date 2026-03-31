from typing import Optional

from RUFAS.biophysical.field.soil.nitrogen_cycling.denitrification import Denitrification
from RUFAS.biophysical.field.soil.nitrogen_cycling.humus_mineralization import HumusMineralization
from RUFAS.biophysical.field.soil.nitrogen_cycling.leaching_runoff_erosion import LeachingRunoffErosion
from RUFAS.biophysical.field.soil.nitrogen_cycling.mineralization_decomp import MineralizationDecomposition
from RUFAS.biophysical.field.soil.nitrogen_cycling.nitrification_volatilization import NitrificationVolatilization
from RUFAS.biophysical.field.soil.soil_data import SoilData


class NitrogenCycling:
    """
    Composite class for managing all aspects of nitrogen cycling within the soil profile.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track and manage nitrogen cycling in the soil. If not provided,
        a new SoilData object will be created.
    field_size : float, optional
        The size of the field in hectares (ha), utilized to initialize a SoilData object if one is not directly
        supplied.

    Attributes
    ----------
    data : SoilData
        Holds the SoilData object for tracking nitrogen cycling processes.
    leaching_runoff_erode : LeachingRunoffErosion
        Component responsible for tracking nitrogen movement between soil layers and loss due to runoff and erosion.
    nitrification_volatilization : NitrificationVolatilization
        Component managing the nitrification and volatilization of ammonium within the soil.
    denitrification : Denitrification
        Component for the denitrification of nitrate within the soil profile.
    mineralization_decomposition : MineralizationDecomposition
        Component for the mineralization and decomposition of fresh nitrogen and residue in the soil.
    humus_mineralization : HumusMineralization
        Component managing the active and stable organic nitrogen pools.

    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

        self.leaching_runoff_erode = LeachingRunoffErosion(self.data)
        self.nitrification_volatilization = NitrificationVolatilization(self.data)
        self.denitrification = Denitrification(self.data)
        self.mineralization_decomposition = MineralizationDecomposition(self.data)
        self.humus_mineralization = HumusMineralization(self.data)

    def cycle_nitrogen(self, field_size: float) -> None:
        """
        Executes the daily update operations on all process components.

        Parameters
        ----------
        field_size : float
            Size of the field (ha).

        """
        self.leaching_runoff_erode.leach_runoff_and_erode_nitrogen(field_size)
        self.nitrification_volatilization.do_daily_nitrification_and_volatilization()
        self.denitrification.denitrify(field_size)
        self.mineralization_decomposition.mineralize_and_decompose_nitrogen()
        self.humus_mineralization.mineralize_organic_nitrogen()
