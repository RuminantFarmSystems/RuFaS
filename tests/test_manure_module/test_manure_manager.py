import collections

import pytest
from pytest_mock import MockFixture

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
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
    mock_manure_manager_output_handler = mocker.MagicMock()
    patch_for_manure_manager_output_handler = mocker.patch(
        "RUFAS.routines.manure.manure_manager.ManureManagerOutputHandler",
        return_value=mock_manure_manager_output_handler,
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
    assert manure_manager._all_data == collections.defaultdict(list)

    patch_for_manure_manager_config_handler.assert_called_once_with(mock_manure_manager_config)
    assert manure_manager.manure_manager_config_handler == mock_manure_manager_config_handler

    patch_for_manure_manager_output_handler.assert_called_once()
    assert manure_manager.manure_manager_output_handler == mock_manure_manager_output_handler

    patch_for_configure_manure_manager_components.assert_called_once_with(mock_animal_manager)


def test_all_data_property(mocker: MockFixture) -> None:
    """Unit test for all_data property of ManureManager in manure_manager.py"""
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

    mock_all_data = mocker.MagicMock()
    manure_manager._all_data = mock_all_data

    # Act
    actual_all_data = manure_manager.all_data

    # Assert
    assert actual_all_data == mock_all_data


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
    """Unit test for _handle_daily_update_for_simple_manure_treatment() in manure_manager.py."""
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
    mock_manure_treatment.daily_update.return_value = mock_manure_treatment_daily_output
    manure_manager.manure_treatments[pen_id] = mock_manure_treatment

    # Act
    manure_separator_daily_output, manure_treatment_daily_output = \
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
        assert manure_treatment_daily_output == mock_manure_treatment_daily_output
    else:
        assert manure_separator_daily_output is None
        mock_manure_treatment.daily_update.assert_called_once_with(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            manure_treatment_daily_input=mock_reception_pit_daily_output,
            pen=mock_manure_manager_pen,
            sim_day=simulation_day
        )
        assert manure_treatment_daily_output == mock_manure_treatment_daily_output


def test_handle_update_for_compound_anaerobic_manure_treatment(mocker: MockFixture) -> None:
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
    mock_manure_treatment.daily_update.return_value = mock_manure_treatment_daily_output

    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_manure_treatment.anaerobic_digestion_daily_output = mock_anaerobic_digestion_daily_output

    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_treatment.manure_separator_daily_output = mock_manure_separator_daily_output

    manure_manager.manure_treatments = {pen_id: mock_manure_treatment}

    # Act
    anaerobic_digestion_daily_output, manure_separator_daily_output, manure_treatment_daily_output = \
        manure_manager._handle_daily_update_for_compound_anaerobic_manure_treatment(simulation_day=simulation_day,
                                                                                    pen=mock_manure_manager_pen,
                                                                                    manure_handler_daily_output=mock_manure_handler_daily_output,
                                                                                    reception_pit_daily_output=mock_reception_pit_daily_output)

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


@pytest.mark.parametrize(
    'is_compound_anaerobic_manure_treatment',
    [
        True,
        False,
    ]
)
def test_pen_daily_update_for_separator_and_treatment(is_compound_anaerobic_manure_treatment: bool,
                                                      mocker: MockFixture) -> None:
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

    patch_for_handle_daily_update_for_compound_anaerobic_manure_treatment = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.'
        '_handle_daily_update_for_compound_anaerobic_manure_treatment',
        return_value=(mock_anaerobic_digestion_daily_output,
                      mock_manure_separator_daily_output,
                      mock_manure_treatment_daily_output),
    )

    patch_for_handle_daily_update_for_simple_manure_treatment = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.'
        '_handle_daily_update_for_simple_manure_treatment',
        return_value=(mock_manure_separator_daily_output_2,
                      mock_manure_treatment_daily_output_2),
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
    anaerobic_digestion_daily_output, manure_separator_daily_output, manure_treatment_daily_output = \
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


def test_pen_daily_update(mocker: MockFixture) -> None:
    """Unit test for _pen_daily_update() in manure_manager.py."""
    # Arrange
    simulation_day = 1
    mock_pen = mocker.MagicMock()
    mock_manure_manager_pen = mocker.MagicMock()
    mock_manure_manager_pen.id = pen_id = 1
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
    patch_for_pen_daily_update_for_separator_and_treatment = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.'
        '_pen_daily_update_for_separator_and_treatment',
        return_value=(mock_anaerobic_digestion_daily_output,
                      mock_manure_separator_daily_output,
                      mock_manure_treatment_daily_output),
    )

    expected_daily_update_output = (
        mock_manure_manager_pen,
        mock_manure_handler_daily_output,
        mock_reception_pit_daily_output,
        mock_manure_separator_daily_output,
        mock_manure_treatment_daily_output,
        mock_anaerobic_digestion_daily_output,
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
    manure_manager.beddings = {pen_id: mock_bedding}
    manure_manager.manure_handlers = {pen_id: mock_manure_handler}
    manure_manager.reception_pits = {pen_id: mock_reception_pit}
    manure_manager._all_data = {pen_id: []}
    mock_manure_manager_output_handler = mocker.MagicMock()
    mock_manure_manager_output_handler.append_daily_update_output_for_pen.return_value = None
    manure_manager.manure_manager_output_handler = mock_manure_manager_output_handler

    patch_for_add_manure_nutrients = mocker.patch.object(
        manure_manager, '_add_manure_nutrients', return_value=None
    )

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
    assert manure_manager._all_data[pen_id] == [expected_daily_update_output]
    mock_manure_manager_output_handler.append_daily_update_output_for_pen.assert_called_once_with(
        simulation_day=simulation_day,
        data=expected_daily_update_output,
    )
    patch_for_add_manure_nutrients.assert_called_once_with(mock_manure_manager_pen,
                                                           mock_manure_treatment_daily_output)


@pytest.mark.parametrize(
    'is_last_day_of_simulation',
    [
        True,
        False,
    ])
def test_manure_manager_daily_update(is_last_day_of_simulation: bool,
                                     mocker: MockFixture) -> None:
    # Arrange

    mock_animal_manager = mocker.MagicMock()
    mock_animal_manager.simulation_day = simulation_day = 1
    num_pens = 10
    mock_all_pens = [mocker.MagicMock() for _ in range(num_pens)]
    mock_animal_manager.all_pens = mock_all_pens

    mock_animal_manager_init = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_time.is_last_day_of_simulation = is_last_day_of_simulation
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
    mock_manure_manager_output_handler = mocker.MagicMock()
    mock_manure_manager_output_handler.sort_by_pen_id_and_simulation_day.return_value = None
    mock_manure_manager_output_handler.export_to_csv.return_value = None
    manure_manager.manure_manager_output_handler = mock_manure_manager_output_handler
    manure_manager.time = mock_time

    # Act
    manure_manager.daily_update(mock_animal_manager)

    # Assert
    assert patch_for_pen_daily_update.call_count == num_pens
    assert patch_for_pen_daily_update.call_args_list == [mocker.call(simulation_day, pen) for pen in mock_all_pens]

    if is_last_day_of_simulation:
        mock_manure_manager_output_handler.sort_by_pen_id_and_simulation_day.assert_called_once()
        mock_manure_manager_output_handler.export_to_csv.assert_called_once()
    else:
        mock_manure_manager_output_handler.sort_by_pen_id_and_simulation_day.assert_not_called()
        mock_manure_manager_output_handler.export_to_csv.assert_not_called()


@pytest.mark.parametrize(
    'treatment_type, expected_manure_type',
    [
        (ManureTreatmentType.SLURRY_STORAGE_OUTDOOR, ManureType.SLURRY),
        (ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR, ManureType.SLURRY),
        (ManureTreatmentType.ANAEROBIC_LAGOON, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_DIGESTION, ManureType.LIQUID),
        (ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT, ManureType.LIQUID),
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
    'manure_type, expected_density',
    [
        (ManureType.LIQUID, ManureConstants.LIQUID_MANURE_DENSITY),
        (ManureType.SLURRY, ManureConstants.SLURRY_MANURE_DENSITY),
        (ManureType.SOLID, ManureConstants.SOLID_MANURE_DENSITY),
    ]
)
def test_get_manure_density(manure_type: ManureType, expected_density: float,
                            mocker: MockFixture) -> None:
    """
    Unit test for the _get_manure_density method of the ManureManager class in manure_manager.py.

    This test checks whether the _get_manure_density method returns the correct manure density
    for a mock pen with the provided ManureTreatmentType.

    """
    # Arrange
    mock_pen = mocker.MagicMock()
    mock_pen.manure_treatment = mock_manure_treatment_name = 'mock_manure_treatment_name'
    mock_manure_treatment_type = mocker.MagicMock()
    patch_for_get_treatment_type = mocker.patch(
        'RUFAS.routines.manure.manure_manager.'
        'ManureTreatmentType.get_type',
        return_value=mock_manure_treatment_type,
    )
    patch_for_get_manure_type = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureManager.'
        '_get_manure_type',
        return_value=manure_type,
    )

    # Act
    actual_density = ManureManager._get_manure_density(mock_pen)

    # Assert
    assert actual_density == expected_density
    patch_for_get_treatment_type.assert_called_once_with(mock_manure_treatment_name)
    patch_for_get_manure_type.assert_called_once_with(mock_manure_treatment_type)


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
    mock_manure_treatment_daily_output.liquid_manure_nitrogen = manure_nitrogen = 1
    mock_manure_treatment_daily_output.liquid_manure_phosphorus = manure_phosphorus = 2
    mock_manure_treatment_daily_output.liquid_manure_potassium = manure_potassium = 3
    mock_manure_treatment_daily_output.liquid_manure_total_solids = manure_total_solids = 4
    mock_manure_treatment_daily_output.liquid_manure_daily_volume = manure_daily_volume = 5

    mock_manure_nutrient_manager = mocker.MagicMock()
    manure_manager._manure_nutrient_manager = mock_manure_nutrient_manager

    mock_manure_density = 1000
    patch_get_manure_density = mocker.patch.object(manure_manager, '_get_manure_density',
                                                   return_value=mock_manure_density)
    mock_manure_nutrients = mocker.MagicMock()
    patch_manure_nutrients_init = mocker.patch(
        'RUFAS.routines.manure.manure_manager.ManureNutrients',
        return_value=mock_manure_nutrients,
    )

    # Act
    manure_manager._add_manure_nutrients(mock_pen, mock_manure_treatment_daily_output)

    # Assert
    patch_get_manure_density.assert_called_once_with(mock_pen)
    mock_manure_nutrient_manager.add_nutrients.assert_called_once_with(mock_manure_nutrients)
    patch_manure_nutrients_init.assert_called_once_with(
        nitrogen=manure_nitrogen,
        phosphorus=manure_phosphorus,
        potassium=manure_potassium,
        dry_matter=manure_total_solids,
        total_manure_mass=manure_daily_volume * mock_manure_density
    )


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
