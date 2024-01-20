from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from RUFAS.routines.manure.beddings.bedding_classes import BeddingConfig
from RUFAS.routines.manure.beddings.bedding_classes import BeddingType
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    ManureHandlerConfig,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    ManureHandlerType,
)
from RUFAS.routines.manure.manure_separators.manure_separator_classes import (
    ManureSeparatorConfig,
)
from RUFAS.routines.manure.manure_separators.manure_separator_classes import (
    ManureSeparatorType,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    ManureTreatmentConfig,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import (
    ManureTreatmentType,
)


class ManureManagerConfigHandler:
    """A class that manages the custom manure manager configs."""

    def __init__(self, manure_manager_config):
        """Initializes the ManureManagerConfigHandler class.

        Parameters
        ----------
        manure_manager_config : Dict
            The manure manager config dictionary that contains all the manure manager config information.

        """
        self.custom_bedding_configs = self._process_bedding_configs(
            manure_manager_config["bedding_configs"]
        )
        self.custom_manure_handler_configs = self._process_manure_handler_configs(
            manure_manager_config["manure_handler_configs"]
        )
        self.custom_manure_separator_configs = self._process_manure_separator_configs(
            manure_manager_config["manure_separator_configs"]
        )
        self.custom_manure_treatment_configs = self._process_manure_treatment_configs(
            manure_manager_config["manure_treatment_configs"]
        )

    def get_custom_bedding_config(
        self, bedding_type_name: str
    ) -> Optional[BeddingConfig]:
        """Returns the custom bedding config for the given bedding type name, or None if no custom config exists.

        Parameters
        ----------
        bedding_type_name : str
            The name of the bedding type for which to get the custom config.

        Returns
        -------
        Optional[BeddingConfig]
            The custom bedding config for the given bedding type name, or None if no custom config exists.

        """
        return self.custom_bedding_configs.get(
            BeddingType.get_type(bedding_type_name), None
        )

    def get_custom_manure_handler_config(
        self, manure_handler_type_name: str
    ) -> Optional[ManureHandlerConfig]:
        """Returns the custom manure handler config for the given manure handler type name, or None if no custom
        config exists.

        Parameters
        ----------
        manure_handler_type_name : str
            The name of the manure handler type for which to get the custom config.

        Returns
        -------
        Optional[ManureHandlerConfig]
            The custom manure handler config for the given manure handler type name, or None if no custom config exists.

        """
        return self.custom_manure_handler_configs.get(
            ManureHandlerType.get_type(manure_handler_type_name), None
        )

    def get_custom_manure_separator_config(
        self, manure_separator_type_name: str
    ) -> Optional[ManureSeparatorConfig]:
        """Returns the custom manure separator config for the given manure separator type name, or None if no custom
        config exists.

        Parameters
        ----------
        manure_separator_type_name : str
            The name of the manure separator type for which to get the custom config.

        Returns
        -------
        Optional[ManureSeparatorConfig]
            The custom manure separator config for the given manure separator type name, or None if no custom config
            exists.

        """
        return self.custom_manure_separator_configs.get(
            ManureSeparatorType.get_type(manure_separator_type_name), None
        )

    def get_custom_manure_treatment_config(
        self, manure_treatment_type_name: str
    ) -> Optional[ManureTreatmentConfig]:
        """Returns the custom manure treatment config for the given manure treatment type name, or None if no custom
        config exists.

        Parameters
        ----------
        manure_treatment_type_name : str
            The name of the manure treatment type for which to get the custom config.

        Returns
        -------
        Optional[ManureTreatmentConfig]
            The custom manure treatment config for the given manure treatment type name, or None if no custom config
            exists.

        """
        return self.custom_manure_treatment_configs.get(
            ManureTreatmentType.get_type(manure_treatment_type_name), None
        )

    @classmethod
    def _process_bedding_configs(
        cls, bedding_json_configs: List[Dict]
    ) -> Dict[BeddingType, BeddingConfig]:
        """Returns a dictionary of bedding config objects, with the key being the bedding type.

        Parameters
        ----------
        bedding_json_configs : List[Dict]
            A list of dictionaries containing the bedding config information.

        Returns
        -------
        Dict[BeddingType, BeddingConfig]
            A dictionary of bedding config objects, with the key being the bedding type.

        """
        bedding_config_by_bedding_type: Dict[BeddingType, BeddingConfig] = {}
        for json_bedding_config in bedding_json_configs:
            bedding_type = BeddingType.get_type(json_bedding_config["bedding_type"])
            del json_bedding_config["bedding_type"]
            bedding_config_by_bedding_type[bedding_type] = BeddingConfig(
                **json_bedding_config, bedding_type=bedding_type
            )
        return bedding_config_by_bedding_type

    @classmethod
    def _process_manure_handler_configs(
        cls, manure_handler_json_configs: List[Dict]
    ) -> Dict[ManureHandlerType, ManureHandlerConfig]:
        """Returns a dictionary of manure handler config objects, with the key being the manure handler type.

        Parameters
        ----------
        manure_handler_json_configs : List[Dict]
            A list of dictionaries containing the manure handler config information.

        Returns
        -------
        Dict[ManureHandlerType, ManureHandlerConfig]
            A dictionary of manure handler config objects, with the key being the manure handler type.

        """
        manure_handler_config_by_manure_handler_type: Dict[
            ManureHandlerType, ManureHandlerConfig
        ] = {}
        for json_manure_handler_config in manure_handler_json_configs:
            manure_handler_type = ManureHandlerType.get_type(
                json_manure_handler_config["manure_handler_type"]
            )
            del json_manure_handler_config["manure_handler_type"]
            manure_handler_config_by_manure_handler_type[
                manure_handler_type
            ] = ManureHandlerConfig(**json_manure_handler_config)
        return manure_handler_config_by_manure_handler_type

    @classmethod
    def _process_manure_separator_configs(
        cls, manure_separator_json_configs: List[Dict]
    ) -> Dict[ManureSeparatorType, ManureSeparatorConfig]:
        """Returns a dictionary of manure separator config objects, with the key being the manure separator type.

        Parameters
        ----------
        manure_separator_json_configs : List[Dict]
            A list of dictionaries containing the manure separator config information.

        Returns
        -------
        Dict[ManureSeparatorType, ManureSeparatorConfig]
            A dictionary of manure separator config objects, with the key being the manure separator type.

        """
        manure_separator_config_by_manure_separator_type: Dict[
            ManureSeparatorType, ManureSeparatorConfig
        ] = {}
        for json_manure_separator_config in manure_separator_json_configs:
            manure_separator_type = ManureSeparatorType.get_type(
                json_manure_separator_config["manure_separator_type"]
            )
            del json_manure_separator_config["manure_separator_type"]
            manure_separator_config_by_manure_separator_type[
                manure_separator_type
            ] = ManureSeparatorConfig(**json_manure_separator_config)
        return manure_separator_config_by_manure_separator_type

    @classmethod
    def _process_manure_treatment_configs(
        cls, manure_treatment_json_configs: List[Dict]
    ) -> Dict[
        ManureTreatmentType,
        Union[
            ManureTreatmentConfig, Tuple[ManureTreatmentConfig, ManureTreatmentConfig]
        ],
    ]:
        """Returns a dictionary of manure treatment config objects, with the key being the manure treatment type.

        There is one special case that involves a combination of anaerobic digestion and anaerobic
        lagoon. In this case, we return a tuple of the two manure treatment configs.

        Parameters
        ----------
        manure_treatment_json_configs : List[Dict]
            A list of dictionaries containing the manure treatment config information.

        Returns
        -------
        Dict[ManureTreatmentType, Union[ManureTreatmentConfig, Tuple[ManureTreatmentConfig, ManureTreatmentConfig]]]
            A dictionary of manure treatment config objects, with the key being the manure treatment type.

        """
        manure_treatment_config_by_type: Dict[
            ManureTreatmentType,
            Union[
                ManureTreatmentConfig,
                Tuple[ManureTreatmentConfig, ManureTreatmentConfig],
            ],
        ] = {}

        for json_manure_treatment_config in manure_treatment_json_configs:
            manure_treatment_type = ManureTreatmentType.get_type(
                json_manure_treatment_config["manure_treatment_type"]
            )
            del json_manure_treatment_config["manure_treatment_type"]
            manure_treatment_config_by_type[
                manure_treatment_type
            ] = ManureTreatmentConfig(**json_manure_treatment_config)

        # Only do this because we only have one special case
        if (
            ManureTreatmentType.ANAEROBIC_LAGOON in manure_treatment_config_by_type
            and ManureTreatmentType.ANAEROBIC_DIGESTION
            in manure_treatment_config_by_type
        ):
            combo_config = (
                manure_treatment_config_by_type[
                    ManureTreatmentType.ANAEROBIC_DIGESTION
                ],
                manure_treatment_config_by_type[ManureTreatmentType.ANAEROBIC_LAGOON],
            )
            manure_treatment_config_by_type[
                ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON
            ] = manure_treatment_config_by_type[
                ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT
            ] = combo_config

        return manure_treatment_config_by_type
