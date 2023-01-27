import collections

import pytest
from pytest_mock import MockFixture

from RUFAS.routines.manure.manure_management import ManureManagement
from RUFAS.routines.manure.manure_management import simulate_daily_manure_management
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType


def test_simulate_daily_manure_management(mocker: MockFixture) -> None:
    """Unit test for simulate_daily_manure_management() in manure_management.py"""
    # Arrange
    mock_manure_management = mocker.MagicMock()
    mock_manure_management.daily_update.return_value = None
    mock_animal_management = mocker.MagicMock()

    # Act
    simulate_daily_manure_management(mock_manure_management, mock_animal_management)

    # Assert
    mock_manure_management.daily_update.assert_called_once_with(mock_animal_management)


def test_manure_management_init(mocker: MockFixture) -> None:
    """Unit test for __init__() of ManureManagement in manure_management.py"""
    # Arrange
    mock_animal_management = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_management_config = mocker.MagicMock()
    mock_manure_management_config_handler = mocker.MagicMock()
    patch_for_manure_management_config_handler = mocker.patch(
            "RUFAS.routines.manure.manure_management.ManureManagementConfigHandler",
            return_value=mock_manure_management_config_handler,
    )
    mock_manure_management_output_handler = mocker.MagicMock()
    patch_for_manure_management_output_handler = mocker.patch(
            "RUFAS.routines.manure.manure_management.ManureManagementOutputHandler",
            return_value=mock_manure_management_output_handler,
    )
    patch_for_configure_manure_management_components = mocker.patch(
            "RUFAS.routines.manure.manure_management.ManureManagement."
            "_configure_manure_management_components",
            return_value=None,
    )

    # Act
    manure_management = ManureManagement(
            animal_management=mock_animal_management,
            weather=mock_weather,
            time=mock_time,
            manure_management_config=mock_manure_management_config,
    )

    # Assert
    assert manure_management.beddings == {}
    assert manure_management.manure_handlers == {}
    assert manure_management.reception_pits == {}
    assert manure_management.manure_separators == {}
    assert manure_management.manure_treatments == {}
    assert manure_management.weather == mock_weather
    assert manure_management.time == mock_time
    assert manure_management._all_data == collections.defaultdict(list)

    patch_for_manure_management_config_handler.assert_called_once_with(mock_manure_management_config)
    assert manure_management.manure_management_config_handler == mock_manure_management_config_handler

    patch_for_manure_management_output_handler.assert_called_once()
    assert manure_management.manure_management_output_handler == mock_manure_management_output_handler

    patch_for_configure_manure_management_components.assert_called_once_with(mock_animal_management)


def test_all_data_property(mocker: MockFixture) -> None:
    """Unit test for all_data property of ManureManagement in manure_management.py"""
    # Arrange
    mock_animal_management = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_management_config = mocker.MagicMock()

    mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureManagement.__init__',
            return_value=None,
    )

    manure_management = ManureManagement(
            animal_management=mock_animal_management,
            weather=mock_weather,
            time=mock_time,
            manure_management_config=mock_manure_management_config,
    )

    mock_all_data = mocker.MagicMock()
    manure_management._all_data = mock_all_data

    # Act
    actual_all_data = manure_management.all_data

    # Assert
    assert actual_all_data == mock_all_data


@pytest.mark.parametrize(
        'manure_separator',
        ['none',
         'test_manure_separator',
         ])
def test_configure_manure_management_components(manure_separator: str,
                                                mocker: MockFixture) -> None:
    """Unit test for _configure_manure_management_components() in manure_management.py"""
    # Arrange
    mock_animal_management = mocker.MagicMock()
    mock_pen = mocker.MagicMock()
    mock_all_pens = [mock_pen]
    mock_animal_management.all_pens = mock_all_pens

    mock_manure_management_pen = mocker.MagicMock()
    mock_manure_management_pen.id = pen_id = 1
    mock_manure_management_pen.bedding_type = bedding_type = 'test_bedding_type'
    mock_manure_management_pen.manure_handler = manure_handler = 'test_manure_handler'
    mock_manure_management_pen.manure_separator = manure_separator
    mock_manure_management_pen.manure_treatment = manure_treatment = 'test_manure_treatment'
    patch_for_manure_management_pen_init = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureManagementPen',
            return_value=mock_manure_management_pen,
    )

    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_management_config = mocker.MagicMock()

    mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureManagement.__init__',
            return_value=None,
    )

    manure_management = ManureManagement(
            animal_management=mock_animal_management,
            weather=mock_weather,
            time=mock_time,
            manure_management_config=mock_manure_management_config,
    )

    mock_manure_management_config_handler = mocker.MagicMock()

    mock_custom_bedding_config = mocker.MagicMock()
    mock_manure_management_config_handler.get_custom_bedding_config.return_value = mock_custom_bedding_config
    mock_bedding = mocker.MagicMock()
    patch_for_bedding_factory_get_instance = mocker.patch(
            'RUFAS.routines.manure.manure_management.BeddingFactory.get_instance',
            return_value=mock_bedding,
    )

    mock_custom_manure_handler_config = mocker.MagicMock()
    mock_manure_management_config_handler.get_custom_manure_handler_config.return_value = \
        mock_custom_manure_handler_config
    mock_manure_handler = mocker.MagicMock()
    patch_for_manure_handler_factory_get_instance = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureHandlerFactory.get_instance',
            return_value=mock_manure_handler,
    )

    mock_reception_pit = mocker.MagicMock()
    patch_for_reception_pit_init = mocker.patch(
            'RUFAS.routines.manure.manure_management.ReceptionPit',
            return_value=mock_reception_pit,
    )

    mock_custom_manure_separator_config = mocker.MagicMock()
    mock_manure_management_config_handler.get_custom_manure_separator_config.return_value = \
        mock_custom_manure_separator_config
    mock_manure_separator = mocker.MagicMock()
    patch_for_manure_separator_factory_get_instance = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureSeparatorFactory.get_instance',
            return_value=mock_manure_separator,
    )

    mock_custom_manure_treatment_config = mocker.MagicMock()
    mock_manure_management_config_handler.get_custom_manure_treatment_config.return_value = \
        mock_custom_manure_treatment_config
    mock_manure_treatment = mocker.MagicMock()
    patch_for_manure_treatment_factory_get_instance = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureTreatmentFactory.get_instance',
            return_value=mock_manure_treatment,
    )

    manure_management.manure_management_config_handler = mock_manure_management_config_handler
    manure_management.beddings = {}
    manure_management.manure_handlers = {}
    manure_management.reception_pits = {}
    manure_management.manure_separators = {}
    manure_management.manure_treatments = {}
    manure_management.weather = mock_weather
    manure_management.time = mock_time

    # Act
    manure_management._configure_manure_management_components(mock_animal_management)

    # Assert
    patch_for_manure_management_pen_init.assert_called_once_with(mock_pen)

    mock_manure_management_config_handler.get_custom_bedding_config.assert_called_once_with(bedding_type)
    patch_for_bedding_factory_get_instance.assert_called_once_with(
            bedding_type_name=bedding_type,
            custom_bedding_config=mock_custom_bedding_config,
    )
    assert manure_management.beddings[pen_id] == mock_bedding

    mock_manure_management_config_handler.get_custom_manure_handler_config.assert_called_once_with(manure_handler)
    patch_for_manure_handler_factory_get_instance.assert_called_once_with(
            manure_handler_type_name=manure_handler,
            weather=mock_weather,
            time=mock_time,
            custom_manure_handler_config=mock_custom_manure_handler_config,
    )
    assert manure_management.manure_handlers[pen_id] == mock_manure_handler

    patch_for_reception_pit_init.assert_called_once()
    assert manure_management.reception_pits[pen_id] == mock_reception_pit

    if manure_separator == 'none':
        mock_manure_management_config_handler.get_custom_manure_separator_config.assert_not_called()
        patch_for_manure_separator_factory_get_instance.assert_not_called()
        assert manure_management.manure_separators[pen_id] is None
    else:
        mock_manure_management_config_handler.get_custom_manure_separator_config \
            .assert_called_once_with(manure_separator)
        patch_for_manure_separator_factory_get_instance.assert_called_once_with(
                manure_separator_type_name=manure_separator,
                custom_manure_separator_config=mock_custom_manure_separator_config,
        )
        assert manure_management.manure_separators[pen_id] == mock_manure_separator

    mock_manure_management_config_handler.get_custom_manure_treatment_config.assert_called_once_with(manure_treatment)
    patch_for_manure_treatment_factory_get_instance.assert_called_once_with(
            manure_treatment_type_name=manure_treatment,
            weather=mock_weather,
            time=mock_time,
            custom_manure_treatment_config=mock_custom_manure_treatment_config
    )
    assert manure_management.manure_treatments[pen_id] == mock_manure_treatment


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
    """Unit test for _is_compound_anaerobic_manure_treatment() in manure_management.py."""
    # Arrange
    manure_treatment_name = 'test_manure_treatment'
    patch_for_manure_treatment_type_get_type = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureTreatmentType.get_type',
            return_value=manure_treatment_type,
    )

    # Act
    result = ManureManagement._is_compound_anaerobic_manure_treatment(manure_treatment_name)

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
    """Unit test for _handle_daily_update_for_simple_manure_treatment() in manure_management.py."""
    # Arrange
    simulation_day = 1
    mock_manure_management_pen = mocker.MagicMock()
    mock_manure_management_pen.id = pen_id = 1
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_reception_pit_daily_output = mocker.MagicMock()

    mock_animal_management = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_management_config = mocker.MagicMock()

    manure_management = ManureManagement(
            animal_management=mock_animal_management,
            weather=mock_weather,
            time=mock_time,
            manure_management_config=mock_manure_management_config,
    )
    manure_management.manure_separators = {}
    manure_management.manure_treatments = {}

    mock_manure_separator = mocker.MagicMock()
    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_separator.daily_update.return_value = mock_manure_separator_daily_output
    if is_manure_separator_present:
        manure_management.manure_separators[pen_id] = mock_manure_separator
    else:
        manure_management.manure_separators[pen_id] = None

    mock_manure_treatment = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment.daily_update.return_value = mock_manure_treatment_daily_output
    manure_management.manure_treatments[pen_id] = mock_manure_treatment

    # Act
    manure_separator_daily_output, manure_treatment_daily_output = \
        manure_management._handle_daily_update_for_simple_manure_treatment(simulation_day=simulation_day,
                                                                           pen=mock_manure_management_pen,
                                                                           manure_handler_daily_output=mock_manure_handler_daily_output,
                                                                           reception_pit_daily_output=mock_reception_pit_daily_output)

    # Assert
    if is_manure_separator_present:
        mock_manure_separator.daily_update.assert_called_once_with(
                manure_separator_daily_input=mock_reception_pit_daily_output,
        )
        assert manure_separator_daily_output == mock_manure_separator_daily_output
        mock_manure_treatment.daily_update.assert_called_once_with(
                manure_handler_daily_output=mock_manure_handler_daily_output,
                manure_treatment_daily_input=mock_manure_separator_daily_output,
                pen=mock_manure_management_pen,
                sim_day=simulation_day
        )
        assert manure_treatment_daily_output == mock_manure_treatment_daily_output
    else:
        assert manure_separator_daily_output is None
        mock_manure_treatment.daily_update.assert_called_once_with(
                manure_handler_daily_output=mock_manure_handler_daily_output,
                manure_treatment_daily_input=mock_reception_pit_daily_output,
                pen=mock_manure_management_pen,
                sim_day=simulation_day
        )
        assert manure_treatment_daily_output == mock_manure_treatment_daily_output


def test_handle_update_for_compound_anaerobic_manure_treatment(mocker: MockFixture) -> None:
    # Arrange
    simulation_day = 1
    mock_manure_management_pen = mocker.MagicMock()
    mock_manure_management_pen.id = pen_id = 1
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_reception_pit_daily_output = mocker.MagicMock()

    mock_animal_management = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_management_config = mocker.MagicMock()

    manure_management = ManureManagement(
            animal_management=mock_animal_management,
            weather=mock_weather,
            time=mock_time,
            manure_management_config=mock_manure_management_config,
    )
    mock_manure_separator = mocker.MagicMock()
    manure_management.manure_separators = {pen_id: mock_manure_separator}

    mock_manure_treatment = mocker.MagicMock()

    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment.daily_update.return_value = mock_manure_treatment_daily_output

    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_manure_treatment.anaerobic_digestion_daily_output = mock_anaerobic_digestion_daily_output

    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_treatment.manure_separator_daily_output = mock_manure_separator_daily_output

    manure_management.manure_treatments = {pen_id: mock_manure_treatment}

    # Act
    anaerobic_digestion_daily_output, manure_separator_daily_output, manure_treatment_daily_output = \
        manure_management._handle_daily_update_for_compound_anaerobic_manure_treatment(simulation_day=simulation_day,
                                                                                       pen=mock_manure_management_pen,
                                                                                       manure_handler_daily_output=mock_manure_handler_daily_output,
                                                                                       reception_pit_daily_output=mock_reception_pit_daily_output)

    # Assert
    mock_manure_treatment.daily_update.assert_called_once_with(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            manure_treatment_daily_input=mock_reception_pit_daily_output,
            pen=mock_manure_management_pen,
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
    mock_manure_management_pen = mocker.MagicMock()
    mock_manure_management_pen.manure_treatment = manure_treatment = 'test_manure_treatment'
    mock_manure_handler_daily_output = mocker.MagicMock()
    mock_reception_pit_daily_output = mocker.MagicMock()

    patch_for_is_compound_anaerobic_manure_treatment = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureManagement._is_compound_anaerobic_manure_treatment',
            return_value=is_compound_anaerobic_manure_treatment,
    )

    mock_anaerobic_digestion_daily_output = mocker.MagicMock()
    mock_manure_separator_daily_output = mocker.MagicMock()
    mock_manure_separator_daily_output_2 = mocker.MagicMock()
    mock_manure_treatment_daily_output = mocker.MagicMock()
    mock_manure_treatment_daily_output_2 = mocker.MagicMock()

    patch_for_handle_daily_update_for_compound_anaerobic_manure_treatment = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureManagement.'
            '_handle_daily_update_for_compound_anaerobic_manure_treatment',
            return_value=(mock_anaerobic_digestion_daily_output,
                          mock_manure_separator_daily_output,
                          mock_manure_treatment_daily_output),
    )

    patch_for_handle_daily_update_for_simple_manure_treatment = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureManagement.'
            '_handle_daily_update_for_simple_manure_treatment',
            return_value=(mock_manure_separator_daily_output_2,
                          mock_manure_treatment_daily_output_2),
    )

    mock_animal_management = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_management_config = mocker.MagicMock()
    manure_management = ManureManagement(
            animal_management=mock_animal_management,
            weather=mock_weather,
            time=mock_time,
            manure_management_config=mock_manure_management_config,
    )

    # Act
    anaerobic_digestion_daily_output, manure_separator_daily_output, manure_treatment_daily_output = \
        manure_management._pen_daily_update_for_separator_and_treatment(
                simulation_day=simulation_day,
                pen=mock_manure_management_pen,
                manure_handler_daily_output=mock_manure_handler_daily_output,
                reception_pit_daily_output=mock_reception_pit_daily_output,
        )

    # Assert
    patch_for_is_compound_anaerobic_manure_treatment.assert_called_once_with(manure_treatment)
    if is_compound_anaerobic_manure_treatment:
        patch_for_handle_daily_update_for_compound_anaerobic_manure_treatment.assert_called_once_with(
                simulation_day=simulation_day,
                pen=mock_manure_management_pen,
                manure_handler_daily_output=mock_manure_handler_daily_output,
                reception_pit_daily_output=mock_reception_pit_daily_output,
        )
        assert anaerobic_digestion_daily_output == mock_anaerobic_digestion_daily_output
        assert manure_separator_daily_output == mock_manure_separator_daily_output
        assert manure_treatment_daily_output == mock_manure_treatment_daily_output
    else:
        patch_for_handle_daily_update_for_simple_manure_treatment.assert_called_once_with(
                simulation_day=simulation_day,
                pen=mock_manure_management_pen,
                manure_handler_daily_output=mock_manure_handler_daily_output,
                reception_pit_daily_output=mock_reception_pit_daily_output,
        )
        assert anaerobic_digestion_daily_output is None
        assert manure_separator_daily_output == mock_manure_separator_daily_output_2
        assert manure_treatment_daily_output == mock_manure_treatment_daily_output_2


def test_pen_daily_update(mocker: MockFixture) -> None:
    """Unit test for _pen_daily_update() in manure_management.py."""
    # Arrange
    simulation_day = 1
    mock_pen = mocker.MagicMock()
    mock_manure_management_pen = mocker.MagicMock()
    mock_manure_management_pen.id = pen_id = 1
    patch_for_manure_management_pen_init = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureManagementPen',
            return_value=mock_manure_management_pen,
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
            'RUFAS.routines.manure.manure_management.ManureManagement.'
            '_pen_daily_update_for_separator_and_treatment',
            return_value=(mock_anaerobic_digestion_daily_output,
                          mock_manure_separator_daily_output,
                          mock_manure_treatment_daily_output),
    )

    expected_daily_update_output = (
        mock_manure_management_pen,
        mock_manure_handler_daily_output,
        mock_reception_pit_daily_output,
        mock_manure_separator_daily_output,
        mock_manure_treatment_daily_output,
        mock_anaerobic_digestion_daily_output,
    )

    mock_animal_management = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_manure_management_config = mocker.MagicMock()
    manure_management = ManureManagement(
            animal_management=mock_animal_management,
            weather=mock_weather,
            time=mock_time,
            manure_management_config=mock_manure_management_config,
    )
    manure_management.beddings = {pen_id: mock_bedding}
    manure_management.manure_handlers = {pen_id: mock_manure_handler}
    manure_management.reception_pits = {pen_id: mock_reception_pit}
    manure_management._all_data = {pen_id: []}
    mock_manure_management_output_handler = mocker.MagicMock()
    mock_manure_management_output_handler.append_daily_update_output_for_pen.return_value = None
    manure_management.manure_management_output_handler = mock_manure_management_output_handler

    # Act
    manure_management._pen_daily_update(
            simulation_day=simulation_day,
            pen=mock_pen,
    )

    # Assert
    patch_for_manure_management_pen_init.assert_called_once_with(mock_pen)
    mock_manure_handler.daily_update.assert_called_once_with(
            pen=mock_manure_management_pen,
            bedding=mock_bedding,
            sim_day=simulation_day,
    )
    mock_reception_pit.daily_update.assert_called_once_with(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            pen=mock_manure_management_pen,
            bedding=mock_bedding,
    )
    patch_for_pen_daily_update_for_separator_and_treatment.assert_called_once_with(
            simulation_day=simulation_day,
            pen=mock_manure_management_pen,
            manure_handler_daily_output=mock_manure_handler_daily_output,
            reception_pit_daily_output=mock_reception_pit_daily_output,
    )
    assert manure_management._all_data[pen_id] == [expected_daily_update_output]
    mock_manure_management_output_handler.append_daily_update_output_for_pen.assert_called_once_with(
            simulation_day=simulation_day,
            data=expected_daily_update_output,
    )


@pytest.mark.parametrize(
        'is_last_day_of_simulation',
        [
            True,
            False,
        ])
def test_manure_management_daily_update(is_last_day_of_simulation: bool,
                                        mocker: MockFixture) -> None:
    # Arrange

    mock_animal_management = mocker.MagicMock()
    mock_animal_management.simulation_day = simulation_day = 1
    num_pens = 10
    mock_all_pens = [mocker.MagicMock() for _ in range(num_pens)]
    mock_animal_management.all_pens = mock_all_pens

    mock_animal_management_init = mocker.MagicMock()
    mock_weather = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_time.is_last_day_of_simulation.return_value = is_last_day_of_simulation
    mock_manure_management_config = mocker.MagicMock()
    manure_management = ManureManagement(
            animal_management=mock_animal_management_init,
            weather=mock_weather,
            time=mock_time,
            manure_management_config=mock_manure_management_config,
    )
    patch_for_pen_daily_update = mocker.patch(
            'RUFAS.routines.manure.manure_management.ManureManagement.'
            '_pen_daily_update',
            return_value=None,
    )
    mock_manure_management_output_handler = mocker.MagicMock()
    mock_manure_management_output_handler.sort_by_pen_id_and_simulation_day.return_value = None
    mock_manure_management_output_handler.export_to_csv.return_value = None
    manure_management.manure_management_output_handler = mock_manure_management_output_handler

    # Act
    manure_management.daily_update(mock_animal_management)

    # Assert
    assert patch_for_pen_daily_update.call_count == num_pens
    assert patch_for_pen_daily_update.call_args_list == [mocker.call(simulation_day, pen) for pen in mock_all_pens]

    if is_last_day_of_simulation:
        mock_manure_management_output_handler.sort_by_pen_id_and_simulation_day.assert_called_once()
        mock_manure_management_output_handler.export_to_csv.assert_called_once()
    else:
        mock_manure_management_output_handler.sort_by_pen_id_and_simulation_day.assert_not_called()
        mock_manure_management_output_handler.export_to_csv.assert_not_called()
