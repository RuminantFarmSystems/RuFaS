################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: t_LP.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from RUFAS.util import LP_solve, LP_print


#-------------------------------------------------------------------------------
# Function: test_LP
#-------------------------------------------------------------------------------
def test_LP():
 
    LHS = [
            [13, 19, 54],
            [20, 29, 87]
          ]
    RHS = [ 2400, 2100 ]
    objective = [ 17.1667, 25.8667, 69.69 ]
    variables = [ 'x', 'y', 'z' ]
    min_v = [ 0,0,0]
    max_v = [ None, None, None ]
    operators = [ '<=', '>=' ]

    result = LP_solve(LHS, RHS, objective, variables, operators,
                      "maximize", "TEST", min_v, max_v)
    print(result)

    LP_print(LHS, RHS, objective, variables, operators,
                      "maximize", "TEST", min_v, max_v)

        
    