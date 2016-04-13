from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

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
            .replace('DBPassword', os.environ['DBPASS'])\
            .replace('DBHost', os.environ['DBHOST'])\
            .replace('DBName', os.environ['DBNAME'])
    except KeyError:
        log.debug("ERROR: You need to set environment variables for "
              "DBUSER, DBPASS, DBHOST, DBNAME")
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

    config.add_route('users', '/users')  # get shows list, post adds,
    config.add_route('show_user', '/users/{user_id}')  # get shows, post updates, delete deletes
    config.add_route('update_user', '/users/{user_id}/level')

    config.add_route('home', '/')
    config.add_route('help', '/help')

    config.add_route('plugin', '/plugin')
    config.add_route('plugin_update', '/plugin/{plugin_id}')

    config.add_route('schedule_update', '/schedule/{group_id}')  #post to manage the scheduel of a group

    config.add_route('group', '/group')  # post to make, get to list user's groups
    config.add_route('group_update',            '/group/{group_id}')  # get to show
    config.add_route('group_update_users',      '/group/{group_id}/users') # post
    config.add_route('group_delete_user',       '/group/{group_id}/users/delete')
    config.add_route('group_update_user_level', '/group/{group_id}/users/level')

    config.add_route('group_plugins_delete',    '/group/{group_id}/plugins/delete')
    config.add_route('group_plugins_add',       '/group/{group_id}/plugins/add')

    config.scan()
    return config.make_wsgi_app()
