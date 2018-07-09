################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: util.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
'''
################################################################################

import sys
import pulp
import time as timer
from pathlib import Path
import csv

#-------------------------------------------------------------------------------
# Function: get_base_dir
#-------------------------------------------------------------------------------
def get_base_dir():
    '''Gets the base directory as reference for all relative paths.

    Unfrozen appliaction - gets the project directory
    Frozen application - gets the executable directory

    Returns:
        Path: The reference directory for all paths in the program.
    '''

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

#-------------------------------------------------------------------------------
# Function: LP_solve
#-------------------------------------------------------------------------------
def LP_solve(LHS, RHS, objective, variables, operators,
             mode="min", name="LP", min_v=None, max_v=None):
    '''Solves the linear program using the PULP package solver.

    Solves the Linear Program and returns the results of the optimization.
    LHS, RHS, and operators will have length of #constraints in the LP.
    variables, objective, min_v, max_v, and each sub-list in LHS must have
    length of #variables in the LP.

    Args:
        LHS (float[[]]): Coefficients of the LHS of the constraints of the LP.
            Each sublist corresponds to a constraint equation.
        RHS (float[]): RHS values of each constraints of the LP.
        objective (float[]): Coefficients of the objective function.
        variables (str[]): List of variable names.
        operators (str[]): List of equation operator for each constraint.
            Must contain only: '>', '<', or '='
        mode (str, optional): Direction of the optimization og the LP.
            Could start with "min" or "max", case-insensitive.
            Defaults to "min" if not specified.
        name (str, optional): Name of the LP problem.
            Defaults to "LP" if not specified.
        min_v (float[], optional): Lower bound for each of the variables.
            Defaults to no bounds if not specified.
        max_v (float[], optional): Upper bound for each of the variables.
            Defaults to no bounds if not specified.

    Returns:
        dict: a dictionary with the names of variables as keys and the values of
            that variable at the optimal solution (if possible).
            {
             'status': "Infeasible" or "Optimal"
             'objective':  optimized value of the objective function
             (for all variables):
                'variable_name': variable value
            }
    '''

    start = timer.time()

    if mode.lower().startswith("min"):
        LP = pulp.LpProblem(name, pulp.LpMinimize)
    elif mode.lower().startswith("max"):
        LP = pulp.LpProblem(name, pulp.LpMaximize)
    else:
        print("ERROR")

    #if len(LHS) != len(RHS) or len(variables) != len(objective):
    #    print("ERROR")
    #    return None

    num_constraints = len(RHS)
    num_variables = len(variables)


    # If max and min values for variables were not given
    if min_v is None:
        min_v = [None]*num_variables
    if max_v is None:
        max_v = [None]*num_variables

    for constraint_eq in LHS:
        if len(constraint_eq) != len(variables):
            print("LP ERROR")

    #
    # LP Variables
    #
    LP_vars = []
    for v in range(num_variables):
        LP_vars.append( pulp.LpVariable(variables[v], min_v[v], max_v[v]) )
        #print("Appending {}, min:{}, max:{} to LP_vars".format(variables[v], min_v[v], max_v[v]))

    #
    # Objective function
    #
    LP += pulp.lpSum([ LP_vars[v] * objective[v] for v in range(num_variables) ])

    #
    # Constraints
    #
    for c in range(num_constraints):
        if operators[c] == '<=':
            LP += pulp.lpSum([ LHS[c][v] * LP_vars[v] for v in range(num_variables) ]) <= RHS[c]
        elif operators[c] == '>=':
            LP += pulp.lpSum([ LHS[c][v] * LP_vars[v] for v in range(num_variables) ]) >= RHS[c]
        else:
            LP += pulp.lpSum([ LHS[c][v] * LP_vars[v] for v in range(num_variables) ]) == RHS[c]

    LP.solve(pulp.solvers.GLPK(msg=0))

    results = { }
    for v in LP.variables():
        results[v.name] = v.varValue

    results['status'] = pulp.LpStatus[LP.status]
    results['objective'] = pulp.value(LP.objective)

    end = timer.time()

    #print("LP elapsed time: " + str(end-start))
    return results

#-------------------------------------------------------------------------------
# Function: LP_print
#-------------------------------------------------------------------------------
def LP_print(LHS, RHS, objective, variables, operators,
             mode="min", name="LP", min_v=None, max_v=None):
    '''Text representation of the Linear Programming problem.'''

    LHS = [ [round(x, 4) for x in row] for row in LHS]
    RHS = [ round(x, 4) for x in RHS]
    objective = [ round(x, 4) for x in objective]

    # Problem name
    LP_text = "\nLP Problem: {}\n".format(name)
    #LP_text += str(len(variables)) + " variables\n"
    #LP_text += str(len(LHS)) + " constraints\n"

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