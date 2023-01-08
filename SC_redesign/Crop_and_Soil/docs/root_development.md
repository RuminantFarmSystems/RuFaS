### Root development
The `RootDevelopment` class handles development of crop roots on a daily basis. The main function that carries out root development processes is called `develop_roots()` and it is initialized with:

* `heat_fraction`: fraction of potential heat units accumulated
for the plant on a given day (unitless)
* `max_root_depth`: maximum depth for root development in the soil (mm)
* `is_perennial`: plants that maintain their root systems throughout the year, becoming dormant in the winter and resuming growth when average daily air temperature exceeds the
 base temperature required (unitless)
* `root_depth`: depth of root development in the soil on a given day (mm)
* `root_fraction`: fraction of total biomass partitioned to roots on a given day (unitless)

The function updates the **root fraction** and **root depth** attributes. 

**Root fraction** is updated as a function of plant maturity using heat fraction as a proxy. It returns the daily fraction of a plant's biomass comprised of roots [0.4-0.2] using the equations:

$$ r = 
  \begin{cases}
     0.4 - 0.2 \times h & \text{if } h < 2.0 \\
     0 & \text{else}
  \end{cases}
$$

where $r$ is `root_fraction` and $h$ is `heat_fraction`.

**Root depth** is updated differently depending upon whether the plant is perennial. It is assumed that perennials have roots down to the maximum rooting depth. For annuals, root depth varies linearly from 10 mm at the beginning of the growing season to the maximum rooting depth at heat fraction = 0.40 using the equations: 

$$ d = 
  \begin{cases}
    2.5 \times h \times d_{m} & \text{if } h \leq 0.4 \\
    d_{m} & \text{else}
  \end{cases}
$$


where $d$ is `root_depth`, $d_m$ is `max_root_depth` and $h$ is `heat_fraction`.

---
**References**: this module is based upon the "Root Development" section of the [SWAT][1]  model (5:2.1.3)

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf


