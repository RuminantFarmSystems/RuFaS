"""
RUFAS: Ruminant Farm Systems Model
File name: util.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
"""
import json
import pulp
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
            conn = sqlite3.connect(Path(self.db_file))
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


def LP_solve(LHS, RHS, objective, var_names, operators,
             mode="min", name="LP", lower_var_bounds=None, upper_var_bounds=None):
    """Solves the linear program using the PULP package solver.

    Solves the Linear Program and returns the results of the optimization.
    LHS, RHS, and operators will have length of #constraints in the LP.
    variables, objective, lower_var_bounds, upper_var_bounds, and each sub-list in LHS must have
    length of #variables in the LP.

    Args:
        LHS (float[[]]): Coefficients of the LHS of the constraints of the LP.
            Each sublist corresponds to a constraint equation.
        RHS (float[]): RHS values of each constraints of the LP.
        objective (float[]): Coefficients of the objective function.
        var_names (str[]): List of variable names.
        operators (str[]): List of equation operator for each constraint.
            Must contain only: '>', '<', or '='
        mode (str, optional): Direction of the optimization og the LP.
            Could start with "min" or "max", case-insensitive.
            Defaults to "min" if not specified.
        name (str, optional): Name of the LP problem.
            Defaults to "LP" if not specified.
        lower_var_bounds (float[], optional): Lower bound for each of the variables.
            Defaults to no bounds if not specified.
        upper_var_bounds (float[], optional): Upper bound for each of the variables.
            Defaults to no bounds if not specified.

    Returns:
        dict: a dictionary with the names of variables as keys and the values of
            that variable at the optimal solution (if possible).
            {
            'status': "Infeasible" or "Optimal",
            'objective':  optimized value of the objective function,
            'variable1_name': variable value,
            'variable2_name': variable value,
            .
            .
            .
            
            'variableN_name': variable value
            }
    """
    num_variables = len(var_names)

    # Ensure the LP is structured correctly
    if is_correct_structure(LHS, RHS, objective, var_names):
        LP = create_LP_problem(name, mode)
    else:
        LP = None
        print("Incorrect LP structure. Exiting ...")
        exit()

    # Create LP Variables
    LP_vars = generate_LP_vars(var_names, lower_var_bounds, upper_var_bounds)

    # Add objective function
    LP += pulp.lpSum([LP_vars[v] * objective[v] for v in range(num_variables)])

    # Add constraints
    add_LP_constraints(LHS, RHS, LP_vars, operators, LP)

    # Solve
    # Uses the fastest solver available
    solve_with_fastest_solver(LP)

    # Get organized results
    results = organize_results(LP)

    return results


def create_LP_problem(name, mode):
    """
    Description:
        Initializes the LP problem
    """

    LP = None
    if mode.lower().startswith("min"):
        LP = pulp.LpProblem(name, pulp.LpMinimize)
    elif mode.lower().startswith("max"):
        LP = pulp.LpProblem(name, pulp.LpMaximize)
    else:
        print("Incorrect LP mode. Exiting ...")
        exit()
    return LP


def is_correct_structure(LHS, RHS, objective, var_names):
    """
    Description:
        Checks if there are equal number of constraints and RHS values
        Checks that objective and each constraint have all variables
    """

    if len(LHS) != len(RHS) or len(objective) != len(var_names):
        return False
    for constraint_eq in LHS:
        if len(constraint_eq) != len(var_names):
            return False
    return True


def generate_LP_vars(var_names, lower_bounds, upper_bounds):
    """
    Description:
        Initializes the LP variables, and returns a list containing them.
        Each variable represents the quantity of a feed type. The variables
        are organized in order of the feed types alphabetically.
    """

    num_vars = len(var_names)

    # If max and min values for variables were not given
    if lower_bounds is None:
        lower_bounds = [None] * num_vars
    if upper_bounds is None:
        upper_bounds = [None] * num_vars

    #
    # LP Variables
    #
    LP_vars = []
    for var_info in zip(var_names, lower_bounds, upper_bounds):
        new_variable = pulp.LpVariable(*var_info)
        LP_vars.append(new_variable)
    return LP_vars


def add_LP_constraints(LHS, RHS, LP_Vars, operators, LP):
    """
    Description:
        Adds the constraints to the LP problem. Each constraint represents the needed
        amount of a certain nutrient in the ration for the cow.
    """

    num_vars = len(LP_Vars)
    for constraint_eq, constraint_value, operator in zip(LHS, RHS, operators):
        terms_in_equation = [constraint_eq[v] * LP_Vars[v] for v in range(num_vars)]
        if operator == '<=':
            LP += pulp.lpSum(terms_in_equation) <= constraint_value
        elif operator == '>=':
            LP += pulp.lpSum(terms_in_equation) >= constraint_value
        else:
            LP += pulp.lpSum(terms_in_equation) == constraint_value


def solve_with_fastest_solver(LP):
    """Finds the fastest solver available, and uses it to solve the LP."""

    try:
        LP.solve(pulp.GUROBI_CMD(msg=0))
    except pulp.PulpSolverError:
        try:
            LP.solve(pulp.GLPK(msg=0))
        except pulp.PulpSolverError:
            try:
                LP.solve(pulp.PULP_CBC_CMD(msg=0))
            except pulp.PulpSolverError:
                LP.solve(pulp.COIN_CMD(msg=0))


def organize_results(LP):
    """
    Description:
        Organizes the results in a dictionary such that the names of variables
        pair up with their optimal value (if possible), 'objective' with the optimal
        value of the objective, and the LP status with 'status'.
    """

    results = {}
    for v in LP.variables():
        results[v.name] = v.varValue

    results['status'] = pulp.LpStatus[LP.status]
    results['objective'] = pulp.value(LP.objective)
    return results


def LP_print(LHS, RHS, objective, variables, operators,
             mode="min", name="LP", min_v=None, max_v=None):
    """
    Description:
        Text representation of the Linear Programming problem.
    """

    LHS = [[round(x, 4) for x in row] for row in LHS]
    RHS = [round(x, 4) for x in RHS]
    objective = [round(x, 4) for x in objective]

    # Problem name
    LP_text = "\nLP Problem: {}\n".format(name)
    # LP_text += str(len(variables)) + " variables\n"
    # LP_text += str(len(LHS)) + " constraints\n"

    # Direction of Optimization
    if mode.lower().startswith("min"):
        mode_text = "Minimize"
    elif mode.lower().startswith("max"):
        mode_text = "Minimize"
    else:
        mode_text = "Bad Mode Input"
    LP_text += mode_text + ":\n"

    # Objective Function
    objective_text = "\t"
    for v in range(len(variables)):
        objective_text += "{}*{} ".format(objective[v], variables[v])
        if not v == len(variables) - 1:
            objective_text += "+ "
    LP_text += objective_text + '\n'

    # Constraint Equations
    constraint_text = "Subject to:\n"
    for c in range(len(LHS)):
        constraint_text += '\t'
        for v in range(len(variables)):
            constraint_text += "{}*{} ".format(LHS[c][v], variables[v])
            if not v == len(variables) - 1:
                constraint_text += "+ "
        constraint_text += "{} {}\n".format(operators[c], RHS[c])
    LP_text += constraint_text

    # Variable Bounds
    LP_text += "With:\n"
    for v in range(len(variables)):
        LP_text += "\t{} ≤ {} ≤ {}\n".format(min_v[v], variables[v], max_v[v])

    # Print and return
    print(LP_text)
    print("* All floats rounded to 4 decimal places")
    return LP_text
