from typing import Any

from RUFAS.input_manager import InputManager


class CrossValidator:
    def __init__(self) -> None:
        self._alias_pool: dict[str, Any] = {}
        self._event_logs: list[dict[str, str | dict[str, str]]] = []
        self.im = InputManager()

    def cross_validate_data(
        self, im_variable_pool: dict[str, Any], cross_validation_rules: list[dict[str, Any]]
    ) -> bool:
        """
        Performs cross-validation on the provided data using the provided cross validation rules.

        Parameters
        ----------
        im_variable_pool : dict[str, Any]
            A dictionary containing the InputManager variable pool to be validated.
        cross_validation_rules : list[dict[str, Any]]
            A list of dictionaries containing the cross-validation rules to be applied.

        Returns
        -------
        bool
            A boolean indicating whether the data passed cross-validation.
        """
        pass

    def _save_to_alias_pool(self, alias_name: str, value: Any) -> None:
        """
        Saves a value to the alias pool with the specified alias name.

        Parameters
        ----------
        alias_name : str
            The name of the alias to be saved.
        value : Any
            The value to be saved.
        """
        self._alias_pool[alias_name] = value

    def _get_alias_value(self, alias_name: str) -> Any:
        """
        Retrieves the value associated with the specified alias name from the alias pool.

        Parameters
        ----------
        alias_name : str
            The alias of the value to retrieve.

        Returns
        -------
        Any
            The value associated with the specified alias name from the alias pool.
        """
        try:
            return self._alias_pool[alias_name]
        except KeyError:
            self._event_logs.append(
                {
                    "error": "Alias name not found.",
                    "message": f"{alias_name} doe not exits in the alias pool of cross validator.",
                    "info_map": {
                        "class": CrossValidator.__name__,
                        "function": CrossValidator._get_alias_value.__name__,
                    },
                }
            )
            return None

    def _target_and_save(self, target_and_save_block: dict[str, dict[str, Any]]) -> None:
        """
        This function handles the "target and save block" in the cross-validation rule.
        It retrieves the value of the target variable from the InputManager variable pool
        and saves it to the alias pool with the specified alias name. It also saves the
        constants defined in the "constants" block to the alias pool with the specified alias.

        Parameters
        ----------
        target_and_save_block : dict[str, dict[str, Any]]
            A dictionary containing the "target and save block" of the cross-validation rule.

        """
        self._check_target_and_save_block(target_and_save_block)
        sections = ["variables", "constants"]
        for section in sections:
            if section == "variables":
                for key, address in target_and_save_block[section].items():
                    self._alias_pool[key] = self.im.get_data(address)
            else:
                for constant_name, value in target_and_save_block[section].items():
                    self._alias_pool[constant_name] = value

    def _check_target_and_save_block(self, target_and_save_block: dict[str, dict[str, Any]]) -> None:
        """Check if the target and save block is valid."""
        for section in target_and_save_block.keys():
            if section not in ["variables", "constants"]:
                self._event_logs.append(
                    {
                        "error": "Unsupported Target and Save Block Content",
                        "message": "Only constants or variables keys' content will be processed for retrieving and"
                        f" saving values. Unsupported keys {section} provided.",
                        "info_map": {
                            "class": CrossValidator.__name__,
                            "function": CrossValidator._check_target_and_save_block.__name__,
                        },
                    }
                )

    def _evaluate_expression(self, expression_block: dict[str, Any]) -> Any:
        """
        Evaluates an expression based on the provided expression block. This function also
        optionally adds to the alias pool if the "save_as" key is present in the expression block.

        Parameters
        ----------
        expression_block : dict[str, Any]
            A dictionary containing the expression block to be evaluated.

        Returns
        -------
        Any
            The result of the expression.
        """
        pass

    def _evaluate_condition(self, condition_clause: dict[str, Any]) -> bool:
        """
        Evaluates if a single condition is satisfied based on the provided condition clause.

        Parameters
        ----------
        condition_clause : dict[str, Any]
            The condition clause to be evaluated.

        Returns
        -------
        bool
            A boolean indicating whether the condition is satisfied.
        """
        pass

    def _evaluate_condition_clause_array(self, condition_clause_array: list[dict[str, Any]]) -> bool:
        """
        Evaluates if all conditions in the provided condition clause array are satisfied.

        Parameters
        ----------
        condition_clause_array : list[dict[str, Any]]
            An array of condition clauses to be evaluated.

        Returns
        -------
        bool
            A boolean indicating whether all conditions in the array are satisfied.
        """
        pass
