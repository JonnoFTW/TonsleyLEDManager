# lecture notice
from plugins.fonts import Font
import numpy as np

class Runner:
    def __init__(self, dims):
        self.dims = dims

        fnt = Font('open_sans.ttf', 16)
        # import numpy as np
        self.np = np
        message = self.get_text()
        render = fnt.render_text(message)
        message = str(render).splitlines()
        self.pixels = np.zeros((dims[1], max(dims[0], render.width), 3), dtype=np.uint8)
        white = [255, 255, 255]
        for y in range(render.height):
            for x in range(render.width):
                if message[y][x] == '#':
                    self.pixels[y, x] = white
        self.pixels = np.flipud(np.rot90(self.pixels, 1))

    def run(self):
        self.pixels = self.np.roll(self.pixels, -1, 0)
        out = self.pixels[0: self.dims[0]]
        return out

    def get_text(self):
        import requests
        import os
        from datetime import datetime
        from bs4 import BeautifulSoup

        with requests.session() as s:
            login_url = "https://timetable.flinders.edu.au/Staff2016/Login.aspx"
            default_url = "https://timetable.flinders.edu.au/Staff2016/default.aspx"
            user = os.getenv("WEBUSER", "")
            password = os.getenv("WEBPASS", "")
            if user == "" or password == "":
                return "Welcome to Tonsley!"
            data = {
                'tUserName': user,
                'tPassword': password,
                'bLogin': 'Login'
            }

            login_page = s.get(login_url).text
            login_soup = BeautifulSoup(login_page, 'html.parser')
            for hidden_input in login_soup.find_all('input', {'type': 'hidden'}):
                data[hidden_input['name']] = hidden_input['value']
            #login
            p = s.post(login_url, data=data)
            welcome_soup = BeautifulSoup(p.text, 'html.parser')

            #click the locations button
            data.clear()
            for hidden_input in welcome_soup.find_all('input', {'type': 'hidden'}):
                data[hidden_input['name']] = hidden_input['value']
            data['__EVENTTARGET'] = 'LinkBtn_locations'
            data['__EVENTARGUMENT'] = ''
            tt_page = s.post(default_url, data=data).text
            data.clear()
            # get all the form data in
            tt_soup = BeautifulSoup(tt_page, 'html.parser')
            for field in tt_soup.find_all('input'):
                try:
                    data[field['name']] = field['value']
                except KeyError:
                    pass
            data['__EVENTTARGET'] = 'dlPeriod'
            data['__EVENTARGUMENT'] = ''
            full_day_soup = s.post(default_url, data=data).text
            # got the page with full day selected
            data.clear()

            # put the list query in
            tt_data = {
                'tLinkType': 'locations',
                'dlFilter2': '%',
                'dlFilter': '%',
                'tWildcard': '',
                'dlObject': 'TON_T1_G.42',
                'lbWeeks': 't',
                'lbDays': '1-7;1;2;3;4;5;6;7',
                'dlPeriod': '1-34;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29;30;31;32;33;34;',
                'RadioType': 'flinders_location_list;cyon_reports_list_url;dummy',
                'bGetTimetable': 'View Timetable',
            }
            for hidden_input in BeautifulSoup(full_day_soup, 'html.parser').find_all('input', {'type': 'hidden'}):
                tt_data[hidden_input['name']] = hidden_input['value']
            now = datetime.now()
            tt_text = s.post(default_url, data=tt_data).text
            soup = BeautifulSoup(tt_text, 'html.parser')
            rows = soup.find('tbody').find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                day = int(cells[2].p.text)
                title = cells[1].text
                if day != now.weekday():
                    continue
                time_start = int(cells[3].p.text.split(':')[0])
                time_end = int(cells[4].p.text.split(':')[0])
                if time_start <= now.hour < time_end:
                    return " {} - {}:00 to {}:00 ".format(title, time_start, time_end)

        return "Hello!"


if __name__ == "__main__":
    import pygame, sys
    FPS = 10
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