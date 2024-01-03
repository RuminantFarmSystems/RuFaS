from mock import call
import pytest
from pytest_mock import MockFixture

from RUFAS.routines.manure.IO_helpers.manure_module_output_manager_helper import ManureModuleOutputManagerHelper
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_manager import ManureManager
from RUFAS.routines.manure.manure_manager import simulate_daily_manure_manager
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.routines.manure.manure_treatments.manure_types import ManureType


def test_simulate_daily_manure_manager(mocker: MockFixture) -> None:
    """Unit test for simulate_daily_manure_manager() in manure_manager.py"""
    # Arrange
    mock_manure_manager = mocker.MagicMock()
    mock_manure_manager.daily_update.return_value = None
    mock_animal_manager = mocker.MagicMock()

    # Act
    simulate_daily_manure_manager(mock_manure_manager, mock_animal_manager)

    # Assert
    mock_manure_manager.daily_update.assert_called_once_with(mock_animal_manager)


def test_manure_manager_init(mocker: MockFixture) -> None:
    """Unit test for __init__() of ManureManager in manure_manager.py"""
    # Arrange
    mock_animal_manager = mocker.MagicMock()
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
    patch_for_configure_manure_manager_components = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManager."
        "_configure_manure_manager_components",
        return_value=None,
    )

    # Act
    manure_manager = ManureManager(
        animal_manager=mock_animal_manager,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )

    # Assert
    assert manure_manager.beddings == {}
    assert manure_manager.manure_handlers == {}
    assert manure_manager.reception_pits == {}
    assert manure_manager.manure_separators == {}
    assert manure_manager.manure_treatments == {}
    assert manure_manager.weather == mock_weather
    assert manure_manager.time == mock_time

    patch_for_manure_manager_config_handler.assert_called_once_with(mock_manure_manager_config)
    assert manure_manager.manure_manager_config_handler == mock_manure_manager_config_handler
    patch_for_manure_nutrient_manager.assert_called_once()
    patch_for_configure_manure_manager_components.assert_called_once_with(mock_animal_manager)


def test_data_property(mocker: MockFixture) -> None:
    """
    Unit test for `data` property of ManureManager in manure_manager.py

    This test verifies that the 'data' property correctly returns the '_daily_output_per_pen' value attribute
    of the ManureManager object.

    """
    # Arrange
    mock_animal_manager = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()

    mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.__init__',
        return_value=None,
    )

    manure_manager = ManureManager(
        animal_manager=mock_animal_manager,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )

    mock_daily_output_per_pen = mocker.MagicMock()
    manure_manager._daily_output_per_pen = mock_daily_output_per_pen

    # Act
    actual_daily_output_per_pen = manure_manager.data

    # Assert
    assert mock_daily_output_per_pen == actual_daily_output_per_pen


@pytest.mark.parametrize(
    'manure_separator',
    ['none',
     'test_manure_separator',
     ])
def test_configure_manure_manager_components(manure_separator: str,
                                             mocker: MockFixture) -> None:
    """Unit test for _configure_manure_manager_components() in manure_manager.py"""
    # Arrange
    mock_animal_manager = mocker.MagicMock()
    mock_pen = mocker.MagicMock()
    mock_all_pens = [mock_pen]
    mock_animal_manager.all_pens = mock_all_pens

    mock_manure_manager_pen = mocker.MagicMock()
    mock_manure_manager_pen.id = pen_id = 1
    mock_manure_manager_pen.bedding_type = bedding_type = 'test_bedding_type'
    mock_manure_manager_pen.manure_handler = manure_handler = 'test_manure_handler'
    mock_manure_manager_pen.manure_separator = manure_separator
    mock_manure_manager_pen.manure_treatment = manure_treatment = 'test_manure_treatment'
    patch_for_manure_manager_pen_init = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManagerPen',
        return_value=mock_manure_manager_pen,
    )

    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()

    mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.__init__',
        return_value=None,
    )

    manure_manager = ManureManager(
        animal_manager=mock_animal_manager,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )

    mock_manure_manager_config_handler = mocker.MagicMock()

    mock_custom_bedding_config = mocker.MagicMock()
    mock_manure_manager_config_handler.get_custom_bedding_config.return_value = mock_custom_bedding_config
    mock_bedding = mocker.MagicMock()
    patch_for_bedding_factory_get_instance = mocker.patch(
        'RUFAS.routines.manure.manure_manager.BeddingFactory.get_instance',
        return_value=mock_bedding,
    )

    mock_custom_manure_handler_config = mocker.MagicMock()
    mock_manure_manager_config_handler.get_custom_manure_handler_config.return_value = \
        mock_custom_manure_handler_config
    mock_manure_handler = mocker.MagicMock()
    patch_for_manure_handler_factory_get_instance = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureHandlerFactory.get_instance',
        return_value=mock_manure_handler,
    )

    mock_reception_pit = mocker.MagicMock()
    patch_for_reception_pit_init = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ReceptionPit',
        return_value=mock_reception_pit,
    )

    mock_custom_manure_separator_config = mocker.MagicMock()
    mock_manure_manager_config_handler.get_custom_manure_separator_config.return_value = \
        mock_custom_manure_separator_config
    mock_manure_separator = mocker.MagicMock()
    patch_for_manure_separator_factory_get_instance = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureSeparatorFactory.get_instance',
        return_value=mock_manure_separator,
    )

    mock_custom_manure_treatment_config = mocker.MagicMock()
    mock_manure_manager_config_handler.get_custom_manure_treatment_config.return_value = \
        mock_custom_manure_treatment_config
    mock_manure_treatment = mocker.MagicMock()
    patch_for_manure_treatment_factory_get_instance = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureTreatmentFactory.get_instance',
        return_value=mock_manure_treatment,
    )

    manure_manager.manure_manager_config_handler = mock_manure_manager_config_handler
    manure_manager.beddings = {}
    manure_manager.manure_handlers = {}
    manure_manager.reception_pits = {}
    manure_manager.manure_separators = {}
    manure_manager.manure_treatments = {}
    manure_manager.weather = mock_weather
    manure_manager.time = mock_time

    # Act
    manure_manager._configure_manure_manager_components(mock_animal_manager)

    # Assert
    patch_for_manure_manager_pen_init.assert_called_once_with(mock_pen)

    mock_manure_manager_config_handler.get_custom_bedding_config.assert_called_once_with(bedding_type)
    patch_for_bedding_factory_get_instance.assert_called_once_with(
        bedding_type_name=bedding_type,
        custom_bedding_config=mock_custom_bedding_config,
    )
    assert manure_manager.beddings[pen_id] == mock_bedding

    mock_manure_manager_config_handler.get_custom_manure_handler_config.assert_called_once_with(manure_handler)
    patch_for_manure_handler_factory_get_instance.assert_called_once_with(
        manure_handler_type_name=manure_handler,
        weather=mock_weather,
        time=mock_time,
        custom_manure_handler_config=mock_custom_manure_handler_config,
    )
    assert manure_manager.manure_handlers[pen_id] == mock_manure_handler

    patch_for_reception_pit_init.assert_called_once()
    assert manure_manager.reception_pits[pen_id] == mock_reception_pit

    if manure_separator == 'none':
        mock_manure_manager_config_handler.get_custom_manure_separator_config.assert_not_called()
        patch_for_manure_separator_factory_get_instance.assert_not_called()
        assert manure_manager.manure_separators[pen_id] is None
    else:
        mock_manure_manager_config_handler.get_custom_manure_separator_config \
            .assert_called_once_with(manure_separator)
        patch_for_manure_separator_factory_get_instance.assert_called_once_with(
            manure_separator_type_name=manure_separator,
            custom_manure_separator_config=mock_custom_manure_separator_config,
        )
        assert manure_manager.manure_separators[pen_id] == mock_manure_separator

    mock_manure_manager_config_handler.get_custom_manure_treatment_config.assert_called_once_with(manure_treatment)
    patch_for_manure_treatment_factory_get_instance.assert_called_once_with(
        manure_treatment_type_name=manure_treatment,
        weather=mock_weather,
        time=mock_time,
        custom_manure_treatment_config=mock_custom_manure_treatment_config
    )
    assert manure_manager.manure_treatments[pen_id] == mock_manure_treatment


@pytest.mark.parametrize(
    'manure_treatment_type, is_compound_anaerobic_treatment',
    [
        (ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR, False),
        (ManureTreatmentType.SLURRY_STORAGE_OUTDOOR, False),
        (ManureTreatmentType.ANAEROBIC_LAGOON, False),
        (ManureTreatmentType.ANAEROBIC_DIGESTION, False),
        (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON, True),
        (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT, True),
    ]
)
def test_is_compound_anaerobic_manure_treatment(manure_treatment_type: ManureTreatmentType,
                                                is_compound_anaerobic_treatment: bool,
                                                mocker: MockFixture) -> None:
    """Unit test for _is_compound_anaerobic_manure_treatment() in manure_manager.py."""
    # Arrange
    manure_treatment_name = 'test_manure_treatment'
    patch_for_manure_treatment_type_get_type = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureTreatmentType.get_type',
        return_value=manure_treatment_type,
    )

    # Act
    result = ManureManager._is_compound_anaerobic_manure_treatment(manure_treatment_name)

    # Assert
    patch_for_manure_treatment_type_get_type.assert_called_once_with(manure_treatment_name)
    assert result == is_compound_anaerobic_treatment


@pytest.mark.parametrize(
    'is_manure_separator_present',
    [
        True,
        False,
    ]
)
def test_handle_daily_update_for_simple_manure_treatment(is_manure_separator_present: bool,
                                                         mocker: MockFixture) -> None:
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
        'RUFAS.routines.manure.manure_manager.ManureManager.__init__',
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
    manure_separator_daily_output, manure_treatment_daily_output, manure_treatment_accumulated_output = \
        manure_manager._handle_daily_update_for_simple_manure_treatment(
            simulation_day=simulation_day,
            pen=mock_manure_manager_pen,
            manure_handler_daily_output=mock_manure_handler_daily_output,
            reception_pit_daily_output=mock_reception_pit_daily_output
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
            sim_day=simulation_day
        )
    else:
        assert manure_separator_daily_output is None
        mock_manure_treatment.daily_update.assert_called_once_with(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            manure_treatment_daily_input=mock_reception_pit_daily_output,
            pen=mock_manure_manager_pen,
            sim_day=simulation_day
        )
    assert manure_treatment_daily_output == mock_manure_treatment_daily_output
    assert manure_treatment_accumulated_output == mock_manure_treatment_accumulated_output


def test_handle_update_for_compound_anaerobic_manure_treatment(mocker: MockFixture) -> None:
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
        'RUFAS.routines.manure.manure_manager.ManureManager.__init__',
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

    mock_manure_treatment = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_accumulated_output = mocker.MagicMock()

    mock_manure_treatment.daily_update.return_value = mock_manure_treatment_daily_output
    mock_manure_treatment.accumulated_output = mock_manure_treatment_accumulated_output

    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_manure_treatment.anaerobic_digestion_daily_output = mock_anaerobic_digestion_daily_output

    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_treatment.manure_separator_daily_output = mock_manure_separator_daily_output

    manure_manager.manure_treatments = {pen_id: mock_manure_treatment}

    # Act
    anaerobic_digestion_daily_output, manure_separator_daily_output, \
        manure_treatment_daily_output, manure_treatment_accumulated_output = \
        manure_manager._handle_daily_update_for_compound_anaerobic_manure_treatment(
            simulation_day=simulation_day,
            pen=mock_manure_manager_pen,
            manure_handler_daily_output=mock_manure_handler_daily_output,
            reception_pit_daily_output=mock_reception_pit_daily_output
        )

    # Assert
    mock_manure_treatment.daily_update.assert_called_once_with(
        manure_handler_daily_output=mock_manure_handler_daily_output,
        manure_treatment_daily_input=mock_reception_pit_daily_output,
        pen=mock_manure_manager_pen,
        sim_day=simulation_day,
        manure_separator=mock_manure_separator,
    )
    assert manure_treatment_daily_output == mock_manure_treatment_daily_output
    assert anaerobic_digestion_daily_output == mock_anaerobic_digestion_daily_output
    assert manure_separator_daily_output == mock_manure_separator_daily_output
    assert manure_treatment_accumulated_output == mock_manure_treatment_accumulated_output


@pytest.mark.parametrize(
    'is_compound_anaerobic_manure_treatment',
    [
        True,
        False,
    ]
)
def test_pen_daily_update_for_separator_and_treatment(is_compound_anaerobic_manure_treatment: bool,
                                                      mocker: MockFixture) -> None:
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
    mock_manure_manager_pen.manure_treatment = manure_treatment = 'test_manure_treatment'
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_reception_pit_daily_output = mocker.MagicMock()

    patch_for_is_compound_anaerobic_manure_treatment = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager._is_compound_anaerobic_manure_treatment',
        return_value=is_compound_anaerobic_manure_treatment,
    )

    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_separator_daily_output_2 = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output_2 = mocker.MagicMock()
    mock_manure_treatment_accumulated_output = mocker.MagicMock()
    mock_manure_treatment_accumulated_output_2 = mocker.MagicMock()

    patch_for_handle_daily_update_for_compound_anaerobic_manure_treatment = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.'
        '_handle_daily_update_for_compound_anaerobic_manure_treatment',
        return_value=(mock_anaerobic_digestion_daily_output,
                      mock_manure_separator_daily_output,
                      mock_manure_treatment_daily_output,
                      mock_manure_treatment_accumulated_output),
    )

    patch_for_handle_daily_update_for_simple_manure_treatment = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.'
        '_handle_daily_update_for_simple_manure_treatment',
        return_value=(mock_manure_separator_daily_output_2,
                      mock_manure_treatment_daily_output_2,
                      mock_manure_treatment_accumulated_output_2),
    )

    mock_animal_manager = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()
    mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.__init__',
        return_value=None,
    )
    manure_manager = ManureManager(
        animal_manager=mock_animal_manager,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )

    # Act
    anaerobic_digestion_daily_output, manure_separator_daily_output, \
        manure_treatment_daily_output, manure_treatment_accumulated_output = \
        manure_manager._pen_daily_update_for_separator_and_treatment(
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
        'RUFAS.routines.manure.manure_manager.ManureManagerPen',
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
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_accumulated_output = mocker.MagicMock()
    patch_for_pen_daily_update_for_separator_and_treatment = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.'
        '_pen_daily_update_for_separator_and_treatment',
        return_value=(mock_anaerobic_digestion_daily_output,
                      mock_manure_separator_daily_output,
                      mock_manure_treatment_daily_output,
                      mock_manure_treatment_accumulated_output),
    )

    expected_daily_output_data = {
        'simulation_day': simulation_day,
        'pen': mock_manure_manager_pen,
        'animal_manure_excretions': mock_pen_manure,
        'manure_handler_daily_output': mock_manure_handler_daily_output,
        'reception_pit_daily_output': mock_reception_pit_daily_output,
        'manure_separator_daily_output': mock_manure_separator_daily_output,
        'manure_treatment_daily_output': mock_manure_treatment_daily_output,
        'manure_treatment_accumulated_output': mock_manure_treatment_accumulated_output,
        'anaerobic_digestion_daily_output': mock_anaerobic_digestion_daily_output
    }

    mock_animal_manager = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()
    mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.__init__',
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

    patch_for_add_manure_nutrients = mocker.patch.object(
        manure_manager, '_add_manure_nutrients', return_value=None
    )

    mocker.patch.object(ManureModuleOutputManagerHelper, 'add_dataclass_object', return_value=None)

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
    assert manure_manager.data == [expected_daily_output_data]
    patch_for_add_manure_nutrients.assert_called_once_with(mock_manure_manager_pen,
                                                           mock_manure_treatment_daily_output)


def test_manure_manager_daily_update(mocker: MockFixture) -> None:
    """
    Unit test for the daily_update() method in ManureManager class found in manure_manager.py.

    This test verifies that the daily_update() method correctly performs the daily updates for all pens
    by calling the _pen_daily_update() method for each pen returned by the AnimalManager.

    """
    # Arrange
    mock_animal_manager = mocker.MagicMock()
    mock_animal_manager.simulation_day = simulation_day = 1
    num_pens = 10
    mock_all_pens = [mocker.MagicMock() for _ in range(num_pens)]
    mock_animal_manager.all_pens = mock_all_pens

    mock_animal_manager_init = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_manager_config = mocker.MagicMock()
    mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.__init__',
        return_value=None,
    )
    manure_manager = ManureManager(
        animal_manager=mock_animal_manager_init,
        weather=mock_weather,
        time=mock_time,
        manure_manager_config=mock_manure_manager_config,
    )
    patch_for_pen_daily_update = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.'
        '_pen_daily_update',
        return_value=None,
    )
    manure_manager.time = mock_time
    manure_manager._manure_nutrient_manager = mocker.MagicMock()
    mocker.patch('RUFAS.routines.manure.manure_manager.ManureModuleOutputManagerHelper.add_dataclass_object',
                 return_value=None)

    # Act
    manure_manager.daily_update(mock_animal_manager)

    # Assert
    assert patch_for_pen_daily_update.call_count == num_pens
    assert patch_for_pen_daily_update.call_args_list == [mocker.call(simulation_day, pen) for pen in mock_all_pens]


@pytest.mark.parametrize(
    'treatment_type, expected_manure_type',
    [
        (ManureTreatmentType.SLURRY_STORAGE_OUTDOOR, ManureType.LIQUID),
        (ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_LAGOON, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_DIGESTION, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT, ManureType.LIQUID),
        (ManureTreatmentType.COMPOST_BEDDED_PACK_BARN, ManureType.SOLID),
    ]
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
    ]
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
    mocker.patch('RUFAS.routines.manure.manure_manager.ManureManager.__init__', return_value=None)
    manure_manager = ManureManager(animal_manager=mocker.MagicMock(), weather=mocker.MagicMock(),
                                   time=mocker.MagicMock(), manure_manager_config=mocker.MagicMock())

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
    patch_get_manure_density = mocker.patch.object(manure_manager, '_get_manure_density_by_type',
                                                   return_value=mock_manure_density)
    mock_manure_nutrients = mocker.MagicMock()
    patch_manure_nutrients_init = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureNutrients',
        return_value=mock_manure_nutrients,
    )

    # Act
    manure_manager._add_manure_nutrients(mock_pen, mock_manure_treatment_daily_output)

    # Assert
    patch_get_manure_density.assert_has_calls([
        mocker.call(ManureType.LIQUID),
    ])
    mock_manure_nutrient_manager.add_nutrients.assert_called_with(mock_manure_nutrients)
    expected_calls = [
        call(
            nitrogen=max(mock_manure_treatment_daily_output.liquid_manure_nitrogen, 0.0),
            phosphorus=max(mock_manure_treatment_daily_output.liquid_manure_phosphorus, 0.0),
            potassium=max(mock_manure_treatment_daily_output.liquid_manure_potassium, 0.0),
            dry_matter=max(mock_manure_treatment_daily_output.liquid_manure_total_solids, 0.0),
            total_manure_mass=max(mock_manure_treatment_daily_output.liquid_manure_daily_volume * mock_manure_density,
                                  0.0),
            manure_type=ManureType.LIQUID,
        ),
        call(
            nitrogen=max(mock_manure_treatment_daily_output.solid_manure_nitrogen, 0.0),
            phosphorus=max(mock_manure_treatment_daily_output.solid_manure_phosphorus, 0.0),
            potassium=max(mock_manure_treatment_daily_output.solid_manure_potassium, 0.0),
            dry_matter=max(mock_manure_treatment_daily_output.solid_manure_total_solids, 0.0),
            total_manure_mass=max(mock_manure_treatment_daily_output.solid_manure_daily_mass, 0.0),
            manure_type=ManureType.SOLID,
        )
    ]
    patch_manure_nutrients_init.assert_has_calls(expected_calls)


def test_request_nutrients(mocker: MockFixture) -> None:
    """
    Unit test for the request_nutrients method of the ManureManager class in manure_manager.py.

    This test checks whether the request_nutrients method forwards the nutrient request to the
    ManureNutrientManager instance correctly.

    """
    # Arrange
    mocker.patch('RUFAS.routines.manure.manure_manager.ManureManager.__init__', return_value=None)
    manure_manager = ManureManager(animal_manager=mocker.MagicMock(), weather=mocker.MagicMock(),
                                   time=mocker.MagicMock(), manure_manager_config=mocker.MagicMock())
    mock_manure_nutrient_manager = mocker.MagicMock()
    manure_manager._manure_nutrient_manager = mock_manure_nutrient_manager
    mock_nutrient_request = mocker.MagicMock()
    mock_nutrient_request_results = mocker.MagicMock()
    mock_manure_nutrient_manager.request_nutrients.return_value = mock_nutrient_request_results

    # Act
    actual_results = manure_manager.request_nutrients(mock_nutrient_request)

    # Assert
    mock_manure_nutrient_manager.request_nutrients.assert_called_once_with(mock_nutrient_request)
    assert actual_results == mock_nutrient_request_results
