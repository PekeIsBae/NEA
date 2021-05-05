# Takes a level file as input (Set to None if new level)
# On quitting the level should be written in text json form to the levels folder

import pygame as pg

FPS = 30

PLAYER_CLR = (178, 34, 34)  # https://graf1x.com/shades-of-red-color-palette-hex-rgb-code/ (Fire Brick)
BOX_CLR = (67, 38, 22)  # https://www.color-meanings.com/shades-of-brown-color-names-html-hex-rgb-codes/ (Walnut)
WALL_CLR = (72, 72, 72)  # http://ezavada.com/pdg/javascript/html/classpdg_1_1_color.html ('#484848')
TILE_CLR = (250, 218, 94)  # https://graf1x.com/shades-of-yellow-color-palette-chart/ (Royal)
GTILE_CLR = (93, 187, 99)  # https://www.color-meanings.com/shades-of-green-color-names-html-hex-rgb-codes/ (Fern)

edit_cnfg = {
    'title': 'Create/Edit level',
    'x': 1100,
    'y': 700,
    'bg_col': (136, 136, 136),
    'b_x': 1100/10,
    'b_y': 700/5,
    'b_sizex': 80,
    'b_sizey': 80,
    'wrk_x': 1100/2,
    'wrk_y': 700/2,
    'wrk_sizex': 700-50,
    'wrk_sizey': 700-50
}


class GameSprite(pg.sprite.Sprite):

    def __init__(self, x, y, w, h, fill=None):
        # Change fill=None to sprite=None after prototype is working
        super().__init__()
        self.image = pg.Surface((w, h))
        if fill:
            self.image.fill(fill)

        '''
        if sprite is None:
            self.image = pg.Surface((w, h))
        else:
            self.image = pg.image.load(f'images/{sprite}').convert()
        '''

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.center = (x, y)


class EmptySlot(GameSprite):
    '''
    Empty slots and tiles are fitted onto the grid by a tile buffer
    Each tile and empty slot has a row and column, this multiplied by tile buffer gives pixel pos
    When grid is expanded:
        - Adjust tile buffer appropriately
        - Give all existing tiles and empty slots row and column + 1
    '''
    pass


class Workspace(GameSprite):
    '''
    How editing will work:
    - Grid starts as a 9/9
    - Placing an item on the outermost rim of the grid adds an outer layer to the grid, zooming out
    '''
    pass


class Editor:

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((edit_cnfg['x'], edit_cnfg['y']))
        self.screen.fill(edit_cnfg['bg_col'])
        self.clock = pg.time.Clock()
        pg.display.set_caption(edit_cnfg['title'])
        self.done = False

        self.create_widgets()

        self.mainloop()

    def create_widgets(self):
        self.player_b = GameSprite(edit_cnfg['b_x'], edit_cnfg['b_y'], edit_cnfg['b_sizex'],
                                   edit_cnfg['b_sizey'], PLAYER_CLR)
        self.box_b = GameSprite(edit_cnfg['b_x'], edit_cnfg['b_y']*2, edit_cnfg['b_sizex'],
                                edit_cnfg['b_sizey'], BOX_CLR)
        self.wall_b = GameSprite(edit_cnfg['b_x'], edit_cnfg['b_y']*3, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'], WALL_CLR)
        self.gtile_b = GameSprite(edit_cnfg['b_x'], edit_cnfg['b_y']*4, edit_cnfg['b_sizex'],
                                  edit_cnfg['b_sizey'], GTILE_CLR)

        self.eraser_b = GameSprite(edit_cnfg['x'] - edit_cnfg['b_x'], edit_cnfg['b_y'], edit_cnfg['b_sizex'],
                                   edit_cnfg['b_sizey'])
        self.wipe_b = GameSprite(edit_cnfg['x'] - edit_cnfg['b_x'], edit_cnfg['b_y']*2, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'])
        self.save_b = GameSprite(edit_cnfg['x'] - edit_cnfg['b_x'], edit_cnfg['b_y']*3, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'])
        self.quit_b = GameSprite(edit_cnfg['x'] - edit_cnfg['b_x'], edit_cnfg['b_y']*4, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'])

        self.workspace = Workspace(edit_cnfg['wrk_x'], edit_cnfg['wrk_y'],
                                   edit_cnfg['wrk_sizex'], edit_cnfg['wrk_sizey'])

        self.buttons_group = pg.sprite.Group()
        self.buttons_group.add(self.player_b, self.box_b, self.wall_b, self.gtile_b,
                               self.eraser_b, self.wipe_b, self.save_b, self.quit_b)

        self.workspace_group = pg.sprite.Group()
        self.workspace_group.add(self.workspace)

    def draw_groups(self):
        self.workspace_group.draw(self.screen)
        self.buttons_group.draw(self.screen)

    def mainloop(self):

        while not self.done:

            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True

            self.draw_groups()

            pg.display.flip()

        pg.quit()


if __name__ == '__main__':
    win = Editor()
