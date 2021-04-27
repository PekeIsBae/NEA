# Simulate a Sokoban level fully with a pre-made level hard-written in code

import json
import os

class PySoko:
    pass

class MainMenu:

    def __init__(self):
        self.main_menu_mainloop()

    def get_levels(self):
        return os.listdir('./old_levels')

    def display_menu(self, levels):
        for counter, level in enumerate(levels):
            print(f'{counter}. {level}')
        self.choice = str(input('Choose a level by their numbers, exit ("e") or create a new level ("c"): '))
        if self.choice == 'c':
            print('WIP')
            return False
        elif self.choice == 'e':
            return True
        try:
            level_numb = int(self.choice)
            if level_numb in list(range(len(levels))):
                self.g = Game(levels[int(self.choice)])
                self.g.start()
                return False
        except ValueError:
            return False

    def main_menu_mainloop(self):
        self.done = False
        while not self.done:
            all_levels = self.get_levels()
            self.done = self.display_menu(all_levels)


class Game:

    def __init__(self, level):
        self.level = level

    def start(self):
        self.b = Board(self.level)
        self.game_mainloop()

    def game_mainloop(self):
        self.done = False
        while not self.done:
            self.done = self.b.events()


class Board:

    def __init__(self, level):
        # Read the level data from the json file
        self.level_data = self.parse_level_data(level)
        self.grid_dimensions = self.level_data['grid_dimensions']
        self.player_coords = self.level_data['player_coords']
        self.wall_coords = self.level_data['wall_coords']
        self.box_coords = self.level_data['box_coords']
        self.gtile_coords = self.level_data['gtile_coords']
        # 2D array: [vector of the move, box that was pushed on that move, otherwise None]
        self.history = []
        self.history_offset = 1
        self.layout = [[Tile(None) for x in range(self.grid_dimensions[0])] for y in range(self.grid_dimensions[1])]
        self.p = Player(self.player_coords[0], self.player_coords[1])
        self.place_objs()

    def parse_level_data(self, level):
        with open(f'./levels/{level}') as file:
            return json.load(file)

    def place_objs(self):
        # Places objects on grid
        for coord in self.wall_coords:
            self.layout[coord[0]][coord[1]].change_contents(Wall())
        for coord in self.box_coords:
            self.layout[coord[0]][coord[1]].change_contents(Box(coord[0], coord[1]))
        for coord in self.gtile_coords:
            self.layout[coord[0]][coord[1]] = Goal_Tile(None)
        self.layout[self.player_coords[0]][self.player_coords[1]].change_contents(self.p)

    def move_player(self, current, new, direction, record):
        self.layout[current[0]][current[1]].change_contents(None)
        # If the place the player moves to has a box in it, move that box in the same direction
        if type(self.layout[new[0]][new[1]].get_contents()) is Box:
            self.box = self.layout[new[0]][new[1]].get_contents()
            if record:
                self.history.append([direction, self.box])
            self.move_box(self.box.get_curr_pos(), self.box.get_new_pos(direction), self.box)
        else:
            if record:
                self.history.append([direction, None])
        self.layout[new[0]][new[1]].change_contents(self.p)

    def move_box(self, current, new, box):
        self.layout[current[0]][current[1]].change_contents(None)
        self.layout[new[0]][new[1]].change_contents(box)

    def undo(self, offset):
        self.move_data = self.history[len(self.history) - offset]
        self.reverse_move = self.p.get_direction(list(map(lambda x: x*-1, self.p.get_vector(self.move_data[0]))))
        self.move_player(self.p.get_curr_pos(), self.p.get_new_pos(self.reverse_move), self.reverse_move, False)
        if self.move_data[1]:
            self.box = self.move_data[1]
            self.move_box(self.box.get_curr_pos(), self.box.get_new_pos(self.reverse_move), self.box)

    def reset(self):
        self.history = []
        self.layout = [[Tile(None) for x in range(self.grid_dimensions[0])] for y in range(self.grid_dimensions[1])]
        self.p = Player(self.player_coords[0], self.player_coords[1])
        self.place_objs()

    def events(self):
        # Go through every box in the layout, change their valid_moves
        self.win = True
        for row in self.layout:
            for tile in row:
                if type(tile.get_contents()) is Box:
                    tile.get_contents().update_valid_moves(self.layout)
                # The game is won if and only if all goal tiles have box on them
                if type(tile) is Goal_Tile and type(tile.get_contents()) is not Box:
                    self.win = False
        if self.win:
            return True
        self.p.update_valid_moves(self.layout)
        self.valid_moves = self.p.get_valid_moves()
        while True:
            direction = str(input('udlr, reset to reset, undo to undo, or 0 to exit: '))
            if direction == '0':
                return True
            elif direction == 'reset':
                self.reset()
                return False
            elif direction == 'undo':
                if self.history_offset > len(self.history):
                    print('No moves left to undo')
                    return False
                self.undo(self.history_offset)
                self.history_offset += 1
                for row in self.layout:
                   print(list(map(lambda x: x.get_contents(), row)))
                print(self.history)
                return False
            elif direction in self.valid_moves:
                # On the player inputting a move, all history that was undo'd is removed
                self.history = self.history[0:len(self.history) - (self.history_offset - 1)]
                self.history_offset = 1
                self.move_player(self.p.get_curr_pos(), self.p.get_new_pos(direction), direction, True)
                # Check layout after moving
                for row in self.layout:
                    print(list(map(lambda x: x.get_contents(), row)))
                # Check history
                # print(self.history)
                # Check type of tile in layout
                # for row in self.layout:
                #    print(row)
                return False


class Moving:

    '''
    The boxes and player as basically the same object, in terms of how they interact with other objects
    The only difference between the two is the player can move boxes, but boxes cannot.

    This slight difference is accounted for by overriding the assess_collisions method
    '''

    def __init__(self, starty, startx):
        self.posy = starty
        self.posx = startx
        self.dirs = ('u', 'd', 'l', 'r')
        self.movement_vectors = ([-1, 0], [1, 0], [0, -1], [0, 1])
        self.valid_moves = []

    def get_vector(self, direction):
        return self.movement_vectors[self.dirs.index(direction)]

    def get_direction(self, vector):
        return self.dirs[self.movement_vectors.index(vector)]

    def get_curr_pos(self):
        return self.posy, self.posx

    def get_new_pos(self, direction):
        self.posy += self.movement_vectors[self.dirs.index(direction)][0]
        self.posx += self.movement_vectors[self.dirs.index(direction)][1]
        return self.posy, self.posx

    def find_valid_moves(self, board):
        self.valid_moves = []
        for counter, dir in enumerate(self.dirs):
            self.valid = True
            self.moves_box = False
            self.new_posy = self.posy + self.movement_vectors[counter][0]
            self.new_posx = self.posx + self.movement_vectors[counter][1]
            try:
                if self.new_posx >= 0 and self.new_posy >= 0:
                    self.tile_at_new_pos = board[self.new_posy][self.new_posx]
                    self.item = self.tile_at_new_pos.get_contents()
                    self.valid = self.assess_collision(self.item, dir)
                else:
                    self.valid = False
            except IndexError:
                self.valid = False
            if self.valid:
                self.valid_moves.append(dir)
        return self.valid_moves

    def assess_collision(self, item, direction):
        return None

    def update_valid_moves(self, board):
        self.valid_moves = self.find_valid_moves(board)

    def get_valid_moves(self):
        return self.valid_moves


class Player(Moving):

    def __init__(self, starty, startx):
        super().__init__(starty, startx)

    def assess_collision(self, item, direction):
        # Player cannot move if a wall is in the way
        if type(item) is Wall:
            return False
        # If a box is in the way, check if the player is able to push it
        elif type(item) is Box:
            if direction not in item.get_valid_moves():
                return False
        return True


class Box(Moving):

    def __init__(self, starty, startx):
        super().__init__(starty, startx)

    def assess_collision(self, item, direction):
        # Boxes cannot move if anything is in their way
        if item is not None:
            return False
        return True


class Tile:

    '''
    The regular and goal tile are exactly the same.
    The goal tile needs to be named differently so the board can assess it differently to normal tiles.
    '''

    def __init__(self, contents):
        self.contents = contents

    def get_contents(self):
        return self.contents

    def change_contents(self, item):
        self.contents = item


class Goal_Tile(Tile):

    def __init__(self, contents):
        super().__init__(contents)


class Wall:
    pass


if __name__ == '__main__':
    m = MainMenu()