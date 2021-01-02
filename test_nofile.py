# Simulate a sokoban level fully with a pre-made level hard-written in code

class Game:

    def start(self):
        self.b = Board()
        self.mainloop()

    def mainloop(self):
        done = False
        while not done:
            done = self.b.events()
        exit()


class Board:

    def __init__(self):
        # Coordinates will later be read from text file
        self.wall_coords = [(0, 1), (0, 3)]
        self.box_coords = [(1, 1), (1, 3)]
        self.gtile_coords = [(4, 0), (4, 4)]
        self.player_coords = (2, 2)
        # This will be given as width*height in a text file
        self.layout = [[Tile(0, None), Tile(1, None), Tile(2, None), Tile(3, None), Tile(4, None)],
                       [Tile(5, None), Tile(6, None), Tile(7, None), Tile(8, None), Tile(9, None)],
                       [Tile(10, None), Tile(11, None), Tile(12, None), Tile(13, None), Tile(14, None)],
                       [Tile(15, None), Tile(16, None), Tile(17, None), Tile(18, None), Tile(19, None)],
                       [Tile(20, None), Tile(21, None), Tile(22, None), Tile(23, None), Tile(24, None)]]
        self.p = Player(self.player_coords[0], self.player_coords[1])
        self.place_objs()

    def place_objs(self):
        # Places objects on grid
        for coord in self.wall_coords:
            self.layout[coord[0]][coord[1]].change_contents(Wall())
        for coord in self.box_coords:
            self.layout[coord[0]][coord[1]].change_contents(Box(coord[0], coord[1]))
        for coord in self.gtile_coords:
            self.layout[coord[0]][coord[1]].change_contents(G_Tile())
        self.layout[self.player_coords[0]][self.player_coords[1]].change_contents(self.p)

    def move_player(self, current, new):
        # TODO add a move_box function that does the same thing but for a box
        self.layout[current[0]][current[1]].change_contents(None)
        self.layout[new[0]][new[1]].change_contents(self.p)
        # Check position by id
        # print(f'You are at {self.layout[new[0]][new[1]].get_id()}')

    def events(self):
        # Go through every tile in the layout, change their valid_moves
        for row in self.layout:
            for tile in row:
                if type(tile.get_contents()) is Box:
                    tile.get_contents().update_valid_moves(self.layout)
        self.valid_moves = self.p.find_valid_moves(self.layout)
        while True:
            direction = str(input('udlr, or 0 to exit: '))
            if direction == '0':
                return True
            elif direction in self.valid_moves:
                self.move_player(self.p.get_curr_pos(), self.p.get_new_pos(direction))
                # Check layout after moving
                # for row in self.layout:
                    # print(list(map(lambda x: x.get_contents(), row)))
                return False


class Player:

    # startx and starty may become a parameter in a Game_Obj object
    def __init__(self, starty, startx):
        self.posy = starty
        self.posx = startx
        self.dirs = ('u', 'd', 'l', 'r')
        self.movement_vectors = ([-1, 0], [1, 0], [0, -1], [0, 1])

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
            self.new_posy = self.posy + self.movement_vectors[counter][0]
            self.new_posx = self.posx + self.movement_vectors[counter][1]
            try:
                if self.new_posx >= 0 and self.new_posy >= 0:
                    self.tile_at_new_pos = board[self.new_posy][self.new_posx]
                    self.item = self.tile_at_new_pos.get_contents()
                    if type(self.item) is Wall:
                        print(f'Wall at {dir}')
                        self.valid = False
                    elif type(self.item) is G_Tile:
                        print(f'Goal tile at {dir}')
                        self.valid = False
                    elif type(self.item) is Box:
                        print(f'Box at {dir}')
                        if dir not in self.item.get_valid_moves():
                            self.valid = False
                else:
                    self.valid = False
            except IndexError:
                self.valid = False
            if self.valid:
                self.valid_moves.append(dir)
        # Check if valid directions are calculated correctly
        print(self.valid_moves)
        return self.valid_moves


class Tile:

    def __init__(self, _id, contents):
        # To remove
        self._id = _id
        self.contents = contents

    def get_contents(self):
        return self.contents

    def change_contents(self, item):
        self.contents = item

    # To remove
    def get_id(self):
        return self._id

class Game_Obj:
    pass

class G_Tile:
    pass

class Box:

    def __init__(self, starty, startx):
        self.posy = starty
        self.posx = startx
        self.dirs = ('u', 'd', 'l', 'r')
        self.movement_vectors = ([-1, 0], [1, 0], [0, -1], [0, 1])
        self.valid_moves = []

    def find_valid_moves(self, board):
        self.valid_moves = []
        for counter, dir in enumerate(self.dirs):
            self.valid = True
            self.new_posy = self.posy + self.movement_vectors[counter][0]
            self.new_posx = self.posx + self.movement_vectors[counter][1]
            try:
                if self.new_posx >= 0 and self.new_posy >= 0:
                    self.tile_at_new_pos = board[self.new_posy][self.new_posx]
                    if self.tile_at_new_pos.get_contents() is not None:
                        self.item = self.tile_at_new_pos.get_contents()
                        if type(self.item) is Wall:
                            print(f'Box has Wall at {dir}')
                        if type(self.item) is Box:
                            print(f'Box has Box at {dir}')
                        if type(self.item) is G_Tile:
                            print(f'Box has Goal tile at {dir}')
                        self.valid = False
                else:
                    self.valid = False
            except IndexError:
                self.valid = False
            if self.valid:
                self.valid_moves.append(dir)
        # Check if valid directions are calculated correctly
        # print(self.valid_dirs)
        return self.valid_moves

    def update_valid_moves(self, board):
        self.valid_moves = self.find_valid_moves(board)

    def get_valid_moves(self):
        # Check box valid moves
        # print(f'Box can move in {self.valid_moves}')
        return self.valid_moves


class Wall:
    pass

if __name__ == '__main__':
    g = Game()
    g.start()