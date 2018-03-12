################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# t_LP.py - Test bench for LP module
#
# Authors: Kass Chupongstimun
#          Jit Patil JITs
#
################################################################################

#!/usr/bin/env python3

from RUFAS.util import LP_solve


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

#-------------------------------------------------------------------------------
#
# PROGRAM ENTRY POINT
#
#------------------------------------------------------------------------------- 
if __name__ == '__main__': test_LP()
        
    