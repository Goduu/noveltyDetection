
from data_preparation import execute_extraction
import time

for i in range(75000,10000000,5000):
    print("[ETL] Executing... ", i)
    execute_extraction(4,i)
    time.sleep(1)