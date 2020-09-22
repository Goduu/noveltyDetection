
from skmultiflow.data import DataStream
from skmultiflow.evaluation import EvaluateHoldout
import pandas as pd 
import matplotlib.pyplot as plt
from db_conexion import session
from Consumption import Consumption
import time
import pickle
from db_conexion import engine
from sqlalchemy import update

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_log_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import max_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import median_absolute_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_poisson_deviance
from sklearn.metrics import mean_gamma_deviance
from sklearn.metrics import mean_tweedie_deviance

max_samples = 1000000
# plt.ion()
# plt.show()


def evaluate_cstm():
    print("Starting Evaluation custom...")   
    plt.ion()
    plt.show()
    val_df = pd.read_sql(session.query(Consumption).filter(Consumption.integrated == False).statement,session.bind)
    fig, ax = plt.subplots(figsize=(15, 6))

    start_time = time.time()
    
    df = val_df.drop(columns=['id','client_id','year','month','integrated'])
    ht_regressor = pickle.load(open('ht_regressor.p', 'rb'))
    ssth_regressor = pickle.load(open('ssth_regressor.p', 'rb'))
    stream = DataStream(data = df,target_idx=0)

    n_samples = 0
    plr = []
    plprev_ht = []
    plprev_ssth = []
    ssth_mae = []
    ht_mae = []
    while n_samples < max_samples and stream.has_more_samples():
        X, y = stream.next_sample()
        y_ht = ht_regressor.predict(X)
        y_ssth = ssth_regressor.predict(X)[0][0]
        ht_regressor.partial_fit(X, y)
        ssth_regressor.partial_fit(X, y)
        n_samples += 1
        plr.append(y)
        plprev_ht.append(y_ht)
        plprev_ssth.append(y_ssth)
        ###---------------------
        ssth_mae.append(mean_tweedie_deviance(plr,plprev_ssth))
        ht_mae.append(mean_tweedie_deviance(plr, plprev_ht))
        ###---------------------
        if(n_samples > 100):
            plr = plr[1:]
            plprev_ht = plprev_ht[1:]
            plprev_ssth =plprev_ssth[1:]
        #     ssth_mae = ssth_mae[1:]
        #     ht_mae = ht_mae[1:]
        if(n_samples %25 == 0):
            plt.clf()
            plt.title("mean_tweedie_deviance") 
            plt.plot(range(len(ssth_mae)),ssth_mae,'b--',label='ssth')
            plt.plot(range(len(ht_mae)),ht_mae,'g--',label='ht')
            plt.legend()
            plt.pause(0.2)
    filename = "images/mean_tweedie_deviance.png"
    plt.savefig(filename)

    
    # filename = "images/prediction" + client_id + ".png"
    # plt.savefig(filename)
    # plt.close()

    print("Execution--- %s seconds ---" % (time.time() - start_time))


def predict():
    print("Starting prediction...")       
    # val_df = pd.read_sql(engine.execute("select * from consumption where integrated = 0 limit 0,10").statement,session.bind)
    val_df = pd.read_sql(session.query(Consumption).filter(Consumption.integrated == False).limit(5000).statement,session.bind)
    n_samples = 0
    cnter = 0
    for client_id in val_df.client_id.unique():
        

        start_time = time.time()
        
        df = val_df[val_df['client_id']==client_id].drop(columns=['id','client_id','year','month','integrated'])
        ht_regressor = pickle.load(open('ht_regressor.p', 'rb'))
        ssth_regressor = pickle.load(open('ssth_regressor.p', 'rb'))
        stream = DataStream(data = df,target_idx=0)

        plr = []
        plprev_ht = []
        plprev_ssth = []
        while n_samples < max_samples and stream.has_more_samples():
            X, y = stream.next_sample()
            y_ht = ht_regressor.predict(X)
            y_ssth = ssth_regressor.predict(X)[0][0]
            ht_regressor.partial_fit(X, y)
            ssth_regressor.partial_fit(X, y)
            n_samples += 1
            plr.append(y)
            plprev_ht.append(y_ht)
            plprev_ssth.append(y_ssth)
        cnter+=1
        print("Updtading ",client_id)
        update(Consumption).where(Consumption.client_id == client_id). \
                            values(integrated = 1)

        if(cnter % 500 == 0 and len(plr) > 0):
            fig, ax = plt.subplots(figsize=(15, 6))
            plt.plot(range(len(plr)),plr,'b-',label='Real')
            plt.plot(range(len(plprev_ht)),plprev_ht,'g--',label='HoeffdingTreeRegressor')
            plt.plot(range(len(plprev_ssth)),plprev_ssth, 'y--',label='StackedSingleTargetHoeffdingTreeRegressor')
            plt.legend()
            ht_mse = mean_squared_error(plr,plprev_ht)
            ssth_mse = mean_squared_error(plr,plprev_ssth)
            plt.title("HT MSE:" + str(ht_mse) + "SSTH MSE:" + str(ssth_mse))
            print("Ht mse: ",ht_mse)
            print("SSTH mse: ",ssth_mse)
            filename = "images/predictionMSE" + client_id + ".png"
            plt.savefig(filename)
            plt.close()
            pickle.dump(ht_regressor, open( "models/ht_regressor(samples="+str(n_samples)+").p", "wb" ) )
            pickle.dump(ssth_regressor, open( "models/ssth_regressor(samples="+str(n_samples)+").p", "wb" ) )
            #Updating 

        print("Execution--- %s seconds ---" % (time.time() - start_time))
    # except :
    #     pickle.dump(ht_regressor, open( "models/ht_regressor(samples="+str(n_samples)+").p", "wb" ) )
    #     pickle.dump(ssth_regressor, open( "models/ssth_regressor(samples="+str(n_samples)+").p", "wb" ) )
    #     update(Consumption).where(Consumption.client_id == client_id). \
    #                             values(integrated = 1)
    #     print("[Error]",er)



def predict2():
    val_df = pd.read_sql(session.query(Consumption).filter(Consumption.integrated == False).statement,session.bind)
    n_samples = 0
    print("Loading Models...")
    ht_regressor0 = pickle.load(open('ht_regressor.p', 'rb'))
    ht_regressor1 = pickle.load(open('ht_regressor(samples=7000).p', 'rb'))
    ht_regressor2 = pickle.load(open('ht_regressor(samples=30000).p', 'rb'))
    ssth_regressor0 = pickle.load(open('ssth_regressor.p', 'rb'))
    ssth_regressor1 = pickle.load(open('ssth_regressor(samples=7000).p', 'rb'))
    ssth_regressor2 = pickle.load(open('ssth_regressor(samples=30000).p', 'rb'))
    print("Starting prediction...")       
    for client_id in val_df.client_id.unique():

        start_time = time.time()
        
        df = val_df[val_df['client_id']==client_id].drop(columns=['id','client_id','year','month','integrated'])
        
        stream = DataStream(data = df,target_idx=0)

        cnter = 0
        plr = []
        plprev_ht0 = []
        plprev_ssth0 = []
        plprev_ht1 = []
        plprev_ssth1 = []
        plprev_ht2 = []
        plprev_ssth2 = []
        while n_samples < max_samples and stream.has_more_samples():
            n_samples += 1
            X, y = stream.next_sample()
            if(n_samples %1000 == 0): print(n_samples)

            if(n_samples > 30000):
                y_ht0 = ht_regressor0.predict(X)
                y_ssth0 = ssth_regressor0.predict(X)[0][0]
                y_ht1 = ht_regressor1.predict(X)
                y_ssth1 = ssth_regressor1.predict(X)[0][0]
                y_ht2 = ht_regressor2.predict(X)
                y_ssth2 = ssth_regressor2.predict(X)[0][0]
                plr.append(y)
                plprev_ht0.append(y_ht0)
                plprev_ssth0.append(y_ssth0)
                plprev_ht1.append(y_ht1)
                plprev_ssth1.append(y_ssth1)
                plprev_ht2.append(y_ht2)
                plprev_ssth2.append(y_ssth2)
                cnter+=1
        if(n_samples > 30000):
            print('ploting alcapaha')
            fig, ax = plt.subplots(figsize=(15, 6))
            plt.plot(range(len(plr)),plr,'b-',label='Real')
            plt.plot(range(len(plprev_ht0)),plprev_ht0,'g--',label='HoeffdingTreeRegressor0')
            plt.plot(range(len(plprev_ssth0)),plprev_ssth0, 'r--',label='StackedSingleTargetHoeffdingTreeRegressor0')
            plt.plot(range(len(plprev_ht1)),plprev_ht1,'c--',label='HoeffdingTreeRegressor1')
            plt.plot(range(len(plprev_ssth1)),plprev_ssth1, 'm--',label='StackedSingleTargetHoeffdingTreeRegressor1')
            plt.plot(range(len(plprev_ht2)),plprev_ht2,'y--',label='HoeffdingTreeRegressor2')
            plt.plot(range(len(plprev_ssth2)),plprev_ssth2, 'k--',label='StackedSingleTargetHoeffdingTreeRegressor2')
            plt.legend()
            ht_mse = mean_squared_error(plr,plprev_ht0)
            ssth_mse = mean_squared_error(plr,plprev_ssth0)
            print("Ht mse0: ",ht_mse)
            print("SSTH mse0: ",ssth_mse)
            ht_mse = mean_squared_error(plr,plprev_ht1)
            ssth_mse = mean_squared_error(plr,plprev_ssth1)
            print("Ht mse1: ",ht_mse)
            print("SSTH mse1: ",ssth_mse)
            ht_mse = mean_squared_error(plr,plprev_ht2)
            ssth_mse = mean_squared_error(plr,plprev_ssth2)
            print("Ht mse2: ",ht_mse)
            print("SSTH mse2: ",ssth_mse)
            filename = "images/predictionComparison" + client_id + ".png"
            plt.savefig(filename)
            plt.close()

            print("Execution--- %s seconds ---" % (time.time() - start_time))

from skmultiflow.evaluation import EvaluateHoldout
from skmultiflow.trees import HoeffdingTreeRegressor


def evaluate():
    print("Starting evaluation...")       
    val_df = pd.read_sql(session.query(Consumption).filter(Consumption.integrated == False).statement,session.bind)
    start_time = time.time()
    
    df = val_df.drop(columns=['id','client_id','year','month','integrated'])
    print(df)
    ht_regressor = pickle.load(open('ht_regressor.p', 'rb'))
    ssth_regressor = pickle.load(open('ssth_regressor.p', 'rb'))
    stream = DataStream(data = df.to_numpy(),target_idx=0)
    
    evaluator = EvaluateHoldout(
                        max_time=1000,
                        show_plot=True,
                        metrics=['mean_square_error'],
                        dynamic_test_set=True)

    evaluator.evaluate(stream=stream, model=[ssth_regressor], model_names=['SSTH'])
    

    print("Execution--- %s seconds ---" % (time.time() - start_time))
    
