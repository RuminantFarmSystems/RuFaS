"""
RUFAS: Ruminant Farm Systems Model
File name: test_db_output.py
Description: Implements test cases
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
import builtins
import os.path
import threading
import time
from urllib.request import urlopen
import socket
import socketserver

import pytest
from mock.mock import MagicMock
from output_db.db_view import RequestHandler, DB_OUTPUT_PATH, PORT
from output_db.db_view import write_csv
from output_db.db_view import create_all_dirs


@pytest.fixture(scope="session", autouse=True)
def start_server():
    server = socketserver.TCPServer(("", PORT), RequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server_thread.start()
    # Wait a bit for the server to come up
    time.sleep(1)
    yield server
    server.shutdown()


def test_write_csv(mocker):
    """Unit test for function write_csv in file output_db/db_view.py"""
    builtins.open = MagicMock()
    open_spy = mocker.spy(builtins, 'open')
    write_csv('', [], [])
    assert open_spy.call_count == 1


def test_create_all_dirs(mocker):
    """Unit test for function create_all_dirs in file output_db/db_view.py"""
    title = "test_title"
    result_id = "-1"

    os.mkdir = MagicMock()
    mkdir_spy = mocker.spy(os, 'mkdir')

    path = create_all_dirs(title, result_id)

    assert path == DB_OUTPUT_PATH + str(result_id) + '_' + title + '/'
    assert mkdir_spy.call_count == 6


def test_do_GET():
    """Unit test for function do_GET in file output_db/db_view.py"""
    print(urlopen("http://localhost:" + str(PORT) + "/").read())
    assert False


def test_do_POST():
    """Unit test for function do_POST in file output_db/db_view.py"""
    pass


def test_do_DELETE():
    """Unit test for function do_DELETE in file output_db/db_view.py"""
    pass


def test_respond():
    """Unit test for function respond in file output_db/db_view.py"""
    pass


def test_get_results_table():
    """Unit test for function get_results_table in file output_db/db_view.py"""
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
