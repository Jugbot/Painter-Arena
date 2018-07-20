import base64
import pathlib
import shutil
import time
from binascii import a2b_base64

from flask import Flask, request, g, render_template
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
from sqlalchemy import exists

from tables import session, Arena, User
from app import api, app

auth = HTTPBasicAuth()

SUCCESS = 200
UNAUTHORIZED = 400 #401 # dumb browsers causing unwanted popups
BAD_REQUEST = 402
INTERNAL_ERROR = 500
INVALID_MEDIA = 415
CONFLICT = 409

# TODO: Look into file security
def get_dynamic_file_base64(user, filename):
    with open('dynamic/u/%s/%s.png' % (user.username, filename), "rb") as imageFile:
        return 'data:image/png;base64,%s' % base64.b64encode(imageFile.read()).decode()

def set_dynamic_file(user, filename, file):
    pathlib.Path("dynamic/u/%s" % user.username).mkdir(parents=True, exist_ok=True)

    data = file.split(',')[1]
    binary_data = a2b_base64(data)

    fd = open('dynamic/u/%s/%s.png' % (user.username, filename), 'wb')
    fd.write(binary_data)
    fd.close()

    # file.save('dynamic/u/%s/%s.png' % (user.username, filename))
    setattr(user, filename, True)
    session.commit()

@auth.verify_password
def verify_password(username, password):
    u = session.query(User).filter_by(username=username).first()
    if not u or not u.verify_password(password):
        return False
    g.user = u
    return True


class Match(Resource):
    @auth.login_required
    def get(self):
        user = g.user
        if not user.arena_id: # in battle
            min_range, max_range = 50, 1000
            interval = 10
            start = time.time()
            progress = 0
            while progress < 1:
                closest = session.query(Arena).filter(Arena.available).order_by(Arena.difference(user)).first()
                if closest is None:
                    progress = 1
                    continue
                # See if skill is a match, with larger tolerance over a minute of searching
                progress = (time.time() - start) / interval
                # skill_difference < time_scalar * min_to_max_skill
                if closest.difference(user) < progress * (max_range - min_range) + min_range:
                    user.join_arena(closest)
                    session.commit()
                    break
            else:
                arena = user.create_arena()
                session.add(arena)
                user.join_arena(arena)
                session.commit()
        timeout = None
        if hasattr(user.arena.timeout, 'isoformat'):
            timeout =  user.arena.timeout.isoformat()
        return { 'id': user.arena_id, 'start': user.arena.closed, 'votes': user.votes_pouch, 'timeout': timeout }, SUCCESS



class ArenaGallery(Resource):
    @auth.login_required
    def get(self, id):
        if not id:
            return 'Invalid', BAD_REQUEST
        arena = session.query(Arena).filter_by(id=id).first()
        payload = []
        voted_users = g.user.voted_users
        for user in arena.players:
            image = user.entry
            if image:
                image = get_dynamic_file_base64(user, 'entry')
                # with open('dynamic/u/%s/entry.png' % user.username, "rb") as imageFile:
                #     image = base64.b64encode(imageFile.read())
            avatar = user.avatar
            if avatar:
                avatar = get_dynamic_file_base64(user, 'avatar')
                # with open('dynamic/u/%s/avatar.png' % user.username, "rb") as imageFile:
                #     avatar = base64.b64encode(imageFile.read())

            payload.append({ 'username': user.username,
                             'avatar': avatar,
                             'image': image,
                             'votes': user.votes_received
                             })
        return payload

    @auth.login_required
    def put(self, id): # Updates votes only, set images in Player.update()
        if g.user.arena_id != id:
            return 'You are not in that Arena!', UNAUTHORIZED
        arena = session.query(Arena).filter_by(id=id).first()
        votes = request.json
        for user in arena.players:
            if user.username in votes:
                g.user.toggle_vote(user)


class Player(Resource):
    FILES = ['entry', 'avatar']

    def get(self, name):
        user = session.query(User).filter_by(username=name).first()
        if not user:
            return "No such user", BAD_REQUEST

        authy = request.authorization
        authorized = False
        if authy and name == authy.username:
            authorized = verify_password(authy.username, authy.password)
        payload = {'authorized': authorized}
        ##############
        # PUBLIC INFO
        for filename in self.FILES:
            payload[filename] = None
            if getattr(user,filename):
                payload[filename] = get_dynamic_file_base64(user, filename)
        payload['skill'] = user.skill
        ###############
        # PRIVATE INFO
        if authorized:
            if user.arena_id:
                payload['arena'] = { 'id': user.arena_id,
                                     'start': user.arena.closed,
                                     'votes': user.votes_pouch,
                                     'voted_users': [u.username for u in user.voted_users]
                                     }

        return payload, SUCCESS

    @auth.login_required
    def put(self, name):
        if name != g.user.username:
            return "Url header mismatch", BAD_REQUEST
        for filename in self.FILES:
            if filename in request.form:
                set_dynamic_file(g.user, filename, request.form[filename])

    def post(self, name): #Create user
        if not request.authorization:
            return "No credentials sent", BAD_REQUEST
        name = request.authorization.username
        password = request.authorization.password
        if not self._valid_password(password):
            return "Password needs to be longer than 5 characters", BAD_REQUEST
        if session.query(exists().where(User.username == name)).scalar():
            return "Username %s in use" % name, CONFLICT
        u = User(username=name)
        u.hash_password(password)
        session.add(u)
        session.commit()
        return self.get(name)

    @staticmethod
    def _valid_password(password):
        return len(password) >= 6

    @auth.login_required
    def delete(self, name):
        if name != g.user.username:
            return "Url header mismatch", BAD_REQUEST
        doomed_user = g.user
        shutil.rmtree('dynamic/u/%s' % name)
        session.delete(doomed_user)
        session.commit()
        return "Success", SUCCESS





# TODO: Player Pages
class PlayercCollection(Resource):
    def get(self, name):
        amount = request.args['len'] or 10  # amount of images to fetch
        pathlib.Path("dynamic/u/%s/collection" % name).mkdir(parents=True, exist_ok=True)




api.add_resource(Player, '/api/u/<string:name>')
api.add_resource(ArenaGallery, '/api/arena/<int:id>')
api.add_resource(Match, '/api/match')

'''''''''''''''''''''''''''''''''''''''
    Single page website with Vue.js
'''''''''''''''''''''''''''''''''''''''
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # if app.debug:
    #     return request.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False)
    #socketio.run(app, debug=True)

'''
class Avatar(Resource):
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
        if name != g.user.username:
            return "Url header mismatch", BAD_REQUEST
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

class Entry(Resource):
    def get(self, name):
        u = session.query(User).filter_by(username=name).first()
        if not u:
            return "No such user", BAD_REQUEST
        assert u.entry is not None
        if u.entry:  # Apparently Flask should not do this? Apache...
            print("hi")
            return send_from_directory('dynamic/u/%s' % name, 'entry.png')
        else:
            return send_from_directory('dynamic/defaults/u', 'entry.png')

    @auth.login_required
    def post(self, name):
        if name != g.user.username:
            return "Url header mismatch", BAD_REQUEST
        u = g.user
        if 'entry' not in request.files:
            return "No file recieved", BAD_REQUEST
        file = request.files['entry']
        if file.content_type != 'image/png':
            return "Entry must be a png", INVALID_MEDIA
        assert pathlib.Path("dynamic").exists()
        pathlib.Path("dynamic/u/%s" % name).mkdir(parents=True, exist_ok=True)
        file.save('dynamic/u/%s/entry.png' % name)
        u.entry = True
        session.commit()
        return "Success", SUCCESS
'''