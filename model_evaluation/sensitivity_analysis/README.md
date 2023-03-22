# Sensitivity Analyses for RuFaS

Authors: Clay J. Morrow <!-- TODO: Joe, Varma, and others, please add your name here when you make changes/additions -->   
Date Created: 17 Mar 2023   
Last Updated: 22 Mar 2023 <!-- NOTE: please remember to change this date when editing this file --> 

__Contents:__
1. [Introduction](#1-introduction)
2. [Summary of RuFaS Sensitivity Analyses](#2-summary-of-rufas-sensitivity-analyses)  
   a. [Parallelization](#parallelization)   
   b. [Types of SA](#types-of-sa)
3. [References and Links](#3-references-and-links)  
   a. [Primary Sources](#primary-sources)  
   b. [SALib](#salib)

---

## 1. Introduction

The purpose of this document is to guide the developers of RuFaS in conducting sensitivity analyses (SA). These methods
can be applied to either 1) The entire RuFaS model or 2) any submodule, with minimal work on the user's part. 
Joe Waddell began this process, by finding the relevant packages and writing some scripts to implement SA for the full 
RuFaS module. My goal is to build on his work to write a module that generalises the SA methods and allows them to be 
applied to any python function/module. 

The [References and Links](#references-and-links) section provides both the primary and secondary sources that we used
to create these methods. 
----

## 2. Summary of RUFAS Sensitivity Analyses

Broadly speaking, a global sensitivity analysis (SA) simply aims to answer the questions, "which parameters have the 
largest impact on the results of a model".

Within the [generalized_sensitivity.py](generalized_sensitivity.py) file, is the class `SensitivityAnalysis`. This 
class executes a standardized procedure for conducting SA. The user needs to provide an objective function, names of
parameters of that function to be analyzed, upper and lower bounds for each parameter, and some additional 
specifications about how the SA should be conducted. 

Currently, this class supports 3 methods for conducting SA. These methods (Sobol, FAST, and Morris' method) are
further discussed below in [Types of SA](#types-of-sa). 

### Parallelization

Because RuFaS takes a long time to run and will need to be executed many times (thousands), it will be important to
parallelize its execution. Luckily the package that we are using to perform SA 
[SALib](https://salib.readthedocs.io/en/latest/) (additional links and description provided in the 
[SALib Section](#salib) below) already utilizes parallel processing. We leverage that functionality in our SA class.

### Types of SA

In this document, we'll consider 3 methods of global sensitivity analysis: 1) Morris' method, 2) the extended FAST
method, and 2) the Sobol method. They each have their advantages and disadvantages. Generally speaking, Sobol is
the most accurate but is the slowest by far. The other methods are fast and accurate but can't quantify
interactive effects (Sobol can quantify 2nd order).

###### Morris' method

Based on Morris (1991), it appears that this method (perhaps all SA?) assume that, given a set of input, the output is
always the same (i.e., deterministic and non-stochastic): "... a computational model is viewed as a representation of a 
function that produces unique values of outputs when executed for specific values of inputs" and "... Since model 
outputs do not contain random error, the well-known inefficiencies of estimation based on linear-models analyses of
noisy data from one-factor-at-a-time plans are not an issue here". This indicates that any stochastic output will 
need additional consideration. One idea would be to use statistical methods (e.g., regression), but Pang et al (2019)
demonstrates that statistical SA tools may not perform well.

There is no explicit test of interactions in this method but a large variance "indicates an input whose influence is 
highly dependent on the values of the inputs - that is, one involved in interactions or whose effect is nonlinear."

###### FAST (Extended)
<!-- TODO: add summary of FAST method -->

###### Sobol method
<!-- TODO: add summary of Sobol Method -->

----

## 3. References and Links

This section contains primary and secondary sources used to evaluate SA methods.

### Primary sources

These are the primary sources used for researching the best methods and practices for conducting SA: 

* [*Sensitivity Analyses in Practice* book (Saltelli 2004)](
  http://www.andreasaltelli.eu/file/repository/SALTELLI_2004_Sensitivity_Analysis_in_Practice.pdf
  )
* [Original article on Morris' method (Morris 1991)](
  https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=150efe8feb764de271a01dc261f7a74b3ccb9187
  )
* [Study comparing SA methods (Pang et al. 2019)](http://www.ibpsa.org/proceedings/BS2019/BS2019_210209.pdf)
* [Extended FAST method (Saltelli et  al. 2012)](
  https://www.researchgate.net/profile/Andrea-Saltelli-2/publication/243587760_A_Quantitative_Model-Independent_Method_for_Global_Sensitivity_Analysis_of_Model_Output/links/00b49536889b064f12000000/A-Quantitative-Model-Independent-Method-for-Global-Sensitivity-Analysis-of-Model-Output.pdf
  )
 
### SALib

SALib is the python package that we will use for conducting sensitivity analyses. It is well-supported and implemented.
Here are some relevant links to help get started with this package:

* [GitHub page](https://github.com/SALib)
* [Python doc page](https://salib.readthedocs.io/en/latest/index.html)
* [Author blog](https://waterprogramming.wordpress.com/2013/08/05/running-sobol-sensitivity-analysis-using-salib/)
* [Author post about package extension](
  https://waterprogramming.wordpress.com/2014/02/11/extensions-of-salib-for-more-complex-sensitivity-analyses/
  )
* [Applied example 1](http://keyboardscientist.weebly.com/blog/sensitivity-analysis-with-salib)
* [Applied example 2](https://notebook.community/locie/locie_notebook/misc/Sensitivity_analysis)
* [Package example using a variable and parameters](https://salib.readthedocs.io/en/latest/basics.html#another-example)
* [Categorical data GitHub Issue](https://github.com/SALib/SALib/issues/195)
* [Negative sobol index GitHub Issues](https://github.com/SALib/SALib/issues/102)
* [How to wrap existing models](https://salib.readthedocs.io/en/latest/user_guide/wrappers.html)

The documentation for the package pretty good, and the two blogs are helpful at seeing how others have used it. 

NOTE: SALIb has parallel and distributed processing available out of box. It DOES NOT work in pycharm, but DOES work
with all other methods of running python code. It is a known issue that the python interactive console cannot execute
code from the `multiprocessing` package (it has been 4 years, so I doubt it will ever get patched): [Link](
https://youtrack.jetbrains.com/issue/PY-36151?_ga=2.6010288.221937295.1679330535-2071016451.1670387953&_gl=1*1qr3jl1*_ga*MjA3MTAxNjQ1MS4xNjcwMzg3OTUz*_ga_9J976DJZ68*MTY3OTMzMDUzNC4xMS4wLjE2NzkzMzA1NDMuMC4wLjA.
)

