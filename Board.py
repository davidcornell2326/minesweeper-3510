from AI1 import AI1
from AI2 import AI2

class Board:
    def __init__(self, width, height, start_x, start_y, bomb_count, grid_string):
        self.width = width
        self.height = height
        self.start_x = start_x
        self.start_y = start_y
        self.bomb_count = bomb_count
        self.grid_string = grid_string
        self.grid_actual = [[] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                self.grid_actual[y].append(int(grid_string[(y * width) + x]))
        self.grid = [[-1 for _ in range(self.width)] for _ in range(self.height)]       # -1 represents unknown (will show up as a * when printed)
        self.playing = True     # True while game is ongoing
        self.first_move = True
        self.num_probes = 0

    def __repr__(self):
        return "\n".join([self.grid_string[i:i+self.width] for i in range(0, len(self.grid_string), self.width)])

    def __str__(self):
        top = "    " + " ".join(str(i) for i in range(self.width)) + "\n   " + "-" * self.width * 2 + "\n"
        return top + "\n".join(str(i) + " | " + str(" ".join(str(self.grid[i][j] if self.grid[i][j] > -1 else ("*" if self.grid[i][j] == -1 else "X")) for j in range(self.width))) for i in range(self.height))

    def user_mode(self):
        print("\nChoose a spot to \"click\" by entering the row and then column where prompted.")
        print("Add the letter \"m\" to the end of either of the two numbers to \"mark\" that spot instead of clicking it.")
        print("\nStarting spot: row " + str(self.start_x) + ", column " + str(self.start_y) + "\n")
        while self.playing:
            print(self)
            row = input("Choose row: ")
            col = input("Choose column: ")
            if "m" in row or "m" in col:
                if self.grid[int(row[0])][int(col[0])] == -1:
                    self.grid[int(row[0])][int(col[0])] = -2        # -2 for marked bombed (it will appear as a X when printed)
                elif self.grid[int(row[0])][int(col[0])] == -2:
                    self.grid[int(row[0])][int(col[0])] = -1    # un-mark
                else:
                    print("\nYou can only mark unknown spots!")
            else:
                results = self.probe(int(row), int(col))
                if results is not None:
                    return results
            print("\n\n")

    def AI1(self):
        # print("Starting AI1\n")
        ai1 = AI1(self)
        while self.playing:
            # print(self)
            # print("")
            row,col = ai1.get_choice()
            if "m" in row:  # marking mine case
                if self.grid[int(row[0:len(row)-1])][int(col)] == -1:
                    self.grid[int(row[0:len(row)-1])][int(col)] = -2        # -2 for marked bombed (it will appear as a X when printed)
                elif self.grid[int(row[0:len(row)-1])][int(col)] == -2:
                    self.grid[int(row[0:len(row)-1])][int(col)] = -1    # un-mark (will never be used by AI1)
                else:
                    print("\nYou can only mark unknown spots!")
                    pass
            else:
                results = self.probe(int(row), int(col))
                if results is not None:
                    return results
            # input("Press enter to have the AI submit this choice")
            # print("Press enter to have the AI submit this choice")
            # print("\n\n")

    def AI2(self):
        print("Starting AI1\n")
        ai2 = AI2(self)
        while self.playing:
            row,col = ai2.get_choice()
            if "m" in row:  # marking mine case
                if self.grid[int(row[0:len(row) - 1])][int(col)] == -1:
                    self.grid[int(row[0:len(row) - 1])][
                        int(col)] = -2  # -2 for marked bombed (it will appear as a X when printed)
                elif self.grid[int(row[0:len(row) - 1])][int(col)] == -2:
                    self.grid[int(row[0:len(row) - 1])][int(col)] = -1  # un-mark
                else:
                    print("\nYou can only mark unknown spots!")
            else:
                results = self.probe(int(row), int(col))
                if results is not None:
                    return results
            print(self)
            # input("Press enter to continue the AI")
            print("Press enter to continue the AI")
            print("\n\n")

    def probe(self, row, col):
        if self.grid[row][col] >= 0:    # can't probe if square is already revealed
            return
        actual_square = self.grid_actual[row][col]
        self.num_probes += 1
        self.grid[row][col] = actual_square
        if actual_square == 9:
            # print("That was a bomb! Play will continue")
            pass
        # elif actual_square == 0:
            # if row > 0:
            #     self.probe(row-1, col)
            # if row < self.height-1:
            #     self.probe(row+1, col)
            # if col > 0:
            #     self.probe(row, col-1)
            # if col < self.width-1:
            #     self.probe(row, col+1)
            # for i in range(max(row-1, 0), min(row+2, self.height)):
            #     for j in range(max(col-1, 0), min(col+2, self.width)):
            #         if 0 < self.grid_actual[i][j] < 9:
            #             self.grid[i][j] = self.grid_actual[i][j]
        if self.win() is not None:
            self.playing = False
            # print("\n\n" + str(self))
            # print("\nEvery remaining spot is a bomb. Algorithm terminates!")
            print("Number of squares revealed (NOT counting marked mines that weren't actually chosen:", self.num_probes, "/", self.width * self.height)
            # print("Bomb locations (listed as (row, col) with (0,0) as top left):")
            return self.win()
        else:
            return None
        # if neither of the above cases is true, all we have to do is set the grid square to the actual

    def win(self): # returns list of (row, col) bomb locations if win, None if else
        known_bombs = []
        unknown_spots = []
        for row in range(self.height):
            for col in range(self.width):
                # Count revealed bombs and unknown spaces:
                if self.grid[row][col] == -2 or self.grid[row][col] == 9:
                    known_bombs.append((row,col))
                if self.grid[row][col] == -1:
                    unknown_spots.append((row,col))
        if len(known_bombs) == self.bomb_count:
            return known_bombs
        if len(known_bombs) + len(unknown_spots) == self.bomb_count:
            return known_bombs + unknown_spots
        else:
            return None

    def get_surrounding_squares(self, row, col):    # returns a list of the coordinates of the surrounding squares (regardless of contents)
        surrounding_squares = []
        for i in range(max(row - 1, 0), min(row + 2, self.height)):
            for j in range(max(col-1, 0), min(col+2, self.width)):
                if i != row or j != col:
                    surrounding_squares.append((i, j))
        return surrounding_squares
