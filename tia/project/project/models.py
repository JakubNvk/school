import datetime
from random import SystemRandom

from backports.pbkdf2 import pbkdf2_hmac, compare_digest
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from project.data import db, CRUDMixin


association_table = db.Table('association',
                             db.Model.metadata,
                             db.Column('user', db.Integer, db.ForeignKey('user.id')),
                             db.Column('expedition', db.Integer, db.ForeignKey('expedition.id')) )

class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    _password = db.Column(db.LargeBinary(120))
    _salt = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    profile = db.relationship('Profile')
    created_expeditions = db.relationship('Expedition', backref='creator')
    comments = db.relationship('Comment')
    expeditions = db.relationship('Expedition', secondary=association_table, back_populates='members')
    messages = db.relationship('Message')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if self._salt is None:
            self._salt = bytes(SystemRandom().getrandbits(128))
        self._password = self._hash_password(value)

    def is_valid_password(self, password):
        new_hash = self._hash_password(password)
        return compare_digest(new_hash, self._password)

    def _hash_password(self, password):
        pwd = password.encode("utf-8")
        salt = bytes(self._salt)
        buff = pbkdf2_hmac("sha512", pwd, salt, iterations=100000)
        return bytes(buff)


class Profile(CRUDMixin, db.Model):
    __tablename__ = 'profile'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    age = db.Column(db.Integer)
    skills = db.Column(db.Integer, default=0)
    region = db.Column(db.String)
    description = db.Column(db.String)


class Comment(CRUDMixin, db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String)
    expedition = db.Column(db.Integer, db.ForeignKey('expedition.id'))


class Message(CRUDMixin, db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String)
    created = db.Column(db.DateTime)



class Expedition(CRUDMixin, db.Model):
    __tablename__ = 'expedition'

    plus_year = datetime.datetime.now() + datetime.timedelta(days=365)
    
    id = db.Column(db.Integer, primary_key=True)
    valid_to = db.Column(db.DateTime, default=plus_year)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, default=plus_year)
    min_difficulty = db.Column(db.Integer, default=0)
    max_difficulty = db.Column(db.Integer, default=10)
    description = db.Column(db.String)
    comments = db.relationship('Comment')
    locations = db.relationship('Location')
    members = db.relationship('User', secondary=association_table, back_populates='expeditions')



class Location(CRUDMixin, db.Model):
    __tablename__ = 'location'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    expeditions = db.Column(db.Integer, db.ForeignKey('expedition.id'))