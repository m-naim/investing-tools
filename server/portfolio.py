
from server import app, stocks
from server.helpers import respose_success
from flask import request, jsonify
from importlib.machinery import SourceFileLoader
from bson.json_util import dumps
import yfinance as yf

from pandas import DataFrame
import pandas as pd
from yahoo_fin import stock_info as si
import numpy as np
from datetime import datetime


db = SourceFileLoader('*', './config.py').load_module().db
@app.route("/api/v1/portfolio", methods=['GET'])
def fetch_portfolio():
    collection = db.portfolios.find_one({'name':"current"})

    if collection!= None:
            return respose_success(collection)
    else:
        return jsonify([])

@app.route("/api/v1/portfolio", methods=['post'])
def post_portfolio():
    collection = db.portfolios.find_one({'name':"us dividends"})
    pf_stocks=[]

    collection['allocation']= pf_stocks
    print(collection['allocation'])
    if collection!= None:
            return respose_success(collection)
    else:
        return jsonify([])

@app.route("/api/v1/portfolio/performance", methods=['GET'])
def get_portfolio_performance():
    transactions=db.portfolios.find_one({'name': 'current'})['transactions']
    transactions= DataFrame(transactions)
    stocks= list(set(transactions['symbol']))
    transactions=transactions.sort_values(by='date')
    date_min= transactions['date'].iloc[0]
    date_max= datetime.now()

    dates= pd.date_range(date_min, date_max).tolist()
    portfolio = pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    stocks_weight= pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    portfolio_returns= pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    portfolio['date'] = dates
    stocks_weight['date']= dates
    initial_cash=460
    for idx,d in transactions.iterrows():
        stocks_weight.loc[portfolio['date']>=d['date'], d['symbol']] = d['price']/initial_cash
        portfolio.loc[portfolio['date']>=d['date'], d['symbol']] =portfolio.loc[portfolio['date']==d['date']].iloc[0][d['symbol']] + d['qty']
        
    result= pd.DataFrame(0, index=np.arange(len(dates)),columns= stocks)
    result['date']=portfolio['date']
    portfolio_returns['date']=portfolio['date']
    result=result.set_index('date')
    stocks_weight= stocks_weight.set_index('date')
    portfolio=portfolio.set_index('date')
    portfolio_returns=portfolio_returns.set_index('date')
    
    for s in stocks:
        stocks_returns= yf.Ticker(s).history(start=date_min,end=date_max,period="1d")['Close']
        stocks_returns= stocks_returns.pct_change()
        portfolio_returns[s]=stocks_returns
        float_portfolio=portfolio[s].astype('float64')
        result[s]= stocks_returns*float_portfolio * stocks_weight[s]
    
    stocks_weight= stocks_weight*100
    perf= DataFrame()
    perf['sum']= result.sum(axis=1)
    perf['cum'] = (1 + perf['sum']).cumprod()
    perf= perf.reset_index()
    print(perf)
    res= perf.to_dict('list')
    if res!= None:
            return respose_success(res)
    else:
        return jsonify({})
