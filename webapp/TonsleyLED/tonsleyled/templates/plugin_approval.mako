<%include file="header.html"/>
<div class="container" style="padding-top:50px">
    <div class="row" style="padding-top:20px">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    Proposed Changes
                </div>
                <table class="table table-bordered table-striped table-hover">
                    <thead>
                    <tr>
                        % for title in ['Name', 'Approve', 'Reject']:
                            <th>${title}</th>
                        % endfor
                    </tr>
                    </thead>
                    <tbody>
                        % for row in plugins:
                            <tr data-id="${row.led_plugin_id}">
                                <td><a href="/plugin/${row.led_plugin_id}">${row.led_plugin.name}</a></td>
                                <td>
                                    <form action="/plugin/${row.led_plugin_id}/approve" method="POST">
                                        <button type="submit" class="btn btn-success">Approve</button>
                                    </form>
                                </td>
                                <td>
                                    <form action="/plugin/${row.led_plugin_id}/reject" method="POST">
                                        <button type="submit" class="btn btn-danger">Reject</button>
                                    </form>
                                </td>
                            </tr>
                        % endfor
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-lg-6" id="code-preview">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Old Plugin Code
                </div>
                <div class="panel-body">
                    <textarea id="code_old" class="form-control"></textarea>
                </div>
            </div>
        </div>
        <div class="col-lg-6" id="code-preview">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Plugin Code
                </div>
                <div class="panel-body">
                    <textarea id="code_new" class="form-control"></textarea>
                </div>
            </div>

        </div>
    </div>
</div>
<script>
        <%
            import json
        %>
    var editor_new = CodeMirror.fromTextArea(document.getElementById("code_new"), {
        mode: {name: 'python'},
        lineNumbers: true,
        readOnly: true
    });
    var editor_old = CodeMirror.fromTextArea(document.getElementById("code_old"), {
        mode: {name: 'python'},
        lineNumbers: true,
        readOnly: true
    });
    var codes = {
        %for i in plugins:
            ${i.led_plugin_id}: {
                old_code: ${json.dumps(i.led_plugin.code) |n},
                new_code: ${json.dumps(i.code) |n}
            },
        %endfor
    }

    $('tbody > tr').click(function () {
        var id = $(this).data('id');
        editor_new.setValue(codes[id].new_code);
        editor_old.setValue(codes[id].old_code);
    });


    // when you click on a table row, it should fill the 2 editors

</script>
<%include file="footer.html"/>
