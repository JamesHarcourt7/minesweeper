import pygame
import random

LEFT = 1
RIGHT = 3


class Tile:

    def __init__(self, size, position, colour=(255, 255, 255), clicked_colour=(150, 150, 150), font_size=15):
        self.size = size
        self.position = position
        self.colour = colour
        self.clicked_colour = clicked_colour
        self.font_size = font_size
        self.image = pygame.Surface((size - 1, size - 1))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=position)

        self.clicked = False
        self.mine = False
        self.warned = False
        self.numbered = False

        self.font = pygame.font.SysFont('Comic Sans MS', self.font_size)
        self.text_image = self.font.render('', 1, (255, 0, 0))
        self.text_rect = self.text_image.get_rect(center=(size//2 - 2, size//2 - 2))

        self.adjacents = []

    def update(self, screen, left, right, found):
        if left:
            if self.rect.collidepoint(left):
                self.clicked = True
                if not self.numbered and not self.mine:
                    connected = [self]
                    visited = []
                    while len(connected) != 0:
                        current = connected.pop(0)
                        visited.append(current)
                        for a in current.get_adjacents():
                            if a not in visited:
                                if not a.mine and not a.numbered:
                                    a.clicked = True
                                    connected.append(a)
                                elif a.numbered:
                                    a.clicked = True
                elif self.mine:
                    return 'lose'
        if right:
            if self.rect.collidepoint(right):
                if not self.clicked:
                    if self.warned:
                        self.warned = False
                        if self.mine:
                            found -= 1
                    else:
                        self.warned = True
                        if self.mine:
                            found += 1

        self.draw(screen)
        return found

    def draw(self, screen):
        if self.clicked:
            self.image.fill(self.clicked_colour)
            if self.mine:
                pygame.draw.ellipse(self.image, (0, 0, 0), (0, 0, self.size, self.size))
        elif self.warned:
            self.image.fill((255, 0, 0))
        else:
            self.image.fill(self.colour)

        if self.clicked and not self.warned:
            self.image.blit(self.text_image, self.text_rect)
        screen.blit(self.image, self.rect)

    def assign_mine(self):
        self.mine = True

    def add_adjacent(self, tile):
        self.adjacents.append(tile)

    def get_adjacents(self):
        return self.adjacents

    def update_text(self, new_text):
        self.text_image = self.font.render(new_text, 1, (255, 0, 0))
        self.numbered = True


class Grid:

    def __init__(self, screen, dimensions, tile_size, position):
        self.screen = screen
        self.width, self.height = dimensions
        self.tile_size = tile_size
        self.position = position

        self.offset = (-(self.screen.get_width() - (self.width * self.tile_size)) // 2,
                       -(self.screen.get_height() - (self.height * self.tile_size)) // 2)

        self.image = pygame.Surface(((self.width * self.tile_size) + 1, (self.height * self.tile_size) + 1))
        self.rect = self.image.get_rect(center=position)

        self.tiles = self.generate_grid()

    def generate_grid(self):
        array = []

        for y in range(self.tile_size//2, (self.height * self.tile_size), self.tile_size):
            for x in range(self.tile_size//2, (self.width * self.tile_size), self.tile_size):
                array.append(Tile(self.tile_size, (x, y)))

        graph = {}
        grid_dict = {tile.position: tile for tile in array}
        grid_list = [tile.position for tile in array]
        while len(grid_list) != 0:
            graph, grid_dict, grid_list = self.find_adjacents(graph, grid_dict, grid_list)

        return graph

    def find_adjacents(self, graph, grid_dict, grid_list):
        if len(grid_dict) == 0:
            return graph, grid_dict, grid_list

        current = grid_list.pop(0)
        tile = grid_dict.pop(current)
        position = tile.position
        graph[position] = tile

        left = (position[0] - self.tile_size, position[1])
        right = (position[0] + self.tile_size, position[1])
        up = (position[0], position[1] - self.tile_size)
        down = (position[0], position[1] + self.tile_size)
        ne = (position[0] + self.tile_size, position[1] - self.tile_size)
        se = (position[0] + self.tile_size, position[1] + self.tile_size)
        sw = (position[0] - self.tile_size, position[1] + self.tile_size)
        nw = (position[0] - self.tile_size, position[1] - self.tile_size)

        directions = [left, right, up, down, ne, se, sw, nw]

        for i in range(len(directions)):
            try:
                square = grid_dict[directions[i]]
            except KeyError:
                continue
            else:
                tile.add_adjacent(square)
                square.add_adjacent(tile)

        graph, grid_dict, grid_list = self.find_adjacents(graph, grid_dict, grid_list)

        return graph, grid_dict, grid_list

    def update(self, left, right, found):
        if left:
            left = (left[0] + self.offset[0], left[1] + self.offset[1])
        if right:
            right = (right[0] + self.offset[0], right[1] + self.offset[1])
        self.image.fill((0, 0, 0))

        for tile in self.tiles.values():
            returned = tile.update(self.image, left, right, found)
            if returned == 'lose':
                return 'lose'
            else:
                found = returned

        self.draw()
        return found

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def add_mines(self, mines):
        m = [tile for tile in self.tiles.values()]
        for n in range(mines):
            repeated = True
            while repeated:
                i = random.randint(0, (self.height * self.width) - 1)
                if m[i].mine:
                    repeated = True
                else:
                    m[i].assign_mine()
                    repeated = False

    def assign_text(self):
        for tile in self.tiles.values():
            if tile.mine:
                continue
            counter = 0
            for a in tile.get_adjacents():
                if a.mine:
                    counter += 1
            if counter == 0:
                continue
            else:
                tile.update_text(str(counter))


class Game:

    def __init__(self, screen, mines=20):
        self.screen = screen
        self.mines = mines
        self.running = True
        width = self.screen.get_width() // 2
        height = self.screen.get_height() // 2
        self.grid = Grid(self.screen, (15, 15), 30, (width, height))
        self.clock = pygame.time.Clock()

    def run(self):
        self.grid.add_mines(self.mines)
        self.grid.assign_text()

        found = 0

        while self.running:
            dt = self.clock.get_time() / 1000
            left_pos = None
            right_pos = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == LEFT:
                        left_pos = pygame.mouse.get_pos()
                    elif event.button == RIGHT:
                        right_pos = pygame.mouse.get_pos()

            self.screen.fill((200, 200, 200))
            returned = self.grid.update(left_pos, right_pos, found)
            if returned == 'lose':
                self.lose()
                self.running = False
            else:
                found = returned

            if found == self.mines:
                self.win()
                self.running = False

            pygame.display.flip()
            self.clock.tick(60)

    def win(self):
        m1 = TextBox((self.screen.get_width() // 2, self.screen.get_height() //2),
                          (600, 100), 'You Win!', (0, 0, 0), 30, (0, 255, 0))
        m2 = TextBox((self.screen.get_width() // 2, self.screen.get_height() //2 + 150),
                          (600, 100), 'Press ENTER to quit.', (0, 0, 0), 20, (0, 255, 0))
        messages = [m1, m2]

        done = False
        while not done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True

            self.screen.fill((0, 255, 0))

            for m in messages:
                m.draw(self.screen)

            pygame.display.flip()

    def lose(self):
        m1 = TextBox((self.screen.get_width() // 2, self.screen.get_height() //2),
                          (600, 100), 'You Lose!', (0, 0, 0), 30, (255, 0, 0))
        m2 = TextBox((self.screen.get_width() // 2, self.screen.get_height() //2 + 150),
                          (600, 100), 'Press ENTER to quit.', (0, 0, 0), 20, (255, 0, 0))
        messages = [m1, m2]

        done = False
        while not done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        done = True

            self.screen.fill((255, 0, 0))

            for m in messages:
                m.draw(self.screen)

            pygame.display.flip()


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


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    g = Game(display)
    g.run()
    pygame.quit()
