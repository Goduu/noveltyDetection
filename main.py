from data_preparation import execute_extraction
from model_training import train_all
from prediction import increment_model,predict2, evaluate,evaluate_cstm
import time

# execute_extraction(12,10000)
# time.sleep(60)
train_all()
# execute_extraction(4,55000)

# predict2()
