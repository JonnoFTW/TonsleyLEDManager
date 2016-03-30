<%include file="header.html"/>
<div class="container"  style="padding-top:50px">
    <div class="row" style="padding-top:20px">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Plugins
                </div>

                <div class="input-group"><span class="input-group-addon"> <i class="fa fa-search fa-fw"></i></span>
                    <input id="filter" type="text" class="form-control" placeholder="Type here...">
                </div>
                <table class="table table-hover table-bordered table-striped sortable" id="node-table">
                    <thead>
                    <tr>
<%
titles = ('Name', 'Length', 'Author', 'Enabled', 'Time From', 'Time To', 'Days', 'Repeats', 'Date From','Position' ,'Special Event', 'Save')
if request.authenticated_userid is None:
    titles = titles[:4]
%>
                        % for i in titles:
                            <th data-field="${i}">${i}</th>
                        % endfor
                    </tr>
                    </thead>
                    <tbody class="searchable rows">
                        % for plugin in schedule:
                        <tr class="clickable-row" data-id="${plugin.id}">
                            <td>${plugin.name}</td>
                            <td><input type="number" min="0" id="duration" style="width:40px" value="${plugin.length}" /></td>
                            <td>${plugin.user.email.split('@')[0]}</td>
                            <%
                                    checked = ""
                                    if plugin.enabled:
                                        checked = "checked"
                                %>
                            <td><input data-id="${plugin.id}" class="enabler" type="checkbox" ${checked}/></td>
                            % if request.authenticated_userid is not None:
                            <td>
                                <div class="form-group">
                                    <div class='input-group date time_' >
                                        <input type='text' class="form-control" id='time_from' value="${plugin.time_from} " />
                                        <span class="input-group-addon">
                                            <i class="fa fa-clock-o"></i>
                                        </span>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="form-group">
                                    <div class='input-group date time_'>
                                        <input type='text' class="form-control" id='time_to' value="${plugin.time_to}" />
                                        <span class="input-group-addon">
                                            <i class="fa fa-clock-o"></i>
                                        </span>
                                    </div>
                                </div>
                            </td>
                            <td width="150px">
                            %for idx,i in enumerate(['Mo','Tu','We','Th','Fr','Sa','Su']):
<%
                                    checked = ""
                                    if plugin.days_of_week is not None and plugin.days_of_week[idx] == '1':
                                        checked = "checked"
                                %>${i} <input type="checkbox"  name="day_${idx}" ${checked} />
                            %endfor
                            </td>
                                <%
                                  repeats = ""
                                  if plugin.repeats is not None:
                                    repeats = "value={}".format(plugin.repeats)
                                %>
                            <td><input type="number" min="0" id="repeats" style="width:40px" ${repeats} /></td>
                            <td>
                                <div class="form-group">
                                    <div class='input-group date' >
                                        <%
                                            date_from = ""
                                            if plugin.date_from is not None:
                                                date_from = 'value="'+(plugin.date_from.strftime("%d/%m/%Y"))+'"'
                                            %>
                                        <input type='text' class="form-control date_from" ${date_from|n} />
                                        <span class="input-group-addon">
                                            <i class="fa fa-calendar"></i>
                                        </span>
                                    </div>
                                </div>
                            </td>
                                <td><i class="fa fa-2x fa-arrow-up row-up"></i> <i class="fa fa-2x fa-arrow-down row-down"></i></td>
                            <td><button name="special" class="btn btn-warning clear-event">Clear</button></td>
                            <td><button data-id="${plugin.id}" class="save btn btn-primary">Save</button></td>
                            %endif
                        % endfor
                    </tbody>
                </table>
            </div>
        </div>
        <div class="col-lg-6" id="code-preview">
            <div class="panel panel-default">
                <div class="panel-heading" >
                    <i class="fa fa-info fa-fw"></i> Source
                </div>
                <div class="panel-body">
                <textarea id="code" class="form-control"></textarea>
                </div>
            </div>
            % if request.authenticated_userid is not None:
        </div>
        <div class="col-lg-6" >
            <div class="panel panel-default">
                <div class="panel-heading" >
                    <i class="fa fa-info fa-fw"></i> New Plugin
                </div>
                <div class="panel-body">
                    <form class="form-horizontal" id="new-plugin-form">
                      <div class="form-group">
                        <label for="inputEmail3" class="col-sm-2 control-label">Name</label>
                        <div class="col-sm-10">
                          <input type="text" class="form-control" name="name" id="inputName" placeholder="Plugin Name">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="inputLength" class="col-sm-2 control-label">Length</label>
                        <div class="col-sm-10">
                          <input type="number" class="form-control" id="inputLength" name="length" placeholder="Seconds">
                        </div>
                      </div>
                      <div class="form-group">
                        <label for="inputLength" class="col-sm-2 control-label">Source</label>
                        <div class="col-sm-10">
                          <textarea class="form-control" id="inputSource" name="source" placeholder="while 1: print 1"></textarea>
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
                 % endif
        </div>

    </div>
</div>
<script>
var plugins = {
    % for plugin in schedule:
        ${plugin.id}: [
        %for line in plugin.code.splitlines():
             "${line.replace('"', '\\"') |n}",
        %endfor
        ].join("\n"),
    % endfor
};
var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    mode: {name:'python'},
    lineNumbers: true
});
var current_id = -1;
editor.on("change", function() {
    plugins[current_id] = editor.getValue();
});
$('.clickable-row').click(function() {
   // clicking on a row loads the code
    current_id = $(this).data('id');
    editor.setValue(plugins[current_id]);
});
$('#new-plugin-form').submit(function(e) {
    e.preventDefault();
        $("#submit-message").hide(300);
        console.log("posting");
        $.post('/',{
            source: $("#inputSource").val(),
            name: $("#inputName").val(),
            length: $("#inputLength").val()
        }, function(data) {
            console.log("posted");
            if (data.hasOwnProperty('error')) {
                $('#submit-message').text(data.error).show(300);
            } else {
                window.location.reload(true);
            }
        });
});
$('.save').click(function() {
    var row = $(this).parent().parent();
    var checked = row.find('input:checkbox').first().is(':checked');
    // update the plugin
    var id = $(this).data('id');
    var code = plugins[id];
    editor.setValue(code);
    var days = [];
    row.find('input[name^="day_"]').each(function () {
        days.push($(this).is(':checked')? '1': '0');
    });
    days = days.join("");
    var data = {
        length: row.find('#duration').val(),
        enabled: checked,
        time_from: row.find('#time_from').val(),
        time_to: row.find('#time_to').val(),
        days:days,
        repeats:row.find('#repeats').val(),
        date_from: row.find('.date_from').val(),
        code: code,
        position: row.index(),
    };
    console.log(data);
    $.post('/plugin/'+id, data,function(data) {
        console.log(data);
    });
});
$()
$(function () {
    $('.time_').datetimepicker({format:'HHmm'});
    $('.date_from').datetimepicker({format:'D/MM/YYYY'});
});
    $('.clear-event').click(function() {
        $(this)
                .parent()
                .siblings()
                .find('input')
                .slice(1)
                .not(':button, :submit, :reset, :hidden')
                .val('')
                .removeAttr('checked')
                .removeAttr('selected');
    });

$('i.row-up, i.row-down').click(function() {
    // move the table row up
    // should call a position setting api
    var row = $(this).parent().parent();
    var rows = row.parent().children();
    var idx = row.index();

    if ($(this).hasClass('row-up') && idx > 0) {
        rows.eq(idx-1).before(row);
    } else {
        rows.eq(idx+1).after(row);
    }
    var row_map = {};
    rows.each(function() {
        row_map[$(this).data('id')] = $(this).index();
    });
    console.log(row_map);
    $.post("/plugin/positions/update", row_map, function(data) {
        console.log(data);
    });
});
</script>

<%include file="footer.html"/>
