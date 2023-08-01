Manure Module: Calculate Methane (CH4) and Nitrous Oxide (N2O) Emissions
from Digester

   4.Calculate Methane (CH4) and Nitrous Oxide (N2O) Emissions.

   •Inputs (All inputs come from the weather file, the Animal Module).

+-----------------------------------+-----------------------------------+
| i.                                |    | Vn = Daily average           |
|                                   |      volumetric flow rate for day |
| ii.                               |      n (acfm)                     |
|                                   |    | Cn = Daily average CH4       |
|                                   |      concentration of digester    |
|                                   |      gas for day n (%, wet        |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   basis)

+-----------------------------------+-----------------------------------+
| iii.                              |    | Pn = Pressure at which flow  |
|                                   |      is measured for day n (atm)  |
| iv.                               |    | Days = Number of days in the |
|                                   |      reporting year (days/yr)     |
| v.                                |    | DE = CH4 destruction         |
|                                   |      efficiency from flaring or   |
| vi.                               |      burning in engine OH =       |
|                                   |      Number of hours destruction  |
| vii.                              |      device is functioning        |
|                                   |    | Hours = Hours in reporting   |
|    | viii.                        |    | CE = CH4 collection          |
|    | ix.                          |      efficiency of anaerobic      |
|                                   |      digester                     |
| x.                                |    | Nex = Total nitrogen         |
|                                   |      excreted per animal type     |
| xi.                               |      (kg/day)                     |
|                                   |    | Efmms = Emission factor for  |
|                                   |      MMS (kg N2O-N/kg N)          |
|                                   |    | TR = Read Temperature        |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   •Outputs

+-----------------------------------+-----------------------------------+
| i.                                |    B = The amount of Methane CH4  |
|                                   |    generated from the digester    |
| ii.                               |    (kg/day). C = Methane CH4      |
|                                   |    Destruction of Digesters       |
| iii.                              |    (kg/day).                      |
|                                   |                                   |
|                                   |    E = Direct Nitrous oxide N2O   |
|                                   |    emissions from manure          |
|                                   |    management systems             |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   (kg/day).

   iv. Generation = The greenhouse gas generation from manure management

   systems.

   v. Emissions = The greenhouse gas emissions from manure management

   systems.

   1

   1.Calculate Methane CH4 emissions from manure management 1.The amount
   of Methane CH4 generated from the digester

   B=Vn*Cn/100*0.0423*(520/TR)*Pn*1440*(1/2.20462)*Days [M.4.1.1]

   | 2.Methane CH4 Destruction of Digesters
   | CH4D=B [M.4.2.1] C=CH4D*DE*OH/Hours [M.4.2.2] 3.Methane CH4 Leakage
     at Digesters
   | D=CH4D*(1/CE-1) [M.4.3.1]

   2. Calculate Nitrous oxide N2O emissions from manure management

   | 4. Direct Nitrous oxide N2O emissions from manure management
     systems
   | E= (44/28)*Nex*EFmms*Days [M.4.4.1] 5. The greenhouse gas
     generation from manure management systems
   | Generation=B+E [M.4.5.1]

   | 6. The greenhouse gas emissions from manure management systems
   | Emissions=B-C+D+E [M.4.6.1]

   | **References**
   | U.S. Environmental Protection Agency. (2009). “Technical support
     document for manure management systems: proposed rule for mandatory
     reporting of ggases”. Climate Change Division Office of Atmospheric
     Programs, February 4, 2009

   2
