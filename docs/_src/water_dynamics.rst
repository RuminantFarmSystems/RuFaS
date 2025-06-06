**Water dynamics**
~~~~~~~~~~~~~~~~~~

The ``WaterDynamics``\ class handles for each selected field the
evapotranspiration process by which water, through evaporation and
transpiration, becomes atmospheric water vapor. The main method,
``cycle_water()``, comprises the **cumulative evapotranspiration** and
**water deficiency** methods:

**Cumulative evapotranspiration** represents the total millimeters of
evapotranspired water at the end of the growing season (or at defined
harvest/cut time):

.. math::

    Et_{\text{cum}} =    E_{\text{cum}}+T_{\text{cum}}     

where :math:`Et_{\text{cum}}` is the total millimeters of
evapotranspired water at the end of the growing season
(``cumulative_evapotranspiration``), :math:`E_{\text{cum}}` is the sum
of the daily values of water evaporated at the end of the growing season
(``cumulative_evaporation``), and :math:`T_{\text{cum}}` is the sum of
the daily values of water transpired at the end of the growing season
(``cumulative_transpiration``).

**Water deficiency** is a factor that represents the relationship
between cumulative and potential evapotranspiration during the growing
season. It is used to incorporate the effect of water deficit in the
**potential harvest index**. The factor is calculated at harvest/cut
time using the following equations:

.. math::

    W_{\text{def}} = 
   \begin{cases}
       100\times \frac{Et_{\text{cum}}}{Et_{\text{pot,cum}}}         & \text{if } Et_{\text{pot,cum}} \not= 0 \\
       0                                                             & \text{otherwise}
   \end{cases}

where :math:`W_{\text{def}}` is the water deficiency factor
(``water_deficiency``), :math:`Et_{\text{cum}}` is the total millimeters
of evapotranspired water at the end of the growing season
(``cumulative_evapotranspiration``), and :math:`Et_{\text{pot,cum}}` is
the total millimeters of evapotranspired water in the growing season
from a large area uniformly covered with growing vegetation with access
to unlimited water supply (``max_cumulative_evapotranspiration``).

--------------

**References**: this module is based upon the “Potential
Evapotranspiration”, “Actual Evapotranspiration” and “Actual yield”
sections of the
`SWAT <https://swat.tamu.edu/media/99192/swat2009-theory.pdf>`__ model
(2:2.1; 2:2.2; 5:3.3).
