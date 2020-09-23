
from prediction import predict
from db_conexion import engine
import time
import pickle

def get_integrate():
    return engine.execute("SELECT count(client_id) \
                                     FROM Consumption \
                                     WHERE integrated = 0").first()[0]

ht_regressor = pickle.load(open('models/ht_regressorRecent.p', 'rb'))
ssth_regressor = pickle.load(open('models/ssth_regressorRecent.p', 'rb'))
print("[ML] Models Loaded...")
while True:

    while get_integrate() == 0:
        print("[ML] Waiting new data...")
        time.sleep(60)
    start_time = time.time()
    print("[ML] ", get_integrate(),"data to be integrated...")

    ht_regressor,ssth_regressor = predict(ht_regressor,ssth_regressor)
    print("[ML] Integration successfull execution in%d--- seconds ---" % (time.time() - start_time))


    
    

