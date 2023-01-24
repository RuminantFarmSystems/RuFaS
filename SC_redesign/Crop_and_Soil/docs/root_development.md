### Root development
The `RootDevelopment` class handles development of crop roots on a daily basis. 
The main function that carries out root development processes is called `develop_roots()` 
which updates the `root_fraction` and `root_depth` attributes.

`root_fraction` is the fraction of total biomass partitioned to roots on a given day. 
It is updated as a function of plant maturity using `heat_fraction` as a proxy. 
It returns the daily fraction of a plant's biomass comprised of roots [0.4-0.2] 
using the equations:

```math
  $$ r = 
  \begin{cases}
     0.4 - 0.2 \times h        & \text{if } h < 2.0 \\
     0                         & \text{otherwise}
  \end{cases}
$$
```
where $r$ is `root_fraction` and $h$ is `heat_fraction` (i.e., the fraction of potential heat 
units accumulated for the plant on a given day).

`root_depth` represents the depth of root development in the soil on a given day. It is 
updated differently depending upon whether the plant is perennial or annual. It is assumed that 
perennials have roots down to the maximum rooting depth (`max_root_depth`; maximum depth for root development 
in the soil). <!-- TODO: this seems like a bad assumption, especially during the first year of growth --> 
For annuals, `root_depth` varies linearly from 10 mm at the beginning of the growing 
season to the maximum rooting depth at `heat_fraction = 0.40` using the equations: 

```math
  $$ d = 
  \begin{cases}
     2.5 \times h \times d_\text{max}       & \text{if } h ≤ 0.4 \\
     d_\text{max}                           & \text{otherwise}
  \end{cases}
$$
```

where $d% is `root_depth`, $d_\text{max}$ is `max_root_depth` and $h$ is `heat_fraction`.

---
**References**: this module is based upon the "Root Development" section of the [SWAT][1]  model (5:2.1.3)

[1]:https://swat.tamu.edu/media/99192/swat2009-theory.pdf

