from flask import request, jsonify
from server import app

@app.route("/health", methods=['GET'])
def get_health():
        return jsonify({'up':"I'm ok :)"})