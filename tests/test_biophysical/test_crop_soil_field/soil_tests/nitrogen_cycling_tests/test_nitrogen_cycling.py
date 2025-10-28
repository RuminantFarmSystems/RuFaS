from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.field.soil.nitrogen_cycling.denitrification import Denitrification
from RUFAS.biophysical.field.soil.nitrogen_cycling.humus_mineralization import HumusMineralization
from RUFAS.biophysical.field.soil.nitrogen_cycling.leaching_runoff_erosion import LeachingRunoffErosion
from RUFAS.biophysical.field.soil.nitrogen_cycling.mineralization_decomp import MineralizationDecomposition
from RUFAS.biophysical.field.soil.nitrogen_cycling.nitrification_volatilization import NitrificationVolatilization
from RUFAS.biophysical.field.soil.nitrogen_cycling.nitrogen_cycling import NitrogenCycling


@pytest.mark.parametrize(
    "field_size",
    [
        3,
        90.24,
        77,
    ],
)
def test_cycle_nitrogen(field_size: float) -> None:
    NitrificationVolatilization.do_daily_nitrification_and_volatilization = MagicMock()
    Denitrification.denitrify = MagicMock()
    HumusMineralization.mineralize_organic_nitrogen = MagicMock()
    MineralizationDecomposition.mineralize_and_decompose_nitrogen = MagicMock()
    LeachingRunoffErosion.leach_runoff_and_erode_nitrogen = MagicMock()

    cycle = NitrogenCycling(field_size=field_size)
    cycle.cycle_nitrogen(field_size=field_size)

    LeachingRunoffErosion.leach_runoff_and_erode_nitrogen.assert_called_once_with(field_size)
    assert Denitrification.denitrify.call_count == 1
    assert HumusMineralization.mineralize_organic_nitrogen.call_count == 1
    assert MineralizationDecomposition.mineralize_and_decompose_nitrogen.call_count == 1
    assert NitrificationVolatilization.do_daily_nitrification_and_volatilization.call_count == 1
