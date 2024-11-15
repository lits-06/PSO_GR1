from oss import *
import numpy as np
from tqdm import tqdm
import random

num_tasks = dimension
sol = [None] * num_particles
sol_cost = np.zeros(num_particles)
best_so_far = None
best_cost = 1e300


def pso(seed):
    np.random.seed(seed)
    for particle in range(num_particles):
        sol[particle] = initialize_solution()

    evaluate_solutions()

    for i in tqdm(range(1, num_iterations + 1)):
        for particle in range(num_particles):
            update_velocity(particle)
            update_position(particle)

        evaluate_solutions()

    return best_so_far, best_cost


def initialize_solution():
    return list(np.random.permutation(range(0, num_tasks)))


def evaluate_solutions():
    global best_cost, best_so_far

    for i in range(0, num_particles):
        sol_cost[i], _ = objective_function(sol[i])  # Save solution cost for each pariticle

    ibest = sol_cost.argmin()  # Take best solution (minimum cost) for the pariticle
    if sol_cost[ibest] < best_cost:  # If the iteration best is better than best so far replace the solution
        best_cost = sol_cost[ibest]
        best_so_far = sol[ibest]


def update_velocity(particle):
    personal_diff = [
        (i, j) for i, j in zip(range(len(sol[particle])), range(len(best_so_far)))
        if sol[particle][i] != best_so_far[j]
    ]

    if personal_diff:
        personal_changes = random.choice(personal_diff)
        return personal_changes

    return []


def update_position(particle):
    if len(update_velocity(particle)) != 0:
        i, j = update_velocity(particle)
        sol[particle] = swap(sol[particle], i, j)


def swap(sol, i, j):
    sol_swapped = sol.copy()
    sol_swapped[i] = sol[j]
    sol_swapped[j] = sol[i]
    return sol_swapped
