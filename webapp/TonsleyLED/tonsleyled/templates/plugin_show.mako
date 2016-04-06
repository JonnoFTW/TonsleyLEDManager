<%include file="header.html"/>
<div class="container" style="padding-top:50px">
    <div class="row" style="padding-top:20px">
        <div class="col-lg-12" id="code-preview">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> ${plugins[0].name} by <a href="/users/${plugins[0].user.id}">${plugins[0].user.email}</a>
                </div>
                <div class="panel-body">
                    <textarea id="code" class="form-control">${plugins[0].code}</textarea>
                </div>
            </div>
        </div>
    </div>
</div>
<%include file="codemirror.mako"/>
<%include file="footer.html"/>
