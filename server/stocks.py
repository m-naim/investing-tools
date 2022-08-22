from server import app
from server.helpers import parse_query_params, respose_success 
from flask import request, jsonify
from importlib.machinery import SourceFileLoader
from update_last import get_portfolios_symbs, update, get_last_index
from datetime import datetime

db = SourceFileLoader('*', './config.py').load_module().db
collection = db.stocks

@app.route("/api/v1/update/stocks", methods=['GET'])
def update_stocks():
    try:
        print('update_stocks_job start The time is: %s' % datetime.now())
        start= datetime.now()
        portfolios=db.portfolios.find({},{"name":1, "_id":0})
        symbs=[]
        for pf in portfolios:
            print(pf)
            symbs += get_portfolios_symbs(pf['name'])
        symbs= set(symbs)
        print(symbs)
        update(symbs)
        end= datetime.now() -start
        print('update_stocks_job excuted in:'+str(end))
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