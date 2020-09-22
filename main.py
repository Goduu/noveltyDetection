from data_preparation import execute_extraction
from model_training import train_all
from prediction import predict,predict2, evaluate,evaluate_cstm


execute_extraction(4,100000)

# train_all()
predict()
