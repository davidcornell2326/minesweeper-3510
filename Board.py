from AI1 import AI1

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
        print("Starting AI1\n")
        ai1 = AI1(self)
        while self.playing:
            print(self)
            row,col = ai1.get_choice()
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
            input("Press enter to continue the AI")
            print("\n\n")

        return AI1.run(self)

    def probe(self, row, col):
        if self.grid[row][col] >= 0:    # can't probe if square is already revealed
            return
        actual_square = self.grid_actual[row][col]
        self.grid[row][col] = actual_square
        if actual_square == 9:
            print("That was a bomb! Play will continue")
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
            print("\n\n" + str(self))
            print("\nEvery remaining spot is a bomb. You win!")
            return self.win()
        else:
            return None
        # if neither of the above cases is true, all we have to do is set the grid square to the actual

    def win(self): # returns list of (row, col) bomb locations if win, None if else
        possible_return_spaces = []
        for row in range(self.height):
            for col in range(self.width):
                # Count revealed bombs and unknown spaces:
                if self.grid[row][col] == -1 or self.grid[row][col] == -2 or self.grid[row][col] == 9:
                    possible_return_spaces.append((row,col))
        if len(possible_return_spaces) == self.bomb_count:
            return possible_return_spaces
        else:
            return None

    def get_surrounding_squares(self, row, col):    # returns a list of the coordinates of the surrounding squares (regardless of contents)
        surrounding_squares = []
        for i in range(max(row - 1, 0), min(row + 2, self.height)):
            for j in range(max(col-1, 0), min(col+2, self.width)):
                if i != row or j != col:
                    surrounding_squares.append((i, j))
        return surrounding_squares
