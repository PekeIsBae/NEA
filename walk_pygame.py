# Play a Sokoban game made using PyGame

import pygame as pg

'''
- Later it may be necessary to include a written form of the layout for each level in their text file
- 'grid_dimensions' can be a quick way of the game finding the minimum square space it needs to fit all level tiles in
- The actual tiles can then have their locations indicated in the layout, either explicitly or by 'voids'
'''

'''
Current Goal:

- Fill the screen with tile objects of uniform area
- The dimensions of the grid they form needs to be depended on how many tiles there are
- The more tiles there are, the smaller those tiles are

(Complete)

Extra: Potentially remove the 'scanlines' caused by lack of divisibility between grid and board dims
Likely rounding up/down will work
'''

SCREEN_DIMS = (800, 500)
BOARD_OFFSET = (10, 10)
BOARDW = SCREEN_DIMS[0] / 1.6
BOARDH = SCREEN_DIMS[1] - (BOARD_OFFSET[0]*2)

GRID_DIMS = (30, 30)

SCREEN_COLOUR = (136, 136, 136)  # http://ezavada.com/pdg/javascript/html/classpdg_1_1_color.html ('#888888')
TILE_COLOUR = (250, 218, 94)  # https://graf1x.com/shades-of-yellow-color-palette-chart/ (Royal)

pg.init()
screen = pg.display.set_mode(SCREEN_DIMS)
pg.display.set_caption('walk')
clock = pg.time.Clock()


class Game:

    def __init__(self):
        pg.init()
        pg.display.set_caption('walk')
        self.screen = pg.display.set_mode(SCREEN_DIMS)
        self.screen.fill(SCREEN_COLOUR)
        self.clock = pg.time.Clock()
        self.done = False
        self.b = Board()
        self.game_mainloop()

    def game_mainloop(self):

        '''
        As this is a turn-based game, there is no need to update all sprites every frame
        Updates to variables should only happen after a valid move is made
        '''

        while not self.done:

            clock.tick(30)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True

            self.screen.blit(self.b, BOARD_OFFSET)
            pg.display.flip()

        pg.quit()


class Board(pg.Surface):

    '''
    The 'board' will appear as a section of the game screen.
    It will be where the game is actually played
    '''

    def __init__(self):
        super().__init__((BOARDW, BOARDH))
        self.layout = []
        # To demonstrate that tiles are properly positioned
        #self.col = 0
        self.tile_group = pg.sprite.Group()
        self.draw_tiles()
        self.tile_group.draw(self)

    def draw_tiles(self):
        for row in range(0, GRID_DIMS[0]):
            for column in range(0, GRID_DIMS[1]):
                #self.tile_group.add(Tile(column * (BOARDW / GRID_DIMS[0]), row * (BOARDH / GRID_DIMS[1]), self.col + (3*column) + (3*row)))
                self.tile_group.add(Tile(column * (BOARDW / GRID_DIMS[0]), row * (BOARDH / GRID_DIMS[1])))


class Tile(pg.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        # Size of this surface must vary by the board width and number of tiles
        self.image = pg.Surface((BOARDW / GRID_DIMS[0], BOARDH / GRID_DIMS[1]))
        self.image.fill(TILE_COLOUR)
        #self.image.fill((col, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


if __name__ == '__main__':
    game = Game()
