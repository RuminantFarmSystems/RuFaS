"""
RUFAS: Ruminant Farm Systems Model
File name: pyomo_solver.py

Description: This file formats the non-linear program ration model into a
    pyomo structured model. Various different solvers can be used in this
    format.
Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""

import pyomo.environ as pyo

#available_feeds.price = [1,2,3]

price = [1,2,3]
TDN = [58,57,59]
DE = [2,3,4]
EE = [3,2,4]
is_fat = [0,0,0]
calcium = [22,24,26]
phosphorus = [0.5,0.2,0.3]
NDF = [10,12,11]
feed_type = ['Conc', 'Forage', 'Forage']
is_wetforage = [0,0,0]
Kd = [5,3,2]
N_A =[52,44,37]
N_B = [23,26,27]
CP = [9.4,5.6,8.9]
dRUP = [50,45,65]
n = len(price)
limit = [10, 10, 10]

#creating the model
model = pyo.ConcreteModel()
#creating model sets
model.feed = pyo.RangeSet(1,n, doc='FEEDS')
model.nrg = pyo.Set(doc = 'ENERGY', initialize = ['mact', 'lact', 'growth'])

#getting data from the lists in a valid input for pyomo parameters
price_dat = {}
TDN_dat = {}
DE_dat = {}
EE_dat = {}
is_fat_dat = {}
calcium_dat = {}
phosphorus_dat = {}
NDF_dat = {}
feed_type_dat = {}
is_wetforage_dat = {}
Kd_dat = {}
N_A_dat = {}
N_B_dat = {}
CP_dat = {}
dRUP_dat = {}
limit_dat = {}

for i in range(n):
    for j in model.nrg:
        price_dat[i+1, j] = price[i]
        TDN_dat[i+1, j] = TDN[i]
        DE_dat[i+1, j] = DE[i]
        EE_dat[i+1, j] = EE[i]
        is_fat_dat[i+1, j] = is_fat[i]
        calcium_dat[i+1, j] = calcium[i]
        phosphorus_dat[i+1, j] = phosphorus[i]
        NDF_dat[i+1, j] = NDF[i]
        feed_type_dat[i+1, j] = feed_type[i]
        is_wetforage_dat[i+1, j] = is_wetforage[i]
        Kd_dat[i+1, j] = Kd[i]
        N_A_dat[i+1, j] = N_A[i]
        N_B_dat[i+1, j] = N_B[i]
        CP_dat[i+1, j] = CP[i]
        dRUP_dat[i+1, j] = dRUP[i]
        limit_dat[i+1, j] = limit[i]

#crearing an initialize model parameters with the data
model.price = pyo.Param(model.feed, model.nrg, initialize = price_dat)
model.TDN = pyo.Param(model.feed, model.nrg, initialize = TDN_dat)
model.DE = pyo.Param(model.feed, model.nrg, initialize = DE_dat)
model.EE = pyo.Param(model.feed, model.nrg, initialize = EE_dat)
model.is_fat = pyo.Param(model.feed, model.nrg, initialize = is_fat_dat)
model.calcium = pyo.Param(model.feed, model.nrg, initialize = calcium_dat)
model.phosphorus = pyo.Param(model.feed, model.nrg, initialize = phosphorus_dat)
model.NDF = pyo.Param(model.feed, model.nrg, initialize = NDF_dat)
model.feed_type = pyo.Param(model.feed, model.nrg, initialize = feed_type_dat, within = pyo.Any)
model.is_wetforage = pyo.Param(model.feed, model.nrg, initialize = is_wetforage_dat)
model.Kd = pyo.Param(model.feed, model.nrg, initialize = Kd_dat)
model.N_A = pyo.Param(model.feed, model.nrg, initialize = N_A_dat)
model.N_B = pyo.Param(model.feed, model.nrg, initialize = N_B_dat)
model.CP = pyo.Param(model.feed, model.nrg, initialize = CP_dat)
model.dRUP = pyo.Param(model.feed, model.nrg, initialize = dRUP_dat)

#variables

def fb(model, i, j):
    return(0, limit_dat[i,j])
model.feed_amount = pyo.Var(model.feed*model.nrg, domain = pyo.PositiveReals,
                                            bounds =fb, initialize=3)
