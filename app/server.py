from flask import Flask, request, g, render_template, send_from_directory
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
import pathlib
import shutil
import os
import time
from threading import Lock
from tables import Base, Arena, User
from templates import *

thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = 'the quick brown fox jumps over the lazy dog'
app.config["DATABASE_URI"] = 'mysql://root:Minecraft700@localhost/store'
api = Api(app)  # blueprint?
db_engine = create_engine(app.config["DATABASE_URI"], echo=True)
Session = sessionmaker(bind=db_engine)
session = Session()
auth = HTTPBasicAuth()
socketio = SocketIO(app)

Base.metadata.drop_all(db_engine)
Base.metadata.create_all(db_engine)

SUCCESS = 200
UNAUTHORIZED = 401
BAD_REQUEST = 402
INTERNAL_ERROR = 500
INVALID_MEDIA = 415
CONFLICT = 409


@auth.verify_password
def verify_password(username, password):
    if username != request.view_args.get('name'):
        return False
    u = session.query(User).filter_by(username=username).first()
    if not u or not u.verify_password(password):
        return False
    g.user = u
    return True


class Match(Resource):
    @auth.login_required
    def get(self):
        global thread
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(target=self.background_match_search, args=g.user)
        socketio.emit('match_search_progress', {'message': "Starting search", 'progress': 0, 'success': False})

    @staticmethod
    def background_match_search(user):
        min_range, max_range = 50, 1000
        interval = 60000  # minute
        start = time.time()
        progress = 0
        while progress < 1:
            closest = session.query(Arena).filter(Arena.available()).order_by(Arena.difference(user)).first()
            # See if skill is a match, with larger tolerance over a minute of searching
            progress = (time.time() - start) / interval
            # skill_difference < time_scalar * min_to_max_skill
            if closest.difference(user) < progress * (max_range - min_range) + min_range:
                socketio.emit('match_search_progress', {'message': "Found a match", 'success': True, 'id': closest.id})
                user.joinArena(closest)
                session.commit()
                break
            socketio.emit('match_search_progress', {'message': "Searching...", 'progress': progress, 'success': True})
        arena = user.createArena()
        session.add(arena)
        user.joinArena(arena)
        session.commit()


class ArenaGallery(Resource):
    # TODO: Unnecessary API route
    def get(self):
        id = request.args['id']
        if not id:
            return 'Invalid', BAD_REQUEST
        arena = session.query(Arena).filter_by(id=id)
        return [user.entry for user in arena.players]


class Avatar(Resource):
    # TODO: Unnecessary API route
    def get(self, name):
        u = session.query(User).filter_by(username=name).first()
        if not u:
            return "No such user", BAD_REQUEST
        assert u.avatar is not None
        if u.avatar:  # Apparently Flask should not do this? Apache...
            print("hi")

            return send_from_directory('dynamic/u/%s' % name, 'avatar.png')
        else:
            return send_from_directory('dynamic/defaults/u', 'avatar.png')

    @auth.login_required
    def post(self, name):
        u = g.user
        if 'avatar' not in request.files:
            return "No file recieved", BAD_REQUEST
        file = request.files['avatar']
        if file.content_type != 'image/png':
            return "Avatar must be a png", INVALID_MEDIA
        assert pathlib.Path("dynamic").exists()
        pathlib.Path("dynamic/u/%s" % name).mkdir(parents=True, exist_ok=True)
        file.save('dynamic/u/%s/avatar.png' % name)
        u.avatar = True
        session.commit()
        return "Success", SUCCESS


class Player(Resource):
    @auth.login_required
    def get(self, name):
        return "Success", SUCCESS

    def post(self, name):
        if not request.authorization:
            return "No credentials sent", BAD_REQUEST
        name = request.authorization.username
        password = request.authorization.password
        if not self.valid_password(password):
            return "Password needs to be longer than 5 characters", BAD_REQUEST
        if session.query(exists().where(User.username == name)).scalar():
            return "Username %s in use" % name, CONFLICT
        u = User(username=name)
        u.hash_password(password)
        session.add(u)
        session.commit()
        return "Success", SUCCESS

    @auth.login_required
    def delete(self, name):
        doomed_user = g.user
        shutil.rmtree('dynamic/u/%s' % name)
        session.delete(doomed_user)
        session.commit()
        return "Success", SUCCESS

    @staticmethod
    def valid_password(password):
        return len(password) >= 6


# TODO: Unnecessary API route
class PlayercCollection(Resource):
    def get(self, name):
        amount = request.args['len'] or 10  # amount of images to fetch
        pathlib.Path("dynamic/u/%s/collection" % name).mkdir(parents=True, exist_ok=True)




api.add_resource(Avatar, '/api/u/<string:name>/avatar.png')
api.add_resource(Player, '/api/u/<string:name>')

'''''''''''''''''''''''''''''''''''''''
    Single page website with Vue.js
'''''''''''''''''''''''''''''''''''''''
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return request.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)
    import matchmaker
