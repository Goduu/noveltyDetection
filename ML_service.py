
from prediction import increment_model
from db_conexion import engine
import time
import pickle
from db_conexion import logging
import sys

logging.info("[ML] Loading Models...")
ht_regressor = pickle.load(open('models/ht_regressor12F48.p', 'rb'))

logging.info("[ML] Models Loaded...")

def get_integrate():
    while True:
        try:
            cnt = engine.execute("SELECT count(client_id) \
                                     FROM Consumption \
                                     WHERE integrated = 0").first()[0] 
            return cnt
        except:
            logging.error("[ML] Error to read the database")

    return 
# try:
start_time = time.time()
counter = 49
while True:
    while get_integrate() == 0:
        logging.info("[ML] Waiting new data..."+str(round(time.time() - start_time,2)))
        time.sleep(60)
    start_time = time.time()
    logging.info("[ML] " +  str(get_integrate())+" data points to be integrated..."+ str(round(time.time() - start_time,2)))

    ht_regressor,client_id_min,client_id_max = increment_model(ht_regressor)
    time.sleep(3)
    logging.info("[ML] Last Client integrated: "+ client_id_max)
    logging.info("[ML] Saving model at 'models/ht_regressor12F'..." + str(counter))
    pickle.dump(ht_regressor, open( "models/ht_regressor12F"+str(counter)+ ".p", "wb" ) )
    logging.info("[ML] Updating from " + client_id_min + " to " + client_id_max)
    engine.execute("UPDATE Consumption \
            SET integrated = 1 \
            WHERE client_id BETWEEN " + client_id_min + " and " + client_id_max)
    logging.info("[ML] Integration successfull execution in %d--- seconds ---" % round(time.time() - start_time,2))
    time.sleep(7)
    counter += 1

# except:
#     logging.error("[ML] Exception...")
#     sys.exit(1)


    
    

