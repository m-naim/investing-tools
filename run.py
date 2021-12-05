from server import app

if __name__ == '__main__':
    # Running app in debug mode
    app.run(debug=True,use_reloader=True, port=5000, threaded=True)