import random

class AI1:
    def __init__(self, board):
        self.board = board
        self.safe_squares = []
        self.mine_squares = []

    def get_choice(self, details):   # returns row,col choice as strings (so that the "m" can be included)
        if self.board.first_move:
            self.board.first_move = False
            if details:
                print("AI1's next choice: " + str(self.board.start_y),str(self.board.start_x) + " (first move)")
            return str(self.board.start_y),str(self.board.start_x)      # return safe starting choice if on first move

        # step 1: process current board with new information
        for row in range(self.board.height):
            for col in range(self.board.width):
                if self.is_afn(row, col):   # helper method to determine if square is AFN (all-free-neighbors)
                    self.add_surrounding_squares_safe(row, col)
                elif self.is_amn(row, col):     # helper method to determine if square is AMN (all-mine-neighbors)
                    self.add_surrounding_squares_mine(row, col)

        # Priority: mark all mines in mine_squares > choose safe square > choose random square (NOT uniformly random; informed/weighted random)
        if len(self.mine_squares) > 0:
            square = self.mine_squares[0]
            del self.mine_squares[0]
            if details:
                print("AI1's next choice: " + str(square[0]) + "m", str(square[1]) + " (marking a known mine)")
            return str(square[0]) + "m", str(square[1])  # choose to mark a mine
        if len (self.safe_squares) > 0:
            square = self.safe_squares[0]
            del self.safe_squares[0]
            if details:
                print("AI1's next choice: " + str(square[0]), str(square[1]) + " (guaranteed non-mine)")
            return str(square[0]), str(square[1])  # choose to reveal/probe a safe square
        choice_r,choice_c = self.informed_random_selection()  # choose an informed random space if all else fails
        if details:
            print("AI1's next choice: " + str(choice_r), str(choice_c) + " (informed, weighted random based on revealed squares)")
        return choice_r,choice_c

    def informed_random_selection(self):    # tries to choose a mine square based on a "votes" system of surrounding squares
        counter_board = [[0 for _ in range(self.board.width)] for _ in range(self.board.height)]   # each spot in this counter will hold a number, where higher number = more likely to contain a bomb
        for row in range(self.board.height):
            for col in range(self.board.width):
                surrounding_squares = self.board.get_surrounding_squares(row, col)  # helper method to get a list of the surrounding squares
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
        # finally, choose random spot from among the ones with the max votes value
        coord = random.choice(max_coords)
        return str(coord[0]), str(coord[1])

    def is_afn(self, row, col):     # helper method to determine if square is AFN (all-free-neighbors)
        surrounding_squares = self.board.get_surrounding_squares(row, col)
        count = 0
        for r,c in surrounding_squares:
            if self.board.grid[r][c] == -2 or self.board.grid[r][c] == 9:
                count += 1
        return count == self.board.grid[row][col]

    def is_amn(self, row, col):     # helper method to determine if square is AMN (all-mine-neighbors)
        surrounding_squares = self.board.get_surrounding_squares(row, col)
        count = 0
        for r, c in surrounding_squares:
            if self.board.grid[r][c] == -1 or self.board.grid[r][c] == -2 or self.board.grid[r][c] == 9:
                count += 1
        return count == self.board.grid[row][col]

    def add_surrounding_squares_safe(self, row, col):   # add surrounding squares of the input to the safe squares list
        surrounding_squares = self.board.get_surrounding_squares(row, col)
        for r, c in surrounding_squares:
            if self.board.grid[r][c] == -1 and (r,c) not in self.safe_squares:
                self.safe_squares.append((r,c))

    def add_surrounding_squares_mine(self, row, col):   # add surrounding squares of the input to the mine squares list
        surrounding_squares = self.board.get_surrounding_squares(row, col)
        for r, c in surrounding_squares:
            if self.board.grid[r][c] == -1 and (r, c) not in self.mine_squares:
                self.mine_squares.append((r, c))

# Main method
if __name__ == "__main__":
    print("If you're seeing this, please read README.MD!!!")
