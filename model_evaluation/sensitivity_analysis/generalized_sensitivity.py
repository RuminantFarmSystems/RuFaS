"""
This module will contain the functions needed to apply global sensitivity analyses to the generalized case.

The workhorse of this module is the SALib python package (Herman et al. 2023): https://salib.readthedocs.io/en/latest/

This module uses functional programming instead of object-oriented. This may change down the line.
"""

from SALib import ProblemSpec
from SALib.sample import sobol as sobol_sampler, morris as morris_sampler, fast_sampler
from SALib.analyze import sobol, morris, fast

from typing import List, Tuple, Optional, Callable
from enum import Enum
import numpy
from matplotlib import pyplot


class SupportedSensitivityMethods(Enum):
    SOBOL = "sobol"
    FAST = "fast"
    MORRIS = "morris"
    FAST_SOBOL = "fs"  # need to figure out how to run SOBOL on reduced set determined by FAST results
    MORRIS_SOBOL = "ms"  # same here


class SensitivityAnalysis:
    """Conduct sensitivity analysis on an objective function over a set of parameters.

    Parameters
    ----------
    fun : function
        The objective function for which the sensitivity analysis should be conducted.
    pars : list[str]
        Names of the parameters over which the sensitivity analysis will be conducted.
    bounds : list[tuple(float, float)]
        The lower, and upper bounds, respectively, of each parameter.
    method: str
        The type of sensitivity analysis to be conducted. Current supported options are "sobol" for Sobol global SA,
        "fast" for the FAST method, and "fs" for a combination of FAST and SOBOL (see details).
    # groups : list[str], optional
    #     The groups (contrasts) that each parameter belongs to for grouped SA.
    outputs : list[str], optional
        The names of the output variables. If present, should have a length equal to the number of columns
        returned by fun for a single set of parameters.

    Returns
    -------

    Raises
    ------
    ValueError
        if `pars` and `bounds` aren't the same length;
        if `groups` is given and differs in length from `pars`
    """
    def __init__(self, fun: Callable, pars: List[str], bounds: List[Tuple[float, float]], method: str = "fs",
                 groups: Optional[List[str]] = None, outputs: Optional[List[str]] = None, sample_n: int = 2**10,
                 *args, **kwargs):

        self._check_inputs(pars, bounds, groups)

        self.objective_function = fun
        self.parameter_names = pars
        self.parameter_bounds = bounds
        self.sensitivity_method = SupportedSensitivityMethods(method)
        self.parameter_groups = groups
        self.output_names = outputs
        self.additional_args = args
        self.additional_kwargs = kwargs
        self.sample_n = sample_n

        self.problem = self.define_problem()
        self.original_problem = None


    @staticmethod
    def _check_inputs(pars: List[str], bounds: List[Tuple[float, float]], groups: Optional[List[str]] = None):
        if len(pars) != len(bounds):
            raise ValueError("pars and bounds must be the same length")
        if groups is not None and len(groups) != len(pars):
            raise ValueError("groups must be the same length as pars")

    def define_problem(self) -> ProblemSpec:
        return ProblemSpec(names=self.parameter_names, bounds=self.parameter_bounds, groups=self.parameter_groups,
                           outputs=self.output_names)

    def sample_parameter_space(self, *args, **kwargs):
        if self.sensitivity_method == SupportedSensitivityMethods.FAST:
            self.problem.sample(func=fast_sampler.sample, N=self.sample_n, *args, **kwargs)
        if self.sensitivity_method == SupportedSensitivityMethods.SOBOL:
            self.problem.sample(func=sobol_sampler.sample, N=self.sample_n, *args, **kwargs)
        if self.sensitivity_method == SupportedSensitivityMethods.MORRIS:
            self.problem.sample(func=morris_sampler.sample, N=self.sample_n, *args, **kwargs)

    # TODO add options for the parallelized versions of `evaluate` and `analyze`.
    def evaluate_model(self):
        self.problem.evaluate(func=self.objective_function, *self.additional_args, **self.additional_kwargs)

    def analyze_model(self, *args, **kwargs):
        if self.sensitivity_method == SupportedSensitivityMethods.FAST:
            self.problem.analyze(fast.analyze, *args, **kwargs)
        if self.sensitivity_method == SupportedSensitivityMethods.SOBOL:
            self.problem.analyze(sobol.analyze, *args, **kwargs)
        if self.sensitivity_method == SupportedSensitivityMethods.MORRIS:
            self.problem.analyze(morris.analyze, *args, **kwargs)

    def perform_sensitivity_analysis(self):
        original_method = self.sensitivity_method

        if original_method == SupportedSensitivityMethods.FAST_SOBOL:
            self.sensitivity_method = SupportedSensitivityMethods.FAST
        if original_method == SupportedSensitivityMethods.MORRIS_SOBOL:
            self.sensitivity_method = SupportedSensitivityMethods.MORRIS

        self.sample_parameter_space()
        self.evaluate_model()
        self.analyze_model()

        # Perform second analysis for compound methods
        if original_method in (SupportedSensitivityMethods.FAST_SOBOL, SupportedSensitivityMethods.MORRIS_SOBOL):

            self.sensitivity_method = SupportedSensitivityMethods.SOBOL
            self.original_problem = self.problem

            self.define_followup_problem()

            self.sample_parameter_space()
            self.evaluate_model()
            self.analyze_model()

            self.sensitivity_method = original_method

    def define_followup_problem(self, cutoff: Optional[float], keep_n: Optional[int]):
        """if a cutoff is given, all parameters with total effects greater than this value will be considered for the
        second analysis

        if keep_n is specified, the top n parameters equal to this value will be considered for the analysis

        if both cutoff and keep_n is given, a maximum of keep_n parameters that fall below the cutoff value will be
        considered for the second analysis

        if neither cutoff nor keep_n is given, then all parameters with significant effects (ST-ST_conf > 0) will be
        considered for the second analysis
        """
        pass







# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    from SALib.test_functions import Ishigami
    sens = SensitivityAnalysis(fun=Ishigami.evaluate, pars=["x1", "x2", "x3"], bounds=[(-numpy.pi, numpy.pi)]*3,
                               groups=None, outputs=["response"], method="sobol")
    sens.define_problem()
    print(dict(sens.problem))
    sens.sample_parameter_space()
    print(sens.problem.samples)
    sens.evaluate_model()
    print(sens.problem.results)
    sens.analyze_model()
    print(sens.problem.analysis)
    # sens.evaluate_model()
    sens.problem.plot()
    pyplot.show()
    #
    sens.problem.heatmap()
    pyplot.show()
