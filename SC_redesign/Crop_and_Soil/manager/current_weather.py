from dataclasses import dataclass
from typing import Optional
from juliandate import juliandate
import numpy


from RUFAS.classes import Weather

"""
The purpose of this class is to combine and covert infos from weather data and field data and creates a 
current weather class that have all the needed attributes to allow field and field manager to work properly.

Notes
-------
_deg_trig and _determine_daylength are more of temporary methods that approximately estimates the day length, this will 
be revisited for a more accurate implementation post v1
"""


@dataclass
class CurrentWeather:
    """class containing the current day's weather, used by the crop class"""  # TODO: useful for entire RUFAS model?
    incoming_light: Optional[float] = None
    """incoming light radiation energy (MJ/m)"""
    min_air_temperature: Optional[float] = None
    """minimum air temperature for the day (C)"""
    mean_air_temperature: Optional[float] = None
    """average air temperature for the day (C)"""
    max_air_temperature: Optional[float] = None
    """maximum air temperature for the day (C)"""
    daylength: Optional[float] = None
    """Length of time from sunup to sundown on the day (hours)"""
    annual_mean_air_temperature: Optional[float] = None
    """average annual air temperature for the year (C)"""
    snow_fall: float = 0    # TODO: make this better integrated with Soil module
    """amount of snow that falls on the day (mm)"""
    rainfall: float = 0
    """amount of rainfall that occurs on the day (mm)"""

    @classmethod
    def check_current_weather(cls, weather: Weather, latitude: float, year: int,
                              month: int, day: int) -> 'CurrentWeather':
        """creates a CurrentWeather object by extracting the relevant values for the current day from a Weather
        object"""
        cls.incoming_light = weather.radiation
        cls.min_air_temperature = weather.T_min
        cls.mean_air_temperature = weather.T_avg
        cls.max_air_temperature = weather.T_max
        cls.annual_mean_air_temperature = weather.T_avg_annual
        cls.rainfall = weather.rainfall
        cls.daylength = _determine_daylength(latitude=latitude, year=year, month=month, day=day)
        return CurrentWeather()  # TODO: placeholder for typing, needs implementation


def _deg_trig(degree, fun=numpy.sin):
    """apply a trig function that expects radians to degrees
    ​
    Parameters
    ----------
    degree: the angle in degrees
    fun: the trig function to apply, defaults to sin
    ​
    Returns
    -------
    the result of the trig function
    """
    radian = degree * (numpy.pi / 180)
    return fun(radian)


def _determine_daylength(latitude: float, year: int, month: int, day: int, is_sea_horizon=False,
                         longtitude=-89.401230, elevation=266.09) -> float:
    """Calculates the daylength"""
    # Step 1: Calculate days since 1/1/2000
    # year_zero = 1721060.5
    y2k = 2451545.0
    jDate = juliandate.from_gregorian(year, month, day)  # Julian (Astronomical) Date
    # JDate = year_zero + (year * 365.2508) + day_of_year  # Julian Date - rudimentary method
    n = jDate - y2k + 0.0008
    # Step 2: Mean solar time
    Jstar = n - (longtitude / 360)
    # Step 3: Solar mean anomaly
    mean_anomaly = (357.5291 + (09.8560028 * Jstar)) % 360
    # Step 4: Equation of the center
    earth_coef = 1.9148
    C = (earth_coef * _deg_trig(mean_anomaly)) + (0.0200 * _deg_trig(2 * mean_anomaly)) +\
        (0.0003 * _deg_trig(3 * mean_anomaly))
    # Step 5: Ecliptic longitude
    arg_of_perihelion = 102.9372
    lamb = (mean_anomaly + C + 180 + arg_of_perihelion) % 360
    # Step 6: Solar transit
    equation_of_time = (0.0053 * _deg_trig(mean_anomaly)) - (0.0069 * _deg_trig(2 * lamb))  # zelda vibes
    JTransit = y2k + Jstar + equation_of_time
    # Step 7: Declination of the Sun
    maximum_tilt = 23.44
    sin_delta = _deg_trig(lamb) * _deg_trig(maximum_tilt)
    delta = _deg_trig(sin_delta, numpy.arcsin)  # actual declination  # --- Praise the Sun!! ---
    # Step 8: Hour angle
    elev_factor = -0.83
    if is_sea_horizon:
        elev_factor += -2.076 * numpy.sqrt(elevation) / 60

    cos_w = (_deg_trig(elev_factor) - (_deg_trig(latitude) * sin_delta)) / (
                _deg_trig(latitude, numpy.cos) * _deg_trig(delta, numpy.cos))
    w = _deg_trig(cos_w, numpy.arccos)  # actual hour angle

    # Step 9: sunrise and sunset
    JRise = JTransit - (w / 360)
    JSet = JTransit + (w / 360)

    length = juliandate.__h_m_s(JSet-JRise)

    return length[0]
