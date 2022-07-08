from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import ManureHandlerFactory
from pytest import fixture


from pytest_mock import MockerFixture

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen

from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.manual_scraping import ManualScraping
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.manual_scraping import ManualScraping
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler

from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import BaseReceptionPit
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput

from RUFAS.routines.manure_management.treatments.treatment_classes import AnaerobicDigestion
from RUFAS.routines.manure_management.treatments.treatment_classes import AnaerobicDigesterInitData
from RUFAS.routines.manure_management.misc.daily_variables import DailyVariables

@fixture
def default_daily_vars_obj() -> DailyVariables:
    return DailyVariables()

@fixture
def cow(mocker: MockerFixture) -> Cow:
    cw = mocker.MagicMock(spec=Cow)
    return cw


@fixture
def pen0(mocker: MockerFixture, calf: Calf) -> Pen:
    p0 = mocker.MagicMock(spec=Pen)
    p0.id = 0
    p0.animals_in_pen = [calf] * 20
    p0.classes_in_pen = {calf.__class__}
    p0.housing_type = 'open air barn'
    p0.bedding_type = 'sand'
    p0.manure_handling = 'manual_scraping'
    p0.manure_separator = 'sedimentation'
    p0.manure_storage = 'storage_pit'
    p0.manure = {
        'U': 0,
        'TAN_s': 0,
        'MN': 0,
        'Mkg': 0,
        'TSd': 0,
        'VSd': 0,
        'VSnd': 0,
        'WIP_frac': 0,
        'WOP_frac': 0,
        'p_excrt_manure': 0,
        'p_frac': 0,
        'K_manure': 0,
        'CH4_manure': 0
    }
    return p0


@fixture
def simple_pen0(pen0: Pen) -> SimplePen:
    return SimplePen(pen0)

@fixture
def manure_handler0():
    pen0 = simple_pen0(Pen)
    return ManualScraping(pen=pen0)


"""
TODO: Ask about configuration. The manure separator needs reception pit as input.
 Reception pit needs manure handler, 
 and manure handler needs separator. This is cyclic.
"""  
@fixture
def manure_separator0():
    pass

@fixture
def reception_pit0():
    manure_handler = manure_handler0()
    return BaseReceptionPit(manure_handler=manure_handler) 

## TODO: Write test for actual weather api
class MockWeatherData:
    def __init__(self):
        self.T_avg = 25
@fixture
def mock_weather_data():
    weather_data = MockWeatherData()
    return weather_data

@fixture
def init_data0():
    return AnaerobicDigesterInitData
 
@fixture
def anaerobic_digestion0():
    pen = simple_pen0
    manure_handler = manure_handler0()
    manure_separator = manure_separator0()
    init_data = init_data0()
    weather_data = mock_weather_data()
    return AnaerobicDigestion(pen=pen,manure_handler=manure_handler,manure_separator=manure_separator, \
        treatment_init_data=init_data,weather_data=weather_data)

 