from pytest import fixture
from unittest.mock import Mock, MagicMock
from pytest_mock import MockerFixture
from tkinter.ttk import Separator
from RUFAS.time import Time
from RUFAS.weather import Weather

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import BaseReceptionPit
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import BaseManureHandler
from RUFAS.routines.manure_management.manure_handlers.manure_handler_output import ManureHandlerOutput
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure_management.manure_treatments.treatment_classes import AnaerobicDigestion, AnaerobicLagoon, TreatmentType, SlurryStorageOutdoor, SlurryStorageUnderfloor
from RUFAS.routines.manure_management.manure_treatments.treatment_classes import ManureTreatmentConfig
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
    p0.manure_management = 'storage_pit'
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
def mock_handler_output(mocker:MockerFixture)->ManureHandlerOutput:
    sample_output = mocker.MagicMock(spec=ManureHandlerOutput)
    sample_output.manure_nitrogen = 0
    sample_output.TSd= 2548.70
    sample_output.VSd = 1980.94
    sample_output.VSnd = 0.0
    sample_output.VS_total = 1980.94
    sample_output.p_excrt_manure = 0
    sample_output.K_manure= 0
    sample_output.total_daily_mass = 270015
    sample_output.cleaning_water = 249000
    sample_output.TAN_s = 0.0
    return sample_output

@fixture
def mock_reception_pit_output(mocker:MockerFixture)->ReceptionPitOutput:
    sample_output = mocker.MagicMock(spec=ReceptionPitOutput)
    sample_output.manure_nitrogen = 0
    sample_output.TSd= 2548.70
    sample_output.VSd = 1980.94
    sample_output.VSnd = 0.0
    sample_output.VS_total = 1980.94
    sample_output.p_excrt_manure = 0
    sample_output.K_manure= 0
    sample_output.total_daily_mass = 270015
    return sample_output

@fixture
def mock_handler(mocker:MockerFixture, mock_handler_output)->BaseManureHandler:
    manure_handler = mocker.MagicMock(spec=BaseManureHandler)
    manure_handler.last_output = mock_handler_output
    return manure_handler
@fixture
def mock_time(mocker:MockerFixture)->Time:
    time = mocker.MagicMock(spec=Time)
    return time

@fixture
def mock_weather(mocker:MockerFixture)->Weather:
    weather = mocker.MagicMock(spec=Weather)
    return weather

@fixture
def mock_separator(mocker:MockerFixture,mock_reception_pit,mock_handler)->BaseManureSeparator:
    manure_separator = mocker.MagicMock(spec=BaseManureSeparator)
    manure_separator.reception_pit = mock_reception_pit
    manure_separator.manure_handler = mock_handler
    return manure_separator

@fixture
def mock_reception_pit(mocker:MockerFixture, mock_reception_pit_output)->BaseReceptionPit:
    reception_pit = mocker.MagicMock(spec=BaseReceptionPit)
    sample_output_reception_pit = mock_reception_pit_output
    reception_pit.last_output = mock_reception_pit_output
    return reception_pit

@fixture
def mock_ad_init_data(mocker:MockerFixture)->ManureTreatmentConfig:
    init_data = mocker.MagicMock(spec=ManureTreatmentConfig)
    init_data.hydraulic_retention_time = 25  
    init_data.sludge_accumulation_period = 1.0  
    init_data.SAV_fraction = 0.03
    init_data.top_cover_volume_fraction = 0.2
    init_data.biogas_gen_ratio = 0.38
    init_data.evaporation_fraction = 0.02

    init_data.TS_removal_efficiency = 0.45  
    init_data.VS_removal_efficiency = 0.40  
    init_data.N_removal_efficiency = 0.0  
    init_data.P_removal_efficiency = 0.0  
    init_data.K_removal_efficiency = 0.0  

    init_data.AD_temp_set_point= 37.5
    init_data.AD_temp= 37.5
    return init_data

@fixture
def mock_lagoon_init_data(mocker:MockerFixture)->ManureTreatmentConfig:
    init_data = mocker.MagicMock(spec=ManureTreatmentConfig)
    init_data.hydraulic_retention_time: int = 365  # 180 - 365 days
    init_data.sludge_accumulation_period: float = 5.0  # Sludge accumulation period 5-20 years
    init_data.SAV_fraction: float = 0.00251  # Sludge Accumulation volume fraction 0.00274-0.00455 of VS loaded

    init_data.percent_dry_solids = 1.0
    init_data.TS_removal_efficiency = 0.75 # Between 70-85%
    init_data.VS_removal_efficiency = 0.84 # Between 80-90%
    init_data.N_removal_efficiency = 0.75
    init_data.TAN_removal_efficiency = 0.75
    init_data.P_removal_efficiency = 0.65
    init_data.K_removal_efficiency = 0.24
    init_data.TS_DM_effluent_rate = 0.0
    return init_data
 
@fixture
def ad_fixture(pen0,mock_separator,mock_ad_init_data,mock_time,mock_weather):
    pen= pen0
    manure_separator= mock_separator
    init_data = mock_ad_init_data
    time=mock_time
    weather=mock_weather
    ad = AnaerobicDigestion(pen=pen, manure_separator=manure_separator, time=time, weather=weather, \
                            manure_treatment_config=init_data)
    return ad

@fixture
def get_expected_values_anaerobic_digestion(mock_handler_output):
    expected_values=Mock()
    expected_values.TSd = 1401.785
    expected_values.VSd = 1188.56
    expected_values.VSnd = 0
    expected_values.VS_total = 1188.56

    expected_values.manure_nitrogen = 0.0
    expected_values.p_excrt_manure = 0.0
    expected_values.K_manure = 0.0
    expected_values.total_daily_mass = mock_handler_output.total_daily_mass 
    expected_values.final_volume=mock_handler_output.total_daily_mass

    ##Non output variables check
    expected_values.moisture_content=0.9905
    
    expected_values.sludge_accumulation_volume=21.69
    expected_values.minimum_digester_volume=6763
    expected_values.top_cover_volume=1352.57
    expected_values.AD_biogas=475.4
    expected_values.AD_methane_generation_volume=309.0
    expected_values.AD_input_energy_heating=0.0

    expected_values.sludge_accumulation_volume=0.0
    expected_values.minimum_digester_volume=1.0
    expected_values.top_cover_volume=0.2
    expected_values.energy_content=0.0
    expected_values.evaporated_water=0.0
    return expected_values

@fixture
def al_fixture(pen0,mock_separator,mock_lagoon_init_data,mock_time,mock_weather):
    pen= pen0
    manure_separator= mock_separator
    init_data = mock_lagoon_init_data
    time=mock_time
    weather=mock_weather
    al = AnaerobicLagoon(pen=pen, manure_separator=manure_separator, time=time, weather=weather, \
                         manure_treatment_config=init_data)
    return al

@fixture
def get_expected_values_anaerobic_lagoon(mock_handler_output):
    expected_values=Mock()
    expected_values.TSd = 637
    expected_values.VSd = 297
    expected_values.VSnd = 0
    expected_values.VS_total = 297

    expected_values.manure_nitrogen = 0
    expected_values.TAN_s = 185
    expected_values.p_excrt_manure = 0
    expected_values.K_manure = 0
    expected_values.total_daily_mass= mock_handler_output.total_daily_mass

    ## Sizing Expected values
    expected_values.flushing_recycled= 249
    expected_values.reduced_volume= 21
    expected_values.minimum_treatment_volume= 7940
    expected_values.sludge_accumulation_volume = 23350
    expected_values.volume_needed = 31290

    expected_values.a= 10.971
    expected_values.b = -106.989
    expected_values.c = -31029.37
    expected_values.lagoon_width = 58.28
    expected_values.lagoon_length = 174.84
    expected_values.lagoon_surface_area = 10190
    expected_values.precip = 259
    expected_values.freeboard = 3106
    expected_values.total_lagoon_volume = 34655
    
    return expected_values


@fixture
def mock_ssuf_init_data(mocker:MockerFixture)->ManureTreatmentConfig:
    init_data = mocker.MagicMock(spec=ManureTreatmentConfig)
    init_data.percent_dry_solids = 1.0

    init_data.TS_removal_efficiency = 0.1  # Between 10-30%
    init_data.VS_removal_efficiency = 0.85  # Between 80-90%
    init_data.N_removal_efficiency = 0.1  # # Between 10-30%
    init_data.TAN_removal_efficiency = 0.45  # Between 61-80%
    init_data.P_removal_efficiency = 0.05  # # Between 5-30%
    init_data.K_removal_efficiency = 0.05  # # Between 5-30%
    init_data.TS_DM_effluent_rate = 0.0
    return init_data
 
@fixture
def ssuf_fixture(pen0,mock_separator,mock_ssuf_init_data,mock_time,mock_weather):
    pen= pen0
    init_data = mock_ssuf_init_data
    manure_separator= mock_separator
    time=mock_time
    weather=mock_weather
    ssuf = SlurryStorageUnderfloor(pen=pen,manure_separator=manure_separator,time=time,weather=weather,treatment_init_data=init_data)
    return ssuf

@fixture
def get_expected_values_ssuf(mock_handler_output):
    ##TODO Update these values based on spreadsheet
    
    expected_values=Mock()
    expected_values.TSd = 2294
    expected_values.VSd = 1950
    expected_values.VSnd = 0
    expected_values.VS_total = 1950

    expected_values.manure_nitrogen = 1783
    expected_values.TAN_s = 338
    expected_values.p_excrt_manure = 66
    expected_values.K_manure = 129
    expected_values.total_daily_mass= mock_handler_output.total_daily_mass

    ## Sizing Expected values

    expected_values.minimum_treatment_volume= 7940
    expected_values.sludge_accumulation_volume = 23350
    expected_values.volume_needed = 31290

    expected_values.a= 10.971
    expected_values.b = -106.989
    expected_values.c = -31029.37
    expected_values.lagoon_width = 58.28
    expected_values.lagoon_length = 174.84
    expected_values.lagoon_surface_area = 10190
    expected_values.precip = 259
    expected_values.freeboard = 3106
    expected_values.total_lagoon_volume = 34655
    return expected_values
    
@fixture
def ssod_fixture(pen0,mock_separator,mock_ssuf_init_data,mock_time,mock_weather):
    pen= pen0
    init_data = mock_ssuf_init_data
    manure_separator= mock_separator
    time=mock_time
    weather=mock_weather
    ssuf = SlurryStorageOutdoor(pen=pen,manure_separator=manure_separator,time=time,weather=weather,treatment_init_data=init_data)
    return ssuf

@fixture
def get_expected_values_ssod(mock_handler_output):
    ##TODO Update these values based on spreadsheet
    expected_values=Mock()
    expected_values.TSd = 2294
    expected_values.VSd = 1950
    expected_values.VSnd = 0
    expected_values.VS_total = 1950

    expected_values.manure_nitrogen = 1783
    expected_values.TAN_s = 338
    expected_values.p_excrt_manure = 66
    expected_values.K_manure = 129
    expected_values.total_daily_mass= mock_handler_output.total_daily_mass

    ## Sizing Expected values

    expected_values.minimum_treatment_volume= 7940
    expected_values.sludge_accumulation_volume = 23350
    expected_values.volume_needed = 31290

    expected_values.a= 10.971
    expected_values.b = -106.989
    expected_values.c = -31029.37
    expected_values.lagoon_width = 58.28
    expected_values.lagoon_length = 174.84
    expected_values.lagoon_surface_area = 10190
    expected_values.precip = 259
    expected_values.freeboard = 3106
    expected_values.total_lagoon_volume = 34655
    return expected_values