import importlib
from random import Random
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer, RationConfig


@pytest.fixture
def optimizer() -> RationOptimizer:
    return RationOptimizer()


def test_build_initial_value_no_status_and_objective(optimizer: RationOptimizer) -> None:
    """Tests _build_initial_value() when the previous ration have no status or objective keys."""
    result = optimizer._build_initial_value({"test": 30, "test2": 80}, MagicMock(RationConfig))
    assert result == [30, 80]


def test_build_initial_value_no_previous_ration(optimizer: RationOptimizer, mocker: MockerFixture) -> None:
    """Tests _build_initial_value() when no previous ration provided"""
    config = MagicMock(RationConfig)
    config.price_list = [43.6, 329.7]
    module_name = RationOptimizer.__module__
    mod = importlib.import_module(module_name)

    mocker.patch.object(mod.random, "random", return_value=1)

    result = optimizer._build_initial_value(previous_ration=None, ration_config=config)

    assert result == [1.0, 10]
