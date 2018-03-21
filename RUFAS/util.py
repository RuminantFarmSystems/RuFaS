################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# util.py - Contains utility functions
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import sys
import pulp
from pathlib import Path

#-------------------------------------------------------------------------------
# Function: get_base_dir
#           Gets the base directory as reference for all relative paths
#
#           Unfrozen appliaction - gets the project directory
#           Frozen application - gets the executable directory
#
# Returns: The reference directory for all paths in the program
#-------------------------------------------------------------------------------
def get_base_dir():
    
    # Frozen
    if getattr(sys, 'frozen', False):
        
        # Get the executable file path
        # Resolve to absolute path
        # Take the parent base_dir/RUFAS_exe
        #                 parent = base_dir/
        return Path(sys.executable).resolve().parent
    
    # Unfrozen
    else:
        
        # Get path of current file (util.py)
        # Resolve to absolute path
        # Get the 2nd parent  base_dir/RUFAS/util.py
        #                     parent[0] = base_dir/RUFAS
        #                     parent[1] = base_dir/
        return Path(__file__).resolve().parents[1]

#-------------------------------------------------------------------------------
# Function: LP_solve
#
# Parameters: LHS: float[[]] - Each sublist contains coefficients for each
#                              constraint equation
#             RHS: float[] - List of right hand side values of each constraint
#             objective: float[] - List of coefficients in objective function
#             variables: string[] - List of variable names 
#             operators: string[] - List of operators for each constraint
#             mode: string - direction of optimization for LP
#                            could start with "min" or "max", case-insensitive
#             name: string - name for the LP problem
#             min_v: float[] - minimum bounds for each variable
#                              defaults to no bounds if not specified
#             max_v: float[] - maximum bounds for each variable
#                              defaults to no bounds if not specified
#             LHS, RHS, and operators will have length of #constraints
#             variables, objective, min_v, max_v, and each sub-list in LHS
#             must have length of #variables
#
# Returns: a dictionary with the names of variables as keys and the values of
#          that variable at the optimal solution (if possible)
#          the dictionary contains the key: "status" which would show whether
#          the solution is "optimal" or "infeasible"
#          the dictionay also contains the key: "objective" which has the
#          value of the optimized objective equation
#-------------------------------------------------------------------------------
def LP_solve(LHS, RHS, objective, variables, operators,
             mode="min", name="LP", min_v=None, max_v=None):

    if mode.lower().startswith("min"):
        LP = pulp.LpProblem(name, pulp.LpMinimize)
    elif mode.lower().startswith("max"):
        LP = pulp.LpProblem(name, pulp.LpMaximize)
    else:
        print("ERROR")

    if len(LHS) != len(RHS):
        print("ERROR")

    if len(variables) != len(objective):
        print("ERROR")

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

    #pulp.LpSolverDefault.msg = 1
    LP.solve()

    results = { }
    for v in LP.variables():
        results[v.name] = v.varValue

    results['status'] = pulp.LpStatus[LP.status]
    results['objective'] = pulp.value(LP.objective)

    return results

#-------------------------------------------------------------------------------
# Function: LP_print
# Returns: Text representation of the Linear Programming problem
#-------------------------------------------------------------------------------
def LP_print(LHS, RHS, objective, variables, operators,
             mode="min", name="LP", min_v=None, max_v=None):

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



