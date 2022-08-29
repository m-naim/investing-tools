
import os
from flask import Flask
from flask_cors import CORS

# Place where app is defined
app = Flask(__name__, static_folder='../client/build')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


from server import stocks, predictions, portfolio, health
from . import service