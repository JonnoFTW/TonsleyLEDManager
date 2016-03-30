from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from sqlalchemy import engine_from_config

import os
import logging
from .models import (
    LedUser,
    DBSession,
    Base
    )

log = logging.getLogger(__name__)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    try:
        db_url = settings['sqlalchemy.url']\
            .replace('DBUser', os.environ['DBUSER'])\
            .replace('DBPassword', os.environ['DBPASSWORD'])\
            .replace('DBHost', os.environ['DBHOST'])\
            .replace('DBName', os.environ['DBNAME'])
    except KeyError:
        log.debug("ERROR: You need to set environment variables for "
              "DBUSER, DBPASSWORD, DBHOST, DBNAME")
        exit(1)
    settings['sqlalchemy.url'] = db_url
    # engine = engine_from_config(settings, 'sqlalchemy.')
    # DBSession.configure(bind=engine)
    # Base.metadata.bind = engine

    config = Configurator(settings=settings)

    config.include('pyramid_mako')
    config.include('.models')

    def auth_callback(uid, request):
        user = request.db_session.query(LedUser).filter(LedUser.id == uid).first()
        if user is not None:
            return ['auth']

    auth_policy = AuthTktAuthenticationPolicy('skfjhklseh54w345kko954', callback=auth_callback, hashalg='sha512')
    config.set_authentication_policy(auth_policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('login', '/login') # post and get
    config.add_route('logout', '/logout')
    config.add_route('schedule_position', '/plugin/positions/update')
    config.add_route('schedule_update', '/plugin/{plugin_id}')

    config.add_route('help', '/help')
    config.add_route('register', '/register') # post and get
    config.add_route('schedule', '/') # post and get

    config.scan()
    return config.make_wsgi_app()
