import csv

from RUFAS import errors
from RUFAS.util import Utility


class Weather:

    def __init__(self, weather_file, config):
        """
        Description:
            Contains daily weather information stored in 2D lists
            Data lists are in the format Data[year][julian_day].
            Allows daily information to be accessed by indexing to
            [time.year - 1][time.day - 1] (list indexing starts at 0,
            time starts at 1)

        Args:
            weather_file: path to the weather file specified in the json file
            config: instance of the Config class containing information necessary
                to initialize the Weather object
        """

        years = config.years
        w_start_year = config.w_start_year
        w_start_day = config.w_start_day
        start_year = config.start_year
        start_day = config.start_day

        # initialize data sets
        self.rainfall = []
        self.T_max = []
        self.T_min = []
        self.T_avg = []
        self.radiation = []
        self.irrigation = []
        self.T_avg_annual = []

        year_length = config.year_length
        leap_year_length = config.leap_year_length

        # calculate the number of days between the beginning of
        # the weather file and the next year
        if Utility.is_leap_year(w_start_year):
            w_day_offset = leap_year_length - w_start_day
        else:
            w_day_offset = year_length - w_start_day

        # calculates the amount of days between the start day of the weather
        # file and the start day of the simulation
        if start_year == w_start_year:
            days_to_start = start_day - w_start_day
        elif start_year == w_start_year + 1:
            days_to_start = w_day_offset + start_day
        else:
            days_to_start = w_day_offset + start_day
            temp_year = w_start_year + 1
            while temp_year < start_year:
                if Utility.is_leap_year(temp_year):
                    days_to_start += leap_year_length
                else:
                    days_to_start += year_length
                temp_year += 1

        # fill the weather arrays with zeros for the size of each year in years[]
        for year in years:
            self.rainfall.append([0.0 for _ in range(len(year))])
            self.T_max.append([0.0 for _ in range(len(year))])
            self.T_min.append([0.0 for _ in range(len(year))])
            self.T_avg.append([0.0 for _ in range(len(year))])
            self.radiation.append([0.0 for _ in range(len(year))])
            self.irrigation.append([0.0 for _ in range(len(year))])

        # read in the input csv file
        weather_full_path = Utility.get_base_dir() / 'input/weather' / weather_file

        if not weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")

        with weather_full_path.open('r') as f:
            readCSV = csv.reader(f, delimiter=',')

            # this for loop takes the weather data and parses it into multiple
            # 2D arrays [year][day] for different weather variables used by the
            # module
            current_row = 0
            year = 0
            day = start_day
            # used to offset pointer to the start of the simulation
            # in the weather file
            counter = 0
            skips = 0
            offset = 1
            for row in readCSV:
                # limits weather data read in to the length of the simulation
                if year > len(years) - 1:
                    break

                # if a line is empty then skip it
                if len(row) == 0:
                    skips += 1
                    continue

                # sets a pointer to the start date of the simulation in the weather file
                if counter < days_to_start:
                    counter += 1
                    continue

                # row 0 contains variable names
                if current_row != 0:
                    # try/except statement to catch faulty weather data
                    try:
                        # fill data at appropriate location
                        self.rainfall[year][day - offset] = float(row[2])
                        self.T_max[year][day - offset] = float(row[3])
                        self.T_min[year][day - offset] = float(row[4])
                        self.T_avg[year][day - offset] = float(row[5])
                        self.radiation[year][day - offset] = float(row[6])
                        self.irrigation[year][day - offset] = float(row[7])
                    except(IndexError, ValueError):
                        # prints out each problematic row in the weather CSV file
                        skips += 1
                        if skips == 1:
                            print("Weather CSV file has invalid data in: " + weather_full_path.name
                                  + "\nInvalid rows that are skipped:")
                        if skips <= 5:
                            print("Row: " + str(current_row + skips + days_to_start) + "")
                        continue

                    # iterate year counter accounting for leap years
                    if day == len(years[year]):
                        year += 1
                        day = 0

                    day += 1

                current_row += 1

            # prints if there are more than 5 skipped lines in order to
            # prevent console clutter
            if skips > 5:
                print("Only printing first 5 invalid rows, there are " + str(skips)
                      + " total invalid rows")

            # calculates T_avg_annual for each year
            for i in range(len(years)):
                avg = sum(self.T_avg[i]) / (len(years[i]))
                self.T_avg_annual.append(avg)

            if len(years) > 2:
                T_avg = sum([self.T_avg_annual[j] for j in range(1, len(self.T_avg_annual) - 1)]) \
                        / (len(self.T_avg_annual) - 2)
            else:
                T_avg = sum([self.T_avg_annual[j] for j in range(len(self.T_avg_annual))]) \
                        / len(self.T_avg_annual)

            self.T_avg_annual[0] = T_avg
            self.T_avg_annual[len(self.T_avg_annual) - 1] = T_avg
