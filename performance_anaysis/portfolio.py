from ast import Try
from datetime import date
import pandas as pd
import quantstats as qs
import numpy as np
from yahoo_fin import stock_info as si
from datetime import datetime
from bson import ObjectId
import yfinance
from pandas import DataFrame
from importlib.machinery import SourceFileLoader

def portfolio_from_degiro_transactions():
    transactions=pd.read_csv("transactions(1).csv")
    stocks_dictionary=pd.read_excel("stocksDictionary.xlsx")
    transactions['Date']=pd.to_datetime(transactions['Date'], format='%d-%m-%Y')

    date_min= transactions['Date'].iloc[-1]
    date_max= datetime.now()

    stocks= list(set(transactions['Produit']))
    transactions=transactions.sort_values(by='Date')

    dates= pd.date_range(date_min, date_max).tolist()
    portfolio = pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    stocks_weight= pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    portfolio_returns= pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    portfolio['Date'] = dates
    stocks_weight['Date']= dates

    for idx,d in transactions.iterrows():
        # maj des qty
        portfolio.loc[portfolio['Date']>=d['Date'], d['Produit']] =portfolio.loc[portfolio['Date']==d['Date']].iloc[0][d['Produit']] + d['Quantité']
        # calcule poid
        stocks_weight.loc[portfolio['Date']>=d['Date'], d['Produit']] = d['Cours']/760
        
    result= pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    result['Date']=portfolio['Date']
    portfolio_returns['Date']=portfolio['Date']
    result=result.set_index('Date')
    stocks_weight= stocks_weight.set_index('Date')
    portfolio=portfolio.set_index('Date')
    portfolio_returns=portfolio_returns.set_index('Date')
    
    for s in stocks:
        ticker=stocks_dictionary.loc[stocks_dictionary['Names']==s].iloc[0]['Symboles']
        stocks_returns= yfinance.Ticker(ticker).history(start=date_min,end=date_max,period="1d")['Close']
        stocks_returns= stocks_returns.pct_change()
        portfolio_returns[s]=stocks_returns
        float_portfolio=portfolio[s].astype('float64')
        result[s]= stocks_returns*float_portfolio * stocks_weight[s]
    
    stocks_weight= stocks_weight*100
    stocks_weight.to_excel('data.xlsx')
    return result

# df = DataFrame (stocks,columns=['Names'])
# df=pd.read_excel("stocksDictionary.xlsx")
# del df['Unnamed: 0']
# print(df)

db = SourceFileLoader('*', '../config.py').load_module().db

if __name__=="__main__":
    # retuns_data=portfolio_from_degiro_transactions()
    # retuns_data['sum']= retuns_data.sum(axis=1)
    # retuns_data['cum'] = (1 + retuns_data['sum']).cumprod()
    # print(retuns_data['sum'])
    # metrics=qs.reports.metrics(mode='full', returns=retuns_data['sum'],display=False).T.to_dict('records')
    try:
        portfolio=db.portfolios.find_one({'_id': ObjectId('6141fcfef2ae7e6fb0122251')});
        df= DataFrame(portfolio['perfs']).set_index('date')
        qs.reports.html(df['sum'], "SPY", output="per.html")
    except:
        print('error')



