import math
import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling, IntegerRandomSampling
from pymoo.termination import get_termination
from pymoo.visualization.scatter import Scatter
from pymoo.optimize import minimize
from pymoo.operators.repair.rounding import RoundingRepair
# Constants
I_0 = 12000
height_min = 3
height_max = 7
num_lights_min = 1
num_lights_max = 15
pop_size = 200  # Increased population size
max_gen = 300  # Increased number of generations
crossover_probability = 0.9
mutation_probability = 0.1


# Points to be illuminated (adjust granularity as needed)
points = [(x, y) for y in np.arange(0, 8, 0.5) for x in range(0, 201, 1)]

# ... (rest of the helper functions remain the same)


class LightingProblem(ElementwiseProblem):
    # ... (same as before)

    def _evaluate(self, x, out, *args, **kwargs):
        num_lights = int(x[-1])
        h = round(x[-2])
        indices = [int(x[i]) for i in range(num_lights)]
        solution = [points[idx % len(points)] for idx in indices] # Wrap around if index exceeds bounds
        average_E, min_E = average_illuminance(solution, h)
        uniformity = uniformity_ratio(solution, h)
        cost_val = cost(solution, h)

        out["F"] = [-average_E, -uniformity, cost_val]  # Minimize negative average E and negative uniformity

        # Constraints (corrected and simplified)
        g1 = average_E - 270  # Should be <= 270, so g1 <= 0
        g2 = 150 - min_E       # Should be >= 150, so g2 <= 0
        g3 = 0.7 - uniformity  # Should be >= 0.7, so g3 <= 0
        out["G"] = [g1, g2, g3, 0] # Dummy constraint to maintain n_constr = 4


# Algorithm Setup
algorithm = NSGA2(
    pop_size=pop_size,
    sampling=IntegerRandomSampling(),
    crossover=SBX(prob=crossover_probability, eta=15, vtype=float, repair=RoundingRepair()),
    mutation=PM(prob=mutation_probability, eta=20, vtype=float, repair=RoundingRepair()),
    eliminate_duplicates=True
)

termination = get_termination("n_gen", max_gen)

# Optimization
res = minimize(LightingProblem(),
               algorithm,
               termination,
               seed=1,
               save_history=True,
               verbose=True)


# Pareto Front Visualization
plot = Scatter()
plot.add(res.F, facecolor="none", edgecolor="red")
plot.show()


# 3D Pareto Front Visualization
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter(-res.F[:, 0], -res.F[:, 1], res.F[:, 2], c='blue', marker='o')  # Invert objectives for plotting
ax.set_xlabel("Average Illuminance")
ax.set_ylabel("Uniformity Ratio")
ax.set_zlabel("Cost")
plt.show()


# Print results (optional)
print("Best solutions:")
for f in res.F:
    print(f"Average Illuminance: {-f[0]}, Uniformity: {-f[1]}, Cost: {f[2]}")
