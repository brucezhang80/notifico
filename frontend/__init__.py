# -*- coding: utf8 -*-
from flask import Flask, g, session
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

from frontend.models import User
from frontend.public import public

app.register_blueprint(public)


@app.context_processor
def installation_variables():
    """
    Include static template variables from the configuration file in
    every outgoing template. Typically used for branding.
    """
    return app.config['TEMP_VARS']


@app.before_request
def set_user():
    g.user = None
    if '_u' in session and '_ue' in session:
        g.user = User.query.filter_by(
            id=session['_u'],
            email=session['_ue']
        ).first()


@app.before_request
def set_db():
    g.db = db


def start(debug=False):
    """
    Sets up a basic deployment ready to run in production in light usage.

    Ex: ``gunicorn -w 4 -b 127.0.0.1:4000 "notifico:start()"``
    """
    import os
    import os.path
    from werkzeug import SharedDataMiddleware

    app.config.from_object('frontend.default_config')

    if app.config.get('HANDLE_STATIC'):
        # We should handle routing for static assets ourself (handy for
        # small and quick deployments).
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/': os.path.join(os.path.dirname(__file__), 'static')
        })

    if debug:
        # Override the configuration's DEBUG setting.
        app.config['DEBUG'] = True

    # Let SQLAlchemy create any missing tables.
    db.create_all()

    return app
