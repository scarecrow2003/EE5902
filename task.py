class Task(object):
    def __init__(self, env, name, worst_case_execution_time, actual_execution_time, period):
        self.env = env
        self.name = name
        self.worst_case_execution_time = worst_case_execution_time
        self.actual_execution_time = actual_execution_time
        self.period = period
        self.deadline = period
        self.next_deliver_time = period

