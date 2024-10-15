import math
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination
from pymoo.visualization.scatter import Scatter
from pymoo.optimize import minimize

# Constants
I_0 = 12000
height_min = 3
height_max = 7
num_lights_min = 1
num_lights_max = 15
pop_size = 50
max_gen = 100

# Points to be illuminated
points = [(x, y) for y in np.arange(0, 8, 0.5) for x in range(0, 201, 1)]

# ... (rest of the helper functions remain the same)


class LightingProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=num_lights_max * 2 + 1 + 1,  # x, y for each light + height + num_lights
                         n_obj=3,
                         n_constr=1,  # Just one constraint: num_lights within bounds
                         xl=np.array([0] * num_lights_max * 2 + [height_min, num_lights_min]),
                         xu=np.array([200] * num_lights_max * 2 + [height_max, num_lights_max]),
                         type_var=np.int64)  # Specify integer type

    def _evaluate(self, x, out, *args, **kwargs):
        h = int(round(x[-2]))  # Height
        num_lights = int(round(x[-1]))

        # Extract x, y coordinates for active lights
        solution = []
        for i in range(0, num_lights * 2, 2):
            x_coord = int(round(x[i]))
            y_coord = int(round(x[i+1]))
            solution.append((x_coord, y_coord))


        average_E, min_E = average_illuminance(solution, h)
        uniformity = uniformity_ratio(solution, h)
        cost_val = cost(solution, h)

        out["F"] = [-average_E, -uniformity, cost_val]  # Maximize average_E and uniformity

        # Constraint: Number of lights within min/max
        out["G"] = [num_lights - num_lights_max, num_lights_min - num_lights] # Check both upper and lower bounds


# Algorithm Setup
algorithm = NSGA2(
    pop_size=pop_size,
    sampling=IntegerRandomSampling(),  # Use integer sampling
    crossover=SBX(prob=0.9, eta=15, vtype=np.int64, repair=RoundingRepair()),  # Integer crossover
    mutation=PM(prob=1.0 / (num_lights_max * 2 + 2), eta=20, vtype=np.int64, repair=RoundingRepair()),  # Integer mutation
    eliminate_duplicates=True
)

termination = get_termination("n_gen", max_gen)

# Optimization
res = minimize(
    LightingProblem(),
    algorithm,
    termination,
    seed=1,
    save_history=True,
    verbose=True
)


# Visualization and Results
plot = Scatter()
plot.add(res.F, color="red")
plot.show()

print("Best solution found: %s" % res.X)
print("Function value: %s" % res.F)
print("Constraint violation: %s" % res.CV)

# Analyze Results (e.g., Pareto front, hypervolume, etc.)
# ...