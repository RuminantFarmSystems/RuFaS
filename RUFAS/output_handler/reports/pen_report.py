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
            self.reports['pen_' + str(pen.id)] = PenReport(data, state.feed, pen, pen.id)

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
    def __init__(self, data, feed, individual_pen, pen_id):
        super().__init__(data)
        self.pen_id = pen_id
        self.report_name = 'pen_' + str(pen_id)
        self.reports = {
            'ration_report': self.RationReport(data['ration_report'], feed, individual_pen, self.pen_id),
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
                # index 2 is the accumulator for the evauated variables
                # index 0 is the string literal code representation of the variable
                self.daily_variables[variable][2].append(
                    eval(self.daily_variables[variable][0], globals(), locals()))

        def annual_update(self, state, weather, time):
            animal_management = state.animal_management
            feed = state.feed
            pen = state.animal_management.all_pens[self.pen_id]

            for variable in self.annual_variables:
                # index 2 is the accumulator for the evauated variables
                # index 0 is the string literal code representation of the variable
                self.annual_variables[variable][2] = \
                    eval(self.daily_variables[variable]
                         [0], globals(), locals())

    class GrowthReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)

            self.daily_variables = {'year': ['time.calendar_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals_in_pen': ['len(pen.animals_in_pen)', '', []],
                                    'average_growth': ['pen.avg_growth', 'kg', []],
                                    'average_milk': ['pen.avg_milk', 'kg', []],
                                    'average_p_animal': ['pen.avg_p_animal', 'g', []],
                                    'average_p_req': ['pen.avg_p_req', 'g', []]
                                    }

            self.annual_variables = {'year': ['time.calendar_year', '', 0]
                                     }

    class ManureReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)

            self.daily_variables = {'year': ['time.calendar_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals': ['len(pen.animals_in_pen)', '', []],
                                    'manure': ['pen.manure[\'p_excrt_manure\']', 'kg', []],
                                    'urea_conc': ['pen.manure[\'U\']', 'mol/L', []],
                                    'ammoniacal_N_conc': ['pen.manure[\'TAN_s\']', 'mol/L', []],
                                    'manure_N': ['pen.manure[\'MN\']', 'g', []],
                                    'total_solids': ['pen.manure[\'TSd\']', 'kg', []],
                                    'manure_VSd': ['pen.manure[\'VSd\']', 'g', []],
                                    'manure_VSnond': ['pen.manure[\'VSnd\']', 'g', []],
                                    'WIP_frac': ['pen.manure[\'WIP_frac\']', 'g/g total man', []],
                                    'WOP_frac': ['pen.manure[\'WOP_frac\']', 'g/g total man', []],
                                    'manure_P': ['pen.manure[\'p_excrt_manure\']', 'g', []],
                                    'P_frac': ['pen.manure[\'p_frac\']', 'g/g total man', []],
                                    'K_manure': ['pen.manure[\'K_manure\']', 'g', []],
                                    'enteric_methane': ['pen.manure[\'CH4_manure\']', 'g', []]
                                    }

            self.annual_variables = {'year': ['time.calendar_year', '', 0]}

            self.manure_info = {}

    class RationReport(BasePenReport):
        def __init__(self, data, feed, individual_pen, pen_id):
            super().__init__(data, pen_id)
            self.ration_interval = data['ration_interval']

            self.daily_variables = {'year': ['time.calendar_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals': ['len(pen.animals_in_pen)', '', []]
                                    }
            # this subsets the pen's allotted feed given the animals type(s)
            # that are present within the pen that is currently being
            # simulated
            individual_pen.subset_class_feeds(feed)

            # dictionary with all feed ids and keys and their pertaining information as values
            all_feeds = feed.all_feed_ids

            # subsets the entirety of the feed ids for the individual pen's needs
            pen_specific_feeds = {str(x): all_feeds[str(x)] for x in individual_pen.allocated_feeds}

            for feed_id in individual_pen.allocated_feeds:
                feed_name = pen_specific_feeds[str(feed_id)]['feed_name']
                units = pen_specific_feeds[str(feed_id)]['units']

                self.daily_variables[str(feed_id) + "(" + feed_name + ")"] = \
                    [
                        'pen.ration[\'%s\'] if pen.pen_populated and \'%s\' in pen.ration.keys() else 0' % (
                            feed_id, feed_id), units,
                        []]
                # [
                #     'pen.ration[\'%s\'] if pen.pen_populated and int(\'%s\') in pen.allocated_feeds else 0' % (
                #         feed_id, feed_id), units,
                #     []]

            self.annual_variables = {
                'year': ['time.calendar_year', '', 0]
            }

        def produce_report_graphics(self):
            super().produce_report_graphics()
            graphics.ration_graphics(self)
