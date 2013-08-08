from zope.interface import implements

from twisted.internet import defer, reactor
from twisted.mail import smtp
from twisted.mail.imap4 import LOGINCredentials, PLAINCredentials

from twisted.cred.portal import IRealm, Portal
from twisted.application import internet, service

from models import Email, Header, Session
from datetime import datetime


class ConsoleMessageDelivery:
    implements(smtp.IMessageDelivery)

    def receivedHeader(self, helo, origin, recipients):
        return "Received: ConsoleMessageDelivery"

    def validateFrom(self, helo, origin):
        print origin
        return origin

    def validateTo(self, user):
        return ConsoleMessage


class ConsoleMessage:
    implements(smtp.IMessage)

    def __init__(self):
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):

        lines = self.lines

        split_index = lines.index('')
        msg = lines[split_index + 1]

        headers = [Header(*line.split(':', 1)) for line in lines[:split_index]]

        email = Email(headers=headers, received=datetime.now(), msg=msg)

        sn = Session()
        sn.add(email)
        sn.commit()

        self.lines = None
        return defer.succeed(None)

    def connectionLost(self):
        self.lines = None


class ConsoleSMTPFactory(smtp.SMTPFactory):
    protocol = smtp.ESMTP

    def __init__(self, *a, **kw):
        smtp.SMTPFactory.__init__(self, *a, **kw)
        self.delivery = ConsoleMessageDelivery()

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        p.delivery = self.delivery
        p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p


class SimpleRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if smtp.IMessageDelivery in interfaces:
            return smtp.IMessageDelivery, ConsoleMessageDelivery(), lambda: None
        raise NotImplementedError()


def setup():
    from twisted.internet import reactor
    from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse


    portal = Portal(SimpleRealm())
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser("guest", "password")
    portal.registerChecker(checker)

    reactor.listenTCP(7777, ConsoleSMTPFactory(portal))
