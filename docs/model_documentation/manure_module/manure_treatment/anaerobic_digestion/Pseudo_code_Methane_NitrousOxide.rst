Methane Nitrous Oxide
=====================

Manure Module: Calculate Nitrous Oxide & Methane emissions

   1.Calculate Nitrous Oxide & Methane emissions from puddle and slurry

   •Inputs (All inputs come from the weather file, the Animal Module and
   the farm structure file).

+-----------------------------------+-----------------------------------+
| -                                 |    | Variables use to calculate   |
|                                   |      Emission Nitrous N2O from    |
|                                   |      Urine (Puddle) i.Ap = Area   |
|                                   |      of the puddle (m2)           |
|                                   |    | ii.VR = Air velocity (m/s)   |
|                                   |    | iii.Pp = Density of the      |
|                                   |      puddle (kg/m3)               |
|                                   |    | iv.RH = Relative humidity    |
|                                   |      (%)                          |
|                                   |    | v.Sm1 = Urease activity (g   |
|                                   |      NH3/m2/h)                    |
|                                   |    | vi.CF = Correction Factor    |
|                                   |      for unit conversion          |
|                                   |    | vii.Vp = Volume of the       |
|                                   |      puddle (m3)                  |
|                                   |    | viii.U = Urea concentration  |
|                                   |      (mol/L)                      |
|                                   |    | ix.Km = Michaelis constant   |
|                                   |      (mol/L)                      |
|                                   |    | x.pHp = pH of the puddle     |
|                                   |    | xi.Dp = Diameter of the      |
|                                   |      puddle (m) ((4Ap/pi)^(1/2))  |
|                                   |    | xii.TANp = Total ammoniacal  |
|                                   |      nitrogen concentration in    |
|                                   |      the puddle (mol/L)           |
|                                   |    | xiii.CR = Concentration of   |
|                                   |      ammonia already present in   |
|                                   |      the air (mol/L)              |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   | - Additional variables use to calculate Emission Nitrous N2O from
     Feces (Slurry) xiv.VH = velocity over the slurry surface (m/s)
   | xv.LSlat = Slatted floor length (m)
   | xvi.pHs = pH of the slurry
   | xvii.As = Area of the slurry pile (m2)
   | xviii.TANs = Total ammoniacal nitrogen concentration in the manure
     slurry (mol/L)
   | xix.MN = Nitrogen in liquid and solid manure (gN) (g of manure N)
     xx.Mkg = Amount of manure (kg of manure)

+-----------------------------------------------------------------------+
|    | - Variables use for Methane Model                                |
|    | xxi.Afloor = Area covered by manure (m^2). Defined by amount of  |
|      manure xxii.VSd = Degradable volatile solids(g). Comes from      |
|      animal module xxiii.VSnd = Nondegradable volatile solids(g).     |
|      Comes from animal module xxiv.b1 = Rate correcting factors       |
|    | xxv.b2 = Rate correcting factors                                 |
|    | xxvi.A = Arrhenius parameter (g CH4/(kg VS)/h)                   |
|    | xxvii.E = Apparent activation energy (j/mol)                     |
|    | xxviii.R = Constant (J/K/mol)                                    |
|    | xxix.VS = Total volatile solids (g)                              |
+=======================================================================+
+-----------------------------------------------------------------------+

..

   | xxx.Bo = Maximum methane producing capacity (m3 CH4/g VS) xxxi.TR =
     Read Temperature (K-Kelvin)
   | xxxii.Ts = Temperature of slurry

   •Outputs

   | i. Ep = Emission Nitrous Oxide from the puddle (mol/s) ii. Es =
     Emission Nitrous Oxide from the slurry (mol/s) iii. TotN2O = Total
     Nitrous Oxide produced during time step (g N2O/hr)
   | iv. Methanefloor = Methane produced from unprocessed manure on the
     ground/floor (g CH4/day)

   | v. Methaneliquid = Methane produced from stored liquid manure (g
     CH4/day)
   | vi. Methanesolid = Methane produced from stored solid manure (g
     CH4/day)
   | vii. TotCH4 = Total methane emissions (g CH4/day)

   1. Emission Nitrous Oxide from the puddle

   The equations from 1 to 11 are used to calculate Emission Nitrous N2O
   from Urine (Puddle). It will use the temperature of the environment
   which comes from weather file. Also, there are some other inputs from
   the Animal module and farm structure file. Also, we have to update
   Vp, U, TANp, and pHp each day and use the new value in the equations.

   1. Saturation pressure of water

+-----------------------+-----------------------+-----------------------+
| e                     |    )                  | [M.1.1.1]             |
| (                     |                       |                       |
| 77.345+0.0057∗TR−7235 |                       |                       |
| TR                    |                       |                       |
|                       |                       |                       |
|    Psat = TR8.2       |                       |                       |
+=======================+=======================+=======================+
+-----------------------+-----------------------+-----------------------+

..

   2. Density of vapor of the puddle

+-----------------------------------+-----------------------------------+
| ρv =                              |    | Psat∗18                      |
|                                   |    | 100,000∗TR∗0.08315 [M.1.1.2] |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   3. Convective mass transfer coefficient for water

+-------------+-------------+-------------+-------------+-------------+
| kH2O =      | 0.7 ∗ vR    | 0.5 ∗ DP    | −0.5 ∗      |    0.666    |
| 0.0821 ∗ TR |             |             | DH2O,Air    |             |
|             |             |             |             |   [M.1.1.3] |
+=============+=============+=============+=============+=============+
+-------------+-------------+-------------+-------------+-------------+

..

   4. Change in the volume of the puddle

+-----------------+-----------------+-----------------+-----------------+
|                 | kH2O∗Ap         |                 | +-----+-----+   |
|                 |                 |                 | |     |     |   |
|                 |                 |                 | |  RH | [M. |   |
|                 |                 |                 | |     | 1.1 |   |
|                 |                 |                 | |     | .4] |   |
|                 |                 |                 | +=====+=====+   |
|                 |                 |                 | +-----+-----+   |
+=================+=================+=================+=================+
| dVP =           | ρP              | ∗ 1000 ∗ (ρv ∗  |    100− 1))     |
+-----------------+-----------------+-----------------+-----------------+

..

   5. Change in Urea concentration

+-----------------------------------+-----------------------------------+
| 1. Urease activity                |    Sm = Sm1 / (Vp / Ap) \* CF     |
|                                   |    [M.1.1.5.1]                    |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   2. Change in Urea concentration

+-----------------------------------+-----------------------------------+
|    | Sm∗U                         |    | U                            |
|    | dU = − ( Km+U) −             |    | Vp∗ dVp [M.1.1.5.2]          |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   6. Convective mass transfer coefficient for ammonia

+-------------+-------------+-------------+-------------+-------------+
| kNH3 =      | 0.7 ∗ vR    | 0.5 ∗ DP    | −0.5 ∗      |    0.666    |
| 0.0821 ∗ TR |             |             | DNH3,Air    |             |
|             |             |             |             |   [M.1.1.6] |
+=============+=============+=============+=============+=============+
+-------------+-------------+-------------+-------------+-------------+

..

   7. Fraction of TAN in ammonia form

+-----------------------------------+-----------------------------------+
|    | 10pHp                        |    ), 0.05] [M.1.1.7]             |
|    | fp = max[ (0.0897+2729       |                                   |
|      10pHp+5∗10 TR                |                                   |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   8. Dimensionless Henry Constant for ammonia (puddle)

Hp = 1431 ∗ 1.053(293−TR) [M.1.1.8]

   9. Change in total ammoniacal nitrogen concentration in the puddle

+-----------+-----------+-----------+-----------+-----------+-----------+
|           |           | fp∗TANp   |           |           |           |
+===========+===========+===========+===========+===========+===========+
| −Sm∗U     | kNH3∗     | Hp        | −CR       |           | TANp      |
|           | Ap∗1000∗( |           |           |           | [M.1.1.9] |
+-----------+-----------+-----------+-----------+-----------+-----------+
|    dTANp  | Vp        |           |           | −         |    Vp∗    |
|    = −2 ∗ |           |           |           |           |    dVp    |
|    (      |           |           |           |           |           |
|    Km+U)  |           |           |           |           |           |
|    −      |           |           |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+

..

   10. Change in the concentration of the pH of the puddle

dpHp = −0.75 ∗ dTANpfor dTANp > 0 [M.1.1.10.1]

dpHp = 6 ∗ dTANpfor dTANp < 0 [M.1.1.10.2]

   11. Emission from the puddle

+-----------------------------------+-----------------------------------+
|    fp∗TANp Ep = kNH3 ∗ Ap ∗ 1000  | − CR) [M.1.1.11]                  |
|    ∗ ( Hp                         |                                   |
+===================================+===================================+
+-----------------------------------+-----------------------------------+

..

   2.Emission Nitrous Oxide from the slurry

   The equations from1 to 5 are used to calculate Emission Nitrous N2O
   from Feces (Slurry). It will use the film temperature of the slurry.
   Also, there are some other inputs from the Animal module and farm
   structure file.

   1. Tfilm

+-----------------------+-----------------------+-----------------------+
| Tfilm =               |    (TR+TS)            | [M.1.2.1]             |
+=======================+=======================+=======================+
|                       |    2                  |                       |
+-----------------------+-----------------------+-----------------------+

..

   2. Convective mass transfer coefficient for ammonia

+-----------------------+-----------------------+-----------------------+
|    kNH3_s = 0.0821 ∗  | 0.7 ∗ VH0.5 ∗         |    0.666 [M.1.2.2]    |
|    Tfilm              | LSlat−0.5 ∗ DNH3,Air  |                       |
+=======================+=======================+=======================+
+-----------------------+-----------------------+-----------------------+

..

   3. Fraction of TAN in ammonia form from the slurry (dimensionless)

+-----------+-----------+-----------+-----------+-----------+-----------+
|           |           |    10pHS  |           |           | [M.1.2.3] |
+===========+===========+===========+===========+===========+===========+
| fS =      | pHS       | 1         |           |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+
|           | 10+       | 9.245∗10  |           | )         |           |
|           |           |           | −(0.0897+ |           |           |
|           |           |           |    2729   |           |           |
|           |           |           |    Tfilm  |           |           |
+-----------+-----------+-----------+-----------+-----------+-----------+

..

   4. Dimensionless Henry Constant for ammonia (puddle)

Hs = 1431 ∗ 1.053(293−Tfilm) [M.1.2.4]

   5. Emission from Slurry

+-----------------------+-----------------------+-----------------------+
| ES = kNH3 ∗ AS ∗ 1000 | f\ *S∗TANS*           |    − CR) [M.1.2.5]    |
| ∗ (                   |                       |                       |
+=======================+=======================+=======================+
|                       | HS                    |                       |
+-----------------------+-----------------------+-----------------------+

..

   3. Total Nitrous Oxide produced during time step from the puddle and
   slurry

+-------------+-------------+-------------+-------------+-------------+
|    TotN2O = |             |    | g NH3  |    | g N2O  |    | g N2O  |
|    [3600 ∗  |             |    | mol    |    | g NH3] |    | g      |
|    (ES +    |             |      NH3∗   |      +      |      manure |
|    Ep) ∗ 17 |             |      0.01   |      [0.005 |      N∗ MN] |
|             |             |             |             |      +      |
+=============+=============+=============+=============+=============+
| [5.4 ∗ 10−5 |    | g N2O  |             |             |             |
|             |    | kg     |             |             |             |
|             |             |             |             |             |
|             |     manure∗ |             |             |             |
|             |      Mkg]   |             |             |             |
|             |             |             |             |             |
|             |     [M.1.3] |             |             |             |
+-------------+-------------+-------------+-------------+-------------+

..

   4. Methane produced from unprocessed manure on the ground/floor

   The equations from 4 to 7 are used to calculate Methane emissions. It
   will use the temperature of the environment which comes from weather
   file. Also, there are some other inputs from the Animal module.

   Methanefloor = MAX(0, 0.13 ∗ TR) ∗ Afloor [M.1.4]

   5. Methane produced from stored liquid manure

+-----------------------+-----------------------+-----------------------+
|    24∗VS\ *d*\ ∗b1    |    | E                |    | E                |
|    Methaneliquid = [( |    | ln(A)−           |    | ln(A)−           |
|    1000               |      24∗VS\ *nd*\ ∗b2 |    | ) ∗ e R∗TR]      |
|                       |      ) ∗ e R∗TR] + [( |      [M.1.5]          |
|                       |    | 1000             |                       |
+=======================+=======================+=======================+
+-----------------------+-----------------------+-----------------------+

..

   6. Methane produced from stored solid manure

   1. CH4 conversion factor (%)

   MCF = 0.201 ∗(TR − 273) − 0.29 [M.1.6.1]

   2. Methane produced from stored solid manure

+-----------------------+-----------------------+-----------------------+
| Methanesolid =        |    VS∗Bo∗0.68∗MCF     | [M.1.6.2]             |
+=======================+=======================+=======================+
|                       |    100                |                       |
+-----------------------+-----------------------+-----------------------+

..

   7. Total methane emissions

   TotCH4 = Methanefloor + Methaneliquid + Methanesolid [M.1.7]

   **References**

Cortus, E. L., Lemay, S. P., & Barber, E. M. (2010). Dynamic simulation
of ammonia

concentration and emission within swine barns: Part I. Model
development. Transactions of the

   Asabe, 53(3), 911-923.
