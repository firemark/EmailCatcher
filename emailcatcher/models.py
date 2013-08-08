from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, DateTime,
                        Text, ForeignKey, PrimaryKeyConstraint)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

Base = declarative_base()
Session = sessionmaker()


class Email(Base):

    """Email model"""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    mail_from = Column(String(100))
    rctp_to = Column(String(100))
    received = Column(DateTime)

    def __str__(self):
        return "Email '%s%s'" % (self.msg[:20],
                                 '...' if len(self.msg) > 20 else '')

    def __repr__(self):
        return "< %s >" % self


class Header(Base):

    """Single Header to Email"""
    __tablename__ = "headers"

    email_id = Column(Integer, ForeignKey('emails.id'), primary_key=True)
    key = Column(String(100), primary_key=True)
    value = Column(String(100))

    email = relationship(Email, backref="headers")

    def __init__(self, key, value):
        self.key = key
        self.value = value.strip()

    def __repr__(self):
        return "<Header %s: %s >" % (self.key, self.value)


class Message(Base):

    """Email may has many messages with another content-types"""
    __tablename__ = "messages"

    content_type = Column(String(100), primary_key=True)
    content_transfer_encoding = Column(String(100))
    email_id = Column(Integer, ForeignKey('emails.id'), primary_key=True)

    msg = Column(Text)

    email = relationship(Email, backref="headers")


def setup():
    from sqlalchemy import create_engine
    global Session

    engine = create_engine('sqlite:///tits.db')
    Base.metadata.create_all(engine)

    Session.configure(bind=engine)
