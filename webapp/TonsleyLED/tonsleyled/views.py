import re
from collections import defaultdict
from pluck import pluck
from ldap3 import Server, Connection, ALL, NTLM
from pyramid.security import remember
from pyramid.view import view_config, forbidden_view_config

from pyramid.view import view_config, forbidden_view_config, notfound_view_config
from pyramid.security import remember, forget, Authenticated, Allow
import pyramid.httpexceptions as exc
from sqlalchemy import and_, update, exc as sql_exc, func

import datetime
from models import LedSchedule, LedUser, LedGroup, LedPlugin, LedGroupUser, LedLog, LedPluginProposed

"""
Helper functions and wrapppers
"""


def get_user_by_id(request, id):
    return request.db_session.query(LedUser).filter(LedUser.id == id).first()


def log(request, msg):
    return request.db_session.add(LedLog(datetime=datetime.datetime.now(), email=request.user.email, action=msg))


def admin_only(func):
    def _admin_only(*args, **kwargs):
        user = args[1].user
        if user is None or not user.admin:
            print user, "is forbidden"
            raise exc.HTTPForbidden('You do not have sufficient permissions to view this page')
        return func(args, **kwargs)
    return _admin_only


def authenticate(func):
    def auth_only(*args, **kwargs):
        if len(args) == 1:
            args = args[0]
        # print "auth uid is", request.authenticated_userid
        if args[1].authenticated_userid is None:
            print "Not logged in!"
            raise exc.HTTPFound(location='/login')
        return func(args[1], **kwargs)
    return auth_only


def get_all_plugins(request):
    query = request.db_session.query(LedPlugin)
    if request.user is not None and request.user.admin:
        query.filter(LedPlugin.user == request.user)
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
    return get_all_plugins(request)



@view_config(route_name='plugin', renderer='templates/plugin_list.mako', request_method='POST')
@authenticate
def create_plugin(request):
    """
    Create a plugin
    """
    try:
        # print request.POST
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
    log(request, 'Created plugin <a href="/plugin/{}">{}</a>'.format(plugin.id ,plugin.name))
    return get_all_plugins(request)

@view_config(route_name='plugin_delete', request_method='POST')
@authenticate
def delete_plugin(request):
    """
    Delete A plugin
    """
    plugin_id = request.matchdict['plugin_id']
    user = request.user
    query = request.db_session.query(LedPlugin).filter(LedPlugin.id == plugin_id)
    plugin = query.first()
    if plugin is None:
        raise exc.HTTPBadRequest('No such plugin')
    if user != plugin.user and not user.admin:
        raise exc.HTTPForbidden("You don't have access to do that")
    request.db_session.query(LedPluginProposed).filter(LedPluginProposed.id == plugin_id).delete()
    query.delete()
    log(request, 'Deleted plugin ' + plugin.name)
    return exc.HTTPFound(location='/plugin')


@view_config(route_name='plugin_update', renderer='templates/plugin_show.mako', request_method='GET')
def show_plugin(request):
    plugin = request.db_session.query(LedPlugin).filter(LedPlugin.id == request.matchdict['plugin_id']).first()
    if plugin is None:
        raise exc.HTTPNotFound()
    groups = request.db_session.query(LedSchedule).filter(LedSchedule.led_plugin == plugin).all()
    return {
        'plugins': [plugin],
        'groups': groups
    }


def to_null(val):
    if val == '':
        return None
    return val


@view_config(route_name='plugin_approve', renderer='templates/plugin_approval.mako')
@admin_only
@authenticate
def plugin_approve_list(request):
    return {
        'plugins': request.db_session.query(LedPluginProposed).all()
    }


@view_config(route_name='plugin_approve_update', request_method='POST')
@admin_only
@authenticate
def approve_plugin_update(request):
    plugin_id = request.matchdict['plugin_id']
    plugin_update_query = request.db_session.query(LedPluginProposed).filter(LedPluginProposed.led_plugin_id == plugin_id)
    plugin_update = plugin_update_query.first()
    if plugin_update is None:
        raise exc.HTTPBadRequest("No such plugin to update")
    plugin = request.db_session.query(LedPlugin).filter(LedPlugin.id == plugin_id).first()
    plugin.code = plugin_update.code
    plugin_update_query.delete()
    log(request, 'Approved updates to plugin <a href="/plugin/{}">{}</a>'.format(plugin.id, plugin.name))
    return exc.HTTPFound(location='/plugin_approve')


@view_config(route_name='plugin_reject_update', request_method='POST')
@admin_only
@authenticate
def reject_plugin_update(request):
    plugin_id = request.matchdict['plugin_id']
    plugin_query = request.db_session.query(LedPluginProposed).filter(LedPluginProposed.led_plugin_id == plugin_id)
    plugin_update = plugin_query.first()
    if plugin_update is None:
        raise exc.HTTPBadRequest("No proposal for this plugin")
    plugin = plugin_update.led_plugin
    plugin_query.delete()
    log(request, 'Rejected updates to plugin <a href="/plugin/{}">{}</a>'.format(plugin.id, plugin.name))
    return exc.HTTPFound(location='/plugin_approve')



@view_config(route_name='plugin_update', renderer='json', request_method='POST')
@authenticate
def update_plugin(request):
    # make sure the plugin id exists
    plugin_id = request.matchdict['plugin_id']
    plugin = request.db_session.query(LedPlugin).filter(LedPlugin.id == plugin_id).first()
    if not plugin:
        raise exc.HTTPBadRequest("No such plugin")
    else:
        # only a site admin or plugin owner can edit

        # a non-admin plugin owner can suggest changes
        user = request.user
        if user != plugin.user and not user.admin:
            raise exc.HTTPForbidden("You don't have access to do that")
        POST = {k: to_null(v) for k, v in request.POST.items()}
        if not user.admin:
            if 'code' not in POST:
                raise exc.HTTPBadRequest("Please provide the code")
            plugin_update = request.db_session.query(LedPluginProposed).filter(LedPluginProposed.led_plugin_id == plugin_id).first()
            if plugin_update is not None:
                    plugin_update.code = POST['code']
            else:
                request.db_session.add(LedPluginProposed(led_plugin_id=plugin_id, code=POST['code']))
            log(request, "Proposed changes to plugin <a href='/plugin/{}'>{}</a>".format(plugin.id, plugin.name))
            return {
                'msg': 'Your update is now awaiting approval'
            }

        else:
            if POST['code']:
                plugin.code = POST['code']
            if 'name' in POST and POST['name']:
                plugin.name = POST['name']
            log(request, 'Updated <a href="/plugin/{0}">plugin {1}</a>: '.format(plugin_id, plugin.name, ))
            return {
                'msg': 'Updated code'
            }


def post_to_dict(post):
    out = defaultdict(defaultdict)

    for id, data in post.items():
        if data.lower() == 'true':
            data = True
        elif data.lower() == 'false':
            data = False
        matches = re.match(r'(.*)\[(.*)]', id)
        out[matches.group(1)][matches.group(2)] = data
    return out

"""
Update the Schedule of a group
"""

@view_config(route_name='schedule_update', renderer='json', request_method='POST')
@authenticate
def update_schedule(request):
    # post args should be a mapping of plugin_id -> [position, enabled, duration]
    group_id = request.matchdict['group_id']
    # print request.POST
    for plugin_id, data in post_to_dict(request.POST).items():

        plugin = request.db_session.query(LedSchedule).filter(
            and_(LedSchedule.led_plugin_id == plugin_id,
                 LedSchedule.led_group_id == group_id)).first()
        plugin.position = data['position']
        plugin.enabled = data['enabled']
        plugin.duration = data['duration']
        if 'message' in data:
            plugin.message = data['message']
        else:
            plugin.message = None
    log(request, 'Updated plugin schedule for <a href="/group/{}">{}</a>'.format(plugin.led_group_id, plugin.led_group.name))
    return {'message': 'Done'}


"""
Manage A Group
"""
@view_config(route_name='group_update', renderer='json', request_method='POST')
@authenticate
def update_group_plugins(request):
    # make sure the plugin id exists

    group_id = request.matchdict['group_id']
    can_modify_group(request, group_id)
    group = request.db_session.query(LedGroup).filter(LedGroup.id == group_id).first()
    if not group:
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
            group.time_to = time_to
            group.time_from = time_from
        else:
            group.time_from = None
            group.time_to = None
        if POST['date_from']:
            date_from = datetime.datetime.strptime(POST['date_from'], fmt_date)
            group.date_from = date_from
        else:
            group.date_from = None
        if POST['days']:
            days = POST['days'][:7]
            if not re.match("[0|1]{7}", days):
                raise exc.HTTPBadRequest("Days must have 7 valid days")
            # print "Setting days", days
            if "1" in days:
                group.days_of_week = days
            else:
                group.days_of_week = None
        else:
            group.days_of_week = None
        if POST['repeats']:
            repeats = int(POST['repeats'])
            group.repeats = max(0, repeats)
        else:
            group.repeats = None
        if POST['enabled']:
            group.enabled = POST['enabled'] == 'true'
        log(request, "Updated scheduling for <a href='/group/{}'>{}</a>".format(group.id, group.name))
        return {'success': True}


@view_config(route_name='group_delete', request_method='POST')
@admin_only
@authenticate
def delete_group(request):
    gid = request.matchdict['group_id']
    group = request.db_session.query(LedGroup).filter(LedGroup.id == gid).first()
    if group is None:
        raise exc.HTTPNotFound("No such group")
    request.db_session.query(LedSchedule).filter(LedSchedule.led_group == group).delete()
    request.db_session.query(LedGroupUser).filter(LedGroupUser.led_group == group).delete()
    log(request, 'Delete group {}'.format(group.name))
    request.db_session.delete(group)
    return exc.HTTPFound(location='/group')


def can_modify_group(request, gid, raise_exc=True):
    user = request.user
    if user.admin:
        return True
    group_user = request.db_session.query(LedGroupUser).filter(and_(
        LedGroupUser.led_group_id == gid,
        LedGroupUser.led_user == user)).first()
    if group_user is None or group_user.access_level != 2:
        if raise_exc:
            raise exc.HTTPForbidden("You can't modify this group")
        return False
    return True


@view_config(route_name='group_plugins_delete', request_method='POST')
@admin_only
@authenticate
def delete_group_plugin(request):
    gid = request.matchdict['group_id']
    can_modify_group(request, gid)
    plugin_id = request.POST['plugin_id']
    query = request.db_session.query(LedSchedule).filter(and_(LedSchedule.led_group_id == gid,
                                                      LedSchedule.led_plugin_id == plugin_id))
    sched = query.first()
    if sched is None:
        return exc.HTTPBadRequest("Plugin does not exist in that schedule")
    query.delete()
    log(request, 'Removed plugin <a href="/plugin/{0}">{1}</a> from schedule of group <a href="/group/{2}">{3}</a>'.
        format(sched.led_plugin_id, sched.led_plugin.name, sched.led_group_id, sched.led_group.name))
    return exc.HTTPFound(location='/group/' + gid)


@view_config(route_name='group_plugins_add', request_method='POST')
@admin_only
@authenticate
def add_group_plugin(request):
    # make sure the users are in the group:
    # only a site admin or group admin can do this

    gid = request.matchdict['group_id']
    can_modify_group(request, gid)
    plugins = request.POST.get('plugins', None)
    # print request.POST.values()
    if plugins is None:
        return exc.HTTPFound(location='/group/' + gid)
    for plugin in request.POST.values():
        scheduled_plugin = LedSchedule(led_group_id=gid, led_plugin_id=int(plugin), duration=30, enabled=True, position=9)
        try:
            request.db_session.add(scheduled_plugin)
        except sql_exc.DatabaseError as e:
            print scheduled_plugin, "already in scheduled"
    return exc.HTTPFound(location='/group/' + gid)


@view_config(route_name='group_update_user_level', request_method='POST')
@admin_only
@authenticate
def update_group_user_level(request):
    # only a group admin should be able to do this
    gid = request.matchdict['group_id']
    can_modify_group(request, gid)
    user_id = request.POST['user_id']
    access_level = int(request.POST['access_level'])
    if access_level in [0, 2]:
        user = request.db_session.query(LedGroupUser).filter(
            and_(LedGroupUser.led_group_id == gid,
                 LedGroupUser.led_user_id == user_id)).first().access_level = access_level
    return exc.HTTPFound(location='/group/'+gid)




@view_config(route_name='group_delete_user', request_method='POST')
@admin_only
@authenticate
def delete_group_user(request):
    gid = request.matchdict['group_id']
    can_modify_group(request, gid)

    user_id = request.POST['user_id']
    request.db_session.query(LedGroupUser).filter(and_(LedGroupUser.led_group_id == gid,
                                                       LedGroupUser.led_user_id == user_id)).delete()
    log(request, 'Removed from  <a href="/group/{0}">group {0}</a>: {1}'.format(gid, get_user_by_id(request, user_id).email))
    return exc.HTTPFound(location='/group/' + gid)


@view_config(route_name='group_update_users', request_method='POST')
@admin_only
@authenticate
def add_group_users(request):
    # make sure the users are in the group:
    # only a site admin or group admin can do this

    gid = request.matchdict['group_id']
    can_modify_group(request, gid)
    users = request.POST.get('users', None)
    # print request.POST
    if users is None:
        raise exc.HTTPBadRequest('Please specify users to add to the group')
    new_users = []
    for user in request.POST.values():
        group_user = LedGroupUser(led_group_id=gid, led_user_id=user)
        try:
            request.db_session.add(group_user)
            new_users.append(get_user_by_id(request, user).email)
        except sql_exc.DatabaseError as e:
            print group_user, "already in group"
    log(request, 'Added users to <a href="/group/{0}">group {0}</a>: {1}'.format(gid, ', '.join(new_users)))
    return exc.HTTPFound(location='/group/' + gid)


@view_config(route_name='group', renderer='templates/group_list.mako', request_method='GET')
@admin_only
@authenticate
def list_groups(request):
    # a regular user will have their groups listed
    # admin will see all groups
    user = request.user

    query = request.db_session.query(LedGroup)
    users_groups = request.db_session.query(LedGroupUser).filter(LedGroupUser.led_user == user).all()
    if not user.admin:
        query.filter(LedGroup.id.in_(pluck(users_groups, 'led_group_id')))
    groups_admin = [group.led_group_id for group in users_groups if group.access_level == 2]
    return {
        'user_admins': groups_admin,
        'groups': query.all()
    }


@view_config(route_name='group', request_method='POST')
@admin_only
@authenticate
def create_group(request):
    # create a group
    name = request.POST.get('name', None)
    if name is None:
        raise exc.HTTPBadRequest('Please specify a group name')
    group = LedGroup(name=name, default=False, enabled=False)
    request.db_session.add(group)
    request.db_session.flush()
    request.db_session.add(LedGroupUser(
        led_group_id=group.id,
        led_user=request.user,
        access_level=2))
    print("Made group", group)
    log(request, 'Created group <a href="/group/{0}">{1}</a>'.format(group.id, group.name))
    return exc.HTTPFound(location='/group/'+str(group.id))


@view_config(route_name='group_update', renderer='templates/group_show.mako', request_method='GET')
@authenticate
def show_group(request):
    # a regular user will have their groups listed
    # admin will see all groups
    user = request.user
    group = request.db_session.query(LedGroup).filter(LedGroup.id == request.matchdict['group_id']).first()

    users = request.db_session.query(LedGroupUser).filter(LedGroupUser.led_group == group).all()
    if not (user.admin or user.id in pluck(users, 'led_user_id')):
        raise exc.HTTPForbidden("Only site admins or group members can view this")
    schedule = request.db_session.query(LedSchedule).filter(LedSchedule.led_group == group).order_by(LedSchedule.position.asc()).all()
    subquery = request.db_session.query(LedGroupUser.led_user_id).filter(LedGroupUser.led_group == group)
    other_users = request.db_session.query(LedUser).filter(~LedUser.id.in_(subquery))
    subquery = request.db_session.query(LedSchedule.led_plugin_id).filter(LedSchedule.led_group == group)
    # other_plugins = request.db_session.query(LedPlugin).filter(~LedPlugin.id.in_(subquery))
    other_plugins = request.db_session.query(LedPlugin)
    return {
        'group': group,
        'users': users,
        'schedule': schedule,
        'other_users': other_users,
        'other_plugins': other_plugins,
        'group_admin': can_modify_group(request, group.id, False)
    }


def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns True on success or False on failure
    """
    ldap_user = '\\{}@flinders.edu.au'.format(username)
    server = Server('ad.flinders.edu.au', use_ssl=True)

    connection = Connection(server, user=ldap_user, password=password, authentication=NTLM)
    try:
        return connection.bind()
    except:
        return False


"""
User Stuff
"""
@view_config(route_name='login', renderer='templates/login.mako')
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
        if user and check_credentials(email, password):
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


@view_config(route_name='update_user', renderer='json', request_method='POST')
@admin_only
@authenticate
def update_user(request):
    """
    update the user level
    :param request:
    :return:
    """
    user = request.db_session.query(LedUser).filter(LedUser.id == request.matchdict['user_id']).first()

    if user is not None:
        level = request.POST.get('access_level', None)
        if level is not None and int(level) in [0, 2]:
            user.access_level = int(level)
            log(request, 'Updated user {} to level {}'.format(user.email, level))
            return {'message': 'success'}

    else:
        return {'message': "Nothing changed"}


@view_config(route_name='users', renderer='json', request_method='POST')
@admin_only
@authenticate
def create_user(request):
    # create a user, generate a password and send it to them in an email
    # comma separated emails will make users for all of them
    # user must be a flinders address
    # all users are unnassociated with a particular group by default
    users = []
    if request.POST.get('emails', None):
        for email in request.POST['emails'].split(','):
            if not re.match(r"[^\W\d_]{1,4}\d{4}", email):
                continue
            user = LedUser(email=email, access_level=0)
            users.append(email)
            request.db_session.add(user)
    log(request, 'Added users ' + ', '.join(users))
    request.db_session.flush()
    return exc.HTTPFound(location='/users')


@view_config(route_name='user_delete', request_method='POST')
@admin_only
@authenticate
def user_delete(request):
    """
    Deletes a user and their group memberships
    Their plugins will be handed over to the user that deleted them
    :param request:
    :return:
    """
    # make sure the user actually exists
    user_id = request.matchdict['user_id']
    query = request.db_session.query(LedUser).filter(LedUser.id == user_id)
    user = query.first()
    if user is None:
        return exc.HTTPBadRequest("No such user exists")
    logged_in_user = request.user

    for plugin in request.db_session.query(LedPlugin).filter(LedPlugin.user == user).all():
        plugin.user_id = logged_in_user.id
    request.db_session.query(LedGroupUser).filter(LedGroupUser.led_user == user).delete()
    query.delete()
    log(request, 'Deleted user '+user.email)
    return exc.HTTPFound(location='/users')


@view_config(route_name='logs', renderer='templates/logs.mako', request_method='GET')
@admin_only
@authenticate
def show_logs(request):
    limit = 100
    offset = 0
    if 'limit' in request.GET:
        limit = int(request.GET['limit'])
    if 'offset' in request.GET:
        offset = int(request.GET['offset'])
    request.offset = offset
    request.limit = limit
    request.max = request.db_session.query(func.count(LedLog.id)).scalar()
    users = {user.email: user.id for user in request.db_session.query(LedUser).all()}
    return {
        'logs': request.db_session.query(LedLog).order_by(LedLog.datetime.desc()).offset(offset).limit(limit),
        'users': users
    }

"""
Error Views
"""
@view_config(context=exc.HTTPNotFound, renderer='templates/404.mako')
def not_found(self, request):
    request.response.status = 404
    return {}


@forbidden_view_config(renderer='templates/403.mako')
def not_allowed(self, request):
    request.response.status = 403
    return {}