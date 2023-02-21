"""
User-defined ration tools
JCW
"""
import json
with open('input/userdefinedration/userdefinedration_test.json', 'r') as f:
    rationall = json.load(f)
    key_list = list(rationall.keys())

# def format_ration_from_json(rationall):
#     value = 1
#     ration_as_dict = {'example1':value}
#     return ration_as_dict

# inputration = ration_cow_lactating
# def make_newbnds(inputration):
#     """
#     make a set of bounds that is used for the user-defind ration
#     this can be input into the optimize function to constrain it
#     this means it'll fail if it's not exactly what's needed for the available feeds
#     SO...
#     we give it the available feeds from the user-defined ration
#     THEN it tries the optimization for this narrow range
#     """
#     newbnds = []
#     for key in inputration:
#         #print(inputration[key])
#         newbnds.append(inputration[key])
#         newbnds.append(inputration[key])
#         newbnds.append(inputration[key])
#     newbnd2=[]
#     for bnd in newbnds:
#         newbnd2.append((bnd-bnd*0.1, bnd+bnd*0.1))
#     return tuple(newbnd2)

# def userbnds(animal_type):
#     import json
#     with open('input/userdefinedration/userdefinedration_test.json', 'r') as f:
#         rationall = json.load(f)
#         key_list = list(rationall.keys())
#     ration_calf = rationall[key_list[0]]['ration']
#     ration_all_heifers = rationall[key_list[1]]['ration']
#     ration_cow_lactating = rationall[key_list[2]]['ration']
#     ration_cow_dry = rationall[key_list[3]]['ration']
#     if animal_type == 'cow':
#         if cow_type == True:
#             rationtouse = make_newbnds(ration_cow_lactating)
#         else:
#             rationtouse = make_newbnds(ration_cow_dry)
#     elif animal_type == 'heifer':
#         rationtouse = make_newbnds(ration_all_heifers)
#     else: 
#         rationtouse = make_newbnds(ration_calf)
#     return rationtouse

# ration_calf = rationall[key_list[0]]['ration']
# ration_all_heifers = rationall[key_list[1]]['ration']
# ration_cow_lactating = rationall[key_list[2]]['ration']
# ration_cow_dry = rationall[key_list[3]]['ration']

# make_newbnds(ration_calf)
# make_newbnds(ration_all_heifers)
# make_newbnds(ration_cow_lactating)
# make_newbnds(ration_cow_dry)
ration_calf = rationall[key_list[0]]['ration']
ration_all_heifers = rationall[key_list[1]]['ration']
ration_cow_lactating = rationall[key_list[2]]['ration']
ration_cow_dry = rationall[key_list[3]]['ration']
with open('input/feed/panke_buisse_feed.json', 'r') as f:
    ff = json.load(f)
    key_list = list(ff.keys())

ff['calf_feeds']
ff['growing_feeds']
ff['close_up_feeds']
ff['lac_cow_feeds']

new_calf_feeds = [int(i) for i in ration_calf]
new_growing_feeds = [int(i) for i in ration_all_heifers]
new_close_up_feeds = [int(i) for i in ration_cow_dry]
new_lac_cow_feeds = [int(i) for i in ration_cow_lactating]

ff['calf_feeds']=new_calf_feeds
ff['growing_feeds']=new_growing_feeds
ff['close_up_feeds']=new_close_up_feeds
ff['lac_cow_feeds']=new_lac_cow_feeds

# fftoprint = json.dumps(ff, sort_keys=True, indent=4)

with open('input/feed/user_defined_ration_feed.json', 'w') as file:
  json.dump(ff, file, indent=4)

with open('input/feed/user_defined_ration_feed.json', 'r') as f:
    fff = json.load(f)
fff['purchased_feeds_costs']

feedslisted = list(fff['purchased_feeds_costs'].keys())
feedsprices = list(fff['purchased_feeds_costs'].values())

newlist = new_lac_cow_feeds + new_calf_feeds + new_close_up_feeds \
    + new_lac_cow_feeds
setlist = set(newlist)
newsetted = list(setlist)
newsetted.sort()
newsetted = [str(i) for i in newsetted]
# [newsetted not in feedslisted for newsetted in newsetted]
difflist = list(set(newsetted).difference(feedslisted))
difflist.sort()

dummyprices = [1 for i in difflist]
len(feedslisted)
len(difflist)
len(newsetted)
len(dummyprices)

newpricesdict = {}
for i in newsetted:
    print(i)
    if i in fff['purchased_feeds_costs'].keys():
        price = fff['purchased_feeds_costs'][str(i)]
        print(fff['purchased_feeds_costs'][str(i)])
    else: 
        price = 0.9999
        print(0.9999)
    newpricesdict[i] = price
len(newpricesdict)

fff['purchased_feeds_costs'] = newpricesdict
purchased_feeds_keynames = list(newpricesdict.keys())
fff['purchased_feeds'] = [int(i) for i in purchased_feeds_keynames]



with open('input/feed/user_defined_ration_feed.json', 'w') as file:
  json.dump(fff, file, indent=3)

with open('input/feed/user_defined_ration_feed.json', 'r') as f:
    fff = json.load(f)

def check_user_ration_and_requirements(user_ration, requirements):
    """    
    # set the requirements
    # WHAT ABOUT _ instead, we're putting very narrow bounds \
    # on the amount of EACH AVAILABLE FEED
    # MAKING THE BOUNDS THE VALUES FROM THE INPUTS THEMSELVES
    # 
    """    
    user_ration = [] 
    if user_ration >= requirements:
        value = 'success'
    else:
        value = 'not_a_success'
    return value


# follow the order of the feeds in the list - price or other?
# then go through and if it's not used in this ration, keep the bounds as is
# when it's a feed that's possible, set it to the ones in the json?
# 
llist = fff['purchased_feeds']

for i in llist:
    print(i)


with open('input/userdefinedration/userdefinedration_test.json', 'r') as f:
    user_ration_input = json.load(f)






def make_newbnds(inputration):
    """
    make a set of bounds that is used for the user-defind ration
    this can be input into the optimize function to constrain it
    this means it'll fail if it's not exactly what's needed for the available feeds
    SO...
    we give it the available feeds from the user-defined ration
    THEN it tries the optimization for this narrow range
    """
    newbnds = []
    if 1==2: print(' inputration is = ' +str(inputration))
    for key in inputration:
        #print(inputration[key])
        newbnds.append(inputration[key])
        newbnds.append(inputration[key])
        newbnds.append(inputration[key])
    newbnd2=[]
    for bnd in newbnds:
        bnd = bnd/3 # JCW ADDED 7dec
        # newbnd2.append((bnd-bnd*1, bnd+bnd*1.5))
        newbnd2.append((0, bnd+bnd*1.5))
    return tuple(newbnd2)


feed_available_feeds_keys_ = ['2', '26', '51', '86', '103', '118', '136', '139', '155', '157']
#feed.available_feeds.keys()
animal_type = 'cow'
cow_type = True
def clumsytemp(animal_type):
    import json
    with open('input/userdefinedration/userdefinedration_test.json', 'r') as f:
        rationall = json.load(f)
        key_list = list(rationall.keys())
    ration_calf = rationall['calf']['ration']
    ration_all_heifers = rationall['all_heifers']['ration']
    ration_cow_lactating = rationall['cow_lactating']['ration']
    ration_cow_dry = rationall['cow_dry']['ration']
    if animal_type == 'cow':
        if cow_type == True:
            rationtouse = ration_cow_lactating
        else:
            rationtouse = ration_cow_dry
    elif animal_type == 'heifer':
        rationtouse = ration_all_heifers
    else: 
        rationtouse = ration_calf
    #jcw# print('ration to use = '+ str(rationtouse))
    #return rationtouse
    # NEW BOUNDS to use instead
    triplethreat = []
    for key in feed_available_feeds_keys_:
        if key in rationtouse.keys():
            print(key)
            triplethreat.append(rationtouse[key])
            triplethreat.append(rationtouse[key])
            triplethreat.append(rationtouse[key])
        else:
            print('nothing')
            triplethreat.append(0)
            triplethreat.append(0)
            triplethreat.append(0)

############################
############################
############################
animal_type = 'cow'
cow_type = True
animal_type = 'cow'
cow_type = False
animal_type = 'heifer'
cow_type = False


# read in the JSON from the input/userdefinedration folder

# get the architecture sorted out with the format_ration_from_json function

# the main loop


#################################
# optimization from ration_driver
#   above uses: NLP.list_reconfig, NLP.set_globals, NLP.optimize, NLP.get_ration_vals
#           JCW focus on NLP.optimize
#   NLP.optimize checks if the solution good or not - then if YES, makes the ration
#   above imports AvailableFeeds class
#   above imports requirements, object of Requirements class
#################################


# needs to touch calc_rqmts
            # # creating instance of class requirements
            # req = Requirements()
            # req.set_requirements(pen, animal_type, False)

# mimic ration_formulation
# requirements - req.set_requirements(#ETC)
# THEN if animal ==cow, while not solution success 
            # # The logic here - solution success is FIRST checked using NEW FUNC
            # solution, ration_vals = optimization(req, available_feeds, animal_type, cow_type)
            # # Reduction of milk production estimate process to achieve feasible solution
            # if animal_type == 'cow':
            #     while not solution.success:
            #         # This values for reduction are not from pseudocode, but the vales below
            #         # are based on fastest case runtime testing
            #         # TODO: continue testing for more efficient reductions
            #         NEl_con = NLP.NEl_constraint(solution.x)
            #         if NEl_con < -0.5:
            #             reduction = 3 * (-NEl_con)
            #         else:
            #             reduction = 1.5

            #         for animal in pen.animals_in_pen:
            #             animal.estimated_daily_milk_produced -= reduction
            #         # recalculating requirements after reduction
            #         req.set_requirements(pen, animal_type, True)
            #         solution, ration_vals = optimization(req, available_feeds, animal_type, cow_type)

            # if solution != None:
            #     ration = {}
            #     for feed_id in range(len(available_feeds.feed_id)):
            #         i = feed_id * 3
            #         num = solution.x[i]
            #         num += solution.x[i + 1]
            #         num += solution.x[i + 2]
            #         ration[available_feeds.feed_key[feed_id]] = round(num, 6)
            #     ration['status'] = 'Optimal'
            #     ration['objective'] = NLP.objective(solution.x)
            #     return ration, ration_vals
            # # safeguard if scipy SLSQP bounds error still occurs after many iterations
            # # using previous cycles ration for this pen
            # else:
            #     return pen.ration, ration_vals