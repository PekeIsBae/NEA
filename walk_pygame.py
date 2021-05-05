# Play a Sokoban game made using PyGame

import pygame as pg
import os
import math
import json

'''
Conditions for a valid level:
- Closed off by walls
- Must not be completed (at least one goal tile uncovered)
- Number of boxes >= number of goal tiles
'''

# Colours
SCREEN_COLOUR = (136, 136, 136)  # http://ezavada.com/pdg/javascript/html/classpdg_1_1_color.html ('#888888')
TILE_COLOUR = (250, 218, 94)  # https://graf1x.com/shades-of-yellow-color-palette-chart/ (Royal)
GTILE_COLOUR = (93, 187, 99)  # https://www.color-meanings.com/shades-of-green-color-names-html-hex-rgb-codes/ (Fern)
PLAYER_COLOUR = (178, 34, 34)  # https://graf1x.com/shades-of-red-color-palette-hex-rgb-code/ (Fire Brick)
BOX_COLOUR = (67, 38, 22)  # https://www.color-meanings.com/shades-of-brown-color-names-html-hex-rgb-codes/ (Walnut)
WALL_COLOUR = (72, 72, 72)  # http://ezavada.com/pdg/javascript/html/classpdg_1_1_color.html ('#484848')
LEVEL_BUTTON_COLOUR = (255, 255, 255)
BLACK = (0, 0, 0)

FPS = 30

# Screen and Board dimension constants
SCREEN_DIMS = (800, 600)
BOARD_OFFSET = (10, 10)

SCROLL_SPD = 10

# Button dimensions and positioning
GAME_BUTTON_SIZE = (80, 80)
# Main Menu
PLAY_DIMS = (440, 375, 340, 200)
CREATE_DIMS = (20, 480, 400, 100)
LEVEL_SELECT_DIMS = (400, 450)
LEVEL_BUTTON_DIMS = (360, 100)
LEVEL_BUTTON_OFFSET = (20, 20)
LEVEL_BUTTON_TEXT_OFFSET = (10, 10)
PREVIEW_DIMS = (340, 340)
PREVIEW_OFFSET = (440, 25)
# Game Screen buttons
UNDO_DIMS = (SCREEN_DIMS[0]*0.84, SCREEN_DIMS[1]*(1/7), GAME_BUTTON_SIZE[0], GAME_BUTTON_SIZE[1])
RESTART_DIMS = (SCREEN_DIMS[0]*0.84, SCREEN_DIMS[1]*(3/7), GAME_BUTTON_SIZE[0], GAME_BUTTON_SIZE[1])
QUIT_DIMS = (SCREEN_DIMS[0]*0.84, SCREEN_DIMS[1]*(5/7), GAME_BUTTON_SIZE[0], GAME_BUTTON_SIZE[1])

# The size of the board depends on how large the screen is
BOARDW = SCREEN_DIMS[0] / 1.3
BOARDH = SCREEN_DIMS[1] - (BOARD_OFFSET[0]*2)

# Instead of the original layout, every button for a level will have a delete, edit and leaderboard icon on it
# These icons do the appropriate actions for their level


class MainMenu:

    def __init__(self):
        pg.init()
        pg.display.set_caption('PySoko')
        self.screen = pg.display.set_mode(SCREEN_DIMS)
        self.screen.fill(SCREEN_COLOUR)
        self.clock = pg.time.Clock()
        self.done = False

        self.selected = None

        self.scroll_offset = 0
        self.max_scroll_offset = -430

        self.level_buttons_group = pg.sprite.Group()
        self.level_buttons = []
        self.menu_buttons_group = pg.sprite.Group()

        self.level_select = GameSprite(20, 20, 400, 450)
        self.preview = pg.Surface(PREVIEW_DIMS)
        self.create_b = GameSprite(20, 480, 400, 100)
        self.play_b = GameSprite(440, 375, 340, 200)
        self.menu_buttons_group.add(self.level_select, self.create_b, self.play_b)

        self.make_level_buttons()

        self.menu_mainloop()

    def get_levels(self):
        return os.listdir('./levels')

    def make_level_buttons(self):
        self.level_select.image.fill(BLACK)
        self.level_buttons_group = pg.sprite.Group()
        self.level_buttons = []
        self.scroll_offset = 0
        self.max_scroll_offset = -430
        for numb, level in enumerate(self.get_levels()):
            self.button = LevelButton(numb, level)
            self.level_buttons_group.add(self.button)
            self.level_buttons.append(self.button)
            self.max_scroll_offset += LEVEL_BUTTON_DIMS[1] + 20
        self.level_buttons_group.draw(self.level_select.image)

    def scroll_menu(self, dir):
        if -self.max_scroll_offset <= (self.scroll_offset + SCROLL_SPD * dir) <= 0:
            self.level_select.image.fill(BLACK)
            self.level_buttons_group.update(dir)
            # Draw sprites onto the empty surface immediately after update to avoid flicker
            self.scroll_offset += SCROLL_SPD * dir
        self.level_buttons_group.draw(self.level_select.image)

    def localise_pos_level_select(self, pos):
        return pos[0] - 20, pos[1] - 20

    def menu_mainloop(self):

        while not self.done:

            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.MOUSEMOTION:
                    self.mouse_point = event.pos
                if event.type == pg.QUIT:
                    self.done = True
                if event.type == pg.MOUSEWHEEL:
                    if self.level_select.rect.collidepoint(self.mouse_point):
                        self.scroll_menu(event.y)
                if event.type == pg.MOUSEBUTTONDOWN:
                    # '1' indicates a left click
                    if event.button == 1:
                        if self.level_select.rect.collidepoint(self.mouse_point):
                            # Make the mouse position be relative to the level_select sprite
                            self.local_pos = self.localise_pos_level_select(self.mouse_point)
                            for button in self.level_buttons:
                                if button.rect.collidepoint(self.local_pos):
                                    self.selected = button
                                    # Make the mouse position be relative to the button selected
                                    self.button_local_pos = button.localise_pos(self.local_pos)
                                    if button.check_option_pressed(self.button_local_pos):
                                        self.option_pos = button.check_option_pressed(self.button_local_pos).rect.x
                                        if self.option_pos == 10:
                                            os.unlink(f'./levels/{button.filename}')
                                            self.make_level_buttons()
                                        elif self.option_pos == 60:
                                            print('Edit')
                                        elif self.option_pos == 110:
                                            print('Leader')
                        if self.create_b.rect.collidepoint(self.mouse_point):
                            self.create = Edit()
                            pg.display.set_caption('PySoko')
                        if self.play_b.rect.collidepoint(self.mouse_point) and self.selected:
                            self.game = Game(self.selected.get_filename(), self.selected.get_display_name())
                            pg.display.set_caption('PySoko')

            self.screen.fill(SCREEN_COLOUR)

            self.screen.blit(self.preview, PREVIEW_OFFSET)

            self.menu_buttons_group.draw(self.screen)
            self.level_buttons_group.draw(self.level_select.image)

            pg.display.flip()

        pg.quit()


class LevelButton(pg.sprite.Sprite):

    def __init__(self, row, filename):
        super().__init__()
        # Level button appearence
        self.image = pg.Surface(LEVEL_BUTTON_DIMS)
        self.image.fill(LEVEL_BUTTON_COLOUR)

        # Draw level name of the level button
        self.font = pg.font.SysFont('Times New Roman', 24)
        self.filename = filename
        self.display_name = self.display_name(self.filename)
        self.text = self.font.render(self.display_name, True, BLACK)
        self.image.blit(self.text, LEVEL_BUTTON_TEXT_OFFSET)

        # Option buttons for delete, edit and leaderboard for each level button
        self.option_buttons_group = pg.sprite.Group()
        self.delete_b = GameSprite(10, 50, 40, 40)
        self.edit_b = GameSprite(60, 50, 40, 40)
        self.leader_b = GameSprite(110, 50, 40, 40)
        self.option_buttons_group.add(self.delete_b, self.edit_b, self.leader_b)
        self.option_buttons_group.draw(self.image)

        # Level button positioning
        self.rect = self.image.get_rect()
        self.rect.x = LEVEL_BUTTON_OFFSET[0]
        self.rect.y = (row * LEVEL_BUTTON_DIMS[1]) + ((row + 1) * LEVEL_BUTTON_OFFSET[1])

    def localise_pos(self, pos):
        return pos[0] - self.rect.x, pos[1] - self.rect.y

    def check_option_pressed(self, pos):
        for button in self.option_buttons_group:
            if button.rect.collidepoint(pos[0], pos[1]):
                return button

    def get_display_name(self):
        return self.display_name

    def get_filename(self):
        return self.filename

    def display_name(self, filename):
        return filename[0:len(filename)-4].replace('_', ' ')

    def update(self, y):
        self.rect.y += SCROLL_SPD * y


class Edit:

    def __init__(self, level_file=None):
        pg.display.set_caption('Create new level')
        self.screen = pg.display.set_mode(SCREEN_DIMS)
        self.screen.fill(SCREEN_COLOUR)
        self.clock = pg.time.Clock()
        self.done = False

        self.editspace = EditSpace(SCREEN_DIMS[0]/2, SCREEN_DIMS[1]/2, 400, 400)
        self.editspace_group = pg.sprite.Group()
        self.editspace_group.add(self.editspace)

        self.edit_mainloop()

    def edit_mainloop(self):

        while not self.done:

            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True

            self.editspace_group.draw(self.screen)

            pg.display.flip()


class Game:

    def __init__(self, level_file, name):
        pg.display.set_caption(name)
        self.screen = pg.display.set_mode(SCREEN_DIMS)
        self.screen.fill(SCREEN_COLOUR)
        self.clock = pg.time.Clock()
        self.done = False
        pg.key.set_repeat(400, 50)

        self.level_data = self.parse_level_data(level_file)
        self.b = Board(self.level_data)

        self.game_buttons_group = pg.sprite.Group()
        self.undo_b = GameSprite(SCREEN_DIMS[0]*0.84, SCREEN_DIMS[1]*(1/7), GAME_BUTTON_SIZE[0], GAME_BUTTON_SIZE[1])
        self.restart_b = GameSprite(SCREEN_DIMS[0]*0.84, SCREEN_DIMS[1]*(3/7), GAME_BUTTON_SIZE[0], GAME_BUTTON_SIZE[1])
        self.quit_b = GameSprite(SCREEN_DIMS[0]*0.84, SCREEN_DIMS[1]*(5/7), GAME_BUTTON_SIZE[0], GAME_BUTTON_SIZE[1])
        self.game_buttons_group.add(self.undo_b, self.restart_b, self.quit_b)

        self.game_mainloop()

    def parse_level_data(self, level_file):
        with open(f'./levels/{level_file}') as file:
            return json.load(file)

    def game_mainloop(self):

        '''
        As this is a turn-based game, there is no need to update all sprites every frame
        Updates to variables should only happen after a valid move is made
        '''

        while not self.done:

            pg.display.flip()

            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                if event.type == pg.KEYDOWN:
                    self.done = self.b.events(event.__dict__['key'])
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_point = event.pos
                        if self.undo_b.rect.collidepoint(self.mouse_point):
                            self.b.undo()
                        if self.restart_b.rect.collidepoint(self.mouse_point):
                            self.b = Board(self.level_data)
                        if self.quit_b.rect.collidepoint(self.mouse_point):
                            self.done = True

            self.screen.blit(self.b, BOARD_OFFSET)

            # Draw game screen buttons
            self.game_buttons_group.draw(self.screen)

            #pg.display.flip()


class Board(pg.Surface):

    def __init__(self, level_data):
        super().__init__((BOARDW, BOARDH))

        # Possibly add a feature that adds void tiles and aligns the level so tile dims are consistent?
        # This feature may be a part of level creation
        # After a level is created, the game my add void blocks around the level to keep tile sizes square looking

        self.map = level_data['map']

        # Coordinates for interactive items (column, row (top to bottom))
        self.player_coords = level_data['player_coords']
        self.box_coords = level_data['box_coords']

        self.boxes = []
        self.gtiles = []

        self.history = []
        self.history_offset = 1

        self.tileh = math.ceil(BOARDH/len(self.map))
        self.tilew = math.ceil(BOARDW/len(self.map[0]))

        # Initialize sprite groups
        self.tile_group = pg.sprite.Group()
        self.gtile_group = pg.sprite.Group()
        self.wall_group = pg.sprite.Group()
        self.box_group = pg.sprite.Group()
        self.player_group = pg.sprite.Group()

        # Initialize objects
        self.p = None
        self.place_objects()

        self.draw()

    def place_objects(self):
        # Responsible for laying the initial board
        self.p = Player(self.player_coords[0] * self.tilew, self.player_coords[1] * self.tileh, self.tilew, self.tileh)
        self.player_group.add(self.p)
        for box_coord in self.box_coords:
            self.b = Box(box_coord[0] * self.tilew, box_coord[1] * self.tileh, self.tilew, self.tileh)
            self.box_group.add(self.b)
            self.boxes.append(self.b)
        for row in range(0, len(self.map)):
            for col in range(0, len(self.map[row])):
                item = self.map[row][col]
                if item == '.':
                    self.tile_group.add(Tile(col * self.tilew, row * self.tileh, self.tilew, self.tileh))
                elif item == '#':
                    self.wall_group.add(Wall(col * self.tilew, row * self.tileh, self.tilew, self.tileh))
                elif item == 'x':
                    self.g = GTile(col * self.tilew, row * self.tileh, self.tilew, self.tileh)
                    self.gtile_group.add(self.g)
                    self.gtiles.append(self.g)
        # Update box moves first, as the player needs them to decide their valid moves
        for box in self.boxes:
            box.update_valid_moves(self.wall_group, self.box_group)
        self.p.update_valid_moves(self.wall_group, self.box_group)

    def undo(self):
        '''
        If the previous move was valid, then the reverse of that move will be valid
        This means no extra positional checks are needed to undo a move
        '''
        # Cannot undo if there are no more moves left to undo
        if self.history_offset > len(self.history):
            return
        # Calculate the reverse of the move the player made
        self.prev_move = self.history[-self.history_offset][0]
        self.rev_move = tuple(map(lambda x: x*-1, self.prev_move))
        # The player must have their move undone first before the box can move
        self.p.undo(self.p.get_key(self.rev_move))
        if self.history[-self.history_offset][1]:
            self.history[-self.history_offset][1].undo(self.p.get_key(self.rev_move))
            for box in self.boxes:
                    box.update_valid_moves(self.wall_group, self.box_group)
        self.p.update_valid_moves(self.wall_group, self.box_group)
        # Allows rewinding multiple moves
        self.history_offset += 1
        self.draw()

    def draw(self):
        self.tile_group.draw(self)
        self.gtile_group.draw(self)
        self.wall_group.draw(self)
        self.player_group.draw(self)
        self.box_group.draw(self)

    def events(self, key):
        # Wipe the screen
        self.fill(BLACK)
        # Only need to update variables if the move was valid
        if key in self.p.get_valid_moves().keys():
            self.history = self.history[0:len(self.history) - (self.history_offset - 1)]
            self.history.append(self.p.move(key))
            self.history_offset = 1
            for box in self.boxes:
                box.update_valid_moves(self.wall_group, self.box_group)
            # Update the players valid moves first at it relies on the boxes valid moves
            self.p.update_valid_moves(self.wall_group, self.box_group)
        self.draw()
        # To check for a win, loop through every goal tile to check if a box is on top of it
        for gtile in self.gtiles:
            if not gtile.check_filled(self.box_group):
                return False
        return True


class GameSprite(pg.sprite.Sprite):

    def __init__(self, x, y, w, h, sprite=None):
        super().__init__()
        if sprite is None:
            self.image = pg.Surface((w, h))
        else:
            self.image = pg.image.load(f'images/{sprite}').convert()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class EditSpace(GameSprite):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image.fill(BLACK)
        self.rect.center = (x, y)


class Moving(GameSprite):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.movement_vectors = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}
        self.valid_moves = {}
        self.w = w
        self.h = h

    def get_key(self, vect):
        self.val_index = list(self.movement_vectors.values()).index(vect)
        return list(self.movement_vectors.keys())[self.val_index]

    def get_new_pos(self, key):
        self.newposx = self.rect.x + self.movement_vectors[key][0] * self.w
        self.newposy = self.rect.y + self.movement_vectors[key][1] * self.h
        return self.newposx, self.newposy

    def get_valid_moves(self):
        return self.valid_moves

    def update_valid_moves(self, walls, boxes):
        self.valid_moves = {}
        for key in self.movement_vectors.keys():
            self.valid = True
            self.box_pushed = None
            self.newposx, self.newposy = self.get_new_pos(key)
            for wall in walls:
                if self.newposx == wall.rect.x and self.newposy == wall.rect.y:
                    self.valid = False
                    break
            for box in boxes:
                # There will only ever be one box with the same x and y as new pos
                # Once this box is found, carry out a check and ignore the rest
                if self.newposx == box.rect.x and self.newposy == box.rect.y:
                    self.valid, self.box_pushed = self.assess_box_collision(key, box)
                    break
            if BOARDW <= self.newposx <= 0 or BOARDH <= self.newposy <= 0:
                self.valid = False
            if self.valid:
                self.valid_moves.update({key: self.box_pushed})

    def move(self, key):
        if self.valid_moves[key]:
            self.valid_moves[key].move(key)
        self.rect.x += self.movement_vectors[key][0] * self.w
        self.rect.y += self.movement_vectors[key][1] * self.h
        return self.movement_vectors[key], self.valid_moves[key]

    def undo(self, key):
        self.rect.x += self.movement_vectors[key][0] * self.w
        self.rect.y += self.movement_vectors[key][1] * self.h

    def assess_box_collision(self, key, box):
        return False, None


class Player(Moving):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image.fill(PLAYER_COLOUR)

    def assess_box_collision(self, key, box):
        if key not in box.get_valid_moves():
            return False, None
        else:
            return True, box


class Box(Moving):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image.fill(BOX_COLOUR)


class Wall(GameSprite):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image.fill(WALL_COLOUR)


class Tile(GameSprite):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image.fill(TILE_COLOUR)


class GTile(Tile):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image.fill(GTILE_COLOUR)

    def check_filled(self, boxes):
        for box in boxes:
            if box.rect.x == self.rect.x and box.rect.y == self.rect.y:
                return True
        return False


if __name__ == '__main__':
    game = MainMenu()
