import simpy
import csv
from task import Task


ex_flag = 1
is_idle = False
idle_start = 0
TU = 0  # worst case total utilization of all task in the system
CU = 0  # actual total utilization of system
TC = []  # completed tasks
total_energy_saved = 0
deadline_missed = 0


def power_aware(env, tasks):
    print('start to schedule tasks')
    tasks_in_queue = []
    current_task = None
    last_cpu_speed = 100
    global TU
    global is_idle
    global deadline_missed
    while True:
        current_time = env.now
        if current_time > 5000:
            percentage = total_energy_saved / 5000
            print('Total energy saved: ' + str(percentage) + '%')
            print('Missed deadline: ' + str(deadline_missed))
            break
        for name, task in tasks.items():
            if current_time % task.period == 0:
                # task arrival
                add_task_to_queue(tasks_in_queue, TaskWrapper(task, current_time))
                adjust_idleness(current_time, last_cpu_speed)
                TU += float(task.worst_case_execution_time) / task.period
                last_cpu_speed = calculate_cpu_speed(current_task)
        if (current_task is None) & (len(tasks_in_queue) > 0):
            current_task = tasks_in_queue.pop(0)
            current_task.start_time = current_time
        for task in TC:
            if task.abs_deadline <= current_time:
                adjust_idleness(current_time, last_cpu_speed)
                TC.remove(task)
                TU += float(task.task.worst_case_execution_time) / task.task.period
        if current_task is not None:
            cpu_speed = last_cpu_speed
            yield env.process(run_task(current_task, cpu_speed))
            if current_task.remaining_execution_time <= 0:
                adjust_idleness(current_time, last_cpu_speed)
                if current_task.abs_deadline < current_time:
                    deadline_missed += 1
                TC.append(current_task)
                current_task = None
        else:
            is_idle = True
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


def adjust_idleness(current_time, last_cpu_speed):
    if ex_flag:
        increase_temporal_idleness(current_time)
    elif is_idle:
        decrease_temporal_idleness(current_time, last_cpu_speed)


def calculate_cpu_speed(task):
    global ex_flag
    speed = CU
    for task_i in TC:
        if (task is None) or task_i.abs_deadline <= task.abs_deadline:
            speed -= task_i.idleness - float(100) * (task_i.task.worst_case_execution_time - task_i.task.actual_execution_time) / task_i.task.period
        if speed < 0:
            ex_flag = 1
            break
    if speed < 0:
        return 0
    else:
        return speed


def decrease_temporal_idleness(current_time, last_cpu_speed):
    idle_work = (current_time - idle_start) * last_cpu_speed
    for task in TC:
        if task.idleness > idle_work:
            task.idleness -= idle_work
            idle_work = 0
        else:
            idle_work -= task.idleness
            task.idleness = 0


def increase_temporal_idleness(current_time):
    for task in TC:
        slack = task.abs_deadline - task.start_time - task.task.actual_execution_time
        if task.abs_deadline != current_time:
            task.idleness += float(slack) / (task.abs_deadline - current_time)


def run_task(task, cpu_speed):
    cpu_speed = max(cpu_speed, 30)
    remaining_execution_time = float(task.remaining_execution_time) * 100 / cpu_speed
    if remaining_execution_time > 1:
        time_to_run = 1
    else:
        time_to_run = remaining_execution_time
    yield task.task.env.timeout(time_to_run)
    global total_energy_saved
    total_energy_saved += time_to_run * (100 - cpu_speed)
    task.remaining_execution_time -= float(time_to_run) * cpu_speed / 100


class TaskWrapper(object):
    def __init__(self, task, reach_time):
        self.task = task
        self.remaining_execution_time = task.actual_execution_time
        self.abs_deadline = task.deadline + reach_time
        self.idleness = 0
        self.start_time = 0


tasks = {}
env = simpy.Environment()
with open('tasks.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    for row in reader:
        tasks[row[0]] = Task(env, row[0], int(
            row[1]), int(row[2]), int(row[3]))

env.process(power_aware(env, tasks))
env.run()
