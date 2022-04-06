"""
RUFAS: Ruminant Farm Systems Model
File name: util.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
"""
import json
import sys
from pathlib import Path
import sqlite3

from RUFAS import errors


class DatabaseReader:
    """
    Description: Stores the information from the database source specified.
    """
    def __init__(self, database_file: str):
        self.db_file = database_file

    def query(self, table, distinct=False, cols=None, identifier=None,
              desired_rows=None, compare_val=None, low_col=None, high_col=None):
        """
        Constructs and executes a query on @table of the following form
        (all clauses in square brackets are optional, depending on parameters
        given):
        SELECT [DISTINCT] * FROM table [WHERE low_col <= compare_val AND
            high_col >= compare_val] [AND/WHERE identifier IN (desired_rows)]
        or, if columns are specified using @cols:
        SELECT [DISTINCT] cols FROM table [WHERE low_col <= compare_val AND
            high_col >= compare_val] [AND/WHERE identifier IN (desired_rows)]
        The result of this query is returned.
        If an exception is raised when connecting/querying the database, this
        method prints the error message and quits the program.

        Args:
            table: string - the name of the table to be queried
            distinct: (optional) boolean - if true, the query result contains no
                duplicates
            cols: (optional) list of strings - each string in this list is a
                column name that will be returned. If this argument is not
                specified, all columns from the specified table will be returned
            identifier: (optional) string - the column name which will be
                compared to the desired_rows values. If this argument is
                specified, desired_rows must also be specified, otherwise both
                will be treated as None.
            desired_rows: (optional) tuple of strings - the values of the
                identifier column which are being queried. If this argument is
                specified, identifier must also be specified, otherwise both
                will be treated as None.
            compare_val: (optional) string - the value which should fall in the
                range of [low_col, high_col]. If this argument is specified,
                low_col and high_col must also be specified, otherwise these
                three arguments will be treated as None.
            low_col: (optional) string - the column name of the lower bound of
                the desired range. If this argument is specified, compare_val
                and high_col must also be specified, otherwise these three
                arguments will be treated as None.
            high_col: (optional) string - the column name of the upper bound of
                the desired range. If this argument is specified, compare_val
                and low_col must also be specified, otherwise these three
                arguments will be treated as None.

        Returns:
            the result of the query formed as a list of dictionaries where each
            dictionary represents a row returned (the keys in each dictionary
            are the column names and they are mapped to the values in the
            database)
        """

        try:
            # Forms a connection to the database
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            # the query starts with SELECT
            query = "SELECT "

            # if distinct is true, append the DISTINCT keyword
            if distinct:
                query += "DISTINCT "

            # if cols is not specified, all columns are returned, otherwise
            # the specified column names are joined by commas and inserted
            # into the query
            if cols is None:
                query += "* FROM " + table
            else:
                query += ",".join(cols) + " FROM " + table

            # appends the range part of the query if all 3 components are
            # specified
            append_range = compare_val is not None and \
                low_col is not None and \
                high_col is not None
            if append_range:
                query += " WHERE " + low_col + " <= " + compare_val + \
                         " AND " + high_col + " >= " + compare_val

            if desired_rows is None or identifier is None:
                # Since identifier and desired_rows are None, the following
                # command will execute the query as formulated above on all the
                # rows of the database.
                c.execute(query)

            else:
                # if the range has already been appending, the identifier part
                # of the query is another AND clause, otherwise it is the
                # beginning of the WHERE clause
                if append_range:
                    query += " AND "
                else:
                    query += " WHERE "
                # filters which rows should be returned from the query
                query += identifier + " IN " + \
                    "({})".format(','.join(['?'] * len(desired_rows)))
                # Here, desired_rows is a parameter to the query as the list of
                # rows for which information is wanted. This list will be
                # formatted as specified in the query above (i.e. all elements
                # are separated by a comma and the list is surrounded by
                # parentheses).
                c.execute(query, desired_rows)

            # construct a list of dictionaries, where each dictionary in
            # the list corresponds to a row in the database table storing
            # the information for the row
            result = []
            row = c.fetchone()
            while row is not None:
                result.append(dict(row))
                row = c.fetchone()

            conn.close()

            return result

        except Exception as e:
            print("DatabaseReader.query(): The program encountered the "
                  "following exception while connecting to and querying table",
                  table, "from database", self.db_file, ":", e, "\nExiting.")
            exit(1)


def get_base_dir():
    """Gets the base directory as reference for all relative paths.

    Unfrozen application - gets the project directory
    Frozen application - gets the executable directory

    Returns:
        Path: The reference directory for all paths in the program.
    """

    # Frozen
    if getattr(sys, 'frozen', False):
        #
        # Get the executable file path
        # Resolve to absolute path
        # Take the parent base_dir/RUFAS_exe
        #                 parent = base_dir/

        return Path(sys.executable).resolve().parent

    # Unfrozen
    else:
        #
        # Get path of current file (util.py)
        # Resolve to absolute path
        # Get the 2nd parent  base_dir/RUFAS/util.py
        #                     parent[0] = base_dir/RUFAS
        #                     parent[1] = base_dir/
        return Path(__file__).resolve().parents[1]


def read_json_file(file_path: Path):
    """
    Description:
        Reads and interprets the JSON file at the given path. Compiles the
        information into dictionaries used to instantiate simulation objects.

    Args:
        file_path (Path): Path to the input json file

    Raises:
        InvalidJSONFileError: If the json file at the given path does not
            conform with the format required

    Returns:
        data: the data read from the json file
    """

    try:
        if file_path.suffix == '.json':
            if not file_path.is_file():
                raise errors.UserInput((str(file_path), 'does not exist'))
        else:
            raise errors.UserInput((str(file_path), 'is not a JSON file'))

        with file_path.open('r') as f:
            data = json.load(f)

        return data

    except errors.UserInput as e:
        print(e.msg)
