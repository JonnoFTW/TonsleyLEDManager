<%include file="header.html"/>
<div class="jumbotron text-center">
    <div class="container">
        <h1 class="main-title">

            Tonsley LED Controller</h1>
        <div class="col-md-12">
    Want to get involved? Email <a href="mailto:craig.dawson@flinders.edu.au">craig.dawson@flinders.edu.au</a>
        </div>
    </div>
</div>
<div class="container" style="padding-top:50px">
     <div class="col-sm-3 col-sm-offset-1 box bg-info text-center">
            <i class="fa fa-2x fa-paint-brush"></i><br>
            <h1><a href="/plugin">View/Create Plugins</a></h1>
        </div>
        <div class="col-sm-3 box bg-info text-center">
            <i class="fa fa-2x fa-question"></i><br>
            <h1><a href="/help">Help</a></h1>
        </div>
        % if request.user is not None and request.user.admin:

        <div class="col-sm-3 box bg-info text-center">
            <i class="fa fa-2x fa-users"></i><br>
            <h1><a href="/group">View Groups</a></h1>
        </div>
             % endif
    <div class="row" >

##             <div class="panel panel-default">
##                 <div class="panel-heading">
##                     <i class="fa fa-info fa-fw"></i> Help
##                 </div>
##                 <div class="panel-body">
##                     <h2>Introduction</h2>
##                     Welcome
##                 </div>
##             </div>

    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/prettify/r298/run_prettify.min.js"></script>
<%include file="footer.html"/>
