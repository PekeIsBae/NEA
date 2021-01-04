# Simulate a Sokoban level fully with a pre-made level hard-written in code

import json

class Game:

    def __init__(self, level):
        self.level = level

    def start(self):
        self.b = Board(self.level)
        self.mainloop()

    def mainloop(self):
        done = False
        while not done:
            done = self.b.events()
        exit()


class Board:

    def __init__(self, level):
        # Read the level data from the json file
        self.level_data = self.parse_level_data(level)
        self.grid_dimensions = self.level_data['grid_dimensions']
        self.player_coords = self.level_data['player_coords']
        self.wall_coords = self.level_data['wall_coords']
        self.box_coords = self.level_data['box_coords']
        self.gtile_coords = self.level_data['gtile_coords']
        self.layout = [[Tile(None) for x in range(self.grid_dimensions[0])] for y in range(self.grid_dimensions[1])]
        self.p = Player(self.player_coords[0], self.player_coords[1])
        self.place_objs()

    def parse_level_data(self, level):
        with open(f'./levels/{level}.txt') as file:
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

    def move_player(self, current, new, direction):
        self.layout[current[0]][current[1]].change_contents(None)
        # If the place the player moves to has a box in it, move that box in the same direction
        if type(self.layout[new[0]][new[1]].get_contents()) is Box:
            self.box_to_move = self.layout[new[0]][new[1]].get_contents()
            self.move_box(self.box_to_move.get_curr_pos(), self.box_to_move.get_new_pos(direction), self.box_to_move)
        self.layout[new[0]][new[1]].change_contents(self.p)

    def move_box(self, current, new, box):
        self.layout[current[0]][current[1]].change_contents(None)
        self.layout[new[0]][new[1]].change_contents(box)

    def reset(self):
        self.layout = ([Tile(None) for x in range(self.grid_dimensions[0])] for y in range(self.grid_dimensions[1]))
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
            direction = str(input('udlr, reset to reset, or 0 to exit: '))
            if direction == '0':
                return True
            elif direction == 'reset':
                self.reset()
                return False
            elif direction in self.valid_moves:
                self.move_player(self.p.get_curr_pos(), self.p.get_new_pos(direction), direction)
                # Check layout after moving
                for row in self.layout:
                   print(list(map(lambda x: x.get_contents(), row)))
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
    g = Game('level')
    g.start()