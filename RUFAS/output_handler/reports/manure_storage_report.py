"""
RUFAS: Ruminant Farm Systems Model
File name: feed_storage_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
from RUFAS.output_handler.reports.base_report import BaseReport


class ManureStorageReport(BaseReport):

    def __init__(self, data):
        super().__init__(data)

        self.daily_variables = {'year': ['time.cal_year', '', []],
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
                                'TS_DM_effluent': ['manure_storage.TS_DM_effluent', 'kg', []]
                                }

        self.annual_variables = {'year': ['time.cal_year', '', 0],
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
                                 'TS_DM_effluent': ['manure_storage.TS_DM_effluent_annual', 'kg', 0]
                                 }
