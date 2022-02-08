"""
RUFAS: Ruminant Farm Systems Model
File name: test_db_output.py
Description: Implements test cases
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
import os.path
import shutil

import pytest
from output_db.db_view import *
from output_db.db_view import write_csv
from output_db.db_view import create_dir
from output_db.db_view import create_all_dirs


def test_write_csv():
    """Unit test for function write_csv in file output_db/db_view.py"""
    # Test that the file can be successfully created.
    file_name = "../test.csv"
    column_headers = ["col1", "col2", "col3"]
    data_rows = [["1", "2", "3"], ["4", "5", "6"]]
    write_csv(file_name, column_headers, data_rows)

    with open(file_name) as csv_file:
        line_count = 0
        csv_reader = csv.reader(csv_file)

        for row in csv_reader:
            if line_count == 0:
                assert row == column_headers
            elif line_count == 1:
                assert row == data_rows[0]
            elif line_count == 2:
                assert row == data_rows[1]
            else:
                # Test should fail if this code is reached.
                assert False

            line_count += 1

    # (Test Cleanup) Remove created file.
    os.remove(file_name)


def test_create_dir():
    """Unit test for function create_dir in file output_db/db_view.py"""
    path = '../test_dir_creation'

    # Test that the directory can be successfully created.
    status, message = create_dir(path)
    assert status == OK
    assert message == "Successfully created the directory %s " % path

    # Test that the appropriate error message appears when the directory
    # already exists.
    status, message = create_dir(path)
    assert status == OK
    assert message == "Warning: Directory " + path + " already exists - old "\
                                                     "data will be overwritten."

    # Test that the appropriate error message appears when a different error
    # occurs.
    bad_path = '../test/dir/creation'
    status, message = create_dir(bad_path)
    assert status == BAD_GATEWAY
    assert message.startswith("Creation of the directory " + bad_path +
                              " failed with exception ")

    # (Test Cleanup) Remove created directory.
    try:
        os.rmdir(path)
    except OSError as e:
        print("Error: %s : %s" % (path, e.strerror))
        # Test should fail if this code is reached.
        assert False


def test_create_all_dirs():
    """Unit test for function create_all_dirs in file output_db/db_view.py"""
    # Test that the directory can be successfully created.
    title = "test_title"

    # A result_id that the database will never generate, thus ensuring that
    # this test does not overwrite any existing directories.
    result_id = "-1"

    status, message, path = create_all_dirs(title, result_id)
    assert status == OK
    assert message == "Successfully created directories"
    assert os.path.isdir(path)
    assert os.path.isdir(path + MANURE_PATH_SUFFIX)
    assert os.path.isdir(path + FARM_ES_PATH_SUFFIX)
    assert os.path.isdir(path + FARM_ES_PATH_SUFFIX +
                         FARM_ES_FEED_PRINT_PATH_SUFFIX)
    assert os.path.isdir(path + FARM_ES_PATH_SUFFIX +
                         FARM_ES_SUMMARY_PATH_SUFFIX)

    # Edge cases for other status/warning messages are tested in
    # test_create_dir().

    # (Test Cleanup) Remove created directories.
    try:
        shutil.rmtree(path)
    except OSError as e:
        print("Error: %s : %s" % (path, e.strerror))
        # Test should fail if this code is reached.
        assert False


def test_do_GET():
    """Unit test for function do_GET in file output_db/db_view.py"""
    # Hard to make a RequestHandler to test this.
    pass


def test_do_POST():
    """Unit test for function do_POST in file output_db/db_view.py"""
    # Hard to make a RequestHandler to test this.
    pass


def test_do_DELETE():
    """Unit test for function do_DELETE in file output_db/db_view.py"""
    # Hard to make a RequestHandler to test this.
    pass


def test_respond():
    """Unit test for function respond in file output_db/db_view.py"""
    # Hard to make a RequestHandler to test this.
    pass


def test_get_results_table():
    """Unit test for function get_results_table in file output_db/db_view.py"""
    request_handler = RequestHandler(b'\x04\x00', ("", PORT), PORT)
    print(request_handler.get_results_table())
    pass


def test_multiple_to_csv():
    """Unit test for function multiple_to_csv in file output_db/db_view.py"""
    pass


def test_to_csv():
    """Unit test for function to_csv in file output_db/db_view.py"""
    pass


def test_write_farm_es_outputs():
    """Unit test for function write_farm_es_outputs in file
    output_db/db_view.py"""
    pass


def test_write_farm_summary_outputs():
    """Unit test for function write_farm_summary_outputs in file
    output_db/db_view.py"""
    pass


def test_write_cow_print():
    """Unit test for function write_cow_print in file output_db/db_view.py"""
    pass


def test_write_feed_print():
    """Unit test for function write_feed_print in file output_db/db_view.py"""
    pass


def test_write_manure_print():
    """Unit test for function write_manure_print in file output_db/db_view.py"""
    pass


def test_write_energy_print():
    """Unit test for function write_energy_print in file output_db/db_view.py"""
    pass


def test_read_table():
    """Unit test for function read_table in file output_db/db_view.py"""
    pass


def test_delete_results_set():
    """Unit test for function delete_results_set in file output_db/db_view.py"""
    pass


def test_get_columns():
    """Unit test for function get_columns in file output_db/db_view.py"""
    pass


def test_perform_join():
    """Unit test for function perform_join in file output_db/db_view.py"""
    pass


def test_find_desired_cols():
    """Unit test for function find_desired_cols in file output_db/db_view.py"""
    pass


def test_re_title():
    """Unit test for function re_title in file output_db/db_view.py"""
    pass
