"""
RUFAS: Ruminant Farm Systems Model
File name: feed_storage_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
from RUFAS.output_handler.reports.base_report import BaseReport
from RUFAS.output_handler.reports.base_report_driver import BaseReportDriver


class ManureStorageReport(BaseReportDriver):

    def __init__(self, data, state):
        super().__init__(data)

        for handler in state.manure_management.pens:
            self.reports[handler] = HandlingReport(data['handling_report'], handler)

        for separator in state.manure_management.separators:
            self.reports[separator] = SeparatorReport(data['separator_report'], separator)

        for storage in state.manure_management.storage:
            self.reports[storage] = StorageReport(data['storage_report'], storage)

        self.reports['manure_storage_summary'] = ManureStorageSummary(data['manure_storage_summary'])


class ManureStorageSummary(BaseReport):
    def __init__(self, data):
        super().__init__(data)

        self.daily_variables = {'year': ['time.calendar_year', '', []],
                                'j_day': ['time.day', '', []],
                                'TS': ['manure_storage.TS', 'kg', []],
                                'VS': ['manure_storage.VS', 'kg', []],
                                'N': ['manure_storage.N', 'kg', []],
                                'P': ['manure_storage.P', 'kg', []],
                                'K': ['manure_storage.K', 'kg', []],
                                'TS_liquid': ['manure_storage.TS_liquid', 'kg', []],
                                'VS_liquid': ['manure_storage.VS_liquid', 'kg', []],
                                'N_liquid': ['manure_storage.N_liquid', 'kg', []],
                                'P_liquid': ['manure_storage.P_liquid', 'kg', []],
                                'K_liquid': ['manure_storage.K_liquid', 'kg', []],
                                'TS_DM_effluent': ['manure_storage.TS_DM_effluent', 'kg', []],
                                'CH4_emissions': ['manure_storage.CH4_emissions', 'kg', []],
                                }

        self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                 'TS': ['manure_storage.TS_annual', 'kg', 0],
                                 'VS': ['manure_storage.VS_annual', 'kg', 0],
                                 'N': ['manure_storage.N_annual', 'kg', 0],
                                 'P': ['manure_storage.P_annual', 'kg', 0],
                                 'K': ['manure_storage.K_annual', 'kg', 0],
                                 'TS_liquid': ['manure_storage.TS_liquid_annual', 'kg', 0],
                                 'VS_liquid': ['manure_storage.VS_liquid_annual', 'kg', 0],
                                 'N_liquid': ['manure_storage.N_liquid_annual', 'kg', 0],
                                 'P_liquid': ['manure_storage.P_liquid_annual', 'kg', 0],
                                 'K_liquid': ['manure_storage.K_liquid_annual', 'kg', 0],
                                 'TS_DM_effluent': ['manure_storage.TS_DM_effluent_annual', 'kg', 0],
                                 'CH4_emissions': ['manure_storage.CH4_emissions_annual', 'kg', 0],
                                 }


class BaseHandlingReport(BaseReport):
    def __init__(self, data, handler):
        super().__init__(data)
        self.report_name = 'handler_' + str(handler)
        self.handler_name = handler

    def daily_update(self, state, weather, time):
        handler = state.manure_management.pens[self.handler_name]
        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        handler = state.manure_management.pens[self.handler_name]
        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())


class BaseSeparatorReport(BaseReport):
    def __init__(self, data, separator):
        super().__init__(data)
        self.report_name = 'separator_' + separator
        self.separator_name = separator

    def daily_update(self, state, weather, time):
        separator = state.manure_management.separators[self.separator_name]
        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        separator = state.manure_management.separators[self.separator_name]
        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())


class BaseStorageReport(BaseReport):
    def __init__(self, data, storage):
        super().__init__(data)
        self.report_name = 'storage_' + storage
        self.storage_name = storage

    def daily_update(self, state, weather, time):
        storage = state.manure_management.storage[self.storage_name]
        for variable in self.daily_variables:
            self.daily_variables[variable][2].append(
                eval(self.daily_variables[variable][0], globals(), locals()))

    def annual_update(self, state, weather, time):
        storage = state.manure_management.storage[self.storage_name]
        for variable in self.annual_variables:
            self.annual_variables[variable][2] = \
                eval(self.annual_variables[variable][0], globals(), locals())


class HandlingReport(BaseHandlingReport):
    def __init__(self, data, handler):
        super().__init__(data, handler)

        self.daily_variables = {
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []],
            'VS_excreted': ['handler.VS_excreted', 'kg', []],
            'TS_excreted': ['handler.TS_excreted', 'kg', []],
            'N_excreted': ['handler.N_excreted', 'kg', []],
            'P_excreted': ['handler.P_excreted', 'kg', []],
            'K_excreted': ['handler.K_excreted', 'kg', []],
            'flush_water_volume': ['handler.flush_water_volume', 'kg', []],
            'TS_loss': ['handler.TS_loss', 'kg', []],
            'VS_loss': ['handler.VS_loss', 'kg', []],
            'WIP': ['handler.WIP', 'kg', []],
            'WOP': ['handler.WOP', 'kg', []],
            'CH4': ['handler.CH4', 'kg', []]
        }

        self.annual_variables = {
            'year': ['time.calendar_year', '', 0]
        }


class SeparatorReport(BaseSeparatorReport):
    def __init__(self, data, separator):
        super().__init__(data, separator)
        self.daily_variables = {
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []],
            'flush_water_volume': ['separator.flush_water_volume', 'liters', []],
            'TS': ['separator.TS', 'kg', []],
            'VS': ['separator.VS', 'kg', []],
            'N': ['separator.N', 'kg', []],
            'P': ['separator.P', 'kg', []],
            'K': ['separator.K', 'kg', []],
            'TS_liquid': ['separator.TS_liquid', 'kg', []],
            'VS_liquid': ['separator.VS_liquid', 'kg', []],
            'N_liquid': ['separator.N_liquid', 'kg', []],
            'P_liquid': ['separator.P_liquid', 'kg', []],
            'K_liquid': ['separator.K_liquid', 'kg', []],
            'TS_DM_effluent': ['separator.TS_DM_effluent', 'kg', []],
            'WIP': ['separator.WIP', 'kg', []],
            'WOP': ['separator.WOP', 'kg', []],
            'CH4': ['separator.CH4', 'kg', []]
        }

        self.annual_variables = {
            'year': ['time.calendar_year', '', 0]
        }


class StorageReport(BaseStorageReport):
    def __init__(self, data, storage):
        super().__init__(data, storage)
        self.daily_variables = {
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []],
            'TS': ['storage.TS', 'kg', []],
            'VS': ['storage.VS', 'kg', []],
            'N': ['storage.N', 'kg', []],
            'P': ['storage.P', 'kg', []],
            'K': ['storage.K', 'kg', []],
            'TS_liquid': ['storage.TS_liquid', 'kg', []],
            'VS_liquid': ['storage.VS_liquid', 'kg', []],
            'N_liquid': ['storage.N_liquid', 'kg', []],
            'P_liquid': ['storage.P_liquid', 'kg', []],
            'K_liquid': ['storage.K_liquid', 'kg', []],
            'WIP': ['storage.WIP', 'kg', []],
            'WOP': ['storage.WOP', 'kg', []],
            'CH4': ['storage.CH4', 'kg', []],
            'WOP_frac': ['storage.WOP_frac', '%', []],
            'WIP_frac': ['storage.WIP_frac', '%', []]
        }

        self.annual_variables = {
            'year': ['time.calendar_year', '', 0]
        }
