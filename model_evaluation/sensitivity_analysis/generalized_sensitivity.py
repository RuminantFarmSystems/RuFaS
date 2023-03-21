"""
This module will contain the classes and methods needed to apply global sensitivity analyses to any objective function.

The workhorse of this module is the SALib python package (Herman et al. 2023): https://salib.readthedocs.io/en/latest/
"""
from __future__ import annotations
import numpy as np
from SALib import ProblemSpec
from SALib.sample import sobol as sobol_sampler, morris as morris_sampler, fast_sampler
from SALib.analyze import sobol, morris, fast

from typing import List, Tuple, Optional, Callable, Dict
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
                 n_cores: int = 1, *args, **kwargs):

        self._check_inputs(pars, bounds, groups)

        self.objective_function: Callable = fun
        self.parameter_names: List[str] = pars
        self.parameter_bounds: List[Tuple[float, float]] = bounds
        self.sensitivity_method: SupportedSensitivityMethods = SupportedSensitivityMethods(method)
        self.parameter_groups: Optional[List[str]] = groups
        self.output_names: Optional[List[str]] = outputs
        self.sample_n: int = sample_n
        self.parallel_processors: int = n_cores  # TODO: not yet implemented
        self.additional_args: Tuple = args
        self.additional_kwargs: Dict = kwargs

        self.problem = self.define_problem()
        self.original_problem: Optional[ProblemSpec] = None

    @staticmethod
    def make_and_run(fun: Callable, pars: List[str], bounds: List[Tuple[float, float]], method: str = "fs",
                     groups: Optional[List[str]] = None, outputs: Optional[List[str]] = None, sample_n: int = 2**10,
                     n_cores: int = 1, *args, **kwargs) -> SensitivityAnalysis:
        obj = SensitivityAnalysis(fun, pars, bounds, method, groups, outputs, sample_n, n_cores, int, *args, **kwargs)
        obj.perform_sensitivity_analysis()
        return obj


    def perform_sensitivity_analysis(self) -> None:
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

            self.problem = self.define_followup_problem()
            self.sample_parameter_space()
            self.evaluate_model()
            self.analyze_model()

            self.sensitivity_method = original_method

    @staticmethod
    def _check_inputs(pars: List[str], bounds: List[Tuple[float, float]], groups: Optional[List[str]] = None) -> None:
        if len(pars) != len(bounds):
            raise ValueError("pars and bounds must be the same length")
        if groups is not None and len(groups) != len(pars):
            raise ValueError("groups must be the same length as pars")

    def define_problem(self) -> ProblemSpec:
        return ProblemSpec(names=self.parameter_names, bounds=self.parameter_bounds, groups=self.parameter_groups,
                           outputs=self.output_names)

    def sample_parameter_space(self, *args, **kwargs) -> None:
        if self.sensitivity_method == SupportedSensitivityMethods.FAST:
            self.problem.sample(func=fast_sampler.sample, N=self.sample_n, *args, **kwargs)
        if self.sensitivity_method == SupportedSensitivityMethods.SOBOL:
            self.problem.sample(func=sobol_sampler.sample, N=self.sample_n, *args, **kwargs)
        if self.sensitivity_method == SupportedSensitivityMethods.MORRIS:
            self.problem.sample(func=morris_sampler.sample, N=self.sample_n, *args, **kwargs)

    # TODO add options for the parallelized versions of `evaluate` and `analyze`.
    def evaluate_model(self) -> None:
        if self.parallel_processors > 1:
            self.problem.evaluate(func=self.objective_function, nprocs=self.parallel_processors,
                                  *self.additional_args, **self.additional_kwargs)
        else:
            self.problem.evaluate(func=self.objective_function, *self.additional_args, **self.additional_kwargs)

    def analyze_model(self, *args, **kwargs) -> None:
        if self.parallel_processors > 1:
            if self.sensitivity_method == SupportedSensitivityMethods.FAST:
                self.problem.analyze(fast.analyze, nprocs=self.parallel_processors, *args, **kwargs)
            if self.sensitivity_method == SupportedSensitivityMethods.SOBOL:
                self.problem.analyze(sobol.analyze, nprocs=self.parallel_processors, *args, **kwargs)
            if self.sensitivity_method == SupportedSensitivityMethods.MORRIS:
                self.problem.analyze(morris.analyze, nprocs=self.parallel_processors, *args, **kwargs)
        else:
            if self.sensitivity_method == SupportedSensitivityMethods.FAST:
                self.problem.analyze(fast.analyze, *args, **kwargs)
            if self.sensitivity_method == SupportedSensitivityMethods.SOBOL:
                self.problem.analyze(sobol.analyze, *args, **kwargs)
            if self.sensitivity_method == SupportedSensitivityMethods.MORRIS:
                self.problem.analyze(morris.analyze, *args, **kwargs)

    def define_followup_problem(self, cutoff: Optional[float] = None, keep_n: Optional[int] = None) -> ProblemSpec:
        """if a cutoff is given, all parameters with total effects greater than this value will be considered for the
        second analysis

        if keep_n is specified, the top n parameters equal to this value will be considered for the analysis

        if both cutoff and keep_n is given, a maximum of keep_n parameters that fall below the cutoff value will be
        considered for the second analysis

        if neither cutoff nor keep_n is given, then all parameters with significant effects (ST-ST_conf > 0) will be
        considered for the second analysis
        """
        # TODO: Note that this method requires that the all the parameters have default values in the function.
        # empty declarations
        total_effects: numpy.array = numpy.empty(1)
        conf_int: numpy.array = numpy.empty(1)
        lower_bound: numpy.array = numpy.empty(1)

        # get important variables
        if "ST" in self.original_problem.analysis.keys(): # Most methods
            total_effects = numpy.array(self.original_problem.analysis["ST"])
            conf_int = numpy.array(self.original_problem.analysis["ST_conf"])
            lower_bound = total_effects - conf_int

        if "mu" in self.original_problem.analysis.keys():  # Morris' method
            total_effects = numpy.array(self.original_problem.analysis["mu"])
            conf_int = numpy.array(self.original_problem.analysis["mu_star_conf"])
            lower_bound = total_effects - conf_int

        # reorder the arrays
        order = total_effects.argsort()
        total_effects = total_effects[order]
        conf_int = conf_int[order]
        pars = numpy.array(self.parameter_names)[order]
        bounds = numpy.array(self.parameter_bounds)[order]
        groups = numpy.array(self.parameter_groups)[order] if self.parameter_groups is not None else None

        # filter the arrays
        if cutoff is not None:
            beat_cutoff = lower_bound > cutoff
            total_effects = total_effects[beat_cutoff]
            conf_int = conf_int[beat_cutoff]
            pars = pars[beat_cutoff]
            bounds = bounds[beat_cutoff]
            groups = groups[beat_cutoff] if groups is not None else None

        # trim the arrays
        if keep_n is not None and keep_n < len(total_effects):
            total_effects = total_effects[:keep_n]
            conf_int = conf_int[:keep_n]
            pars = pars[:keep_n]
            bounds = bounds[:keep_n]
            groups = groups[:keep_n] if groups is not None else None

        return ProblemSpec(names=pars, bounds=bounds, groups=groups, outputs=self.output_names)

    def __str__(self):  # TODO: need to implement this. Formatted output from printing the object
        pass

    def __repr__(self):  # TODO: need to implement this too.
        pass




# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Run Examples
    from SALib.test_functions import Ishigami, oakley2004
    # -- Ishigami function --
    sens = SensitivityAnalysis(Ishigami.evaluate, pars=["x1", "x2", "x3"], bounds=[(-numpy.pi, numpy.pi)]*3,
                               groups=None, outputs=["response"], method="sobol")
    sens.define_problem()
    sens.sample_parameter_space()
    sens.evaluate_model()
    sens.analyze_model()
    # # Uncomment this block to visualize results
    # sens.problem.plot()
    # pyplot.show()

    # -- More complex function (Oakley 2004) --
    weights = numpy.array([[1.0]*5 + [0.1]*5 + [0.01]*5,
                           [0.5]*5 + [0.05]*5 + [0.005]*5,
                           [0.2]*5 + [0.02]*5 + [0.002]*5])
    correlation_matrix = numpy.zeros((15, 15))
    numpy.fill_diagonal(correlation_matrix, 1)
    numpy.random.seed(210)
    for i in range(15):
        for j in range(i+1, 15, 1):
            cor = numpy.random.rand().__round__(2)  # random correlation
            correlation_matrix[i, j] = cor
            correlation_matrix[j, i] = cor

    sens2 = SensitivityAnalysis(fun=oakley2004.evaluate, pars=["x" + str(val) for val in range(1, 16, 1)],
                                bounds=[(-1, 1)]*15, groups=None, outputs=["response"], method="fs",
                                A=weights, M=correlation_matrix)
    sens2.perform_sensitivity_analysis()
    print(sens2.original_problem.analysis)
    print(sens2.problem.analysis)
    # sens2.problem.heatmap()
    # pyplot.show()
