import random

class AI1:
    def __init__(self, board):
        self.board = board
        self.safe_squares = []
        self.mine_squares = []

    def get_choice(self):   # returns row,col choice as strings (so that the "m" can be included)
        if self.board.first_move:
            self.board.first_move = False
            return str(self.board.start_x),str(self.board.start_y)      # return safe starting choice if on first move

        # step 1: process current board with new information
        for row in range(self.board.height):
            for col in range(self.board.width):
                if self.is_afn(row, col):
                    self.add_surrounding_squares_safe(row, col)
                elif self.is_amn(row, col):
                    self.add_surrounding_squares_mine(row, col)

        # Priority: mark all mines in mine_squares > choose safe square > choose random square
        if len(self.mine_squares) > 0:
            square = self.mine_squares[0]
            del self.mine_squares[0]
            return str(square[0]) + "m", str(square[1])  # mark a mine
        if len (self.safe_squares) > 0:
            square = self.safe_squares[0]
            del self.safe_squares[0]
            return str(square[0]), str(square[1])  # probe a safe square
        return str(random.randint(0,self.board.height-1)), str(random.randint(0,self.board.width-1))    # random space if all else fails

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
