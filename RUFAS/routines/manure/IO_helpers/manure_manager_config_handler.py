from typing import Any, Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from RUFAS.output_manager import OutputManager
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

om = OutputManager()


class ManureManagerConfigHandler:
    """A class that manages the custom manure manager configs."""

    def __init__(self, manure_manager_config):
        """Initializes the ManureManagerConfigHandler class.

        Parameters
        ----------
        manure_manager_config : Dict
            The manure manager config dictionary that contains all the manure manager config information.

        """
        self.bedding_configs = self._process_bedding_configs(manure_manager_config["bedding_configs"])
        self.manure_handler_configs = self._process_manure_handler_configs(
            manure_manager_config["manure_handler_configs"]
        )
        self.manure_separator_configs = self._process_manure_separator_configs(
            manure_manager_config["manure_separator_configs"]
        )
        self.manure_treatment_configs = self._process_manure_treatment_configs(
            manure_manager_config["manure_treatment_configs"]
        )

    def get_bedding_config(self, bedding_name: str) -> BeddingConfig:
        """Returns the bedding config for the given bedding type name.

        Parameters
        ----------
        bedding_name : str
            The name of the bedding configuration for which to get the config.

        Returns
        -------
        BeddingConfig
            The bedding config associated with the given bedding name.

        """
        try:
            return self.bedding_configs[bedding_name]
        except KeyError:
            info_map = {"class": self.__class__.__name__, "function": self.get_bedding_config.__name__}
            error_title = "Unknown manure bedding configuration name"
            error_message = f"Attempted to use a non-existent manure bedding configuration called '{bedding_name}'"
            om.add_error(error_title, error_message, info_map)
            raise KeyError(error_message)

    def get_manure_handler_config(self, manure_handler_type_name: str) -> ManureHandlerConfig:
        """Returns the manure handler config for the given manure handler type name.

        Parameters
        ----------
        manure_handler_type_name : str
            The name of the manure handler type for which to get the config.

        Returns
        -------
        ManureHandlerConfig
            The manure handler config for the given manure handler type name.

        Raises
        ------
        KeyError
            If the name of the manure handler type is not present in the available manure handler configs.

        """
        try:
            return self.manure_handler_configs[manure_handler_type_name]
        except KeyError:
            info_map = {
                "class": self.__class__.__name__,
                "function": self.get_manure_handler_config.__name__,
            }
            error_title = "Unknown manure handler configuration name"
            error_message = (
                f"Attempted to use a non-existent manure handler configuration called '{manure_handler_type_name}'"
            )
            om.add_error(error_title, error_message, info_map)
            raise KeyError(error_message)

    def get_manure_separator_config(self, manure_separator_name: str) -> Optional[ManureSeparatorConfig]:
        """
        Returns the config for the given manure separator name, or None if no separation is to occur.

        Parameters
        ----------
        manure_separator_name : str
            The name of the manure separator type for which to get the config.

        Returns
        -------
        Optional[ManureSeparatorConfig]
            The manure separator config for the given manure separator type name, or None if the requested config is
            "none".

        Raises
        ------
        KeyError
            If the specified manure separator config name is not present and is not "none".

        """
        if manure_separator_name == "none":
            return None
        try:
            return self.manure_separator_configs[manure_separator_name]
        except KeyError:
            info_map = {"class": self.__class__.__name__, "function": self.get_manure_separator_config.__name__}
            error_title = "Unknown manure separator configuration name"
            error_message = (
                f"Attempted to use a non-existent manure separator configuration called '{manure_separator_name}'"
            )
            om.add_error(error_title, error_message, info_map)
            raise KeyError(error_message)

    def get_manure_treatment_config(self, manure_treatment_type_name: str) -> ManureTreatmentConfig:
        """
        Returns the custom manure treatment config for the given manure treatment type name.

        Parameters
        ----------
        manure_treatment_type_name : str
            The name of the manure treatment type for which to get the config.

        Returns
        -------
        ManureTreatmentConfig
            The manure treatment config for the given manure treatment type name.

        Raises
        ------
        KeyError
            If the specified manure treatment config name is not present in the available manure treatment configs.

        """
        try:
            return self.manure_treatment_configs[manure_treatment_type_name]
        except KeyError:
            info_map = {"class": self.__class__.__name__, "function": self.get_manure_treatment_config.__name__}
            error_title = "Unknown manure treatment configuration name"
            error_message = (
                f"Attempted to use a non-existent manure treatment configuration called '{manure_treatment_type_name}'"
            )
            om.add_error(error_title, error_message, info_map)
            raise KeyError(error_message)

    @classmethod
    def _process_bedding_configs(cls, bedding_configs: List[Dict]) -> Dict[str, BeddingConfig]:
        """
        Creates a mapping of bedding configs to be used when setting up manure beddings.

        Parameters
        ----------
        bedding_configs : List[Dict]
            A list of dictionaries containing the bedding config information.

        Returns
        -------
        Dict[str, BeddingConfig]
            A dictionary of bedding config objects, with the key being the bedding name.

        """
        info_map = {"class": cls.__class__.__name__, "function": cls._process_bedding_configs.__name__}
        available_bedding_configs: Dict[str, BeddingConfig] = {}
        for config in bedding_configs:
            bedding_name = config.pop("name")
            if bedding_name in available_bedding_configs:
                error_name = "Duplicate bedding configurations found"
                error_message = f"Bedding config '{bedding_name}' has multiple configurations"
                om.add_error(error_name, error_message, info_map)
                raise ValueError(error_message)
            bedding_type = BeddingType(config["bedding_type"])
            del config["bedding_type"]
            available_bedding_configs[bedding_name] = BeddingConfig(**config, bedding_type=bedding_type)
        return available_bedding_configs

    @classmethod
    def _process_manure_handler_configs(cls, manure_handler_configs: List[Dict]) -> Dict[str, ManureHandlerConfig]:
        """
        Returns a dictionary of manure handler config objects, with the key being the name of the manure handler
        configuration option.

        Parameters
        ----------
        manure_handler_configs : List[Dict]
            A list of dictionaries containing the manure handler config information.

        Returns
        -------
        Dict[str, ManureHandlerConfig]
            A dictionary of manure handler config objects, with the key being the manure handler type.

        Raises
        ------
        ValueError
            If there are multiple configurations for one configuration name.

        """

        info_map = {
            "class": cls.__name__,
            "function": cls._process_manure_handler_configs.__name__,
        }

        available_manure_handler_configs: Dict[str, ManureHandlerConfig] = {}

        for manure_handler_config in manure_handler_configs:
            handler_name = manure_handler_config.pop("name")
            if handler_name in available_manure_handler_configs:
                error_name = "Duplicate manure handler configurations"
                error_message = f"Manure handler '{handler_name}' has multiple configurations"
                om.add_error(error_name, error_message, info_map)
                raise ValueError(error_message)
            handler_type = ManureHandlerType(manure_handler_config["manure_handler_type"])
            manure_handler_config["manure_handler_type"] = handler_type
            available_manure_handler_configs[handler_name] = ManureHandlerConfig(**manure_handler_config)
        return available_manure_handler_configs

    @classmethod
    def _process_manure_separator_configs(
        cls, manure_separator_configs: list[dict[str, Any]]
    ) -> Dict[str, ManureSeparatorConfig | None]:
        """
        Returns a dictionary of manure separator config objects, with the key being the name of the separator config.

        Parameters
        ----------
        manure_separator_configs : list[dict[str, Any]]
            A list of dictionaries containing the manure separator config information.

        Returns
        -------
        Dict[ManureSeparatorType, ManureSeparatorConfig | None]
            A dictionary of manure separator config objects, with the key being the manure separator type.

        """
        info_map = {"class": cls.__name__, "function": cls._process_manure_separator_configs.__name__}

        available_manure_separator_configs: Dict[str, ManureSeparatorConfig | None] = {}
        for config in manure_separator_configs:
            name = config.pop("name")
            if name in available_manure_separator_configs:
                error_name = "Duplicate manure separator configurations"
                error_message = f"Manure separator '{name}' has multiple configurations"
                om.add_error(error_name, error_message, info_map)
                raise ValueError(error_message)
            config["manure_separator_type"] = ManureSeparatorType(config["manure_separator_type"])
            available_manure_separator_configs[name] = ManureSeparatorConfig(**config)
        return available_manure_separator_configs

    @classmethod
    def _process_manure_treatment_configs(cls, manure_treatment_configs: list[dict[str, Any]]) -> dict[
        str, Union[ManureTreatmentConfig, Tuple[ManureTreatmentConfig, ManureTreatmentConfig]]
    ]:
        """Returns a dictionary of manure treatment config objects, with the key being the manure treatment type.

        There is one special case that involves a combination of anaerobic digestion and anaerobic
        lagoon. In this case, we return a tuple of the two manure treatment configs.

        Parameters
        ----------
        manure_treatment_configs : list[dict[str, Any]]
            A list of dictionaries containing the manure treatment config information.

        Returns
        -------
        dict[str, Union[ManureTreatmentConfig, Tuple[ManureTreatmentConfig, ManureTreatmentConfig]]]
            A dictionary of manure treatment config objects, with the key being the manure treatment type.

        """
        info_map = {"class": cls.__name__, "function": cls._process_manure_treatment_configs.__name__}
        available_manure_treatment_configs: dict[
            str, ManureTreatmentConfig | tuple[ManureTreatmentConfig, ManureTreatmentConfig]
        ] = {}

        for config in manure_treatment_configs:
            name = config.pop("name")
            if name in available_manure_treatment_configs:
                error_name = "Duplicate manure separator configurations"
                error_message = f"Manure treatment '{name}' has multiple configurations"
                om.add_error(error_name, error_message, info_map)
                raise ValueError(error_message)
            config["manure_treatment_type"] = ManureTreatmentType(config["manure_treatment_type"])
            available_manure_treatment_configs[name] = ManureTreatmentConfig(**config)

        # Only do this because we only have one special case
        if (
            ManureTreatmentType.ANAEROBIC_LAGOON in manure_treatment_config_by_type
            and ManureTreatmentType.ANAEROBIC_DIGESTION in manure_treatment_config_by_type
        ):
            combo_config = (
                manure_treatment_config_by_type[ManureTreatmentType.ANAEROBIC_DIGESTION],
                manure_treatment_config_by_type[ManureTreatmentType.ANAEROBIC_LAGOON],
            )
            manure_treatment_config_by_type[ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON] = (
                manure_treatment_config_by_type[ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SEPARATOR]
            ) = combo_config

        return manure_treatment_config_by_type
