from cProfile import label
from cgitb import reset
from datetime import datetime
from operator import concat
from pickle import DICT
# from performance_anaysis.portfolio import portfolio_from_degiro_transactions
from numpy.core.fromnumeric import product
import yfinance as yf
from pprint import pprint
from config import db 
from pandas import DataFrame
import pandas as pd
import yahoo_fin.stock_info as si
import numpy as np
import matplotlib.pyplot as plt
from bson.objectid import ObjectId 
from pandasgui import show

def add_assets(portfolio):
    allocations=[]
    for allc in portfolio['allocation']:
        new_allc= allc
        itm = db.stocks.find_one({"symbol":allc['Symbol']})
        try:
            allc['asset']= itm
        except:
            allc['asset']= None
        allocations.append(allc)
    db.portfolios.update_one({'name':"us dividends"},{'$set':{"allocation": allocations}})

def add_transaction(trs):
    db.portfolios.update_one({'name':"current"},{'$push':{"transactions": trs}})

def creat_allocation(pf_name):
    pf= db.portfolios.find_one({'name':pf_name})
    transactions= pf['transactions']
    df=DataFrame.from_dict(transactions)
    alloc= DataFrame()
    alloc['qty']= df.groupby("symbol") ['qty'].sum()
    alloc['bep']= df.groupby("symbol") ['price'].mean()
    # alloc['bep_eur']= df.groupby("symbol") ['value'].mean()
    alloc= alloc.reset_index()
    symbols=alloc['symbol'].tolist()
    stocks= db.stocks.find({'symbol':{'$in': symbols}})
    stocks_dict = dict((s["symbol"], s) for s in stocks)

    alloc['asset'] = alloc['symbol'].apply(lambda x: ObjectId(stocks_dict[x]['_id']))
    balance= DataFrame.from_dict(pf['cash_flow'])['amount'].sum()
    alloc['last']=alloc['symbol'].apply(lambda x: stocks_dict[x]['last']) 
    alloc['total_value']= alloc['qty']*alloc['symbol'].apply(lambda x: stocks_dict[x]['last']) 
    if alloc['total_value'].sum()>balance:
        balance=alloc['total_value'].sum()

    alloc['weight']= alloc['total_value']/balance
    alloc= alloc.loc[alloc['weight']>0]
    allocation= list(alloc.to_dict(orient='index').values())
    pprint(allocation)
    db.portfolios.update_one({'name':pf_name},{'$set': {'allocation':allocation}})

def update_allocation(pf_name):
    pf= db.portfolios.find_one({'name':pf_name})
    alloc= pf['allocation']
    alloc=DataFrame.from_dict(alloc)

    symbols=alloc['symbol'].tolist()
    stocks= db.stocks.find({'symbol':{'$in': symbols}})
    stocks_dict = dict((s["symbol"], s) for s in stocks)

    alloc['asset'] = alloc['symbol'].apply(lambda x: ObjectId(stocks_dict[x]['_id']))
    balance= DataFrame.from_dict(pf['cash_flow'])['amount'].sum()
    alloc['last']=alloc['symbol'].apply(lambda x: stocks_dict[x]['last']) 
    # alloc['total_value']= alloc['weight']*alloc['symbol'].apply(lambda x: stocks_dict[x]['last']) 
    # if alloc['total_value'].sum()>balance:
    #     balance=alloc['total_value'].sum()

    # alloc['weight']= alloc['total_value']/balance
    # alloc= alloc.loc[alloc['weight']>0]
    allocation= list(alloc.to_dict(orient='index').values())
    pprint(allocation)
    db.portfolios.update_one({'name':pf_name},{'$set': {'allocation':allocation}})

def dump_ex_transactions():
    transaction_ex= {
                'symbol':'MSFT',
                'action': 'buy',
                'qty':1,
                'date': datetime.strptime("15-09-2021",'%d-%m-%Y'),
                'price': 289,
                'value': 240,
                }
    transaction_ex_2= {
                'symbol':'STM.PA',
                'action': 'buy',
                'qty':1,
                'date': datetime.strptime("15-09-2021",'%d-%m-%Y'),
                'price': 40,
                'value': 40,
                }
    add_transaction(transaction_ex_2)
    add_transaction(transaction_ex)

def add_cash_flow(trs):
    db.portfolios.update_one({'name':"current"},{'$push':{"cash_flow": trs}})
def dump_ex_cash():
    amount_1= {
                'action': 'deposite',
                'date': datetime.strptime("15-09-2021",'%d-%m-%Y'),
                'amount': 800,
                }
    amount_2= {
                'action': 'withdrow',
                'date': datetime.strptime("15-09-2021",'%d-%m-%Y'),
                'amount': -40,
                }
    add_cash_flow(amount_1)
    add_cash_flow(amount_2)

def calculate_performance(pf_name):
    print("calculate perfs for: "+pf_name)
    transactions=db.portfolios.find_one({'name': pf_name})['transactions']
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
    perf['cum_All'] = (1+perf['sum']).cumprod()
    perf['cum_1Y'] = (1+perf['sum'].tail(365)).cumprod()
    perf['cum_6M'] = (1+perf['sum'].tail(182)).cumprod()
    perf['cum_1M'] = (1+perf['sum'].tail(30)).cumprod()
    perf= perf.reset_index()
    res= perf.to_dict('list')
    db.portfolios.update_one({'name':pf_name},{'$set':{"perfs": res,"last_perfs_update": datetime.now() }})
    return perf

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


def get_dividends(id):
    print("calculate perfs for: "+id)
    start= datetime.now()
    pft=db.portfolios.find_one({'_id': ObjectId(id)})
    transactions=pft['transactions']
    transactions= DataFrame(transactions)
    stocks= list(set(transactions['symbol']))
    transactions=transactions.sort_values(by='date')
    date_min= transactions['date'].iloc[0]
    if(type(date_min)==str):
        date_min= datetime.strptime(date_min, '%Y-%m-%d')
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
    print(date_min)
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
    
def test():
    # res=get_stocks(['MSFT','AAPL','ACA.PA'],"2021-01-01")
    # print(res)
    res=calculate_performance_fixed('6300ed81d08cb823d0225828')
    # get_dividends('62b38bb44bccfe2988898a2b')

def plot_graph(df):
    """
    This function plots true close price along with predicted close price
    with blue and red colors respectively
    """
    fig = plt.figure(figsize=(10,5))
    plt.plot(df, c='b')
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend(["Actual Price", "Predicted Price"])
    # Saving the plot as an image
    # today= strftime("%Y-%m-%d")
    # dir_path=os.path.join("predections",'figures',today)
    # if not os.path.isdir(dir_path):
    #     os.mkdir(dir_path)
    # graph_name= os.path.join("predections",'figures',today,f'{ticker}.jpg')
    # fig.savefig(graph_name, bbox_inches='tight', dpi=150)
    plt.show()

def plot_graph_multiple(df):
    df.plot( y=df.columns.values,use_index=True,kind="line", figsize=(10, 10))
    plt.show()
    
# creat_allocation("current")
# portfolio_name="current"
# # creat_allocation(portfolio_name)
# perf=calculate_performance(portfolio_name)
# perf['sum']= perf.sum(axis=1)
# perf['cum'] = (1 + perf['sum']).cumprod()
# print(perf)
