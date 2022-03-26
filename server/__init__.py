
import os
from flask import Flask,send_from_directory

# Place where app is defined
app = Flask(__name__, static_folder='../client/build')

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    print('ehh')
    print(path)
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

from server import stocks, predictions, portfolio