class Runner:
    def __init__(self, dims):
        self.dims = dims
        import numpy as np
        self.np = np

        from flask import Flask
        from flask_sockets import Sockets
        import json
        from random import randint

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
                                     [0,0, 0, 1, 0, 0,0],
                                     [0,0, 1, 1, 1, 0,0],
                                     [0,1, 1, 1, 1, 1,0],
                                     [0,0, 0, 1, 0, 0,0],
                                     [1,1, 0, 1, 0, 1,1],
                                     [0,1, 1, 1, 1, 1,0],
                                     [0,0, 1, 1, 1, 0,0]
                                 ]}
                                 }
        self.current_players = {}
        game_x_min = 0
        game_x_max = 100
        app_port = 5000

        ug_socket = {
            'ws': None
        }

        def make_player(ws):
            player = {
                'type': 'boat',
                'colour': [[randint(0, 255) for _ in range(3)]],
                'hookpos': 0,
                'xpos': randint(game_x_min, game_x_max),
                'ypos': 8
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
            ug_socket['ws'] = None

        @sockets.route('/client')
        def device_client_socket(ws):
            make_player(ws)
            while not ws.closed:
                message = ws.receive()
                if message is None:
                    break
                message = message.lower()
                player_state = self.current_players[ws]
                if message == 'left':
                    player_state['xpos'] = (player_state['xpos'] - 1) % self.dims[0]
                elif message == 'right':
                    player_state['xpos'] = (player_state['xpos']) + 1 % self.dims[0]
                ws.send(json.dumps(self.current_players[ws]))
            del self.current_players[ws]

        @app.route('/')
        def home():
            return """
        <html>
          <head>
            <title>
              Fishing Game
            </title>

          </head>
          <body>
            <h2><a href="#">Left</a></h2>
            <h2><a href="#">Right</a></h2>
            <h2><a href="#">Drop</a></h2>
            <pre id="output"></pre>
          </body>
          <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
          <script type="text/javascript">
            $(document).ready(function() {
              ws = new WebSocket('ws://'+document.domain+':{APP_PORT}/client')
              ws.onmessage = function (event) {
                console.log(event.data);
                $('#output').text(event.data);
              }
               $('h2').click(function() {
                  ws.send($(this).text());
               });
            });
          </script>
        </html>    
            """.replace('{APP_PORT}', str(app_port))

        def flaskThread():
            from gevent import pywsgi
            from geventwebsocket.handler import WebSocketHandler

            server = pywsgi.WSGIServer(('localhost', app_port), app, handler_class=WebSocketHandler)
            server.serve_forever()

        import thread
        thread.start_new_thread(flaskThread, ())

    def update_things(self):
        for thing in self.things:
            thing['xpos'] = (thing['xpos'] + thing['velocity']) % self.dims[0]
            if thing['xpos'] >= self.dims[0]:
                thing['xpos'] = 0 - len(self.things_templates[thing['type']]['template'][0])

    def run(self):
        np = self.np
        water = [14, 69, 156]
        sky = [206, 237, 255]
        pixels = np.full((self.dims[0], self.dims[1], 3), water, dtype=np.uint8)
        pixels[:, 0:13] = sky
        self.update_things()
        # draw some happy little boats
        # for p in self.current_players.values():
        #     xpos = self.dims[0] - int(p['xposition'] / 100. * self.dims[0])
        #     pixels[xpos - 2:xpos + 2, 9:14] = p['colour']
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
