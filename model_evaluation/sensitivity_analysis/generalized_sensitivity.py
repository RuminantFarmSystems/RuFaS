"""
This module will contain the classes and methods needed to apply global sensitivity analyses to any objective function.

The workhorse of this module is the SALib python package (Herman et al. 2023): https://salib.readthedocs.io/en/latest/
"""
from __future__ import annotations
from SALib import ProblemSpec
from SALib.sample import sobol as sobol_sampler, morris as morris_sampler, fast_sampler
from SALib.analyze import sobol, morris, fast

from typing import List, Tuple, Optional, Callable, Dict
from enum import Enum
import numpy
from matplotlib import pyplot

class SupportedSensitivityMethods(Enum):
    """Enumerator for the SA methods supported by this module.

    The methods refer to those utilized by the `SALib` package:

    'sobol'
        `Sobol method <https://salib.readthedocs.io/en/latest/api/SALib.analyze.html#module-SALib.analyze.sobol>`_
    'fast'
       `FAST method <https://salib.readthedocs.io/en/latest/api/SALib.analyze.html#module-SALib.analyze.fast>`_
    `morris`
        `Morris' method <https://salib.readthedocs.io/en/latest/api/SALib.analyze.html#module-SALib.analyze.morris>`_
    """
    SOBOL = "sobol"
    FAST = "fast"
    MORRIS = "morris"
    FAST_SOBOL = "fs"  # need to figure out how to run SOBOL on reduced set determined by FAST results
    MORRIS_SOBOL = "ms"  # same here
    # TODO: add fractional factorial method


class SensitivityAnalysis:
    """Object for performing generalized global sensitivity analysis on an objective function over a set of parameters.

    Attributes
    ----------
    objective_function : function
        The objective function for which the sensitivity analysis should be conducted
    parameter_names : list[str]
        Names of the parameters over which the sensitivity analysis will be conducted.
    parameter_bounds : list[tuple(float, float)]
        The lower, and upper bounds, respectively, of each parameter.
    sensitivity_method : SupportedSensitivityMethods
        The type of sensitivity analysis to be conducted (See SupportedSensitivityMethods)
    parameter_groups : list[str], optional
        The groups (contrasts) that each parameter belongs to for grouped SA (not yet supported)
    output_names : list[str], optional
        The names of the output variables. If present, should have a length equal to the number of columns
        returned by fun for a single set of parameters.
    sample_n : int
        The number of samples (N) to request from the SA sampler.
    parallel_processors : int
        The number of processors (threads?) across which the model will be evaluated and SA will be conducted.
    additional_args : tuple
        Additional positional arguments passed to the `objective_function`.
    additional_kwargs : dict
        Additional keyword arguments passed to the `objective_function`.
    problem : ProblemSpec
        The `SALib.ProblemSpec` object on which the SA will be conducted.

    Notes
    -----
    The workhorse of this class is
    `ProblemSpec <https://salib.readthedocs.io/en/latest/api/SALib.util.html#module-SALib.util.problem>`_ from the
    `SALib <https://salib.readthedocs.io/en/latest/index.html>`_ package. This class is primarily a wrapper for
    functionality found in `SALib`.
    """
    def __init__(self, fun: Callable, pars: List[str], bounds: List[Tuple[float, float]], method: str = "fs",
                 groups: Optional[List[str]] = None, outputs: Optional[List[str]] = None, sample_n: int = 2**10,
                 n_cores: int = 1, *args, **kwargs):
        """Sets up the sensitivity analysis object

        This method first calls assigns attributes from the given arguments, after verifying them with `_check_inputs()`
        and then sets up the SA problem (using `SALib.ProblemSpec()`)

        Parameters
        ----------
        fun : function
            The objective function
        pars : list[str]
            Names of the parameters to analyze
        bounds : list[tuple(float, float)]
            Lower and upper parameter bounds, respectively
        method : str
            The SA analysis method to use (passed to SupportedSensitivityMethods)
        groups : list[str], optional
            Contrast groups for the parameters
        outputs : list[str], optional
            Names of the output variables
        sample_n : int, optional
            Target number of samples (passed to `SALib.ProblemSpec.sample()` as `N`). Defaults to :math:`2^10`
        n_cores : int, optional
            Number of cores/threads across which SA will be conducted. Defaults to 1.
        *args
            Additional positional arguments passed to `fun` during model evaluation.
        **kwargs
            Additional keyword arguments passed to `fun` during model evaluation.
        """
        self._check_inputs(pars, bounds, groups)

        self.objective_function: Callable = fun
        self.parameter_names: List[str] = pars
        self.parameter_bounds: List[Tuple[float, float]] = bounds
        self.sensitivity_method: SupportedSensitivityMethods = SupportedSensitivityMethods(method)
        self.parameter_groups: Optional[List[str]] = groups
        self.output_names: Optional[List[str]] = outputs
        self.sample_n: int = sample_n
        self.parallel_processors: int = n_cores
        self.additional_args: Tuple = args
        self.additional_kwargs: Dict = kwargs

        self.problem = self.define_problem()
        self.original_problem: Optional[ProblemSpec] = None

    @staticmethod
    def make_and_run(fun: Callable, pars: List[str], bounds: List[Tuple[float, float]], method: str = "fs",
                     groups: Optional[List[str]] = None, outputs: Optional[List[str]] = None, sample_n: int = 2**10,
                     n_cores: int = 1, *args, **kwargs) -> SensitivityAnalysis:
        """Standalone method to create a SensitivityAnalysis instance and perform the actual SA in a single call

        Returns
        -------
        SensitivityAnalysis
            A SensitivityAnalysis instance, with SA results computed.

        Notes
        -----
        Parameters are identical to those documented in the `__init__()` method.
        """
        obj = SensitivityAnalysis(fun, pars, bounds, method, groups, outputs, sample_n, n_cores, int, *args, **kwargs)
        obj.perform_sensitivity_analysis()
        return obj


    def perform_sensitivity_analysis(self) -> None:
        """Executes SA on the current problem

        Notes
        -----
        This method should be called after the problem is set up (via `define_problem()`). It 1) samples the parameter
        space, generating a sample table (`problem.samples`); 2) evaluates the objective function for each row in the
        sample table, generating model results (`problem.results`); and 3) performs the SA on the results, generating
        analysis results (`problem.analysis`).
        """
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
        """Performs validation checks for class specification arguments

        Notes
        -----
        This method is called by the `__init__()` method and its input parameters are documented in that method.
        """
        if len(pars) != len(bounds):
            raise ValueError("pars and bounds must be the same length")
        if groups is not None and len(groups) != len(pars):
            raise ValueError("groups must be the same length as pars")

    def define_problem(self) -> ProblemSpec:
        """Sets up the SA problem

        Returns
        -------
        ProblemSpec
            The problem on which SA will be conducted.
        """
        return ProblemSpec(names=self.parameter_names, bounds=self.parameter_bounds, groups=self.parameter_groups,
                           outputs=self.output_names)

    def sample_parameter_space(self, *args, **kwargs) -> None:
        """Samples the parameter space, based on the `sensitivity_method`.

        Parameters
        ----------
        *args
            additional positional arguments passed to `problem.sample()`
        **kwargs
            additional keyword arguments passed to `problem.sample()`

        Notes
        -----
        This is a wrapper for `problem.sample()`. This method is entirely serialized and, therefore, ignores `n_cores`.
        """
        if self.sensitivity_method == SupportedSensitivityMethods.FAST:
            self.problem.sample(func=fast_sampler.sample, N=self.sample_n, *args, **kwargs)
        if self.sensitivity_method == SupportedSensitivityMethods.SOBOL:
            self.problem.sample(func=sobol_sampler.sample, N=self.sample_n, *args, **kwargs)
        if self.sensitivity_method == SupportedSensitivityMethods.MORRIS:
            self.problem.sample(func=morris_sampler.sample, N=self.sample_n, *args, **kwargs)

    def evaluate_model(self) -> None:
        """Evaluates the objective function over the entire parameter sample space

        Notes
        -----
        This is a wrapper for `problem.evaluate()`. If `parallel_processors > 1`, then the parallel version of
        `problem.evaluate()` is used. This method should really benefit from parallelization, especially if the
        objective function has a substantial run time (as RuFaS does).

        Running this method in parallel will always result in a warning, indicating that it is experimental.
        """
        if self.parallel_processors > 1:
            self.problem.evaluate(func=self.objective_function, nprocs=self.parallel_processors,
                                  *self.additional_args, **self.additional_kwargs)
        else:
            self.problem.evaluate(func=self.objective_function, *self.additional_args, **self.additional_kwargs)

    def analyze_model(self, *args, **kwargs) -> None:
        """Performs the actual sensitivity analysis, based on the `sensitivity_method`

        Parameters
        ----------
        *args
            additional positional arguments passed to `problem.analyze()`
        **kwargs
            additional keyword arguments passed to `problem.analyze()`

        Notes
        -----
        This is a wrapper for `problem.analyze()`.

        If `parallel_processors > 1`, then the parallel version of `problem.analyze()` is used. This method is much
        less likely to benefit from parallelization when compared with `evaluate_model` because it can only work
        in parallel when multiple response variables are present (one process per response). If you want to perform
        SA on multiple output variables simultaneously (likely for RuFaS), then the parallel version should improve
        runtime.

        Running this method in parallel will always result in a warning, indicating that it is experimental.
        """
        # The poor structure of the `if else` blocks in this method are due to the way SALib implements parallelization.
        #   analyze(..., nprocs=1) will try to run the parallel version.
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


    def __str__(self):  # TODO: need to implement this - formatted output from printing the object
        pass

    def __repr__(self):  # TODO: need to implement this too.
        pass


if __name__ == '__main__':
    # Run Examples
    from SALib.test_functions import Ishigami, oakley2004
    from matplotlib import pyplot

    # -- Simple: Ishigami function --
    sens = SensitivityAnalysis(Ishigami.evaluate, pars=["x1", "x2", "x3"], bounds=[(-numpy.pi, numpy.pi)]*3,
                               groups=None, outputs=["response"], method="fast", n_cores=4)
    sens.define_problem()
    sens.sample_parameter_space()
    sens.evaluate_model()
    sens.analyze_model()
    print(sens.problem.analysis)

    # -- More complex: Oakley 2004 --
    weights = numpy.array([[1.0]*5 + [0.1]*5 + [0.01]*5,  # first 5 params have strong main effects, others are weaker
                           [0.5]*5 + [0.05]*5 + [0.005]*5,
                           [0.2]*5 + [0.02]*5 + [0.002]*5])
    correlation_matrix = numpy.zeros((15, 15))
    numpy.fill_diagonal(correlation_matrix, 1)
    numpy.random.seed(210)
    for i in range(11):
        for j in range(i+1, 15, 1):
            cor = numpy.random.rand().__round__(2)  # random correlations among first 11 parameters
            correlation_matrix[i, j] = cor
            correlation_matrix[j, i] = cor

    sens2 = SensitivityAnalysis(fun=oakley2004.evaluate, pars=["x" + str(val) for val in range(1, 16, 1)],
                                bounds=[(-1, 1)]*15, groups=None, outputs=["response"], method="sobol",
                                A=weights, M=correlation_matrix)
    sens2.perform_sensitivity_analysis()
    print(sens2.problem.analysis)
    sens2.problem.heatmap()
    sens2.problem.plot()
    pyplot.show()
