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
# Parameters: variables - { name: "variable_name", min: int, max: int }
#             objective - { }
#             LHS - [ { } ]
#             RHS - [ ]
# Returns:
#-------------------------------------------------------------------------------
def LP_solve(LHS, RHS, objective, variables, operators,
             mode="minimize", name="LP", min_v=None,max_v=None):

    if mode == 'minimize':
        LP = pulp.LpProblem(name, pulp.LpMinimize)
    elif mode == 'maximize':
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
        print("Appending {}, min:{}, max:{} to LP_vars".format(variables[v], min_v[v], max_v[v]))

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

    results = {}
    for v in LP.variables():
        results[v.name] = v.varValue
    results['status'] = pulp.LpStatus[LP.status]
    results['sol'] = pulp.value(LP.objective)

    return results





