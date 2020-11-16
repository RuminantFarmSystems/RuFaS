"""
RUFAS: Ruminant Farm Systems Model
File name: pyomo_solver.py

Description: This file formats the non-linear program ration model into a
    pyomo structured model. Various different solvers can be used in this
    format.
Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""
from pyomo.environ import *

model = ConcreteModel()
model.energys = Set(doc = 'ENERGY', initialize = ['mact', 'lact', 'growth'])




import pyomo.environ as pyo

model = pyo.ConcreteModel()
model.A = Set(doc='FEEDS', initialize = ['feed_1', 'feed_2', 'feed_3'])
model.E = Set(doc = 'ENERGY', initialize = ['mact', 'lact', 'growth'])
model.C = model.A * model.E

v={}
v['feed_1','mact'] = 9
v['feed_2', 'lact'] = 16
v['feed_3','growth'] = 25
model.S1 = Param(model.A, model.E, initialize=v, default=0)
#creating a parameter across the set
model.price = Param(model.A, initialize ={'feed_1': 1, 'feed_2': 2, 'feed_3': 3})

for i in model.A:
    for j in model.E:
        print(i)


'''
model.A = RangeSet(1,3)
model.B = Set()
model.P = Param(model.A, model.B)

v={}
v[1,3] = 9
v[2,2] = 16
v[3,3] = 25
model.S1 = Param(model.A, model.A, initialize=v, default=0)

def s_init(model, i, j):
    if i == j:
        return i*i
    else:
        return 0.0
model.S2 = Param(model.A, model.A, initialize=s_init)


for i in model.S1:
    print(model.S1[i])
'''
