# Use objects to create a grid based game with no interface
# Movement carried out by typing commands
# Practice before using PyGame

'''
Essentials for OOP:
- Using methods means we can generally use less parameters for functions
- Reduce interdependency between objects as much as possible, the program should not crash for every change made
- Keep data in objects, only access it via a few functions. This makes the interface simpler.
'''

# Wraps the entire game
class Game:

    def start(self):
        self.b = Board()
        self.b.place_player()
        self.mainloop()

    def mainloop(self):
        done = False
        while not done:
            done = self.b.events()
        exit()


# Contains the all tile, box and player objects
class Board:
    def __init__(self):
        '''
        TODO Rework all object placement to be based on 'place' functions, rather than writing things into layout
             This is closer to what the final produce will be like
             In the final product levels can be stored as:
             - Dimensions of tiles (how large will the level be)
             - Places of various objects (location of all walls, crates, player and goal tile)
             At the start of the game these objects are 'placed' on the tile grid
             This can be done as a text file
        '''
        self.layout = [[Tile(0, None), Tile(1, None), Tile(2, None), Tile(3, None)],
                       [Tile(4, None), Tile(5, None), Tile(6, Wall(1)), Tile(7, None)],
                       [Tile(8, None), Tile(9, None), Tile(10, Wall(2)), Tile(11, None)],
                       [Tile(12, None), Tile(13, None), Tile(14, None), Tile(15, None)]]
        self.p = Player()

    # TODO rework into 'place_object' that takes a list of objects and places them on the grid
    def place_player(self):
        self.p.place(self.layout)

    def events(self):
        # First find which directions the player can move in
        self.valid_moves = self.p.possible_moves(self.layout)
        # Directions will eventually be inputted by 'udlr', single letters indicating direction
        while True:
            direction = str(input('Move the player udlr, otherwise, enter "0" to exit: '))
            if direction in self.valid_moves:
                self.p.move(self.layout, direction)
                return False
            elif direction == '0':
                return True

'''
TODO create game_object class that player, box, wall and goal_tile inherits from
     - Properties: start_pos (indicates where the object is placed on layout)
     - Methods: place (reads from a list of objects and their start_pos. Places them at that start_pos)
'''

# Occupies the board as an area the player can move to
# TODO remove id feature, contents is the only tile property
class Tile:
    def __init__(self, _id, contents):
        self.id = _id
        self.contents = contents

    def get_id(self):
        return self.id

    # A tile can only contain one item at a time
    def update_contents(self, item):
        self.contents = item

    def get_contents(self):
        return self.contents

class Wall:
    # There is no need for the wall to have an id, this can be removed later after testing
    def __init__(self, _id):
        self.id = _id

    def get_id(self):
        return self.id

# Moves around the board based on commands
class Player:

    # TODO: Possible_moves, move and direction vectors in 'moveable' class. player and box inherits

    def __init__(self):
        # (row, column)
        self.start_pos = [0, 0]
        self.pos = [0, 0]
        # (up, down, right, left)
        # up is [-1, 0] as the higher up rows are earlier in the array, same for down as [1, 0]
        self.dirs = ['u', 'd', 'r', 'l']
        self.direction_vectors = [[-1, 0], [1, 0], [0, 1], [0, -1]]
        self.tile_below = None
        self.temp_tile_below = None

    def place(self, board):
        self.tile_below = board[self.start_pos[0]][self.start_pos[1]]
        print(self.get_tile_below())

    def get_tile_below(self):
        return self.tile_below.get_id()

    def possible_moves(self, board):
        self.valid_directions = []
        # Find which directions the player can move in
        for place, direction in enumerate(self.direction_vectors):
            self.valid = True
            self.new_pos_y = self.pos[0] + direction[0]
            self.new_pos_x = self.pos[1] + direction[1]
            try:
                # Prevents user having negative position
                if self.new_pos_y >= 0 and self.new_pos_x >= 0:
                    # Assignment causes value error if value is too high (out of bounds)
                    self.tile_at_new_pos = board[self.new_pos_y][self.new_pos_x]
                    # Checks the contents of the tile, if it is not empty return the wall direction and id
                    if self.tile_at_new_pos.get_contents() is not None:
                        print(f'wall at {self.dirs[place]} with id {self.tile_at_new_pos.get_contents().get_id()}')
                        self.valid = False
                else:
                    self.valid = False
            except IndexError:
                self.valid = False
            if self.valid:
                self.valid_directions.append(self.dirs[place])
        return self.valid_directions

    def move(self, board, _dir):
        # Set the players position to the new position
        self.pos[0] += self.direction_vectors[self.dirs.index(_dir)][0]
        self.pos[1] += self.direction_vectors[self.dirs.index(_dir)][1]
        # Change the tile the player is above of
        self.tile_below = board[self.pos[0]][self.pos[1]]
        # For testing purposes and until a simple GUI is implemented
        print(self.get_tile_below())


g = Game()
g.start()

#exit()