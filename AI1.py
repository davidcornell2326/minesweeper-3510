import random

class AI1:
    def __init__(self, board):
        self.board = board
        self.safe_squares = []
        self.mine_squares = []

    def get_choice(self):   # returns row,col choice as strings (so that the "m" can be included)
        if self.board.first_move:
            self.board.first_move = False
            print("AI1's next choice: " + str(self.board.start_y),str(self.board.start_x) + " (first move)")
            return str(self.board.start_y),str(self.board.start_x)      # return safe starting choice if on first move

        # step 1: process current board with new information
        for row in range(self.board.height):
            for col in range(self.board.width):
                if self.is_afn(row, col):
                    self.add_surrounding_squares_safe(row, col)
                elif self.is_amn(row, col):
                    self.add_surrounding_squares_mine(row, col)

        # Priority: mark all mines in mine_squares > choose safe square > choose random square (not uniformly random; informed/weighted random)
        if len(self.mine_squares) > 0:
            square = self.mine_squares[0]
            del self.mine_squares[0]
            print("AI1's next choice: " + str(square[0]) + "m", str(square[1]) + " (marking a known mine)")
            return str(square[0]) + "m", str(square[1])  # mark a mine
        if len (self.safe_squares) > 0:
            square = self.safe_squares[0]
            del self.safe_squares[0]
            print("AI1's next choice: " + str(square[0]), str(square[1]) + " (guaranteed non-mine)")
            return str(square[0]), str(square[1])  # probe a safe square
        choice_r,choice_c = self.informed_random_selection()  # informed random space if all else fails
        print("AI1's next choice: " + str(choice_r), str(choice_c) + " (informed, weighted random based on revealed squares)")
        return choice_r,choice_c
        # return str(random.randint(0,self.board.height-1)), str(random.randint(0,self.board.width-1))    # random space if all else fails

    def informed_random_selection(self):
        counter_board = [[0 for _ in range(self.board.width)] for _ in range(self.board.height)]   # each spot in this counter will hold a number, where higher number = more likely to contain a bomb
        for row in range(self.board.height):
            for col in range(self.board.width):
                surrounding_squares = self.board.get_surrounding_squares(row, col)
                for r,c in surrounding_squares:
                    if self.board.grid[r][c] > -1 and self.board.grid[r][c] < 9:    # if the spot is a revealed number, [0,9]
                        counter_board[row][col] += self.board.grid[r][c]
        # now, counter_board is populated with the sum of "votes" from surrounding squares
        # we will choose a square with the highest vote (in order to hopefully reveal a bomb, which will allow the surrounding squares to be closer to "known" information)
        # first, find max:
        max = -1
        for row in range(self.board.height):
            for col in range(self.board.width):
                if counter_board[row][col] > max and self.board.grid[row][col] == -1:
                    max = counter_board[row][col]
        # second, get list of all spots with this value:
        max_coords = []
        for row in range(self.board.height):
            for col in range(self.board.width):
                if counter_board[row][col] == max and self.board.grid[row][col] == -1:
                    max_coords.append((row,col))
        coord = random.choice(max_coords)
        return str(coord[0]), str(coord[1])

    def is_afn(self, row, col):
        surrounding_squares = self.board.get_surrounding_squares(row, col)
        count = 0
        for r,c in surrounding_squares:
            if self.board.grid[r][c] == -2 or self.board.grid[r][c] == 9:
                count += 1
        return count == self.board.grid[row][col]

    def is_amn(self, row, col):
        surrounding_squares = self.board.get_surrounding_squares(row, col)
        count = 0
        for r, c in surrounding_squares:
            if self.board.grid[r][c] == -1 or self.board.grid[r][c] == -2 or self.board.grid[r][c] == 9:
                count += 1
        return count == self.board.grid[row][col]

    def add_surrounding_squares_safe(self, row, col):
        surrounding_squares = self.board.get_surrounding_squares(row, col)
        for r, c in surrounding_squares:
            if self.board.grid[r][c] == -1 and (r,c) not in self.safe_squares:
                self.safe_squares.append((r,c))

    def add_surrounding_squares_mine(self, row, col):
        surrounding_squares = self.board.get_surrounding_squares(row, col)
        for r, c in surrounding_squares:
            if self.board.grid[r][c] == -1 and (r, c) not in self.mine_squares:
                self.mine_squares.append((r, c))
