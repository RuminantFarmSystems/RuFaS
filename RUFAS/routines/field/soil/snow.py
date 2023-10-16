from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

im = InputManager()
om = OutputManager()


class Snow:
    snow_content = 0

    def __init__(self, snow_content):
        self.snow_content = snow_content

    def calc_snow_temp(self, date: str) -> float:
        """
        This function calculates the snow pack temperature based on equation 1:2.5.1 in SWAT 2009 Theoretical
        Documentation. According to the equation, T_snow_day_n = T_snow_day_(n-1) * (1 - l_sno) + T_av * l_sno, where
        T_snow_day_(n-1) is the snow pack temperature of the previous day, T_av is the mean air temperature on the
        current day in Celsius, and l_sno is a lagging factor the accounts for snow pack density, snow pack depth,
        exposure and other factors affecting snow pack temperature. However, the l_sno term is set to a default value of
        1.0 as described in the SWAT 2012 Input/Output: .BSN documentation. This means that mathematically, the snow
        pack temperature on the current day is the same as the current day average air temperature.
        Parameters
        ----------
        date: str
            The date of which snow temperature to be calculated

        """
        t_snow_nminus1 = 0.0
        l_sno = 1.0
        print(im.get_data('weather'))
        return 0.0


# if __name__ == '__main__':
#     snow = Snow(0.0)
#     snow.calc_snow_temp('')
