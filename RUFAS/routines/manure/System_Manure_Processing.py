'''
Created on Oct 2, 2018

@author: ombenomr
'''
'''
Created on Sep 4, 2018

@author: ombenomr
'''
# This code is written by Osama Ben Omran
# Date : 08/23/2018
# Program Name: System_Manure_Processing.py
# This program is for calculate Emissions from Manure Management System 
#Calculate Nitrous Oxide N2O & Methane CH4 emissions from puddle and slurry
#
#  Ver (1.00)

import math


def Input_data():
    # For read data from weather module
    return
def Read_Farm_Structure():
    # For read Farm Structure
    global T_storage_treatment
    global Farm_no, Farm_name, Farm_Location
    global G_surface,T_collection

    #
    Farm_no=1
    Farm_name="N Arkansas"
    Farm_Location="444 Arkansas"
    G_surface="Solid Concrete"
    T_collection="Flush"
    T_storage_treatment= []
    # T_storage_treatment ( Storage number, manure  management system name, QTY in stock before processing, percentage number go in the storage from manure, size area
    T_storage_treatment.append(['3','Solid Storage', '1000', '60', '2000'])
    T_storage_treatment.append(['8', 'Liquid/Slurry', '0', '40', '1000'])

    return

def Read_temp(x_days):
    # Read Temperature
    global Temp
    file = open("weather_file.txt", "r")
    file.readline()
    file.readline()
    file.readline()
    line_count = 0
    # with open(filename) as f:
    Temp = []
    while True:
        c = file.read(1)
        while c != '#':
            c = file.read(1)
        c = file.read(1)
        tmp = ''
        while c != '#':
            tmp = tmp + c
            c = file.read(1)
        file.readline()
        
        #366
        if not c or line_count == x_days:
            #("End of file")
            break
        # print ("Read a character:", c)
        # print (float(tmp)+10)
        Temp.append([float(tmp)])
        line_count = line_count + 1

    return

def System_Manure_Processing(x_days):
    #Some variables
    
    Ap=4 #Area of the puddle
    VR=2 #Air velocity
    Pp=1 #Density of the puddle
    RH=3 # Relative humidity
    Sm1=1.5 # Urease activity
    CF=1.6*10**(-13) #Correction Factor for unit conversion
    Vp=4 #Volume of the puddle
    U=1 #Urea concetration
    Km=0.002  #Michaelis constant
    pHp=9.2 # pH of the puddle
    TANp=3  # Total ammoniacal nitrogen concentration in the puddle
    #Hp=1
    CR=0 #Concentration of ammonia already present in the air
    #for Feces Slurry
    VH = 2 # velocity over the slurry surface
    LSlat = 3 #Slatted floor length
    pHs = 8.5 #pH of the slurry
    As = 3 # Area of the slurry pile
    TANs = 2 #Total ammoniacal nitrogen concentration in the manure slurry
    MN=3   #Nitrogen in liquid and solid manure (gN)
    Mkg=8  #Amount of manure (kg of manure)
    # For Methane Model
    Afloor=3 # Area covered by manure (m^2). Defined by amount of manure
    VSd=5 # Degradable  volatile solids(g). Comes from animal module
    VSnd=3 # Nondegradable volatile solids(g). Comes from animal module
    b1=1  #Rate correcting factors
    b2=0.01 #Rate correcting factors
    A=1000000  #Arrhenius parameter
    E=112700 #Apparent activation energy
    R=8.314 # Constant
    VS=5 #Total volatile solids
    Bo=0.00023  # Maximum methane producing capacity

    Pi=3.142
    DH20=0.26*10**(-4)
    DNH3=0.28*10**(-4)
    Eppen=0
    #Call Function to read data
    # Diameter of the puddle
    Dp=math.sqrt(4*Ap/Pi)
    Read_temp(x_days)
    # Read Farm Structure
    Read_Farm_Structure
    Result_Urine = [] # for Nitrous Oxide Data
    Result_Slurry = [] # for Nitrous Oxide Data
    Result_Methane = [] # for Methane Data
    i_array=0
    file=open("result_output.txt","w")
    # Repeat Loop
    for i in Temp:
        for TR in i:
            #Saturation pressure of water
            Psat = math.exp(77.345 + 0.0057 * TR - 7235 / TR) / TR ** (8.2)
            #Density of vapor of the puddle
            Pv=Psat*18/(100000*TR*0.08315)
            #Convective mass transfer coefficient for water
            KH20=0.0821*TR**(0.7)*VR**(0.5)*Dp**(-0.5)*DH20**(0.666)
            #change in the volume of the puddle
            dVp=KH20*Ap/Pp*1000*(Pv*(RH/100-1))
            # Urease activity
            Sm = Sm1 / (Vp / Ap) * CF
            #Change in Urea concentration
            dU=(-1)*(Sm*U/(Km+U))-U/Vp*dVp
            # Convective mass transfer coefficient for ammonia
            KNH3=0.0821*TR**(0.7)*VR**(0.5)*Dp**(-0.5)*DNH3**(0.666)
    
            # Fraction of TAN in ammonia form
            A1=0.0897+2729/TR
    
            for_max = 10 ** pHp / (10 ** pHp + 5 * 10 **A1)
            fp=max(for_max,0.05)
    
            #?
            #Dimensionless Henry Constant for ammonia (puddle)
            Hp=1431*1.053**(293-TR)
            #Change in total ammoniacal nitrogen concentration in the puddle
            #Sums the effects of urea degradation, ammonia volatilization, and water evaporation on TAN concentration
            dTANp=(-2)*(-Sm*U/(Km+U))-KNH3*Ap*1000*(fp*TANp/Hp-CR)/Vp-TANp/Vp*dVp
            #Change in the concentration of the pH of the puddle
            if dTANp>0:
                dpHp=-0.75*dTANp
            else:
                dpHp=6*dTANp
            # Equ.23 from paper
            # Emission from the puddle
            
            Ep = KNH3 * Ap * 1000 * (fp * TANp / Hp - CR)
            #print (KNH3, Ap, fp, TANp, Hp, CR, Ep)
            #Tfilm=(TR+TS)/2
            #Tfilm=120 # Fahrenheit
            Tfilm=322.039 #Kelvin
            # Convective mass transfer coefficient for ammonia
            KNH3_s = 0.0821 * Tfilm ** (0.7) * VH ** (0.5) * LSlat ** (-0.5) * DNH3 ** (0.666)
            # Fraction of TAN in ammonia form from the slurry (dimensionless)
            A11 =(-1)* (0.0897 + 2729 / Tfilm)
            #fs = Decimal(10) ** Decimal(pHs) / (Decimal(10) ** Decimal(pHs) + Decimal(1)/(Decimal(9.245) * Decimal(10) ** Decimal(A11)))
            fs = 10 ** pHs / (10 ** pHs + 1 / (9.245 * 10 ** A11))
            # Henry constant of the slurry (Dimensionless)
            Hs = 1431 * 1.053 ** (293 - Tfilm)
    
            #Emission from Slurry
            Es=KNH3_s*As*1000*(fs*TANs/Hs-CR)
            # Put the result in the array
            #Result_Urine.append([TR, dVp, dU, dTANp, dpHp, Ep])
            Result_Urine.append([TR, Vp, U, TANp, pHp, Ep])
            Result_Slurry.append([Tfilm, fs, Es])
    
            #Methane Model
            Methane_floor = max(0, 0.13*TR)*Afloor
            Methane_liquid=24*VSd*b1/1000*math.exp(math.log(A)-E/(R*TR))+24*VSnd*b2/1000*math.exp(math.log(A)-E/(R*TR))
            MCF=0.201*(TR-273)-0.29
            Methane_solid=VS*Bo*0.68*MCF/100
            Tot_CH4 = Methane_floor + Methane_liquid + Methane_solid
            Result_Methane.append([Methane_floor, Methane_liquid, MCF, Methane_solid, Tot_CH4])
    
            #New values for (Vp, U, TANp, pHp)
            Vp=Vp+dVp
            U=U+dU
            TANp=TANp+dTANp
            pHp=pHp+dpHp
    
            i_array=i_array+1
    
    #Total NO2 produced during time step (g N2o/hr)
    TotN2O=3600*(Es+Ep)*17*0.01+0.005*MN+5.4*10**(-5)*Mkg
    
    # Print the result in Result Urine
    
    #print (Result_Urine)
    file.write("     Nitrous Oxide emissions \n")
    file.write("   Total N2O produced %11.5f \n"% TotN2O)
    #for i in range(i_array):
     #   for j in range(6):
      #      print (" ", Result_Urine[i][j], end = " "),
       # print ()

    file.write(" \n\n")    
    file.write("Emission Nitrous N2O from Urine(Puddle) \n")   
    file.write ("Temperature     Volume           Urea      Total ammoniacal       PHP of      Emission \n")
    file.write ("              of the puddle   concetration nitrogen concentation the puddle from the puddle \n")
    file.write ("================================================================================================== \n")
    
    for i in Result_Urine:
        for j in i:
            f_print="%11.5f"% j+'    '
            file.write(f_print)
            #file.write("%11.5f"% j, end='    ')
        file.write("\n")
    file.write ("================================================================================================== \n")
 
    
    # Print the result in Result Slurry
    
    file.write(" \n\n")
    file.write("Emission Nitrous N2O from Feces(Slurry) \n")  
    file.write (" Film        Fraction of TAN  Emission from \n") 
    file.write ("Temperature     in Ammonia      the Slurry \n")
    file.write ("=================================================== \n")
    
    for i in Result_Slurry:
        for j in i:
            f_print="%11.5f"% j+'    '
            file.write(f_print)
            #file.write("%11.5f"% j, end='    ')
        file.write(" \n")
    file.write ("=================================================== \n")
    #print("Total methane emissions=", Tot_CH4)
    file.write(" \n\n")
        
    file.write("        Methane emissions \n")
    file.write ("  Methane produced from        Methane produced from   CH4 conversion Methane produced from      Total methane\n") 
    file.write ("unprocessed manure on Ground   stored liquid manure      factor       stored solid manure         emissions\n")
    file.write ("=============================================================================================================\n")
    
    # Print the result in Result Slurry
    for i in Result_Methane:
        for j in i:
            f_print="%11.5f"% j+'              '
            file.write(f_print)
            #file.write("%11.5f"% j, end='              ')
        file.write(" \n")
    file.write ("============================================================================================================= \n")
    file.close()
    return
 

#System_Manure_Processing(3)  

 