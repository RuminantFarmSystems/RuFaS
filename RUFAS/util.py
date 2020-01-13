"""
RUFAS: Ruminant Farm Systems Model
File name: util.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
"""

import csv
import pulp
import sys
from pathlib import Path


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

    LP = None
    num_variables = len(var_names)

    # Ensure the LP is structured correctly
    if is_correct_structure(LHS, RHS, objective, var_names):
        LP = create_LP_problem(name, mode)
    else:
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


# Initializes the LP problem
def create_LP_problem(name, mode):
    if mode.lower().startswith("min"):
        LP = pulp.LpProblem(name, pulp.LpMinimize)
    elif mode.lower().startswith("max"):
        LP = pulp.LpProblem(name, pulp.LpMaximize)
    else:
        print("Incorrect LP mode. Exiting ...")
        exit()
    return LP


# Checks if there are equal number of constraints and RHS values
# Checks that objective and each constraint have all variables
def is_correct_structure(LHS, RHS, objective, var_names):
    if len(LHS) != len(RHS) or len(objective) != len(var_names):
        return False
    for constraint_eq in LHS:
        if len(constraint_eq) != len(var_names):
            return False
    return True


# Initializes the LP variables, and returns a list containing them.
# Each variable represents the quantity of a feed type. The variables
# are organized in order of the feed types alphabetically.
def generate_LP_vars(var_names, lower_bounds, upper_bounds):
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


# Adds the constraints to the LP problem. Each constraint represents the needed
# amount of a certain nutrient in the ration for the cow.
def add_LP_constraints(LHS, RHS, LP_Vars, operators, LP):
    num_vars = len(LP_Vars)
    for constraint_eq, constraint_value, operator in zip(LHS, RHS, operators):
        terms_in_equation = [constraint_eq[v] * LP_Vars[v] for v in range(num_vars)]
        if operator == '<=':
            LP += pulp.lpSum(terms_in_equation) <= constraint_value
        elif operator == '>=':
            LP += pulp.lpSum(terms_in_equation) >= constraint_value
        else:
            LP += pulp.lpSum(terms_in_equation) == constraint_value


# Finds the fastest solver available, and uses it to solve the LP.
def solve_with_fastest_solver(LP):
    try:
        LP.solve(pulp.solvers.GUROBI(msg=0))
    except pulp.PulpSolverError:
        try:
            LP.solve(pulp.solvers.GLPK(msg=0))
        except pulp.PulpSolverError:
            try:
                LP.solve(pulp.solvers.PULP_CBC_CMD(msg=0))
            except pulp.PulpSolverError:
                LP.solve(pulp.solvers.COIN_CMD(msg=0))


# Organizes the results in a dictionary such that the names of variables
# pair up with their optimal value (if possible), 'objective' with the optimal
# value of the objective, and the LP status with 'status'.
def organize_results(LP):
    results = {}
    for v in LP.variables():
        results[v.name] = v.varValue

    results['status'] = pulp.LpStatus[LP.status]
    results['objective'] = pulp.value(LP.objective)
    return results


def LP_print(LHS, RHS, objective, variables, operators,
             mode="min", name="LP", min_v=None, max_v=None):
    """Text representation of the Linear Programming problem."""

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

    # Contraint Equations
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


#
# Takes in the path to a csv file with the path starting after MASM/
# This function returns a list of tuples. Each tuple is the contents of
# a column in the csv. Thus, returnedList[0] would be the tuple of the contents
# in the first column in the csv. If an entry in the csv can be turned into a
# float, then it will be.
#
# This is useful for reading in time series data where each column corresponds
# to data of a specific attribute such as temperature.
#
def get_csv_columns(fileName):
    filePath = get_base_dir() / fileName
    with filePath.open("r") as input:
        readCSV = csv.reader(input, delimiter=',')
        allRows = list(readCSV)

        # Convert all numerical data to floats if possible
        allRows = [[try_to_float(value) for value in row] for row in allRows]

        allColumns = zip(*allRows)
        return list(allColumns)


def try_to_float(input):
    try:
        return float(input)
    except:
        return input


#
# Serves as a generic library. Each item in the library is represented as
# a dictionary with the traits of the item as keys, and the values of each
# trait as the values in the dictionary.
#
# This library is populated by csv files in which the first row specifies the
# traits of the type of item in the library. For example, a library of foods
# could have the traits of calories, grams fat, and grams protein. Each row
# corresponds to a specific item. Keeping with the food library example, each
# row would specify the specifics for a different food like hamburger, pizza,
# and apple. The only requirements are that each item in the library
# (defined in the csv) must have a unique "ID" trait and a unique "Name" trait.
#
class Library():
    def __init__(self, csv_file):
        self.lib_by_id = {}
        self.lib_by_name = {}
        info = get_csv_columns(csv_file)

        # The names of the traits are the first entry in each column
        traits = [col[0] for col in info]
        size = len(info[0])

        # Create and add each item to the library
        for i in range(1, size):
            item = {}
            values = [col[i] for col in info]

            # Populate the item's dictionary of traits
            for trait, value in zip(traits, values):
                item[trait] = value

            self.add_to_library(item)

    # Returns the dictionary of traits and corresponding values for the item
    # in the library with the given key. Items in the library can be retrieved
    # by either their Name or their ID.
    def checkout(self, key):
        if key in self.lib_by_name:
            return self.lib_by_name[key]
        elif key in self.lib_by_id:
            return self.lib_by_id[key]
        else:
            print("Unable to find '" + str(key) + "' in the library.")
            print("Please check that this is the correct Name or ID for the item, and that the "
                  "csv containing this item is the one specified in the input file.")
            print("Exiting...")
            exit()

    # In order for an item to be added to the library, the item must be a
    # dictionary containing an 'ID' and a 'Name' which can be used to uniquely
    # identify the item in the library.
    def add_to_library(self, item):
        if (type(item) is not dict) or ('ID' not in item) or ("Name" not in item):
            print("In order to add an item to the library, it must be a "
                  "dictionary containing an 'ID' and a 'Name'.")
            print("Exiting ...")
            exit()

        id = item['ID']
        name = item['Name']

        # Check for duplicate Names or IDs
        duplicate = ""
        if id in self.lib_by_id:
            duplicate = "ID of '%s'" % str(id)
        elif name in self.lib_by_name:
            duplicate = "Name of '%s'" % name

        if duplicate != "":
            print("The " + duplicate + " corresponds with multiple items in the specified csv.\n"
                                       "Please modify the csv so that the " + duplicate + " is unique to one item.")
            print("Exiting ...")
            exit()

        # Add the item to the library
        self.lib_by_id[id] = item
        self.lib_by_name[name] = item
