from typing import Callable

from RUFAS.routines.manure_management.helpers.enum_helpers import DefaultEnum
from RUFAS.routines.manure_management.manure_handlers.manure_handler_enum import ManureHandlerEnum


def test_default_enum_member_should_return_flush_system_enum() -> None:
    assert ManureHandlerEnum.DEFAULT is ManureHandlerEnum.FLUSH_SYSTEM


def test_get_default_enum_should_return_flush_system_enum_as_default() -> None:
    assert ManureHandlerEnum.get_default_type() is ManureHandlerEnum.FLUSH_SYSTEM


def check_formatted_substrs_should_get_same_expected_enum(full_name: str,
                                                          idx: int,
                                                          expected_enum: DefaultEnum,
                                                          formatter: Callable[[str], str]):
    cls = expected_enum.__class__
    for j in range(idx, len(full_name)):
        assert cls.get_type(formatter(full_name[:j])) is expected_enum


def check_lower_case_substrs_should_get_same_expected_enum(full_name: str,
                                                           idx: int,
                                                           expected_enum: DefaultEnum):
    check_formatted_substrs_should_get_same_expected_enum(full_name,
                                                          idx,
                                                          expected_enum,
                                                          lambda s: s.lower())


def check_upper_case_substrs_should_get_same_expected_enum(full_name: str,
                                                           idx: int,
                                                           expected_enum: DefaultEnum):
    check_formatted_substrs_should_get_same_expected_enum(full_name,
                                                          idx,
                                                          expected_enum,
                                                          lambda s: s.upper())


def check_capitalize_case_substrs_should_get_same_expected_enum(full_name: str,
                                                                idx: int,
                                                                expected_enum: DefaultEnum):
    check_formatted_substrs_should_get_same_expected_enum(full_name,
                                                          idx,
                                                          expected_enum,
                                                          lambda s: s.capitalize())


def check_substrs_with_leading_and_trailing_spaces_should_get_same_expected_enum(full_name: str,
                                                                                 idx: int,
                                                                                 expected_enum: DefaultEnum):
    check_formatted_substrs_should_get_same_expected_enum(full_name,
                                                          idx,
                                                          expected_enum,
                                                          lambda s: ' ' + s + '  ')


def check_all_valid_substrs_should_get_same_expected_enum(full_name: str,
                                                          expected_enum: DefaultEnum,
                                                          idx: int = 3):
    params = {'full_name': full_name, 'expected_enum': expected_enum, 'idx': idx}
    check_lower_case_substrs_should_get_same_expected_enum(**params)
    check_upper_case_substrs_should_get_same_expected_enum(**params)
    check_capitalize_case_substrs_should_get_same_expected_enum(**params)
    check_substrs_with_leading_and_trailing_spaces_should_get_same_expected_enum(**params)


def test_get_enum_should_return_flush_system_when_correct_flush_system_substr_given() -> None:
    full_name = 'flush_system'
    for j in range(2, len(full_name)):
        assert ManureHandlerEnum.get_type(full_name[:j]) is ManureHandlerEnum.FLUSH_SYSTEM
        assert ManureHandlerEnum.get_type(' ' + full_name[:j] + '  ') is ManureHandlerEnum.FLUSH_SYSTEM
        assert ManureHandlerEnum.get_type(full_name[:j].upper()) is ManureHandlerEnum.FLUSH_SYSTEM
        assert ManureHandlerEnum.get_type(full_name[:j].capitalize()) is ManureHandlerEnum.FLUSH_SYSTEM


def test_get_enum_should_return_default_enum_when_incorrect_flush_system_substr_given() -> None:
    assert ManureHandlerEnum.get_type('_flush') is ManureHandlerEnum.DEFAULT
    assert ManureHandlerEnum.get_type('flu sh') is ManureHandlerEnum.DEFAULT


def test_get_enum_should_return_manual_scraping_when_correct_manual_scraping_substr_given() -> None:
    check_all_valid_substrs_should_get_same_expected_enum(full_name='manual_scraping',
                                                          expected_enum=ManureHandlerEnum.MANUAL_SCRAPING)

