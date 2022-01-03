"""
RUFAS: Ruminant Farm Systems Model
File name: pen_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""

from .base_report_driver import BaseReportDriver
from .base_report import BaseReport
from .. import graphics


class PensReport(BaseReportDriver):
    def __init__(self, data, state):
        super().__init__(data)
        for pen in state.animal_management.all_pens:
            self.reports['pen_' +
                         str(pen.id)] = PenReport(data, state.feed, pen.id)

        self.reports['pens_summary'] = PensSummary(data['pens_summary'])


class PensSummary(BaseReport):
    def __init__(self, data):
        super().__init__(data)

        self.daily_variables = {
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []]
        }

        self.annual_variables = {
            'year': ['time.calendar_year', '', 0]
        }


class PenReport(BaseReportDriver):
    def __init__(self, data, feed, pen_id):
        super().__init__(data)
        self.pen_id = pen_id
        self.report_name = 'pen_' + str(pen_id)
        self.reports = {
            'ration_report': self.RationReport(data['ration_report'], feed, self.pen_id),
            'growth_report': self.GrowthReport(data['growth_report'], self.pen_id),
            'manure_report': self.ManureReport(data['manure_report'], self.pen_id)
        }

    class BasePenReport(BaseReport):
        def __init__(self, data, pen_id):
            super().__init__(data)
            self.pen_id = pen_id

        def daily_update(self, state, weather, time):
            animal_management = state.animal_management
            feed = state.feed
            pen = state.animal_management.all_pens[self.pen_id]

            for variable in self.daily_variables:
                # old variable evaluation code
                # code_to_eval = self.daily_variables[variable][0]
                # variable_values = self.daily_variables[variable][2]
                # variable_values.append(
                #     eval(code_to_eval, globals(), locals()))

                variable_value = evaluate_variable(variable, time, pen, feed)
                # self.daily_variables[variable][2] is a list containing all of the values for the given variable
                self.daily_variables[variable][2].append(variable_value)

        def annual_update(self, state, weather, time):
            animal_management = state.animal_management
            feed = state.feed
            pen = state.animal_management.all_pens[self.pen_id]

            for variable in self.annual_variables:
                # old variable evaluation code
                # code_to_eval = self.daily_variables[variable][0]
                # variable_value = eval(code_to_eval, globals(), locals())
                # self.annual_variables[variable][2] = variable_value

                variable_value = evaluate_variable(variable, time, pen, feed)
                # self.annual_variables[variable][2] is the value for the given variable
                self.annual_variables[variable][2] = variable_value

    class GrowthReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)

            daily_variables_lst = [('year', ''), ('j_day', ''), ('num_animals_in_pen', ''), ('average_growth', 'kg'),
                                   ('average_milk', 'kg'), ('average_p_animal', 'g'), ('average_p_req', 'g')]

            self.new_daily_variables = dict.fromkeys(daily_variables_lst, [])

            # temporary fix - remap new structure to old
            self.daily_variables = remap_variables_dict(self.new_daily_variables)

            self.annual_variables = {'year': ['time.calendar_year', '', 0]
                                     }

    class ManureReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)

            daily_variables_lst = [('year', ''), ('j_day', ''), ('num_animals', ''), ('manure', 'kg'),
                                   ('urea_conc', 'mol/L'), ('ammoniacal_N_conc', 'mol/L'),
                                   ('manure_N', 'g'), ('total_solids', 'kg'), ('manure_VSd', 'g'),
                                   ('manure_VSnond', 'g'), ('WIP_frac', 'g/g total man'), ('WOP_frac', 'g/g total man'),
                                   ('manure_P', 'g'), ('P_frac', 'g/g total man'), ('K_manure', 'g'),
                                   ('enteric_methane', 'g')]

            self.new_daily_variables = dict.fromkeys(daily_variables_lst, [])

            # temporary fix - remap new structure to old
            self.daily_variables = remap_variables_dict(self.new_daily_variables)

            self.annual_variables = {'year': ['time.calendar_year', '', 0]}

            self.manure_info = {}

    class RationReport(BasePenReport):
        def __init__(self, data, feed, pen_id):
            super().__init__(data, pen_id)
            self.ration_interval = data['ration_interval']

            daily_variables_lst = [('year', ''), ('j_day', ''), ('num_animals', '')]

            self.new_daily_variables = dict.fromkeys(daily_variables_lst, [])

            # temporary fix - remap new structure to old
            self.daily_variables = remap_variables_dict(self.new_daily_variables)

            all_feeds = feed.all_feed_ids
            for feed_id in all_feeds:
                feed_name = all_feeds[feed_id]['feed_name']
                units = all_feeds[feed_id]['units']

                self.daily_variables[feed_id + "(" + feed_name + ")"] = \
                    [
                        'pen.ration[\'%s\'] if pen.pen_populated and \'%s\' in feed.available_feeds else 0' % (
                            feed_id, feed_id), units,
                        []]

            self.annual_variables = {
                'year': ['time.calendar_year', '', 0]
            }

        def produce_report_graphics(self):
            super().produce_report_graphics()
            graphics.ration_graphics(self)


# temporary function to remap the new variable dict structure to the old structure
# this is necessary because some of the output relies on the old structure
def remap_variables_dict(variables_dict):
    new_variables_dict = dict()
    for variable, unit in variables_dict:
        new_variables_dict[variable] = ['', unit, []]
    return new_variables_dict


def evaluate_variable(variable, time, pen, feed):
    """
    Evaluates a daily or annual variable within the provided scope.

    Args:
        TODO: add better descriptions for the args
        variable: the variable to evaluate
        time: the time object to evaluate the variable with
        pen: the pen object to evaluate the variable with
        feed: the feed object to evaluate the variable with

    Returns:
        TODO: the type varies based on the variable, find a fix if possible
        ___: the value of the variable after evaluation
    """
    if variable == 'year':
        return time.calendar_year
    elif variable == 'j_day':
        return time.day
    elif variable == 'num_animals_in_pen':
        return len(pen.animals_in_pen)
    elif variable == 'average_growth':
        return pen.avg_growth
    elif variable == 'average_milk':
        return pen.avg_milk
    elif variable == 'average_p_animal':
        return pen.avg_p_animal
    elif variable == 'average_p_req':
        return pen.avg_p_req
    elif variable == 'num_animals':
        return len(pen.animals_in_pen)
    elif variable == 'manure':
        return pen.manure['p_excrt_manure']
    elif variable == 'urea_conc':
        return pen.manure['U']
    elif variable == 'ammoniacal_N_conc':
        return pen.manure['TAN_s']
    elif variable == 'manure_N':
        return pen.manure['MN']
    elif variable == 'total_solids':
        return pen.manure['TSd']
    elif variable == 'manure_VSd':
        return pen.manure['VSd']
    elif variable == 'manure_VSnond':
        return pen.manure['VSnd']
    elif variable == 'WIP_frac':
        return pen.manure['WIP_frac']
    elif variable == 'WOP_frac':
        return pen.manure['WOP_frac']
    elif variable == 'manure_P':
        return pen.manure['p_excrt_manure']
    elif variable == 'P_frac':
        return pen.manure['p_frac']
    elif variable == 'K_manure':
        return pen.manure['K_manure']
    elif variable == 'enteric_methane':
        return pen.manure['CH4_manure']

    # variable is a type of feed
    else:
        # TODO: find a better way to get the feed_id
        feed_id = variable.split('(')[0]

        return pen.ration[feed_id] if pen.pen_populated and feed_id in feed.available_feeds else 0
