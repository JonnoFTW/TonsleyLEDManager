import random
import re
import validate_email
from pluck import pluck
# import ldap
from pyramid.security import remember
from pyramid.view import view_config, forbidden_view_config

from pyramid.view import view_config, forbidden_view_config, notfound_view_config
from pyramid.security import remember, forget, Authenticated, Allow
import pyramid.httpexceptions as exc
from sqlalchemy import and_, update
import datetime
from models import LedSchedule, LedUser, LedGroup, LedPlugin, LedGroupUser

"""
Helper functions and wrapppers
"""
def get_user(request):
    return request.db_session.query(LedUser).filter(LedUser.id == request.authenticated_userid).first()

def admin_only(func):
    def _admin_only(*args, **kwargs):
        user = args[1].db_session.query(LedUser).filter(and_(LedUser.access_level == 2, LedUser.id == args[1].authenticated_userid)).first()
        if user is None:
            raise exc.HTTPForbidden('You do not have sufficient permissions to view this page')
        return func(args, **kwargs)
    return _admin_only

def authenticate(func):
    def auth_only(*args, **kwargs):
        if len(args) == 1:
            args = args[0]
        # print "auth uid is", request.authenticated_userid
        if args[1].authenticated_userid is None:
            raise exc.HTTPFound(location='/login')
        return func(args[1], **kwargs)
    return auth_only

def get_all_plugins(request):
    query = request.db_session.query(LedPlugin)
    user = get_user(request)
    if user is not None and user.access_level != 2:
        query.filter(LedPlugin.user == user)
    return {
        'plugins': query.all()
    }

"""
Misc Stuff
"""
@view_config(route_name='home', renderer='templates/home.mako')
def home(request):
    return {}


@view_config(route_name='help', renderer='templates/help.mako', request_method='GET')
def help_get(request):
    return {}


"""
Managing Plugins
"""

@view_config(route_name='plugin', renderer='templates/plugin_list.mako', request_method='GET')
@authenticate
def list_plugins(request):
    """List plugins
    """
    print request.exception
    return get_all_plugins(request)


@view_config(route_name='plugin', renderer='templates/plugin_list.mako', request_method='POST')
@authenticate
def create_plugin(request):
    """
    Create a plugin
    """
    try:
        print request.POST
        code = request.POST['source']
        name = request.POST['name']
        userid = request.authenticated_userid
    except KeyError as e:
        return {'error': "Missing "+e.message}
    except Exception as e:
        return {'error': e.message}
    plugin = LedPlugin(name=name, code=code, user_id=userid)
    request.db_session.add(plugin)
    request.db_session.flush()
    return get_all_plugins(request)

@view_config(route_name='plugin_update', renderer='json', request_method='DELETE')
@authenticate
def delete_plugin(request):
    """
    Delete A plugin
    """
    plugin_id = request.matchdict['plugin_id']
    request.db_session.query(LedPlugin).filter(LedPlugin.id == plugin_id).delete()
    request.db_session.flush()
    return {'msg': 'Deleted'}



@view_config(route_name='plugin_update', renderer='json', request_method='POST')
@authenticate
def update_plugin(request):
    # make sure the plugin id exists
    plugin_id = request.matchdict['plugin_id']
    plugin = request.db_session.query(LedPlugin).filter(LedPlugin.id == plugin_id).first()
    if not plugin:
        raise exc.HTTPBadRequest("No such plugin")
    else:
        def to_null(val):
            if val == '':
                return None
            return val
        POST = {k: to_null(v) for k, v in request.POST.items()}
        if POST['code']:
            plugin.code = POST['code']
        if POST['name']:
            plugin.name = POST['name']
        request.db_session.flush()
        return {
            'success': True
        }




"""
Update the Schedule of a group
"""

@view_config(route_name='schedule_update', renderer='json', request_method='POST')
@authenticate
def update_schedule(request):
    # post args should be a mapping of plugin_id -> position
    for plugin_id, position in request.POST.items():
        plugin = request.db_session.query(LedSchedule).filter(LedSchedule.id == plugin_id).first()
        plugin.position = position
    return {'message': 'Done'}


"""
Manage A Group
"""
@view_config(route_name='group_update', renderer='json', request_method='POST')
@authenticate
def update_plugin(request):
    # make sure the plugin id exists
    plugin_id = request.matchdict['plugin_id']
    plugin = request.db_session.query(LedPlugin).filter(LedPlugin.id == plugin_id).first()
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


@view_config(route_name='group', renderer='templates/group_list.mako', request_method='GET')
@authenticate
def list_groups(request):
    # a regular user will have their groups listed
    # admin will see all groups
    user = get_user(request)

    query = request.db_session.query(LedGroup)
    if user.access_level != 2:
        users_groups = request.db_session.query(LedGroupUser).filter(LedGroupUser.led_user == user).all()
        query.filter(LedGroup.id.in_(pluck(users_groups, 'led_group_id')))
    return {
        'groups': query.all()
    }

@view_config(route_name='group_update', renderer='templates/group_show.mako', request_method='GET')
@authenticate
def show_group(request):
    # a regular user will have their groups listed
    # admin will see all groups
    group = request.db_session.query(LedGroup).filter(LedGroup.id == request.matchdict['group_id']).first()
    users = request.db_session.query(LedGroupUser).filter(LedGroupUser.led_group == group).all()
    schedule = request.db_session.query(LedSchedule).filter(LedSchedule.led_group == group).all()
    return {
        'group': group,
        'users': users,
        'schedule': schedule
    }


def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure
    # Adapt to your needs
    """
    LDAP_SERVER = 'ldap://ad.flinders.edu.au'
    # fully qualified AD user name
    LDAP_USERNAME = '%s@flinders.edu.au' % username
    # your password
    LDAP_PASSWORD = password
    base_dn = 'DC=xxx,DC=xxx'
    ldap_filter = 'userPrincipalName=%s@xxx.xx' % username
    attrs = ['memberOf']
    try:
        # build a client
        ldap_client = ldap.initialize(LDAP_SERVER)
        # perform a synchronous bind
        ldap_client.set_option(ldap.OPT_REFERRALS, 0)
        ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
    except ldap.INVALID_CREDENTIALS:
        ldap_client.unbind()
        return False
    except ldap.SERVER_DOWN:
        raise exc.HTTPInternalServerError('Authentication server not available')
    # all is well
    # get all user groups and store it in cerrypy session for future use
    ldap_client.unbind()
    return None


"""
User Stuff
"""
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
        user = request.db_session.query(LedUser).filter(LedUser.email == email).first()
        if user and True:# check_credentials(email, password):
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


@view_config(route_name='users', renderer='templates/user_list.mako', request_method='GET')
@admin_only
@authenticate
def list_users(request):
    # show all users

    return {
       'users': request.db_session.query(LedUser).all()
    }


@view_config(route_name='show_user', renderer='templates/user_show.mako', request_method='GET')
@authenticate
def show_user(request):
    # show a user
    user = request.db_session.query(LedUser).filter(LedUser.id == request.matchdict['user_id']).first()
    plugins = request.db_session.query(LedPlugin).filter(LedPlugin.user == user).all()
    groups = request.db_session.query(LedGroupUser).filter(LedGroupUser.led_user == user).all()
    return {
       'user': user,
       'plugins': plugins,
       'groups': groups
    }

@view_config(route_name='users', renderer='json', request_method='POST')
@admin_only
@authenticate
def create_user(request):
    # create a user, generate a password and send it to them in an email
    # comma separated emails will make users for all of them
    # user must be a flinders address
    # all users are unnassociated with a particular group by default
    if request.POST.get('emails', None):
        for email in request.POST['emails'].split(','):
            if not validate_email(email) or not email.endswith('@flinders.edu.au'):
                continue
            user = LedUser(email=email, access_level=0)
            request.db_session.add(user)
    request.db_session.flush()
    return {
       'users': request.db_session.query(LedUser).all()
    }




"""
Error Views
"""

@view_config(context=exc.HTTPNotFound, renderer='templates/404.mako')
def not_found(self, request):
    request.response.status = 404
    return {}