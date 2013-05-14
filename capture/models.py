from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship

from capture.database import Base


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    sid = Column(String(34), unique=True)
    date_time = Column(DateTime)
    sent = Column(String(15))
    received = Column(String(15))
    body = Column(String(160))
    status = Column(String(8))
    direction = Column(String(14))
    uri = Column(String(125), unique=True)

    def __init__(self, sid=None, date_time=None, sent=None, received=None,
                 body=None, status=None, direction=None, uri=None):
        self.sid = sid
        self.date_time = date_time
        self.sent = sent
        self.received = received
        self.body = body
        self.status = status
        self.direction = direction
        self.uri = uri

    def __repr__(self):
        return '<Message %r>' % (self.body)


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
    url = Column(String(255), unique=True)
    date_time = Column(DateTime)
    orientation = Column(SmallInteger)
    source = Column(String(64))
    location = Column(String(64))
    collection = Column(String(64))
    poses = Column(Integer)

    def __init__(self, url=None, date_time=None, orientation=None, source=None,
                 location=None, collection=None, poses=None):
            self.url = url
            self.date_time = date_time
            self.orientation = orientation
            self.source = source
            self.location = location
            self.collection = collection
            self.poses = poses

    def __repr__(self):
        return '<Photo %r>' % (self.url)


class Entries(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('message.id'))
    photo_id = Column(Integer, ForeignKey('photo.id'))
    date_time = Column(DateTime)

    message = relationship(Message, primaryjoin=Message.id == message_id)
    photo = relationship(Photo, primaryjoin=Photo.id == photo_id)
