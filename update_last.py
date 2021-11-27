from config import db 
from pprint import pprint 
import yfinance as yf
import time
import multiprocessing.pool as mp

def get_last(s):
    obj={}
    start = time.time()
    print(start)
    try:
        obj['symbol'] = s
        obj['last'] = yf.Ticker(s).history(period="1d").iloc[0]['Close']
        obj['sector'] = yf.Ticker(s).info['sector']
        obj['industry'] = yf.Ticker(s).info['industry']
        obj['currency'] = yf.Ticker(s).info['currency']
        obj['country'] = yf.Ticker(s).info['country']
        obj['name'] = yf.Ticker(s).info['longName']
        db.stocks.update_one({'symbol': s},{'$set': obj}, upsert=True)
        
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

symbs= get_portfolios_symbs()
update(symbs)