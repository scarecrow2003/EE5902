import random
import string
import csv
import math

load = 100
current_load = 0
with open('tasks.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    while True:
        # generate random string task name
        name = 'task_' + \
            ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(5))
        # generate random execution time
        worst_case_execution_time = random.randint(5, 10)
        actual_execution_time = worst_case_execution_time - random.randint(1, 2)
        period = random.randint(20, 50)  # generate period
        if current_load + worst_case_execution_time * 100 / period >= load:
            period = int(math.ceil(worst_case_execution_time * 100 / (load - current_load)))
            writer.writerow([name, worst_case_execution_time, actual_execution_time, period])
            break
        else:
            current_load += worst_case_execution_time * 100 / period
            writer.writerow([name, worst_case_execution_time, actual_execution_time, period])
csvFile.close()
