################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: lactating_cow_ration_NLP.py
Description: Calculates the ration for lactating cows using a NLP solver.
Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""
################################################################################
import numpy as np
from scipy.optimize import minimize


#retreiving decision variables (feeds) from the feed library
#TODO when neew feed library is brought into master
#For now just initialze a dummy X variable
feeds = ['Corn_grain', 'Legume_hay', 'Cotton_Seed', 'Roasted_Soybean', 'Rye_Hay', 'Corn_Silage']
price = [25, 30, 10, 11, 67]


def objective(x):
    obj = 0
    return sum(np.multiply(x, price))
    #return x[0]*price[0] + x[1]*price[1] + x[2]*price[2] + x[3]*price[3] + x[4]*price[4]

def constraint1(x):
    denom = sum(x)
    if denom != 0:
        return (1/denom) * (x[0]+ x[1] + x[2]) - 10

def constraint2(x):
    return x[1] + x[4] - 20

n = len(price)
x0 = np.zeros(n)

## OPTIMIZE:
b= (1, 100)
bnds = (b, b, b, b, b)
con1 = {'type': 'ineq', 'fun': constraint1}
con2 = {'type': 'ineq', 'fun': constraint2}
cons = ([con1, con2])
solution = minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=cons)

x = solution.x

print(x)
print(objective(x))
