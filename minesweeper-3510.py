import json
from Board import Board
import time

########################################################################################################################
#                                                                                                                      #
#                                          CS3510 Minesweeper Algorithms                                               #
#                                   David Cornell, Josh Rosenthal, Michael Ryan                                        #
#                                                                                                                      #
########################################################################################################################


testcase = "./testcases/standard_boards/varied_size_boards/25rows_40cols_10d_0.json"
# testcase = "./testcases/deterministic_board.json"

def load_board(testcase_path):
    with open(testcase_path) as f:
        data = json.load(f)

        dims = data['dim'].split(',')
        height = int(dims[0])
        width = int(dims[1])

        startPos = data['safe'].split(',')
        startX = int(startPos[0])
        startY = int(startPos[1])

        bombCount = int(data['bombs'])

        grid = data['board']

        return Board(width, height, startX, startY, bombCount, grid)


# Main method
if __name__ == "__main__":
    board = load_board(testcase)
    start_time = time.time()
    print(board.AI2())
    end_time = time.time()
    print("\n")
    print("Milliseconds of execution:", 1000*(end_time - start_time))
