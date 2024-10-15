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
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling

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

# Function to calculate intensity at a point from a light source
def calculate_I(x, y, x_p, y_p, h, I_0):
    D = math.sqrt((x - x_p) ** 2 + (y - y_p) ** 2 + h ** 2)
    return (I_0) * (h / D) ** 0.904839

# Function to calculate E at a point from a light source
def calculate_E(x, y, x_p, y_p, h):
    D = math.sqrt((x - x_p) ** 2 + (y - y_p) ** 2 + h ** 2)
    I = calculate_I(x, y, x_p, y_p, h, I_0)
    return (I * h) / (D ** 3)

# Function to calculate total illuminance for a given solution
def calculate_total_E(solution, h):
    total_E_grid = np.zeros((len(points),))
    min_E = float('inf')
    for light in solution:
        x_p, y_p = light
        for i, (x, y) in enumerate(points):
            illuminance = calculate_E(x, y, x_p, y_p, h)
            total_E_grid[i] += illuminance
            if illuminance < min_E:
                min_E = illuminance
    total_E = np.sum(total_E_grid)
    min_E = np.min(total_E_grid)
    return total_E, min_E

# Function to calculate average illuminance
def average_illuminance(solution, h):
    total_E, min_E = calculate_total_E(solution, h)
    return total_E / len(points), min_E

# Function to calculate uniformity ratio
def uniformity_ratio(solution, h):
    average_E, min_E = average_illuminance(solution, h)
    return min_E / average_E if average_E != 0 else 0

# Function to calculate the cost
def cost(solution, h):
    cost_generator = 150000000
    cost_lamp = 875000
    height_costs = {3: 1000000, 4: 1200000, 5: 1500000, 6: 1700000, 7: 2000000}
    total_cost = cost_generator + len(solution) * cost_lamp + len(solution) * height_costs[h]
    return total_cost


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