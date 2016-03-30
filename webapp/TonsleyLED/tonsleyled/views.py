import hashlib

import re
from pyramid.security import remember
from pyramid.view import view_config, forbidden_view_config

from pyramid.view import view_config, forbidden_view_config, notfound_view_config
from pyramid.security import remember, forget, Authenticated, Allow
import pyramid.httpexceptions as exc
from sqlalchemy import and_, update
import datetime
from models import LedSchedule, LedUser

# config.add_route('login', '/login')
#  config.add_route('register', '/register') # post
#  config.add_route('schedule', '/schedule') # post and get


def authenticate(func):
    def auth_only(*args, **kwargs):

        # print "auth uid is", request.authenticated_userid
        if args[1].authenticated_userid is None:
            raise exc.HTTPFound(location='/login')
        return func(args[1], **kwargs)
    return auth_only

def get_schedule_all(request):
    return {
        'schedule': request.db_session.query(LedSchedule).order_by(LedSchedule.position.asc()).all()
    }

@view_config(route_name='schedule', renderer='templates/schedule.mako', request_method='GET')
def schedule_get(request):
    print request.exception
    return get_schedule_all(request)


@view_config(route_name='help', renderer='templates/help.mako', request_method='GET')
def help_get(request):
    return {}



@view_config(route_name='schedule', renderer='templates/schedule.mako', request_method='POST')
@authenticate
def schedule_post(request):
    # get the post params from form and insert
    try:
        print request.POST
        code = request.POST['source']
        name = request.POST['name']
        length = int(request.POST['length'])
        userid = request.authenticated_userid
        position = 1
    except KeyError as e:
        return {'error': "Missing "+e.message}
    except Exception as e:
        return {'error': e.message}
    sched = LedSchedule(name=name, code=code, length=length, user_id=userid, position=position)
    request.db_session.add(sched)
    request.db_session.flush()
    return get_schedule_all(request)



@view_config(route_name='login', renderer='templates/login.mako')
@forbidden_view_config(renderer='templates/login.mako')
def login_view(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    email = ''
    password = ''
    if 'form.submitted' in request.params:
        email = request.params['email']
        password = request.params['password']
        user = request.db_session.query(LedUser).filter(and_(LedUser.email == email,
                                                  LedUser.password == hashlib.sha512(password).hexdigest())
                                             ).first()
        if user:
            if not user.access_level > 0:
                message = "User is not approved yet"
            else:
                print(email, "successfully logged in")
                headers = remember(request, user.id)
                return exc.HTTPFound(location=came_from, headers=headers)
        else:
            message = 'Failed login'

    return dict(
        message=message,
        url=request.application_url + '/login',
        came_from=came_from,
        email=email,
        password=password,
        )


@view_config(route_name='logout')
@authenticate
def logout(request):
    headers = forget(request)
    return exc.HTTPFound(location='/login', headers=headers)


@view_config(route_name='schedule_position', renderer='json', request_method='POST')
@authenticate
def schedule_update_position(request):
    # post args should be a mapping of plugin_id -> position
    for plugin_id, position in request.POST.items():
        plugin = request.db_session.query(LedSchedule).filter(LedSchedule.id == plugin_id).first()
        plugin.position = position
    return {'message': 'Done'}


@view_config(route_name='schedule_update', renderer='json', request_method='POST')
@authenticate
def schedule_update(request):
    # make sure the plugin id exists
    plugin_id = request.matchdict['plugin_id']
    plugin = request.db_session.query(LedSchedule).filter(LedSchedule.id == plugin_id).first()
    if not plugin:
        raise exc.HTTPBadRequest("No such plugin")
    else:
        def to_null(val):
            if val == '':
                return None
            return val
        POST = {k: to_null(v) for k, v in request.POST.items()}
        time_from, time_to = sorted([request.POST['time_from'], request.POST['time_to']])
        fmt_24 = "%H%M"
        fmt_date = "%d/%m/%Y"

        if (not time_from and time_to) or (not time_to and time_from):
            raise exc.HTTPBadRequest('If you want a time range, please specify a time from and time to')
        if time_from:
            time_from = datetime.datetime.strptime(time_from, fmt_24)
            time_to = datetime.datetime.strptime(time_to, fmt_24)
            plugin.time_to = time_to
            plugin.time_from = time_from
        else:
            plugin.time_from = None
            plugin.time_to = None
        if POST['date_from']:
            date_from = datetime.datetime.strptime(POST['date_from'], fmt_date)
            plugin.date_from = date_from
        else:
            plugin.date_from = None
        if POST['days']:
            days = POST['days'][:7]
            if not re.match("[0|1]{7}", days):
                raise exc.HTTPBadRequest("Days must have 7 valid days")
            print "Setting days", days
            if "1" in days:
                plugin.days_of_week = days
            else:
                plugin.days_of_week = None
        else:
            plugin.days_of_week = None

        if POST['code']:
            plugin.code = POST['code']
        if POST['repeats']:
            repeats = int(POST['repeats'])
            plugin.repeats = max(0, repeats)
        else:
            plugin.repeats = None
        if POST['enabled']:
            plugin.enabled = POST['enabled'] == 'true'
        if POST['length']:
            plugin.length = POST['length']
        return {'success': True}


@view_config(route_name='register', renderer='json', request_method='POST')
def register_post(request):
    email = request.params.get('email', None)
    password = request.params.get('password', None)
    if not (email and password):
        return {'error': "Please provide a username and email"}
    user = request.db_session.query(LedUser).filter(LedUser.email == email).first()
    if user:
        # user exists
        return {'error': 'User already exists'}
    else:
        # make the user
        new_user = LedUser(email=email, password=hashlib.sha512(password).hexdigest())
        request.db_session.add(new_user)
        return {'success': 'Successfully made an account, please login'}
