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
        super().__init__(n_var=num_lights_max + 2,  # num_lights_max positions + height + num_lights 
                         n_obj=3,  # Number of objectives 
                         n_constr=4,  # Number of constraints 
                         xl=np.array([0] * num_lights_max + [height_min, num_lights_min]),  # Min values 
                         xu=np.array([len(points) - 1] * num_lights_max + [height_max, num_lights_max]),  # Max values 
                         vtype=int)   
 
 
    def _evaluate(self, x, out, *args, **kwargs): 
        num_lights = int(x[-1])  # Number of lights 
        h = round(x[-2])  # Height of lights, rounded to nearest integer 
        indices = [int(x[i]) for i in range(num_lights)]  # Light position indices 
        solution = [points[idx] for idx in indices]  # Map indices to points 
        average_E, min_E = average_illuminance(solution, h) 
        uniformity = uniformity_ratio(solution, h) 
        cost_val = cost(solution, h) 
        # Invert the objectives to convert maximization to minimization 
        out["F"] = [-average_E, -uniformity, cost_val]  # Objective values 
 
        # Constraints