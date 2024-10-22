from typing import List
from unittest.mock import MagicMock, patch

import pytest

from RUFAS.routines.field.field.fertilizer_application import FertilizerApplication
from RUFAS.routines.field.soil.layer_data import LayerData
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.routines.field.soil.soil_data import SoilData


@pytest.mark.parametrize(
    "depth,bottom_depths,expected",
    [
        (15.0, [20.0, 70.0, 200.0], [1.0]),
        (0.0, [20.0, 70.0, 200.0], [1.0]),
        (40.0, [20.0, 70.0, 200.0], [0.5, 0.5]),
        (65.0, [20.0, 70.0, 200.0], [0.30769231, 0.69230769]),
        (70.0, [20.0, 70.0, 200.0], [0.28571429, 0.71428571]),
        (120.0, [20.0, 70.0, 200.0], [0.16666667, 0.58333333, 0.25]),
    ],
)
def test_generate_depth_factors(depth: float, bottom_depths: list[float], expected: list[float]) -> None:
    """Tests that the depth factors are correctly calculated for subsurface nutrient applications."""
    actual = FertilizerApplication.generate_depth_factors(depth, bottom_depths)
    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "nutrient_amounts,depth,subsurface_frac,expected",
    [
        (100.0, 50.0, 0.6, [6.0, 24.0, 30.0, 0.0]),
        (45.0, 120.0, 0.89, [4.005, 16.02, 20.025, 0.0]),
    ],
)
def test_apply_subsurface_fertilizer(
    nutrient_amounts: float, depth: float, subsurface_frac: float, expected: list[float]
) -> None:
    """Tests that subsurface nutrients from fertilizer are applied correctly."""
    field_size = 1.3
    soil_layers = [
        LayerData(top_depth=0.0, bottom_depth=20.0, field_size=field_size),
        LayerData(top_depth=20.0, bottom_depth=70.0, field_size=field_size),
        LayerData(top_depth=70.0, bottom_depth=200.0, field_size=field_size),
        LayerData(top_depth=200.0, bottom_depth=400.0, field_size=field_size),
    ]
    for layer in soil_layers:
        layer.labile_inorganic_phosphorus_content = 0.0
        layer.nitrate_content = 0.0
        layer.ammonium_content = 0.0
        layer.fresh_organic_nitrogen_content = 0.0
        layer.active_organic_nitrogen_content = 0.0
    soil = Soil(soil_data=SoilData(soil_layers=soil_layers, field_size=field_size))
    fert_app = FertilizerApplication(soil=soil)

    with patch(
        "RUFAS.routines.field.field.fertilizer_application.FertilizerApplication.generate_depth_factors",
        new_callable=MagicMock,
        return_value=[0.1, 0.4, 0.5],
    ) as patched_depth_factor_generator:
        fert_app._apply_subsurface_fertilizer(
            nutrient_amounts,
            nutrient_amounts,
            nutrient_amounts,
            nutrient_amounts,
            depth,
            subsurface_frac,
        )

        patched_depth_factor_generator.assert_called_once_with(depth, [20.0, 70.0, 200.0, 400.0])
        for index, expected_result in enumerate(expected):
            assert fert_app.soil.data.soil_layers[index].labile_inorganic_phosphorus_content == expected_result
            assert fert_app.soil.data.soil_layers[index].nitrate_content == expected_result
            assert fert_app.soil.data.soil_layers[index].ammonium_content == expected_result
            assert fert_app.soil.data.soil_layers[index].fresh_organic_nitrogen_content == expected_result
            assert fert_app.soil.data.soil_layers[index].active_organic_nitrogen_content == expected_result


@pytest.mark.parametrize(
    "phosphorus,fertilizer,inorganic_nitrogen_frac,ammonium_frac,organic_nitrogen_frac,depth,"
    "remainder,expected,subsurface_app_call",
    [
        (
            15,
            90,
            0.15,
            0.44,
            0.09,
            0.0,
            1.0,
            [15, 4.44705882, 3.49411765, 2.38235294],
            None,
        ),
        (
            22.1,
            144,
            0.33,
            0.2,
            0.06,
            40.0,
            0.88,
            [19.448, 19.6788706, 4.91971765, 2.23623529],
            (13, 22.3623529, 5.5905882, 2.5411764, 40.0, 0.12),
        ),
        (0, 0, 0, 0, 0, 0.0, 1.0, [0, 0, 0, 0], None),
    ],
)
def test_apply_fertilizer(
    phosphorus: float,
    fertilizer: float,
    inorganic_nitrogen_frac: float,
    ammonium_frac: float,
    organic_nitrogen_frac: float,
    depth: float,
    remainder: float,
    expected: List[float],
    subsurface_app_call: tuple[float],
) -> None:
    """Tests that fertilizer is applied correctly."""
    field_size = 1.7
    fert_app = FertilizerApplication(field_size=field_size)
    fert_app.soil.data.soil_layers[0].nitrate_content = 0
    fert_app.soil.data.soil_layers[0].ammonium_content = 0
    fert_app.soil.data.soil_layers[0].fresh_organic_nitrogen_content = 0
    fert_app.soil.data.soil_layers[0].active_organic_nitrogen_content = 0

    with (
        patch(
            "RUFAS.routines.field.field.fertilizer_application.FertilizerApplication._apply_subsurface_fertilizer",
            new_callable=MagicMock,
        ) as patched_subsurface_applicator,
        patch(
            "RUFAS.routines.field.soil.phosphorus_cycling.fertilizer.Fertilizer.add_fertilizer_phosphorus",
            new_callable=MagicMock,
        ) as patched_phosphorus_applicator,
    ):
        fert_app.apply_fertilizer(
            phosphorus,
            fertilizer,
            inorganic_nitrogen_frac,
            ammonium_frac,
            organic_nitrogen_frac,
            depth,
            remainder,
            field_size,
        )

        patched_phosphorus_applicator.assert_called_once_with(expected[0])
        assert pytest.approx(fert_app.soil.data.soil_layers[0].nitrate_content) == expected[1]
        assert pytest.approx(fert_app.soil.data.soil_layers[0].ammonium_content) == expected[2]
        assert pytest.approx(fert_app.soil.data.soil_layers[0].fresh_organic_nitrogen_content) == expected[3]
        assert pytest.approx(fert_app.soil.data.soil_layers[0].active_organic_nitrogen_content) == expected[3]
        if subsurface_app_call is not None:
            patched_subsurface_applicator.assert_called_once_with(
                pytest.approx(subsurface_app_call[0]),
                pytest.approx(subsurface_app_call[1]),
                pytest.approx(subsurface_app_call[2]),
                pytest.approx(subsurface_app_call[3]),
                subsurface_app_call[4],
                subsurface_app_call[5],
            )
        else:
            patched_subsurface_applicator.assert_not_called()
