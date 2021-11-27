import os
import pandas as pd
from importlib.machinery import SourceFileLoader

db = SourceFileLoader('*', '../config.py').load_module().db

filename= os.path.join("portfolios","us_dividend_portfolio.xlsx")
portfolio_df= pd.read_excel(filename)
df= portfolio_df[['Symbol', 'Weight']]
portfolio= {"name": "us dividends"}
portfolio['allocation']= df.to_dict('records')

