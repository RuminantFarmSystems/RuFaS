"""
RUFAS: Ruminant Farm Systems Model
File name: feed_storage_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
from RUFAS.output_handler.reports.base_report import BaseReport
from RUFAS.output_handler.reports.base_report_driver import BaseReportDriver


class FeedStorageReport(BaseReportDriver):

    def __init__(self, data, state):
        super().__init__(data)

        self.storage_report_data = data['feed_storage_report']

        for storage in state.feed.storage_options:
            self.reports[storage] = StorageReport(self.storage_report_data, storage)

        self.reports['feed_storage_summary'] = FeedStorageSummary(data['feed_storage_summary'])


class FeedStorageSummary(BaseReport):
    def __init__(self, data):
        super().__init__(data)
        self.daily_variables = {'year': ['time.calendar_year', '', []],
                                'j_day': ['time.day', '', []],
                                'DM': ['feed.DM', 'kg', []],
                                'NDF': ['feed.NDF', 'kg', []],
                                'C': ['feed.C', 'kg', []],
                                'N': ['feed.N', 'kg', []],
                                'P': ['feed.P', 'kg', []],
                                'CP': ['feed.CP', 'kg', []],
                                'NPN': ['feed.NPN', 'kg', []],
                                'C_loss': ['feed.C_loss', 'kg', []],
                                'CP_loss': ['feed.CP_loss', 'kg', []]
                                }

        self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                 'DM': ['feed.DM', 'kg', 0],
                                 'NDF': ['feed.NDF', 'kg', 0],
                                 'C': ['feed.C', 'kg', 0],
                                 'N': ['feed.N', 'kg', 0],
                                 'P': ['feed.P', 'kg', 0],
                                 'CP': ['feed.CP', 'kg', 0],
                                 'NPN': ['feed.NPN', 'kg', 0],
                                 'C_loss': ['feed.C_loss', 'kg', 0],
                                 'CP_loss': ['feed.CP_loss', 'kg', 0]
                                 }


class BaseStorageReport(BaseReport):
    def __init__(self, data, storage_name):
        super().__init__(data)
        self.storage_name = storage_name
        self.report_name = storage_name

    def daily_update(self, state, weather, time):
        storage = state.feed.storage_options[self.storage_name]
        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        storage = state.feed.storage_options[self.storage_name]
        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())


class StorageReport(BaseStorageReport):
    def __init__(self, data, storage_name):
        super().__init__(data, storage_name)

        self.daily_variables = {
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []],
            'NDF': ['storage.NDF', '', []],
            'C': ['storage.C', '', []],
            'N': ['storage.N', '', []],
            'P': ['storage.P', '', []],
            'C_harvest_gas': ['storage.C_harvest_gas', '', []],
            'C_harvest_particle': ['storage.C_harvest_particle', '', []],
            'NPN': ['storage.NPN', '', []],
            'CP_loss': ['storage.CP_loss', '', []],
            'CP_leachate': ['storage.CP_leachate', '', []],
            'CP_gas': ['storage.CP_gas', '', []],
            'CP': ['storage.CP', '', []],
            'C_loss': ['storage.C_loss', '', []],
            'C_feed_out_particle': ['storage.C_feed_out_particle', '', []],
            'C_feed_out_gas': ['storage.C_feed_out_gas', '', []],
            'C_storage_leachate': ['storage.C_storage_leachate', '', []],
            'C_storage_gas': ['storage.C_storage_gas', '', []]
        }

        self.annual_variables = {
            'year': ['time.calendar_year', '', 0]
        }
