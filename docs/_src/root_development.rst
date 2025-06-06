**Root development**
~~~~~~~~~~~~~~~~~~~~

The ``RootDevelopment`` class handles the root development of the crop
on a daily basis. The main method that carries out the processes
involved is ``develop_roots()``, which calls on the **root fraction**
and **root depth** methods to provide a daily update on the status of
crop roots.

**Root fraction** is the daily fraction of total plant biomass comprised
of roots and is updated as a function of plant maturity using heat
fraction as a proxy:

.. math::

    r = 
   \begin{cases}
        0.4 - 0.2 \times h        & \text{if } h < 2.0 \\
        0                         & \text{otherwise}
   \end{cases}

where :math:`r` is the fraction of total biomass partitioned to roots on
a given day [0.2-0.4] (``root_fraction``), and :math:`h` is the fraction
of potential heat units accumulated by the plant on a given day
(``heat_fraction``).

**Root depth** represents the depth of root development in the soil on a
given day. It is updated differently depending upon whether the plant is
perennial. It is assumed that perennials have roots down to the maximum
rooting depth in the soil. For annuals, root depth varies according to:

.. math::

    r_{\text{depth}} = 
   \begin{cases}
        2.5 \times h \times r_{\text{depth, max}}       & \text{if } h ≤ 0.4 \\
        r_{\text{depth, max}}                           & \text{otherwise}
   \end{cases}

where :math:`r_{\text{depth}}` is the depth of root development on a
given day (``root_depth``), :math:`r_{\text{depth, max}}` is the maximum
depth for root development in the soil (``max_root_depth``), and
:math:`h` is the fraction of potential heat units accumulated by the
plant on a given day (``heat_fraction``).

--------------

**References**: this module is based upon the “Root Development” section
of the `SWAT <https://swat.tamu.edu/media/99192/swat2009-theory.pdf>`__
model (5:2.1.3).
