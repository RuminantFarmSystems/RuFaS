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
# Returns:
#-------------------------------------------------------------------------------
def LP_SOLVE(LHS, RHS, objective, variables, operators, mode, name):

    if mode == 'minimize':
        LP = pulp.LpProblem(name, LpMinimize)
    elif mode == 'maximize':
        LP = pulp.LpProblem(name, LpMaximize)
    else:
        # ERROR!
        pass

    if len(LHS) != len(RHS):
        # ERROR!
        pass
    
    num_constraints = len(RHS)

    for constraint_eq in LHS:
        if len(constraint_eq) != len(variables):
            # ERROR!
            pass

    num_variables = len(variables)

    #
    # LP Variables
    #
    LP_vars = {}
    for v in variables:
        LP_vars.update({ v['name']: LpVariable(v['name'], v['min'], v['max']) })

    #
    # Objective function
    #
    for r in range(len(RHS)):
        LP += LpSum([ LP_vars[c] * objective[c] for c in range(len(LP_vars)) ])








