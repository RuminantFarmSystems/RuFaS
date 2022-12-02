"""
RUFAS: Ruminant Farm Systems Model
File name: pyomo_solver.py

Description: This file formats the non-linear program ration model into a
    pyomo structured model. Various different solvers can be used in this
    format.
Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""

import pyomo.environ as pyo
from RUFAS.output_manager import OutputManager

om = OutputManager()

def model_shell():
    """
    Calling this function will construct and return a valid pyomo Abstract model
    ready to be populated with an according pyomo data dictionary.
    """
    #creatin abstract model blueprint
    model = pyo.AbstractModel()
    ###Sets###
    #set of feeds for formulation
    model.feed = pyo.Set(doc='FEEDS')
    #set of different energy types
    model.nrg = pyo.Set(doc = 'ENERGY', initialize = ['mact', 'lact', 'growth'])

    ###Parameters###
    #feed nutrient data and information
    model.price = pyo.Param(model.feed, model.nrg)
    model.TDN = pyo.Param(model.feed, model.nrg)
    model.DE = pyo.Param(model.feed, model.nrg)
    model.EE = pyo.Param(model.feed, model.nrg)
    model.is_fat = pyo.Param(model.feed, model.nrg)
    model.calcium = pyo.Param(model.feed, model.nrg)
    model.phosphorus = pyo.Param(model.feed, model.nrg)
    model.NDF = pyo.Param(model.feed, model.nrg)
    model.ftype = pyo.Param(model.feed, model.nrg, within = pyo.Any)
    model.is_wetforage = pyo.Param(model.feed, model.nrg)
    model.Kd = pyo.Param(model.feed, model.nrg)
    model.N_A = pyo.Param(model.feed, model.nrg)
    model.N_B = pyo.Param(model.feed, model.nrg)
    model.CP = pyo.Param(model.feed, model.nrg)
    model.dRUP = pyo.Param(model.feed, model.nrg)
    model.limit = pyo.Param(model.feed, model.nrg)
    #animal requirement parameters
    model.NEmaint = pyo.Param(within = pyo.NonNegativeReals)
    model.NEa = pyo.Param(within = pyo.NonNegativeReals)
    model.NEg = pyo.Param(within = pyo.NonNegativeReals)
    model.NEpreg = pyo.Param(within = pyo.NonNegativeReals)
    model.NEl = pyo.Param(within = pyo.NonNegativeReals)
    model.MP_req = pyo.Param(within = pyo.NonNegativeReals)
    model.Ca_req = pyo.Param(within = pyo.NonNegativeReals)
    model.P_req = pyo.Param(within = pyo.NonNegativeReals)
    model.DMIest = pyo.Param(within = pyo.NonNegativeReals)
    model.BW = pyo.Param(within = pyo.NonNegativeReals)
    #big M
    model.bigM = pyo.Param(initialize = 1000000)

    ###Variables###
    #bounds function for variables
    def bnds(m, i, j):
        """
        Arg(s):
            m: an abstract model
            i: the index of set feed
            j: the index of set nrg
        """
        return(0, m.limit[i, j])
    model.x = pyo.Var(model.feed, model.nrg, domain = pyo.NonNegativeReals, bounds=bnds)
    #single variable for discount value
    model.discount = pyo.Var(domain = pyo.NonNegativeReals)
    #Indicator variables
    model.Z1 = pyo.Var(domain = pyo.Binary)
    model.Z2 = pyo.Var(domain = pyo.Binary)

    ###Objectives###
    def obj_cost(m):
        """
        Objective function
        Arg(s):
            m: model object
        """
        return pyo.summation(m.price, m.x)
    #objective pyomo object
    model.cost = pyo.Objective(rule=obj_cost, sense=pyo.minimize)

    ###Constraints###
    #constraint rules
    '''
    def discount_con(m):
        C = 0.035*(m.BW*0.98)**0.75
        TDNconc = (pyo.summation(m.TDN, m.x)*0.01) / pyo.summation(m.x)
        DMI_to_maint = ((pyo.summation(m.TDN, m.x)*0.01)/C)*(1-m.Z1) + m.Z1
        Discount = (((TDNconc - 0.18*TDNconc - 10.3)*(DMI_to_maint - 1)) / \
                        TDNconc) * (1-m.Z2) + m.Z2
        return m.discount == Discount
        '''

    def NDF_constraint_1(m):
        return pyo.summation(m.NDF, m.x)  >= 25 * pyo.summation(m.x)
    def NDF_constraint_2(m):
        return pyo.summation(m.NDF, m.x) <= 45 * pyo.summation(m.x)

    #Indicator Variable Constraint Rules#
    #These constraints and variables are used in the place of conditional
    #statements on variable values
    '''
    #These constraint ensures that Z1 = 1 if TotalTDN < C and Z1 = 0 else
    def z_con1(m):
        C = 0.035*(m.BW*0.98)**0.75
        return pyo.summation(m.TDN, m.x)*0.01 >= (C - m.bigM*(m.Z1))
    def z_con11(m):
        C = 0.035*(m.BW*0.98)**0.75
        return pyo.summation(m.TDN, m.x)*0.01 <= (C + m.bigM*(1-m.Z1))
    #These constraint ensures that Z2 = 1 if Totalconc < 60 and Z2 = 0 else
    def z_con2(m):
        TDN_tot = (pyo.sum_product(m.TDN, m.x)*0.01)
        return TDN_tot >= (60 - m.bigM*m.Z2) * pyo.summation(m.x)
    def z_con22(m):
        TDN_tot = (pyo.summation(m.TDN, m.x)*0.01)
        return TDN_tot / (60 + m.bigM*(1-m.Z2)) <= pyo.summation(m.x)
    '''
    #constrain pyomo objects
    model.NDF_con1 = pyo.Constraint(rule = NDF_constraint_1)
    model.NDF_con2 = pyo.Constraint(rule= NDF_constraint_2)
    #model.Indcon1 = pyo.Constraint(rule = z_con1)
    #model.Indcon11 = pyo.Constraint(rule = z_con11)
    #model.Indcon2 = pyo.Constraint(rule = z_con2)
    #model.Indcon22 = pyo.Constraint(rule = z_con22)
    #model.discountcon = pyo.Constraint(rule = discount_con)

    return model

def create_model(feeds_data, req_data, feeds):
    """
    Creates a concrete model out of the abstract model shell from the function
    above, populates this abstract model with data organized in ration_driver.py

    Arg(s):
        feeds_data: a dictionary of the feed nutrition information for each feed
                    in this optimization
        req_data: a dictionary of the animal requirements for the optimization
        feeds: a list of the feeds to be used in this optimization
    """
    #inner data of the pyomo dictionary input structure
    in_data = {}
    in_data['feed'] = {None: feeds}
    #populating data container with feed nutrient parameter data
    for key, val in feeds_data.items():
        in_data[key] = val
    #populating data container with animal requirements parameter data
    for key, val in req_data.items():
        in_data[key] = {None: val}

    #data structured for pyomo model input
    data = {None: in_data}
    #creating an instance of this model withe the populated data
    model = model_shell()
    m1 = model.create_instance(data)
    results = pyo.SolverFactory('APOPT').solve(m1)

    info_map = {"class": "no_caller_class",
                "function": self.create_model.__name__,
                "feeds_data": feeds_data,
                "req_data": req_data,
                "feeds": feeds,}

    om.add_variable("m1", 
                    m1,
                    info_map)  
    
    # for i,j in m1.feed*m1.nrg:
    #     print(i, j, m1.x[i,j]())

    #print('\nConstraints')
    #print('NDF Con 1  = ', m1.NDF_con1())
    #print('NDF Con 2 = ', m1.NDF_con2())
