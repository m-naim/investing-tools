from sklearn.model_selection import train_test_split

import os
import time
import modelBuilder
import setting

if not os.path.isdir("models"):
    os.mkdir("models")
if not os.path.isdir("logs"):
    os.mkdir("logs")
if not os.path.isdir("data"):
    os.mkdir("data")

# date now
date_now = time.strftime("%Y-%m-%d")

tickers = ["FDX","MSFT","SU.PA","SGO.PA","NXI.PA","TTE.PA","VCT.PA","ATO.PA","^FCHI"]
def getModelAndDataTiker(ticker):
    scale_str = f"sc-{int(setting.SCALE)}"
    shuffle_str = f"sh-{int(setting.SHUFFLE)}"
    split_by_date_str = f"sbd-{int(setting.SPLIT_BY_DATE)}"
    
    ticker_data_filename = os.path.join("data", f"{ticker}_{date_now}.csv")
    # model name to save, making it as unique as possible based on parameters
    model_name = f"{ticker}-{shuffle_str}-{scale_str}-{split_by_date_str}-{setting.LOSS}-{setting.OPTIMIZER}-{setting.CELL.__name__}-seq-{setting.N_STEPS}-step-{setting.LOOKUP_STEP}-layers-{setting.N_LAYERS}-units-{setting.UNITS}"
    if setting.BIDIRECTIONAL:
        model_name += "-b"
    model,data= modelBuilder.getModel(ticker,ticker_data_filename,model_name)
    return model,data

# train the model and save the weights whenever we see 
# a new optimal model using ModelCheckpoint
import pridictor

# models = model,data
models=list(map(lambda ticker:getModelAndDataTiker(ticker),tickers))
tickers_prediction_metrics=list(map(lambda tup:pridictor.predictionData(tup[0],tup[1]),models)) 


# plot true/pred prices graph
# pridictor.plot_graph(final_df)

# save csv for predicted result
from pandas import DataFrame as dfm
predicted_result_filename=  f"predictions_by_{setting.LOOKUP_STEP}_{date_now}"
result_df= dfm(tickers_prediction_metrics)
result_df.to_csv(os.path.join("predections","csv",f"{predicted_result_filename}.csv" ))
result_df.to_excel(os.path.join("predections","xlsx",f"{predicted_result_filename}.xlsx"))