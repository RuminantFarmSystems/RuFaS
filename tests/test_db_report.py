"""
RUFAS: Ruminant Farm Systems Model
File name: test_db_report.py
Description: Implements test cases
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
import os
import sqlite3

import pytest
from pathlib import Path
from mock.mock import MagicMock, PropertyMock

from RUFAS.output_handler.reports import BaseReport
from RUFAS.output_handler.reports.db_report import unpack_input_json
from RUFAS.output_handler.reports.db_report import DBReport


class MyCursor:
    def execute(self, arg1, arg2):
        assert isinstance(arg1, str)
        assert isinstance(arg2, tuple)

    def executemany(self, arg1, arg2):
        assert isinstance(arg1, str)
        assert isinstance(arg2, list)


@pytest.fixture
def output_json_data():
    return {
        "produce_csv": True,
        "produce_graphics": False,
        "report_name": "rufas_test",
        "version": "pre_v1",
        "user": "default"
    }


@pytest.fixture
def db_report_instance(output_json_data):
    # Temporarily change the current working directory to the MASM folder so
    # that the constructor can find the files using the Paths it specifies.
    current_working_directory = os.getcwd()
    os.chdir(current_working_directory[:current_working_directory.rindex("/")])

    db = DBReport(output_json_data, Path("input/animal_management.json"))

    # Change working directory back to original.
    os.chdir(current_working_directory)

    return db


@pytest.fixture
def base_report_instance(output_json_data):
    return BaseReport(output_json_data)


@pytest.fixture
def cursor_instance():
    return MyCursor()


def test_unpack_input_json():
    """Unit test for function unpack_input_json in file
    RUFAS/output_handler/reports/db_report.py"""
    # Ensure that the execution of this function does not cause an exception,
    # which would likely be caused because the function has not been updated
    # to reflect any changes in the input JSON structure.

    # Temporarily change the current working directory to the MASM folder so
    # that the function can find the files using the Paths it specifies.
    current_working_directory = os.getcwd()
    os.chdir(current_working_directory[:current_working_directory.rindex("/")])

    try:
        _ = unpack_input_json(Path("input/animal_management.json"))
    except Exception as e:
        print("Error in unpack_input_json - likely an issue because the "
              "overall structure of the input JSON files has changed and "
              "this method was not updated:", e)
        assert False

    # Change working directory back to original.
    os.chdir(current_working_directory)


def test_initialize(mocker, db_report_instance, base_report_instance):
    """Unit test for function initialize in file
    RUFAS/output_handler/reports/db_report.py"""
    # This function explicitly does nothing, so this ensures that the
    # overridden superclass method is not called.
    spy = mocker.spy(base_report_instance, 'initialize')
    db_report_instance.initialize()
    assert spy.call_count == 0


def test_write_headers(mocker,  db_report_instance, base_report_instance):
    """Unit test for function write_headers in file
    RUFAS/output_handler/reports/db_report.py"""
    # This function explicitly does nothing, so this ensures that the
    # overridden superclass method is not called.
    spy = mocker.spy(base_report_instance, 'write_headers')
    db_report_instance.write_headers(None, None)
    assert spy.call_count == 0


def test_produce_report_graphics(mocker,  db_report_instance,
                                 base_report_instance):
    """Unit test for function initialize in file
    RUFAS/output_handler/reports/db_report.py"""
    # This function explicitly does nothing, so this ensures that the
    # overridden superclass method is not called.
    spy = mocker.spy(base_report_instance, 'produce_report_graphics')
    db_report_instance.produce_report_graphics()
    assert spy.call_count == 0


def test_finalize(db_report_instance):
    """Unit test for function finalize in file
    RUFAS/output_handler/reports/db_report.py"""
    # This test mocks the Connection attribute of DBReport to ensure that
    # calling finalize() calls commit() once.
    db_report_instance.conn = MagicMock()
    db_report_instance.finalize(None, None, None)
    db_report_instance.conn.commit.assert_called_once()


def test_get_cursor(db_report_instance):
    """Unit test for function get_cursor in file
    RUFAS/output_handler/reports/db_report.py"""
    db_report_instance.conn = MagicMock()
    _ = db_report_instance.get_cursor()
    db_report_instance.conn.cursor.assert_called_once()


def test_store_results_setup(mocker, db_report_instance, cursor_instance):
    """Unit test for function store_results_setup in file
    RUFAS/output_handler/reports/db_report.py"""
    db_report_instance.get_cursor = MagicMock(return_value=cursor_instance)
    execute_spy = mocker.spy(cursor_instance, 'execute')

    db_report_instance.store_results_setup({})

    # Ensures that execute() was called exactly as many times as it appears
    # in store_results_setup().
    assert execute_spy.call_count == 1


def test_write_annual_report(mocker, db_report_instance,
                             base_report_instance, cursor_instance):
    """Unit test for function write_annual_report in file
    RUFAS/output_handler/reports/db_report.py"""
    base_class_spy = mocker.spy(base_report_instance, 'write_annual_report')

    db_report_instance.get_cursor = MagicMock(return_value=cursor_instance)
    execute_spy = mocker.spy(cursor_instance, 'execute')
    execute_many_spy = mocker.spy(cursor_instance, 'executemany')

    db_report_instance.write_annual_report()

    # Ensures that the overridden superclass method was not called.
    assert base_class_spy.call_count == 0

    # Ensures that execute() and executemany() were called exactly as many
    # times as they appear in write_annual_report().
    assert execute_spy.call_count == 4
    assert execute_many_spy.call_count == 5


def test_daily_update():
    """Unit test for function daily_update in file
    RUFAS/output_handler/reports/db_report.py"""
    # See note for test_annual_update() below. This has similar logic since
    # any changes to the OutputHandler will also affect how this method works.
    # TODO Once we re-vamp the OutputHandler structure, this test should be
    #  modified accordingly.
    pass


def test_annual_update():
    """Unit test for function annual_update in file
    RUFAS/output_handler/reports/db_report.py"""
    #   My initial thought on how to test this function was to check that for
    # each of the dictionaries that this function updates, we compare the
    # lengths of the value lists within them before and after the function
    # call. However, this strategy has 2 issues: (1) initializing the
    # bare-bones State, Weather, and Time instances to call the function does
    # not provide a meaningful enough representation for this to make sense
    # and (2) not all of the values updated are lists (some are annual float
    # values) and this combined with (1) also means that nothing would really be
    # different between the before and after values.
    #   My next thought was to test that the function updated the dictionaries
    # of the DBReport class by asserting that they are different from what
    # they were prior to the function call (by "different" I mean checking
    # !=). However, this runs into a similar issue as (1) above - since there
    # is no simulation happening, there are a lot of 0 values. 0 is the
    # default initial value for many of the dictionaries so there wouldn't be
    # any change even after the function is called.
    #   Thus, I am not sure how to test this function in a meaningful way. I do
    # know that we are re-vamping the OutputHandler structure, and with that,
    # how we are testing it, so maybe writing a test for this function (since
    # it is overridden from the base class anyway, so it should follow a
    # similar testing pattern to the other Report classes) isn't worth it at
    # this stage so I am leaving this to-do below.
    # TODO Once we re-vamp the OutputHandler structure, this test should be
    #  modified accordingly.
    pass


def test_annual_flush(db_report_instance):
    """Unit test for function annual_flush in file
    RUFAS/output_handler/reports/db_report.py"""
    db_report_instance.annual_flush()

    for variable in db_report_instance.daily_manure_variables:
        assert db_report_instance.daily_manure_variables[variable][2] == []

    for variable in db_report_instance.purchased_feed_info_variables:
        assert db_report_instance.purchased_feed_info_variables[variable][2] \
               == []

    for variable in db_report_instance.grown_feed_info_variables:
        assert db_report_instance.grown_feed_info_variables[variable][2] == []

    for variable in db_report_instance.cow_print_variables:
        assert db_report_instance.cow_print_variables[variable][2] == 0

    for variable in db_report_instance.feed_print_variables:
        assert db_report_instance.feed_print_variables[variable][2] == 0

    for variable in db_report_instance.energy_print_variables:
        assert db_report_instance.energy_print_variables[variable][2] == 0

    for variable in db_report_instance.annual_manure_variables:
        assert db_report_instance.annual_manure_variables[variable][2] == []
