1. Install package simpy by running `pip install simpy`

2. Generate task use `python generate_task_with_load.py`. The generate task set will be stored in file tasks.csv

3. Use `python power_aware.py` to schedule the generated tasks using power-aware scheduler. The scheduler will
 run until time reaches 5000.

4. Use `python past.py` to schedule the generated tasks using PAST. The scheduler will run
until time reaches 5000.

5. The outcome of two algorithm can be compared.