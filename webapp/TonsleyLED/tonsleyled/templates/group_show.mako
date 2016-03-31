<%include file="header.html"/>

<div class="container" style="padding-top:50px">
    <div class="row" style="padding-top:20px">
         <div class="col-lg-6">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Plugins
                </div>
                <table class="table table-hover table-bordered table-striped">
                    <thead>
                    <tr>
                        % for i in  ('Name','Author', 'Position'):
                            <th data-field="${i}">${i}</th>
                        % endfor
                    </tr>
                    </thead>
                    <tbody>
                        % for plugin in schedule:
                            <tr>
                                <td>${plugin.led_plugin.name}</td>
                                <td><a href="/users/${plugin.led_plugin.user_id}">${plugin.led_plugin.user.email}</a></td>
                                <td><i class="fa fa-arrow-up row-up"></i> <i class="fa fa-arrow-down row-down"></i></td>
                            </tr>
                        % endfor
                    </tbody>
                </table>

            </div>
        </div>
        <div class="col-lg-6">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Group Members
                </div>
                <table class="table table-hover table-bordered table-striped">
                    <thead>
                    <tr>
                        % for i in  ('Name', 'Role'):
                            <th data-field="${i}">${i}</th>
                        % endfor
                    </tr>
                    </thead>
                    <tbody>

                        % for user in users:
                            <tr>
                                <td><a href="/user/${user.led_user_id}">${user.led_user.email}</a></td>
                                <td>${user.access_level}</td>
                            </tr>
                        % endfor
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
</div>
<script>

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
        var row_map = {};
        rows.each(function () {
            row_map[$(this).data('id')] = $(this).index();
        });
        console.log(row_map);
        $.post("/plugin/positions/update", row_map, function (data) {
            console.log(data);
        });
    });

</script>
<%include file="footer.html"/>
