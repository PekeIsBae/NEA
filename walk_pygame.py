# Play a Sokoban game made using PyGame

import pygame as pg
import tkinter as tk
# Missing pixels between tiles solved using math.ciel, but this may cause problems with collisions down the line
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

# Screen and Board dimension constants
SCREEN_DIMS = (800, 600)
BOARD_OFFSET = (10, 10)
BUTTON_SIZE = (80, 80)
# The size of the board depends on how large the screen is
BOARDW = SCREEN_DIMS[0] / 1.3
BOARDH = SCREEN_DIMS[1] - (BOARD_OFFSET[0]*2)


class MainMenu:

    def __init__(self, root):
        self.root = root
        self.root.title("PySoko")
        self.create_widgets()

    def create_widgets(self):
        self.levels_f = tk.Frame(self.root)
        self.levels_f.pack(padx=10, pady=10, side='left')
        self.levels_c = tk.Canvas(self.levels_f)
        self.levels_c.pack(side='top')
        self.create_b = tk.Button(self.levels_f, width=50, height=5, text='Create new level')
        self.create_b.pack(side='bottom')
        self.levelops_f = tk.Frame(self.root)
        self.levelops_f.pack(side='right')
        self.lvlpreview_c = tk.Canvas(self.levelops_f, width=250, height=250)
        self.lvlpreview_c.pack()
        self.levelops_buttons_f = tk.Frame(self.levelops_f, padx=10, pady=10)
        self.levelops_buttons_f.pack(padx=5, pady=5, side='bottom')
        self.play_b = tk.Button(self.levelops_buttons_f, width=15, height=4, text='Play', command=self.play)
        self.play_b.grid(padx=5, pady=5, row=0, column=0)
        self.edit_b = tk.Button(self.levelops_buttons_f, width=15, height=4, text='Edit')
        self.edit_b.grid(padx=5, pady=5, row=0, column=1)
        self.leader_b = tk.Button(self.levelops_buttons_f, width=15, height=4, text='Leaderboard')
        self.leader_b.grid(padx=5, pady=5, row=1, column=0)
        self.delete_b = tk.Button(self.levelops_buttons_f, width=15, height=4, text='Delete')
        self.delete_b.grid(padx=5, pady=5, row=1, column=1)

    def play(self):
        self.game = Game("new_lvl.txt")

class Game:

    def __init__(self, level_file):
        pg.init()
        pg.display.set_caption('walk')
        self.screen = pg.display.set_mode(SCREEN_DIMS)
        self.screen.fill(SCREEN_COLOUR)
        self.clock = pg.time.Clock()
        self.done = False
        pg.key.set_repeat(400, 50)
        self.level_data = self.parse_level_data(level_file)
        self.b = Board(self.level_data)

        self.undo_b = pg.Rect(SCREEN_DIMS[0]*0.84, SCREEN_DIMS[1]*(1/7), BUTTON_SIZE[0], BUTTON_SIZE[1])
        self.restart_b = pg.Rect(SCREEN_DIMS[0] * 0.84, SCREEN_DIMS[1] * (3/7), BUTTON_SIZE[0], BUTTON_SIZE[1])
        self.quit_b = pg.Rect(SCREEN_DIMS[0] * 0.84, SCREEN_DIMS[1] * (5/7), BUTTON_SIZE[0], BUTTON_SIZE[1])

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

            self.clock.tick(30)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                if event.type == pg.KEYDOWN:
                    self.done = self.b.events(event.__dict__['key'])
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.mouse_point = event.pos
                    # The mouse can only be in one place at a time
                    if self.undo_b.collidepoint(self.mouse_point):
                        self.b.undo()
                    if self.restart_b.collidepoint(self.mouse_point):
                        self.b = Board(self.level_data)
                    if self.quit_b.collidepoint(self.mouse_point):
                        self.done = True

            self.screen.blit(self.b, BOARD_OFFSET)

            pg.draw.rect(self.screen, (0, 0, 0), self.undo_b)
            pg.draw.rect(self.screen, (0, 0, 0), self.restart_b)
            pg.draw.rect(self.screen, (0, 0, 0), self.quit_b)

            pg.display.flip()

        pg.quit()


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
        self.fill((0, 0, 0))
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


class Tile_Obj(pg.sprite.Sprite):

    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Moving(Tile_Obj):

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


class Wall(Tile_Obj):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.image.fill(WALL_COLOUR)


class Tile(Tile_Obj):

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
    root = tk.Tk()
    game = MainMenu(root)
    root.mainloop()
