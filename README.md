# Introduction

This project has 2 parts:

1. An command line application to send data to the LED sign at Tonsley. It works by fetching plugins from a database
   and running their code. The code that runs
2. A web based application for managing the scheduling of items

The command line application uses `plugins` to manage what is shown. Each plugin has:

 * Name
 * Duration in seconds
 * Python source code
 * An associated user
 * Position to indicate the order in which plugins run

# Organisation

The system is organised as follows:

 * Plugins are a single piece of code that a user can upload and edit.
 * A group of users have a schedule that runs at a specific time.
 * A default schedule
 exists.
 * Users can be part of many groups and each user in a group has either a basic user or administrator user level.
 * Each schedule has many plugins and specify the duration that the plugins runs. Different schedules may use the same plugin.

Each group has the following fields which may be null, if they aren't, then they are used when considering whether or not to use the schedule:

 * A date from that indicates after what date the schedule will play
 * Repeats indicates how many weeks after the starting week the schedule will play
 * Days of the week indicating what days the schedule runs
 * Start time and end time to indicate what time of day the schedule will play

# Installation

Since you're probably running on windows, you need to:

 1. Install python 2.7.x.
 2. Install git and make sure it's in your `PATH`
 3. Rename the freetype*.dll to freetype.dll appropriate for your system.
 4. Open a command prompt and navigate to the root directory of this project.
 5. Setup the environment variables:
    * DBUSER
    * DBPASSWORD
    * DBHOST
    * DBNAME
 6. If you want the current lecture plugin, you need to additionally setup credentials for a staff account:
    * WEBUSER
    * WEBPASS

# Running

In order to run the sender program, you probably want to make a script that looks like:

```
set DBUSER=some0001
set DBHOST=mysql
....

python main.py
```
The webapp should be the same but the last line will be

```
cd webapp\TonsleyLED
pserve production.ini
```

# Plugins

This system uses plugins, look in the plugins directory for example. Basically, you need to define
a class called `Runner` that looks like:
```
class Runner:
    def __init__(self, board_dimensions):
        import numpy as np
        self.np = np
        self.dims = board_dimensions
        # dims[0] = columns = 165
        # dims[1] = rows    = 17
    def run(self):
        return self.np.zeros((self.dims[1], self.dims[0], 3), dtype=self.np.uint8)
```

Take special note of the dimensions of the resultant array. If an exception is thrown during
the constructor or during the `run` call the plugin is skipped.