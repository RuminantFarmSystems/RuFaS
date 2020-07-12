"""
RUFAS: Ruminant Farm Systems Model
File name: pen_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""

from .base_report_driver import BaseReportDriver
from .base_report import BaseReport
from .. import graphics


class PenReport(BaseReportDriver):
    def __init__(self, data, feed, pen_id):
        super().__init__(data)
        self.pen_id = pen_id
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
            soil = state.soil
            crop_type = state.crop.current_crop
            animal_management = state.animal_management
            feed = state.feed

            pen = state.animal_management.all_pens[self.pen_id]

            for variable in self.daily_variables:
                self.daily_variables[variable][2].append(
                    eval(self.daily_variables[variable][0], globals(), locals()))

    class GrowthReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals_in_pen': ['len(pen.animals_in_pen)', '', []],
                                    'average_growth': ['pen.avg_growth', 'kg', []],
                                    'average_milk': ['pen.avg_milk', 'kg', []],
                                    'average_p_animal': ['pen.avg_p_animal', 'g', []],
                                    'average_p_req': ['pen.avg_p_req', 'g', []]
                                    }

            self.annual_variables = {'year': ['time.cal_year', '', 0]
                                     }

    class ManureReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals': ['len(pen.animals_in_pen)', '', []],
                                    'manure': ['pen.manure[\'p_excrt_manure\']', 'g', []]
                                    }

            self.annual_variables = {'year': ['time.cal_year', '', 0]}

            self.manure_info = {}

    class RationReport(BasePenReport):
        def __init__(self, data, feed, pen_id):
            super().__init__(data, pen_id)
            self.ration_interval = data['ration_interval']

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals': ['len(pen.animals_in_pen)', '', []]
                                    }

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
                'year': ['time.cal_year', '', 0]
            }

        def produce_report_graphics(self):
            super().produce_report_graphics()
            graphics.ration_graphics(self)
