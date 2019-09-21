import pygame
import ms_database
import minesweeper


class Main:

    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((850, 650))
        pygame.display.set_caption('Mine Sweeper')
        icon = pygame.image.load('mine.png')
        pygame.display.set_icon(icon)
        self.running = True
        self.signed_in = False

        d = ms_database.Database()
        self.user = ''
        self.get_name()

        self.start = Start(self.display, d)
        self.g15 = Loader(self.display, d, self.user, (15, 15), 30, 20)
        self.g20 = Loader(self.display, d, self.user, (20, 20), 25, 40)
        self.g30 = Loader(self.display, d, self.user, (30, 30), 18, 80)
        self.scores = Scores(self.display, d)
        self.screen_dict = {'start': self.start, '15': self.g15, '20': self.g20, '30': self.g30, 'scores': self.scores}

        self.current_screen = self.start

    def run(self):
        while self.running:
            returned = self.current_screen.run()
            if returned == 'quit':
                self.running = False
            elif returned:
                try:
                    self.current_screen = self.screen_dict[returned]
                except KeyError:
                    self.current_screen = self.screen_dict[returned[0]]
                    self.current_screen.pass_information(returned[1])

    def get_name(self):
        button = Button((425, 500), (100, 50), 'Enter', (0, 0, 0), 20, (200, 200, 200), (150, 150, 150), self.begin)
        input_box = TextInput((425, 400), (300, 50), (0, 0, 0), 20, (200, 200, 200), (150, 150, 150), 'user')
        message = TextBox((425, 320), (600, 50), 'Enter a nickname (3 characters min):', (0, 0, 0), 25,
                          (150, 150, 150))

        title = pygame.image.load('ms_title.png').convert_alpha()
        title = pygame.transform.scale(title, (600, 80))
        title_pos = (125, 50)

        while not self.signed_in:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return 'quit'

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    returned = button.clicked(pos)
                    if returned:
                        return returned

                    input_box.click_check(pos)

                elif event.type == pygame.KEYDOWN:
                    returned = input_box.update(event)
                    self.process(returned)

            self.display.fill((255, 255, 255))

            button.draw(self.display)
            input_box.draw(self.display)
            message.draw(self.display)

            self.display.blit(title, title_pos)

            pygame.display.flip()

    def process(self, returned):
        if not returned:
            return
        if returned[0] == 'user':
            self.user = returned[1]

    def begin(self):
        if len(self.user) >= 3:
            self.signed_in = True


class Screen:

    def __init__(self, screen, database, colour=(255, 255, 255)):
        self.screen = screen
        self.database = database
        self.running = True

        self.images = []
        self.buttons = []
        self.text_boxes = {}
        self.inputs = []

        self.colour = colour

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return 'quit'

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    for b in self.buttons:
                        returned = b.clicked(pos)
                        if returned:
                            return returned

                    for t in self.inputs:
                        t.click_check(pos)

                elif event.type == pygame.KEYDOWN:
                    for t in self.inputs:
                        returned = t.update(event)
                        self.process(returned)

                for t in self.inputs:
                    returned = t.update(event)
                    self.process(returned)

            self.screen.fill(self.colour)

            for b in self.buttons:
                b.draw(self.screen)
            for i in self.images:
                self.screen.blit(i[0], i[1])
            for i in self.inputs:
                i.draw(self.screen)
            for v in self.text_boxes.values():
                v.draw(self.screen)

            pygame.display.flip()

    def process(self, returned):
        pass


class Start(Screen):

    def __init__(self, screen, database):
        Screen.__init__(self, screen, database)

        b15 = Button((225, 300), (150, 100), '15x15', (0, 0, 0), 30, (150, 150, 150), (50, 50, 50), self.b15)
        b20 = Button((425, 300), (150, 100), '20x20', (0, 0, 0), 30, (150, 150, 150), (50, 50, 50), self.b20)
        b30 = Button((625, 300), (150, 100), '30x30', (0, 0, 0), 30, (150, 150, 150), (50, 50, 50), self.b30)
        quit_button = Button((425, 500), (100, 50), 'Quit', (0, 0, 0), 20, (200, 200, 200), (150, 150, 150), self.quit)

        self.buttons = [b15, b20, b30, quit_button]

    def b15(self):
        return '15'

    def b20(self):
        return '20'

    def b30(self):
        return '30'

    def quit(self):
        return 'quit'


class Scores(Screen):

    def __init__(self, screen, database):
        Screen.__init__(self, screen, database)

        self.scoreboard = None
        self.information = None

        back_button = Button((425, 600), (100, 50), 'Continue', (0, 0, 0), 20,
                             (200, 200, 200), (150, 150, 150), self.back)

        self.buttons = [back_button]

    def run(self):
        if self.information:
            self.scoreboard = ScoreBoard((400, 300), (600, 400), ['No.', 'Name', 'Time', 'Date'],
                                         self.database, 1, self.information)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return 'quit'

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    for b in self.buttons:
                        returned = b.clicked(pos)
                        if returned:
                            return returned

            self.screen.fill(self.colour)

            for b in self.buttons:
                b.draw(self.screen)
            for v in self.text_boxes.values():
                v.draw(self.screen)

            self.scoreboard.update(self.screen)

            pygame.display.flip()

    def pass_information(self, returned):
        self.information = returned

    def up(self):
        if self.scoreboard:
            self.scoreboard.move_up()

    def down(self):
        if self.scoreboard:
            self.scoreboard.move_down()

    def back(self):
        return 'start'


class Loader:

    def __init__(self, screen, database, user, dimensions, size, mines):
        self.screen = screen
        self.database = database
        self.user = user
        self.dimensions = dimensions
        self.size = size
        self.mines = mines

    def run(self):
        game = minesweeper.Game(self.screen, self.database, self.user, self.dimensions, self.size, self.mines)
        returned = game.run()
        return returned


class Button:

    def __init__(self, position, dimensions, text, t_colour, font_size, active, inactive, func):
        self.position = position
        self.dimensions = dimensions
        self.text = text
        self.t_colour = t_colour
        self.font_size = font_size
        self.active = active
        self.inactive = inactive

        self.colour = self.inactive

        self.font = pygame.font.SysFont('Comic Sans MS', self.font_size)
        self.text_image = self.font.render(self.text, 1, self.t_colour)
        self.text_rect = self.text_image.get_rect(center=[d // 2 for d in self.dimensions])

        self.image = pygame.Surface(self.dimensions)
        self.rect = self.image.get_rect(center=self.position)

        self.func = func

    def draw(self, screen):
        self.update()

        self.image.fill(self.colour)
        self.image.blit(self.text_image, self.text_rect)
        screen.blit(self.image, self.rect)

    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.colour = self.active
        else:
            self.colour = self.inactive

    def clicked(self, pos):
        if self.rect.collidepoint(pos):
            return self.func()


class TextInput:

    def __init__(self, position, dimensions, t_colour, font_size, active, inactive, process):
        self.position = position
        self.dimensions = dimensions
        self.text = ''
        self.display_text = ''
        self.t_colour = t_colour
        self.font_size = font_size
        self.active = active
        self.inactive = inactive

        self.colour = self.inactive
        self.clicked = False

        self.font = pygame.font.SysFont('Comic Sans MS', self.font_size)
        self.text_image = self.font.render(self.display_text, 1, self.t_colour)
        self.text_rect = self.text_image.get_rect(center=[d // 2 for d in self.dimensions])

        self.image = pygame.Surface(self.dimensions)
        self.rect = self.image.get_rect(center=self.position)

        self.process = process

    def update(self, event):
        if self.clicked:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.display_text = self.display_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.clicked = False
                self.colour = self.inactive
                return
            else:
                character = chr(event.key)
                if event.key in [304, 306, 311, 301, 308, 307, 305, 280, 276, 274, 273, 275, 281, 303, 27, 282, 283,
                                 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 278, 279, 277, 127]:
                    pass
                else:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        character = character.upper()
                    self.display_text += character
                    self.text += character

            self.text_image = self.font.render(self.display_text, 1, self.t_colour)
            self.text_rect = self.text_image.get_rect(center=[d // 2 for d in self.dimensions])

            self.image = pygame.Surface(self.dimensions)
            self.rect = self.image.get_rect(center=self.position)

            return [self.process, self.text]

    def draw(self, screen):
        self.image.fill(self.colour)
        self.image.blit(self.text_image, self.text_rect)
        screen.blit(self.image, self.rect)

    def click_check(self, pos):
        if self.rect.collidepoint(pos):
            self.colour = self.active
            self.clicked = True
        else:
            self.colour = self.inactive
            self.clicked = False

    def clear(self):
        self.text = ''
        self.display_text = ''

        self.text_image = self.font.render(self.display_text, 1, self.t_colour)
        self.text_rect = self.text_image.get_rect(center=[d // 2 for d in self.dimensions])

        self.image = pygame.Surface(self.dimensions)
        self.rect = self.image.get_rect(center=self.position)


class TextBox:

    def __init__(self, position, dimensions, text, t_colour, font_size, colour):
        self.position = position
        self.dimensions = dimensions
        self.text = text
        self.t_colour = t_colour
        self.font_size = font_size
        self.colour = colour

        self.font = pygame.font.SysFont('Comic Sans MS', self.font_size)
        self.text_image = self.font.render(self.text, 1, self.t_colour)
        self.text_rect = self.text_image.get_rect()

        self.image = pygame.Surface(self.dimensions)
        self.image.set_colorkey((250, 250, 250))
        self.rect = self.image.get_rect(center=self.position)

    def draw(self, screen):
        self.image.fill(self.colour)
        self.image.blit(self.text_image, self.text_rect)
        screen.blit(self.image, self.rect)

    def update(self, new_text):
        self.text = new_text
        self.text_image = self.font.render(self.text, 1, self.t_colour)


class ScoreBoard:

    def __init__(self, position, dimensions, fields, database, index, table):
        self.position = position
        self.dimensions = dimensions
        self.fields = fields
        self.db = database
        self.index = index
        self.table = table

        self.image = pygame.Surface(dimensions)
        self.rect = self.image.get_rect(center=position)

        self.headers = self.make_headers()
        self.columns, self.score_list = self.make_columns()

        self.multiplier = 0
        self.limit = (len(self.score_list) // 10)
        self.assign_to_box()

    def make_headers(self):
        headers = []
        width_space = self.dimensions[0] / len(self.fields)
        for i in range(1, len(self.fields) + 1):
            headers.append(TextBox(((width_space * i) - (width_space // 2), 10), (width_space - 1, 25),
                                   self.fields[i - 1], (255, 255, 255), 20, (250, 250, 250)))

        return headers

    def make_columns(self):
        scores = self.db.return_scores(self.table)
        score_list = sorted(scores, key=lambda x: x[self.index])

        width_space = self.dimensions[0] / len(self.fields)
        height_space = self.dimensions[1] / 11
        columns = []
        for i in range(1, len(self.fields) + 1):
            t_boxes = []
            for n in range(2, 12):
                t_boxes.append(TextBox(((width_space * i) - (width_space // 2), (height_space * n) - (height_space//2)),
                                       (width_space - 1, 25), '', (255, 255, 255), 15, (250, 250, 250)))
            columns.append(t_boxes)

        return columns, score_list

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, screen):
        self.image.fill((0, 0, 0))
        for h in self.headers:
            h.draw(self.image)
        for c in self.columns:
            for t in c:
                t.draw(self.image)
        self.draw(screen)

    def move_down(self):
        if self.multiplier < self.limit:
            self.multiplier += 1
            self.assign_to_box()

    def move_up(self):
        if self.multiplier > 0:
            self.multiplier -= 1
            self.assign_to_box()

    def assign_to_box(self):
        for i in range(len(self.fields)):
            column = self.columns[i]
            for j in range(10):
                column[j].update('')
                try:
                    if i == 0 and ((j + 1) + (10 * self.multiplier)) <= len(self.score_list):
                        column[j].update(str((j + 1) + (10 * self.multiplier)))
                    else:
                        column[j].update(str(self.score_list[j + (10 * self.multiplier)][i - 1]))
                except IndexError:
                    pass


if __name__ == '__main__':
    m = Main()
    m.run()
    pygame.quit()
