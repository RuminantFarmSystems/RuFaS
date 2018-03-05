setwd("C:/users/kreed.MLIT/desktop/IFSM updates/Model structure/ration formulation")



################ Ration formulation pseudocode



#################################################
########### Estimate Requirements
#################################################
#################################################

#### ************** Note that these requirement estimates will be replaced when the new nutrition recommendations come out

#### inputs - DIM, parity, average milk fat (AMF),body weight ratio (BWR)

parity = 1 # number of lactations
WIM = 20 # week in milk, week
AMF = 3.5 # average milk fat for the breed, %
BWR = 1 # ratio of calving body weight to holstein calving weight
BaseNED = 1 # Baseline net energy density of the diet
HOUSE = "Barn"

########## Calculate Fiber intake capacity
#FIC = fiber intake capacity

if(parity > 1){
  FIC = (0.564*(WIM + 0.857)^(0.360))* exp(-0.0186 *(WIM + 0.857)) 
}else{
  FIC = (0.388*(WIM+3)^(0.588))*exp(-0.0277*(WIM+3))
}


########## Estimate Base milk production
#BaseMY is the milk base milk yield estimated from breed specific lactation curve

if(parity >1){
  BaseMY = 33.95*(WIM^0.2208)*exp(-0.03395*WIM)  
}else{
  BaseMY = 24.12*(WIM^0.1782)*exp(-0.02095*WIM)
}

############### Estimate Base milk fat
#BaseMF is the base milk fat estimated from breed specific 
# average milk fat and component lactation curve

BaseMF = 1.4286*AMF*WIM^(-0.24)*exp(0.016*WIM)



############### Estimate Body Weight

### The body weight is estimated as a function of DIM and 
### the ratio of the calving weight of the breed to that of holsteins

if(parity >1){
  BW = BWR*690*(WIM + 1.57)^(-0.0803)*exp(0.00720*(WIM + 1.57))
}else{
  BW = BWR*567*(WIM+1.71)^(-0.0730)*exp(0.00869*(WIM+1.71))
}


############## Estimate Change in Body weight

if(WIM<56){
  if(parity>1){
    DBW = BWR*690*(WIM+0.57)^(-.0803)*exp(.00720*(WIM+0.57))
  }else{
    DBW = BWR*567*(WIM+0.71)^-0.730*exp(0.00869*(WIM+0.71))
  }
  
  CBW = (BW-DBW)/7 # change in body weight (kg/d)
}

### Estimate energy equivalent of Change in Bodyweight
if(WIM<11){CS = 3.4}else{CS = 5} # change energy value depending on stage in lactation
NEKG = 0.5381*CS + 3.2855 #Net energy in deposited or mobilized body (Mcal/kg bw) tissue

if(CBW < 0){ 
  MECBW = NEKG*CBW/0.785/100}else{
    MECBW = NEKG*CBW/0.75/100}
  

###########################################################
##################          Estimate Prot and Energy Req
############################################################


############ Estimate Maintenance Energy Req

SBW = 0.96*BW
NEM = 0.073*SBW^0.75

############### Estimate Activity Energy Rew

#### set number of hours, position changes and distances traveled if housed in a barn, drylot or grazing
if(HOUSE == "Barn"){
  HOURS = 12; POSCHG = 9; FLATDIST = 0.5; SLOPEDIST = 0.001} else {
    if(HOUSE == "DRYLOT"){
      HOURS = 15; POSCHG = 9; FLATDIST = 1.5; SLOPEDIST = 0.001
    }else{ HOURS = 16; POSCHG = 6; FLATDIST = 1; SLOPEDIST = 0}
  }


STAND  = 0.1*HOURS*SBW/0.96
CHANG  = 0.062*POSCHG*SBW/0.96
DISTF  = 0.621*FLATDIST*SBW/0.96
DISTS  = 6.69*SLOPEDIST*SBW/0.96
NEACT = (STAND+CHANG+DISTF+DISTS)/1000

############ Estimate Maintenance Protein Req

MPM = 3.8*SBW^0.75 # g metabolizable protein for maintenance

############ Estimate lacatation energy and protein Req

MEMLK = BaseMY*(0.3523 + 0.0962*BaseMF)/0.644  #Mcal ME required for milk 
 MLKPROT = 1.9 + 0.4*BaseMF  # milk protein %
MPMLK = 10*MLKPROT*BaseMY/0.65  # g metabolizable protein for milk

######### Sum total req

MEReq = NEM/0.667 + NEACT/0.667 + MEMLK + MECBW # total ME req (Mcal)
MPReq = MPM + MPMLK # total MP rew (g)



###############################################
### Estimate Rumen degradable and undegradable protein
############################################

BaseMED = 1.095*BaseNED + 0.751 # BaseMED is the baseline Metabolizable energy of the diet


DMIEst = MEReq/BaseMED

TDN = 0.31*BaseNED + 0.2 #Total digestible Nutrients (TDN) is a measure of diet quality/content used the the NRC

MCP = 0.13*TDN*DMIEst # MCP is microbial crude protein





#############################################################
############################################################
# Set Up Inputs for Linear Program
#
##########################################################





#####################################################
### Set Constraints limits based on requirements and intake capacity (RHS of constraints matrix)
#####################################################

FIMax = 0.01025*BW*FIC # Fiber intake maximum
RVMin = 0
MEIMin = BaseNED*DMIEst*(1-0.0206) - 0.7*MPReq/1000
RDPMin = MCP/0.9
RUPMin = MPReq /1000 - 0.8*0.8*MCP



######################################################
#####   Establish constraint coefficiencts for feeds
########################################################

### IFSM allows for the use of a combination of up to 6 feeds 
    # 1. Forage
    # 2. Corn, high moisture
    # 3. Corn , grain
    # 4. Protein supplement
    # 5. Undegradable protein supplement
    # 6. Fat supplement

###  9 descriptions of each feed is required
    # 1. NDF, fraction of DM
    # 2. Fill Units, fraction of DM
    # 3. Roughage Units, fraction of DM
    # 4. NE, Mcal/kg Dm
    # 5. CP, fraction of DM
    # 6. Indigestible CP, fraction of DM
    # 7. Rumen degradable protein, fraction of CP
    # 8. Concentrate or Roughage, "Conc" or "For"
    # 9. Cost of feed

### These are used to calculate 5 metrics (constraints) of the feed for use in ration forumlation
    # 1. Physical fill
    # 2. Roughage value/ effective nDF
    # 3. Energy
    # 4. Degradable Protein
    # 5. Undegradable protein

    #read in feed matrix
    feed = read.csv("feed inputs.csv")
    row.names(feed) = feed[, 1]
    
    feed = feed[ , 2:ncol(feed)]
    
    
    #establish empty vectors
    Fill = NA; RumenVol = NA; NE = NA; NH3 = NA; UnavailProt = NA; RumenDegProt = NA; EscapeProt = NA
    # loop over type of feed
    for(i in 1:6){
     #set fill, rumen volume, and net energy 
      Fill[i] = feed[i, 2]
      RumenVol[i] = feed[i , 3]
      NE[i] = feed[i, 4]
      
      #Use rumen degradable, total, and indigestible CP to estimate degradable and undegradable CP
      NH3[i] = feed[i, 5]*feed[i , 7]
      
      if(feed[i, 8] == "Conc"){
        UnavailProt[i] = 0.4*feed[i, 6]
      }else {UnavailProt[i] = 0.7*feed[i,6]}
      
      RumenDegProt[i] = NH3[i] + 0.15*feed[i, 5]
      EscapeProt[i] = 0.87*(feed[i, 5] - NH3[i] - UnavailProt[i]*feed[i, 5])
    }

    
    # Set up RHS limits to limit intake of purchased feeds
    
    CGLimit = feed["Corn Grain", "Limit"]
    ProtLimit =  feed["Protein Supp", "Limit"]
    UndProtLimit = feed["Undegradable Protein Supp", "Limit"]
    FatLimit = feed["Fat Supplement", "Limit"]

    # Set up LHS Constraint vectors to limit intake of purchased feeds
    
    CGConstraint = c(0, 0, 1, 0, 0, 0)
    ProtConstraint = c(0, 0, 0, 1, 0, 0)
    UndProtConstraint = c(0, 0, 0, 0, 1, 0)
    FatConstraint = c(0, 0, 0, 0, 0, 1)
    
######################################################
####     Set up RHS and LHS of Constraints matrix
########################################################    


RHS = c(FIMax, RVMin, MEIMin, RDPMin, RUPMin, CGLimit, ProtLimit, UndProtLimit, FatLimit)
LHS = rbind(Fill, RumenVol, NE, RumenDegProt, EscapeProt, CGConstraint,ProtConstraint,
            UndProtConstraint, FatConstraint)




######################################################
####     Set price vector as variables for the objective function for least cost ration formulation
########################################################

Price = NA

for(i in 1:6) {
  Price[i] = feed[i , 9]
}


#### Run LP solver

library(lpSolve)

sol = lp(direction = "min", objective.in = Price, const.mat = LHS, 
         const.dir = c("<=", ">", ">=", ">=", ">=", "<=", "<=", "<=", "<="), 
   const.rhs = RHS)
sol$solution
sol$constraints
sol$objective
sol$status
sol$objval
