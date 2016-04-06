<%include file="header.html"/>
<%
    def checked(val):
        if val:
            return "checked"
        else:
            return ""
%>

<div class="container" style="padding-top:50px">
    <div class="row" style="padding-top:20px">
        <div class="col-lg-8">
            <div class="panel panel-default">
                <div class="panel-heading">
                    % if group_admin:

                        <button class="btn btn-sm btn-primary pull-right" id="save-btn">Save</button>
                    %endif


                    ##                     <i class="fa fa-info fa-fw"></i>

                    <small class="panel-title">Plugins</small>
                </div>
                <table class="table table-hover table-bordered table-striped">
                    <thead>
                    <tr>
                        <%
                            cols = ['Name','Author','Duration (s)']
                            if group_admin:
                                cols.extend(['Enabled' ,'Position', 'Message?', 'Delete'])
                        %>
                        % for i in  cols:
                            <th data-field="${i}">${i}</th>
                        % endfor
                    </tr>
                    </thead>
                    <tbody id="plugins">
                        % for plugin in schedule:
                            <tr data-plugin-id="${plugin.led_plugin_id}">
                                <td><a href="/plugin/${plugin.led_plugin.id}">${plugin.led_plugin.name}</a></td>
                                <td><a href="/users/${plugin.led_plugin.user_id}">${plugin.led_plugin.user.email}</a>
                                </td>
                                % if group_admin:
                                    <td><input type="number" style="width:40px" value="${plugin.duration}" type="number" min="0"/></td>
                                    <td><input type="checkbox" ${checked(plugin.enabled)}/></td>
                                    <td><i class="fa fa-arrow-up row-up"></i> <i class="fa fa-arrow-down row-down"></i>
                                    </td>
                                    <td class="message">
                                        ## message?
                                        % if 'message' in plugin.led_plugin.name.lower():
                                            <input type="text" value="${plugin.message}"/>
                                        % endif
                                    </td>
                                    <td>
                                        <form method="POST" action="/group/${group.id}/plugins/delete">
                                            <input type="hidden" name="plugin_id" value="${plugin.led_plugin_id}"/>
                                            <button class="btn btn-danger btn-sm" id="delete-btn"
                                                    data-plugin-id="${plugin.led_plugin_id}">Remove
                                            </button>
                                        </form>
                                    </td>
                                % endif
                            </tr>
                        % endfor
                    </tbody>
                </table>
                %if group_admin:

                    <div class="panel-heading">
                        Add Plugins
                    </div>
                    <div class="panel-body">
                        ## list all plugins here

                        <form method="POST" action="/group/${group.id}/plugins/add">
                            <select class="selectpicker" data-live-search="true" multiple name="plugins">
                                ## list all users not in the group
                                % for plugin in other_plugins:
                                <option value="${plugin.id}">${plugin.name}</option>
                            % endfor
                            </select>
                            <button class="btn btn-primary">Save</button>
                        </form>
                    </div>
                %endif
            </div>
        </div>
        <div class="col-lg-4">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Group Members
                </div>
                <table class="table table-hover table-bordered table-striped">
                    <thead>
                    <tr>
                        <%
                            cols = ['Name', 'Role']
                            if group_admin:
                                cols.append('Delete')
                        %>
                        % for i in  cols:
                            <th data-field="${i}">${i}</th>
                        % endfor
                    </tr>
                    </thead>
                    <tbody>

                        % for user in users:
                            <tr>
                                <td><a href="/user/${user.led_user_id}">${user.led_user.email}</a></td>
                                <td>
                                    <select data-user-id="${user.led_user_id}" class="user_level show-tick" data-width="fit">
                                        <option value="0"
                                                %if user.access_level == 0:
                                                selected
                                                %endif
                                        >Member</option>
                                        <option value="2"
                                        %if user.access_level == 2:
                                        selected
                                        %endif
                                        >Admin</option>
                                    </select>

                                </td>
                                %if group_admin:
                                    <td>
                                        <form action="/group/${group.id}/users/delete" method="POST">
                                            <input type="hidden" name="user_id" value="${user.led_user_id}"/>
                                            <button name="submitted" class="btn btn-danger btn-sm"
                                                    id="delete-user-from-group"
                                                    data-user-id="${user.led_user_id}">Remove
                                            </button>
                                        </form>
                                    </td>
                                %endif
                            </tr>
                        % endfor
                    </tbody>
                </table>
                % if group_admin:

                    <div class="panel-heading">Add Group Members</div>
                    <div class="panel-body">
                        <form method="POST" action="/group/${group.id}/users">
                            <select class="selectpicker" data-live-search="true" multiple name="users">
                                ## list all users not in the group
                                % for user in other_users:
                                <option value="${user.id}">${user.email}</option>
                            % endfor
                            </select>
                            <button class="btn btn-primary">Save</button>
                        </form>
                    </div>

                % endif
            </div>
        </div>
    </div>
</div>
</div>
% if group_admin:

<script>
$(document).ready(function(){

    $('.selectpicker').selectpicker({
        size: 4
    });
    $('.user_level').selectpicker({
        size: 4
    }).on('change', function() {
        console.log($(this));
        var obj = {user_id:$(this).data('user-id'), access_level:parseInt($(this).val())};
        console.log(obj);
        $.post('/group/${group.id}/users/level',obj);
    });


    $('i.row-up, i.row-down').click(function () {
        // move the table row up
        // should call a position setting api
        var row = $(this).parent().parent();
        var rows = row.parent().children();
        var idx = row.index();

        if ($(this).hasClass('row-up') && idx > 0) {
            rows.eq(idx - 1).before(row);
        } else {
            rows.eq(idx + 1).after(row);
        }
    });
    $('#save-btn').click(function () {
        var rows = $('#plugins').children();
        var row_map = {};
        rows.each(function () {

            row = $(this).children();
            var msg = $(this).find('.message > input').val();
            row_map[$(this).data('plugin-id')] = {
                position: $(this).index(),
                duration: parseInt(row.eq(2).find('input').val()),
                message: msg,
                enabled: row.eq(3).find('input').is(':checked')
            }
        });
        console.log(row_map);
        $.post("/schedule/${group.id}", row_map, function (data) {
            console.log(data);
        });
    });
    $('#delete-btn').click(function () {
        var plugin_id = $(this).data('plugin-id');
        $.ajax()
    });
 });
</script>
% endif
<%include file="footer.html"/>
