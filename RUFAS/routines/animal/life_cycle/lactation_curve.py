from RUFAS.input_manager import InputManager
import numpy as np
from scipy.integrate import quad

im = InputManager()


class LactationCurve:
    def __init__(self):
        self.region_dict = im.get_data("lactation.fips_region")

        self.year = im.get_data("config.end_date")[:4]
        if int(self.year) > 2016:
            self.year = "2016"

        self.FIPS_code = im.get_data("config.FIPS_county_code")
        self.FIPS_state_code = None 
        if self.FIPS_code != None: 
            self.FIPS_state_code= int(self.FIPS_code /1000)
        self.region = None
        if self.FIPS_state_code != None:
            for code_region in self.region_dict:
                if code_region["code"] == self.FIPS_state_code:
                    self.region= code_region["region"]
                    print(str(self.FIPS_state_code))
                    print(self.region)
                    print(code_region["code"])
                    print(code_region["region"])

        self.annual_MY_lbs = im.get_data("animal.herd_information.annual_milk_yield_lbs")  # int or None
        self.parity_percentages = im.get_data("animal.herd_information.parity_percentages")  # list of 3 floats
        self.num_milking_cows = im.get_data("animal.herd_information.cow_num") * (305 / 365)

        self.milking_freq = im.get_data("animal.animal_config.management_decisions.cow_times_milked_per_day")
        if self.milking_freq >= 2.5:
            self.milking_freq = "3x/d"
        else:
            self.milking_freq = "2x/d"

        # Assuming Y = 1632 and Z = 2196 based on the given assumptions
        self.P2_MY305_adj = im.get_data("lactation.parity_milk_adjustments.MY305_P2_adjustment")
        self.P3_MY305_adj = im.get_data("lactation.parity_milk_adjustments.MY305_P3_adjustment")

        self.adjustment_dict = im.get_data("lactation.adjustment_dict")

    def get_y_values_wood_curve(
        self, t: float, parameter_a: float, parameter_b: float, parameter_c: float
    ) -> np.float64:
        return parameter_a * np.power(t, parameter_b) * np.exp(-1 * parameter_c * t)

    def calc_integral_wood_curve(self, parameter_a: float, parameter_b: float, parameter_c: float) -> float:
        result, _ = quad(self.get_y_values_wood_curve, 1, 305, args=(parameter_a, parameter_b, parameter_c))
        return result

    def get_wood_parameters(
        self,
        lactation_group: str = None,
        year: str = None,
        month: str = None,
        region: str = None,
        milking_frequency: str = None,
        MY_305d: str = None,
    ) -> tuple:
        parameter_a = 19.9
        parameter_b = 24.7 * 1e-2
        parameter_c = 33.76 * 1e-4

        farm_specific = {}
        farm_specific["parity"] = lactation_group
        farm_specific["year"] = year
        farm_specific["month"] = month
        farm_specific["region"] = region
        farm_specific["milking_frequency"] = milking_frequency

        for category in ["parity", "year", "month", "region", "milking_frequency"]:
            if farm_specific[category]:
                print(category)
                adjustment_applied = False
                x = 0
                while (x<len(self.adjustment_dict[category]) and (not adjustment_applied)):
                    if self.adjustment_dict[category][x][category] == farm_specific[category]:
                        parameter_a += self.adjustment_dict[category][x]["adjustments"][0]
                        parameter_b += self.adjustment_dict[category][x]["adjustments"][1] * 1e-2
                        parameter_c += self.adjustment_dict[category][x]["adjustments"][2] * 1e-4
                        adjustment_applied = True
                        
                        print(self.adjustment_dict[category][x][category])
                        print(farm_specific[category])

                    x = x+1
        '''for category in [lactation_group, year, month, region, milking_frequency]:
            if category:
                parameter_a += self.adjustment_dict[category][0]
                parameter_b += self.adjustment_dict[category][1] * 1e-2
                parameter_c += self.adjustment_dict[category][2] * 1e-4'''

        if MY_305d == None:
            MY_305d = self.calc_integral_wood_curve(parameter_a, parameter_b, parameter_c)
            return parameter_a, parameter_b, parameter_c, MY_305d

        else:
            min_diff = float("inf")
            parameter_a_best_estimate = 0
            MY_305d_best_estimate = 0

            for parameter_a_error in np.arange(-10, 10, 0.01):
                parameter_a_vary = parameter_a + parameter_a_error
                MY_305d_vary = self.calc_integral_wood_curve(parameter_a_vary, parameter_b, parameter_c)
                if abs(MY_305d_vary - MY_305d) < min_diff:
                    min_diff = abs(MY_305d_vary - MY_305d)
                    parameter_a_best_estimate = parameter_a_vary
                    MY_305d_best_estimate = MY_305d_vary
            return parameter_a_best_estimate, parameter_b, parameter_c, MY_305d_best_estimate

    def set_lactation_curve_parameters(self) -> tuple[tuple, tuple, tuple]:

        # calculate lactation group yield

        if self.annual_MY_lbs != None:
            total_avg_305 = self.annual_MY_lbs * 305 / (365 * self.num_milking_cows * 2.205)

            # Extracting percentage distribution for each lactation group
            percent_P2 = self.parity_percentages[1] * 100
            percent_P3 = self.parity_percentages[2] * 100

            # Solving for P1-305 using the provided equation
            P1_305 = total_avg_305 - percent_P2 * self.P2_MY305_adj / 100 - percent_P3 * self.P3_MY305_adj / 100

            # Calculating 305-day milk yield for each lactation group
            P2_305 = P1_305 + self.P2_MY305_adj
            P3_305 = P1_305 + self.P3_MY305_adj

        else:
            P1_305 = None
            P2_305 = None
            P3_305 = None

        return (
            self.get_wood_parameters(
                lactation_group="1",
                year=self.year,
                region=self.region,
                milking_frequency=self.milking_freq,
                MY_305d=P1_305,
            ),
            self.get_wood_parameters(
                lactation_group="2",
                year=self.year,
                region=self.region,
                milking_frequency=self.milking_freq,
                MY_305d=P2_305,
            ),
            self.get_wood_parameters(
                lactation_group="3",
                year=self.year,
                region=self.region,
                milking_frequency=self.milking_freq,
                MY_305d=P3_305,
            ),
        )
