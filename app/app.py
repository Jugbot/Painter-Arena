from flask import Flask
from flask_restful import Api
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = 'the quick brown fox jumps over the lazy dog'
app.config["DATABASE_URI"] = 'mysql://root:Minecraft700@localhost/store'
app.config["WIPE"] = False
socketio = SocketIO(app)


