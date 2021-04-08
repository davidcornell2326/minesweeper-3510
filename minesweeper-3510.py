import json
from Board import Board

########################################################################################################################
#                                                                                                                      #
#                                          CS3510 Minesweeper Algorithms                                               #
#                                   David Cornell, Josh Rosenthal, Michael Ryan                                        #
#                                                                                                                      #
########################################################################################################################


testcase = "./testcases/deterministic_board.json"


def load_board(testcase_path):
    with open(testcase_path) as f:
        data = json.load(f)

        dims = data['size'].split(',')
        width = int(dims[0])
        height = int(dims[1])

        startPos = data['safe'].split(',')
        startX = int(startPos[0])
        startY = int(startPos[1])

        bombCount = int(data['bombs'])

        grid = data['grid']

        return Board(width, height, startX, startY, bombCount, grid)


board = load_board(testcase)
print(board)
