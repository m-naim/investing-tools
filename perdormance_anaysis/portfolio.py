from datetime import date
import pandas as pd
import quantstats as qs
import numpy as np
from yahoo_fin import stock_info as si
from datetime import datetime


def portfolio_from_degiro_transactions():
    transactions=pd.read_csv("transactions.csv")
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
        print( d['Montant']/460)
        stocks_weight.loc[portfolio['Date']>=d['Date'], d['Produit']] = d['Cours']/460
        portfolio.loc[portfolio['Date']>=d['Date'], d['Produit']] =portfolio.loc[portfolio['Date']==d['Date']].iloc[0][d['Produit']] + d['Quantité']
        
    result= pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    result['Date']=portfolio['Date']
    portfolio_returns['Date']=portfolio['Date']
    result=result.set_index('Date')
    stocks_weight= stocks_weight.set_index('Date')
    portfolio=portfolio.set_index('Date')
    portfolio_returns=portfolio_returns.set_index('Date')
    
    for s in stocks:
        ticker=stocks_dictionary.loc[stocks_dictionary['Names']==s].iloc[0]['Symboles']
        stocks_returns= si.get_data(ticker,date_min,date_max)
        stocks_returns= stocks_returns['close'].pct_change()
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
