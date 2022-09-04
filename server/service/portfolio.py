from datetime import datetime
import yfinance as yf
from pandas import DataFrame
import pandas as pd
import numpy as np
from importlib.machinery import SourceFileLoader
from bson import ObjectId

db = SourceFileLoader('*', './config.py').load_module().db

def calculate_performance_fixed(id):
    print("calculate perfs for: "+id)
    pft=db.portfolios.find_one({'_id': ObjectId(id)})
    transactions=pft['transactions']
    transactions= DataFrame(transactions)
    stocks= list(set(transactions['symbol']))
    transactions=transactions.sort_values(by='date')
    date_min= transactions['date'].iloc[0]

    df_stocks= get_stocks(stocks,date_min).reset_index().sort_values(by='Date')
    # df_stocks.dropna(inplace=True)  
    portfolio = pd.DataFrame(0, index=np.arange(len(df_stocks['Date'])),columns= stocks+['cash','apport','invested'])
    portfolio['Date'] = df_stocks['Date']

    movements=list(pft['cash_flow'])
    for m in movements:
         portfolio.loc[portfolio['Date']>=m['date'], 'apport'] += m['amount']

    for i,transaction in transactions.iterrows():
        portfolio.loc[portfolio['Date']>=transaction['date'], transaction['symbol']] += transaction['qty']
        portfolio.loc[portfolio['Date']>=transaction['date'], 'invested'] += float(transaction['price'])
    
    portfolio['cash'] = portfolio['apport']- portfolio['invested'] 
    portfolio=portfolio.sort_values(by='Date')


    df_stocks= df_stocks.set_index('Date')
    portfolio=portfolio.set_index('Date')

    result= df_stocks[stocks]*portfolio[stocks]
    # plot_graph_multiple(result[['IHPCF']])
    result['value']= result.sum(axis=1)
    result['pnl']= result['value'] - portfolio['invested'] 
    result['cash']= portfolio['cash']
    result['apport']= portfolio['apport']
    result['invested']= portfolio['invested']
    result['total']= result['value']+ portfolio['cash']
    result['daily_returns']= (result['pnl']+1).pct_change()
    result['all']= result['invested']+ np.where(result['cash']>0, result['cash'], 0) 
    result['performance']= result['pnl']/result['all']*100
    result.dropna(inplace=True)
    perf= result[['performance','total','pnl']].reset_index().rename(columns={'Date':'date'})
    res= perf.to_dict('list')
    db.portfolios.update_one({'_id':ObjectId(id)},{'$set':{"perfs": res,"last_perfs_update": datetime.now() }})
    return perf

def get_stocks(stocks,date_min):
    start= datetime.now()
    stockArray= []
    for s in stocks:
        stock=db.histories.find_one({'symbol': s})
        if stock is None:
            stock= {'history':{}}

        if not('last_update' in stock) or stock['last_update'].date()<datetime.today().date():
            print(s,date_min)
            stock['history']= yf.Ticker(s).history(start=date_min,period="1d").reset_index()[['Date','Close']].to_dict('records')
            stock['last_update']=datetime.today()
            db.histories.replace_one({'symbol': s}, stock)

        df= pd.DataFrame(stock['history'],columns=['Date','Close']).set_index('Date').rename(columns={"Close":s})
        stockArray.append(df)
    stockDf= pd.concat(stockArray,axis=1, join='outer')
    end= datetime.now() -start
    print('get_stocks executed in: '+str(end))
    return stockDf

def calculate_dividends(id):
    print("calculate perfs for: "+id)
    start= datetime.now()
    pft=db.portfolios.find_one({'_id': ObjectId(id)})
    transactions=pft['transactions']
    transactions= DataFrame(transactions)
    stocks= list(set(transactions['symbol']))
    transactions=transactions.sort_values(by='date')
    date_min= transactions['date'].iloc[0]
    dividensArray= []

    for s in stocks:
        stock=db.dividends.find_one({'symbol': s})
        if stock is None:
            stock= {'dividends':{}}
        if  not('dividends' in stock) or not('last_update' in stock) or stock['last_update'].date()<datetime.today().date():
            stock['dividends']= yf.Ticker(s).get_dividends().to_frame().reset_index().to_dict('records')
            stock['last_update']=datetime.today()
            db.dividends.replace_one({'symbol': s}, stock,upsert=True)
        df= pd.DataFrame(stock['dividends'],columns=['Date','Dividends']).set_index('Date').rename(columns={"Dividends":s})
        dividensArray.append(df)

    dividends_df= pd.concat(dividensArray,axis=1, join='outer')
    dividends_df=dividends_df.loc[dividends_df.index>=date_min]

    portfolio = pd.DataFrame(0, index=np.arange(len(dividends_df.index)),columns= stocks)
    portfolio['Date']= dividends_df.index
    for i,transaction in transactions.iterrows():
        portfolio.loc[portfolio['Date']>=transaction['date'], transaction['symbol']] += transaction['qty']
    
    portfolio=portfolio.set_index('Date')
    res= dividends_df*portfolio
    res= res.sort_index()
    res['values']= res.sum(axis=1)
    res.index = pd.to_datetime(res.index)
    monthy= res['values'].resample('MS').sum().reset_index().to_dict('list')
    yearly= res['values'].resample('ys').sum().reset_index().to_dict('list')
    end= datetime.now() -start
    print('get_dividends executed in: '+str(end))
    dividends= {'monthy':monthy,'yearly':yearly}
    db.portfolios.update_one({'_id':ObjectId(id)},{'$set':{"dividends": dividends}})
    return dividends
