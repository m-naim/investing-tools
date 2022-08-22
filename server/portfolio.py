
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
from bson import ObjectId
import quantstats as qs


db = SourceFileLoader('*', './config.py').load_module().db


@app.route("/api/v1/portfolio/<id>/performance", methods=['GET'])
def get_portfolio_performance(id):

    res= calculate_performance(id)
    if res!= None:
            return respose_success(res)
    else:
        return jsonify({})


@app.route("/api/v1/portfolio/<id>/stats", methods=['GET'])
def get_portfolio_stats(id):
    portfolio=db.portfolios.find_one({'_id': ObjectId(id)});
    delta= portfolio['last_perfs_update'] - datetime.now() 
    print(delta)
    res=portfolio['perfs']
    if(delta.total_seconds()/3600 > 1): 
        res= calculate_performance(id)
    
    df= DataFrame(res).set_index('date')
    metrics=qs.reports.metrics(mode='full', returns=df['sum'],display=False).T.to_dict('records')

    if metrics!= None:
            return respose_success(metrics)
    else:
        return jsonify({})

def calculate_performance(id):
    print("calculate perfs for: "+id)
    transactions=db.portfolios.find_one({'_id': ObjectId(id)})['transactions']
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
    initial_cash=2000
    for idx,d in transactions.iterrows():
        stocks_weight.loc[portfolio['date']>=d['date'], d['symbol']] = float(d['price'])/initial_cash
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
    perf['cum_All'] = (1+perf['sum']).cumprod()
    perf['cum_1Y'] = (1+perf['sum'].tail(365)).cumprod()
    perf['cum_6M'] = (1+perf['sum'].tail(182)).cumprod()
    perf['cum_1M'] = (1+perf['sum'].tail(30)).cumprod()
    perf= perf.reset_index()
    res= perf.to_dict('list')
    db.portfolios.update_one({'_id': ObjectId(id)},{'$set':{"perfs": res,"last_perfs_update": datetime.now() }})
    return res