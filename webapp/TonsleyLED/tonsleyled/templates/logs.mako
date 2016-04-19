<%include file="header.html"/>
<div class="container" style="padding-top:50px">
    <div class="row" style="padding-top:20px">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Activity Logs: ${request.offset} - ${request.limit + request.offset}
                    %if request.offset > 0:
                        <a href="/logs?offset=${max(0, request.offset - 100)}"><i class="fa fa-arrow-left"></i></a>
                    %endif
                    % if request.max > request.offset + request.limit:
                        <a href="/logs?offset=${min(request.max, request.offset + 100)}"><i class="fa fa-arrow-right"></i></a>
                    % endif
                </div>
                <table class="table table-striped">
                    <thead>
                    %for h in ('Datetime', 'FAN', 'Action'):
                        <th>${h}</th>
                    %endfor
                    </thead>
                    <tbody>
                        %for row in logs:
                        <tr>
                            <td>${row.datetime}</td>
                            % if row.email in users:
                                <td><a href="/users/${users[row.email]}">${row.email}</a></td>
                            % else:
                                <td>${row.email}</td>
                            % endif
                            <td>${row.action | n}</td>
                        </tr>
                        %endfor
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
<%include file="footer.html"/>
