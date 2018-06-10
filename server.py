from flask import Flask, request, send_from_directory, g
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.apps import custom_app_context as pwd_context
import pathlib
import shutil
import os

SUCCESS = 200
UNAUTHORIZED = 401
BAD_REQUEST = 402
INTERNAL_ERROR = 500
INVALID_MEDIA = 415
CONFLICT = 409

db_engine = create_engine('mysql://root:Minecraft700@localhost/store', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(16), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    avatar = Column(Boolean, default=False, nullable=False)

    skill = Column(Integer, default=1000, nullable=False)
    arena = Column(Integer)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return "<User(username='%s', password='%s', avatar path='%s')>" % \
               (self.username, self.password_hash, self.avatar)


Session = sessionmaker(bind=db_engine)
session = Session()
User.__table__.drop(db_engine)
Base.metadata.create_all(db_engine)


app = Flask(__name__)
app.secret_key = 'the quick brown fox jumps over the lazy dog'
api = Api(app) #blueprint?
auth = HTTPBasicAuth()
cors = CORS(app)#, resources={r"/": {"origins": "http://localhost"}})

@auth.verify_password
def verify_password(username, password):
    if username != request.view_args.get('name'):
        return False
    u = session.query(User).filter_by(username=username).first()
    if not u or not u.verify_password(password):
        return False
    g.user = u
    return True


class Avatar(Resource):
    def get(self, name):
        u = session.query(User).filter_by(username=name).first()
        assert u.avatar is not None
        if u.avatar:  # Apparently Flask should not do this? Apache...
            return app.send_static_file('/u/%s/avatar.png' % name)
        else:
            return app.send_static_file('defaults/u/avatar.png')

    @auth.login_required
    def post(self, name):
        u = g.user
        if 'avatar' not in request.files:
            return "No file recieved", BAD_REQUEST
        file = request.files['avatar']
        if file.content_type != 'image/png':
            return "Avatar must be a png", INVALID_MEDIA
        assert pathlib.Path("static").exists()
        pathlib.Path("static/u/%s" % name).mkdir(parents=True, exist_ok=True)
        file.save('static/u/%s/avatar.png' % name)
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
        if not valid_password(password):
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
        shutil.rmtree('static/u/%s' % name)
        session.delete(doomed_user)
        session.commit()
        return "Success", SUCCESS


def valid_password(password):
    return len(password) >= 6


api.add_resource(Avatar, '/u/<string:name>/avatar.png')
api.add_resource(Player, '/u/<string:name>')

if __name__ == '__main__':
    app.run()
