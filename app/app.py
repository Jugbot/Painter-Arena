from flask import Flask
from flask_socketio import SocketIO
from itsdangerous import TimedJSONWebSignatureSerializer as JWT

app = Flask(__name__)
app.config["SECRET_KEY"] = 'the quick brown fox jumps over the lazy dog'
app.config["DATABASE_URI"] = 'mysql://root:password@localhost/store'
app.config["WIPE"] = False
jwt = JWT(app.config['SECRET_KEY'], expires_in=3600)
socketio = SocketIO(app)

