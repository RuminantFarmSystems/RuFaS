These files are from Joe and his work conducting sensitivity analysis on the Animal module (uncleaned).

Also from Joe:

https://salib.readthedocs.io/en/latest/index.html
https://waterprogramming.wordpress.com/2013/08/05/running-sobol-sensitivity-analysis-using-salib/
http://keyboardscientist.weebly.com/blog/sensitivity-analysis-with-salib
https://notebook.community/locie/locie_notebook/misc/Sensitivity_analysis
https://github.com/SALib/SALib/issues/195
https://github.com/SALib/SALib/issues/102
The documentation is pretty good, and those two blogs were helpful in seeing how others have used it. 
Likewise there's a lot of issues to pore through, but those two were ones I had bookmarked for some useful 
details/perspective.

Also a book (Saltelli_Full.pdf), and two script (Saloop_v3.py, Saloop_generate_thefiles_basiclog.py): they're 
the in-progress things I was working on leading up to the RUFAS meeting, so they're far from finished - but 
you can see in the "generate the files" script how I prepped the analysis, to then run it in the SALoop file, 
where the JSONs were all pre-generated, and one could easily run the whole analysis (or sections, e.g. 
analyses X-X, if you run it on multiple PCs/VMs). The loop shows a few different ways to run it in parallel, 
with varying success

# From my own exploring
This header of SAlib's documentation is very helpful: https://salib.readthedocs.io/en/latest/basics.html#another-example

https://waterprogramming.wordpress.com/2014/02/11/extensions-of-salib-for-more-complex-sensitivity-analyses/

This compares methods http://www.ibpsa.org/proceedings/BS2019/BS2019_210209.pdf

# Morris method

Based on Morris (1991), it appears that this method (perhaps all SA?) assume that, given a set of input, the output is
always the same (i.e., deterministic and non-stochastic): "... a computational model is viewed as a representation of a 
function that pro-duces unique values of outputs when executed for specific values of inputs" and "... Since model outputs 
do not contain random error, the well-known inefficiencies of estimation based on linear-models analyses of noisy data 
from one-factor-at-a-time plans are not an issue here". This indicates that any stochastic output will need additional
consideration. https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=150efe8feb764de271a01dc261f7a74b3ccb9187
One idea would be to use a statistical experiment (e.g., regression).

There is not explicit test of interactions in this method but a large variance "indicates an input whose influence is highly 
dependent on the values of the inputs - that is, one involved in interactions or whose effect is nonlinear."

# FAST

https://www.researchgate.net/profile/Andrea-Saltelli-2/publication/243587760_A_Quantitative_Model-Independent_Method_for_Global_Sensitivity_Analysis_of_Model_Output/links/00b49536889b064f12000000/A-Quantitative-Model-Independent-Method-for-Global-Sensitivity-Analysis-of-Model-Output.pdf