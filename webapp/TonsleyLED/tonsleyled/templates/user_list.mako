<%include file="header.html"/>
<div class="container"  style="padding-top:50px">
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
                            <td>${user.access_level}</td>
                            <td><button data-id="${user.id}" class="save btn btn-warning">Delete</button></td>
                        % endfor
                    </tbody>
                </table>
            </div>
        </div>
        <div class="col-lg-6" >
            <div class="panel panel-default">
                <div class="panel-heading" >
                    <i class="fa fa-plus fa-fw"></i> New Users
                </div>
                <div class="panel-body">
                    <form class="form-horizontal" id="new-plugin-form">
                      <div class="form-group">
                        <label for="inputLength" class="col-sm-2 control-label">Emails</label>
                        <div class="col-sm-10">
                          <textarea class="form-control" id="inputSource" name="emails" placeholder="a@flinders.edu.au,b@flinders.edu.au"></textarea>
                        </div>
                      </div>
                      <div class="form-group">
                        <div class="col-sm-offset-2 col-sm-10">
                          <button type="submit" name="form.submitted" class="btn btn-default">Add</button>
                        </div>
                      </div>
                        <div class="form-group">
                        <div class="col-sm-offset-2 col-sm-10">
                            <div style="display: none" id="submit-message" class="alert alert-danger" role="alert">Error</div>
                        </div>
                    </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
<script>

</script>

<%include file="footer.html"/>
