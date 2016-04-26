<script>

    var plugins = {
        % for plugin in plugins:
            ${plugin.id}:
            [
                %for line in plugin.code.splitlines():
                    "${line.replace('"', '\\"') |n}",
                %endfor
            ].join("\n"),
        % endfor
    }
    ;
    var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
        mode: {name: 'python'},
        lineNumbers: true,
    });
    editor.setSize({width: "100%", height: "800px"});

    var current_id = -1;
    var keys = Object.keys(plugins);
    if (keys.length == 1) {
        current_id = keys[0];
    }
    editor.on("change", function () {
        plugins[current_id] = editor.getValue();
    });
    $('.clickable-row').click(function () {
        // clicking on a row loads the code
        current_id = $(this).data('id');
        editor.setValue(plugins[current_id]);
    });
        ## append a button to save at the bottom
        ## if they have the access to edit the code
##     % if request.can_user_edit_plugin():
##     % endif
    var saveCode = function() {
        $('#update-msg').fadeOut().removeClass('alert-danger alert-success');
      // save the code currently being shown
        $.post('/plugin/'+current_id, {
           code: plugins[current_id]
        }, function(data, text, xhr) {
            $('#update-msg').fadeIn(500).addClass('alert-success').text(data.msg);
        }).fail(function(data, text, xhr) {
           // console.log(data,text,xhr);
            $('#update-msg').fadeIn(500).addClass('alert-danger').text('Error: '+data.statusText);
        }).always(function() {
            $('#update-msg').delay(2000).fadeOut(500)
        });
    };
    $('#code-preview').find('.panel-heading').prepend(
            "<div class='pull-right'><span class='alert small' style='display: none' id='update-msg' role='alert'></span> " +
            "<button onclick='saveCode()' class='btn btn-primary btn-sm'>Save</button></div>"
    );
    ;
    $('#update-msg').hide();
</script>