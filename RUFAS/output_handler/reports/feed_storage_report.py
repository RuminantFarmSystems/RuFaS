"""
RUFAS: Ruminant Farm Systems Model
File name: feed_storage_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
from RUFAS.output_handler.reports.base_report import BaseReport


class FeedStorageReport(BaseReport):

    def __init__(self, data):
        super().__init__(data)

        self.daily_variables = {'year': ['time.cal_year', '', []],
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

        self.annual_variables = {'year': ['time.cal_year', '', 0],
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
