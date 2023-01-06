### Root development
The main function is called **`develop_roots()`** and it is initialized with:
* `heat_fraction`: 
* max_root_depth: 
* is_perennial: 
* root_depth:  
* root_fraction: 

The function updates the **root fraction** and **root depth** attributes. 

**Root fraction** is updated as a function of plant maturity using heat fraction as a proxy. It returns the daily fraction of a plant's biomass comprised of roots [0.4-0.2] using the equations:
```math
root_fraction = 0.4 - 0.2 * heat_fraction             if heat_fraction < 2.0

root_fraction = 0                                     if heat_fraction ≥ 2.0
```

where **heat fraction** is the fraction of potential heat units accumulated for the plant 
on a given day in the growing season. 

**Root depth** is updated differently depending upon whether the plant is perennial. It is assumed that perennials have roots down to the maximum rooting depth. For annuals, root depth varies linearly from 10 mm at the beginning of the growing season to the maximum rooting depth at heat fraction = 0.40 using the equations: 
```math
root_depth = 2.5 * heat_fraction * max_depth          if heat_fraction ≤ 0.4

root_depth = max_depth                                if heat_fraction > 0.4
```



