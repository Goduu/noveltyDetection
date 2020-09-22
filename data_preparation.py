from sklearn.impute import SimpleImputer
from numpy import nan
import numpy as np
import time
from db_conexion import engine
import csv
from numpy import std, mean
import pandas as pd

def get_years_months(y,m, lenght):
    y,m = get_start_month(y,m,lenght)
    yf,mf = [],[]
    for i in range(lenght):
        if(m == 12):
            m = 1
            y+=1
            yf.append(y)
            mf.append(m)
        else:
            m+=1
            yf.append(y)
            mf.append(m)
    return yf,mf

def get_start_month(year,month, len):
    for i in range(len):
        if(month == 1):
            month = 12
            year-=1
        else:
            month-=1
    return year, month


imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')

def extract_features(raw_row, window_size):
    client_id = raw_row.get("COD_INSTALACAO")
    refMonth = raw_row.get("MES_REF")  
    year = int(refMonth.split(":")[0])
    month = int(refMonth.split(":")[1])
    client_id = raw_row.get("COD_INSTALACAO")
    raw_row.pop("MES_REF"); raw_row.pop("COD_INSTALACAO"); raw_row.pop("OPERANDO")
    #Trata os pontos sem dados
    row = [[ float(val) if val != '.' else np.nan for val in raw_row.values()][::-1]]
    imp_mean.fit(row)
    row = imp_mean.transform(row)
    row = row[0]
    year,month = get_start_month(year,month, len(row))
    row = list(filter(lambda v : v != -1, row))
    ms_vec = [i if i < window_size else window_size-1 for i in range(len(row))]
    features = {}
    features['client_id'] = client_id
    features['year'],features['month'] = get_years_months(year,month,len(row))
    features['value'] = row
    for i in range(window_size):
        features['v'+str(i+1)] = [ row[vi-i-1] if vi > i else 0 for vi,val in enumerate(row)]
        features['dif'+str(i+1)] = [row[vi-i-1]-row[vi-i-2] if vi > i+1 else 0 for vi,v in enumerate(row)]
    features['movAvg'] = [mean(row[vi-ms_vec[vi]:vi]) if vi>1 else 0 for vi,val in enumerate(row)]
    features['movStd'] = [std(row[vi-ms_vec[vi]:vi]) if vi>1 else 0 for vi,val in enumerate(row)]
    features['integrated'] = False
    df = pd.DataFrame(features)
    df = df[df['dif4'] != 0]
    df.to_sql('Consumption', con=engine, if_exists='append',index=False)

def execute_extraction(window_size,num_to_process):
    start_time = time.time()
    last_client =  engine.execute("SELECT max(client_id) FROM Consumption").first()[0] or '1'
    print("Last",last_client)
    with open('.\consumo.csv', 'r', newline='', encoding='utf-8') as csvfile:
        d_reader = csv.DictReader(csvfile)
        start_time = time.time()
        print("Starting...")
        futures = []
        for count,row in enumerate(d_reader):
            if(count < num_to_process):
                client_id = row.get("COD_INSTALACAO")
                if(client_id) > last_client:
                    a = extract_features(row, window_size)

                    if(count % 100 == 0): print('row',count)
            else: break
                    


    print("Execution %d--- seconds ---" % (time.time() - start_time))
