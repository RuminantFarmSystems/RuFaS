# import pytest
# from pytest import approx
# from pytest_mock import MockerFixture
#
# from RUFAS.routines import AnimalManagement
# from RUFAS.routines.animal.pen import Pen
# from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
# from RUFAS.routines.manure.beddings.bedding_classes import ManureSolidsBedding
# from RUFAS.routines.manure.beddings.bedding_classes import SandBedding
# from RUFAS.routines.manure.beddings.bedding_classes import SawdustBedding
# from RUFAS.routines.manure.manure_handlers.manure_handler_classes import AlleyScraper
# from RUFAS.routines.manure.manure_handlers.manure_handler_classes import BaseManureHandler
# from RUFAS.routines.manure.manure_handlers.manure_handler_classes import DefaultManureHandlerConfigFactory
# from RUFAS.routines.manure.manure_handlers.manure_handler_classes import FlushSystem
# from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManualScraping
# from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManureHandlerConfig
# from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManureHandlerFactory
# from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManureHandlerType
# from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
# from RUFAS.routines.manure.manure_management import ManureManagement
# from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
#
#
# # Test ManureManagement class
# # ===========================
#
# def test_manure_management_init(mocker: MockerFixture, mock_animal_management: AnimalManagement) -> None:
#     """Unit test for function __init__ in file manure_management.py"""
#
#     # Arrange
#     mock_set_up_components = mocker.patch('RUFAS.routines.manure.manure_management.ManureManagement'
#                                           '._configure_manure_management_components', return_value=None)
#
#     # Act
#     manure_management = ManureManagement(mock_animal_management)
#
#     # Assert
#     assert manure_management.manure_handlers == {}
#     assert manure_management.reception_pits == {}
#     assert manure_management.manure_separators == {}
#     assert manure_management.manure_treatments == {}
#     assert manure_management.all_data == {}
#     mock_set_up_components.assert_called_once_with(mock_animal_management)
#
#
# def test_setup_manure_management_components(mocker: MockerFixture,
#                                             mock_animal_management: AnimalManagement) -> None:
#     """Unit test for function _configure_manure_management_components in file manure_management.py"""
#
#     # Arrange
#     num_pens = 3
#     mock_pens = [mocker.MagicMock(autospec=Pen) for _ in range(num_pens)]
#     for i in range(num_pens):
#         mock_pens[i].id = i
#     mock_animal_management.all_pens = mock_pens
#
#     # Act
#     manure_management = ManureManagement(mock_animal_management)
#
#     # Assert
#     assert len(manure_management.manure_handlers) == num_pens
#     assert len(manure_management.reception_pits) == num_pens
#     assert len(manure_management.manure_separators) == num_pens
#     assert len(manure_management.manure_treatments) == num_pens
#
#
# def test_manure_management_update(mocker: MockerFixture,
#                                   mock_animal_management: AnimalManagement) -> None:
#     """Unit test for function update in file manure_management.py"""
#
#     # Arrange
#     num_pens = 3
#     mock_pens = [mocker.MagicMock(autospec=Pen) for _ in range(num_pens)]
#     for i in range(num_pens):
#         mock_pens[i].id = i
#     mock_animal_management.all_pens = mock_pens
#
#     # Act
#     manure_management = ManureManagement(mock_animal_management)
#     manure_management.update(mock_animal_management)
#
#     # Assert
#     assert len(manure_management.manure_handlers) == num_pens
#     assert len(manure_management.reception_pits) == num_pens
#     assert len(manure_management.manure_separators) == num_pens
#     assert len(manure_management.manure_treatments) == num_pens
#     assert len(manure_management.all_data) == num_pens
#
#
# # Test ManureHandlerOutput
# # ========================
#
# def test_manure_handler_daily_output_init() -> None:
#     """Unit test for __init__() of class ManureHandlerDailyOutput in file manure_handler_daily_output.py"""
#
#     # Act
#     manure_handler_output = ManureHandlerDailyOutput(
#             simulation_day=1,
#             pen_id=1,
#             urea=1.0,
#             TAN=2.0,
#             N=3.0,
#             TS=4.0,
#             VSd=5.0,
#             VSnd=6.0,
#             WIP_frac=0.70,
#             WOP_frac=0.80,
#             P=9.0,
#             K=10.0,
#             manure_volume=14.0,
#             cleaning_water_volume=15.0,
#             total_bedding_volume=16.0,
#             total_water_volume_in_milking_parlor=17.0
#     )
#
#     # Assert
#     assert manure_handler_output.simulation_day == 1
#     assert manure_handler_output.pen_id == 1
#     assert manure_handler_output.urea == approx(1.0)
#     assert manure_handler_output.TAN == approx(2.0)
#     assert manure_handler_output.N == approx(3.0)
#     assert manure_handler_output.TS == approx(4.0)
#     assert manure_handler_output.VSd == approx(5.0)
#     assert manure_handler_output.VSnd == approx(6.0)
#     assert manure_handler_output.VS_total == approx(5.0 + 6.0)
#     assert manure_handler_output.WIP_frac == approx(0.70)
#     assert manure_handler_output.WOP_frac == approx(0.80)
#     assert manure_handler_output.P == approx(9.0)
#     assert manure_handler_output.K == approx(10.0)
#     assert manure_handler_output.manure_volume == approx(14.0)
#     assert manure_handler_output.cleaning_water_volume == approx(15.0)
#     assert manure_handler_output.total_bedding_volume == approx(16.0)
#     assert manure_handler_output.total_water_volume_in_milking_parlor == approx(17.0)
#     assert manure_handler_output.total_daily_manure_volume == approx(14.0 + 15.0 + 16.0 + 17.0)
#
#
# # Test ManureHandlerConfig
# # ========================
#
# def test_manure_handler_config_init_() -> None:
#     """Unit test for __init__() of class ManureHandlerConfig"""
#
#     # Act
#     manure_handler_config = ManureHandlerConfig(
#             cleaning_water_use_rate=20.0,
#             minutes_per_cleaning=10,
#             cleanings_per_day=3
#     )
#
#     # Assert
#     assert manure_handler_config.cleaning_water_use_rate == approx(20.0)
#     assert manure_handler_config.minutes_per_cleaning == 10
#     assert manure_handler_config.cleanings_per_day == 3
#
#
# # Test DefaultManureHandlerConfigFactory
#
#
# @pytest.mark.parametrize(
#         'manure_handler_type, expected_cleaning_water_use_rate, '
#         'expected_minutes_per_cleaning, expected_cleanings_per_day',
#         [
#             (ManureHandlerType.FLUSH_SYSTEM, 757.0, 8, 2),
#             (ManureHandlerType.MANUAL_SCRAPING, 10.0, 8, 2),
#             (ManureHandlerType.ALLEY_SCRAPER, 10.0, 8, 2)
#         ]
# )
# def test_default_manure_handler_config_factory_get_instance(manure_handler_type: ManureHandlerType,
#                                                             expected_cleaning_water_use_rate: float,
#                                                             expected_minutes_per_cleaning: int,
#                                                             expected_cleanings_per_day: int) -> None:
#     """Unit test for get_instance() of class DefaultManureHandlerConfigFactory"""
#
#     # Act
#     manure_handler_config = DefaultManureHandlerConfigFactory.get_instance(manure_handler_type)
#
#     # Assert
#     assert manure_handler_config.cleaning_water_use_rate == approx(expected_cleaning_water_use_rate)
#     assert manure_handler_config.minutes_per_cleaning == expected_minutes_per_cleaning
#     assert manure_handler_config.cleanings_per_day == expected_cleanings_per_day
#
#
# # Test ManureHandlerType
# # ======================
#
# def test_manure_handler_type_enum() -> None:
#     """Unit test for enum ManureHandlerType"""
#
#     # Assert
#     assert ManureHandlerType.get_type('flush system') is ManureHandlerType.FLUSH_SYSTEM
#     assert ManureHandlerType.get_type('manual scraping') is ManureHandlerType.MANUAL_SCRAPING
#     assert ManureHandlerType.get_type('alley scraper') is ManureHandlerType.ALLEY_SCRAPER
#     assert ManureHandlerType.get_type('default') is ManureHandlerType.DEFAULT
#     assert ManureHandlerType.DEFAULT is ManureHandlerType.FLUSH_SYSTEM
#     assert ManureHandlerType.get_type('dummy') is ManureHandlerType.FLUSH_SYSTEM
#
#
# # Test ManureHandlerFactory
# # =========================
#
# @pytest.fixture
# def mock_manure_handler_config() -> ManureHandlerConfig:
#     """Mock ManureHandlerConfig"""
#     return ManureHandlerConfig(
#             cleaning_water_use_rate=20.0,
#             minutes_per_cleaning=10,
#             cleanings_per_day=3
#     )
#
#
# @pytest.mark.parametrize(
#         'manure_handler_type_name, bedding_type_name, '
#         'custom_manure_handler_config, expected_manure_handler_class,'
#         'expected_bedding_type, expected_manure_handler_config',
#         [
#             ('flush system', 'sawdust', None, FlushSystem, SawdustBedding,
#              DefaultManureHandlerConfigFactory.FLUSH_SYSTEM_CONFIG),
#             ('manual scraping', 'sawdust', None, ManualScraping, SawdustBedding,
#              DefaultManureHandlerConfigFactory.MANUAL_SCRAPING_CONFIG),
#             ('alley scraper', 'sawdust', None, AlleyScraper, SawdustBedding,
#              DefaultManureHandlerConfigFactory.ALLEY_SCRAPER_CONFIG),
#             ('dummy', 'sawdust', None, FlushSystem, SawdustBedding,
#              DefaultManureHandlerConfigFactory.FLUSH_SYSTEM_CONFIG),
#             ('flush system', 'manure solids', None, FlushSystem, ManureSolidsBedding,
#              DefaultManureHandlerConfigFactory.FLUSH_SYSTEM_CONFIG),
#             ('manual scraping', 'manure solids', None, ManualScraping, ManureSolidsBedding,
#              DefaultManureHandlerConfigFactory.MANUAL_SCRAPING_CONFIG),
#             ('alley scraper', 'manure solids', None, AlleyScraper, ManureSolidsBedding,
#              DefaultManureHandlerConfigFactory.ALLEY_SCRAPER_CONFIG),
#             ('dummy', 'manure solids', None, FlushSystem, ManureSolidsBedding,
#              DefaultManureHandlerConfigFactory.FLUSH_SYSTEM_CONFIG),
#             ('flush system', 'sand', None, FlushSystem, SandBedding,
#              DefaultManureHandlerConfigFactory.FLUSH_SYSTEM_CONFIG),
#             ('manual scraping', 'sand', None, ManualScraping, SandBedding,
#              DefaultManureHandlerConfigFactory.MANUAL_SCRAPING_CONFIG),
#             ('alley scraper', 'sand', None, AlleyScraper, SandBedding,
#              DefaultManureHandlerConfigFactory.ALLEY_SCRAPER_CONFIG),
#             ('dummy', 'sand', None, FlushSystem, SandBedding,
#              DefaultManureHandlerConfigFactory.FLUSH_SYSTEM_CONFIG),
#             ('flush system', 'sawdust', mock_manure_handler_config,
#              FlushSystem, SawdustBedding, mock_manure_handler_config),
#             ('manual scraping', 'sawdust', mock_manure_handler_config,
#              ManualScraping, SawdustBedding, mock_manure_handler_config),
#             ('alley scraper', 'sawdust', mock_manure_handler_config,
#              AlleyScraper, SawdustBedding, mock_manure_handler_config),
#             ('dummy', 'sawdust', mock_manure_handler_config,
#              FlushSystem, SawdustBedding, mock_manure_handler_config),
#         ])
# def test_manure_handler_factory_get_instance(manure_handler_type_name: str,
#                                              bedding_type_name: str,
#                                              manure_handler_config: ManureHandlerConfig,
#                                              expected_manure_handler_class: BaseManureHandler,
#                                              expected_bedding_type: BaseBedding,
#                                              expected_manure_handler_config: ManureHandlerConfig) \
#         -> None:
#     """Unit test for get_instance() of class ManureHandlerFactory"""
#
#     # Act
#     manure_handler = ManureHandlerFactory.get_instance(manure_handler_type_name=manure_handler_type_name,
#                                                        custom_manure_handler_config=manure_handler_config)
#
#     # Assert
#     assert type(manure_handler) is expected_manure_handler_class
#     assert type(manure_handler.bedding) is expected_bedding_type
#     assert manure_handler.config == expected_manure_handler_config
#     assert manure_handler.milking_parlor is not None
#     assert manure_handler.all_output is not None
#     assert len(manure_handler.all_output) == 0
#     assert manure_handler.last_output is None
#
#
# def test_manure_handler_daily_update(mocker: MockerFixture) -> None:
#     """Unit test for daily_update() of class BaseManureHandler in file manure_handler_classes.py"""
#
#     # Arrange
#     pen = mocker.MagicMock(autospec=ManureManagementPen)
#     pen.num_animals = 100
#     flush_system = ManureHandlerFactory.get_instance('flush system')
#     flush_system.config.cleaning_water_use_rate = 20.0
#
#     # Act
#     daily_output1 = flush_system.daily_update(pen, sim_day=1)
#     daily_output2 = flush_system.daily_update(pen, sim_day=2)
#
#     # Assert
#     assert flush_system.cleaning_water_volume_in_main_barn(pen) == approx(2000.0)
#     assert len(flush_system.all_output) == 2
#     assert daily_output1 == flush_system.all_output[0]
#     assert daily_output2 == flush_system.all_output[1]
#     assert daily_output1.simulation_day == 1
#     assert daily_output2.simulation_day == 2
#     assert daily_output2 == flush_system.last_output
#     assert all([type(daily_output) is ManureHandlerDailyOutput for daily_output in flush_system.all_output])
