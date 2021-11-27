from importlib.machinery import SourceFileLoader
import pandas as pd
import os
import time

db = SourceFileLoader('*', '../config.py').load_module().db
date_now = time.strftime("%Y-%m-%d")

predicted_result_filename=  f"predictions_by_{15}_{date_now}"
file_path= os.path.join("predections","xlsx",f"{predicted_result_filename}.xlsx")

df= pd.read_excel(file_path)
del df['Unnamed: 0']
list_of_preds= list(df.T.to_dict().values())
document={'date': date_now, 'data': list_of_preds }
db.predictions.update_one({"date": date_now}, {"$set": document}, upsert = True)