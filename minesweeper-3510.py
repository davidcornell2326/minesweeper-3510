import json
from Board import Board
import time
import os
import pprint

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
        startY = int(startPos[0])
        startX = int(startPos[1])

        bombCount = int(data['bombs'])

        grid = data['board']

        return Board(width, height, startX, startY, bombCount, grid)


# Main method
if __name__ == "__main__":

    directory = "./testcases/standard_boards/varied_size_boards"
    # directory = "./testcases/standard_boards/varied_density_boards"
    for filename in os.listdir(directory):
        board = load_board(directory + "/" + filename)
        start_time = time.time()
        # print(board.AI1())
        print(board.AI2())
        end_time = time.time()
        print("\n")
        print("Milliseconds of execution:", 1000*(end_time - start_time))

