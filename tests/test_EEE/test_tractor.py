from copy import deepcopy
from typing import Any
from unittest.mock import MagicMock

import pytest

from pytest_mock import MockFixture

from RUFAS.EEE.tractor_implement import TractorImplement
from RUFAS.data_structures.tillage_implements import TractorSize, FieldOperationEvent, TillageImplement, OperationType
from RUFAS.EEE.tractor import Tractor
from RUFAS.input_manager import InputManager
from tests.test_EEE.fixtures import EEE_constants, tractor_dataset, mock_tractor

assert EEE_constants is not None
assert tractor_dataset is not None


@pytest.mark.parametrize(
    "herd_size, expected_size",
    [
        (100, TractorSize.SMALL),
        (500, TractorSize.MEDIUM),
        (1500, TractorSize.MEDIUM),
        (2000, TractorSize.LARGE),
        (3000, TractorSize.LARGE),
    ],
)
def test_herd_size_to_tractor_size(
    herd_size: int,
    expected_size: TractorSize,
    EEE_constants: list[dict[str, Any]],
    tractor_dataset: dict[str, list[Any]],
    mocker: MockFixture,
) -> None:
    """Tests the herd size to tractor size conversion."""
    im = InputManager()
    mocker.patch.object(im, "get_data", side_effect=[deepcopy(EEE_constants), tractor_dataset, deepcopy(EEE_constants)])
    specs = Tractor(
        FieldOperationEvent.TILLING,
        herd_size=herd_size,
        tillage_implement=TillageImplement.DISK_HARROW,
        application_depth=10,
    )
    assert specs.tractor_size == expected_size


@pytest.mark.parametrize("tractor_size", list(TractorSize))
def test_tractor_size_initialization(
    tractor_size: TractorSize,
    EEE_constants: list[dict[str, Any]],
    tractor_dataset: dict[str, list[Any]],
    mocker: MockFixture,
) -> None:
    """Tests the tractor size initialization."""
    specs = mock_tractor(tractor_size, EEE_constants, tractor_dataset, mocker)
    assert specs.tractor_size == tractor_size


def test_raises_value_error_for_missing_parameters() -> None:
    """Tests that a ValueError is raised when missing required parameters."""
    with pytest.raises(ValueError):
        Tractor(operation_event=FieldOperationEvent.TILLING)


@pytest.mark.parametrize("herd_size", [-1, -100])
def test_herd_size_negative_value_error(herd_size: int) -> None:
    """Tests that a ValueError is raised when herd size is negative."""
    with pytest.raises(ValueError):
        Tractor(operation_event=FieldOperationEvent.TILLING, herd_size=herd_size)


@pytest.mark.parametrize(
    "operation_event, crop_type, application_depth, expected_result",
    [
        (
            FieldOperationEvent.HARVEST,
            "alfalfa_hay",
            10.0,
            [OperationType.MOWING, OperationType.WINDROWING, OperationType.COLLECTION],
        ),
        (
            FieldOperationEvent.HARVEST,
            "alfalfa_silage",
            10.0,
            [OperationType.MOWING, OperationType.WINDROWING, OperationType.COLLECTION],
        ),
        (
            FieldOperationEvent.HARVEST,
            "alfalfa_baleage",
            10.0,
            [OperationType.MOWING, OperationType.WINDROWING, OperationType.COLLECTION],
        ),
        (
            FieldOperationEvent.HARVEST,
            "tall_fescue_hay",
            10.0,
            [OperationType.MOWING, OperationType.WINDROWING, OperationType.COLLECTION],
        ),
        (
            FieldOperationEvent.HARVEST,
            "tall_fescue_silage",
            10.0,
            [OperationType.MOWING, OperationType.WINDROWING, OperationType.COLLECTION],
        ),
        (
            FieldOperationEvent.HARVEST,
            "tall_fescue_baleage",
            10.0,
            [OperationType.MOWING, OperationType.WINDROWING, OperationType.COLLECTION],
        ),
        (FieldOperationEvent.HARVEST, "winter_wheat_grain", 10.0, [OperationType.COLLECTION]),
        (
            FieldOperationEvent.FERTILIZER_APPLICATION,
            "alfalfa_hay",
            0.0,
            [OperationType.FERTILIZER_APPLICATION_SURFACE],
        ),
        (
            FieldOperationEvent.FERTILIZER_APPLICATION,
            "alfalfa_hay",
            10.0,
            [OperationType.FERTILIZER_APPLICATION_BELOW_SURFACE],
        ),
        (FieldOperationEvent.MANURE_APPLICATION, "alfalfa_hay", 0.0, [OperationType.LIQUID_MANURE_APPLICATION_SURFACE]),
        (
            FieldOperationEvent.MANURE_APPLICATION,
            "alfalfa_hay",
            10.0,
            [OperationType.LIQUID_MANURE_APPLICATION_BELOW_SURFACE],
        ),
        (FieldOperationEvent.PLANTING, "alfalfa_hay", 10.0, [OperationType.PLANTING]),
        (FieldOperationEvent.TILLING, "alfalfa_hay", 10.0, [OperationType.TILLING]),
    ],
)
def test_determine_operation_type(
    operation_event: FieldOperationEvent,
    crop_type: str,
    application_depth: float,
    expected_result: list[OperationType],
    EEE_constants: list[dict[str, Any]],
    tractor_dataset: dict[str, list[Any]],
    mocker: MockFixture,
) -> None:
    """Tests the operation type determination."""
    im = InputManager()
    mocker.patch.object(im, "get_data", side_effect=[deepcopy(EEE_constants)])
    mocker.patch("RUFAS.EEE.tractor_implement.TractorImplement.__init__", return_value=None)
    tractor = Tractor(
        operation_event=operation_event,
        crop_type=crop_type,
        tractor_size=TractorSize.SMALL,
        herd_size=100,
        application_depth=application_depth,
        tillage_implement=TillageImplement.DISK_HARROW,
    )
    assert tractor.operation_types == expected_result


@pytest.mark.parametrize(
    "tractor_size, expected_pto_kW",
    [
        (TractorSize.SMALL, 55.93),
        (TractorSize.MEDIUM, 208.42),
        (TractorSize.LARGE, 328.11),
    ],
)
def test_pto_kW(
    tractor_size: TractorSize,
    expected_pto_kW: float,
    EEE_constants: list[dict[str, Any]],
    tractor_dataset: dict[str, list[Any]],
    mocker: MockFixture,
) -> None:
    """Tests the PTO kW calculation."""
    specs = mock_tractor(tractor_size, EEE_constants, tractor_dataset, mocker)
    assert specs.PTO_kW == expected_pto_kW


@pytest.mark.parametrize(
    "tractor_size, expected_power_available_kW",
    [
        (TractorSize.SMALL, 55.93 / 1.4),
        (TractorSize.MEDIUM, 208.42 / 1.4),
        (TractorSize.LARGE, 328.11 / 1.4),
    ],
)
def test_power_available_kW(
    tractor_size: TractorSize,
    expected_power_available_kW: float,
    EEE_constants: list[dict[str, Any]],
    tractor_dataset: dict[str, list[Any]],
    mocker: MockFixture,
) -> None:
    """Tests the power available kW calculation."""
    specs = mock_tractor(tractor_size, EEE_constants, tractor_dataset, mocker)
    assert specs.power_available_kW == expected_power_available_kW


@pytest.mark.parametrize(
    "tractor_size, expected_mass_kg",
    [
        (TractorSize.SMALL, 8400.0),
        (TractorSize.MEDIUM, 12700.0),
        (TractorSize.LARGE, 20856.0),
    ],
)
def test_mass_kg(
    tractor_size: TractorSize,
    expected_mass_kg: float,
    EEE_constants: list[dict[str, Any]],
    tractor_dataset: dict[str, list[Any]],
    mocker: MockFixture,
) -> None:
    """Tests the mass kg calculation."""
    specs = mock_tractor(tractor_size, EEE_constants, tractor_dataset, mocker)
    assert specs.mass_kg == expected_mass_kg


def test_speed_km_hr(
    EEE_constants: list[dict[str, Any]], tractor_dataset: dict[str, list[Any]], mocker: MockFixture
) -> None:
    """Tests the speed km/hr calculation."""
    specs = mock_tractor(TractorSize.SMALL, EEE_constants, tractor_dataset, mocker)  # Any tractor size would do
    assert specs.speed_km_hr == 10.0


@pytest.mark.parametrize(
    "tractor_mass, implement_mass, speed_km_hr, expected_result",
    [
        # Basic case
        (2000, 500, 10, (2000 + 500) * 10 * 0.00022039111111),  # 2500 * 10 * ~0.00022039111111
        # Zero speed (no power)
        (1500, 800, 0, 0.0),
        # Zero implement mass
        (1800, 0, 15, 1800 * 15 * 0.00022039111111),
        # Zero tractor mass
        (0, 1200, 8, 1200 * 8 * 0.00022039111111),
        # All zeros
        (0, 0, 0, 0.0),
    ],
)
def test_calculate_axel_power(
    tractor_mass: float,
    implement_mass: float,
    speed_km_hr: float,
    expected_result: float,
    EEE_constants: list[dict[str, Any]],
    tractor_dataset: dict[str, list[Any]],
    mocker: MockFixture,
) -> None:
    """Tests the axel power calculation."""
    tractor = mock_tractor(TractorSize.SMALL, EEE_constants, tractor_dataset, mocker)

    mocker.patch.object(Tractor, "mass_kg", new_callable=mocker.PropertyMock, return_value=tractor_mass)
    mocker.patch.object(Tractor, "speed_km_hr", new_callable=mocker.PropertyMock, return_value=speed_km_hr)
    implement = MagicMock(auto_spec=TractorImplement)
    implement.mass_kg = implement_mass

    actual = tractor.calculate_axel_power(implement)

    assert actual == pytest.approx(expected_result)
