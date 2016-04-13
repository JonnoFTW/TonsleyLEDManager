<%include file="header.html"/>
<div class="container" style="padding-top:50px">
    <div class="row" style="padding-top:20px">
        <div class="col-lg-6">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-user"></i> Users
                </div>

                <div class="input-group"><span class="input-group-addon"> <i class="fa fa-search fa-fw"></i></span>
                    <input id="filter" type="text" class="form-control" placeholder="Type here...">
                </div>
                <table class="table table-hover table-bordered table-striped sortable" id="user-table">
                    <thead>
                    <tr>
                        % for i in ('Email', 'Access Level', 'Delete'):
                            <th data-field="${i}">${i}</th>
                        % endfor
                    </tr>
                    </thead>
                    <tbody class="searchable rows">
                        % for user in users:
                        <tr class="clickable-row" data-id="${user.id}">
                            <td><a href="/users/${user.id}">${user.email}</a></td>
                            <td><select data-user-id="${user.id}" class="user_level show-tick" data-width="fit">
                                <option value="0"
                                    %if user.access_level == 0:
                                        selected
                                    %endif
                                >Member
                                </option>
                                <option value="2"
                                    %if user.access_level == 2:
                                        selected
                                    %endif
                                >Admin
                                </option>
                            </select></td>
                            <td>
                                <form id="delete-${user.id}" method="POST" action="/users/${user.id}/delete">
                                    <input type="hidden" value="${user.id}" name="user-id"/>
                                    <button type="submit" data-id="${user.id}" value="submitted" class="save btn btn-warning delete-user">Delete</button>
                                </form>

                            </td>
                        % endfor
                    </tbody>
                </table>
            </div>
        </div>
        <div class="col-lg-6">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-plus fa-fw"></i> New Users
                </div>
                <div class="panel-body">
                    <form class="form-horizontal" id="new-plugin-form" method="POST">
                        <div class="form-group">
                            <label for="inputLength" class="col-sm-2 control-label">Emails</label>
                            <div class="col-sm-10">
                                <textarea class="form-control" id="inputSource" name="emails"
                                          placeholder="fan0001,fami0002"></textarea>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="col-sm-offset-2 col-sm-10">
                                <button type="submit" name="form.submitted" class="btn btn-default">Add</button>
                            </div>
                        </div>
                        <div class="form-group">
                            <div class="col-sm-offset-2 col-sm-10">
                                <div style="display: none" id="submit-message" class="alert alert-danger" role="alert">
                                    Error
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    $('.user_level').selectpicker({
        size: 4
    }).on('change', function() {
##         console.log($(this));
        var user_id = $(this).data('user-id');
        var obj = {access_level:parseInt($(this).val())};
##         console.log(obj);
        $.post('/users/'+user_id+'/level',obj, function(d){console.log(d);});
    });

</script>
<%include file="footer.html"/>
