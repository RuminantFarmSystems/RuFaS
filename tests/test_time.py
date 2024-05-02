from datetime import date
from typing import Dict, Any

import pytest
from unittest.mock import patch
from pytest_mock import MockerFixture

from RUFAS.time import Time


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    config = {
        "start_date": "1999:2",
        "end_date": "2000:1",
        "start_year_int": 1999,
        "calendar_year": 1999,
        "years": [
            [
                None,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                41,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
                49,
                50,
                51,
                52,
                53,
                54,
                55,
                56,
                57,
                58,
                59,
                60,
                61,
                62,
                63,
                64,
                65,
                66,
                67,
                68,
                69,
                70,
                71,
                72,
                73,
                74,
                75,
                76,
                77,
                78,
                79,
                80,
                81,
                82,
                83,
                84,
                85,
                86,
                87,
                88,
                89,
                90,
                91,
                92,
                93,
                94,
                95,
                96,
                97,
                98,
                99,
                100,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
                112,
                113,
                114,
                115,
                116,
                117,
                118,
                119,
                120,
                121,
                122,
                123,
                124,
                125,
                126,
                127,
                128,
                129,
                130,
                131,
                132,
                133,
                134,
                135,
                136,
                137,
                138,
                139,
                140,
                141,
                142,
                143,
                144,
                145,
                146,
                147,
                148,
                149,
                150,
                151,
                152,
                153,
                154,
                155,
                156,
                157,
                158,
                159,
                160,
                161,
                162,
                163,
                164,
                165,
                166,
                167,
                168,
                169,
                170,
                171,
                172,
                173,
                174,
                175,
                176,
                177,
                178,
                179,
                180,
                181,
                182,
                183,
                184,
                185,
                186,
                187,
                188,
                189,
                190,
                191,
                192,
                193,
                194,
                195,
                196,
                197,
                198,
                199,
                200,
                201,
                202,
                203,
                204,
                205,
                206,
                207,
                208,
                209,
                210,
                211,
                212,
                213,
                214,
                215,
                216,
                217,
                218,
                219,
                220,
                221,
                222,
                223,
                224,
                225,
                226,
                227,
                228,
                229,
                230,
                231,
                232,
                233,
                234,
                235,
                236,
                237,
                238,
                239,
                240,
                241,
                242,
                243,
                244,
                245,
                246,
                247,
                248,
                249,
                250,
                251,
                252,
                253,
                254,
                255,
                256,
                257,
                258,
                259,
                260,
                261,
                262,
                263,
                264,
                265,
                266,
                267,
                268,
                269,
                270,
                271,
                272,
                273,
                274,
                275,
                276,
                277,
                278,
                279,
                280,
                281,
                282,
                283,
                284,
                285,
                286,
                287,
                288,
                289,
                290,
                291,
                292,
                293,
                294,
                295,
                296,
                297,
                298,
                299,
                300,
                301,
                302,
                303,
                304,
                305,
                306,
                307,
                308,
                309,
                310,
                311,
                312,
                313,
                314,
                315,
                316,
                317,
                318,
                319,
                320,
                321,
                322,
                323,
                324,
                325,
                326,
                327,
                328,
                329,
                330,
                331,
                332,
                333,
                334,
                335,
                336,
                337,
                338,
                339,
                340,
                341,
                342,
                343,
                344,
                345,
                346,
                347,
                348,
                349,
                350,
                351,
                352,
                353,
                354,
                355,
                356,
                357,
                358,
                359,
                360,
                361,
                362,
                363,
                364,
                365,
            ],
            [1],
        ],
        "leap_year_length": 366,
        "year_length": 365,
    }
    return config


@pytest.fixture
def mock_time(mock_config: Dict[str, Any], mocker: MockerFixture) -> Time:
    mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)
    return Time()


def test_time_initialization(mock_config: Dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that Time instances are created correctly."""

    mock_im_get_data = mocker.patch("RUFAS.input_manager.InputManager.get_data", return_value=mock_config)

    time = Time()

    mock_im_get_data.assert_called_once_with("config")
    assert time.start_year_int == mock_config["start_year_int"] and time.calendar_year == mock_config["calendar_year"]
    assert time.leap_year_length == mock_config["leap_year_length"]
    assert time.year_length == mock_config["year_length"]
    assert time.day == 2
    assert time.simulation_day == 0
    assert time.year == 1
    assert time.years == mock_config["years"]


def test_advance(mock_time: Time) -> None:
    """Tests that Time instances are advanced correctly."""
    time = mock_time
    for n in range(364):
        time.advance()
        assert time.simulation_day == n + 1
        assert time.day == 3 + n
        assert time.year == 1
        assert time.calendar_year == 1999

    time.advance()
    assert time.simulation_day == 365
    assert time.day == 1
    assert time.year == 2
    assert time.calendar_year == 2000


def test_end_year(mock_time: Time) -> None:
    """Tests that Time instances correctly determine if it is the end of a year."""
    time = mock_time
    for _ in range(364):
        assert not time.end_year()
        time.advance()
    assert time.end_year()


def test_end_simulation(mock_time: Time) -> None:
    """Tests that Time instances correctly determine if the simulation has ended."""
    # case when year is less than the length of years list
    time = mock_time
    for _ in range(366):
        assert not time.end_simulation()
        time.advance()
    assert time.end_simulation()


def test_record_time(mock_time: Time) -> None:
    """Tests that Time instances correctly add current time information to the OutputManager."""
    time = mock_time
    with patch("RUFAS.output_manager.OutputManager.add_variable") as add_var:
        time.record_time()
        assert add_var.call_count == 4


def test_is_last_day_of_simulation(mock_time: Time) -> None:
    """Tests that Time instances correctly determine if current day is last day of a simulation."""
    time = mock_time
    for _ in range(365):
        assert not time.is_last_day_of_simulation
        time.advance()
    assert time.is_last_day_of_simulation


@pytest.mark.parametrize(
    "start_date_str, simulation_day, expected_date",
    [
        # Year 2023
        ("2023:1", 1, date(2023, 1, 1)),
        ("2023:1", 365, date(2023, 12, 31)),
        # Year 2024 (Leap Year)
        ("2024:1", 1, date(2024, 1, 1)),
        ("2024:1", 366, date(2024, 12, 31)),
        ("2024:15", 17, date(2024, 1, 31)),
    ],
)
def test_convert_simulation_day_to_date(
    mocker: MockerFixture, start_date_str: str, simulation_day: int, expected_date: date
) -> None:
    """
    Unit test for the convert_simulation_day_to_date method of the Time class.
    """

    # Arrange
    mocker.patch("RUFAS.time.Time.__init__", return_value=None)
    time = Time()
    year, doy = start_date_str.split(":")
    time.start_full_date = [year, doy]

    # Act
    actual_date = time.convert_simulation_day_to_date(simulation_day)

    # Assert
    assert actual_date == expected_date
