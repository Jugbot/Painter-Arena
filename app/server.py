from flask import render_template
from flask_restful import Api
from app import app, socketio
from api import api_routes


'''''''''''''''''''''''''''''''''''''''
    Single page website with Vue.js
'''''''''''''''''''''''''''''''''''''''
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # if app.debug: # Nodejs server
    #     return request.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")


if __name__ == '__main__':
    # app.run(debug=True, use_debugger=False, use_reloader=False)
    socketio.run(app, debug=True)
