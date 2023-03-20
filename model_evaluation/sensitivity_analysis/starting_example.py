import numpy as np
from SALib import ProblemSpec
from SALib.sample import sobol as sobol_sampler, morris as morris_sampler, fast_sampler
from SALib.analyze import sobol, morris, fast
from SALib.test_functions import Ishigami

# ---- Setup Problem ----
problem = ProblemSpec(
    names=["x1", "x2", "x3"],  # List[str]: names of the input parameters to sample
    groups=None,  # Optional[List[str]]: names of the group (factor) that each parameter belongs to for grouped SA
    bounds=[(-np.pi, np.pi)] * 3,  # List[List[float]]: lower and upper bounds for each parameter sampling
    outputs=["response"],  # Optional[List[str]]: names of the response variable(s)
)

# ---- Sample from parameter space ----
# samples = sobol.sample(problem=problem, N=1024)
problem.sample(func=sobol_sampler.sample, N=2**14)  # creates annoying message on each call.
# alternatively, call the samplers directly (thanks to ProblemSpec._add_samplers()):
# problem.sample_sobol(1024); # problem.sample_morris(100); # problem.sample_fast(100)

# View samples (numpy.array)
getattr(problem, "samples")  # problem.samples
# array([[ 0.27913238, -2.16263456, -1.65803756],
#        [-1.82017621, -2.16263456, -1.65803756],
#        [ 0.27913238,  3.13334766, -1.65803756],
#        ...,
#        [-3.0968241 ,  2.8720456 ,  1.50480474],
#        [-3.0968241 ,  1.73726994,  1.42794031],
#        [-3.0968241 ,  1.73726994,  1.50480474]])

# ---- Evaluate the objective function ----
# The function must take a numpy array as input (columns corresponding to parameters) and return a numpy array as
problem.evaluate(func=Ishigami.evaluate, nprocs=16)

# view the results (numpy.array)
getattr(problem, "results")
# array([ 4.84792627,  4.77569087,  6.49499359, ..., -0.41284339,
#         0.9303217 ,  0.97824921])

# ---- Conduct the sensitivity analysis ----
problem.analyze(sobol.analyze)

# View the analysis results
problem.plot()
# problem.heatmap()

# ---- Again, with different hyper parameters ----
problem.evaluate(func=Ishigami.evaluate, A=0.532, B=0.2)
problem.analyze(sobol.analyze)
# problem.plot()


# ---- Evaluate in parallel
# problem.evaluate(Ishigami.evaluate, nprocs=8)


###
import numpy
def linear(intercept, slope, x):
    return intercept + slope * x


def wrapped_linear(X):
    intercept, slope, x = X.T
    return linear(intercept, slope, x)

thisX = numpy.array([[0.5, 0.5, 0.0], [0.5, 0.2, 0.2], [1.0, 1.0, 1.0]]).T
wrapped_linear(X=thisX)
