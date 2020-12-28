# Use objects to create a grid based game with no interface
# Movement carried out by typing commands
# Practice before using PyGame

'''
Essentials for OOP:
- Using methods means we can generally use less parameters for functions
- Make reduce interdependency between objects as much as possible, the program should not crash for every change made
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
        self.layout = [[Tile(0), Tile(1), Tile(2), Tile(3)],
                       [Tile(4), Tile(5), Tile(6), Tile(7)],
                       [Tile(8), Tile(9), Tile(10)]]
        self.p = Player()

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


# Occupies the board as an area the player can move to
class Tile:
    def __init__(self, _id):
        self.id = _id

    def get_id(self):
        return self.id

# TODO: Create wall objects that will be used for collisions instead, rather than board borders
class Wall:
    pass

# Moves around the board based on commands
class Player:
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
        self.get_tile_below()

    def get_tile_below(self):
        return self.tile_below.get_id()

    def possible_moves(self, board):
        # TODO: Implement collisions with wall objects
        self.valid_directions = []
        # Find which directions the player can move in
        for place, direction in enumerate(self.direction_vectors):
            self.valid = True
            self.new_pos_y = self.pos[0] + direction[0]
            self.new_pos_x = self.pos[1] + direction[1]
            try:
                if self.new_pos_y >= 0 and self.new_pos_x >= 0:
                    self.temp_tile_below = board[self.new_pos_y][self.new_pos_x]
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
