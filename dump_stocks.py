from datetime import datetime
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


# portfolio_name="current"
# # creat_allocation(portfolio_name)
# perf=calculate_performance(portfolio_name)
# perf['sum']= perf.sum(axis=1)
# perf['cum'] = (1 + perf['sum']).cumprod()
# print(perf)
