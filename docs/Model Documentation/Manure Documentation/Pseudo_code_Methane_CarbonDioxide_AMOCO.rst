Manure Module: Calculate Methane emissions & Carbon dioxide (AMOCO
Model)

   2.Calculate Methane (CH4) and Carbon dioxide production rate (CO2)
   Emissions.

   •Inputs (All inputs come from the weather file, the Animal Module).

+-----------------------------------+-----------------------------------+
| -                                 |    Variables use to calculate     |
|                                   |    Methane (CH4) and Carbon       |
|                                   |    dioxide (CO2)                  |
+===================================+===================================+
|    i.X1 = acidogenic bacteria (g  |                                   |
|    VS L^−1)                       |                                   |
|                                   |                                   |
|    ii.X2 = methanogenic bacteria  |                                   |
|    (g VS L^−1)                    |                                   |
|                                   |                                   |
|    iii.S1, S1in= organic          |                                   |
|    substrate (g VS L^−1)          |                                   |
|                                   |                                   |
|    iv.S2, S2in= volatile fatty    |                                   |
|    acids (mmol L^−1)              |                                   |
|                                   |                                   |
|    v.k1 = yield for substrate     |                                   |
|    degradation (g COD)            |                                   |
|                                   |                                   |
|    vi.k2 = yield for VFA          |                                   |
|    production (mmol/g)            |                                   |
|                                   |                                   |
|    vii.k3 = yield for VFA         |                                   |
|    consumption (mmol/g)           |                                   |
|                                   |                                   |
|    viii.k4 = yield for CO2        |                                   |
|    production (mmol/g)            |                                   |
|                                   |                                   |
|    ix. k5 = yield for CO2         |                                   |
|    production (mmol/g)            |                                   |
|                                   |                                   |
|    x.k6 = yield for CH4           |                                   |
|    production (mmol/g)            |                                   |
|                                   |                                   |
|    xi.kd = decay constant         |                                   |
|                                   |                                   |
|    xii.M1max = maximum acidogenic |                                   |
|    bacteria growth rate (d^-1)    |                                   |
|                                   |                                   |
|    xiii.M2max = maximum           |                                   |
|    methanogenic bacteria growth   |                                   |
|    rate (d^-1)                    |                                   |
|                                   |                                   |
|    xiv.Ks1 = half saturation      |                                   |
|    constants (g VS L^−1)          |                                   |
|                                   |                                   |
|    xv.Ks2 = half saturation       |                                   |
|    constants (mmol L^−1)          |                                   |
|                                   |                                   |
|    xvi.KI2 = inibition constant   |                                   |
|    (mmol L^−1)                    |                                   |
|                                   |                                   |
|    xvii.KH = Henry's constant for |                                   |
|    CO2 (mmol L^−1 atm^-1)         |                                   |
|                                   |                                   |
|    xviii.PT = Atmospheric         |                                   |
|    pressure (atm)                 |                                   |
|                                   |                                   |
|    xix.kLa = The liquid gas       |                                   |
|    transfer coefficient (d^-1)    |                                   |
|                                   |                                   |
|    xx.rC (input/output) = The     |                                   |
|    carbon dioxide production rate |                                   |
|    (mmol L^-1 d^-1)               |                                   |
|                                   |                                   |
|    xxi.Z, Zin = total alkalinity  |                                   |
|    (mmol L^-1)                    |                                   |
|                                   |                                   |
|    xxii.C,Cin = inorganic carbon  |                                   |
|    (mmol L^-1)                    |                                   |
|                                   |                                   |
|    xxiii.VL = Liquid Volume       |                                   |
|                                   |                                   |
|    xxiv.qin = volumetric flowrate |                                   |
|    (m^3 d^−1)                     |                                   |
|                                   |                                   |
|    xxv.Nbac = nitrogen content in |                                   |
|    the biomass                    |                                   |
|                                   |                                   |
|    xxvi.NS1 = nitrogen content of |                                   |
|    substrate S1 dependent on its  |                                   |
|    protein                        |                                   |
|                                   |                                   |
|    content.                       |                                   |
|                                   |                                   |
|    xxvii.N, Nin = inorganic       |                                   |
|    nitrogen (k mol m^-3)          |                                   |
|                                   |                                   |
|    xxviii.timeN = number of time  |                                   |
|                                   |                                   |
|    xxix.Mt = counter for time     |                                   |
+-----------------------------------+-----------------------------------+

..

   •Outputs

   i. rCH4 = Methane (CH4) production rate (mmol L^-1 d^-1)

   ii. rC = Carbon dioxide production rate (CO2) (mmol L^-1 d^-1)

   1.Organic substrate

+-----------------------+-----------------------+-----------------------+
| dS1_𝑑𝑡 =              |    | 𝑞𝑖𝑛              |    | 𝑆1               |
|                       |    | VL∗ (S1in − S1)  |    | S1+Ks1∗ 𝑋1       |
|                       |      − k1 ∗ M1max ∗   |      [M.2.1.1]        |
|                       |                       |                       |
|                       |                       | [M.2.1.2]             |
+=======================+=======================+=======================+
| new_S1                |                       |                       |
| =(timeN-Mt)*dS1_dt+S1 |                       |                       |
+-----------------------+-----------------------+-----------------------+

..

   2.Volatile fatty acids

+-----------------+-----------------+-----------------+-----------------+
| dS2_dt =        |    | 𝑞𝑖𝑛        |                 |    | 𝑆1         |
|                 |    | VL∗ (S2in  |                 |    | S1+Ks1∗ 𝑋1 |
|                 |      − S2) + k2 |                 |      − k3 ∗     |
|                 |      ∗ M1max ∗  |                 |      M2max ∗    |
|                 |                 |                 |                 |
|                 |                 |                 | [M.2.2.1]       |
|                 |                 |                 |                 |
|                 |                 |                 | [M.2.2.2]       |
+=================+=================+=================+=================+
|    | 𝑆2         |                 |    ∗ 𝑋2         |                 |
|    | S2+KS2+    |                 |                 |                 |
|      𝑆22 KI2    |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
|    new_S2=(time |                 |                 |                 |
| N-Mt)*dS2_dt+S2 |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

..

   3.Acidogenic bacteria

+-----------------+-----------------+-----------------+-----------------+
| dX1_𝑑𝑡 = −      |    | 𝑞𝑖𝑛        |    | 𝑆1         |                 |
|                 |    | VL∗ X1 +   |    | S1+Ks1−    |                 |
|                 |      (M1max ∗   |      kd) ∗ 𝑋1   |                 |
|                 |                 |      [M.2.3.1]  |                 |
+=================+=================+=================+=================+
|    new_X1=(time |                 |                 | [M.2.3.2]       |
| N-Mt)*dX1_dt+X1 |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

..

   4.Methanogenic bacteria

+-------------+-------------+-------------+-------------+-------------+
|             | 𝑞𝑖𝑛         | 𝑆2          |             | [M.2.4.1]   |
+=============+=============+=============+=============+=============+
| dX2_dt = −  | VL∗ X2 +    | S2+KS2      |    +𝑆22 KI2 |    − kd) ∗  |
|             | (M2max ∗    |             |             |    𝑋2       |
+-------------+-------------+-------------+-------------+-------------+
|    new_X    |             |             |             | [M.2.4.2]   |
| 2=(timeN-Mt |             |             |             |             |
| )*dX2_dt+X2 |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

..

   5. Inorganic nitrogen

+-------------+-------------+-------------+-------------+-------------+
| −∗M∗        | dNdt =      |    | 𝑞𝑖𝑛    |             |    | 𝑆1     |
|             |             |    | VL∗    |             |             |
|             |             |      (Nin − |             |   | S1+Ks1∗ |
|             |             |      N) +   |             |      X1     |
|             |             |      (k1 ∗  |             |             |
|             |             |      Ns1 −  |             |             |
|             |             |      Nbac)  |             |             |
|             |             |      ∗      |             |             |
|             |             |      M1max  |             |             |
|             |             |      ∗      |             |             |
+=============+=============+=============+=============+=============+
|             | 𝑆2          |    +𝑆22 KI2 |    ∗ 𝑋2 +   |             |
|             |             |             |    kd ∗     |             |
|             |             |             |    Nbac ∗   |             |
|             |             |             |    M1max ∗  |             |
|             |             |             |    X1 + kd  |             |
|             |             |             |    ∗ Nbac ∗ |             |
|             |             |             |    M2max ∗  |             |
|             |             |             |    X2       |             |
+-------------+-------------+-------------+-------------+-------------+
| −bac ∗Mmax  | S2+KS2      |             |             |             |
| ∗           |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             |             |             | [M.2.5.1]   |             |
+-------------+-------------+-------------+-------------+-------------+
|             |    ne       |             |             | [M.2.5.2]   |
|             | w_N=(timeN- |             |             |             |
|             | Mt)*dN_dt+N |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

..

   6. Alkalinity

+-----------------------+-----------------------+-----------------------+
| dZ_dt =               |    | 𝑞𝑖𝑛              |    | [M.2.6.1]        |
|                       |    | VL∗ (Zin − Z)    |    | [M.2.6.2]        |
+=======================+=======================+=======================+
| new                   |                       |                       |
| _Z=(timeN-Mt)*dZ_dt+Z |                       |                       |
+-----------------------+-----------------------+-----------------------+

..

   7. Inorganic carbon

+-----------+-----------+-----------+-----------+-----------+-----------+
| dC_dt =   |           |    | 𝑞𝑖𝑛  |           |           |    | 𝑆1   |
|           |           |    | VL∗  |           |           |           |
|           |           |      (Cin |           |           | | S1+Ks1∗ |
|           |           |      − C) |           |           |      X1 + |
|           |           |      + k4 |           |           |      k5 ∗ |
|           |           |      ∗    |           |           |           |
|           |           |           |           |           |     M2max |
|           |           |     M1max |           |           |           |
|           |           |      ∗    |           |           | [M.2.7.1] |
+===========+===========+===========+===========+===========+===========+
| ∗         | 𝑆2        |           |           |    ∗ 𝑋2 − |           |
|           |           |           |           |    𝑟𝐶     |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           | S2+KS2    |           |    +𝑆22   |           | [M.2.7.2] |
|           |           |           |    KI2    |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    new_C= |           |           |           |           |           |
| (timeN-Mt |           |           |           |           |           |
| )*dC_dt+C |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+

..

   8. Carbon dioxide production rate (CO2)

+-------------+-------------+-------------+-------------+-------------+
| Zprime=     |    k6       | 𝑆2          |             |             |
| new_Z+new_N |             |             |   [M.2.8.1] |             |
+=============+=============+=============+=============+=============+
|             |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|    Alph = C | kLa∗ M2max  | S2+KS2      |    +𝑆22 KI2 |    ∗ 𝑋2     |
|    + S2 −   | ∗           |             |             |             |
|    Zprime + |             |             |             |             |
|    KH ∗ PT  |             |             |             |             |
|    +        |             |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

[M.2.8.2]

+-----------------------------------+-----------------------------------+
|                                   | Alph−√Alph2−4∗KH∗PT∗(𝐶+𝑆2−Zprime) |
+===================================+===================================+
|    rC = kLa ∗ (C + S2 − Zprime) − | 2                                 |
|    kLa ∗                          |                                   |
+-----------------------------------+-----------------------------------+

[M.2.8.3]

   9. Methane (CH4) production rate

+-----------------+-----------------+-----------------+-----------------+
|                 | 𝑆2              |                 |    [M.2.9.1]    |
+=================+=================+=================+=================+
| rCH4 = k6 ∗     | S2+KS2          |    +𝑆22 KI2     |    ∗ 𝑋2         |
| M2max ∗         |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

..

   **References**

   Ficara, E., Hassam, S., Allegrini, A., Leva, A., Malpei, F., &
   Ferretti, G. (2012). Anaerobic digestion models: a comparative study.
   Math. Model, 7(1), 1052-1057.

   Bernard, O., Hadj‐Sadok, Z., Dochain, D., Genovesi, A., & Steyer, J.
   P. (2001). Dynamical model development and parameter identification
   for an anaerobic wastewater treatment process. Biotechnology and
   bioengineering, 75(4), 424-438.
