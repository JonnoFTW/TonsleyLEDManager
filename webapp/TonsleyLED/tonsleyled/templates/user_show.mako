<%include file="header.html"/>

<div class="container" style="padding-top:50px">
    <div class="row" style="padding-top:20px">
        <h1>${user.email}</h1>
        <div class="col-lg-6">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Users Plugins
                </div>
                <table class="table table-hover table-bordered table-striped sortable" id="node-table">
                    <thead>
                    <tr>
                        <th data-field="name">Name</th>

                    </tr>
                    </thead>
                    <tbody class="searchable rows">
                        % for plugin in plugins:
                            <tr class="clickable-row" data-id="${plugin.id}">
                                <td><a href="/plugin/${plugin.id}">${plugin.name}</a></td>
                            </tr>
                        %endfor
                    </tbody>
                </table>
            </div>
        </div>
        % if request.user.admin or request.user.id == user.id:

            <div class="col-lg-6">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <i class="fa fa-info fa-fw"></i> Groups
                    </div>
                    <table class="table table-hover table-bordered table-striped sortable">
                        <thead>
                        <tr>
                            <th data-field="name">Name</th>
                            <th data-field="level">Level</th>
                        </tr>
                        </thead>
                        <tbody>
                            % for group in groups:
                                <tr data-id="${group.led_group_id}">
                                    <td><a href="/group/${group.led_group_id}">${group.led_group.name}</a></td>
                                    <td>${group.access_level}</td>
                                </tr>
                            %endfor
                        </tbody>
                    </table>
                </div>
            </div>
        % endif
    </div>
    <div class="row">
        <div class="col-lg-12" id="code-preview">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Source
                </div>
                <div class="panel-body">
                    <textarea id="code" class="form-control" style="height:800px"></textarea>
                </div>
            </div>
        </div>
    </div>

</div>
<%include file="codemirror.mako"/>
<%include file="footer.html"/>
