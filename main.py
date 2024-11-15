from pso import *

solution_schedule, solution_cost = pso(seed=777)

_, schedule = objective_function(solution_schedule)
results = get_gantt(schedule)
print(results)
print(solution_cost)
visualize(results)
