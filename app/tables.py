from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, event, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

Base = declarative_base()

scheduler = BackgroundScheduler()
scheduler.add_jobstore('sqlalchemy', url='mysql://root:Minecraft700@localhost/store')
atexit.register(lambda: scheduler.shutdown())
scheduler.start()


class Arena(Base):
    __tablename__ = 'arenas'

    id = Column(Integer, primary_key=True)
    timeout = Column(DateTime)
    skill = Column(Integer, nullable=False, index=True)
    closed = Column(Boolean, default=False, nullable=False)
    players = relationship("User")


    @hybrid_property
    def player_count(self):
        return len(self.players)

    @hybrid_property
    def available(self):
        return self.player_count < 10 and not self.closed

    @available.expression
    def available(self):
        return self.player_count < 10 & ~self.closed

    @available.setter
    def available(self, val):
        self.closed = not val

    @hybrid_property
    def difference(self, other):
        return abs(self.skill - other.skill)

    @difference.expression
    def difference(self, other):
        return func.abs(self.skill - other.skill)

    @classmethod
    def __declare_last__(cls):
        event.listen(cls.timeout, 'set', cls.set_timeout_event)
        # TODO: event.listen(cls.available, )

    @staticmethod
    def set_timeout_event(target, value, initiator):
        scheduler.add_job(
            func=lambda: target.finish_battle(target.id),
            trigger=value, #hmmm
            id=target.id,
            name='Event for the end of the Arena battle',
            replace_existing=True)

    @staticmethod
    def finish_battle(id):
        pass


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(16), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    avatar = Column(Boolean, default=False, nullable=False)
    skill = Column(Integer, default=1000, nullable=False)
    arena = Column(Integer, ForeignKey('arenas.id'))
    entry = Column(Boolean, default=False, nullable=False)

    def joinArena(self, arena):
        arena.players.append(self)

    def createArena(self):
        return Arena(skill=self.skill)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return "<User(username='%s', password='%s', avatar path='%s')>" % \
               (self.username, self.password_hash, self.avatar)

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