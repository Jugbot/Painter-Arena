from flask import render_template, Response
from app import app, socketio
from api import api_routes #ok I need to keep this for some reason

'''''''''''''''''''''''''''''''''''''''
    Single page website with Vue.js
'''''''''''''''''''''''''''''''''''''''
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # if app.debug: # Nodejs server
    #     return request.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")

# @app.errorhandler(401)
def custom_401(error):
    # dumb browsers causing unwanted popups
    print('custom_401')
    return Response('Login Required', 401, {'WWWAuthenticate':'CustomBasic realm="Login Required"'})
app.register_error_handler(401, custom_401)

app.register_blueprint(api_routes)

if __name__ == '__main__':
    # app.run(debug=True, use_debugger=False, use_reloader=False)
    socketio.run(app, debug=True)
