from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, event, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context

import datetime
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

Base = declarative_base()

scheduler = BackgroundScheduler()
scheduler.add_jobstore('sqlalchemy', url='mysql://root:Minecraft700@localhost/store')
atexit.register(lambda: scheduler.shutdown())
scheduler.start()

VOTES_PER_PLAYER = 3
ARENA_TIMEOUT_MINUTES = 5


class Arena(Base):
    __tablename__ = 'arenas'

    id = Column(Integer, primary_key=True)
    timeout = Column(DateTime)
    skill = Column(Integer, nullable=False, index=True)
    closed = Column(Boolean, default=False, nullable=False)
    players = relationship("User", back_populates="arena")
    player_count = Column(Integer, default=0, nullable=False)
    vote_count = Column(Integer, default=0, nullable=False)

    @hybrid_property
    def available(self):
        return self.player_count < 10 and not self.closed

    @available.expression
    def available(self):
        return (self.player_count < 10) & ~self.closed

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
        event.listen(cls.closed, 'set', cls._set_timeout_event)
        event.listen(cls.timeout, 'set', cls._set_timeout_event)
        event.listen(cls.players, 'append', cls._on_player_add_event)

    def _start_battle(self):
        self.timeout = datetime.datetime.now() + datetime.timedelta(minutes=ARENA_TIMEOUT_MINUTES)

    def _finish_battle(self):
        # Reflects skill level over the mean
        for user in self.players:
            skilldiff = self.skill - user.skill
            scorediff = user.votes_received - self.vote_count
            user.skill += skilldiff * scorediff

        for user in self.players:
            user.votes_pouch = VOTES_PER_PLAYER
            user.votes_received = 0
            user.entry = False
        # TODO: Make less anticlimactic
        self.session.remove(self)
        self.session.commit()


    @staticmethod
    def _set_timeout_event(target, value, initiator):
        scheduler.add_job(
            func=target._finish_battle,
            trigger=value, #hmmm
            id=target.id,
            name='Event for the end of the Arena battle',
            replace_existing=True)

    @staticmethod
    def _on_player_add_event(target, value, initiator):
        # skill represents avg player skill
        target.skill = (target.player_count * target.skill + value.skill) / (target.player_count + 1)
        target.player_count += 1
        if not target.available:
            target.closed = True

    def __repr__(self):
        return "<Arena(id='%s', active='%s')>" % (self.id, self.closed)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(16), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    avatar = Column(Boolean, default=False, nullable=False)
    skill = Column(Integer, default=1000, nullable=False)
    arena_id = Column(Integer, ForeignKey('arenas.id'))
    arena = relationship("Arena", back_populates="players")
    entry = Column(Boolean, default=False, nullable=False)
    votes_pouch = Column(Integer, default = VOTES_PER_PLAYER, nullable = False)
    votes_received = relationship("Arena") # Column(Integer, default = 0, nullable = False)

    # TODO: record who you voted for
    def vote(self, other):
        if self.votes_pouch <= 0 and self not in other.votes_received:
            return False
        self.votes_pouch -= 1
        other.votes_received.append(self)
        self.arena.vote_count += 1
        return True

    def join_arena(self, arena):
        arena.players.append(self)

    def create_arena(self):
        return Arena(skill=self.skill, player_count=0)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return "<User(username='%s')>" % self.username

'''
from sortedcontainers import SortedList


class Matchmaker:

    def __init__(self, data=list()):
        self.pool = SortedList(data)

    def find(self, skillscore, radius):
        if not self.pool:
            return None

        ind = self.pool.bisect_left(OpenArena(-1, skillscore))
        right = self.pool[ind]
        left = None if ind == 0 else self.pool[ind-1]
        if left and right:
            dl = skillscore - left.skill
            dr = right.skill - skillscore
            if dr < radius or dl < radius:
                if dl > dr:
                    return right.id
                else:
                    return left.id
        elif left:
            dl = skillscore - left.skill
            if dl < radius:
                return left.id
        elif right:
            dr = right.skill - skillscore
            if dr < radius:
                return right.id

        return None

    def add(self, id, skill):
        self.pool.add(OpenArena(id, skill))

    def remove(self, skill):
        self.pool.remove(skill)

#'''