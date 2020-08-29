"""
RUFAS: Ruminant Farm Systems Model
File name: field_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
from .base_report import BaseReport
from .base_report_driver import BaseReportDriver
from .. import graphics


class FieldsReport(BaseReportDriver):
    def __init__(self, data, state):
        super().__init__(data)
        for field in state.fields.fields.values():
            self.reports[field.field_name] = FieldReport(data, field.field_name, state)

        self.reports['fields_summary'] = FieldsSummary(data['fields_summary'])


class FieldsSummary(BaseReport):
    def __init__(self, data):
        super().__init__(data)
        self.daily_variables = {
            'year': ['time.calendar_year', '', []],
            'j_day': ['time.day', '', []],
            'profile_SW': ['fields.profile_SW', 'mm H2O', []],
            'runoff': ['fields.runoff', 'mm H2O', []],
            'drainage': ['fields.drainage', 'mm H2O', []],
            'erosion': ['fields.erosion', 'ton / ha', []],
            'ET': ['fields.ET', 'mm H2O', []],
            'manure_applied': ['fields.manure_applied', 'kg', []],
            'manure_N_applied': ['fields.manure_N_applied', 'kg', []],
            'manure_P_applied': ['fields.manure_P_applied', 'kg', []],
            'profile_N': ['fields.profile_N', 'kg', []],
            'profile_P': ['fields.profile_P', 'kg', []],
            'N_runoff': ['fields.N_runoff', 'kg', []],
            'P_runoff': ['fields.P_runoff', 'kg', []],
            'N_drainage': ['fields.N_drainage', 'kg', []],
            'P_drainage': ['fields.P_drainage', 'kg', []],
            'N_erosion': ['fields.N_erosion', 'kg', []],
            'P_erosion': ['fields.P_erosion', 'kg', []],
            'yield': ['fields.yield_actual', 'kg', []],
            'N_yield': ['fields.N_yield', 'kg', []],
            'P_yield': ['fields.P_yield', 'kg', []]
        }

        self.annual_variables = {
            'year': ['time.calendar_year', '', 0],
            'runoff': ['fields.runoff_annual', 'mm H2O', 0],
            'drainage': ['fields.drainage_annual', 'mm H2O', 0],
            'erosion': ['fields.erosion_annual', 'ton / ha', 0],
            'ET': ['fields.ET_annual', 'mm H2O', 0],
            'manure_applied': ['fields.manure_applied_annual', 'kg', 0],
            'manure_N_applied': ['fields.manure_N_applied_annual', 'kg', 0],
            'manure_P_applied': ['fields.manure_P_applied_annual', 'kg', 0],
            'N_runoff': ['fields.N_runoff_annual', 'kg', 0],
            'P_runoff': ['fields.P_runoff_annual', 'kg', 0],
            'N_drainage': ['fields.N_drainage_annual', 'kg', 0],
            'P_drainage': ['fields.P_drainage_annual', 'kg', 0],
            'N_erosion': ['fields.N_erosion_annual', 'kg', 0],
            'P_erosion': ['fields.P_erosion_annual', 'kg', 0],
            'yield': ['fields.yield_annual', 'kg', 0],
            'N_yield': ['fields.yield_N_annual', 'kg', 0],
            'P_yield': ['fields.yield_P_annual', 'kg', 0]
        }


class FieldReport(BaseReportDriver):
    def __init__(self, data, field_name, state):
        super().__init__(data)
        self.field_name = field_name
        self.report_name = self.field_name
        self.reports = {
            'soil_report': self.SoilReportDriver(data['soil_report'], state, field_name),
            'crop_report': self.CropReport(data['crop_report'], field_name),
            'field_management_report': self.FieldManagementReport(data['field_management_report'], field_name),
            'nitrogen_mass_balance': self.NitrogenBalance(data['nitrogen_balance'], field_name),
            'phosphorus_mass_balance': self.PhosphorusBalance(data['phosphorus_balance'], field_name),
            'water_balance': self.WaterBalance(data['water_balance'], field_name),
            'custom_field_report': self.CustomFieldReport(data['custom_field_report'], field_name)
        }

    def daily_update(self, state, weather, time):
        for report in self.reports.values():
            report.daily_update(state, weather, time)

    def annual_update(self, state, weather, time):
        for report in self.reports.values():
            report.annual_update(state, weather, time)

    class BaseFieldReport(BaseReport):
        def __init__(self, data, field_name):
            super().__init__(data)
            self.field_name = field_name

        def daily_update(self, state, weather, time):
            field = state.fields.fields[self.field_name]
            soil = field.soil
            crop_type = field.crop.current_crop
            field_management = field.field_management
            for variable in self.daily_variables:
                self.daily_variables[variable][2].append(
                    eval(self.daily_variables[variable][0], globals(), locals()))

        def annual_update(self, state, weather, time):
            field = state.fields.fields[self.field_name]
            soil = field.soil
            crop_type = field.crop.current_crop
            field_management = field.field_management
            for variable in self.annual_variables:
                self.annual_variables[variable][2] = \
                    eval(self.annual_variables[variable][0], globals(), locals())

    class CropReport(BaseFieldReport):
        def __init__(self, data, field_name):
            super().__init__(data, field_name)
            self.daily_variables = {'year': ['time.calendar_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'fr_PHU': ['crop_type.fr_PHU', '%', []],
                                    'biomass': ['crop_type.biomass_actual', 'kg ha^-1', []],
                                    'LAI_actual': ['crop_type.LAI_actual', 'm^2/m^2', []],
                                    'Bio_N': ['crop_type.bio_N', 'kg N ha^-1', []],
                                    'Bio_P': ['crop_type.bio_P', 'kg P ha^-1', []],
                                    'rooting_depth': ['crop_type.z_root', 'mm', []],
                                    'HI_act': ['crop_type.HI_actual', '', []],
                                    'HI_min': ['crop_type.HI_min', '', []],
                                    'HI_max': ['crop_type.HI_max', '', []],
                                    'yield_actual': ['crop_type.yield_actual', 'kg ha^-1', []]
                                    }

            self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                     'yield': ['crop_type.yield_annual', 'kg/ha', 0]
                                     }

    class SoilReportDriver(BaseReportDriver):
        def __init__(self, data, state, field_name):
            super().__init__(data)
            self.field_name = field_name

            self.reports = {
                'soil_nitrogen_report': self.SoilNitrogenReport(data['soil_nitrogen_report'], field_name),
                'soil_phosphorus_report': self.SoilPhosphorusReport(data['soil_phosphorus_report'], field_name),
                'soil_summary': self.SoilSummary(data['soil_summary'], field_name)
            }

            layer_no = 0
            for _ in range(len(state.fields.fields[self.field_name].soil.soil_layers)):
                self.reports['layer_' + str(layer_no)] = \
                    self.LayerReport(data['layer_reports'], field_name, layer_no)
                layer_no += 1

        class BaseSoilReport(BaseReport):
            def __init__(self, data, field_name):
                super().__init__(data)
                self.field_name = field_name

            def daily_update(self, state, weather, time):
                field = state.fields.fields[self.field_name]
                soil = field.soil
                field_management = field.field_management

                for variable in self.daily_variables:
                    self.daily_variables[variable][2].append(
                        eval(self.daily_variables[variable][0], globals(), locals()))

            def annual_update(self, state, weather, time):
                field = state.fields.fields[self.field_name]
                soil = field.soil
                field_management = field.field_management

                for variable in self.annual_variables:
                    self.annual_variables[variable][2] = \
                        eval(self.annual_variables[variable][0], globals(), locals())

        class BaseLayerReport(BaseSoilReport):
            def __init__(self, data, field_name, layer_no):
                super().__init__(data, field_name)
                self.layer_no = layer_no
                self.report_name = 'layer_' + str(self.layer_no)

            def daily_update(self, state, weather, time):
                layer = state.fields.fields[self.field_name].soil.soil_layers[self.layer_no]

                for variable in self.daily_variables:
                    self.daily_variables[variable][2].append(
                        eval(self.daily_variables[variable][0], globals(), locals()))

            def annual_update(self, state, weather, time):
                layer = state.fields.fields[self.field_name].soil.soil_layers[self.layer_no]

                for variable in self.annual_variables:
                    self.annual_variables[variable][2] = \
                        eval(self.annual_variables[variable][0], globals(), locals())

        class LayerReport(BaseLayerReport):
            def __init__(self, data, field_name, layer_no):
                super().__init__(data, field_name, layer_no)

                self.daily_variables = {
                    'year': ['time.calendar_year', '', []],
                    'j_day': ['time.day', '', []],
                    'transpiration': ['layer.trans_act', 'mm H2O', []],
                    'soil_water': ['layer.soil_water', 'mm H2O', []],
                    'evaporation': ['layer.evap', 'mm H2O', []],
                    'percolation': ['layer.percolation', 'mm H2O', []],
                    'temperature': ['layer.temperature', 'ºC', []],
                    'NO3': ['layer.NO3', 'kg', []],
                    'NH4': ['layer.NH4', 'kg', []],
                    'active_N': ['layer.active_N', 'kg', []],
                    'stable_N': ['layer.stable_N', 'kg', []],
                    'nitrification': ['layer.nitrification', 'kg/ha', []],
                    'volatilization': ['layer.volatilization', 'kg/ha', []],
                    'denitrification': ['layer.denitrification', 'kg/ha', []],
                    'nitrification_volatilization': ['layer.nitri_volatil', 'kg/ha', []],
                    'N_trans': ['layer.N_trans', 'kg', []],
                    'NO3_percolation': ['layer.NO3_percolation', 'kg', []],
                    'NH4_percolation': ['layer.NH4_percolation', 'kg', []]
                }

                self.annual_variables = {
                    'year': ['time.calendar_year', '', 0],
                    'NO3_average': ['layer.NO3_average', 'kg', 0],
                    'NH4_average': ['layer.NH4_average', 'kg', 0],
                    'active_N_average': ['layer.active_N_average', 'kg', 0],
                    'stable_N_average': ['layer.stable_N_average', 'kg', 0],
                    'org_N_average': ['layer.org_N_average', 'kg', 0]
                }

        class SoilNitrogenReport(BaseSoilReport):
            def __init__(self, data, field_name):
                super().__init__(data, field_name)

                self.daily_variables = {'year': ['time.calendar_year', '', []],
                                        'j_day': ['time.day', '', []],
                                        'profile_N': ['soil.profile_N', 'kg', []],
                                        'manure_N_applied': ['field_management.manure_N_applied', 'kg', []],
                                        'fresh_N': ['soil.fresh_N', 'kg', []],
                                        'NO3_drainage': ['soil.NO3_drainage', 'kg/ha', []],
                                        'NH4_drainage': ['soil.NH4_drainage', 'kg/ha', []],
                                        'NO3_runoff': ['soil.NO3_runoff', 'kg/ha', []],
                                        'NH4_runoff': ['soil.NH4_runoff', 'kg/ha', []],
                                        'active_N_drainage': ['soil.active_N_drainage', 'kg/ha', []],
                                        'active_N_erosion': ['soil.active_N_erosion', 'kg/ha', []],
                                        'stable_N_erosion': ['soil.stable_N_erosion', 'kg/ha', []],
                                        'fresh_N_erosion': ['soil.fresh_N_erosion', 'kg/ha', []],
                                        'NH4_erosion': ['soil.NH4_erosion', 'kg/ha', []],
                                        }

                self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                         'manure_N_applied': ['field_management.manure_N_applied_annual', 'kg', 0],
                                         'NO3_runoff': ['soil.NO3_runoff_annual', 'kg/ha', 0],
                                         'NH4_runoff': ['soil.NH4_runoff_annual', 'kg/ha', 0],
                                         'NH4_erosion': ['soil.NH4_erosion_annual', 'kg/ha', 0],
                                         'active_N_erosion': ['soil.active_N_erosion_annual', 'kg/ha', 0],
                                         'stable_N_erosion': ['soil.stable_N_erosion_annual', 'kg/ha', 0],
                                         'fresh_N_erosion': ['soil.fresh_N_erosion_annual', 'kg/ha', 0],
                                         'NO3_drainage': ['soil.NO3_drainage_annual', 'kg/ha', 0],
                                         'NH4_drainage': ['soil.NH4_drainage_annual', 'kg/ha', 0],
                                         'active_N_drainage': ['soil.active_N_drainage_annual', 'kg/ha', 0],
                                         'fresh_N': ['soil.fresh_N_average', 'kg', 0],
                                         'profile_N': ['soil.profile_N_average', 'kg', 0]
                                         }

        class SoilPhosphorusReport(BaseSoilReport):
            def __init__(self, data, field_name):
                super().__init__(data, field_name)

                self.daily_variables = {'year': ['time.calendar_year', '', []],
                                        'j_day': ['time.day', '', []],
                                        'manure_P_applied': ['field_management.manure_P_applied', 'kg', []],
                                        'labile_P': ['soil.labile_P', 'kg', []],
                                        'active_P': ['soil.active_P', 'kg', []],
                                        'stable_P': ['soil.stable_P', 'kg', []],
                                        'org_P': ['soil.org_P', 'kg', []],
                                        'P_uptake': ['soil.P_uptake', 'kg', []],
                                        'fert_P_leached': ['soil.fert_P_leached', 'kg', []],
                                        'M_leach': ['soil.M_leach', 'kg', []],
                                        'DRP_drainage': ['soil.DRP_drainage', 'kg', []],
                                        'M_DRP_runoff': ['soil.M_DRP_runoff', 'kg', []],
                                        'fert_P_runoff': ['soil.fert_P_runoff_act', 'kg', []],
                                        'DRP_runoff': ['soil.DRP_runoff', 'kg', []],
                                        'MIP_runoff': ['soil.MIP_runoff', 'kg', []],
                                        'MOP_runoff': ['soil.MOP_runoff', 'kg', []],
                                        'WIP': ['soil.WIP', 'kg', []],
                                        'WOP': ['soil.WOP', 'kg', []],
                                        'profile_P': ['soil.profile_P', 'kg', []],
                                        'STP': ['soil.STP', 'kg', []]
                                        }

                self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                         'manure_P_applied': ['field_management.manure_P_applied_annual', 'kg', 0],
                                         'P_uptake': ['soil.P_uptake_annual', 'kg', 0],
                                         'fert_P_leached': ['soil.fert_P_leached_annual', 'kg', 0],
                                         'M_leach': ['soil.M_leach_annual', 'kg', 0],
                                         'DRP_drainage': ['soil.DRP_drainage_annual', 'kg', 0],
                                         'M_DRP_runoff': ['soil.M_DRP_runoff_annual', 'kg', 0],
                                         'fert_P_runoff': ['soil.fert_P_runoff_annual', 'kg', 0],
                                         'DRP_runoff': ['soil.DRP_runoff_annual', 'kg', 0],
                                         'MIP_runoff': ['soil.MIP_runoff_annual', 'kg', 0],
                                         'MOP_runoff': ['soil.MOP_runoff_annual', 'kg', 0],
                                         'profile_P': ['soil.profile_P_annual', 'kg', 0],
                                         'STP': ['soil.STP_annual', 'kg', 0]
                                         }

        class SoilSummary(BaseSoilReport):
            def __init__(self, data, field_name):
                super().__init__(data, field_name)

                self.daily_variables = {'year': ['time.calendar_year', '', []],
                                        'j_day': ['time.day', '', []],
                                        'manure_applied': ['field_management.manure_applied', 'kg', []],
                                        'precip': ['weather.rainfall[time.year - 1][time.day - 1]', 'mm', []],
                                        'irrigation': ['weather.irrigation[time.year - 1][time.day - 1]', 'mm', []],
                                        'runoff': ['soil.runoff', 'mm', []],
                                        'ET_max': ['soil.ET_max', 'mm d^-1', []],
                                        'ET_act': ['soil.ET_act', 'mm H2O', []],
                                        'trans_max': ['soil.trans_max', 'mm H2O', []],
                                        'evap_max': ['soil.evap_max', 'mm H2O', []],
                                        'surface_temp': ['soil.T_surf', 'C', []],
                                        'sediment_yield': ['soil.sed', 'metric tons', []],
                                        'residue': ['soil.residue', 'kg/ha', []],
                                        'K': ['soil.soil_layers[0].K', 'kg', []]
                                        }

                self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                         'manure_applied': ['field_management.manure_applied_annual', 'kg', 0],
                                         'ET_max': ['soil.ET_max_annual', 'mm H20', 0],
                                         'ET': ['soil.ET_annual', 'mm H20', 0]
                                         }

    class FieldManagementReport(BaseFieldReport):
        def __init__(self, data, field_name):
            super().__init__(data, field_name)
            self.daily_variables = {
                'year': ['time.calendar_year', '', []],
                'j_day': ['time.day', '', []],
                'manure_applied': ['field_management.manure_applied', 'kg', []],
                'manure_N_applied': ['field_management.manure_N_applied', 'kg', []],
                'manure_P_applied': ['field_management.manure_P_applied', 'kg', []],
                'fert_applied': ['field_management.fert_applied', 'kg', []],
                'fert_N_applied': ['field_management.fert_N_applied', 'kg', []],
                'fert_P_applied': ['field_management.fert_P_applied', 'kg', []],
                'fert_K_applied': ['field_management.fert_K_applied', 'kg', []]
            }

            self.annual_variables = {
                'year': ['time.calendar_year', '', 0],
                'manure_applied': ['field_management.manure_applied_annual', 'kg', 0],
                'manure_N_applied': ['field_management.manure_N_applied_annual', 'kg', 0],
                'manure_P_applied': ['field_management.manure_P_applied_annual', 'kg', 0],
                'fert_applied': ['field_management.fert_applied_annual', 'kg', 0],
                'fert_N_applied': ['field_management.fert_N_applied_annual', 'kg', 0],
                'fert_P_applied': ['field_management.fert_P_applied_annual', 'kg', 0],
                'fert_K_applied': ['field_management.fert_K_applied_annual', 'kg', 0]
            }

    class CustomFieldReport(BaseFieldReport):
        def __init__(self, data, field_name):
            super().__init__(data, field_name)

            self.daily_variables = {
                'year': ['time.calendar_year', '', []],
                'j_day': ['time.day', '', []],
                'manure_applied': ['field_management.manure_applied', 'kg', []],
                'manure_N_applied': ['field_management.manure_N_applied', 'kg', []],
                'active_N_l1': ['soil.soil_layers[0].active_N', 'kg', []],
                'stable_N_l1': ['soil.soil_layers[0].stable_N', 'kg', []],
                'profile_N': ['soil.profile_N', 'kg', []],
                'fert_N_applied': ['field_management.fert_N_applied', 'kg', []],
                'N_uptake': ['soil.N_uptake', 'kg', []],
                'biomass': ['crop_type.biomass_actual', 'kg ha^-1', []],
                'bio_N': ['crop_type.bio_N', 'kg N ha^-1', []],
                'yield_actual': ['crop_type.yield_actual', 'kg ha^-1', []]
            }

            self.annual_variables = {
                'year': ['time.calendar_year', '', 0]
            }

    class BaseFieldMassBalanceReport(BaseFieldReport):
        def __init__(self, data, field_name):
            super().__init__(data, field_name)

        def produce_report_graphics(self):
            super().produce_report_graphics()
            graphics.annual_mass_balance_graphics(self)

    class WaterBalance(BaseFieldMassBalanceReport):
        def __init__(self, data, field_name):
            super().__init__(data, field_name)

            self.daily_variables = {'year': ['time.calendar_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'actual': ['soil.p_act', 'mmH2O', []],
                                    'calculated': ['soil.p_calc', 'mmH2O', []],
                                    'difference': ['soil.water_balance_difference', 'mmH2O', []],
                                    'delta': ['soil.delta_SW', 'mmH2O', []],
                                    'runoff': ['soil.runoff', 'mmH2O', []],
                                    'evaporation': ['soil.evap', 'mmH2O', []],
                                    'transpiration': ['soil.trans', 'mmH2O', []],
                                    'drainage': ['soil.drainage', 'mmH2O', []]
                                    }

            self.annual_variables = {'year': ['time.calendar_year', '', 0],
                                     'actual': ['round(soil.p_act_annual, 3)', 'mmH2O', 0],
                                     'calculated': ['round(soil.p_calc_annual, 3)', 'mmH2O', 0],
                                     'difference': ['round(soil.water_balance_difference_annual, 3)', 'mmH2O', 0],
                                     'delta': ['round(soil.delta_SW_annual, 3)', 'mmH2O', 0],
                                     'runoff': ['round(soil.runoff_annual, 3)', 'mmH2O', 0],
                                     'evaporation': ['round(soil.evap_annual, 3)', 'mmH2O', 0],
                                     'transpiration': ['round(soil.trans_annual, 3)', 'mmH2O', 0],
                                     'drainage': ['round(soil.drainage_annual, 3)', 'mmH2O', 0],
                                     # all new variables should be added below here
                                     }

    class PhosphorusBalance(BaseFieldMassBalanceReport):
        def __init__(self, data, field_name):
            super().__init__(data, field_name)

            self.daily_variables = {
                'year': ['time.calendar_year', '', []],
                'j_day': ['time.day', '', []],
                'actual': ['field_management.manure_P_applied', 'kg', []],
                'calculated': ['soil.P_calc', 'kg', []],
                'difference': ['soil.P_balance_difference', 'kg', []],
                'delta': ['soil.delta_P', 'kg', []],
                'P_drainage': ['soil.P_drainage', 'kg', []],
                'P_runoff': ['soil.P_runoff', 'kg', []],
                'P_erosion': ['soil.P_erosion', 'kg', []],
                'P_uptake': ['soil.P_uptake', 'kg', []]
            }

            self.annual_variables = {
                'year': ['time.calendar_year', '', 0],
                'actual': ['field_management.manure_P_applied_annual', 'kg', 0],
                'calculated': ['soil.P_calc_annual', 'kg', 0],
                'difference': ['soil.P_balance_difference_annual', 'kg', 0],
                'delta': ['soil.delta_P_annual', 'kg', 0],
                'P_drainage': ['soil.P_drainage_annual', 'kg', 0],
                'P_runoff': ['soil.P_runoff_annual', 'kg', 0],
                'P_erosion': ['soil.P_erosion_annual', 'kg', 0],
                'P_uptake': ['soil.P_uptake_annual', 'kg', 0]
            }

    class NitrogenBalance(BaseFieldMassBalanceReport):
        def __init__(self, data, field_name):
            super().__init__(data, field_name)

            self.daily_variables = {
                'year': ['time.calendar_year', '', []],
                'j_day': ['time.day', '', []],
                'actual': ['field_management.manure_N_applied', 'kg', []],
                'calculated': ['soil.N_calc', 'kg', []],
                'difference': ['soil.N_balance_difference', 'kg', []],
                'delta': ['soil.delta_N', 'kg N', []],
                # 'NH4': ['soil.NH4', 'kg', []],
                # 'NO3': ['soil.NO3', 'kg', []],
                # 'org_N': ['soil.org_N', 'kg', []],
                # 'active_N': ['soil.active_N', 'kg', []],
                # 'stable_N': ['soil.stable_N', 'kg', []],
                # 'fresh_N': ['soil.fresh_N', 'kg', []],
                # 'NO3_drainage': ['soil.NO3_drainage', 'kg', []],
                # 'NH4_drainage': ['soil.NH4_drainage', 'kg', []],
                # 'active_N_drainage': ['soil.active_N_drainage', 'kg', []],
                'N_drainage': ['soil.N_drainage', 'kg', []],
                # 'NO3_runoff': ['soil.NO3_runoff', 'kg', []],
                # 'NH4_runoff': ['soil.NH4_runoff', 'kg', []],
                'N_runoff': ['soil.N_runoff', 'kg', []],
                # 'NH4_erosion': ['soil.NH4_erosion', 'kg', []],
                # 'active_N_erosion': ['soil.active_N_erosion', 'kg', []],
                # 'fresh_N_erosion': ['soil.fresh_N_erosion', 'kg', []],
                'N_erosion': ['soil.N_erosion', 'kg', []],
                'N_uptake': ['soil.N_uptake', 'kg', []]
            }

            self.annual_variables = {
                'year': ['time.calendar_year', '', 0],
                'actual': ['field_management.manure_N_applied_annual', 'kg', 0],
                'calculated': ['soil.N_calc_annual', 'kg', 0],
                'difference': ['soil.N_balance_difference_annual', 'kg', 0],
                'delta': ['soil.delta_N_annual', 'kg', 0],
                'N_drainage': ['soil.N_drainage_annual', 'kg', 0],
                'N_runoff': ['soil.N_runoff_annual', 'kg', 0],
                'N_erosion': ['soil.N_erosion_annual', 'kg', 0],
                'N_uptake': ['soil.N_uptake_annual', 'kg', 0]
            }
