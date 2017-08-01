class Runner:


    def __init__(self, dims):
        self.dims = dims
        from plugins.fonts import Font
        self.fnt = Font('slkscr.ttf', 16)
        import numpy as np
        import subprocess
        self.np = np
        message = "Unity Plugin"
        self.render_message(message)


        from flask import Flask, request
        app = Flask('KinectStream')

        @app.route('/', methods=['GET'])
        def index():
            val = request.args.get('val', "Nothing!")
            self.render_message(val)
            return val

        app_port = 5000
        def flaskThread():
            app.run(host='0.0.0.0', port=app_port)
        import thread
        thread.start_new_thread(flaskThread, ())
        subprocess.Popen(['python', '-c',
                          "exec(\"import requests\\nimport time\\nfor i in range(60):\\n requests.get('http://localhost:"+str(app_port)+"',params={'val':i})\\n time.sleep(0.5)\")"])



    def render_message(self, message):
        render = self.fnt.render_text(message)
        message = str(render).splitlines()
        np = self.np
        self.pixels = np.zeros((self.dims[1], max(self.dims[0], render.width), 3), dtype=np.uint8)
        white = [199, 255, 199]

        for y in range(render.height):
            for x in range(render.width):
                try:
                    if message[y][x] == '#':
                        self.pixels[y + 3, x + 26] = white
                except:
                    pass
        self.pixels = np.flipud(np.rot90(self.pixels, 1))


    def run(self):
        return self.pixels


if __name__ == "__main__":
    from demo import show

    show(Runner, fps=30, rows=17, cols=165, scale=8)
