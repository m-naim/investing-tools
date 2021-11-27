
from server import app
from server.helpers import respose_success
from flask import request, jsonify
from importlib.machinery import SourceFileLoader
from bson.json_util import dumps
import time
db = SourceFileLoader('*', './config.py').load_module().db


@app.route("/api/v1/predections", methods=['GET'])
def fetch_predections():
    date_now = time.strftime("%Y-%m-%d")
    collection = db.predictions.find({'date':date_now})
    if collection.count() > 0:
            return respose_success(collection)
    else:
        return jsonify([])