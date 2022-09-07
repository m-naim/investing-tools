from datetime import datetime
import yfinance as yf
from pandas import DataFrame
from importlib.machinery import SourceFileLoader

db = SourceFileLoader('*', './config.py').load_module().db

def get_last(s):
    obj={}
    start = datetime.now()
    print("upadating: " +s)
    try:
        ticker=yf.Ticker(s)
        obj['symbol'] = s
        obj['last'] = ticker.history(period="1d").iloc[0]['Close']
        if "sector" in ticker.info:
            obj['sector'] = ticker.info['sector']

        if "industry" in ticker.info:
            obj['industry'] = ticker.info['industry']
        obj['currency'] = ticker.info['currency']
        if "country" in ticker.info:
            obj['country'] = ticker.info['country']
        obj['name'] = ticker.info['longName']
        obj['last_update'] = start
        obj['logo']= ticker.info['logo_url']
        db.stocks.update_one({'symbol': s},{'$set': obj}, upsert=True)
    except Exception as e: 
        print(s+": ")
        print(e)
