# Introduction

This project has 2 parts:

1. An command line application to send data to the LED sign at Tonsley. It works by fetching plugins from a database
   and running their code. It also allows for scheduling rules to determin
2. A web based application for managing the scheduling of items

The command line application uses `plugins` to manage what is shown. Each plugin has:

 * Name
 * Duration in seconds
 * Python source code
 * An associated user
 * Position to indicate the order in which plugins run

The following fields may be null, if they aren't, then they are used:

 * A date from that indicates after what date the plugin will play
 * Repeats indicates how many weeks after the starting week the plugin will play
 * Days of the week indicating what days the plugin runs
 * Start time and end time to indicate what time of day the plugin will play

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

In order to run the sender program:

1. NM
