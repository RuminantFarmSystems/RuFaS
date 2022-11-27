from typing import Dict
from typing import List
from typing import Optional

from RUFAS.routines.manure.beddings.bedding_classes import BeddingConfig
from RUFAS.routines.manure.beddings.bedding_classes import BeddingType
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManureHandlerConfig
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManureHandlerType
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorConfig
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorType
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType


class ManureManagementConfigHandler:
    def __init__(self, manure_management_config):
        self.custom_bedding_configs = self._process_bedding_configs(manure_management_config['bedding_configs'])
        self.custom_manure_handler_configs = \
            self._process_manure_handler_configs(manure_management_config['manure_handler_configs'])
        self.custom_manure_separator_configs = \
            self._process_manure_separator_configs(manure_management_config['manure_separator_configs'])
        self.custom_manure_treatment_configs = \
            self._process_manure_treatment_configs(manure_management_config['manure_treatment_configs'])

    def get_custom_bedding_config(self, bedding_type_name: str) -> Optional[BeddingConfig]:
        return self.custom_bedding_configs.get(BeddingType.get_type(bedding_type_name), None)

    def get_custom_manure_handler_config(self, manure_handler_type_name: str) -> Optional[ManureHandlerConfig]:
        return self.custom_manure_handler_configs.get(ManureHandlerType.get_type(manure_handler_type_name), None)

    def get_custom_manure_separator_config(self, manure_separator_type_name: str) -> Optional[ManureSeparatorConfig]:
        return self.custom_manure_separator_configs.get(ManureSeparatorType.get_type(manure_separator_type_name), None)

    def get_custom_manure_treatment_config(self, manure_treatment_type_name: str) -> Optional[ManureTreatmentConfig]:
        return self.custom_manure_treatment_configs.get(ManureTreatmentType.get_type(manure_treatment_type_name), None)

    @staticmethod
    def _process_bedding_configs(json_bedding_configs: List[Dict]) -> Dict[BeddingType, BeddingConfig]:
        bedding_config_by_bedding_type: Dict[BeddingType, BeddingConfig] = {}
        for json_bedding_config in json_bedding_configs:
            bedding_type = BeddingType.get_type(json_bedding_config['bedding_type'])
            del json_bedding_config['bedding_type']
            bedding_config_by_bedding_type[bedding_type] = BeddingConfig(
                    **json_bedding_config,
                    bedding_type=bedding_type
            )
        return bedding_config_by_bedding_type

    @staticmethod
    def _process_manure_handler_configs(json_manure_handler_configs: List[Dict]) \
            -> Dict[ManureHandlerType, ManureHandlerConfig]:
        manure_handler_config_by_manure_handler_type: Dict[ManureHandlerType, ManureHandlerConfig] = {}
        for json_manure_handler_config in json_manure_handler_configs:
            manure_handler_type = ManureHandlerType.get_type(json_manure_handler_config['manure_handler_type'])
            del json_manure_handler_config['manure_handler_type']
            manure_handler_config_by_manure_handler_type[manure_handler_type] = ManureHandlerConfig(
                    **json_manure_handler_config
            )
        return manure_handler_config_by_manure_handler_type

    @staticmethod
    def _process_manure_separator_configs(json_manure_separator_configs: List[Dict]) \
            -> Dict[ManureSeparatorType, ManureSeparatorConfig]:
        manure_separator_config_by_manure_separator_type: Dict[ManureSeparatorType, ManureSeparatorConfig] = {}
        for json_manure_separator_config in json_manure_separator_configs:
            manure_separator_type = ManureSeparatorType.get_type(
                    json_manure_separator_config['manure_separator_type']
            )
            del json_manure_separator_config['manure_separator_type']
            manure_separator_config_by_manure_separator_type[manure_separator_type] = ManureSeparatorConfig(
                    **json_manure_separator_config
            )
        return manure_separator_config_by_manure_separator_type

    @staticmethod
    def _process_manure_treatment_configs(json_manure_treatment_configs: List[Dict]) \
            -> Dict[ManureTreatmentType, ManureTreatmentConfig]:
        manure_treatment_config_by_manure_treatment_type: Dict[ManureTreatmentType, ManureTreatmentConfig] = {}
        for json_manure_treatment_config in json_manure_treatment_configs:
            manure_treatment_type = ManureTreatmentType.get_type(json_manure_treatment_config['manure_treatment_type'])
            del json_manure_treatment_config['manure_treatment_type']
            manure_treatment_config_by_manure_treatment_type[manure_treatment_type] = ManureTreatmentConfig(
                    **json_manure_treatment_config
            )
        return manure_treatment_config_by_manure_treatment_type
