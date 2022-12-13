from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.reception_pits.reception_pit import ReceptionPit
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput


# Test ReceptionPitDailyOutput
# ============================

def test_reception_pit_daily_output() -> None:
    """Unit test for the ReceptionPitDailyOutput class in file reception_pit_daily_output.py."""
    # Case 1: Use default values
    # Act
    reception_pit_daily_output = ReceptionPitDailyOutput()

    # Assert
    assert reception_pit_daily_output.pen_id == -1
    assert reception_pit_daily_output.simulation_day == -1
    assert reception_pit_daily_output.urea == 0.0
    assert reception_pit_daily_output.liquid_manure_total_ammoniacal_nitrogen == 0.0
    assert reception_pit_daily_output.liquid_manure_nitrogen == 0.0
    assert reception_pit_daily_output.liquid_manure_total_solids == 0.0
    assert reception_pit_daily_output.VSd == 0.0
    assert reception_pit_daily_output.VSnd == 0.0
    assert reception_pit_daily_output.liquid_manure_total_volatile_solids == 0.0
    assert reception_pit_daily_output.liquid_manure_phosphorus == 0.0
    assert reception_pit_daily_output.liquid_manure_potassium == 0.0
    assert reception_pit_daily_output.total_daily_manure_volume == 0.0
    assert reception_pit_daily_output.daily_volume == 0.0

    # --------------------

    # Case 2: Assign a value to each attribute in the initializer
    # Act
    reception_pit_daily_output = ReceptionPitDailyOutput(
            pen_id=1,
            simulation_day=1,
            urea=1.0,
            liquid_manure_total_ammoniacal_nitrogen=2.0,
            liquid_manure_nitrogen=3.0,
            liquid_manure_total_solids=4.0,
            VSd=5.0,
            VSnd=6.0,
            liquid_manure_total_volatile_solids=7.0,
            liquid_manure_phosphorus=8.0,
            liquid_manure_potassium=9.0,
            total_daily_manure_volume=10.0
    )

    # Assert
    assert reception_pit_daily_output.pen_id == 1
    assert reception_pit_daily_output.simulation_day == 1
    assert reception_pit_daily_output.urea == 1.0
    assert reception_pit_daily_output.liquid_manure_total_ammoniacal_nitrogen == 2.0
    assert reception_pit_daily_output.liquid_manure_nitrogen == 3.0
    assert reception_pit_daily_output.liquid_manure_total_solids == 4.0
    assert reception_pit_daily_output.VSd == 5.0
    assert reception_pit_daily_output.VSnd == 6.0
    assert reception_pit_daily_output.liquid_manure_total_volatile_solids == 7.0
    assert reception_pit_daily_output.liquid_manure_phosphorus == 8.0
    assert reception_pit_daily_output.liquid_manure_potassium == 9.0
    assert reception_pit_daily_output.total_daily_manure_volume == 10.0
    assert reception_pit_daily_output.daily_volume == 10.0

    # --------------------

    # Case 3: Pass in a dictionary to the initializer
    # Arrange
    data = {
        'pen_id': 1,
        'simulation_day': 1,
        'urea': 1.0,
        'liquid_manure_total_ammoniacal_nitrogen': 2.0,
        'liquid_manure_nitrogen': 3.0,
        'liquid_manure_total_solids': 4.0,
        'VSd': 5.0,
        'VSnd': 6.0,
        'liquid_manure_total_volatile_solids': 7.0,
        'liquid_manure_phosphorus': 8.0,
        'liquid_manure_potassium': 9.0,
        'total_daily_manure_volume': 10.0
    }

    # Act
    reception_pit_daily_output = ReceptionPitDailyOutput(**data)

    # Assert
    assert reception_pit_daily_output.pen_id == 1
    assert reception_pit_daily_output.simulation_day == 1
    assert reception_pit_daily_output.urea == 1.0
    assert reception_pit_daily_output.liquid_manure_total_ammoniacal_nitrogen == 2.0
    assert reception_pit_daily_output.liquid_manure_nitrogen == 3.0
    assert reception_pit_daily_output.liquid_manure_total_solids == 4.0
    assert reception_pit_daily_output.VSd == 5.0
    assert reception_pit_daily_output.VSnd == 6.0
    assert reception_pit_daily_output.liquid_manure_total_volatile_solids == 7.0
    assert reception_pit_daily_output.liquid_manure_phosphorus == 8.0
    assert reception_pit_daily_output.liquid_manure_potassium == 9.0
    assert reception_pit_daily_output.total_daily_manure_volume == 10.0
    assert reception_pit_daily_output.daily_volume == 10.0


# Test ReceptionPit
# =================

def test_daily_update(mocker: MockerFixture) -> None:
    """Unit test for the ReceptionPit.daily_update method in file reception_pit.py."""
    # Arrange
    mock_manure_handler_daily_output = mocker.MagicMock(auto_spec=ManureHandlerDailyOutput)
    mock_manure_handler_daily_output.simulation_day = sim_day = 1
    mock_manure_handler_daily_output.pen_id = pen_id = 1
    mock_manure_handler_daily_output.urea = urea = 1.0
    mock_manure_handler_daily_output.liquid_manure_total_ammoniacal_nitrogen = TAN = 2.0
    mock_manure_handler_daily_output.liquid_manure_nitrogen = N = 3.0
    mock_manure_handler_daily_output.liquid_manure_total_solids = TS = 4.0
    mock_manure_handler_daily_output.VSd = VSd = 5.0
    mock_manure_handler_daily_output.VSnd = VSnd = 6.0
    mock_manure_handler_daily_output.liquid_manure_total_volatile_solids = VS_total = 7.0
    mock_manure_handler_daily_output.liquid_manure_phosphorus = P = 8.0
    mock_manure_handler_daily_output.liquid_manure_potassium = K = 9.0
    mock_manure_handler_daily_output.total_daily_manure_volume = total_daily_manure_volume = 10.0

    mock_pen = mocker.MagicMock(auto_spec=ManureManagementPen)
    mock_pen.num_animals = num_animals = 100

    mock_bedding = mocker.MagicMock(auto_spec=BaseBedding)
    mock_bedding.calc_total_bedding_dry_solids.return_value = total_bedding_dry_solids = 11.0

    expected_TS = TS + total_bedding_dry_solids

    # Act
    reception_pit_daily_output = ReceptionPit.daily_update(
            manure_handler_daily_output=mock_manure_handler_daily_output,
            pen=mock_pen,
            bedding=mock_bedding
    )

    # Assert
    assert reception_pit_daily_output.simulation_day == sim_day
    assert reception_pit_daily_output.pen_id == pen_id
    assert reception_pit_daily_output.urea == approx(urea)
    assert reception_pit_daily_output.liquid_manure_total_ammoniacal_nitrogen == approx(TAN)
    assert reception_pit_daily_output.liquid_manure_nitrogen == approx(N)
    assert reception_pit_daily_output.liquid_manure_total_solids == approx(expected_TS)
    assert reception_pit_daily_output.VSd == approx(VSd)
    assert reception_pit_daily_output.VSnd == approx(VSnd)
    assert reception_pit_daily_output.liquid_manure_total_volatile_solids == approx(VS_total)
    assert reception_pit_daily_output.liquid_manure_phosphorus == approx(P)
    assert reception_pit_daily_output.liquid_manure_potassium == approx(K)
    assert reception_pit_daily_output.total_daily_manure_volume == approx(total_daily_manure_volume)
    assert reception_pit_daily_output.daily_volume == approx(total_daily_manure_volume)

    mock_bedding.calc_total_bedding_dry_solids.assert_called_once_with(num_animals)
