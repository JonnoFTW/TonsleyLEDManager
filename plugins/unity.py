import json


class Runner:
    def __init__(self, dims):
        self.dims = dims
        import numpy as np
        self.np = np

        from flask import Flask, render_template, request
        from flask_sockets import Sockets
        import json
        from random import randint
        from itertools import cycle
        from matplotlib import cm
        num_cols = 512
        # Pick a colour map from here: https://matplotlib.org/users/colormaps.html
        rainbow = cm.get_cmap('PuBu', num_cols)
        self.sky_colours = [[int(c * 256) for c in rainbow(i)[:-1]] for i in range(num_cols)]
        self.sky_colours = cycle(self.sky_colours + self.sky_colours[::-1])
        app = Flask('UnityGame')
        sockets = Sockets(app)
        self.things = [{
            'type': 'cloud',
            'xpos': 90,
            'ypos': 1,
            'velocity': 0.2,
        }]
        self.things_templates = {'cloud':
                                     {'colours':
                                          [[0xd8, 0xad, 0xde], [253, 245, 251]],
                                      'template':
                                          np.array([
                                              # gratuitously stolen from: https://cdn.dribbble.com/users/1113/screenshots/150244/pixelcloud-dribbble.png
                                              [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 1, 1, 2, 2, 1, 1, 0, 0, 0, 0],
                                              [0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 0, 0, 0],
                                              [0, 0, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 1, 0, 0, 0],
                                              [0, 1, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 1, 0, 0],
                                              [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 0],
                                              [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
                                              [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
                                              [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1],
                                              [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                                          ])
                                      },
                                 'boat': {'template': [
                                     [0, 0, 0, 1, 0, 0, 0],
                                     [0, 0, 1, 1, 1, 0, 0],
                                     [0, 1, 1, 1, 1, 1, 0],
                                     [0, 0, 0, 1, 0, 0, 0],
                                     [1, 1, 0, 1, 0, 1, 1],
                                     [0, 1, 1, 1, 1, 1, 0],
                                     [0, 0, 1, 1, 1, 0, 0]
                                 ]}
                                 }
        self.current_players = {}
        game_x_min = 0
        game_x_max = 100
        self.game_y_max = 100
        boat_velocity = 0.5
        initial_hook_velocity = 0.1
        app_port = 5000

        ug_socket = {
            'ws': None
        }

        def make_player(ws):
            player = {
                'type': 'boat',
                'colour': [[randint(0, 255) for _ in range(3)]],
                'hook_position': 0,
                'hook_velocity': 0,
                'xpos': randint(game_x_min, game_x_max),
                'ypos': 8,
                'velocity': 0,
                'score': 0,
                'id': ws.hander.client_address
            }
            self.current_players[ws] = player
            # inform the unity game about this?

        @sockets.route('/unity')
        def unity_client_socket(ws):
            # should check that unity is running locally only
            if ug_socket['ws'] is not None or ws.handler.client_address[0] != '127.0.0.1':
                return
            ug_socket['ws'] = ws

            while not ws.closed:
                # do stuff here i guess...
                message = ws.receive().lower()
                if message == 'player_state':
                    ws.send(json.dumps(self.current_players.items()))
            ug_socket['ws'] = None

        @sockets.route('/client')
        def device_client_socket(ws):
            make_player(ws)
            ws.send(json.dumps(self.current_players[ws]))
            while not ws.closed:
                message = ws.receive()
                if message is None:
                    break
                message = message.lower()
                player_state = self.current_players[ws]
                print("msg> " + message)
                event_handlers = {
                    'left': None
                }
                if message == 'left':
                    if player_state['hook_velocity'] == 0:
                        player_state['velocity'] = -boat_velocity
                elif message == 'right':
                    if player_state['hook_velocity'] == 0:
                        player_state['velocity'] = boat_velocity
                elif message == 'stop':
                    player_state['velocity'] = 0
                elif message == 'hook':
                    # handle hook drop gameplay
                    # player_state['score'] += 1
                    player_state['velocity'] = 0
                    player_state['hook_velocity'] = initial_hook_velocity
                    # ug_socket['ws'].send('hook dropped')
                self.send_client_state(ws)
            del self.current_players[ws]

        import uuid
        qr_codes = set([uuid.uuid4().hex])

        @app.route('/')
        def home():
            # check they sent a a valid qr code
            # artworkpc.isd.ad.flinders.edu.au:5000/?qr=a6rt5grtg566bt
            qr = request.args.get('qr')
            # if qr not in qr_codes:
            #     return "YOU CANT PLAY WITHOUT A QR CODE"
            with open('fishgame.html') as f:
                fish_html = f.read()
            return fish_html

        def flaskThread():
            from gevent import pywsgi
            from geventwebsocket.handler import WebSocketHandler

            server = pywsgi.WSGIServer(('0.0.0.0', app_port), app, handler_class=WebSocketHandler)
            print("Starting server on: http://{}:{}".format(*server.address))
            server.serve_forever()

        import thread
        thread.start_new_thread(flaskThread, ())

    def send_client_state(self, ws):
        ws.send(json.dumps(self.current_players[ws]))

    def update_things(self):
        for thing in self.things + self.current_players.values():
            thing['xpos'] = (thing['xpos'] + thing['velocity']) % self.dims[0]
            if thing['xpos'] >= self.dims[0]:
                thing['xpos'] = 0 - len(self.things_templates[thing['type']]['template'][0])
        for ws, player in self.current_players.items():
            player['hook_position'] += player['hook_velocity']

            if player['hook_position'] <= 0:
                player['hook_position'] = 0
                player['hook_velocity'] = 0

            if player['hook_position'] >= self.game_y_max:
                player['hook_position'] = 0
            self.send_client_state(ws)

    def run(self):
        np = self.np
        water = [14, 69, 156]
        # sky = [206, 237, 255]
        sky = next(self.sky_colours)
        pixels = np.full((self.dims[0], self.dims[1], 3), water, dtype=np.uint8)
        pixels[:, 0:13] = sky
        self.update_things()
        for thing in self.things + self.current_players.values():
            template = self.things_templates[thing['type']]
            if thing['type'] == 'boat':
                colour = thing['colour']
            else:
                colour = template['colours']
            grid = template['template']
            xpos = thing['xpos']
            ypos = thing['ypos']
            for y, row in enumerate(grid):
                y = np.int(np.floor(ypos + y))
                for x, pix in enumerate(row):
                    if pix != 0:
                        col = colour[pix - 1]
                        x = np.int((xpos + x) % self.dims[0])
                        pixels[x, y] = col
        return pixels


if __name__ == "__main__":
    from demo import show

    show(Runner, fps=30, rows=17, cols=165, scale=8)
