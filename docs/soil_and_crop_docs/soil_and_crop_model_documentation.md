---
title: "RuFaS Soil and Crop 'pseudocode' Rework"
author: "Clay J. Morrow (morrowcj@outlook.com)"
date: "30 September, 2022"
output: 
  html_document: 
    keep_md: yes
    toc: true
    toc_float: true
    toc_depth: 4
---



## Introduction

This document will serve as the model and algorithm documentation for the soil
and crop submodule(s) of RuFaS. It is meant to replace the "pseudocode" files
(`pseudocode_crop` and `pseudocode_soil` google docs). I will update this file
periodically, as I work through the code to refactor and test the individual
submodules.

Equations are written using latex formatting. Components of each equation are 
defined underneath them and parameters are matched to their corresponding python
variables/attributes with code notation: e.g., $x$ is the "x" parameter (`param_x`)

In general, the steps happen **in the order that they appear in this document**.


## Pre-Growth

**Docs Under Construction**


## G: Daily Growth

This section describes the daily routines that simulated plants are subject to
while they are growing (i.e., if `BaseCrop.growing` is `True`). 


### G.1 update heat units

(`heat_units.update_all()`) 
**Docs Under Construction**


### G.2 root development 

(`root_development.udate_all()`) 
**Docs Under Construction**


### G.3 nitrogen uptake/fixation

Nitrogen is incorporated into the plant, during a day's growth, with the 
following routines (executed by `nitrogen_uptake.reallocate_nitrogen()`):


#### G.3.1 ideal nitrogen fraction

The Ideal nitrogen fraction is the proportion of a plant's biomass comprising 
nitrogen at the end of the day, under ideal circumstances. It is calculated and 
updated by `update_nitrogen_fraction()` according to 

$$n_d = (n_{ex,\ 1} - n_{ex,\ 3}) \times \bigg(1-\frac{h_d}{h_d + e^{(s_1 + s_2 \times h_d)}}\bigg)$$
where

* $n_d$: ideal nitrogen fraction (`BaseCrop.fr_N`) for the day $d$ 
* $h_d$: proportion of maximum PHU (potential heat units) accumulated to date
(`BaseCrop.prev_fr_PHU`) 
**Note: need to double check that it shouldn't be `fr_PHU` instead** 
* $n_{ex,\ 1}$: expected nitrogen fraction at emergence (`BaseCrop.fr_n1`)
* $n_{ex,\ 3}$: expected nitrogen fraction at maturity (`BaseCrop.fr_n3`)
* $s_1$ and $s_2$: crop-specific shape parameters 

The shape parameters are calculated with

$$s_2 = \frac{ \ln\big(\frac{h_{50}} {1-A} - h_{50}\big) - \ln\big( \frac{h_{100}} {1-B} - h_{100}\big) } {h_{100} - h_{50}}$$

$$s_1 = \ln\bigg(\frac{h_{50}} {1-A} - h_{50}\bigg) + s_2 \times h_{50}$$

where 

* $A = \frac{n_2 - n_3}{n_1 - n_3}$ and $B = \frac{n_{3^*} - n_3}{n_1 - n_3}$  
* $n_{ex,\ 2}$: expected nitrogen fraction after emergence (`BaseCrop.fr_n2`)  
* $n_{ex,\ 3^*}$, expected nitrogen fraction **near** emergence (`BaseCrop.fr_n3ish`)  
* $h_{50}$: proportion of total PHU accumulated at 50% maturity 
(`BaseCrop.fr_PHU_50`)  
* $h_{100}$: proportion of total PHU accumulated at maturity
(`BaseCrop.fr_PHU_100`)

Note that, if the plant's starting biomass (`BaseCrop.biomass_actual`) is 0, 
then the nitrogen fraction is constrained to 0: $n_d = 0$.


#### G.3.2 optimal nitrogen

The optimal amount of nitrogen that a plant has stored on a given day is 
calculated and updated with `update_optimal_nitrogen()`, according to 

$$N_{d,\ opt} = n_d \times M_{d-1}$$
where 

* $N_{d,\ opt}$: optimal total nitrogen mass (`BaseCrop.bio_N_opt`) for the day $d$ 
* $n_d$: ideal nitrogen fraction for the day (`BaseCrop.fr_N`)
* $M_{d-1}$: plant biomass (`BaseCrop.biomass_actual`) at the end of the 
previous day


#### G.3.3 potential uptake

The maximum amount of nitrogen that a plant can uptake is calculated and updated by `update_potential_nitrogen_uptake()` according to

$$N_{d,\ max} = \min\{\Delta_{d,opt},\ \delta_{d,opt}\}$$

where 

* $N_{d,\ max}$: potential nitrogen uptake (`BaseCrop.N_up`) for the day
* $\Delta_{d,opt} = N_{d,\ opt} - N_{d-1}$: 
  - $N_{d,\ opt}$: optimal nitrogen (`BaseCrop.bio_N_opt`) for the day 
  - $N_{d-1}$: nitrogen biomass (`BaseCrop.bio_N`) for the previous day
* $\delta_{d,opt} = 4\times G_{d,\ max} \times n_{exp,\ 3}$:
  - $G_{d,\ max}$: maximum biomass growth possible for the day
  (`BaseCrop.d_biomass_max`) **Note: the biomass routines are conducted after the nitrogen routines. So how is `d_biomass_max` determined for the current day?**
  - $n_3$: expected nitrogen fraction at maturity

Note that $N_{d, max}$ is constrained to 0 at the lower bound.


#### G.3.4 actual uptake

(`uptake_nitrogen()`)
uptake nitrogen from the soil


#### G.3.5 nitrogen fixation

(`fix_nitrogen()`)
fix nitrogen from the atmosphere 


#### G.3.6 nitrogen storage

(`store_nitrogen_biomass()`)
store the newly acquired nitrogen as biomass


### G.4 uptake phosphorus 

(`phosphorus_uptake.update_all()`)
**Docs Under Construction**


### G.5 update growth constraints 

("`growth_constrains.update_all()`)
**Docs Under Construction**


### G.6 update leaf area index 

(`leaf_area_index.update_all()`)
**Docs Under Construction**


### G.7 allocate resources to biomass 

(`biomass.allocate_biomass()`)


## Post-growth

**Docs Under Construction**

