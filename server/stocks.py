from server import app
from flask import  jsonify
from importlib.machinery import SourceFileLoader
from update_last import  update, get_last_index
from datetime import datetime
from .service.stock import get_last
from pandas import DataFrame
from bson import ObjectId

db = SourceFileLoader('*', './config.py').load_module().db
collection = db.stocks

@app.route("/api/v1/update/stocks/<id>/", methods=['GET'])
def update_stocks(id):
    try:
        print('update_stock The time is: %s' % datetime.now())
        start= datetime.now()
        portfolio= db.portfolios.find_one({"_id":ObjectId(id)},{'allocation':1})
        
        stocks= [ alloc['symbol'] for alloc in portfolio['allocation']]
        update(stocks)
        for s in stocks:
            get_last(s)
        end= datetime.now() -start
        print('update_stocks excuted in:'+str(end))
        return jsonify({"message":"okey letz go"})
    except Exception as e: 
        print(e)
        return "", 500

@app.route("/api/v1/update/indexs", methods=['GET'])
def update_indexs():
    try:
        print('update_indexs_job start The time is: %s' % datetime.now())
        start= datetime.now()

        symbs=['^FCHI','^GSPC']
        
        for s in symbs:
            get_last_index(s)
        end= datetime.now() -start
        print('update_stocks_job excuted in:'+str(end))
        return jsonify({"message":"okey letz go"})
    except Exception as e: 
        print(e)
        return "", 500


# def isin2stockprice(isin):
#     request_string = f"""https://query2.finance.yahoo.com/v1/finance/search?q={isin}&quotesCount=6&newsCount=0&enableFuzzyQuery=false&quotesQueryId=tss_match_phrase_query&multiQuoteQueryId=multi_quote_single_token_query&newsQueryId=news_ss_symbols&enableCb=false&enableNavLinks=false&vespaNewsTimeoutMs=600"""
#     r = requests.get(request_string)
#     data = r.json()
#     try:
#         return yf.Ticker(data['quotes'][0]['symbol'])
#     except IndexError:
#         return None