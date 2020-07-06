################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: db_view.py
Description: This file contains the RequestHandler class and when this file is
    run, the HTTP server is started locally at the specified port. The web page
    can be accessed by 'localhost:8000' (client) and this forms a connection to
    the server. This connection is kept alive until the program is killed.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################
import http.server
import socket
import socketserver
from urllib.parse import urlparse
import urllib.parse
import sqlite3
import json
import csv
import os

# port on machine through which connection to server hosted locally is made
PORT = 8000

# status codes
OK = 200
BAD_GATEWAY = 502
NOT_FOUND = 404


class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Based on which radio button is selected on the client side, a different type
    of request is sent to the server. The information that the server uses is
    the type of the request method (GET, POST, or DELETE - more specific
    information about each method type is found in the do_GET(), do_POST(),
    and do_DELETE() methods below) and the url to get information about the
    specific function that needs to be called as well as parameters provided
    by the user. The url is in the form '/path?query', where the query is in
    the form of
    'variable_name_1=value_1&variable_name_2=value_2&…&variable_name_n=value_n'.
    There are currently 5 supported paths:
        1. '/' : (GET) this signifies to the server that the client has
            requested the HTML page (i.e. the page has been refreshed).
            The server responds by sending index.html back to the client,
            which displays it on the page.
        2. '/getResults' : (GET) this signifies to the server that the client
            has requested to view the saved results that are currently in the
            'results' table of the outputs database. A JSON of this table, as
            well as the column names in the 'daily_results' and 'annual_results'
            tables are returned by the server. If the 'filter' parameter is
            specified, then the text in that parameter will be appended to the
            query.
        3. '/export' : (GET) this signifies to the server that the client has
            requested to export one or more entries in the 'results' table to
            csv files. The server responds by attempting to read the database
            and create the appropriate directories and csv files. The query for
            this request contains a list of the result IDs, a list of the
            columns from the daily results table to be exported, and a list of
            the columns from the annual results table to be exported.
        4. '/rename' : (POST) this signifies to the server that the client has
            requested to change one of the results by renaming it. The server
            responds by attempting to rename the result. The query for this
            request contains the result ID to rename as well as the new name.
        5. '/delete' : (DELETE) this signifies to the server that the client has
            requested to delete one of the results from the database. The server
            responds by deleting this result. The query for this request
            contains the result ID to delete.
    If the client sends a request with a different path than any of the ones
    listed above, the server responds with a 404 (NOT_FOUND) error.

    As described above, the client also sends the method type along with the url
    in the request to the server. The RequestHandler class inherits from
    BaseHTTPRequestHandler, which automatically calls the correct method
    (do_GET(), do_POST(), or do_DELETE()) based on the method type provided by
    the client. In each method, the url is parsed to get the path and different
    functions are called based on the path.

    For more information, see the Python documentation for http.server
    (https://docs.python.org/3/library/http.server.html) and urlib.parse
    (https://docs.python.org/3/library/urllib.parse.html).
    """

    def __init__(self, request, client_address, server):
        self.db_file = 'past_outputs.sqlite'
        super().__init__(request, client_address, server)

    def do_GET(self):
        """
        The GET HTTP method is used to request data from the server. This method
        is called when the javascript sends a request with method type "GET".
        """
        u = urlparse(self.path)
        if u.path == '/':
            file = None
            page = None

            try:
                file = open('index.html')
                page = file.read()

            except Exception as e:
                self.respond(BAD_GATEWAY, str(e))

            self.respond(OK, page)
            file.close()

        elif u.path == '/getResults':
            params = urllib.parse.parse_qs(u.query)
            if params != {}:
                query_appendix = params['filter'][0]
                status_code, returned_text = \
                    self.get_results_table(query_appendix=query_appendix)
            else:
                status_code, returned_text = self.get_results_table()

            self.respond(status_code, returned_text)

        elif u.path == '/export':
            params = urllib.parse.parse_qs(u.query)
            num_ids = [int(str_id) for str_id in params['id'][0].split(',')]
            daily_cols = params['daily'][0]
            annual_cols = params['annual'][0]
            status_code, returned_text = \
                self.multiple_to_csv(num_ids, daily_cols, annual_cols)
            self.respond(status_code, returned_text)

        else:
            self.respond(NOT_FOUND, str(u.path) + " is not a valid path.")

    def do_POST(self):
        """
        The POST HTTP method is used to send data to a server to change a
        resource. This method is called when the javascript sends a request
        with method type "POST".
        """
        u = urlparse(self.path)
        if u.path == '/rename':
            params = urllib.parse.parse_qs(u.query)
            rename_code, rename_returned_text = \
                self.re_title(int(params['id'][0]), params['new_title'][0])

            res_code, res_returned_text = self.get_results_table()

            # the whole request is successful if both operations above are
            status_code = OK if rename_code == res_code == OK else BAD_GATEWAY

            self.respond(status_code, rename_returned_text + res_returned_text)

        else:
            self.respond(NOT_FOUND, str(u.path) + " is not a valid path.")

    def do_DELETE(self):
        """
        The DELETE HTTP method deletes a resource. This method
        is called when the javascript sends a request with method type "DELETE".
        """
        u = urlparse(self.path)
        if u.path == '/delete':
            params = urllib.parse.parse_qs(u.query)
            del_code, del_returned_text = \
                self.delete_results_set(int(params['id'][0]))

            res_code, res_returned_text = self.get_results_table()

            # the whole request is successful if both operations above are
            status_code = OK if res_code == res_code == OK else BAD_GATEWAY

            self.respond(status_code, del_returned_text + res_returned_text)

        else:
            self.respond(NOT_FOUND, str(u.path) + " is not a valid path.")

    def respond(self, status_code, text):
        """
        Sends a response with the given @status_code and @text.

        Args:
            status_code: one of OK, BAD_GATEWAY, NOT_FOUND
            text: the text that will be displayed on the page
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(text.encode())

    def get_results_table(self, query_appendix=None):
        """
        Connects to the past outputs database and obtains all entries in the
        Results table for display on the web-page. Also returns all of the daily
        and annual column names.

        Args:
            query_appendix: (optional) a string with further filtering for the
                query

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = the JSON of the Results table in the outputs database
                    and the daily & annual column names or
                text = an error message if the operation was not successful
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            query = "SELECT result_id, title, created_at, version, user " \
                    "FROM results"
            if query_appendix is not None:
                query += " WHERE " + query_appendix

            c.execute(query)
            results_table = []
            row = c.fetchone()
            while row is not None:
                results_table.append(dict(row))
                row = c.fetchone()

            # get columns of the daily_results table
            daily_query = "PRAGMA table_info('daily_results');"
            c.execute(daily_query)
            row = c.fetchone()
            daily_columns = []
            while row is not None:
                daily_columns.append(dict(row)['name'])
                row = c.fetchone()

            # get columns of the annual_results table
            annual_query = "PRAGMA table_info('annual_results');"
            c.execute(annual_query)
            row = c.fetchone()
            annual_columns = []
            while row is not None:
                annual_columns.append(dict(row)['name'])
                row = c.fetchone()

            conn.close()

            return OK, json.dumps({
                'results_table': results_table,
                'daily_columns': daily_columns,
                'annual_columns': annual_columns
            })

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to obtain stored results:\n" \
                            + str(e)
            return BAD_GATEWAY, error_message

    def delete_results_set(self, id_to_delete):
        """
        Connects to the past outputs database and deletes the result with ID
        @id_to_delete.

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = empty string if the operation was successful or
                text = an error message if not
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute(
                "DELETE FROM results WHERE result_id=?", (id_to_delete,))
            c.execute("DELETE FROM daily_results WHERE result_id=?",
                      (id_to_delete,))
            c.execute("DELETE FROM annual_results WHERE result_id=?",
                      (id_to_delete,))

            conn.commit()
            conn.close()
            return OK, ""

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to and querying " + \
                            self.db_file + " to delete result " + \
                            str(id_to_delete) + ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def multiple_to_csv(self, result_ids, daily_cols, annual_cols):
        """
        Calls to_csv() for each of the ids in @result_ids.

        Args:
            result_ids: a list of result IDs for which a group of csv files
                will be created
            daily_cols: string of the columns from the daily_results table that
                will be in the resulting csv files
            annual_cols: string of the columns from the annual_results table
                that will be in the resulting csv files

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful for all IDs or
                status_code = BAD_GATEWAY if not and
                text = message for the success of creating the directory
                text = an error message if the operation was not successful
        """
        for result_id in result_ids:
            status, message = self.to_csv(result_id, daily_cols, annual_cols)
            if not status == OK:
                return status, message

        # if none of the above queries resulted in an error, return successful
        return OK, "Successfully created all directories"

    def to_csv(self, result_id, daily_cols, annual_cols):
        """
        Connects to the past outputs database and generates the csv files
        corresponding to the the ID @result_id. These files are currently placed
        in the output/db_output directory.

        Args:
            result_id: the result ID for which the daily results,
                annual results, variable descriptions, and input file will be
                created
            daily_cols: string of the columns from the daily_results table that
                will be in the resulting csv files
            annual_cols: string of the columns from the annual_results table
                that will be in the resulting csv files

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = message for the success of creating the directory
                text = an error message if the operation was not successful
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # get name from results table
            c.execute("SELECT title FROM results where result_id=?",
                      (result_id,))
            title_rows = c.fetchall()
            title = title_rows[0][0]

            result_id_param = (result_id,)

            # get data from daily results
            daily_query = "SELECT " + daily_cols + \
                          " FROM daily_results WHERE result_id=?"
            c.execute(daily_query, result_id_param)
            daily_vars = [description[0] for description in c.description]
            daily_rows = c.fetchall()

            # get data from annual results
            annual_query = "SELECT " + annual_cols + \
                           " FROM annual_results WHERE result_id=?"
            c.execute(annual_query, result_id_param)
            annual_vars = [description[0] for description in c.description]
            annual_rows = c.fetchall()

            # get data from variable descriptions table
            c.execute("SELECT * FROM variable_descriptions")
            descr_cols = [description[0] for description in c.description]
            descr_rows = c.fetchall()

            # get input json data
            c.execute("SELECT input_data FROM results WHERE result_id=?",
                      (result_id,))
            input_rows = c.fetchall()
            input_data = json.loads(input_rows[0][0])
            conn.close()

            # the following two try-except blocks make the directories that will
            # contain the csv files
            path = '../output/db_output'
            try:
                # create db_output folder
                os.mkdir(path)
            except FileExistsError:
                folder_path_message = "Directory " + path + " already exists."
            except OSError as e:
                folder_path_message = "Creation of the directory " + path + \
                               " failed with exception " + str(e)
            else:
                folder_path_message = "Successfully created the directory %s " \
                                      % path

            path += '/' + title
            try:
                #  folder for specific result set
                os.mkdir(path)
            except FileExistsError:
                path_message = "Warning: Directory " + path + \
                               " already exists - old data will be overwritten."

            except OSError as e:
                path_message = "Creation of the directory " + path + \
                               " failed with exception " + str(e)
            else:
                path_message = "Successfully created the directory %s " % path

            # create the two csv files using the title as name, the
            # variable description csv, and the input json file
            daily_file_name = path + '/' + title + "_daily.csv"
            annual_file_name = path + '/' + title + "_annual.csv"
            var_descr_file_name = path + '/' + 'variable_descriptions.csv'
            input_json_file_name = path + '/' + title + '_input.json'

            daily_file = open(daily_file_name, "w")
            annual_file = open(annual_file_name, "w")
            var_descr_file = open(var_descr_file_name, "w")
            input_json_file = open(input_json_file_name, "w")

            # open the csv writers
            csvWriterDaily = csv.writer(daily_file)
            csvWriterAnnual = csv.writer(annual_file)
            csvWriterDescr = csv.writer(var_descr_file)

            # write the headers/column names to the csv files
            csvWriterDaily.writerow(daily_vars)
            csvWriterAnnual.writerow(annual_vars)
            csvWriterDescr.writerow(descr_cols)

            # write the data to the csv files
            csvWriterDaily.writerows(daily_rows)
            csvWriterAnnual.writerows(annual_rows)
            csvWriterDescr.writerows(descr_rows)

            # write to input json file
            json.dump(input_data, input_json_file, indent=4)

            # close files
            daily_file.close()
            annual_file.close()
            var_descr_file.close()
            input_json_file.close()

            return OK, folder_path_message + " " + path_message

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to produce csv files from " \
                                           "result " + str(result_id) + \
                            ":\n" + str(e)
            return BAD_GATEWAY, error_message

    def re_title(self, id_to_re_title, new_title):
        """
        Connects to the past outputs database and renames the result with ID
        @id_to_retitle to have the name @new_title.

        Returns:
            (status_code, text) where
                status_code = OK if the operation was successful or
                status_code = BAD_GATEWAY if not and
                text = empty string if the operation was successful or
                text = an error message if not
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute("UPDATE results SET title = ? WHERE result_id=?",
                      (new_title, id_to_re_title))
            conn.commit()

            conn.close()

            return OK, ""

        except Exception as e:
            error_message = "The program has encountered the following " \
                            "exception while connecting to or querying " + \
                            self.db_file + " to rename result " + \
                            str(id_to_re_title) + ":\n" + str(e)
            return BAD_GATEWAY, error_message


# start the server locally at PORT
with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    print("serving at port", PORT)
    print("to open connection, type 'localhost:" + str(PORT) +
          "' into a web browser")
    print("to close connection/end this program, ctrl-c\n")
    httpd.serve_forever()
