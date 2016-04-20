"""
@Author: Jonathan Mackenzie
@Description: Python Program to Control LED sign based off schedule
"""

from collections import deque
import time

from datetime import datetime, timedelta

import opc
import pymysql
import sys
import os
import imp
import numpy as np
from pluck import pluck

FPS = 60
delay = 0.004

rows = 17
cols = 165
board_dimensions = (cols, rows)
output_shape = (cols, rows, 3)
# disp_size = (cols * 8, rows * 8)

disp_size = (1920*6, 1080)
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
try:
    pg = True
    if pg:
        import pygame

        pygame.init()
        size = width, height = board_dimensions
        screen = pygame.display.set_mode(disp_size)
except ImportError:
    pg = False

IP_PORT = "177.22.11.2:7890"
# IP_PORT = "localhost:7891"
if len(sys.argv) > 1:
    IP_PORT = sys.argv[1]


global current_plugin_end, schedule, last_schedule_update, current_plugin
current_plugin = None
last_schedule_update = 0
current_plugin_end = 0
fpsClock = pygame.time.Clock()
schedule = deque()
error_pixels = np.random.normal(128, 128, (board_dimensions[0], board_dimensions[1], 3)).astype(np.uint8)


def get_file(name):
    with open(name, 'r') as f:
        return f.read()


def test_sched():
    code_roll = get_file('plugins/runner.py')
    code_ball = get_file('plugins/balls.py')
    code_maze = get_file('plugins/maze.py')
    code_message = get_file('plugins/message.py')
    code_gol = get_file('plugins/game_of_life.py')
    return deque([
        {
            'id': 1,
            'name': 'Game of Life',
            'duration': 20,
            'code': code_gol
        },
        {
            'id': 2,
            'name': 'Message',
            'duration': 15,
            'message': 'Default Message!',
            'code': code_message
        },
        {
            'id': 3,
            'name': 'Maze Runner',
            'duration': 9,
            'code': code_maze
        },
        {
            'id': 4,
            'name': 'Rolling Gradients',
            'duration': 15,
            'code': code_roll
        },
        {
            'id': 5,
            'name': 'Particle Simulation',
            'duration': 15,
            'code': code_ball
        }
    ])


def get_current_schedule(conn):
    """
    Only returns the group id of the first schedule that should be running,
    if all else fails, play the default
    """
    cursor = conn.cursor()
    sql = """SELECT * FROM led_group WHERE `enabled` = 1"""
    cursor.execute(sql)
    # schedule will be at row 0
    rows = cursor.fetchall()
    default = None
    chosen = None
    for row in rows:
        if row['default']:
            default = row
        else:
            ## check if this schedule needs to run right now
            nowdt = datetime.now()
            midnight = nowdt.replace(hour=0, minute=0, second=0, microsecond=0)
            if row['date_from'] is not None:
                if nowdt.date() < row['date_from']:
                    # print row['name'], "Date from not reached yet"
                    continue
                if row['repeats'] is not None:
                    row_monday = nowdt - timedelta(days=nowdt.weekday())
                    if (row_monday - row['date_from']).days / 7 > row['repeats']:
                        # print row['name'], "Repeated enough times"
                        continue
            if row['time_from'] is not None:
                if nowdt.time() < (midnight + row['time_from']).time():
                    # print row['name'], "Not after time from"
                    continue
            if row['time_to'] is not None:
                if nowdt.time() > (midnight + row['time_to']).time():
                    # print row['name'], "Not before time to"
                    continue
            if row['days_of_week'] is not None:
                if row['days_of_week'][nowdt.weekday()] == "0":
                    # print row['name'], "Not right day of week"
                    continue
            chosen = row
    if chosen is not None:
        return chosen
    return default


def refresh_schedule():
    """
    Get the latest scheduling from the database
    The next plugin to run is at the right
    :return:class Runner:

    def __init__(self, board_dimensions):
        self.board_dimensions = board_dimensions
        import numpy as np
        self.np = np
        self.pixels = self.np.random.normal(128, 128, (self.board_dimensions[0], self.board_dimensions[1], 3)).astype(self.np.uint8)

    def run(self):
        # shift everything to the left, put a new random column on the end

        self.pixels = self.np.roll(self.pixels, 1, 0)
        col = self.np.random.normal(128, 128, [17, 3]).astype(dtype=self.np.uint8)
        for idx, i in enumerate(col):
            self.pixels[0][idx] = i
        self.pixels.sort(1)
        return self.pixels
    """
    global current_plugin
    print "Updating schedule"
    db_user = os.environ.get('DBUSER', '<username>')
    db_pass = os.environ.get('DBPASS', '<password>')
    db_host = os.environ.get('DBHOST', '<host>')
    db_name = os.environ.get('DBNAME', '<dbName>')
    try:
        connection = pymysql.connect(host=db_host,
                                     user=db_user,
                                     passwd=db_pass,
                                     db=db_name,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
    except pymysql.err.OperationalError as e:
        print e
        print "Using default schedule"
        return test_sched()
    cursor = connection.cursor()
    # need to fix this so that it loads the right schedule
    #
    group_id = get_current_schedule(connection)
    if group_id is None:
        return test_sched()
    sql = """SELECT * FROM `led_schedule`
             LEFT OUTER JOIN led_plugin
             ON led_schedule.led_plugin_id = led_plugin.id
             WHERE
              `enabled` = 1 AND
              `led_group_id` = {}
             ORDER BY `position` DESC """.format(group_id['id'])
    cursor.execute(sql)
    schedule.clear()

    for row in cursor:
        schedule.append(row)
    cursor.close()
    connection.close()
    # if there schedule has > 2 elems,
    # roll the schedule until we get old_schedule[0] at the start

    if current_plugin and len(schedule) > 2 and current_plugin['id'] in pluck(schedule, 'id'):
        while schedule[-1]['id'] != current_plugin['id']:
            schedule.rotate(-1)
    else:
        schedule.rotate(-1)
    # show_schedule(schedule)
    return schedule


def show_schedule(sc):
    for i in sc:
        print i['name'], i['position']
    print


def load_next_plugin():
    """
    Attempts to load the next plugin, returns None if there are 
    no valid plugins available
    :return: a plugin that can be run()
    """
    global current_plugin
    while True:
        try:

            schedule.rotate(1)
            next = schedule[-1]
            current_plugin = next
            # show_schedule(schedule)
            print next['name']
        except IndexError as e:
            print "No valid plugins could be loaded"
            return None, 0
        # print "Loading plugin:", next['name']
        plugin = imp.new_module("plugin")
        exec next['code'] in plugin.__dict__
        if not hasattr(plugin, 'Runner'):
            print next, "is not a valid plugin"
            continue
        end = now + next['duration']
        try:

            if next.get('message', None) is not None:
                # print "doing messsage"
                return plugin.Runner(board_dimensions, next['message']), end
            return plugin.Runner(board_dimensions), end
        except Exception as e:
            print "Could not load plugin:", e


client = opc.Client(IP_PORT)

if client.can_connect():
    print ' Connected to %s' % IP_PORT
elif not pg:
    # can't connect, but keep running in case the server appears later
    print ' ERROR: could not connect to %s' % IP_PORT

plugin = None
old_pixels = None
while True:
    now = time.time()
    if now - last_schedule_update > 10:
        schedule = refresh_schedule()
        if not schedule:
            schedule = test_sched()
        last_schedule_update = now
    if now >= current_plugin_end:
        # try:
            if plugin is not None:
                # try to finish() the old plugin
                try:
                    plugin.finish()
                except AttributeError as e:
                    pass
            plugin, current_plugin_end = load_next_plugin()
        # except Exception as e:
        #     print "[x] Failed to load plugin:", e
        #     continue
    if plugin is not None:
        try:
            pixels = plugin.run()
            if not isinstance(pixels, np.ndarray) or pixels.shape != output_shape:
                raise Exception("Pixels must be a numpy array with shape " + str(output_shape)+" received "+str(pixels.shape))
        except Exception as e:
            print "Error running plugin {}: {}".format(schedule[0]['name'], e.message)
            plugin, current_plugin_end = load_next_plugin()
            continue
        # make sure the output is only an array-like that uses
        # board_dimensions
    else:
        print "Entering error state"
        pixels = error_pixels
    row_idx = 1
    for row in reversed(np.rot90(pixels)):
        client.put_pixels(row, row_idx)
        time.sleep(delay)
        client.put_pixels(row, row_idx)
        time.sleep(delay)
        row_idx += 1
    if pg:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
        screen.fill((0, 0, 0))
        # draw the pixels
        temp_surface = pygame.Surface(board_dimensions)
        pygame.surfarray.blit_array(temp_surface, pixels)
        pygame.transform.scale(temp_surface, disp_size, screen)
        pygame.display.flip()

    else:
        print "Not connected"
        break
    fpsClock.tick(FPS)

print "Finished"
