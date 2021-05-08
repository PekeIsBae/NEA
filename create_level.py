# Takes a level file as input (Set to None if new level)
# On quitting the level should be written in text json form to the levels folder

import pygame as pg
import math

FPS = 30

PLAYER_CLR = (178, 34, 34)  # https://graf1x.com/shades-of-red-color-palette-hex-rgb-code/ (Fire Brick)
BOX_CLR = (67, 38, 22)  # https://www.color-meanings.com/shades-of-brown-color-names-html-hex-rgb-codes/ (Walnut)
WALL_CLR = (72, 72, 72)  # http://ezavada.com/pdg/javascript/html/classpdg_1_1_color.html ('#484848')
TILE_CLR = (250, 218, 94)  # https://graf1x.com/shades-of-yellow-color-palette-chart/ (Royal)
GTILE_CLR = (93, 187, 99)  # https://www.color-meanings.com/shades-of-green-color-names-html-hex-rgb-codes/ (Fern)

WHITE = (255, 255, 255)

edit_cnfg = {
    'title': 'Create/Edit level',
    'w': 1100,
    'h': 700,
    'bg_col': (136, 136, 136),
    'b_x': 1100/10,
    'b_y': 700/5,
    'b_sizex': 80,
    'b_sizey': 80,
    'wrk_x': 1100/2,
    'wrk_y': 700/2,
    'wrk_sizex': 700-50,
    'wrk_sizey': 700-50,
    'base_grid_dim': 4,
}


class GameSprite(pg.sprite.Sprite):

    def __init__(self, x, y, w, h):
        # Change fill=None to sprite=None after prototype is working
        super().__init__()
        self.image = pg.Surface((w, h))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Changing rect.centre only moves the rect's centre to a position, not change what its 'centre' is
        # So, this is used to make initial sprite placement easier
        self.rect.center = (x, y)


class EditButton(GameSprite):

    def __init__(self, x, y, w, h, paint, sprite=None):
        super().__init__(x, y, w, h)
        self.paint = paint
        self.sprite = sprite
        if self.sprite:
            self.image = pg.image.load(f'./images/{self.sprite}').convert()
            self.image = pg.transform.scale(self.image, (w, h))

    def get_paint(self):
        return self.paint


class EmptySlot(GameSprite):

    '''
    Empty slots and tiles are fitted onto the grid by a tile buffer
    Each tile and empty slot has a row and column, this multiplied by tile buffer gives pixel pos
    When grid is expanded:
        - Adjust tile buffer appropriately
        - Give all existing tiles and empty slots row and column + 1
    '''

    def __init__(self, x, y, w, h, row, col, edge):
        super().__init__(x, y, w, h)
        self.rect.center = (x + w/2, y + h/2)
        self.edge = edge
        self.contents = None
        self.row = row
        self.col = col
        self.w = w
        self.h = h
        if self.edge:
            self.image.fill((0, 255, 0))

    def get_coords(self):
        return self.row, self.col

    def get_contents(self):
        return self.contents

    def update_contents(self, item):
        self.contents = item
        self.image = pg.transform.scale(pg.image.load(f'./images/wall.png').convert(), (self.w, self.h))


class Workspace(GameSprite):

    '''
    How editing will work:
    - Grid starts as a 4/4
    - Placing an item on the outermost rim of the grid adds an outer layer to the grid, zooming out
    '''

    def __init__(self, x, y, w, h, level_data):
        super().__init__(x, y, w, h)
        self.empty_slots_group = pg.sprite.Group()
        self.set_board(edit_cnfg['base_grid_dim'])

    def set_board(self, grid_dim):
        for row in range(0, grid_dim):
            for col in range(0, grid_dim):
                self.edge = False
                if col == 0 or col == grid_dim - 1 or row == 0 or row == grid_dim - 1:
                    self.edge = True
                self.empty_slot = EmptySlot(edit_cnfg['wrk_sizex']/grid_dim*col, edit_cnfg['wrk_sizey']/grid_dim*row,
                                            math.ceil(edit_cnfg['wrk_sizex']/grid_dim),
                                            math.ceil(edit_cnfg['wrk_sizey']/grid_dim),
                                            row, col, self.edge)
                self.empty_slots_group.add(self.empty_slot)
        self.empty_slots_group.draw(self.image)

    def localise_pos(self, pos):
        return pos[0] - self.rect.x, pos[1] - self.rect.y

    def remove_current_player(self):
        for slot in self.empty_slots_group:
            if slot.get_contents() == 'player':
                slot.update_contents(None)

    def events(self, mouse_point, paint):
        if paint == 'player':
            self.remove_current_player()
        for slot in self.empty_slots_group:
            if slot.rect.collidepoint(self.localise_pos(mouse_point)):
                slot.update_contents(paint)

        self.empty_slots_group.draw(self.image)


class Editor:

    def __init__(self, level_data):
        pg.init()
        self.screen = pg.display.set_mode((edit_cnfg['w'], edit_cnfg['h']))
        self.screen.fill(edit_cnfg['bg_col'])
        self.clock = pg.time.Clock()
        pg.display.set_caption(edit_cnfg['title'])
        self.level_data = level_data
        self.done = False

        self.selected = None

        self.create_widgets()

        self.mainloop()

    def create_widgets(self):
        self.player_b = EditButton(edit_cnfg['b_x'], edit_cnfg['b_y'], edit_cnfg['b_sizex'],
                                   edit_cnfg['b_sizey'], 'player')
        self.box_b = EditButton(edit_cnfg['b_x'], edit_cnfg['b_y']*2, edit_cnfg['b_sizex'],
                                edit_cnfg['b_sizey'], 'box')
        self.wall_b = EditButton(edit_cnfg['b_x'], edit_cnfg['b_y']*3, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'], 'wall', 'wall.png')
        self.gtile_b = EditButton(edit_cnfg['b_x'], edit_cnfg['b_y']*4, edit_cnfg['b_sizex'],
                                  edit_cnfg['b_sizey'], 'gtile')

        self.eraser_b = EditButton(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_y'], edit_cnfg['b_sizex'],
                                   edit_cnfg['b_sizey'], None)
        self.wipe_b = GameSprite(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_y']*2, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'])
        self.save_b = GameSprite(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_y']*3, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'])
        self.quit_b = GameSprite(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_y']*4, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'])

        self.workspace = Workspace(edit_cnfg['wrk_x'], edit_cnfg['wrk_y'],
                                   edit_cnfg['wrk_sizex'], edit_cnfg['wrk_sizey'], self.level_data)

        self.palette_group = pg.sprite.Group()
        self.palette_group.add(self.player_b, self.box_b, self.wall_b, self.gtile_b,
                               self.eraser_b)

        self.workspace_group = pg.sprite.Group()
        self.workspace_group.add(self.workspace)

    def draw_groups(self):
        self.workspace_group.draw(self.screen)
        self.palette_group.draw(self.screen)

    def mainloop(self):

        while not self.done:

            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_point = event.pos
                        for button in self.palette_group:
                            if button.rect.collidepoint(self.mouse_point):
                                self.selected = button.get_paint()
                        if self.workspace.rect.collidepoint(self.mouse_point) and self.selected:
                            self.workspace.events(self.mouse_point, self.selected)

            self.draw_groups()

            pg.display.flip()

        pg.quit()


if __name__ == '__main__':
    win = Editor(None)
