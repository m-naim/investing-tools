from pprint import pprint 
import yfinance as yf
import time
import multiprocessing.pool as mp
from pymongo import MongoClient, ssl_support


def get_last(s):
    obj={}
    hist={}
    start = time.time()
    print(start)
    try:
        ticker=yf.Ticker(s)
        obj['symbol'] = s
        hist['symbol'] = s
        history=ticker.history(period='10y',interval="1d")['Close'].reset_index().to_dict('records')
        hist['history']=history
        obj['last'] = ticker.history(period="1d").iloc[0]['Close']
        obj['sector'] = ticker.info['sector']
        obj['industry'] = ticker.info['industry']
        obj['currency'] = ticker.info['currency']
        obj['country'] = ticker.info['country']
        obj['name'] = ticker.info['longName']

        db.stocks.update_one({'symbol': s},{'$set': obj}, upsert=True)
        db.histories.update_one({'symbol': s},{'$set': hist}, upsert=True)
        
    except Exception as e: 
        print(s+": ")
        print(e)
        # db.stocks.delete_one({'Symbol':s})
        # print(s+" dont exist")

def update(symbs):            
    if __name__=="__main__":
        p=mp.Pool(8)
        start = time.time()
        p.map(get_last,symbs) 
        p.close()
        p.join()
        end = time.time()
        print("The time of execution of above program is :", end-start)

def get_portfolios_symbs():
    pfs=list(db.portfolios.find({'name':'current'}))
    symbols= [ allc['symbol'] for pf in pfs for allc in pf['allocation']]
    return symbols

def get_all_symbs():
    stocks=list(db.stocks.find({}))
    symbs= list(map(lambda s: s['symbol'],stocks))
    return symbs


