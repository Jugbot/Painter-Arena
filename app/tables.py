import atexit
import base64
import datetime
import math
import pathlib
from binascii import a2b_base64

from apscheduler.schedulers.background import BackgroundScheduler
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, event, func
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, backref

from app import app, jwt
from randomnames.utils import random_namepair
from sockets import arena_room

db_engine = create_engine(app.config["DATABASE_URI"])#, echo=True)
Session = sessionmaker(bind=db_engine)
session = scoped_session(Session)
Base = declarative_base()

scheduler = BackgroundScheduler()
scheduler.add_jobstore('sqlalchemy', url='mysql://root:Minecraft700@localhost/store')
atexit.register(lambda: scheduler.shutdown())
scheduler.start()

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

VOTES_PER_PLAYER = 3
# ARENA_TIMEOUT_MINUTES = 1
# MAX_PLAYERS = 10

class Arena(Base):
    __tablename__ = 'arenas'

    id = Column(Integer, primary_key=True)
    timeout = Column(DateTime)
    skill = Column(Integer, nullable=False, index=True)
    closed = Column(Boolean, default=False, nullable=False)
    players = relationship("User", back_populates="arena")
    player_count = Column(Integer, default=0, nullable=False)
    vote_count = Column(Integer, default=0, nullable=False)
    #options
    prompt = Column(String(256))
    max_players = Column(Integer, default=5, nullable=False)
    timeout_delta = Column(Integer, default=2*60000, nullable=False)

    BASE_REWARD = 100

    @hybrid_property
    def available(self):
        return self.player_count < self.max_players and not self.closed

    @available.expression
    def available(self):
        return (self.player_count < self.max_players) & ~self.closed

    @available.setter
    def available(self, val):
        self.closed = not val

    @hybrid_method
    def difference(self, other):
        return abs(self.skill - other.skill)

    @difference.expression
    def difference(self, other):
        return func.abs(self.skill - other.skill)

    @classmethod
    def __declare_last__(cls):
        event.listen(cls.closed, 'set', cls._start_battle)
        event.listen(cls.timeout, 'set', cls._set_timeout_event)
        event.listen(cls.players, 'append', cls._on_player_add_event)
        event.listen(cls.players, 'remove', cls._on_player_del_event)

    @staticmethod
    def _start_battle(target, value, oldvalue, initiator):
        target.timeout = datetime.datetime.now() + datetime.timedelta(milliseconds=target.timeout_delta)

    @staticmethod
    def _arena_timeout(id):
        a = session.query(Arena).get(id)
        try:
            a._finish_battle()
        except Exception as e:
            session.rollback()
            notif = Notification(
                message='Error resolving battle',
                type=3)
            for user in a.players:
                user.notifications.append(notif)
                session.commit()
                arena_room.emit_new_notification(a.id, notif)
            print("Error finishing battle: ", e) # make sure arena is destroyed so players are not in limbo
        a._close()

    def _finish_battle(self):
        for user in self.players:
            # error func _,- (-1.0 <-> 1.0) mean: 0.0
            skillmult = math.erf((self.skill - user.skill) / 100.0)
            scoremult = 1
            # avoid zero division
            if user.votes_received != 0:
                # (0.0 <-> MAX_P) mean: 1.0
                scoremult = user.votes_received / (self.vote_count / self.max_players)
            # mean: 0
            mult = (skillmult + 1) * (scoremult - 1)
            skilldiff = int(mult * self.BASE_REWARD)
            user.skill += skilldiff
            notif = Notification(
                message='Received %d votes and netted a change of %+d skill' % (user.votes_received, skilldiff),
                type=1)
            user.notifications.append(notif)
            session.commit()
            arena_room.emit_new_notification(self.id, notif)
            # have the client do this stuff
            # arena_room.emit_arena_end(user)

        for user in self.players:
            user.votes_pouch = VOTES_PER_PLAYER
            user.votes_received = 0
            user.entry = False
        session.commit()

    def _close(self):
        print('ending... ', self)
        if scheduler.get_job(self.id):
            scheduler.remove_job(self.id)
        arena_room.close_room(self.id, arena_room.namespace)
        session.delete(self)  # MySQL server has gone away
        session.commit()



    @staticmethod
    def _set_timeout_event(target, value, oldvalue, initiator):
        scheduler.add_job(
            func=Arena._arena_timeout,
            args=[target.id],
            trigger="date",
            run_date=value,
            id=str(target.id),
            name='Event for the end of the Arena battle',
            replace_existing=True)

    @staticmethod
    def _on_player_add_event(target, value, initiator):
        # skill represents avg player skill
        target.player_count += 1
        target.skill = ((target.player_count - 1) * target.skill + value.skill) / target.player_count
        if not target.available:
            target.closed = True
            if not target.prompt:
                target.prompt = random_namepair()

    @staticmethod
    def _on_player_del_event(target, value, initiator):
        target.player_count -= 1
        print(value, target.player_count)
        if target.player_count <= 0:
            return target._close()
        # skill represents avg player skill
        target.skill = ((target.player_count + 1) * target.skill - value.skill) / target.player_count

    def __repr__(self):
        return "<Arena(id='%s', active='%s')>" % (self.id, self.closed)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('users.id')) # for self-referential voted_users
    username = Column(String(16), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    avatar = Column(Boolean, default=False, nullable=False)
    skill = Column(Integer, default=1000, nullable=False)
    arena_id = Column(Integer, ForeignKey('arenas.id'))
    arena = relationship("Arena", back_populates="players")
    entry = Column(Boolean, default=False, nullable=False)
    # entry_submitted = Column(Boolean, default=False, nullable=False)
    votes_pouch = Column(Integer, default=VOTES_PER_PLAYER, nullable = False)
    voted_users = relationship("User", backref=backref('parent', remote_side=[id]))
    votes_received = Column(Integer, default = 0, nullable = False)
    notifications = relationship("Notification")

    ##############
    # PUBLIC INFO
    def get_skill(self):
        return self.skill

    def get_entry(self):
        if self.avatar:
            return self.get_dynamic_file_base64('entry')

    def get_avatar(self):
        if self.avatar:
            return self.get_dynamic_file_base64('avatar')

    ###############
    # PRIVATE INFO
    def get_arena(self):
        if self.arena_id:
            return {
                'max_players': self.arena.max_players,
                'prompt': self.arena.prompt,
                'timeout': self.arena.timeout.isoformat() if self.arena.timeout else None,
                'id': self.arena_id,
                'start': self.arena.closed,
                'votes': self.votes_pouch,
                'voted_users': [u.username for u in self.voted_users]}
        return {}

    def get_notifications(self):
        limited_list = []
        count = 0
        for notif in reversed(self.notifications):  # newest first
            if not count < 10:
                break
            count += 1
            limited_list.append({'message': notif.message, 'type': notif.type})
        return limited_list

    def get_token(self):
        return jwt.dumps({'username': self.username}).decode('utf-8')


    ##########
    # ACTIONS
    def toggle_vote(self, other):
        if not other.entry:
            print("invalid", other)
            return
        if other in self.voted_users:
            print("unvote")
            self.unvote(other)
        else:
            print("vote")
            self.vote(other)

    def unvote(self, other):
        self.votes_pouch += 1
        self.voted_users.remove(other) #not persisting??
        other.votes_received -= 1
        self.arena.vote_count -= 1


    def vote(self, other):
        if self.votes_pouch <= 0 and self not in other.votes_received:
            return
        self.votes_pouch -= 1
        self.voted_users.append(other)
        other.votes_received += 1
        self.arena.vote_count += 1

    def join_arena(self, arena):
        arena.players.append(self)

    def leave_arena(self):
        self.arena.players.remove(self)

    def create_arena(self):
        return Arena(skill=self.skill, player_count=0)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    # TODO: Look into file security
    def get_dynamic_file_base64(self, filename):
        with open('dynamic/u/%s/%s.png' % (self.username, filename), "rb") as imageFile:
            return 'data:image/png;base64,%s' % base64.b64encode(imageFile.read()).decode()

    def set_dynamic_file(self, filename, file):
        pathlib.Path("dynamic/u/%s" % self.username).mkdir(parents=True, exist_ok=True)

        data = file.split(',')[1]
        binary_data = a2b_base64(data)

        fd = open('dynamic/u/%s/%s.png' % (self.username, filename), 'wb')
        fd.write(binary_data)
        fd.close()

        # file.save('dynamic/u/%s/%s.png' % (self.username, filename))
        setattr(self, filename, True)

    def __repr__(self):
        return "<User(username='%s')>" % self.username

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('users.id'))
    type = Column(Integer, default=0)
    message = Column(String(512))

if app.config["WIPE"]:
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)

# a = Arena(skill=1000)
# session.add(a)
# session.commit()
# a.closed = True
