from flask import Flask

# Place where app is defined
app = Flask(__name__)

from server import stocks, predictions, portfolio