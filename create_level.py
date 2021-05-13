# Takes a level file as input (Set to None if new level)
# On quitting the level should be written in text json form to the levels folder

import pygame as pg
import math
import json

FPS = 30

PLAYER_CLR = (178, 34, 34)  # https://graf1x.com/shades-of-red-color-palette-hex-rgb-code/ (Fire Brick)
BOX_CLR = (67, 38, 22)  # https://www.color-meanings.com/shades-of-brown-color-names-html-hex-rgb-codes/ (Walnut)
WALL_CLR = (72, 72, 72)  # http://ezavada.com/pdg/javascript/html/classpdg_1_1_color.html ('#484848')
TILE_CLR = (250, 218, 94)  # https://graf1x.com/shades-of-yellow-color-palette-chart/ (Royal)
GTILE_CLR = (93, 187, 99)  # https://www.color-meanings.com/shades-of-green-color-names-html-hex-rgb-codes/ (Fern)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

edit_cnfg = {
    'title': 'Create/Edit level',
    'w': 1100,
    'h': 700,
    'bg_col': (136, 136, 136),
    'b_x': 1100/10,
    'b_left_y': 700/5,
    'b_right_y': 700/6,
    'b_sizex': 80,
    'b_sizey': 80,
    'wrk_x': 1100/2,
    'wrk_y': 700/2,
    'wrk_sizex': 700-50,
    'wrk_sizey': 700-50,
    'base_grid_dim': 4,
}

saveas_cnfg = {
    'main_box_x': 1100/2,
    'main_box_y': 700/2,
    'main_box_w': 500,
    'main_box_h': 130,
    'txt_box_y': 700/2 + 20,
    'txt_box_w': 470,
    'txt_box_h': 60,
    'shade': (0, 0, 0, 200),
    'labelx': 1100/2 - 72,
    'labely': 700/2 - 45,
    'save_namex': 1100/2 - 210,
    'save_namey': 700/2 + 20 - 10,
    'confirm_b_y': 700/2 + 150,
    'confirm_b_w': 200,
    'confirm_b_h': 50,
    'confirm_txt_x': 1100/2 - 42,
    'confirm_txt_y': 700/2 + 138,
    'b_rad': 5,
    'name_surf_lim': 470 - 60,
    'box_outline': 2,
    'font_size': 32,
}

'''
Final Stages:
- Add level naming for Save As option
- Add grid extention
- Add editing for existing levels
'''


class GameSprite(pg.sprite.Sprite):

    def __init__(self, x, y, w, h):
        # Change fill=None to sprite=None after prototype is working
        super().__init__()
        self.image = pg.Surface((w, h))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.rect.center = (x, y)


class Button(GameSprite):

    def __init__(self, x, y, w, h, sprite):
        super().__init__(x, y, w, h)
        self.sprite = sprite
        self.image = pg.image.load(f'./images/{self.sprite}').convert()
        self.image = pg.transform.scale(self.image, (w, h))


class EditButton(Button):

    def __init__(self, x, y, w, h, paint, sprite):
        super().__init__(x, y, w, h, sprite)
        self.paint = paint

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
        self.goal_tile = False
        self.row = row
        self.col = col
        self.w = w
        self.h = h
        self.change_sprite('tile')

    def change_sprite(self, sprite):
        self.image = pg.transform.scale(pg.image.load(f'./images/{sprite}.png').convert(), (self.w, self.h))

    def get_coords(self):
        return self.col, self.row

    def get_goal_tile(self):
        return self.goal_tile

    def get_contents(self):
        return self.contents

    def erase_contents(self):
        self.contents = None
        if self.goal_tile:
            self.change_sprite('goal_tile')
        else:
            self.change_sprite('tile')

    def goal_tile_on(self):
        self.goal_tile = True
        self.change_sprite('goal_tile')

    def goal_tile_off(self):
        self.goal_tile = False
        self.change_sprite('tile')

    def add_fitted_box(self):
        self.contents = 'box'
        self.change_sprite('fitted_box')

    def add_contents(self, item):
        self.contents = item
        self.change_sprite(item)


class Workspace(GameSprite):

    '''
    How editing will work:
    - Grid starts as a 4/4
    - Placing an item on the outermost rim of the grid adds an outer layer to the grid, zooming out
    '''

    def __init__(self, x, y, w, h, curr_level_data):
        super().__init__(x, y, w, h)
        self.empty_slots_group = pg.sprite.Group()
        self.grid_dim = edit_cnfg['base_grid_dim']
        self.set_board(self.grid_dim)

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
                slot.erase_contents()

    def get_slot_data(self):
        self.level_data = {"name": "", "grid_dim": self.grid_dim, "player_coords": [], "box_coords": [],
                           "wall_coords": [], "goal_tile_coords": []}
        for slot in self.empty_slots_group:
            if slot.get_goal_tile():
                self.level_data["goal_tile_coords"].append(slot.get_coords())
            if slot.get_contents():
                if slot.get_contents():
                    self.level_data[f"{slot.get_contents()}_coords"].append(slot.get_coords())
        return self.level_data

    def events(self, mouse_point, paint):
        for slot in self.empty_slots_group:
            if slot.rect.collidepoint(self.localise_pos(mouse_point)):
                if paint == 'eraser':
                    if slot.get_goal_tile() and not slot.get_contents():
                        slot.goal_tile_off()
                    else:
                        slot.erase_contents()
                elif not slot.get_contents():
                    if paint == 'goal_tile':
                        slot.goal_tile_on()
                    else:
                        if slot.get_goal_tile() and paint == 'box':
                            slot.add_fitted_box()
                        elif not slot.get_goal_tile():
                            if paint == 'player':
                                self.remove_current_player()
                                slot.add_contents(paint)
                            else:
                                slot.add_contents(paint)

        self.empty_slots_group.draw(self.image)


class SaveAs:

    def __init__(self, editor_screen_img):
        self.original_bg = editor_screen_img
        self.screen = pg.display.set_mode(self.original_bg.get_size())
        self.dark = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dark.fill(saveas_cnfg['shade'])

        pg.key.set_repeat(500, 25)

        self.clock = pg.time.Clock()
        self.done = False

        self.save_name = ''
        self.confirmed = False
        self.txt_box_active = False

        self.create_widgets()

        self.mainloop()

    def create_widgets(self):
        self.main_box = GameSprite(saveas_cnfg['main_box_x'], saveas_cnfg['main_box_y'],
                                   saveas_cnfg['main_box_w'], saveas_cnfg['main_box_h'])
        self.text_box = GameSprite(saveas_cnfg['main_box_x'], saveas_cnfg['txt_box_y'],
                                   saveas_cnfg['txt_box_w'], saveas_cnfg['txt_box_h'])
        self.font = pg.font.Font(None, saveas_cnfg['font_size'])
        self.save_label = 'Save level as ...'
        self.save_label_txt = self.font.render(self.save_label, True, WHITE)
        self.save_name_txt = self.font.render(self.save_name, True, WHITE)
        self.confirm_b_txt = self.font.render('Confirm', True, WHITE)
        self.confirm_b = GameSprite(saveas_cnfg['main_box_x'], saveas_cnfg['confirm_b_y'],
                                    saveas_cnfg['confirm_b_w'], saveas_cnfg['confirm_b_h'])

    def draw_all(self):
        self.txt_box_col = WHITE if self.txt_box_active else BLACK
        self.screen.blit(self.original_bg, (0, 0))
        self.screen.blit(self.dark, (0, 0))
        self.screen.blit(self.save_label_txt, (saveas_cnfg['labelx'], saveas_cnfg['labely']))
        self.screen.blit(self.confirm_b_txt, (saveas_cnfg['confirm_txt_x'], saveas_cnfg['confirm_txt_y']))
        pg.draw.rect(self.screen, WHITE, self.main_box.rect, saveas_cnfg['box_outline'], saveas_cnfg['b_rad'])
        pg.draw.rect(self.screen, self.txt_box_col, self.text_box.rect, saveas_cnfg['box_outline'], saveas_cnfg['b_rad'])
        pg.draw.rect(self.screen, WHITE, self.confirm_b.rect, saveas_cnfg['box_outline'], saveas_cnfg['b_rad'])
        if self.save_name:
            self.screen.blit(self.save_name_txt,
                             (saveas_cnfg['save_namex'], saveas_cnfg['save_namey']))

    def get_name(self):
        if self.confirmed:
            return self.save_name

    def mainloop(self):

        self.clock.tick(FPS)

        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.text_box.rect.collidepoint(event.pos):
                            self.txt_box_active = True
                        elif self.confirm_b.rect.collidepoint(event.pos):
                            if len(self.save_name) > 0:
                                self.confirmed = True
                                self.done = True
                        else:
                            self.done = True
                if event.type == pg.KEYDOWN:
                    if self.txt_box_active:
                        if event.key == pg.K_BACKSPACE:
                            self.save_name = self.save_name[:-1]
                        elif (event.unicode.isalnum() or event.key == pg.K_SPACE) \
                                and self.save_name_txt.get_width() < saveas_cnfg['name_surf_lim']:
                            self.save_name += event.unicode
                        self.save_name_txt = self.font.render(self.save_name, True, WHITE)

            self.draw_all()

            pg.display.flip()


class Editor:

    def __init__(self, curr_level_data):
        pg.init()
        self.screen = pg.display.set_mode((edit_cnfg['w'], edit_cnfg['h']))
        self.screen.fill(edit_cnfg['bg_col'])
        self.clock = pg.time.Clock()
        pg.display.set_caption(edit_cnfg['title'])
        self.curr_level_data = curr_level_data
        self.done = False

        self.exiting_level = True if self.curr_level_data else False

        self.selected = None

        self.create_widgets()

        self.mainloop()

    def create_widgets(self):
        self.player_b = EditButton(edit_cnfg['b_x'], edit_cnfg['b_left_y'], edit_cnfg['b_sizex'],
                                   edit_cnfg['b_sizey'], 'player', 'player.png')
        self.box_b = EditButton(edit_cnfg['b_x'], edit_cnfg['b_left_y']*2, edit_cnfg['b_sizex'],
                                edit_cnfg['b_sizey'], 'box', 'box.png')
        self.wall_b = EditButton(edit_cnfg['b_x'], edit_cnfg['b_left_y']*3, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'], 'wall', 'wall.png')
        self.gtile_b = EditButton(edit_cnfg['b_x'], edit_cnfg['b_left_y']*4, edit_cnfg['b_sizex'],
                                  edit_cnfg['b_sizey'], 'goal_tile', 'goal_tile.png')

        self.eraser_b = EditButton(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_right_y'], edit_cnfg['b_sizex'],
                                   edit_cnfg['b_sizey'], 'eraser', 'eraser.png')
        self.reset_b = EditButton(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_right_y']*2, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'], None, 'reset.png')
        self.save_b = EditButton(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_right_y']*3, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'], None, 'save.png')
        self.save_as_b = EditButton(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_right_y']*4, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'], None, 'save_as.png')
        self.quit_b = EditButton(edit_cnfg['w'] - edit_cnfg['b_x'], edit_cnfg['b_right_y']*5, edit_cnfg['b_sizex'],
                                 edit_cnfg['b_sizey'], None, 'quit.png')

        self.workspace = Workspace(edit_cnfg['wrk_x'], edit_cnfg['wrk_y'],
                                   edit_cnfg['wrk_sizex'], edit_cnfg['wrk_sizey'], self.curr_level_data)

        self.edit_group = pg.sprite.Group()
        self.edit_group.add(self.player_b, self.box_b, self.wall_b, self.gtile_b,
                            self.eraser_b, self.reset_b, self.save_as_b, self.quit_b)
        if self.exiting_level:
            self.edit_group.add(self.save_b)

        self.workspace_group = pg.sprite.Group()
        self.workspace_group.add(self.workspace)

    def reset_board(self):
        self.workspace_group = pg.sprite.Group()
        self.workspace = Workspace(edit_cnfg['wrk_x'], edit_cnfg['wrk_y'],
                                   edit_cnfg['wrk_sizex'], edit_cnfg['wrk_sizey'], self.curr_level_data)
        self.workspace_group.add(self.workspace)

    def compile_level(self, name):
        self.level_data = self.workspace.get_slot_data()
        self.level_data['name'] = name
        self.file_name = name.replace(' ', '_')
        with open(f'./levels/{self.file_name}.txt', 'w') as file:
            json.dump(self.level_data, file, indent=4)

    def confirm_write(self):
        self.curr_screen = pg.Surface((self.screen.get_size()))
        self.curr_screen.blit(self.screen, (0, 0))
        self.save_name = SaveAs(self.curr_screen).get_name()
        if self.save_name:
            self.compile_level(self.save_name)

    def draw_groups(self):
        self.workspace_group.draw(self.screen)
        self.edit_group.draw(self.screen)

    def mainloop(self):

        while not self.done:

            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_point = event.pos
                        for button in self.edit_group:
                            if button.rect.collidepoint(self.mouse_point):
                                self.selected = button.get_paint()
                        if self.reset_b.rect.collidepoint(self.mouse_point):
                            self.reset_board()
                        if self.save_b.rect.collidepoint(self.mouse_point):
                            # Save writes over the original level file with the same name
                            self.compile_level('new_lvl')
                        if self.save_as_b.rect.collidepoint(self.mouse_point):
                            # Save as will open a window for the user to write a new file name
                            self.confirm_write()
                        if self.quit_b.rect.collidepoint(self.mouse_point):
                            self.done = True
                        if self.workspace.rect.collidepoint(self.mouse_point) and self.selected:
                            self.workspace.events(self.mouse_point, self.selected)

            self.screen.fill(edit_cnfg['bg_col'])
            self.draw_groups()

            pg.display.flip()

        pg.quit()


if __name__ == '__main__':
    win = Editor(None)
