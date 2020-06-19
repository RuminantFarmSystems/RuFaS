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
#from RUFAS.routines.feed.feed import Feed


#retreiving decision variables (feeds) from the feed library
#TODO when neew feed library is brought into master
#For now just initialze a dummy X variable

feeds = {'2': {'feed_id': 2, 'type': 'Conc', 'DM': 86.9, 'CP': 6.5, 'NDICP': 2.3, 'ADICP': 1.8, 'EE': 2.9, 'NDF': 36.8, 'ADF': 28.7, 'lignin': 14.9, 'ash': 6.1, 'non_fiber_carb': 50, 'PAF': 1, 'TDN': 58.36, 'N_A': 29.6, 'N_B': 35.4, 'N_C': 35, 'Kd': 5.3, 'dRUP': 50, 'calcium': 0.28, 'phosphorus': 0.13, 'magnesium': 0.13, 'potassium': 2.6, 'sodium': 0.02, 'chlorine': 0.03, 'sulfur': 0.04, 'DE': 2.53, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}, '24': {'feed_id': 24, 'type': 'Conc', 'DM': 89.4, 'CP': 23.8, 'NDICP': 3.6, 'ADICP': 1.4, 'EE': 3.5, 'NDF': 35.5, 'ADF': 12.1, 'lignin': 2, 'ash': 6.8, 'non_fiber_carb': 34, 'PAF': 1, 'TDN': 74.07, 'N_A': 48, 'N_B': 43.2, 'N_C': 8.8, 'Kd': 7.7, 'dRUP': 85, 'calcium': 0.07, 'phosphorus': 1, 'magnesium': 0.42, 'potassium': 1.46, 'sodium': 0.13, 'chlorine': 0.2, 'sulfur': 0.44, 'DE': 3.43, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}, '36': {'feed_id': 36, 'type': 'Forage', 'DM': 35.1, 'CP': 8.8, 'NDICP': 1.3, 'ADICP': 0.8, 'EE': 3.2, 'NDF': 45, 'ADF': 28.1, 'lignin': 2.6, 'ash': 4.3, 'non_fiber_carb': 40, 'PAF': 0.94, 'TDN': 68.82, 'N_A': 51.3, 'N_B': 30.2, 'N_C': 18.5, 'Kd': 4.4, 'dRUP': 70, 'calcium': 0.28, 'phosphorus': 0.26, 'magnesium': 0.17, 'potassium': 1.2, 'sodium': 0.01, 'chlorine': 0.29, 'sulfur': 0.14, 'DE': 2.99, 'is_fat': 0, 'is_wetforage': 1, 'units': 'kg', 'limit': 100}, '38': {'feed_id': 38, 'type': 'Conc', 'DM': 90.1, 'CP': 23.5, 'NDICP': 2.4, 'ADICP': 1.9, 'EE': 19.3, 'NDF': 50.3, 'ADF': 40.1, 'lignin': 12.9, 'ash': 4.2, 'non_fiber_carb': 5.1, 'PAF': 1, 'TDN': 77.22, 'N_A': 45.4, 'N_B': 46.7, 'N_C': 7.9, 'Kd': 15.7, 'dRUP': 80, 'calcium': 0.17, 'phosphorus': 0.6, 'magnesium': 0.37, 'potassium': 1.13, 'sodium': 0.02, 'chlorine': 0.06, 'sulfur': 0.23, 'DE': 3.55, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}, '91': {'feed_id': 91, 'type': 'Forage', 'DM': 39.1, 'CP': 20, 'NDICP': 2.9, 'ADICP': 1.6, 'EE': 3.1, 'NDF': 45.7, 'ADF': 37, 'lignin': 8.1, 'ash': 10.4, 'non_fiber_carb': 23.7, 'PAF': 1, 'TDN': 56.57, 'N_A': 57.3, 'N_B': 33, 'N_C': 9.9, 'Kd': 11.1, 'dRUP': 65, 'calcium': 1.34, 'phosphorus': 0.32, 'magnesium': 0.27, 'potassium': 2.87, 'sodium': 0.06, 'chlorine': 0.62, 'sulfur': 0.24, 'DE': 2.62, 'is_fat': 0, 'is_wetforage': 1, 'units': 'kg', 'limit': 100}, '102': {'feed_id': 102, 'type': 'Forage', 'DM': 91.9, 'CP': 9.1, 'NDICP': 1.3, 'ADICP': 0.6, 'EE': 2.2, 'NDF': 58, 'ADF': 36.4, 'lignin': 6.5, 'ash': 8.5, 'non_fiber_carb': 23.5, 'PAF': 1, 'TDN': 55.91, 'N_A': 35, 'N_B': 53.1, 'N_C': 11.9, 'Kd': 4.3, 'dRUP': 70, 'calcium': 0.37, 'phosphorus': 0.22, 'magnesium': 0.17, 'potassium': 2.01, 'sodium': 0.33, 'chlorine': 1.08, 'sulfur': 0.14, 'DE': 2.46, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}, '137': {'feed_id': 137, 'type': 'Mineral', 'DM': 97, 'CP': 0, 'NDICP': 0, 'ADICP': 0, 'EE': 0, 'NDF': 0, 'ADF': 0, 'lignin': 0, 'ash': 0, 'non_fiber_carb': 0, 'PAF': 0, 'TDN': 0, 'N_A': 0, 'N_B': 0, 'N_C': 0, 'Kd': 0, 'dRUP': 0, 'calcium': 16.4, 'phosphorus': 21.6, 'magnesium': 0, 'potassium': 0, 'sodium': 0, 'chlorine': 0, 'sulfur': 1.22, 'DE': 0, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}}

global price
global NEmaint
global NEa
global TDN
global DE
global EE
global is_fat
global BW
global SBW

price = [5, 8, 10, 12, 6]
NEmaint = 20
NEa = 30
TDN = [56, 55.91, 53.2, 51, 60]
DE = [3.2, 2, 4.2, 3, 5]
EE = [3.2, 2, 6, 4, 5]
is_fat = [0, 0, 0, 0, 0]
BW = 420
SBW = 389


def objective(x):
    obj = 0
    return sum(np.multiply(x, price))
    #return x[0]*price[0] + x[1]*price[1] + x[2]*price[2] + x[3]*price[3] + x[4]*price[4]

def NEmact_constraint(x):
    '''
    Sets up the RHS multipliers for the maintenance and activity requirments
    satisfied by the feed. Each equation has a reference to the respective
    calculation in the psuedo code.

    Args:
        x: The decision variables of the NLP
        NEmaint: The Net Energy maintenance requirement
        NEa: The Net Energy activity requirement
        TDN: List of TDN values by feed
        DE: List of standard DE feed, Mcal/kg
        EE = List of Feed fat (ether extract) content, %
        is_fat = If the feed is fat supplement or not (yes = 1; no = 0)
        BW:
        SBW:
    '''
    #DMI calculated by the NLP
    DMI = sum(x)
    #Dietary TDN content (calculate using standard value in NRC (2001))
    TotalTDN = sum(np.multiply(x, (TDN)))
    TotalTDN = np.multiply(TotalTDN, 0.01)
    #TDN concentration, %
    if DMI != 0:
        TDNconc = TotalTDN / DMI    #[A.Cow.E.1]
    else:
        TDNconc = 0
    #The amount of intake needed to meet the maintenance requirement, dimensionless
    if TotalTDN < (0.035 * BW**0.75):       #[A.Cow.E.2]
        DMI_to_maint = 1
    else:
        DMI_to_maint = (TotalTDN / (0.035 * SBW**0.75))
    #TDN discount, TDN digestibility decrease caused by DMI and TDNconc
    if TDNconc < 60:        #[A.Cow.E.3]
        Discount = 1
    else:
        Discount = (TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))) / TDNconc
    #Actual TDN content of feed i, %
    TDNact = np.multiply(TDN, Discount)     #[A.Cow.E.4]
    #Actual digestible energy of feed i, Mcal/kg
    DEact = np.multiply(DE, Discount) #[A.Cow.E.5]
    #Actual metabolizable energy of feed i, Mcal/kg
    MEact = []
    for i in range(len(DEact)):    #[A.Cow.E.5]
        if is_fat[i] == 1:
            MEact.append(DE[i])
        elif EE[i] >= 3:
            MEact.append(1.01 * DEact[i] - 0.45 + 0.0046 * (EE[i] - 3))
        else:
            MEact.append(1.01 * DEact[i] - 0.45)
    #Actual net energy for lactation of feed i, Mcal/kg
    NEm_act = []
    for i in range(len(MEact)):     #[A.Cow.E.7]
        if is_fat[i] == 1:
            NEm_act.append(0.8*MEact[i])
        else:
            NEm_act.append(1.37 * MEact[i] - 0.138 * MEact[i]**2 + 0.0105 * MEact[i]**3 - 1.12)


    return sum(np.multiply(x, NEm_act) - (NEmaint + NEa))


n = len(price)
x0 = np.zeros(n)

## OPTIMIZE:
b= (1, 100)
bnds = (b, b, b, b, b)
cons = {'type': 'ineq', 'fun': NEmact_constraint}
#con1 = {'type': 'ineq', 'fun': constraint1}
#con2 = {'type': 'ineq', 'fun': constraint2}
#cons = ([con1, con2]
solution = minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=cons)

x = solution.x

print(x)
print(objective(x))
