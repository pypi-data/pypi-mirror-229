import re
from typing import Callable, Union, Any

from pydantic import BaseModel

from deep_replacer import helpers
from deep_replacer.exceptions import DeepReplacerError
from deep_replacer.key_depth_rules import (
    IGNORE,
    IGNORE_STR_WITHOUT_LETTERS,
    APPLY_ON_TEXT_BETWEEN_PARENTHESIS,
)


def raise_data_type_error():
    raise DeepReplacerError("Data must be a list, set, tuple or dictionary")


class DeepReplacer:
    def __is_dict(self, data: Any) -> bool:
        """Check if data is dict"""

        return isinstance(data, dict)

    def __is_pydantic(self, data: Any) -> bool:
        """Check if data is pydantic"""

        return isinstance(data, BaseModel)

    def __is_list_or_set_or_tuple(self, data: Any):
        """Check if data is list, set or tuple"""

        return (
            isinstance(data, list) or isinstance(data, set) or isinstance(data, tuple)
        )

    def __is_iterable(self, data: Any) -> bool:
        """Check if data is iterable (ignore str)"""

        return self.__is_list_or_set_or_tuple(data) or isinstance(data, dict)

    def __replace(
        self,
        data: Union[list, set, tuple, dict],
        replace_func: Callable,
        pydantic_to_dict: bool,
        ignore_keys: set,
        key_depth_rules: dict[str, set[str]],
        previous_key_depth: str = "",
    ) -> Union[list, set, tuple, dict]:
        """Replace function for internal use"""

        # Convert pydantic model to dictionary to further treat it as such
        if pydantic_to_dict and self.__is_pydantic(data):
            data = dict(data)

        # Handle list or set or tuple
        if self.__is_list_or_set_or_tuple(data):
            tmp_list = list()

            # Convert to list
            if isinstance(data, set) or isinstance(data, tuple):
                data_list = list(data)
            else:
                data_list = data

            for value in data_list:
                # Convert pydantic model to dictionary to further treat it as such
                if pydantic_to_dict and self.__is_pydantic(value):
                    value = dict(value)

                # If iterable, recursively call this function
                if self.__is_iterable(value):
                    tmp_list.append(
                        self.__replace(
                            data=value,
                            replace_func=replace_func,
                            pydantic_to_dict=pydantic_to_dict,
                            ignore_keys=ignore_keys,
                            key_depth_rules=key_depth_rules,
                            previous_key_depth=previous_key_depth,
                        )
                    )

                # Apply replace_func
                else:
                    tmp_list.append(replace_func(value))

            # Return result
            if isinstance(data, set):
                return set(tmp_list)
            elif isinstance(data, tuple):
                return tuple(tmp_list)
            else:
                return tmp_list

        # Handle dictionary
        elif self.__is_dict(data):
            tmp_dict = dict()

            for key, value in data.items():
                # Ignore key
                if key in ignore_keys:
                    tmp_dict[key] = value
                    continue

                # Get current key depth
                key_depth_current = f"{previous_key_depth}{key}"

                # Get key depth rules of the current key
                current_key_depth_rules = key_depth_rules.get(key_depth_current, set())

                # Apply rule: Ignore key depth
                if IGNORE in current_key_depth_rules:
                    tmp_dict[key] = value
                    continue

                # Convert pydantic model to dictionary to further treat it as such
                if pydantic_to_dict and self.__is_pydantic(value):
                    value = dict(value)

                # If iterable, recursively call this function
                if self.__is_iterable(value):
                    tmp_dict[key] = self.__replace(
                        data=value,
                        replace_func=replace_func,
                        pydantic_to_dict=pydantic_to_dict,
                        ignore_keys=ignore_keys,
                        key_depth_rules=key_depth_rules,
                        previous_key_depth=f"{key_depth_current}:",
                    )
                else:
                    # Apply rule IGNORE_STR_WITHOUT_LETTERS
                    if (
                        type(value).__name__ == "str"
                        and IGNORE_STR_WITHOUT_LETTERS in current_key_depth_rules
                    ):
                        if not helpers.contains_letters(value):
                            tmp_dict[key] = value
                            continue

                    # Apply 'replace function' with rule APPLY_ON_TEXT_BETWEEN_PARENTHESIS
                    if (
                        type(value).__name__ == "str"
                        and APPLY_ON_TEXT_BETWEEN_PARENTHESIS in current_key_depth_rules
                    ):
                        texts_between_parentheses = re.findall("\\(([^)]+)", value)
                        if len(texts_between_parentheses) > 0:
                            text_between_parenthesis = texts_between_parentheses[-1]
                            tmp_dict[key] = value.replace(
                                text_between_parenthesis,
                                replace_func(text_between_parenthesis),
                            )
                        else:
                            tmp_dict[key] = replace_func(value)

                    # Apply 'replace function'
                    else:
                        tmp_dict[key] = replace_func(value)

            # Return dictionary result
            return tmp_dict

        else:
            raise_data_type_error()

    def replace(
        self,
        data: Union[list, set, tuple, dict, BaseModel],
        replace_func: Callable,
        pydantic_to_dict: bool = False,
        ignore_keys: list = None,
        key_depth_rules: dict[str, list[str]] = None,
    ) -> Union[list, set, tuple, dict]:
        """
        Given a list, set, tuple or dictionary as data input, loop through the data and replace all values
        that are not a list, set, tuple or dictionary using a replace function.

        :param data: Input data, supports lists, sets, tuples and dictionaries
        :param replace_func: Function used for replacing values
        :param pydantic_to_dict: Convert pydantic models found to dictionary
        :param ignore_keys: Always ignore these dictionary keys
        :param key_depth_rules: Rules to apply at a specific dictionary key depth
        """

        if not pydantic_to_dict and isinstance(data, BaseModel):
            raise_data_type_error()

        # Convert pydantic model to dictionary to further treat it as such
        if pydantic_to_dict and isinstance(data, BaseModel):
            data = dict(data)

        # Check if data is iterable
        if not self.__is_iterable(data):
            raise_data_type_error()

        # Change list to set and use str as set values
        key_depth_rules_parsed: dict[str, set[str]] = {}
        if key_depth_rules:
            for key, value in key_depth_rules.items():
                if isinstance(value, str):
                    key_depth_rules_parsed[key] = {value}
                else:
                    key_depth_rules_parsed[key] = {x for x in value}

        # Change list to set
        if ignore_keys:
            ignore_keys_parsed = set(ignore_keys)
        else:
            ignore_keys_parsed = set()

        return self.__replace(
            data=data,
            replace_func=replace_func,
            pydantic_to_dict=pydantic_to_dict,
            ignore_keys=ignore_keys_parsed,
            key_depth_rules=key_depth_rules_parsed,
        )
