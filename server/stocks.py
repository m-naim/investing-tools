from server import app
from server.helpers import parse_query_params, respose_success 
from flask import request, jsonify
from importlib.machinery import SourceFileLoader


db = SourceFileLoader('*', './config.py').load_module().db
collection = db.stocks

@app.route("/api/v1/stocks", methods=['GET'])
def fetch_stocks():
    try:
        query_params = parse_query_params(request.query_string)
        if query_params:
            query = {k: int(v) if isinstance(v, str) and v.isdigit() else v for k, v in query_params.items()}
            records_fetched = collection.find(query)
            if records_fetched.count() > 0:
                return jsonify(records_fetched)
            else:
                return "", 404
        else:
            stock_list= collection.find()
            if stock_list.count() > 0:
                return respose_success(stock_list)
            else:
                return jsonify([])
    except Exception as e: 
        print(e)
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return "", 500