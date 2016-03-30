<%include file="header.html"/>

<div class="container" style="padding-top:50px">
    <div class="row" style="padding-top:20px">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-info fa-fw"></i> Help
                </div>
                <div class="panel-body">
                    <h2>Introduction</h2>
                    <p>This site manages the schedule for the LED sign on the bottom floor
                        of the Flinders Tonsley building</p>
                    <h1>Code</h1>
                    Programs are run in python2, being dynamically compiled and run by the imp module.
                    In order for your program to run, you need to make a class that looks like:
                    <pre class="prettyprint">
class Runner:
    def __init__(self, board_dimensions):
        import numpy as np
        self.np = np
        self.dims = board_dimensions
        # dims[0] = columns = 165
        # dims[1] = rows    = 17
    def run(self):
        return self.np.zeros((self.dims[1], self.dims[0], 3), dtype=self.np.uint8)
                    </pre>
                    The run function is called by the scheduler at 30 FPS. It needs to return a numpy array
                    of shape (165, 17, 3) with type uint8 (don't worry they're passed into the constructor.
                    The colours are RGB from 0 to 255. The reason for assigning the numpy module to the
                    runner instance variable is something weird to do with imp loading. Live with it.

                    Complete examples can be viewed on the schedule page. My advice is to encapsulate the
                    state as a member of Runner and transform that, then render it. If you want to test your class
                    out before hand, use the following code after your class definition (you'll need pygame and numpy
                    installed):
                    <pre class="prettyprint">if __name__ == "__main__":
    import pygame, sys
    FPS = 60
    fpsClock = pygame.time.Clock()
    rows = 17
    cols = 165
    board_dimensions = (cols, rows)

    disp_size = (cols * 8, rows * 8)
    pygame.init()
    size = width, height = board_dimensions
    screen = pygame.display.set_mode(disp_size)
    runner = Runner(board_dimensions)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
        screen.fill((0, 0, 0))
        # draw the pixels
        pixels = runner.run()
        temp_surface = pygame.Surface(board_dimensions)
        pygame.surfarray.blit_array(temp_surface, pixels)
        pygame.transform.scale(temp_surface, disp_size, screen)
        pygame.display.flip()
        fpsClock.tick(FPS)

                    </pre>

                    <h2>Running other programs</h2>
                    If you don't know python well and want to run other language. You can feed the output of another
                    program
                    into this one by using the subprocess module. It's up to you how you want to read in from the pipe.

                    <h2>Configuration</h2>
                    If any configuration options are empty, they are ignored, if you want to make a plugin run all the
                    time,
                    click the clear box and save it.
                    The configuration options are as follows:
                    <h4>Time From - Time To</h4>
                    Specifies the time range in which the plugin runs.
                    <h4>Enabled</h4>
                    Enables or disables the plugin from running at all.
                    <h4>Days</h4>
                    Species what days the plugin runs
                    <h4>Repeats</h4>
                    Specifies how many <b>weeks</b> the plugin will be run, starting at the week of date from
                    <h4>Date From</h4>
                    Specifies the start date
                    <h4>Position</h4>
                    Specifies the order in which the plugins are run. Moving around plugins in the schedule table will
                    automatically save the position
                    <h4>Source Code</h4>
                    Specifies the python2 source code to run. See above for guidelines. Click on the row you want to edit
                    to populate the source code box.
                </div>
            </div>
        </div>
    </div>
</div>
<script src="https://cdn.rawgit.com/google/code-prettify/master/loader/run_prettify.js"></script>
<%include file="footer.html"/>
