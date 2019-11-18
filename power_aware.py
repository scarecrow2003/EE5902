import simpy
import csv
from task import Task


def power_aware(env, tasks):
    print('start to schedule tasks')
    tasks_in_queue = []
    current_task = None
    cpu_speed = 100
    last_cpu_speed = 100
    TU = 0  # worst case total utilization of all task in the system
    CU = 0  # actual total utilization of system
    while True:
        current_time = env.now
        if current_time > 5000:
            break
        for name, task in tasks.items():
            if current_time % task.period == 0:
                # task arrival
                add_task_to_queue(tasks_in_queue, TaskWrapper(task, current_time))
                TU += float(task.worst_case_execution_time) / task.period
                last_cpu_speed = calculate_cpu_speed()
        if (current_task is None) & (len(tasks_in_queue) > 0):
            current_task = tasks_in_queue.pop(0)
        if current_task is not None:
            cpu_speed = last_cpu_speed
            yield env.process(run_task(current_task, cpu_speed))
            if current_task.remaining_execution_time <= 0:
                current_task = None
        else:
            # set cpu idle
            yield env.timeout(1)


def add_task_to_queue(tasks_in_queue, task):
    queue_len = len(tasks_in_queue)
    if queue_len == 0:
        tasks_in_queue.append(task)
    else:
        for i in xrange(len(tasks_in_queue)-1, -1, -1):
            if task.abs_deadline > tasks_in_queue[i].abs_deadline:
                tasks_in_queue.insert(i+1, task)
                break
            elif i == 0:
                tasks_in_queue.insert(0, task)


def calculate_cpu_speed():
    return 100


def run_task(task, cpu_speed):
    # start = task.task.env.now
    # print(task.task.name, ' starts to run at ', start)
    remaining_execution_time = float(task.remaining_execution_time) * 100 / cpu_speed
    if remaining_execution_time > 1:
        time_to_run = 1
    else:
        time_to_run = remaining_execution_time
    yield task.task.env.timeout(time_to_run)
    task.remaining_execution_time -= float(time_to_run) * cpu_speed / 100


class TaskWrapper(object):
    def __init__(self, task, reach_time):
        self.task = task
        self.remaining_execution_time = task.actual_execution_time
        self.abs_deadline = task.deadline + reach_time


tasks = {}
env = simpy.Environment()
with open('tasks.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    for row in reader:
        tasks[row[0]] = Task(env, row[0], int(
            row[1]), int(row[2]))

env.process(power_aware(env, tasks))
env.run()
