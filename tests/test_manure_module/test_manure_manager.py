import math
import pytest
from mock import MagicMock, call
from pytest_mock import MockFixture, MockerFixture

from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.enums import AnimalCombination
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.field_manure_supplier import FieldManureSupplier
from RUFAS.routines.manure.IO_helpers.manure_module_output_manager_helper import ManureModuleOutputManagerHelper
from RUFAS.routines.manure.manure_manager import ManureManager
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.units import MeasurementUnits


@pytest.mark.parametrize("simulate_animals,log_added", [(True, False), (False, True)])
def test_manure_manager_init(mocker: MockFixture, simulate_animals: bool, log_added: bool) -> None:
    """Unit test for __init__() of ManureManager in manure_manager.py"""
    # Arrange
    mock_animal_manager = mocker.MagicMock()
    mock_animal_manager.all_pens = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()
    mock_manure_manager_config_handler = mocker.MagicMock()
    patch_for_manure_manager_config_handler = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManagerConfigHandler",
        return_value=mock_manure_manager_config_handler,
    )
    mock_manure_nutrient_manager = mocker.MagicMock()
    patch_for_manure_nutrient_manager = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureNutrientManager",
        return_value=mock_manure_nutrient_manager,
    )
    patch_field_manure_supplier = mocker.patch.object(FieldManureSupplier, "__init__", return_value=None)
    patch_forconfigure_manure_manager_components = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager." "configure_manure_manager_components",
        return_value=None,
    )

    # Act
    manure_manager = ManureManager(
        pen_list=mock_animal_manager.all_pens,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
        simulate_animals=simulate_animals,
    )

    # Assert
    assert manure_manager.beddings == {}
    assert manure_manager.manure_handlers == {}
    assert manure_manager.reception_pits == {}
    assert manure_manager.manure_separators == {}
    assert manure_manager.manure_treatments == {}
    assert manure_manager.weather == mock_weather
    assert manure_manager.time == mock_time
    assert manure_manager.simulate_animals == simulate_animals

    patch_for_manure_manager_config_handler.assert_called_once_with(mock_manure_manager_config)
    assert manure_manager.manure_manager_config_handler == mock_manure_manager_config_handler
    patch_for_manure_nutrient_manager.assert_called_once()
    patch_forconfigure_manure_manager_components.assert_called_once_with(mock_animal_manager.all_pens)
    patch_field_manure_supplier.assert_called_once()


@pytest.mark.parametrize(
    "manure_separator",
    [
        "none",
        "test_manure_separator",
    ],
)
def test_configure_manure_manager_components(manure_separator: str, mocker: MockFixture) -> None:
    """Unit test for configure_manure_manager_components() in manure_manager.py"""

    # Arrange
    mock_animal_manager = mocker.MagicMock()
    mock_pen = mocker.MagicMock()
    mock_all_pens = [mock_pen]
    mock_animal_manager.all_pens = mock_all_pens

    mock_manure_manager_pen = mocker.MagicMock()
    mock_manure_manager_pen.id = pen_id = 1
    mock_manure_manager_pen.bedding_type = bedding_type = "test_bedding_type"
    mock_manure_manager_pen.manure_handler = manure_handler = "test_manure_handler"
    mock_manure_manager_pen.manure_separator = manure_separator
    mock_manure_manager_pen.manure_separator_after_digestion = manure_separator
    mock_manure_manager_pen.manure_treatment = manure_treatment = "test_manure_treatment"
    patch_for_manure_manager_pen_init = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManagerPen",
        return_value=mock_manure_manager_pen,
    )

    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()

    mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager.__init__",
        return_value=None,
    )

    manure_manager = ManureManager(
        pen_list=mock_animal_manager.all_pens,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
        simulate_animals=True,
    )

    mock_manure_manager_config_handler = mocker.MagicMock()

    mock_bedding_config = mocker.MagicMock()
    mock_manure_manager_config_handler.get_bedding_config.return_value = mock_bedding_config
    mock_bedding = mocker.MagicMock()
    patch_for_bedding_factory_get_instance = mocker.patch(
        "RUFAS.routines.manure.manure_manager.BeddingFactory.get_instance",
        return_value=mock_bedding,
    )

    mock_manure_handler_config = mocker.MagicMock()
    mock_manure_manager_config_handler.get_manure_handler_config.return_value = mock_manure_handler_config
    mock_manure_handler = mocker.MagicMock()
    patch_for_manure_handler_factory_get_manure_handler = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureHandlerFactory.get_manure_handler",
        return_value=mock_manure_handler,
    )

    mock_reception_pit = mocker.MagicMock()
    patch_for_reception_pit_init = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ReceptionPit",
        return_value=mock_reception_pit,
    )

    mock_manure_separator_config = mocker.MagicMock() if not manure_separator == "none" else None
    mock_manure_manager_config_handler.get_manure_separator_config.return_value = mock_manure_separator_config
    mock_manure_separator = mocker.MagicMock()
    patch_for_manure_separator_factory_get_instance = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureSeparatorFactory.get_instance",
        return_value=mock_manure_separator,
    )

    mock_manure_treatment_config = mocker.MagicMock()
    mock_manure_manager_config_handler.get_manure_treatment_config.return_value = mock_manure_treatment_config
    mock_manure_treatment = mocker.MagicMock()
    patch_for_manure_treatment_factory_get_instance = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureTreatmentFactory.get_instance",
        return_value=mock_manure_treatment,
    )

    manure_manager.manure_manager_config_handler = mock_manure_manager_config_handler
    manure_manager.beddings = {}
    manure_manager.manure_handlers = {}
    manure_manager.reception_pits = {}
    manure_manager.manure_separators = {}
    manure_manager.manure_separators_after_digestion = {}
    manure_manager.manure_treatments = {}
    manure_manager.weather = mock_weather
    manure_manager.time = mock_time

    # Act
    manure_manager.configure_manure_manager_components(mock_animal_manager.all_pens)

    # Assert
    patch_for_manure_manager_pen_init.assert_called_once_with(mock_pen)

    mock_manure_manager_config_handler.get_bedding_config.assert_called_once_with(bedding_type)
    patch_for_bedding_factory_get_instance.assert_called_once_with(
        bedding_name=bedding_type,
        bedding_config=mock_bedding_config,
    )
    assert manure_manager.beddings[pen_id] == mock_bedding

    mock_manure_manager_config_handler.get_manure_handler_config.assert_called_once_with(manure_handler)
    patch_for_manure_handler_factory_get_manure_handler.assert_called_once_with(
        configuration_name=manure_handler,
        weather=mock_weather,
        time=mock_time,
        manure_handler_config=mock_manure_handler_config,
    )
    assert manure_manager.manure_handlers[pen_id] == mock_manure_handler

    patch_for_reception_pit_init.assert_called_once()
    assert manure_manager.reception_pits[pen_id] == mock_reception_pit

    mock_manure_manager_config_handler.get_manure_separator_config.assert_called_with(manure_separator)
    if manure_separator == "none":
        patch_for_manure_separator_factory_get_instance.assert_not_called()
        assert manure_manager.manure_separators[pen_id] is None
    else:
        patch_for_manure_separator_factory_get_instance.assert_called_with(
            configuration_name=manure_separator,
            manure_separator_config=mock_manure_separator_config,
        )
        assert manure_manager.manure_separators[pen_id] == mock_manure_separator

    mock_manure_manager_config_handler.get_manure_treatment_config.assert_called_once_with(manure_treatment)
    patch_for_manure_treatment_factory_get_instance.assert_called_once_with(
        configuration_name=manure_treatment,
        weather=mock_weather,
        time=mock_time,
        manure_treatment_config=mock_manure_treatment_config,
    )
    assert manure_manager.manure_treatments[pen_id] == mock_manure_treatment


@pytest.mark.parametrize(
    "manure_treatment_name, is_compound_anaerobic_treatment",
    [
        ("slurry storage underfloor", False),
        ("slurry storage outdoor", False),
        ("anaerobic lagoon", False),
        ("anaerobic digestion", False),
        ("totally custom manure treatment", False),
        ("anaerobic digestion and lagoon", True),
        ("anaerobic digestion and lagoon with separator", True),
    ],
)
def test_is_compound_anaerobic_manure_treatment(
    manure_treatment_name: str,
    is_compound_anaerobic_treatment: bool,
) -> None:
    """Unit test for _is_compound_anaerobic_manure_treatment() in manure_manager.py."""
    result = ManureManager._is_compound_anaerobic_manure_treatment(manure_treatment_name)

    assert result == is_compound_anaerobic_treatment


@pytest.mark.parametrize(
    "is_manure_separator_present",
    [
        True,
        False,
    ],
)
def test_handle_daily_update_for_simple_manure_treatment(
    is_manure_separator_present: bool, mocker: MockFixture
) -> None:
    """
    Unit test for _handle_daily_update_for_simple_manure_treatment() in manure_manager.py.

    This test checks the daily update functionality of a simple manure treatment process with and
    without a manure separator. It verifies that the method correctly interacts with the manure
    separator (if present), the manure handler, and the manure treatment, returning appropriate daily
    outputs and accumulated output for the treatment.

    """
    # Arrange
    simulation_day = 1
    mock_manure_manager_pen = mocker.MagicMock()
    mock_manure_manager_pen.id = pen_id = 1
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_reception_pit_daily_output = mocker.MagicMock()

    mock_animal_manager = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()

    mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager.__init__",
        return_value=None,
    )
    manure_manager = ManureManager(
        animal_manager=mock_animal_manager,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )
    manure_manager.manure_separators = {}
    manure_manager.manure_treatments = {}

    mock_manure_separator = mocker.MagicMock()
    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_separator.daily_update.return_value = mock_manure_separator_daily_output
    if is_manure_separator_present:
        manure_manager.manure_separators[pen_id] = mock_manure_separator
    else:
        manure_manager.manure_separators[pen_id] = None

    mock_manure_treatment = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_accumulated_output = mocker.MagicMock()

    mock_manure_treatment.daily_update.return_value = mock_manure_treatment_daily_output
    mock_manure_treatment.accumulated_output = mock_manure_treatment_accumulated_output
    manure_manager.manure_treatments[pen_id] = mock_manure_treatment

    # Act
    (
        manure_separator_daily_output,
        manure_treatment_daily_output,
        manure_treatment_accumulated_output,
    ) = manure_manager._handle_daily_update_for_simple_manure_treatment(
        simulation_day=simulation_day,
        pen=mock_manure_manager_pen,
        manure_handler_daily_output=mock_manure_handler_daily_output,
        reception_pit_daily_output=mock_reception_pit_daily_output,
    )

    # Assert
    if is_manure_separator_present:
        mock_manure_separator.daily_update.assert_called_once_with(
            manure_separator_daily_input=mock_reception_pit_daily_output,
        )
        assert manure_separator_daily_output == mock_manure_separator_daily_output
        mock_manure_treatment.daily_update.assert_called_once_with(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            manure_treatment_daily_input=mock_manure_separator_daily_output,
            pen=mock_manure_manager_pen,
            sim_day=simulation_day,
        )
    else:
        assert manure_separator_daily_output is None
        mock_manure_treatment.daily_update.assert_called_once_with(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            manure_treatment_daily_input=mock_reception_pit_daily_output,
            pen=mock_manure_manager_pen,
            sim_day=simulation_day,
        )
    assert manure_treatment_daily_output == mock_manure_treatment_daily_output
    assert manure_treatment_accumulated_output == mock_manure_treatment_accumulated_output


def test_handle_update_for_compound_anaerobic_manure_treatment(
    mocker: MockFixture,
) -> None:
    """
    Unit test for _handle_daily_update_for_compound_anaerobic_manure_treatment() in manure_manager.py.

    This test verifies the daily update functionality for a compound anaerobic manure treatment
    process. It checks for the returned daily and accumulated outputs from the anaerobic
    digestion process, manure separator, and overall manure treatment.

    """
    # Arrange
    simulation_day = 1
    mock_manure_manager_pen = mocker.MagicMock()
    mock_manure_manager_pen.id = pen_id = 1
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_reception_pit_daily_output = mocker.MagicMock()

    mock_animal_manager = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()

    mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager.__init__",
        return_value=None,
    )
    manure_manager = ManureManager(
        animal_manager=mock_animal_manager,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )
    mock_manure_separator = mocker.MagicMock()
    manure_manager.manure_separators = {pen_id: mock_manure_separator}

    mock_manure_separator_after_digestion = mocker.MagicMock()
    manure_manager.manure_separators_after_digestion = {pen_id: mock_manure_separator_after_digestion}

    mock_manure_treatment = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_accumulated_output = mocker.MagicMock()

    mock_manure_treatment.daily_update.return_value = mock_manure_treatment_daily_output
    mock_manure_treatment.accumulated_output = mock_manure_treatment_accumulated_output

    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_manure_treatment.anaerobic_digestion_daily_output = mock_anaerobic_digestion_daily_output

    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_separator.daily_update.return_value = mock_manure_separator_daily_output

    mock_manure_separator_after_digestion_daily_output = mocker.MagicMock()
    mock_manure_treatment.manure_separator_after_digestion_daily_output = (
        mock_manure_separator_after_digestion_daily_output
    )

    manure_manager.manure_treatments = {pen_id: mock_manure_treatment}

    # Act
    (
        anaerobic_digestion_daily_output,
        manure_separator_daily_output,
        manure_separator_after_digestion_daily_output,
        manure_treatment_daily_output,
        manure_treatment_accumulated_output,
    ) = manure_manager._handle_daily_update_for_compound_anaerobic_manure_treatment(
        simulation_day=simulation_day,
        pen=mock_manure_manager_pen,
        manure_handler_daily_output=mock_manure_handler_daily_output,
        reception_pit_daily_output=mock_reception_pit_daily_output,
    )

    # Assert
    mock_manure_treatment.daily_update.assert_called_once_with(
        manure_handler_daily_output=mock_manure_handler_daily_output,
        manure_treatment_daily_input=mock_manure_separator_daily_output,
        pen=mock_manure_manager_pen,
        sim_day=simulation_day,
        manure_separator=mock_manure_separator,
        manure_separator_after_digestion=mock_manure_separator_after_digestion,
    )
    assert manure_treatment_daily_output == mock_manure_treatment_daily_output
    assert anaerobic_digestion_daily_output == mock_anaerobic_digestion_daily_output
    assert manure_separator_daily_output == mock_manure_separator_daily_output
    assert manure_separator_after_digestion_daily_output == mock_manure_separator_after_digestion_daily_output
    assert manure_treatment_accumulated_output == mock_manure_treatment_accumulated_output


@pytest.mark.parametrize(
    "is_compound_anaerobic_manure_treatment",
    [
        True,
        False,
    ],
)
def test_pen_daily_update_for_separator_and_treatment(
    is_compound_anaerobic_manure_treatment: bool, mocker: MockFixture
) -> None:
    """
    Unit test for _pen_daily_update_for_separator_and_treatment() in manure_manager.py.

    This test checks whether the daily updates for the manure separator and treatment are correctly
    executed depending on the manure treatment type (compound anaerobic or simple). It verifies the
    correct execution of either '_handle_daily_update_for_compound_anaerobic_manure_treatment' or
    '_handle_daily_update_for_simple_manure_treatment', based on the manure treatment type.

    """
    # Arrange
    simulation_day = 1
    mock_manure_manager_pen = mocker.MagicMock()
    mock_manure_manager_pen.manure_treatment = manure_treatment = "test_manure_treatment"
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_reception_pit_daily_output = mocker.MagicMock()

    patch_for_is_compound_anaerobic_manure_treatment = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager._is_compound_anaerobic_manure_treatment",
        return_value=is_compound_anaerobic_manure_treatment,
    )

    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_separator_daily_output_2 = mocker.MagicMock()
    mock_manure_separator_after_digestion_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output_2 = mocker.MagicMock()
    mock_manure_treatment_accumulated_output = mocker.MagicMock()
    mock_manure_treatment_accumulated_output_2 = mocker.MagicMock()

    patch_for_handle_daily_update_for_compound_anaerobic_manure_treatment = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager."
        "_handle_daily_update_for_compound_anaerobic_manure_treatment",
        return_value=(
            mock_anaerobic_digestion_daily_output,
            mock_manure_separator_daily_output,
            mock_manure_separator_after_digestion_daily_output,
            mock_manure_treatment_daily_output,
            mock_manure_treatment_accumulated_output,
        ),
    )

    patch_for_handle_daily_update_for_simple_manure_treatment = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager." "_handle_daily_update_for_simple_manure_treatment",
        return_value=(
            mock_manure_separator_daily_output_2,
            mock_manure_treatment_daily_output_2,
            mock_manure_treatment_accumulated_output_2,
        ),
    )

    mock_animal_manager = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()
    mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager.__init__",
        return_value=None,
    )
    manure_manager = ManureManager(
        animal_manager=mock_animal_manager,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )

    # Act
    (
        anaerobic_digestion_daily_output,
        manure_separator_daily_output,
        manure_separator_after_digestion_daily_output,
        manure_treatment_daily_output,
        manure_treatment_accumulated_output,
    ) = manure_manager._pen_daily_update_for_separator_and_treatment(
        simulation_day=simulation_day,
        pen=mock_manure_manager_pen,
        manure_handler_daily_output=mock_manure_handler_daily_output,
        reception_pit_daily_output=mock_reception_pit_daily_output,
    )

    # Assert
    patch_for_is_compound_anaerobic_manure_treatment.assert_called_once_with(manure_treatment)
    if is_compound_anaerobic_manure_treatment:
        patch_for_handle_daily_update_for_compound_anaerobic_manure_treatment.assert_called_once_with(
            simulation_day=simulation_day,
            pen=mock_manure_manager_pen,
            manure_handler_daily_output=mock_manure_handler_daily_output,
            reception_pit_daily_output=mock_reception_pit_daily_output,
        )
        assert anaerobic_digestion_daily_output == mock_anaerobic_digestion_daily_output
        assert manure_separator_daily_output == mock_manure_separator_daily_output
        assert manure_separator_after_digestion_daily_output == mock_manure_separator_after_digestion_daily_output
        assert manure_treatment_daily_output == mock_manure_treatment_daily_output
        assert manure_treatment_accumulated_output == mock_manure_treatment_accumulated_output
    else:
        patch_for_handle_daily_update_for_simple_manure_treatment.assert_called_once_with(
            simulation_day=simulation_day,
            pen=mock_manure_manager_pen,
            manure_handler_daily_output=mock_manure_handler_daily_output,
            reception_pit_daily_output=mock_reception_pit_daily_output,
        )
        assert anaerobic_digestion_daily_output is None
        assert manure_separator_daily_output == mock_manure_separator_daily_output_2
        assert manure_treatment_daily_output == mock_manure_treatment_daily_output_2
        assert manure_treatment_accumulated_output == mock_manure_treatment_accumulated_output_2


def test_pen_daily_update(mocker: MockFixture) -> None:
    """
    Unit test for the _pen_daily_update() method in ManureManager class found in manure_manager.py.

    This test verifies that the _pen_daily_update() method correctly performs the daily
    updates for a given pen. Specifically, it checks that the method creates a ManureManagerPen instance,
    calls the daily_update() method on manure_handler and reception_pit, and calls the
    _pen_daily_update_for_separator_and_treatment() method.

    """
    # Arrange
    simulation_day = 1
    mock_pen = mocker.MagicMock()
    mock_manure_manager_pen = mocker.MagicMock()
    mock_manure_manager_pen.id = pen_id = 1
    mock_manure_manager_pen.manure = mock_pen_manure = mocker.MagicMock()
    patch_for_manure_manager_pen_init = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManagerPen",
        return_value=mock_manure_manager_pen,
    )

    mock_bedding = mocker.MagicMock()

    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_manure_handler = mocker.MagicMock()
    mock_manure_handler.daily_update.return_value = mock_manure_handler_daily_output

    mock_reception_pit_daily_output = mocker.MagicMock()
    mock_reception_pit = mocker.MagicMock()
    mock_reception_pit.daily_update.return_value = mock_reception_pit_daily_output

    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_separator_after_digestion_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_accumulated_output = mocker.MagicMock()
    patch_for_pen_daily_update_for_separator_and_treatment = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager." "_pen_daily_update_for_separator_and_treatment",
        return_value=(
            mock_anaerobic_digestion_daily_output,
            mock_manure_separator_daily_output,
            mock_manure_separator_after_digestion_daily_output,
            mock_manure_treatment_daily_output,
            mock_manure_treatment_accumulated_output,
        ),
    )

    expected_daily_output_data = {
        "simulation_day": simulation_day,
        "pen": mock_manure_manager_pen,
        "animal_manure_excretions": mock_pen_manure,
        "manure_handler_daily_output": mock_manure_handler_daily_output,
        "reception_pit_daily_output": mock_reception_pit_daily_output,
        "manure_separator_daily_output": mock_manure_separator_daily_output,
        "manure_separator_after_digestion_daily_output": mock_manure_separator_after_digestion_daily_output,
        "manure_treatment_daily_output": mock_manure_treatment_daily_output,
        "manure_treatment_accumulated_output": mock_manure_treatment_accumulated_output,
        "anaerobic_digestion_daily_output": mock_anaerobic_digestion_daily_output,
    }

    mock_animal_manager = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()
    mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager.__init__",
        return_value=None,
    )
    manure_manager = ManureManager(
        animal_manager=mock_animal_manager,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )
    manure_manager.beddings = {pen_id: mock_bedding}
    manure_manager.manure_handlers = {pen_id: mock_manure_handler}
    manure_manager.reception_pits = {pen_id: mock_reception_pit}
    manure_manager._daily_output_per_pen = []

    patch_for_add_manure_nutrients = mocker.patch.object(manure_manager, "_add_manure_nutrients", return_value=None)

    mocker.patch.object(ManureModuleOutputManagerHelper, "add_dataclass_object", return_value=None)

    # Act
    manure_manager._pen_daily_update(
        simulation_day=simulation_day,
        pen=mock_pen,
    )

    # Assert
    patch_for_manure_manager_pen_init.assert_called_once_with(mock_pen)
    mock_manure_handler.daily_update.assert_called_once_with(
        pen=mock_manure_manager_pen,
        bedding=mock_bedding,
        sim_day=simulation_day,
    )
    mock_reception_pit.daily_update.assert_called_once_with(
        manure_handler_daily_output=mock_manure_handler_daily_output,
        pen=mock_manure_manager_pen,
        bedding=mock_bedding,
    )
    patch_for_pen_daily_update_for_separator_and_treatment.assert_called_once_with(
        simulation_day=simulation_day,
        pen=mock_manure_manager_pen,
        manure_handler_daily_output=mock_manure_handler_daily_output,
        reception_pit_daily_output=mock_reception_pit_daily_output,
    )
    assert manure_manager._daily_output_per_pen == [expected_daily_output_data]
    patch_for_add_manure_nutrients.assert_called_once_with(mock_manure_manager_pen, mock_manure_treatment_daily_output)


def test_manure_manager_daily_update(mocker: MockFixture) -> None:
    """
    Unit test for the daily_update() method in ManureManager class found in manure_manager.py.

    This test verifies that the daily_update() method correctly performs the daily updates for all pens
    by calling the _pen_daily_update() method for each pen returned by the AnimalManager.

    """
    # Arrange
    mock_animal_manager = mocker.MagicMock()
    mock_animal_manager.simulation_day = simulation_day = 1
    num_pens = 3
    mock_all_pens = [
        PenManureData(
            id=1,
            num_animals=10,
            num_lactating_cows=1,
            classes_in_pen=set(),
            animal_combination=AnimalCombination.CALF,
            pen_type="",
            housing_type="",
            bedding_type="",
            manure_handler="",
            manure_separator="",
            manure_treatment="",
            manure_separator_after_digestion="",
            num_stalls=15,
            manure=AnimalManureExcretions(total_solids=10.0),
        )
        for _ in range(num_pens)
    ]
    mock_all_pens[-1]["num_animals"], mock_all_pens[-1]["manure"] = 0, AnimalManureExcretions(total_solids=0.0)
    mock_animal_manager.all_pens = mock_all_pens

    mock_animal_manager_init = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()
    mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager.__init__",
        return_value=None,
    )
    manure_manager = ManureManager(
        animal_manager=mock_animal_manager_init,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )
    patch_for_configure_manure_manager_components = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager." "configure_manure_manager_components",
        return_value=None,
    )
    patch_for_pen_daily_update = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager." "_pen_daily_update",
        return_value=None,
    )
    manure_manager.time = mock_time
    manure_manager._manure_nutrient_manager = mocker.MagicMock()
    mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureModuleOutputManagerHelper.add_dataclass_object",
        return_value=None,
    )
    mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager.configure_manure_manager_components",
        return_value=None,
    )
    manure_manager.manure_treatments = mocker.MagicMock()

    # Act
    manure_manager.daily_update(mock_animal_manager.all_pens, mock_animal_manager.simulation_day)

    # Assert
    patch_for_configure_manure_manager_components.assert_called_once
    assert patch_for_pen_daily_update.call_count == num_pens - 1
    assert patch_for_pen_daily_update.call_args_list == [mocker.call(simulation_day, pen) for pen in mock_all_pens[:-1]]


@pytest.mark.parametrize(
    "treatment_type, expected_manure_type",
    [
        (ManureTreatmentType.SLURRY_STORAGE_OUTDOOR, ManureType.LIQUID),
        (ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_LAGOON, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_DIGESTION, ManureType.LIQUID),
        (
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SEPARATOR,
            ManureType.LIQUID,
        ),
        (ManureTreatmentType.COMPOST_BEDDED_PACK_BARN, ManureType.SOLID),
    ],
)
def test_get_manure_type(treatment_type: ManureTreatmentType, expected_manure_type: ManureType) -> None:
    """
    Unit test for the _get_manure_type method of the ManureManager class in manure_manager.py.

    This test checks whether the _get_manure_type method returns the correct ManureType
    for the provided ManureTreatmentType.

    """
    # Assert
    assert ManureManager._get_manure_type(treatment_type) == expected_manure_type


@pytest.mark.parametrize(
    "manure_type, expected_density",
    [
        (ManureType.LIQUID, ManureConstants.LIQUID_MANURE_DENSITY),
        (ManureType.SOLID, ManureConstants.SOLID_MANURE_DENSITY),
    ],
)
def test_get_manure_density_by_type(manure_type: ManureType, expected_density: float) -> None:
    """
    Unit test for _get_manure_density_by_type() method in the ManureManager class.
    """

    # Assert
    assert ManureManager._get_manure_density_by_type(manure_type) == expected_density


def test_add_manure_nutrients(mocker: MockFixture) -> None:
    """
    Unit test for the _add_manure_nutrients method of the ManureManager class in manure_manager.py.

    This test checks whether the _add_manure_nutrients method adds the correct amount of nutrients
    to the ManureNutrientManager for a mock pen with the provided ManureTreatmentType.

    """
    # Arrange
    mocker.patch("RUFAS.routines.manure.manure_manager.ManureManager.__init__", return_value=None)
    manure_manager = ManureManager(
        animal_manager=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_manager_config=mocker.MagicMock(),
    )

    mock_pen = mocker.MagicMock()

    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output.liquid_manure_nitrogen = 1.0
    mock_manure_treatment_daily_output.liquid_manure_phosphorus = 2.0
    mock_manure_treatment_daily_output.liquid_manure_potassium = 3.0
    mock_manure_treatment_daily_output.liquid_manure_total_solids = 4.0
    mock_manure_treatment_daily_output.liquid_manure_daily_volume = 5.0

    mock_manure_treatment_daily_output.sludge_manure_nitrogen = 6.0
    mock_manure_treatment_daily_output.sludge_manure_phosphorus = 7.0
    mock_manure_treatment_daily_output.sludge_manure_potassium = 8.0
    mock_manure_treatment_daily_output.sludge_manure_total_solids = 9.0
    mock_manure_treatment_daily_output.sludge_manure_daily_volume = 10.0

    mock_manure_treatment_daily_output.solid_manure_nitrogen = 11.0
    mock_manure_treatment_daily_output.solid_manure_phosphorus = 12.0
    mock_manure_treatment_daily_output.solid_manure_potassium = 13.0
    mock_manure_treatment_daily_output.solid_manure_total_solids = 14.0
    mock_manure_treatment_daily_output.solid_manure_daily_mass = 15.0

    mock_manure_nutrient_manager = mocker.MagicMock()
    manure_manager._manure_nutrient_manager = mock_manure_nutrient_manager

    mock_manure_density = 1000
    patch_get_manure_density = mocker.patch.object(
        manure_manager, "_get_manure_density_by_type", return_value=mock_manure_density
    )
    mock_manure_nutrients = mocker.MagicMock()
    patch_manure_nutrients_init = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureNutrients",
        return_value=mock_manure_nutrients,
    )

    # Act
    manure_manager._add_manure_nutrients(mock_pen, mock_manure_treatment_daily_output)

    # Assert
    patch_get_manure_density.assert_has_calls(
        [
            mocker.call(ManureType.LIQUID),
        ]
    )
    mock_manure_nutrient_manager.add_nutrients.assert_called_with(mock_manure_nutrients)
    expected_calls = [
        call(
            nitrogen=max(mock_manure_treatment_daily_output.liquid_manure_nitrogen, 0.0),
            phosphorus=max(mock_manure_treatment_daily_output.liquid_manure_phosphorus, 0.0),
            potassium=max(mock_manure_treatment_daily_output.liquid_manure_potassium, 0.0),
            dry_matter=max(mock_manure_treatment_daily_output.liquid_manure_total_solids, 0.0),
            total_manure_mass=max(
                mock_manure_treatment_daily_output.liquid_manure_daily_volume * mock_manure_density,
                0.0,
            ),
            manure_type=ManureType.LIQUID,
        ),
        call(
            nitrogen=max(mock_manure_treatment_daily_output.solid_manure_nitrogen, 0.0),
            phosphorus=max(mock_manure_treatment_daily_output.solid_manure_phosphorus, 0.0),
            potassium=max(mock_manure_treatment_daily_output.solid_manure_potassium, 0.0),
            dry_matter=max(mock_manure_treatment_daily_output.solid_manure_total_solids, 0.0),
            total_manure_mass=max(mock_manure_treatment_daily_output.solid_manure_daily_mass, 0.0),
            manure_type=ManureType.SOLID,
        ),
    ]
    patch_manure_nutrients_init.assert_has_calls(expected_calls)


@pytest.mark.parametrize("animals_simulated", [True, False])
@pytest.mark.parametrize("use_supplemental_manure", [True, False])
def test_request_nutrients(mocker: MockerFixture, animals_simulated: bool, use_supplemental_manure: bool) -> None:
    """
    Unit test for the updated request_nutrients method of the ManureManager class.
    """
    # Arrange
    mocker.patch("RUFAS.routines.manure.manure_manager.ManureManager.__init__", return_value=None)
    manure_manager = ManureManager(
        animal_manager=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_manager_config=mocker.MagicMock(),
        simulate_animals=animals_simulated,
    )
    manure_manager.simulate_animals = animals_simulated

    mock_manure_nutrient_manager = mocker.MagicMock()
    mock_field_manure_supplier = mocker.MagicMock()
    mock_output_manager = mocker.MagicMock()
    manure_manager._manure_nutrient_manager = mock_manure_nutrient_manager
    manure_manager._field_manure_supplier = mock_field_manure_supplier
    manure_manager.om = mock_output_manager
    mock_nutrient_request = mocker.MagicMock()
    mock_nutrient_request.use_supplemental_manure = use_supplemental_manure

    mock_request_result = NutrientRequestResults(nitrogen=10.0, phosphorus=5.0, total_manure_mass=50.0)
    mock_supplemental_result = NutrientRequestResults(nitrogen=5.0, phosphorus=2.5, total_manure_mass=25.0)

    mocker.patch.object(
        mock_manure_nutrient_manager,
        "request_nutrients",
        return_value=(mock_request_result, not use_supplemental_manure),
    )
    mocker.patch.object(
        mock_field_manure_supplier,
        "request_nutrients",
        return_value=mock_supplemental_result,
    )
    mocker.patch.object(manure_manager, "_calculate_supplemental_manure_needed", return_value=mocker.MagicMock())
    mocker.patch.object(manure_manager, "_record_manure_request_results")

    # Act
    actual_results = manure_manager.request_nutrients(mock_nutrient_request)

    # Assert
    if animals_simulated:
        mock_manure_nutrient_manager.request_nutrients.assert_called_once_with(mock_nutrient_request)
        manure_manager._record_manure_request_results.assert_any_call(mock_request_result, "on_farm_manure")
        if not use_supplemental_manure:
            assert actual_results == mock_request_result
        else:
            mock_output_manager.add_log.assert_called_once_with(
                "Supplemental manure needed",
                "Attempting to fulfill manure nutrient request shortfall with supplemental manure.",
                {"class": manure_manager.__class__.__name__, "function": manure_manager.request_nutrients.__name__},
            )
            manure_manager._calculate_supplemental_manure_needed.assert_called_once_with(
                mock_request_result, mock_nutrient_request
            )
            mock_field_manure_supplier.request_nutrients.assert_called_once()
            manure_manager._record_manure_request_results.assert_any_call(mock_supplemental_result, "off_farm_manure")
            combined_result = mock_request_result + mock_supplemental_result
            assert actual_results == combined_result
    else:
        mock_field_manure_supplier.request_nutrients.assert_called_once_with(mock_nutrient_request)
        assert actual_results == mock_supplemental_result


@pytest.mark.parametrize(
    "manure_request_results, expected_request_result_values, expected_log_called",
    [
        # Case 1: manure_request_results is None
        (
            None,
            {
                "dry_matter_mass": 0.0,
                "dry_matter_fraction": 0.0,
                "total_manure_mass": 0.0,
                "organic_nitrogen_fraction": 0.0,
                "inorganic_nitrogen_fraction": 0.0,
                "ammonium_nitrogen_fraction": 0.0,
                "organic_phosphorus_fraction": 0.0,
                "inorganic_phosphorus_fraction": 0.0,
                "nitrogen": 0.0,
                "phosphorus": 0.0,
                "request_julian_day": 150,
                "request_calendar_year": 2025,
            },
            True,
        ),
        # Case 2: manure_request_results has valid data
        (
            MagicMock(
                dry_matter=100.0,
                dry_matter_fraction=0.25,
                total_manure_mass=400.0,
                organic_nitrogen_fraction=0.15,
                inorganic_nitrogen_fraction=0.10,
                ammonium_nitrogen_fraction=0.05,
                organic_phosphorus_fraction=0.08,
                inorganic_phosphorus_fraction=0.02,
                nitrogen=50.0,
                phosphorus=10.0,
            ),
            {
                "dry_matter_mass": 100.0,
                "dry_matter_fraction": 0.25,
                "total_manure_mass": 400.0,
                "organic_nitrogen_fraction": 0.15,
                "inorganic_nitrogen_fraction": 0.10,
                "ammonium_nitrogen_fraction": 0.05,
                "organic_phosphorus_fraction": 0.08,
                "inorganic_phosphorus_fraction": 0.02,
                "nitrogen": 50.0,
                "phosphorus": 10.0,
                "request_julian_day": 150,
                "request_calendar_year": 2025,
            },
            False,
        ),
    ],
)
def test_record_manure_request_results_parametrized(
    mocker: MockerFixture,
    manure_request_results,
    expected_request_result_values,
    expected_log_called,
) -> None:
    """
    Parametrized unit test for the _record_manure_request_results method of the ManureManager class.
    """
    # Arrange
    manure_source = "on_farm_manure"
    mock_time = mocker.MagicMock()
    mock_time.current_julian_day = 150
    mock_time.current_calendar_year = 2025

    mocker.patch("RUFAS.routines.manure.manure_manager.ManureManager.__init__", return_value=None)
    manure_manager = ManureManager(
        animal_manager=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mock_time,
        manure_manager_config=mocker.MagicMock(),
        simulate_animals=True,
    )
    manure_manager.time = mock_time

    mock_output_manager = mocker.MagicMock()
    manure_manager.om = mock_output_manager

    # Act
    manure_manager._record_manure_request_results(manure_request_results, manure_source)

    # Assert
    if expected_log_called:
        mock_output_manager.add_log.assert_called_once_with(
            "Recording empty manure request result",
            "No manure available on farm to fulfill request.",
            {
                "class": "ManureManager",
                "function": "_record_manure_request_results",
                "units": {
                    "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS,
                    "dry_matter_fraction": MeasurementUnits.FRACTION,
                    "total_manure_mass": MeasurementUnits.KILOGRAMS,
                    "organic_nitrogen_fraction": MeasurementUnits.FRACTION,
                    "inorganic_nitrogen_fraction": MeasurementUnits.FRACTION,
                    "ammonium_nitrogen_fraction": MeasurementUnits.FRACTION,
                    "organic_phosphorus_fraction": MeasurementUnits.FRACTION,
                    "inorganic_phosphorus_fraction": MeasurementUnits.FRACTION,
                    "nitrogen": MeasurementUnits.KILOGRAMS,
                    "phosphorus": MeasurementUnits.KILOGRAMS,
                    "request_julian_day": MeasurementUnits.ORDINAL_DAY,
                    "request_calendar_year": MeasurementUnits.CALENDAR_YEAR,
                },
            },
        )
    else:
        mock_output_manager.add_log.assert_not_called()

    mock_output_manager.add_variable.assert_called_once()
    actual_manure_source, actual_request_result_values, actual_info_maps = mock_output_manager.add_variable.call_args[0]

    assert actual_manure_source == manure_source
    assert actual_request_result_values == expected_request_result_values

    expected_info_maps = {
        "class": "ManureManager",
        "function": "_record_manure_request_results",
        "units": {
            "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS,
            "dry_matter_fraction": MeasurementUnits.FRACTION,
            "total_manure_mass": MeasurementUnits.KILOGRAMS,
            "organic_nitrogen_fraction": MeasurementUnits.FRACTION,
            "inorganic_nitrogen_fraction": MeasurementUnits.FRACTION,
            "ammonium_nitrogen_fraction": MeasurementUnits.FRACTION,
            "organic_phosphorus_fraction": MeasurementUnits.FRACTION,
            "inorganic_phosphorus_fraction": MeasurementUnits.FRACTION,
            "nitrogen": MeasurementUnits.KILOGRAMS,
            "phosphorus": MeasurementUnits.KILOGRAMS,
            "request_julian_day": MeasurementUnits.ORDINAL_DAY,
            "request_calendar_year": MeasurementUnits.CALENDAR_YEAR,
        },
    }
    assert actual_info_maps == expected_info_maps


@pytest.mark.parametrize(
    "on_farm_manure, nutrient_request, expected_result",
    [
        # Scenario: No supplemental manure needed (on-farm manure fully satisfies the request)
        (
            NutrientRequestResults(
                nitrogen=10,
                phosphorus=5,
                total_manure_mass=15,
                organic_nitrogen_fraction=0.6,
                inorganic_nitrogen_fraction=0.4,
                ammonium_nitrogen_fraction=0.3,
                organic_phosphorus_fraction=0.5,
                inorganic_phosphorus_fraction=0.5,
                dry_matter=3,
                dry_matter_fraction=0.2,
            ),
            NutrientRequest(
                nitrogen=8,
                phosphorus=4,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=0.0,
                phosphorus=0.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
        # Scenario: Partial supplemental manure needed (on-farm manure partially satisfies the request)
        (
            NutrientRequestResults(
                nitrogen=5,
                phosphorus=2,
                total_manure_mass=10,
                organic_nitrogen_fraction=0.7,
                inorganic_nitrogen_fraction=0.3,
                ammonium_nitrogen_fraction=0.5,
                organic_phosphorus_fraction=0.6,
                inorganic_phosphorus_fraction=0.4,
                dry_matter=2,
                dry_matter_fraction=0.1,
            ),
            NutrientRequest(
                nitrogen=8,
                phosphorus=5,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=3.0,
                phosphorus=3.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
        # Scenario: All supplemental manure needed (on-farm manure provides nothing)
        (
            None,
            NutrientRequest(
                nitrogen=10,
                phosphorus=6,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=False,
            ),
            NutrientRequest(
                nitrogen=10.0,
                phosphorus=6.0,
                manure_type=ManureType.LIQUID,
                use_supplemental_manure=True,
            ),
        ),
    ],
)
def test_calculate_supplemental_manure_needed(
    on_farm_manure: NutrientRequestResults,
    nutrient_request: NutrientRequest,
    expected_result: NutrientRequest,
    mocker: MockFixture,
) -> None:
    """
    Unit test for the _calculate_supplemental_manure_needed static method.
    """
    # Arrange
    mocker.patch("RUFAS.routines.manure.manure_manager.ManureManager.__init__", return_value=None)
    manure_manager = ManureManager(
        animal_manager=mocker.MagicMock(),
        weather=mocker.MagicMock(),
        time=mocker.MagicMock(),
        manure_manager_config=mocker.MagicMock(),
        simulate_animals=True,
    )
    # Act
    actual_result = manure_manager._calculate_supplemental_manure_needed(on_farm_manure, nutrient_request)

    # Assert
    assert math.isclose(actual_result.nitrogen, expected_result.nitrogen, abs_tol=1e-6)
    assert math.isclose(actual_result.phosphorus, expected_result.phosphorus, abs_tol=1e-6)
    assert actual_result.manure_type == expected_result.manure_type
    assert actual_result.use_supplemental_manure == expected_result.use_supplemental_manure
