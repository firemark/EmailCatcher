from flask import Flask, render_template
from models import Email, Header, Session
from sqlalchemy.orm import joinedload

app = Flask('emailcatcher')

def setup():
    global app
    from twisted.internet import reactor
    from twisted.web.server import Site
    from twisted.web.wsgi import WSGIResource

    app.debug = True

    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)

    reactor.listenTCP(8000, site, interface="0.0.0.0")


@app.template_filter('datetime')
def datetime_filter(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


@app.route('/')
def index():
    emails = (Session().query(Email)
              .join(Email.headers)
              .options(joinedload(Email.headers))
              .order_by(Email.id.desc())
              .order_by(Header.key)
              .all())

    return render_template('index.html', emails=emails)


@app.route('/<int:email_id>/')
def show_iframe(email_id):
    pass

@app.route('/<int:email_id>/content')
def show_content(email_id):
    pass