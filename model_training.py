import sys
import pickle
from skmultiflow.trees import StackedSingleTargetHoeffdingTreeRegressor
from skmultiflow.trees import HoeffdingTreeRegressor
import pandas as pd
from Consumption import Consumption
import time
from db_conexion import session
from db_conexion import engine
from sqlalchemy import update

sys.setrecursionlimit(6500)

table_df = pd.read_sql(session.query(Consumption).filter(Consumption.integrated == True).statement,session.bind)

X_train = table_df.drop(columns=['value','client_id','year','integrated','month','id'], axis=1).to_numpy()
y_train = table_df['value'].to_numpy()


def train_ssth():
    print("Start training Stacked Single Target Hoeffding Tree Regressor...")
    ssth_regressor = StackedSingleTargetHoeffdingTreeRegressor(max_byte_size=2000000000)

    start_time = time.time()

    ssth_regressor.fit(X_train,y_train)
    print("Execution ssth completed in -- %s seconds --" % round(time.time() - start_time,2))
    pickle.dump(ssth_regressor, open( "models/ssth_regressor.p", "wb" ) )

def train_ht():
    print("Start training Hoeffding Tree Regressor...")

    ht_regressor = HoeffdingTreeRegressor(grace_period = 1000, nb_threshold = 6)

    start_time = time.time()

    ht_regressor.fit(X_train,y_train)
    print("Execution ht completed in -- %s seconds --" % round(time.time() - start_time,2))
    pickle.dump(ht_regressor, open( "models/ht_regressor12F.p", "wb" ) )

def train_all():
    train_ht()
    engine.execute("UPDATE Consumption \
                     SET integrated = 1 \
                     WHERE integrated = 0")
    

