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
        self.layout = [Tile(0), Tile(1)]
        self.p = Player()

    def place_player(self):
        self.p.place(self.layout)

    def events(self):
        direction = int(input('Move the player l/r (-1 or 1), otherwise, enter "0" to exit: '))
        if direction in [-1, 1]:
            self.p.move(self.layout, direction)
            return False
        elif direction == 0:
            return True


# Occupies the board as an area the player can move to
class Tile:
    def __init__(self, _id):
        self.id = _id

    def get_id(self):
        return self.id


# Moves around the board based on commands
class Player:
    def __init__(self):
        self.start_pos = 0
        self.pos = 0
        self.tile_below = None

    def place(self, board):
        self.tile_below = board[self.start_pos]
        self.get_tile_below()

    def get_tile_below(self):
        print(self.tile_below.get_id())

    def move(self, board, _dir):
        self.pos += _dir
        self.tile_below = board[self.pos]
        self.get_tile_below()




g = Game()
g.start()

#exit()

