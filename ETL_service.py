
from data_preparation import execute_extraction
import time
from db_conexion import logging
import sys 

try:
    for i in range(6000000,10000000,100000):
        logging.info("[ETL] Executing... " + str(i))
        execute_extraction(12,i)
        time.sleep(30)
except:
    logging.error("[ETL] Stopping...")
    sys.exit(1)
    
        