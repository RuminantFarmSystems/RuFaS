from tkinter.ttk import Separator
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import BaseManureHandler, ManureHandlerFactory
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseSeparator
from pytest import fixture
from unittest.mock import Mock, MagicMock

from pytest_mock import MockerFixture

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import BaseReceptionPit
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput

from RUFAS.routines.manure_management.treatments.treatment_classes import AnaerobicDigestion, TreatmentEnum
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
def pen0(mocker: MockerFixture, cow: Cow) -> Pen:
    p0 = mocker.MagicMock(spec=Pen)
    p0.id = 0
    p0.animals_in_pen = [cow] * 20
    p0.classes_in_pen = {cow.__class__}
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
def mock_pen(mocker:MockerFixture) ->SimplePen:
    pen = mocker.MagicMock(spec=SimplePen)
    return pen

@fixture
def mock_handler(mocker:MockerFixture)->BaseManureHandler:
    manure_handler = mocker.MagicMock(spec=BaseManureHandler)
    return manure_handler

@fixture
def mock_separator(mocker:MockerFixture,mock_reception_pit)->BaseSeparator:
    manure_separator = mocker.MagicMock(spec=BaseSeparator)
    manure_separator.reception_pit = mock_reception_pit
    return manure_separator



@fixture
def mock_reception_pit_output(mocker:MockerFixture)->ReceptionPitOutput:
    sample_output_reception_pit = mocker.MagicMock(spec=ReceptionPitOutput)
    sample_output_reception_pit.manure_nitrogen = 1.0
    sample_output_reception_pit.TSd= 10.0
    sample_output_reception_pit.VSd = 2.0
    sample_output_reception_pit.VSnd = 1.0
    sample_output_reception_pit.VS_total = 3.0
    sample_output_reception_pit.p_excrt_manure = 1.0
    sample_output_reception_pit.K_manure= 1.0
    sample_output_reception_pit.total_daily_mass = 100.0
    return sample_output_reception_pit

@fixture
def mock_reception_pit_output_zeros(mocker:MockerFixture)->ReceptionPitOutput:
    sample_output_reception_pit = mocker.MagicMock(spec=ReceptionPitOutput)
    sample_output_reception_pit.manure_nitrogen = 0.0
    sample_output_reception_pit.TSd= 0.0
    sample_output_reception_pit.VSd = 0.0
    sample_output_reception_pit.VSnd = 0.0
    sample_output_reception_pit.VS_total = 0.0
    sample_output_reception_pit.p_excrt_manure = 0.0
    sample_output_reception_pit.K_manure= 0.0
    sample_output_reception_pit.total_daily_mass = 1.0
    return sample_output_reception_pit

@fixture
def mock_reception_pit(mocker:MockerFixture, mock_reception_pit_output)->BaseReceptionPit:
    reception_pit = mocker.MagicMock(spec=BaseReceptionPit)
    sample_output_reception_pit = mock_reception_pit_output
    reception_pit.last_output = mock_reception_pit_output
    return reception_pit

@fixture
def mock_reception_pit_zeros(mocker:MockerFixture, mock_reception_pit_output_zeros)->BaseReceptionPit:
    reception_pit = mocker.MagicMock(spec=BaseReceptionPit)
    sample_output_reception_pit = mock_reception_pit_output_zeros
    reception_pit.last_output = mock_reception_pit_output_zeros
    return reception_pit

@fixture
def mock_weather_data():
    weather_data = Mock()
    weather_data.T_avg = 25
    return weather_data

@fixture
def init_data(mocker:MockerFixture)->AnaerobicDigesterInitData:
    init_data = mocker.MagicMock(spec=AnaerobicDigesterInitData)
    init_data.sludge_accumulation_volume = 0.0  
    init_data.hydraulic_retention_time = 25  
    init_data.sludge_accumulation_period = 1.0  
    init_data.SAV_FRACTION = 0.03  

    init_data.TOP_COVER_VOLUME_FRACTION = 0.2  
    init_data.BIOGAS_GEN_RATIO = 0.38  

    init_data.EVAPORATION_FRACTION = 0.02  
    init_data.TS_FRACTION = 0.45  
    init_data.VS_FRACTION = 0.40  
    init_data.N_FRACTION = 0.01  
    init_data.P_FRACTION = 0.01  
    init_data.K_FRACTION = 0.0  

    init_data.AD_TEMP_SETPOINT= 37.5
    init_data.AD_TEMP= 37.5

    return init_data
 
@fixture
def ad_fixture(pen0,mock_handler,mock_separator,init_data,mock_reception_pit,mock_weather_data):

    pen= pen0
    manure_handler= mock_handler
    manure_separator= mock_separator
    init_data = init_data
    reception_pit = mock_reception_pit
    weather_data = mock_weather_data

    ad = AnaerobicDigestion(pen=pen,manure_handler=manure_handler,manure_separator=manure_separator, \
        treatment_init_data=init_data,reception_pit=reception_pit,weather_data=weather_data)
    return ad

@fixture
def ad_fixture_zeros(pen0,mock_handler,mock_separator,init_data,mock_reception_pit_zeros,mock_weather_data):

    pen= pen0
    manure_handler= mock_handler
    manure_separator= mock_separator
    init_data = init_data
    reception_pit = mock_reception_pit_zeros
    weather_data = mock_weather_data

    ad = AnaerobicDigestion(pen=pen,manure_handler=manure_handler,manure_separator=manure_separator, \
        treatment_init_data=init_data,reception_pit=reception_pit,weather_data=weather_data)
    return ad

@fixture
def get_expected_values():
    expected_values=Mock()
    ##Non-daily_output values
    expected_values.moisture_content=0.90
    expected_values.input_energy_heating=0.0
    expected_values.sludge_accumulation_volume=0.0
    expected_values.minimum_digester_volume=1.0
    expected_values.top_cover_volume=0.2
    expected_values.energy_content=0.0
    expected_values.evaporated_water=0.0
    #daily_output values
    expected_values.urea=0.0
    expected_values.TAN_s=0.0
    expected_values.manure_nitrogen=0.0
    expected_values.TSd=0.0
    expected_values.VSd=0.0
    expected_values.VSnd=0.0
    expected_values.VS_total=0.0
    expected_values.p_excrt_manure=0.0
    expected_values.K_manure=0.0
    expected_values.total_daily_mass=0.0
    expected_values.AD_effluent_volume=0.0
    expected_values.AD_biogas=0.0
    expected_values.AD_biogas_energy_content=0.0
    expected_values.AD_methane_generation_volume=0.0
    expected_values.AD_input_energy_heating=0.0
    return expected_values


@fixture
def get_expected_values_zeros():
    expected_values=MagicMock()
    ##Non-daily_output values
    expected_values.moisture_content=0.0
    expected_values.input_energy_heating=0.0
    expected_values.sludge_accumulation_volume=0.0
    expected_values.minimum_digester_volume=0.0
    expected_values.top_cover_volume=0.0
    expected_values.energy_content=0.0
    expected_values.evaporated_water=0.0
    #daily_output values
    expected_values.urea=0.0
    expected_values.TAN_s=0.0
    expected_values.manure_nitrogen=0.0
    expected_values.TSd=0.0
    expected_values.VSd=0.0
    expected_values.VSnd=0.0
    expected_values.VS_total=0.0
    expected_values.p_excrt_manure=0.0
    expected_values.K_manure=0.0
    expected_values.total_daily_mass=0.0
    expected_values.AD_effluent_volume=0.0
    expected_values.AD_biogas=0.0
    expected_values.AD_biogas_energy_content=0.0
    expected_values.AD_methane_generation_volume=0.0
    expected_values.AD_input_energy_heating=0.0
    return expected_values