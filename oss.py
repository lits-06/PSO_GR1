import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os

num_jobs = 4
num_machines = 4
num_particles = 10
num_iterations = 50
# omega = 0.5
# c1 = 1.5
# c2 = 1.5

dimension = num_jobs * num_machines

processing_times_task_order = [
    [54, 34, 61, 2],
    [9, 15, 89, 70],
    [38, 19, 28, 87],
    [95, 34, 7, 29],
]

machines = [[3, 1, 4, 2], [4, 1, 2, 3], [1, 2, 3, 4], [1, 3, 2, 4]]
machine_index = [[value - 1 for value in row] for row in machines]

# Reorder processing times: processingTime[j][m] is the processing time of the
# task of job j that is processed on machine m
processing_times = [
    [
        processing_times_task_order[j][machine_index[j].index(m)]
        for m in range(num_machines)
    ]
    for j in range(num_jobs)
]


def objective_function(solution):
    schedule = (
        []
    )  # Contains n list (n = num machines) with a scheduling for each machine
    for i in range(num_machines):
        schedule.append([])

    for task in solution:  # for each task in solution path
        job = task // num_machines  # Find num of job
        machine = task % num_machines  # Find machine where task need to be executed
        execution_time = processing_times[job][machine]

        task_executed = False
        while not task_executed:
            job_already_executing_list = (
                []
            )  # list where is saved: if the task is executing or not for each machine
            for other_machine in range(num_machines):
                if (
                    job in schedule[other_machine]
                ):  # control if the job is in the schedule of another machine
                    job_already_executing_list.append(
                        True
                    )  # put a priori that is executing, next control if i really executing

                    # save needed data
                    time_this_machine = len(
                        schedule[machine]
                    )  # moment in time in which that machine is
                    time_other_machine = len(
                        schedule[other_machine]
                    )  # moment in time in which other machine is

                    start_task_time_this_machine = time_this_machine  # time if the task is going to start immediatly in this machine
                    finish_task_time_other_machine = find_index(
                        schedule[other_machine], job
                    )  # time when the task stop execution in other machine

                    if (
                        (time_this_machine <= time_other_machine)
                        and (
                            finish_task_time_other_machine
                            < start_task_time_this_machine
                        )
                    ) or (time_this_machine >= time_other_machine):
                        job_already_executing_list[other_machine] = False

                else:
                    job_already_executing_list.append(False)

            job_already_executing = (
                True if True in job_already_executing_list else False
            )

            if job_already_executing:  # if job already executing wait
                schedule[machine].append("-")
            else:
                for _ in range(execution_time):  # otherwise execute the task
                    schedule[machine].append(job)
                    task_executed = True

    machine_execution_lengths = []
    for i in range(num_machines):  # calculate makespan
        machine_execution_lengths.append(len(schedule[i]))

    return max(machine_execution_lengths), schedule


def find_index(other_machine_schedule, job):
    machine_schedule = other_machine_schedule.copy()
    machine_schedule.reverse()  # reversing the list
    index = machine_schedule.index(job)  # finding the index of element
    return len(machine_schedule) - index - 1


def get_gantt(solution):
    gantt_data = []  # machine list of dict
    for i in range(num_machines):
        schedule = {}
        machine_num = i
        time = 0
        job_num = solution[i][0]
        start = time
        duration = 0
        for j in range(len(solution[i])):
            if job_num == solution[i][j]:
                duration += 1
                time += 1
            else:
                schedule = get_dict(job_num, machine_num, start, duration)
                gantt_data.append(schedule)
                start = time
                time += 1
                job_num = solution[i][j]
                duration = 1

        schedule = get_dict(
            job_num, machine_num, start, duration
        )  # Do it because the last control cannot be done (out of bounds with index)
        gantt_data.append(schedule)

    gantt_data = remove_null_execution(gantt_data)

    return gantt_data


def get_dict(job_num, machine_num, start, duration):
    return {
        "Job": "job_" + str(job_num),
        "Machine": "machine_" + str(machine_num),
        "Start": start,
        "Duration": duration,
        "Finish": start + duration,
    }


def remove_null_execution(scheduling):
    new_scheduling = []
    for sched in scheduling:
        if sched["Job"] == "job_-":
            pass
        else:
            new_scheduling.append(sched)

    return new_scheduling


def visualize (results):
    schedule = pd.DataFrame(results)
    JOBS = sorted(list(schedule["Job"].unique()))
    MACHINES = sorted(list(schedule["Machine"].unique()))
    makespan = schedule["Finish"].max()

    bar_style = {"alpha": 1.0, "lw": 25, "solid_capstyle": "butt"}
    text_style = {"color": "white", "weight": "bold", "ha": "center", "va": "center"}
    colors = mpl.cm.Dark2.colors

    schedule.sort_values(by=["Job", "Start"])
    schedule.set_index(["Job", "Machine"], inplace=True)

    fig, ax = plt.subplots(2, 1, figsize=(12, 5 + (len(JOBS) + len(MACHINES)) / 4))

    for jdx, j in enumerate(JOBS, 1):
        for mdx, m in enumerate(MACHINES, 1):
            if (j, m) in schedule.index:
                xs = schedule.loc[(j, m), "Start"]
                xf = schedule.loc[(j, m), "Finish"]
                ax[0].plot([xs, xf], [jdx] * 2, c=colors[mdx % 7], **bar_style)
                ax[0].text((xs + xf) / 2, jdx, m, **text_style)
                ax[1].plot([xs, xf], [mdx] * 2, c=colors[jdx % 7], **bar_style)
                ax[1].text((xs + xf) / 2, mdx, j, **text_style)

    ax[0].set_title("Jobs Schedule")
    ax[0].set_ylabel("Jobs")
    ax[1].set_title("Machines Schedule")
    ax[1].set_ylabel("Machines")

    for idx, s in enumerate([JOBS, MACHINES]):
        ax[idx].set_ylim(0.5, len(s) + 0.5)
        ax[idx].set_yticks(range(1, 1 + len(s)))
        ax[idx].set_yticklabels(s)
        ax[idx].text(
            makespan,
            ax[idx].get_ylim()[0] - 0.2,
            "{0:0.1f}".format(makespan),
            ha="center",
            va="top",
        )
        ax[idx].plot([makespan] * 2, ax[idx].get_ylim(), "r--")
        ax[idx].set_xlabel("Time")
        ax[idx].grid(True)

    fig.tight_layout()
    plt.plot()

    folder_path = "results"
    files = os.listdir(folder_path)
    image_files = [f for f in files if f.endswith(('.png'))]
    num_images = len(image_files)
    image_name = f"results/execution_gantt_{num_images + 1}.png"
    plt.savefig(image_name)
