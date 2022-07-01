import math
from dataclasses import dataclass, asdict
from typing import Protocol

from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from .gas_emissions_constants import GasEmissionConstants as Constants


@dataclass
class CanCalcMethane(Protocol):
    """
    To calculate methane emission, we need VSd and VSnd from
    manure handlers, separators, or treatments.
    """
    VSd: float
    VSnd: float


class GasEmissions:
    @staticmethod
    def calc_E_CH4_storage(data: CanCalcMethane, temp=15.0) -> float:
        """
        ECH4,man = 	[(( 24 * Vs,d * b1)/1000) * exp[ln(A)) - (E/RT)] + (( 24 * Vs,nd *  b2)/1000) * exp[ln(A) -(E/RT)]

        E CH4 man = emission of CH4 from the storage, kg CH4/day
        Vs,d and Vs, nd = degradable and non-degradable VS in the manure, g
        b1 and b2 = rate correcting factors, dimensionless
        A = Arrhenius parameter, g CH4/kg VS-h
        E = apparent activation energy, J/mol
        R = gas constant, J/K-mol
        T = temperature, K
        VS = volatile solids

        Constants

        b1	           = 1
        b2	           = 0.0.1
        ln(A)          = 43.33
        E	           = 112700
        R	           = 8.314
        Temp (manure) °K   = T + 273.15
        T                  = 0 to 25 degree C
        B0                 = 0.2
        ECH4,pot           = 0.48
        VS                 = input value from the manure

        """
        daily_time_steps = 24
        b1 = 1.0
        b2 = 0.01
        lnA = 43.33
        E = 112700
        R = 8.314
        T = temp + 273.15
        ex = math.exp(lnA - (E / (R * T)))

        # Equation: (( 24 * Vs,d * b1)) * exp[ln(A)) - (E/RT)] + (( 24 * Vs,nd *  b2)) * exp[ln(A) -(E/RT)]
        return (daily_time_steps * data.VSd * b1 * ex) + (daily_time_steps * data.VSnd * b2 * ex)

    @staticmethod
    def calc_E_CH4_storage_2(data: CanCalcMethane, temp=15.0, Bo=0.2, E_CH4_pot=0.48) -> float:
        """

        Args:
            data:
            temp:
            Bo:
            E_CH4_pot:

        Returns:

        """
        c = 0.024
        VS_tot = data.VSd + data.VSnd
        b1 = 1.0
        b2 = 0.01
        lnA = 43.33
        E = 112700
        R = 8.314
        T = temp + 273.15
        ex = math.exp(lnA - (E / (R * T)))
        VS_loss = 3 * Bo
        VSd = (data.VSd * (Bo / E_CH4_pot) - VS_loss) / VS_tot
        VSnd = VS_tot - VSd

        return c * VS_tot * (VSd * b1 + VSnd * b2) * ex

    @staticmethod
    def calc_modified_hours(hours: float) -> float:
        """

        Args:
            hours:

        Returns:

        """
        if hours > 14:
            modified_hours = - math.tanh(hours - 21.5) / 3.5
        elif hours > 4:
            modified_hours = math.tanh(hours - 9.5) / 2.5
        else:
            modified_hours = - math.tanh(hours + 3.5) / 3.5
        return modified_hours

    @staticmethod
    def calc_ambient_temp(hours, t_min, t_max):
        """

        Args:
            hours:
            t_min:
            t_max:

        Returns:

        """
        modified_hours = GasEmissions.calc_modified_hours(hours)
        t_ambient = modified_hours * (t_max - t_min) / 2 + (t_max + t_min) / 2
        return t_ambient

    @staticmethod
    def calc_barn_area(pen: SimplePen) -> float:
        """

        Args:
            pen:

        Returns:

        """
        if 'Cow' in pen.classes_in_pen:
            if pen.housing_type == 'tie stall':
                barn_area = 1.2
            elif pen.housing_type == 'bedded pack':
                barn_area = 5.0
            else:  # default is free stall
                barn_area = 3.5
        else:
            if pen.housing_type == 'tie stall':
                barn_area = 1.0
            elif pen.housing_type == 'bedded pack':
                barn_area = 3.0
            else:  # default is free stall
                barn_area = 2.5
        return barn_area

    @staticmethod
    def calc_E_CH4_floor(pen: SimplePen, t_min=20.0, t_max=25.0, hours=24):
        """
        Calculates the ECH4_floor.

        Args:
            pen:
            t_min:
            t_max:
            hours:
        """
        t_ambient = GasEmissions.calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        barn_area = GasEmissions.calc_barn_area(pen)
        return pen.num_animals * max(0.0, 0.13 * t) * barn_area / 1000

    @staticmethod
    def calc_E_C02_floor(pen: SimplePen, t_min=20.0, t_max=25.0, hours=24):
        """

        Args:
            pen:
            t_min:
            t_max:
            hours:

        Returns:

        """
        t_ambient = GasEmissions.calc_ambient_temp(hours, t_min, t_max)
        t = max(-5.0, 0.63 * t_ambient + 6.0)
        barn_area = GasEmissions.calc_barn_area(pen)
        return pen.num_animals * max(0.0, 0.0065 + 0.0192 * t) * barn_area / 1000

    @staticmethod
    def calc_E_NH3_N(Tan, c, p, r, m, q):
        """
        Calculating ammonia emissions.
        TODO: 

        Args:
            Tan:
            c:
            p:
            r:
            m:
            q:

        Returns:

        """
        return (Tan * c * p) / (r * m * q)

    @staticmethod
    def calc_kh(T):
        return 10 ** (1478 / (T + 273) - 1.69)

    @staticmethod
    def calc_ka(T, pH):
        """

        """
        return 1 + 10 ** (0.09018 + 2729.9) / (T + 272 - pH)

    @staticmethod
    def calc_q(ka, kh):
        return kh * ka

    @staticmethod
    def calculate_ruc(vmax, cu, Kmc):
        """
        Returns the RUC = rate of urea transformation to TAN via Eq. (1),
        kg/m3-h

        Args:
        CU = urea concentration in urine, kg/m3
        Vmax = maximum rate of urea conversion, kg N/m3 wet feces-h
        Kmc = Michaelis-Menten coefficient, kg N/m3 mixture
        """
        return vmax * cu / (Kmc + cu)

    @staticmethod
    def calculate_vmax(T):
        """
        Returns the Vmax, maximum rate of urea conversion, kg N/m3 wet feces-h

        Args:
          T - temperature in Kelvin
        """
        return 3.915 * (10 ** 9) * math.exp(-6463 / T)

    @staticmethod
    def calculate_kmc(T):
        """
        Returns the Kmc = Michaelis-Menten coefficient, kg N/m3 mixture

        Args:
          T - temperature in Kelvin
        """
        return 3.371 * (10 ** 8) * math.exp(-5914 / T)

    @staticmethod
    def calculate_f(ph, Ka):
        """
        Returns the ammonia fraction of TAN in a manure solution, F

        Args:

          ph : surface pH of manure or urine
          Ka: the dissociation constant
        """
        return 1 / (1 + (10 ** (-ph)) / Ka)

    @staticmethod
    def calculate_ka(T):
        """
        Returns the dissociation constant, Ka

        Args:
          T - temperature in Kelvin
        """
        return 10 ** (0.05 - 2788 / T)

    @staticmethod
    def calculate_henry_constant(T):
        H = (T/0.2138) * 10**(1825/T - 6.123) 
        return H 
    

    """
    Returns the mass transfer coefficient through gaseous layer

    Args:
        U = air friction velocity near surface, m/s
        SC = Schmidt number

    """
    @staticmethod
    def calculate_mass_transfer_coefficient_gaseous(U, SC):
        return 0.001 + 0.0462 * U * ( SC**(-0.67))


    """
    Returns the air friction velocity

    Args:
        Va: ambient air velocity measured at a standard anemometer height of 
        10 m 
    
    """
    @staticmethod
    def calculate_air_friction_velocity(Va):
        return 0.02*Va**(1.5)
    
        """
        Returns the  Henry’s Law constant for ammonia, H

        Args:
          T - temperature in Kelvin

        """
        hsc = (T / 0.2138) * 10 ** (1825 / T - 6.123)

        return hsc * (1 - 0.027 * (20 - T))


    """
    Returns the mass transfer coefficient through liquid layer
    
    Args:
      T - temparature in Kelvin
    """
    @staticmethod
    def calculate_mass_transfer_coefficient_liquid(T):
        return 1.417 * 10**(-12) * T**(4) 


    """
    Returns the resistance to mass transfer

    Args:
        Rs = resistance to mass transfer through the manure, s/m
        Rc = resistance to mass transfer through a storage cover, s/m
    """
    @staticmethod
    def calculate_resistance_to_mass_transfer(Rs, Rc):
        return Rs + Rc
        


    """
    Returns the the overall mass transfer coefficient, the reciprocal of the 
    sum of the three resistances to mass transfer.

    Args:
        Rm: resistance to mass transfer
        H:  Henry’s Law constant for ammonia, dimensionless aqueous:gas
        Kg: = mass transfer coefficient through gaseous layer, m/s
        Kl: mass transfer coefficient through liquid layer
    """
    @staticmethod
    def calculate_overall_mass_transfer_coefficient(H, Kg, Kl, Rm):
        return (1 / ( H / Kg + 1/Kl + Rm )) 
 


    """
    Returns the ammonia flux, kg/m2-s

    Args:
        Cm = concentration of ammonia in manure, kg/m3
        Ca = concentration of ammonia in ambient air, kg/m3  
    """
    @staticmethod
    def calculate_ammonia_flux(K, Cm, H, Ca):
        return 3600 * K * (Cm - H * (Ca))


    """
    Returns the ammonia concentration in the manure

    Args:
        F = ammonia fraction of TAN in a manure solution
        C_tan = concentration of TAN in the manure solution, kg/m^3
    """
    @staticmethod
    def calculate_concentration_of_ammonia_in_manure(F, C_tan):
        return F * C_tan



"""  
    @staticmethod
    def calc_E_N20_manure(EF_n20, A_storage):

      
        EN2O,manure = emission of N2O from slurry storage, kg N2O /day
        EF,N2O,man = emission rate of N2O, 0.8 g N2O /m2 -day
        A_storage = exposed surface area of the manure storage, m2

        Note: For stacked manure with a greater DM content, an emission factor of 0.005 kg N2O-N /(kg Nexcreted)
             when a crust does not form, no N2O is formed and emitted
             This occurs if the manure DM contents less than 8%, manure is loaded daily onto the top surface of the
             storage, or an enclosed tank is used

"""
    @staticmethod
    def convert_temp_C_to_K(temp_in_C: float):
        """
        
        Args:
            temp_in_C: temperature in Celsius

        Returns:

        """
        return temp_in_C + 273.0
