**Growth constraints**
~~~~~~~~~~~~~~~~~~~~~~

The ``GrowthConstraints`` class handles the environmental constraints to
potential plant growth that a crop faces during the growing season. This
module addresses the stresses caused by insufficient water, inadequate
nutrients (nitrogen and phosphorus) and extreme temperatures, and
determines which, if any, is limiting plant growth on a given day.

The main method, ``constrain_growth()`` calls on the **water stress**,
**temperature stress**, **nitrogen stress** and **phosphorus stress**
methods to provide daily updates on the **plant growth factor**, which
quantifies the fraction of potential plant growth achieved on a given
day. Each environmental stress varies from 0, under optimal conditions,
to 1, under extreme stress.

**Water stress** is the stress caused by the water soil conditions on a
given day by comparing actual and potential plant transpiration:

.. math::

    W_{\text{stress}} = 
   \begin{cases}
       1- \frac{W_{\text{uptake}}}{Tr_{\text{max}}}         & \text{if } Tr_{\text{max}} \not= 0 \\ 
       0                                                    & \text{otherwise}
   \end{cases} 

where :math:`W_{\text{stress}}` is the water stress (``water_stress``),
:math:`W_{\text{uptake}}` is the total water taken up by the plant from
the soil on a given day (``water_uptake``), and :math:`Tr_{\text{max}}`
is the maximum plant transpiration on a given day
(``max_transpiration``).

**Temperature stress** represents the stress experienced by a plant when
the mean air temperature on a given day diverges from the optimal
temperature for plant growth. It is calculated using the following
equations:

.. math::

    T_{\text{stress}} = 
   \begin{cases}
       1- exp\frac{-0.1054\times (T_{\text{crop, opt}} - T_{\text{air}})^{2}}{(T_{\text{air}} - T_{\text{crop, min}})^{2}}                                               & \text{if } T_{\text{crop, min}} < T_{\text{air}} <= T_{\text{crop, opt}} \\
       1- exp\frac{-0.1054\times (T_{\text{crop, opt}} - T_{\text{air}})^{2}}{((2\times T_{\text{crop, opt}} - T_{\text{crop, min}}) - T_{\text{crop, min}})^{2}}        & \text{if } T_{\text{crop, opt}} < T_{\text{air}} <= 2\times T_{\text{crop, opt}} - T_{\text{crop, min}} \\                                                                                                                                                                                                                                                   
       1                                                                                                                                                                 & \text{otherwise}
   \end{cases}

where :math:`T_{\text{stress}}` is the temperature stress
(``temp_stress``), :math:`T_{\text{air}}` is the mean air temperature
for a given day (``temperature``), :math:`T_{\text{crop, 
min}}` is the base or minimum temperature for the crop to grow
(``minimum_temperature``), and :math:`T_{\text{opt}}` is the optimal
temperature for the crop to grow (``optimal_temperature``).

**Nitrogen stress** calculates the plant nitrogen stress on a given day
by comparing actual and optimal plant nitrogen levels and requires the
initial estimation of a **stress factor** for nitrogen stress:

.. math::

    S_{\text{N}} = 
       200\times (\frac{N_{\text{plant}}}{N_{\text{opt}}} - 0.5)         

where :math:`S_{\text{N}}` is the stress factor for nitrogen stress
(``stress_factor``), :math:`N_{\text{plant}}` is the actual mass of
nitrogen stored in plant material on a given day (``nitrogen``), and
:math:`N_{\text{opt}}` is the optimal mass of nitrogen stored in plant
material for the current growth stage (``optimal_nitrogen``).

Then, **nitrogen stress** is calculated as follows:

.. math::

    N_{\text{stress}} = 
       1 - \frac{S_{\text{N}}}{S_{\text{N}} + exp(3.535 - 0.02597 \times S_{\text{N}})}          

where :math:`N_{\text{stress}}` is the nitrogen stress
(``nitrogen_stress``), and :math:`S_{\text{N}}` is the stress factor for
nitrogen stress (``stress_factor``).

**Phosphorus stress** follows the same calculation as **nitrogen
stress**, quantifying the plant phosphorus stress by comparing actual
and optimal plant phosphorus levels. First, the stress_factor for
phosphorus stress is calculated:

.. math::

    S_{\text{P}} = 
       200 \times (\frac{S_{\text{plant}}}{S_{\text{opt}}} - 0.5)         

where :math:`S_{\text{P}}` is the stress factor for phosphorus stress
(``stress_factor``), :math:`P_{\text{plant}}` is the actual mass of
phosphorus stored in plant material on a given day (``phosphorus``), and
:math:`P_{\text{opt}}` is the optimal mass of phosphorus stored in plant
material for the current growth stage (``optimal_phosphorus``).

Then, **phosphorus stress** is calculated using the equation:

.. math::

    P_{\text{stress}} = 
       1 - \frac{S_{\text{P}}}{S_{\text{P}} + exp(3.535 - 0.02597 \times S_{\text{P}})}          

where :math:`P_{\text{stress}}` is the phosphorus stress
(``phosphorus_stress``), and :math:`S_{\text{P}}` is the stress factor
for phosphorus stress (``stress_factor``).

Finally, the 4 environmental stresses quantified on a given day are used
to calculate the **plant growth factor** as follows:

.. math::

    \gamma_{\text{reg}} = 
       1 - max(W_{\text{stress}}, T_{\text{stress}}, N_{\text{stress}}, P_{\text{stress}})        

where :math:`\gamma_{\text{reg}}` is the plant growth factor
(``growth_factor``), :math:`W_{\text{stress}}` is the water stress
(``water_stress``), :math:`T_{\text{stress}}` is the temperature stress
(``temp_stress``), :math:`N_{\text{stress}}` is the nitrogen stress
(``nitrogen_stress``), and :math:`P_{\text{stress}}` is the phosphorus
stress (``phosphorus_stress``).

--------------

**References**: this module is based upon the “Growth Constraints”
section of the
`SWAT <https://swat.tamu.edu/media/99192/swat2009-theory.pdf>`__ model
(5:3.1).
