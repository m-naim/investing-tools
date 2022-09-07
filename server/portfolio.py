
from ast import Try
from server import app, stocks
from server.helpers import respose_success
from flask import  jsonify
from importlib.machinery import SourceFileLoader

from pandas import DataFrame
import numpy as np
from datetime import datetime
from bson import ObjectId
import quantstats as qs
from .service.portfolio import calculate_performance_fixed,calculate_dividends

db = SourceFileLoader('*', './config.py').load_module().db


@app.route("/api/v1/portfolio/<id>/performance", methods=['GET'])
def get_portfolio_performance(id):

    res= calculate_performance_fixed(id)
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
        res= calculate_performance_fixed(id)
    
    df= DataFrame(res).set_index('date')
    metrics=qs.reports.metrics(mode='full', returns=df['performance'],display=False).T.to_dict('records')

    if metrics!= None:
            return respose_success(metrics)
    else:
        return jsonify({})


@app.route("/api/v1/portfolio/<id>/dividends", methods=['GET'])
def get_dividends(id):
    try:
        res=calculate_dividends(id)
        return respose_success(res)
    except:
        return jsonify({})

def get_stocks():
    print("wait")