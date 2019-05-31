from RUFAS.routines.animal import ration
def test_ration(feed):
    #inputs
    BW=650
    BCS=3.5
    CBW=45
    CI=390
    concentrate=6
    CP_Milk=3.2
    DOP=30
    DHD=1.6
    DVD=0.1
    DIM	=100
    fat_milk=3.5
    lactose_milk=4.85
    milk=40
    parity=2
    type="Barn"

    rqmts = ration.calculate_rqmts(BW, BCS, CBW, CI, concentrate, CP_Milk, DOP,
                                        DHD, DVD, DIM, fat_milk, lactose_milk, milk, parity, type, feed.nutrient_rqmts)
    
    formulated_ration = ration.optimize(feed, rqmts)

    '''
    print('Solution is', formulated_ration['status'])
    print('Price is calculated to: \t', formulated_ration['objective'])
    print('Corn_grain is calculated to: \t', formulated_ration['Corn_grain'])
    print('Legume_hay is calculated to: \t', formulated_ration['Legume_hay'])
    print('Cotton_seed is calculated to: \t', formulated_ration['Cotton_seed'])
    print('Roasted_soybean is calculated to:', formulated_ration['Roasted_soybean'])
    print('Rye_hay is calculated to: \t', formulated_ration['Rye_hay'])

    print("\n done")
    '''
    
    return formulated_ration
