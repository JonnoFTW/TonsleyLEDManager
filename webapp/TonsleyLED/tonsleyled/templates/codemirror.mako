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
    editor.setSize({height:"800px"});
    var current_id = -1;
    editor.on("change", function () {
        plugins[current_id] = editor.getValue();
    });
    $('.clickable-row').click(function () {
        // clicking on a row loads the code
        current_id = $(this).data('id');
        editor.setValue(plugins[current_id]);
    });
</script>