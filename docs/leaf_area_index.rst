**Leaf area index**
~~~~~~~~~~~~~~~~~~~

The ``LeafAreaIndex``\ class handles the seasonal changes in canopy
height and leaf area for each crop during the growing season. The **leaf
area index** (*LAI*) is defined as the area of green leaf per unit area
of land, having a maximum value that, once reached, remains constant
until leaf senescence becomes the dominant growth process.

The main method, ``grow_canopy()``, calls on the **optimal leaf area
fraction**, **shape parameters**, **canopy height**, **maximum leaf area
change** and **senescent leaf area index** to update on a daily basis
the **leaf area added** to the crop.

The **optimal leaf area fraction** method controls the **canopy height**
and **leaf area added** until the maximum *LAI* is reached and
represents the fraction of the plant’s maximum *LAI* corresponding to a
given fraction of potential heat units. To calculate this fraction on a
given day, RuFaS first calculates two **shape parameters** and the
**fraction of potential heat units** accumulated. Then, the **optimal
leaf area fraction** is calculated as follows:

.. math::

    A_{\text{leaf, opt}} = \frac{h}{h+exp(l_{\text{1}}-l_{\text{2}}\times h)}

where :math:`A_{\text{leaf, opt}}` is the optimal leaf area fraction on
a given day (``optimal_leaf_area_fraction``), :math:`l_{\text{1}}` is
the first of two shape parameters (``_lai_shapes``),
:math:`l_{\text{2}}` is the second shape parameter, and :math:`h` is the
fraction of potential heat units accumulated by the plant on a given day
(``heat_fraction``).

**Canopy height** represents the canopy height on a given day, in
meters, and is calculated using the following equation:

.. math::

    h_{\text{c}} = h_{\text{c,max}}\times \sqrt{A_{\text{leaf,opt}}}     

where :math:`h_{\text{c}}` is the canopy height (``canopy_height``),
:math:`h_{\text{c,max}}` is the maximum canopy height
(``max_canopy_height``), and :math:`A_{\text{leaf,opt}}` is the optimal
leaf area fraction on a given day (``optimal_leaf_area_fraction``). Once
:math:`h_{\text{c,max}}` is reached, :math:`h_{\text{c}}` remains
constant.

The **maximum leaf area change** calculates the maximum or potential
leaf area added during the day using the following equation:

.. math::

    A_{\text{leaf,pot}} = (A_{\text{leaf, opt}}-A_{\text{leaf, opt i-1}}) \times A_{\text{leaf, max}} \times (1-exp(5\times (A_{\text{leaf, i-1}}-A_{\text{leaf, max}})))

where :math:`A_{\text{leaf, pot}}` is the potential leaf area added on a
given day (``maximum_leaf_area_change``), :math:`A_{\text{leaf, opt}}`
is the optimal leaf area fraction on a given day
(``optimal_leaf_area_fraction``), :math:`A_{\text{leaf, opt i-1}}` is
the optimal leaf area fraction of the previous day
(``previous_optimal_leaf_area_fraction``), :math:`A_{\text{leaf, max}}`
is the maximum leaf area index achievable by the plant
(``max_leaf_area_index``), and :math:`A_{\text{leaf, 
i-1}}` is the leaf area index of the previous day
(``previous_leaf_area``).

The **actual leaf area added** on a given day is based upon the
**maximum leaf area change** on a given day and an adjustment for plant
stress, according to:

.. math::

    A_{\text{leaf, act}} = A_{\text{leaf, pot}} \times \sqrt{\gamma_\text{reg}}      

where :math:`A_{\text{leaf, act}}` is the actual leaf area added on a
given day (``actual_leaf_area_added``), :math:`A_{\text{leaf, pot}}` is
the potential leaf area added on a given day
(``maximum_leaf_area_change``), and :math:`\gamma_\text{reg}` is the
plant growth factor [0.0-1.0] (``growth_factor``).

When **senescence** starts, *LAI* is calculated as follows:

.. math::

    A_{\text{leaf, i}} = A_{\text{leaf, max}} \times \frac {(1-h)}{(1-h_{\text{sen}})}

where :math:`A_{\text{leaf, i}}` is the leaf area index on a given day
(``leaf_area_index``), :math:`A_{\text{leaf, max}}` is the maximum leaf
area index achievable by the plant (``max_leaf_area_index``), :math:`h`
is the fraction of potential heat units accumulated by the plant on a
given day (``heat_fraction``), and :math:`h_{\text{sen}}` is the
fraction of potential heat units at which senescence begins
(``senescent_heat_fraction``).

Finally, the **leaf area index** on a given day is calculated as:

.. math::

    A_{\text{leaf, i}} = A_{\text{leaf, act}} + A_{\text{leaf, i-1}}

where :math:`A_{\text{leaf, i}}` is the leaf area index on a given day
(``leaf_area_index``), :math:`A_{\text{leaf, act}}` is the actual leaf
area added on a given day (``actual_leaf_area_added``), and
:math:`A_{\text{leaf, i-1}}` is the leaf area index of the previous day
(``previous_leaf_area``).

--------------

**References**: this module is based upon the “Canopy Cover and Crop”
and “Actual Growth” sections of the
`SWAT <https://swat.tamu.edu/media/99192/swat2009-theory.pdf>`__ model
(5:2.1.2, 5:3.2).
