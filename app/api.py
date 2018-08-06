import pathlib
import shutil
import time

from flask import request, g, Blueprint, Response
from flask_restful import Resource, Api
from sqlalchemy import exists

from app import app
from sockets import arena_room
from tables import session, Arena, User
from customauth import auth, basic_auth


api_routes = Blueprint('api', __name__)
api = Api(api_routes, prefix='/api')

SUCCESS = 200
UNAUTHORIZED = 401
BAD_REQUEST = 400
INTERNAL_ERROR = 500
INVALID_MEDIA = 415
CONFLICT = 409

class Match(Resource):
    MIN_PLAYERS = 2
    MAX_PLAYERS = 20
    MIN_TIME = 60000

    @auth.login_required
    def post(self):
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
                options = request.get_json() or dict()
                if 'prompt' in options:
                    arena.prompt = options['prompt']
                if 'max_players' in options \
                        and options['max_players'] \
                        and self.MIN_PLAYERS <= options['max_players'] <= self.MAX_PLAYERS :
                    arena.max_players = options['max_players']
                if 'timeout_delta' in options \
                        and options['timeout_delta'] \
                        and options['timeout_delta'] >= self.MIN_TIME:
                    arena.timeout_delta = options['timeout_delta']
                session.add(arena)
                session.commit() #commit inits defaults
                user.join_arena(arena)
                session.commit()
        timeout = None
        if hasattr(user.arena.timeout, 'isoformat'):
            timeout =  user.arena.timeout.isoformat()

        arena_room.emit_player_join(user)
        return { 'id': user.arena_id, 'start': user.arena.closed, 'votes': user.votes_pouch, 'timeout': timeout }, SUCCESS

    @auth.login_required
    def delete(self):
        user = g.user
        arena_room.emit_player_leave(user)
        user.leave_arena()
        session.commit()
        return "Success", SUCCESS


class ArenaGallery(Resource):
    @auth.login_required
    def get(self, id):
        if not id:
            return 'Invalid', BAD_REQUEST
        arena = session.query(Arena).filter_by(id=id).first()
        if not arena:
            return BAD_REQUEST
        payload = {}
        voted_users = g.user.voted_users
        for user in arena.players:
            entry = user.entry
            if entry:
                entry = user.get_dynamic_file_base64('entry')
                # with open('dynamic/u/%s/entry.png' % user.username, "rb") as imageFile:
                #     image = base64.b64encode(imageFile.read())
            avatar = user.avatar
            if avatar:
                avatar = user.get_dynamic_file_base64('avatar')
                # with open('dynamic/u/%s/avatar.png' % user.username, "rb") as imageFile:
                #     avatar = base64.b64encode(imageFile.read())

            payload[user.username] = {
                             'avatar': avatar,
                             'entry': entry,
                             'votes': user.votes_received
                             }
        return payload, SUCCESS

    @auth.login_required
    def put(self, id): # Updates votes only, set images in Player.update()
        if g.user.arena_id != id:
            return 'You are not in that Arena!', UNAUTHORIZED
        arena = session.query(Arena).filter_by(id=id).first()
        votes = request.get_json()
        print(votes)
        for user in arena.players:
            if user.username in votes:
                g.user.toggle_vote(user)
                session.commit()
                arena_room.emit_votes_changed(user)



class Player(Resource):
    FILES = ['entry', 'avatar']

    @auth.login_optional
    def get(self, name):
        user = g.user if hasattr(g, 'user') else session.query(User).filter_by(username=name).first()
        authorized = g.authorized if hasattr(g, 'authorized') else False
        if not user:
            return "No such user", BAD_REQUEST

        payload = {'authorized': authorized}
        if authorized and request.args.get('token'):
            payload['token'] = user.get_token()



        gets = {
            'entry': user.get_entry,
            'avatar': user.get_avatar,
            'skill': user.get_skill,
            'notifications': lambda: user.get_notifications() if authorized else [],
            'arena':  lambda: user.get_arena() if authorized else {}
        }

        item_requests = request.args.get('items')
        if not item_requests: #no params fetches all
            item_requests = list(gets.keys())
        for item in item_requests:
            payload[item] = gets[item]()


        return payload, SUCCESS

    @auth.login_required
    def put(self, name):
        if name != g.user.username:
            return "Url header mismatch", BAD_REQUEST
        for filename in self.FILES:
            if filename in request.form:
                g.user.set_dynamic_file(filename, request.form[filename])
                if filename == 'entry':
                    arena_room.emit_entry_update(g.user, request.form[filename])
        session.commit()

    def post(self, name): #Create user
        if not request.authorization:
            return "No credentials sent", BAD_REQUEST
        name = request.authorization.username
        password = request.authorization.password
        if not self._valid_password(password):
            return "Password needs to be longer than 5 characters", BAD_REQUEST
        if not self._valid_username(name):
            return "Username invalid", BAD_REQUEST
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


    @staticmethod
    def _valid_username(name): #TODO: Revisit on deployment
        return name # name[0] != ' ' and name[-1] != ' '


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
class PlayerCollection(Resource):
    def get(self, name):
        amount = request.args['len'] or 10  # amount of images to fetch
        pathlib.Path("dynamic/u/%s/collection" % name).mkdir(parents=True, exist_ok=True)


api.add_resource(Player, '/u/<string:name>')
api.add_resource(ArenaGallery, '/arena/<int:id>')
api.add_resource(Match, '/match')



