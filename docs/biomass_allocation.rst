**Biomass allocation**
~~~~~~~~~~~~~~~~~~~~~~

The ``BiomassAllocation`` class manages the crop biomass accumulation
through the photosynthesis process and its partition between above and
below ground organs during the growing season.

The central method, ``allocate_biomass()``, calls on the
**photosynthesize** and **partition biomass** methods to make daily
updates on crop biomass allocation.

**Photosynthesize** converts the incoming solar radiation into plant
biomass. First, potential plant growth is modeled by simulating
**intercepted radiation** and **maximum biomass growth**. Then, the
latter is adjusted by plant stress to calculate the **biomass growth**
on a given day and the **biomass** accumulated to date.

**Intercepted radiation** represents the amount of daily
photosynthetically active radiation intercepted by the leaf area of the
crop according to:

.. math::

    R_{\text{int}} = 0.5\times R_{\text{inc}}\times (1-exp(-k_{\text{l}}\times A_{\text{leaf, i}}))

where :math:`R_{\text{int}}` is the photosynthetically active radiation
intercepted (``usable_light``), :math:`R_{\text{inc}}` is the total
solar radiation available on a given day (``incoming_solar_radiation``),
:math:`k_{\text{l}}` is the light extinction coefficient
(``light_extinction``), and :math:`A_{\text{leaf, i}}` is the leaf area
index on a given day (``leaf_area_index``).

**Maximum biomass growth** calculates the potential or upper-limit to
total biomass increase on a given day that results from the
**intercepted radiation** and the crop-specific radiation-use
efficiency, which is the amount of dry biomass produced per unit of
intercepted solar radiation. It is calculated using the following
equation:

.. math::

    Growth_{\text{max}} = R_{\text{int}}\times Eff_{\text{light}}

where :math:`Growth_{\text{max}}` is the potential biomass growth on a
given day (``biomass_growth_max``), :math:`R_{\text{int}}` is the
photosynthetically active radiation intercepted (``usable_light``), and
:math:`Eff_{\text{light}}` is the radiation-use efficiency of the crop
(``light_use_efficiency``).

The **biomass growth** on a given day represents the actual biomass
growth once **maximum biomass growth** is adjusted according to the
daily plant growth factor:

.. math::

    Growth_{\text{i}} = Growth_{\text{max}}\times \gamma_{\text{reg}}

where :math:`G_{\text{i}}` is the actual biomass growth on a given day
(``biomass_growth``), :math:`G_{\text{max}}` is the potential biomass
growth on a given day (``biomass_growth_max``), and
:math:`\gamma_{\text{reg}}` is the plant growth factor [0.0-1.0]
(``growth_factor``).

Then, **biomass**, which represents the total plant biomass on a given
day, is calculated based upon the sum of the previously estimated
**biomass growth**:

.. math::

    Biom_{\text{tot}} = \sum_{i=1}^{d} Growth_{\text{i}}

where :math:`Biom_{\text{tot}}` is the total plant biomass on a given
day (``biomass``) and :math:`Growth_{\text{i}}` is the actual biomass
growth on a given day (``biomass_growth``).

The **partition biomass** method divides **biomass** into above and
below ground portions. The **above ground biomass** is calculated as
follows:

.. math::

    Biom_{\text{ag}} = Biom_{\text{tot}}\times (1-r)

where :math:`Biom_{\text{ag}}` is above ground biomass
(``above_ground_biomass``), :math:`Biom_{\text{tot}}` is the total plant
biomass on a given day (``biomass``), and :math:`r` is the fraction of
total biomass partitioned to roots on a given day (``root_fraction``).

Finally, **below ground biomass** represents the biomass partitioned to
roots and is calculated according to:

.. math::

    Biom_{\text{bg}} = Biom_{\text{tot}}\times r

where :math:`Biom_{\text{bg}}` is below ground biomass
(``below_ground_biomass``), :math:`Biom_{\text{tot}}` is the total plant
biomass on a given day (``biomass``), and :math:`r` is the fraction of
total biomass partitioned to roots on a given day (``root_fraction``).

--------------

**References**: this module is based upon the “Biomass Production” and
“Crop Yield” sections of the
`SWAT <https://swat.tamu.edu/media/99192/swat2009-theory.pdf>`__ model
(5:2.1.1, 5:2.4).
